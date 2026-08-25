import os
import asyncio
import json
import time
import httpx
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
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
    return {
        "service": "AI Consensus Arena (SIH Super-Architecture) API Engine",
        "status": "online",
        "web_app": "http://localhost:3000",
        "api_docs": "http://localhost:8000/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "multi-ai-debate-engine"}

POSSIBLE_PS_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "data", "extracted_problem_statements.json"),
    os.path.join(os.path.dirname(__file__), "..", "..", "extracted_problem_statements.json"),
    os.path.join(os.getcwd(), "data", "extracted_problem_statements.json"),
    os.path.join(os.getcwd(), "extracted_problem_statements.json"),
]

@app.get("/api/problem-statements")
async def get_problem_statements(
    query: Optional[str] = None,
    category: Optional[str] = None,
    theme: Optional[str] = None
):
    """
    Returns list of all imported SIH problem statements with multi-token keyword/code/description filtering.
    """
    target_path = None
    for p in POSSIBLE_PS_PATHS:
        if os.path.exists(p):
            target_path = p
            break

    if not target_path:
        return []

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            all_ps = json.load(f)

        results = all_ps

        if category and category.lower() != "all":
            c_lower = category.strip().lower()
            results = [ps for ps in results if ps.get("category", "").lower() == c_lower]

        if theme and theme.lower() != "all":
            t_lower = theme.strip().lower()
            results = [ps for ps in results if t_lower in ps.get("theme", "").lower()]

        if query and query.strip():
            tokens = [t.strip().lower() for t in query.strip().split() if t.strip()]
            
            def matches(ps: dict) -> bool:
                combined_text = " ".join([
                    str(ps.get("ps_code", "")),
                    str(ps.get("ps_id", "")),
                    str(ps.get("title", "")),
                    str(ps.get("organization", "")),
                    str(ps.get("department", "")),
                    str(ps.get("theme", "")),
                    str(ps.get("category", "")),
                    str(ps.get("description", ""))
                ]).lower()
                return all(token in combined_text for token in tokens)

            results = [ps for ps in results if matches(ps)]

        return results
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

from app.providers.research_engine import ResearchEngine

@app.get("/api/research/config")
async def get_research_config():
    """
    Returns the user's research configuration (Tavily key, polite email, toggle status).
    """
    return ResearchEngine.get_config()

@app.post("/api/research/config")
async def save_research_config(req: Request):
    """
    Saves the user's research settings (Tavily key, polite email, toggle status).
    """
    data = await req.json()
    ResearchEngine.save_config(data)
    return {"status": "success", "config": ResearchEngine.get_config()}

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

