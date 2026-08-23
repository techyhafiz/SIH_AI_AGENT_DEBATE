import os
import asyncio
import json
import time
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse, FileResponse
from sse_starlette.sse import EventSourceResponse

from app.schemas import (
    ModelConfig,
    DebateSession,
    StartDebateRequest,
    FollowUpDebateRequest,
    ModeratorActionRequest,
    ModelTestRequest
)
from app.providers.universal_client import UniversalAIClient
from app.storage import SessionStorage, sanitize_folder_name
from app.engine.orchestrator import DebateOrchestrator

app = FastAPI(
    title="Multi-AI Debate & Consensus Engine (SIH Edition)",
    version="2.0.0",
    description="Multi-LLM Collaborative Debate, Multi-Key Failover & Workspace Deliverables Engine"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Multi-AI Debate Engine API is active."}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "multi-ai-debate-engine"}

PS_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "extracted_problem_statements.json")

@app.get("/api/problem-statements")
async def get_problem_statements(query: Optional[str] = None):
    """
    Returns list of all imported SIH problem statements with optional keyword/code filtering.
    """
    if not os.path.exists(PS_FILE_PATH):
        return []
    try:
        with open(PS_FILE_PATH, "r", encoding="utf-8") as f:
            all_ps = json.load(f)
            
        if not query:
            return all_ps
            
        q = query.strip().lower()
        filtered = [
            ps for ps in all_ps
            if q in ps.get("ps_code", "").lower()
            or q in ps.get("ps_id", "").lower()
            or q in ps.get("title", "").lower()
            or q in ps.get("organization", "").lower()
            or q in ps.get("theme", "").lower()
        ]
        return filtered
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading problem statements: {str(e)}")

from app.storage import SessionStorage, UserConfigStorage, sanitize_folder_name
import subprocess
import httpx