PROVIDER_TEMPLATES = [
    {
        "provider_id": "google_gemini",
        "provider_name": "Google AI Studio (Gemini)",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "key_env": "GEMINI_API_KEY",
        "help_url": "https://aistudio.google.com/app/apikey",
        "models": [
            {"id": "gemini-3.5-flash-lite", "name": "Gemini 3.5 Flash Lite", "model_id": "gemini-3.5-flash-lite", "fallback_models": ["gemini-flash-lite-latest"], "is_arbiter": True, "is_backup_arbiter": False},
            {"id": "gemini-3.7-flash", "name": "Gemini Flash Quota Pool (3.7 / 3.6 / 3.5)", "model_id": "gemini-3.7-flash", "fallback_models": ["gemini-3.6-flash", "gemini-3.5-flash"], "is_arbiter": False, "is_backup_arbiter": True}
        ]
    },
    {
        "provider_id": "openrouter",
        "provider_name": "OpenRouter (Free & Paid Fleet)",
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "help_url": "https://openrouter.ai/keys",
        "models": [
            {"id": "glm-5.2-free", "name": "GLM 5.2 (Free)", "model_id": "z-ai/glm-5.2:free", "fallback_models": []},
            {"id": "nemotron-3-super", "name": "NVIDIA Nemotron 3 Super 120B (Free)", "model_id": "nvidia/nemotron-3-super-120b-a12b:free", "fallback_models": []},
            {"id": "nemotron-3.5-lightning", "name": "NVIDIA Nemotron 3.5 Lightning (Free)", "model_id": "nvidia/nemotron-3.5-lightning:free", "fallback_models": []},
            {"id": "stealth-ox", "name": "Stealth Ox-Alpha", "model_id": "stealth/ox-alpha", "fallback_models": []}
        ]
    },
    {
        "provider_id": "agentrouter",
        "provider_name": "AgentRouter (Claude & GPT Flagships)",
        "base_url": "https://agentrouter.org/v1",
        "key_env": "AGENTROUTER_API_KEY",
        "help_url": "https://agentrouter.org",
        "models": [
            {"id": "claude-opus-4-8", "name": "Claude Opus 4.8", "model_id": "claude-opus-4-8", "fallback_models": []},
            {"id": "claude-opus-5", "name": "Claude Opus 5.0", "model_id": "claude-opus-5", "fallback_models": []},
            {"id": "gpt-5.6-sol", "name": "GPT 5.6 Sol", "model_id": "gpt-5.6-sol", "fallback_models": []}
        ]
    },
    {
        "provider_id": "xkiro",
        "provider_name": "XKiro Router",
        "base_url": "https://api.xkiro.com/v1",
        "key_env": "XKIRO_API_KEY",
        "help_url": "https://api.xkiro.com",
        "models": [
            {"id": "deepseek-v4-pro", "name": "DeepSeek V4 Pro (XKiro)", "model_id": "deepseek/deepseek-v4-pro", "fallback_models": ["deepseek/deepseek-v4-flash", "deepseek/deepseek-chat-v3.1"]},
            {"id": "qwen-3.8-max-xkiro", "name": "Qwen 3.8 Max (XKiro)", "model_id": "qwen/qwen3.8-max", "fallback_models": ["qwen/qwen3.7-max", "qwen/qwen3.7-plus"]},
            {"id": "mistral-large-2512", "name": "Mistral Large 2512 (XKiro)", "model_id": "mistralai/mistral-large-2512", "fallback_models": ["mistralai/mistral-medium-3.5"]},
            {"id": "qwen-3.7-max-xkiro", "name": "Qwen 3.7 Max (XKiro)", "model_id": "qwen/qwen3.7-max", "fallback_models": []},
            {"id": "minimax-m2.7", "name": "MiniMax M2.7 (XKiro)", "model_id": "minimax/minimax-m2.7", "fallback_models": ["minimax/minimax-m2.5-highspeed"]}
        ]
    },
    {
        "provider_id": "tokenin",
        "provider_name": "TokenIn Free Hub",
        "base_url": "https://tokenin.my.id/v1",
        "key_env": "TOKENIN_API_KEY",
        "help_url": "https://tokenin.my.id",
        "models": [
            {"id": "gemini-3.5-flash-free", "name": "Gemini 3.5 Flash Free (TokenIn)", "model_id": "myt/gemini-3.5-flash-free", "fallback_models": ["myt/mimo-v2.5-free"]},
            {"id": "claude-opus-4-8-free", "name": "Claude Opus 4.8 Free (TokenIn)", "model_id": "myt/claude-opus-4-8-free", "fallback_models": ["myt/gpt-5.6-sol-free"]}
        ]
    },
    {
        "provider_id": "tokenfaucet",
        "provider_name": "FreeTokenFaucet",
        "base_url": "https://freetokenfaucet.com/v1",
        "key_env": "TOKENFAUCET_API_KEY",
        "help_url": "https://freetokenfaucet.com",
        "models": [
            {"id": "mimo-v2.5", "name": "Mimo v2.5 (TokenFaucet)", "model_id": "mimo-v2.5", "fallback_models": []},
            {"id": "gpt-5.6-terra", "name": "GPT 5.6 Terra (TokenFaucet)", "model_id": "gpt-5.6-terra", "fallback_models": []},
            {"id": "gpt-5.6-luna", "name": "GPT 5.6 Luna (TokenFaucet)", "model_id": "gpt-5.6-luna", "fallback_models": []}
        ]
    },
    {
        "provider_id": "bluesminds",
        "provider_name": "BluesMinds AI",
        "base_url": "https://api.bluesminds.com/v1",
        "key_env": "BLUESMINDS_API_KEY",
        "help_url": "https://api.bluesminds.com",
        "models": [
            {"id": "claude-sonnet-5", "name": "Claude Sonnet 5 (BluesMinds)", "model_id": "unlimited/claude-sonnet-5", "fallback_models": []}
        ]
    },
    {
        "provider_id": "tokenrouter",
        "provider_name": "TokenRouter",
        "base_url": "https://api.tokenrouter.com/v1",
        "key_env": "TOKENROUTER_API_KEY",
        "help_url": "https://api.tokenrouter.com",
        "models": [
            {"id": "qwen-3.8-max-tokenrouter", "name": "Qwen 3.8 Max (Free)", "model_id": "qwen/qwen3.8-max-free", "fallback_models": []}
        ]
    }
]

@app.get("/api/providers/templates")
async def get_provider_templates():
    return PROVIDER_TEMPLATES

@app.post("/api/models/test-all")
async def test_all_models(models: List[ModelConfig]):
    """
    Tests all configured models concurrently and returns latency + availability map.
    """
    async def _test_single(m: ModelConfig):
        success, message, latency_ms, working_key = await UniversalAIClient.test_connectivity(m)
        return {
            "id": m.id,
            "name": m.name,
            "model_id": m.model_id,
            "success": success,
            "message": message,
            "latency_ms": round(latency_ms, 2),
            "working_key": working_key
        }

    tasks = [_test_single(m) for m in models]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    clean_results = {}
    for r in results:
        if isinstance(r, dict):
            clean_results[r["id"]] = r
        elif isinstance(r, Exception):
            pass
    return clean_results

# Discovery must always answer well inside the frontend dev-proxy timeout, so probes are
# short-lived, concurrency is capped, and the whole sweep runs under a hard time budget.
DISCOVERY_PROBE_TIMEOUT_SECONDS = 12   # per HTTP attempt (NOT the 600s debate timeout)
DISCOVERY_TOTAL_BUDGET_SECONDS = 55    # hard ceiling for the whole sweep
DISCOVERY_MAX_CONCURRENCY = 20         # simultaneous live probes
DISCOVERY_MAX_DYNAMIC_PER_PROVIDER = 15