@app.get("/api/version")
async def check_app_version():
    """
    Checks the local git commit against the latest commit on GitHub repository.
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        local_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root).decode().strip()
    except Exception:
        local_sha = "unknown"

    remote_sha = local_sha
    commit_msg = ""
    html_url = "https://github.com/techyhafiz/SIH_AI_AGENT_DEBATE"
    update_available = False

    try:
        async with httpx.AsyncClient(timeout=4.0, verify=False) as client:
            resp = await client.get(
                "https://api.github.com/repos/techyhafiz/SIH_AI_AGENT_DEBATE/commits/main",
                headers={"User-Agent": "Cline/3.0.0"}
            )
            if resp.status_code == 200:
                data = resp.json()
                remote_sha = data.get("sha", local_sha)
                commit_msg = data.get("commit", {}).get("message", "").split("\n")[0]
                html_url = data.get("html_url", html_url)
                if local_sha != "unknown" and remote_sha != local_sha:
                    update_available = True
    except Exception:
        pass

    return {
        "version": "2.0.0",
        "local_sha": local_sha[:7] if local_sha != "unknown" else "v2.0.0",
        "remote_sha": remote_sha[:7] if remote_sha != "unknown" else "v2.0.0",
        "update_available": update_available,
        "latest_commit_message": commit_msg,
        "github_url": html_url,
        "repo_url": "https://github.com/techyhafiz/SIH_AI_AGENT_DEBATE"
    }

@app.get("/api/user/config")
async def get_user_config():
    """
    Returns the permanently stored user API keys and debater configurations.
    """
    models = await UserConfigStorage.get_user_config()
    return [m.model_dump() for m in models]

@app.post("/api/user/config")
async def save_user_config(models: List[ModelConfig]):
    """
    Permanently saves the user's API keys and model configurations across all sessions.
    """
    if not models or len(models) < 1:
        raise HTTPException(status_code=400, detail="At least 1 model configuration is required.")
    await UserConfigStorage.save_user_config(models)
    return {"status": "success", "message": "User credentials & configurations saved permanently."}

@app.post("/api/models/test")
async def test_model_endpoint(req: ModelTestRequest):
    """
    Tests primary and backup API keys with automatic failover verification.
    """
    cfg = ModelConfig(
        name="Probe Model",
        base_url=req.base_url,
        api_key=req.api_key,
        backup_api_keys=req.backup_api_keys,
        model_id=req.model_id,
        provider_type=req.provider_type,
        timeout_seconds=req.timeout_seconds
    )
    success, message, latency_ms, working_key = await UniversalAIClient.test_connectivity(cfg)
    return {
        "success": success,
        "message": message,
        "latency_ms": round(latency_ms, 2),
        "working_key": working_key
    }

@app.post("/api/debate/start")
async def start_debate(req: StartDebateRequest):
    if not req.models or len(req.models) < 2:
        raise HTTPException(status_code=400, detail="At least 2 participating AI models are required.")

    arbiter_id = req.arbiter_model_id
    if not arbiter_id:
        arbiter_model = next((m for m in req.models if m.is_arbiter), req.models[0])
        arbiter_id = arbiter_model.id

    title = req.session_title or (f"{req.ps_code}_{sanitize_folder_name(req.ministry_domain)}" if req.ps_code else f"SIH_{sanitize_folder_name(req.ministry_domain)}")
    
    full_problem_text = req.problem_statement
    if req.additional_prompt and req.additional_prompt.strip():
        full_problem_text = f"{req.problem_statement}\n\n### 🎯 ADDITIONAL USER CONSTRAINTS & STRATEGIC FOCUS:\n{req.additional_prompt.strip()}"

    session = DebateSession(
        session_title=title,
        ps_code=req.ps_code,
        problem_statement=full_problem_text,
        additional_prompt=req.additional_prompt,
        ministry_domain=req.ministry_domain or "Smart India Hackathon (General)",
        models=req.models,
        arbiter_model_id=arbiter_id,
        status="running",
        current_phase_index=1,
        current_phase_prompt=full_problem_text
    )

    await SessionStorage.save_session(session)
    asyncio.create_task(DebateOrchestrator.run_round_loop(session.session_id, auto_advance=req.auto_advance))

    return {
        "session_id": session.session_id,
        "workspace_folder": session.workspace_folder,
        "status": "running",
        "current_round": 0,
        "current_phase": 1
    }

@app.post("/api/debate/{session_id}/followup")
async def start_followup_debate(session_id: str, req: FollowUpDebateRequest):
    """
    Triggers a follow-up prompt debate phase (e.g., technical specification list, design MD)
    in the same workspace folder, taking prior agreed verdicts as context.
    """
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")

    if not req.followup_prompt.strip():
        raise HTTPException(status_code=400, detail="followup_prompt is required.")

    phase_title = req.phase_title or f"Phase {session.current_phase_index + 1} Specification"
    
    await DebateOrchestrator.start_followup_phase(
        session_id=session_id,
        followup_prompt=req.followup_prompt.strip(),
        phase_title=phase_title,
        auto_advance=req.auto_advance
    )

    return {
        "status": "running",
        "phase_index": session.current_phase_index + 1,
        "phase_title": phase_title
    }

@app.get("/api/debate/stream/{session_id}")
async def stream_debate_events(session_id: str, request: Request):
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")

    queue = DebateOrchestrator.get_event_queue(session_id)

    async def event_generator():
        try:
            yield {
                "event": "CONNECTED",
                "data": json.dumps({
                    "session_id": session_id,
                    "status": session.status,
                    "workspace_folder": session.workspace_folder,
                    "phases": [p.model_dump() for p in session.phases]
                })
            }

            while True:
                if await request.is_disconnected():
                    break

                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=5.0)
                    yield {
                        "event": event_data.get("event", "message"),
                        "data": json.dumps(event_data.get("data", {}))
                    }
                except asyncio.TimeoutError:
                    yield {
                        "event": "HEARTBEAT",
                        "data": json.dumps({"ping": time.time()})
                    }
        finally:
            DebateOrchestrator.remove_event_queue(session_id, queue)

    return EventSourceResponse(event_generator())

@app.get("/api/debate/{session_id}")
async def get_debate_session(session_id: str):
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")
    return session

@app.post("/api/debate/{session_id}/moderator")
async def handle_moderator_action(session_id: str, req: ModeratorActionRequest):
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")

    if req.action == "pause":
        await DebateOrchestrator.pause_debate(session_id)
    elif req.action == "resume":
        await DebateOrchestrator.resume_debate(session_id)
    elif req.action == "call_verdict":
        await DebateOrchestrator.force_call_verdict(session_id)
    elif req.action == "inject_prompt":
        if not req.injection_text:
            raise HTTPException(status_code=400, detail="injection_text is required.")
        await DebateOrchestrator.inject_moderator_prompt(session_id, req.injection_text)
    elif req.action == "update_model_and_retry":
        if not req.ai_model_config:
            raise HTTPException(status_code=400, detail="ai_model_config is required.")
        await DebateOrchestrator.update_and_retry_model(session_id, req.ai_model_config)
    elif req.action == "drop_model":
        if not req.target_model_id:
            raise HTTPException(status_code=400, detail="target_model_id is required.")
        await DebateOrchestrator.drop_model(session_id, req.target_model_id)

    return {"status": "success", "action": req.action}

@app.get("/api/workspaces")
async def list_all_workspaces():
    return await SessionStorage.list_workspaces()

@app.get("/api/workspaces/{session_id}/files/{filename}")
async def download_workspace_file(session_id: str, filename: str):
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")

    file_path = os.path.join(session.workspace_folder, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found in workspace.")

    return FileResponse(file_path, filename=filename, media_type="text/markdown")