@app.post("/api/providers/auto-discover")
async def auto_discover_models(payload: Dict[str, Any] = {}):
    """
    Accepts provider keys, queries provider /models endpoints dynamically + templates in parallel,
    benchmarks latency, sorts available models by speed, flags Admin's Favorites,
    and returns separated available vs unavailable lists.

    Always returns 200 with partial results rather than hanging: probes are capped at
    DISCOVERY_PROBE_TIMEOUT_SECONDS each and the sweep is abandoned after
    DISCOVERY_TOTAL_BUDGET_SECONDS, with unfinished models reported as unavailable.
    """
    data = payload if isinstance(payload, dict) else {}
    raw_keys = data.get("provider_keys") or {}
    if not isinstance(raw_keys, dict):
        raw_keys = {}
    # Tolerate null / non-string values coming from the wizard
    provider_keys = {
        str(k): (v.strip() if isinstance(v, str) else "")
        for k, v in raw_keys.items()
    }

    # Load master admin favorites for matching
    try:
        admin_configs = await UserConfigStorage.get_user_config()
    except Exception as e:
        print(f"[auto-discover] Could not load admin config, continuing without favorites: {e}")
        admin_configs = []
    admin_model_ids = {m.model_id.lower() for m in admin_configs}
    admin_names = {m.name.lower() for m in admin_configs}

    test_tasks = []
    seen_model_keys = set()

    for template in PROVIDER_TEMPLATES:
        p_id = template["provider_id"]
        key = provider_keys.get(p_id, "")
        if not key:
            continue

        base_url = template["base_url"].rstrip("/")
        models_to_test = list(template["models"])

        # Try to query provider's /models endpoint dynamically
        try:
            models_endpoint = f"{base_url}/models"
            headers = {"Authorization": f"Bearer {key}", "User-Agent": "SIH-Consensus-Arena/1.0"}
            async with httpx.AsyncClient(timeout=4.0, verify=False) as client:
                resp = await client.get(models_endpoint, headers=headers)
                if resp.status_code == 200:
                    dyn_data = resp.json()
                    raw_list = dyn_data.get("data", []) if isinstance(dyn_data, dict) else []
                    if isinstance(raw_list, list):
                        for item in raw_list[:DISCOVERY_MAX_DYNAMIC_PER_PROVIDER]:
                            m_id = item.get("id") if isinstance(item, dict) else item
                            # Providers occasionally emit null / numeric / nested ids - skip those
                            if not isinstance(m_id, str) or not m_id.strip():
                                continue
                            m_id = m_id.strip()
                            if any(t.get("model_id") == m_id for t in models_to_test):
                                continue
                            raw_name = item.get("name") if isinstance(item, dict) else None
                            display_name = (
                                raw_name.strip()
                                if isinstance(raw_name, str) and raw_name.strip()
                                else m_id.split("/")[-1].replace("-", " ").title()
                            )
                            models_to_test.append({
                                "id": m_id.replace("/", "-").replace(":", "-"),
                                "name": display_name,
                                "model_id": m_id,
                                "fallback_models": [],
                                "is_dynamic": True
                            })
        except Exception:
            pass  # Fallback to curated templates if /models is not supported

        for m_item in models_to_test:
            try:
                m_model_id = str(m_item.get("model_id") or "").strip()
                if not m_model_id:
                    continue

                dedup_key = f"{base_url}_{m_model_id}"
                if dedup_key in seen_model_keys:
                    continue
                seen_model_keys.add(dedup_key)

                m_name = str(m_item.get("name") or m_model_id)
                m_slug = str(m_item.get("id") or m_model_id).replace("/", "-").replace(":", "-")

                # Check if this model is an Admin Favorite
                is_admin_fav = (
                    m_model_id.lower() in admin_model_ids or
                    m_name.lower() in admin_names
                )

                cfg = ModelConfig(
                    id=f"m_{p_id}_{m_slug}",
                    name=m_name,
                    base_url=template["base_url"],
                    api_key=key,
                    backup_api_keys=[],
                    model_id=m_model_id,
                    fallback_model_ids=[str(f).strip() for f in (m_item.get("fallback_models") or []) if str(f).strip()],
                    provider_type="openai_compatible",
                    timeout_seconds=600,
                    is_arbiter=bool(m_item.get("is_arbiter", False)),
                    is_backup_arbiter=bool(m_item.get("is_backup_arbiter", False)),
                    enabled=True,
                    temperature=0.7
                )
                # Probe with a short timeout; the returned cfg keeps the full 600s debate timeout.
                probe_cfg = cfg.model_copy(update={"timeout_seconds": DISCOVERY_PROBE_TIMEOUT_SECONDS})
                test_tasks.append((cfg, probe_cfg, template, is_admin_fav))
            except Exception as e:
                print(f"[auto-discover] Skipped malformed model entry from {p_id}: {e}")
                continue

    def _result_stub(cfg: ModelConfig, template: dict, is_admin_fav: bool, message: str):
        return {
            "model": cfg.model_dump(),
            "provider_name": template["provider_name"],
            "provider_id": template["provider_id"],
            "success": False,
            "latency_ms": 0.0,
            "message": message,
            "is_admin_favorite": is_admin_fav
        }

    available_models = []
    unavailable_models = []
    timed_out_count = 0

    if test_tasks:
        semaphore = asyncio.Semaphore(DISCOVERY_MAX_CONCURRENCY)

        async def _test_discovery(cfg: ModelConfig, probe_cfg: ModelConfig, template: dict, is_admin_fav: bool):
            async with semaphore:
                try:
                    success, message, latency_ms, _working_key = await UniversalAIClient.test_connectivity(probe_cfg)
                except Exception as e:
                    success, message, latency_ms = False, f"Probe error: {type(e).__name__}: {e}", 0.0
            return {
                "model": cfg.model_dump(),
                "provider_name": template["provider_name"],
                "provider_id": template["provider_id"],
                "success": success,
                "latency_ms": round(latency_ms or 0.0, 2),
                "message": message,
                "is_admin_favorite": is_admin_fav
            }

        jobs = [
            (asyncio.ensure_future(_test_discovery(cfg, probe_cfg, tmpl, is_fav)), cfg, tmpl, is_fav)
            for cfg, probe_cfg, tmpl, is_fav in test_tasks
        ]
        done, pending = await asyncio.wait(
            [job[0] for job in jobs],
            timeout=DISCOVERY_TOTAL_BUDGET_SECONDS
        )

        for task, cfg, tmpl, is_fav in jobs:
            if task in done:
                try:
                    r = task.result()
                except Exception as e:
                    unavailable_models.append(_result_stub(cfg, tmpl, is_fav, f"Probe crashed: {type(e).__name__}: {e}"))
                    continue
                if r.get("success"):
                    available_models.append(r)
                else:
                    unavailable_models.append(r)
            else:
                task.cancel()
                timed_out_count += 1
                unavailable_models.append(_result_stub(
                    cfg, tmpl, is_fav,
                    f"Not verified: discovery time budget of {DISCOVERY_TOTAL_BUDGET_SECONDS}s elapsed. Test this model individually."
                ))

        if pending:
            await asyncio.gather(*pending, return_exceptions=True)

    # Sort available models by latency (fastest first)
    available_models.sort(key=lambda x: x["latency_ms"])

    return {
        "available_models": available_models,
        "unavailable_models": unavailable_models,
        "discovered_models": available_models + unavailable_models,
        "admin_favorites_count": sum(1 for m in available_models if m["is_admin_favorite"]),
        "total_tested": len(test_tasks),
        "not_verified_count": timed_out_count
    }


@app.post("/api/debate/start")
async def start_debate(req: StartDebateRequest):
    if not req.models or len(req.models) < 2:
        raise HTTPException(status_code=400, detail="At least 2 participating AI models are required.")

    arbiter_id = req.arbiter_model_id
    if not arbiter_id:
        arbiter_model = next((m for m in req.models if m.is_arbiter), req.models[0])
        arbiter_id = arbiter_model.id

    backup_arbiter_id = req.backup_arbiter_model_id
    if not backup_arbiter_id:
        backup_candidate = next((m for m in req.models if m.is_backup_arbiter and m.id != arbiter_id), None)
        if not backup_candidate:
            # Pick second enabled model as fallback backup
            other_models = [m for m in req.models if m.id != arbiter_id and m.enabled]
            backup_candidate = other_models[0] if other_models else None
        if backup_candidate:
            backup_arbiter_id = backup_candidate.id

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
        backup_arbiter_model_id=backup_arbiter_id,
        status="running",
        current_phase_index=1,
        current_phase_title="Phase 1: Multi-Persona Genesis",
        current_pass_id="1.1",
        current_pass_title="Pass 1.1: Lead Architect Genesis",
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
    
    session.current_phase_index += 1
    session.current_phase_title = phase_title
    session.current_phase_prompt = req.followup_prompt.strip()
    session.status = "running"
    await SessionStorage.save_session(session)

    await DebateOrchestrator.resume_debate(session_id, auto_advance=req.auto_advance)

    return {
        "status": "running",
        "phase_index": session.current_phase_index,
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

class ArbiterCommandRequest(BaseModel):
    command: str

@app.post("/api/debate/{session_id}/arbiter/command")
async def handle_arbiter_command(session_id: str, req: ArbiterCommandRequest):
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")
    if not req.command or not req.command.strip():
        raise HTTPException(status_code=400, detail="Command text is required.")
    return await DebateOrchestrator.execute_arbiter_command(session_id, req.command.strip())

@app.get("/api/workspaces")
async def list_all_workspaces():
    return await SessionStorage.list_workspaces()

@app.get("/api/workspaces/{session_id}/files/{filename}")
async def download_workspace_file(session_id: str, filename: str):
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")

    workspace_dir = SessionStorage.get_workspace_dir(session)
    safe_filename = os.path.basename(filename)
    file_path = os.path.abspath(os.path.join(workspace_dir, safe_filename))

    if not file_path.startswith(os.path.abspath(workspace_dir)):
        raise HTTPException(status_code=403, detail="Access denied.")

    if not os.path.exists(file_path):
        content_to_write = None
        for phase in session.phases:
            if phase.verdict_filename == safe_filename:
                content_to_write = phase.verdict_markdown
                break
        if not content_to_write and safe_filename in ["LATEST_CONSENSUS_VERDICT.md", "verdict.md"]:
            content_to_write = session.final_markdown_report

        if content_to_write:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content_to_write)
        else:
            raise HTTPException(status_code=404, detail="File not found in workspace.")

    media_type = "application/pdf" if safe_filename.endswith(".pdf") else "text/plain" if safe_filename.endswith(".txt") else "text/markdown; charset=utf-8"
    return FileResponse(file_path, filename=safe_filename, media_type=media_type)


@app.get("/api/workspaces/{session_id}/research/{filename}")
async def download_research_file(session_id: str, filename: str):
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")

    workspace_dir = SessionStorage.get_workspace_dir(session)
    research_dir = os.path.abspath(os.path.join(workspace_dir, "research"))
    safe_filename = os.path.basename(filename)
    file_path = os.path.abspath(os.path.join(research_dir, safe_filename))

    if not file_path.startswith(research_dir) or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Research file not found.")

    media_type = "application/pdf" if safe_filename.endswith(".pdf") else "text/plain; charset=utf-8"
    return FileResponse(file_path, filename=safe_filename, media_type=media_type)

