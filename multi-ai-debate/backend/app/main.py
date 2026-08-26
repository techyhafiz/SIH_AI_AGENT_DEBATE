import os
import re
import random
import asyncio
import json
import time
import subprocess
import httpx
import secrets
from collections import Counter
from contextlib import asynccontextmanager
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
    ModelTestRequest,
    ResearchConfig,
)
from app.providers.universal_client import UniversalAIClient
from app.providers.http_transport import build_async_client, provider_ssl_context, transport_diagnostics
from app.storage import PersistenceError, SessionStorage, UserConfigStorage, sanitize_folder_name
from app.engine.orchestrator import DebateOrchestrator


POSSIBLE_PS_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "data", "extracted_problem_statements.json"),
    os.path.join(os.path.dirname(__file__), "..", "..", "extracted_problem_statements.json"),
    os.path.join(os.getcwd(), "data", "extracted_problem_statements.json"),
    os.path.join(os.getcwd(), "extracted_problem_statements.json"),
]
PROBLEM_STATEMENTS: List[dict] = []
DISCOVERY_CREDENTIALS: Dict[str, Dict[str, str]] = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    global PROBLEM_STATEMENTS
    # Build the shared TLS context up front (it reads the OS root store) so the first burst of
    # provider requests does not pay for it on the event loop.
    await asyncio.to_thread(provider_ssl_context)
    for path in POSSIBLE_PS_PATHS:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    loaded = json.load(handle)
                PROBLEM_STATEMENTS = loaded if isinstance(loaded, list) else []
                break
            except Exception as exc:
                print(f"[startup] Could not load problem statements from {path}: {exc}")

    for item in await SessionStorage.list_workspaces():
        if item.get("loadable") and item.get("status") == "running":
            session = await SessionStorage.get_session(item["session_id"])
            if session:
                session.status = "paused"
                await SessionStorage.save_session(session)
    yield


app = FastAPI(
    title="Multi-AI Debate & Consensus Engine (SIH Edition)",
    version="2.0.0",
    description="Multi-LLM Collaborative Debate, Multi-Key Failover & Workspace Deliverables Engine",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
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
    # `transport` makes a broken local TLS chain (antivirus / proxy interception) visible here
    # instead of only as mysteriously empty model catalogues.
    return {"status": "ok", "service": "multi-ai-debate-engine", "transport": transport_diagnostics()}

@app.get("/api/problem-statements")
async def get_problem_statements(
    query: Optional[str] = None,
    category: Optional[str] = None,
    theme: Optional[str] = None
):
    """
    Returns list of all imported SIH problem statements with multi-token keyword/code/description filtering.
    """
    try:
        results = PROBLEM_STATEMENTS

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
        async with build_async_client(timeout=4.0) as client:
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
    config = ResearchEngine.get_config()
    config["has_tavily_api_key"] = bool(config.get("tavily_api_key"))
    return config

@app.post("/api/research/config")
async def save_research_config(config: ResearchConfig):
    """
    Saves the user's research settings (Tavily key, polite email, toggle status).
    """
    incoming = config.model_dump()
    current = ResearchEngine.get_config()
    if not incoming.get("tavily_api_key"):
        incoming["tavily_api_key"] = current.get("tavily_api_key", "")
    ResearchEngine.save_config(incoming)
    return {"status": "success", "config": await get_research_config()}


def public_model(model: ModelConfig) -> dict:
    data = model.model_dump()
    data["api_key"] = ""
    data["backup_api_keys"] = []
    return data


def public_session(session: DebateSession) -> dict:
    data = session.model_dump()
    data["models"] = [public_model(model) for model in session.models]
    return data


def discovery_credential_for(model: ModelConfig) -> str:
    record = DISCOVERY_CREDENTIALS.get(model.credential_ref or "")
    if not record or model.base_url.rstrip("/") != record["base_url"].rstrip("/"):
        return ""
    return record["key"]


def stored_credential_for(model: ModelConfig, stored: Optional[ModelConfig]) -> tuple[str, List[str]]:
    if not stored or model.base_url.rstrip("/") != stored.base_url.rstrip("/"):
        return "", []
    return stored.api_key, list(stored.backup_api_keys)

@app.get("/api/user/config")
async def get_user_config():
    """
    Returns the permanently stored user API keys and debater configurations.
    """
    models = await UserConfigStorage.get_user_config()
    return [model.model_dump() for model in models]

@app.post("/api/user/config")
async def save_user_config(models: List[ModelConfig]):
    """
    Permanently saves the user's API keys and model configurations across all sessions.
    """
    if not models or len(models) < 1:
        raise HTTPException(status_code=400, detail="At least 1 model configuration is required.")
    existing = {model.id: model for model in await UserConfigStorage.get_user_config()}
    merged = []
    for model in models:
        previous = existing.get(model.id)
        discovered_key = discovery_credential_for(model)
        if discovered_key and not model.api_key:
            model = model.model_copy(update={"api_key": discovered_key, "credential_ref": None})
        if previous and not model.api_key:
            primary, backups = stored_credential_for(model, previous)
            model = model.model_copy(update={
                "api_key": primary,
                "backup_api_keys": model.backup_api_keys or backups,
            })
        merged.append(model)
    await UserConfigStorage.save_user_config(merged)
    return {"status": "success", "message": "User credentials & configurations saved permanently."}

@app.post("/api/models/test")
async def test_model_endpoint(req: ModelTestRequest):
    """
    Tests primary and backup API keys with automatic failover verification.
    """
    stored = None
    if req.config_id and not req.api_key:
        candidate = next((model for model in await UserConfigStorage.get_user_config() if model.id == req.config_id), None)
        if candidate and candidate.base_url.rstrip("/") == req.base_url.rstrip("/"):
            stored = candidate
    cfg = ModelConfig(
        id=req.config_id or "probe",
        name="Probe Model",
        base_url=req.base_url,
        api_key=req.api_key or (stored.api_key if stored else ""),
        backup_api_keys=req.backup_api_keys or (stored.backup_api_keys if stored else []),
        model_id=req.model_id,
        provider_type=req.provider_type,
        timeout_seconds=req.timeout_seconds
    )
    success, message, latency_ms, working_key = await UniversalAIClient.test_connectivity(cfg)
    return {
        "success": success,
        "message": message,
        "latency_ms": round(latency_ms, 2),
        "working_key": "***" if working_key else None
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

FLEET_TEST_PROBE_TIMEOUT_SECONDS = 35   # per HTTP attempt; generous for heavy reasoning models (debates use the full 600s)
FLEET_TEST_CONCURRENCY = 12
FLEET_TEST_BUDGET_SECONDS = 150


@app.post("/api/models/test-all")
async def test_all_models(models: List[ModelConfig]):
    """
    Tests all configured models concurrently and returns latency + availability map.
    """
    stored_models = {model.id: model for model in await UserConfigStorage.get_user_config()}

    async def _test_single(m: ModelConfig):
        stored = stored_models.get(m.id)
        discovered_key = discovery_credential_for(m)
        if not m.api_key and (discovered_key or stored):
            primary, backups = stored_credential_for(m, stored)
            m = m.model_copy(update={
                "api_key": discovered_key or primary,
                "backup_api_keys": m.backup_api_keys or backups,
            })
        # Pinned explicitly rather than inheriting the config's debate timeout (600s), so this
        # endpoint's per-probe ceiling is stated here instead of relying on the client's clamp.
        m = m.model_copy(update={"timeout_seconds": FLEET_TEST_PROBE_TIMEOUT_SECONDS})
        success, message, latency_ms, working_key = await UniversalAIClient.test_connectivity(m)
        return {
            "id": m.id,
            "name": m.name,
            "model_id": m.model_id,
            "success": success,
            "message": message,
            "latency_ms": round(latency_ms, 2),
            "working_key": "***" if working_key else None
        }

    semaphore = asyncio.Semaphore(FLEET_TEST_CONCURRENCY)

    async def bounded_test(model: ModelConfig):
        async with semaphore:
            probe = model.model_copy(update={"timeout_seconds": FLEET_TEST_PROBE_TIMEOUT_SECONDS})
            return await _test_single(probe)

    tasks = [asyncio.create_task(bounded_test(model)) for model in models]
    done, pending = await asyncio.wait(tasks, timeout=FLEET_TEST_BUDGET_SECONDS)
    results = await asyncio.gather(*done, return_exceptions=True)
    for task in pending:
        task.cancel()
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)

    clean_results = {}
    for r in results:
        if isinstance(r, dict):
            clean_results[r["id"]] = r
        elif isinstance(r, Exception):
            clean_results[f"failed_{len(clean_results)}"] = {
                "success": False,
                "message": f"Probe failed: {type(r).__name__}: {r}",
                "latency_ms": 0,
            }
    for model in models:
        if model.id not in clean_results:
            clean_results[model.id] = {
                "id": model.id,
                "name": model.name,
                "model_id": model.model_id,
                "success": False,
                "message": "Not verified: test-all time budget elapsed.",
                "latency_ms": 0,
                "not_verified": True,
            }
    return clean_results

DISCOVERY_CATALOGUE_TIMEOUT_SECONDS = 15   # per-provider GET /models (was 4s, which silently dropped slow catalogues)
DISCOVERY_CATALOGUE_RETRIES = 3            # TokenRouter rate-limits /models itself; one 429 must not cost 128 models
DISCOVERY_PROBE_TIMEOUT_SECONDS = 25       # per live chat probe
DISCOVERY_RETRY_PROBE_TIMEOUT_SECONDS = 60 # second-chance pass is serial and uncontended, so it can wait
DISCOVERY_TOTAL_BUDGET_SECONDS = 900       # hard ceiling for a full sweep of every listed model
DISCOVERY_RETRY_BUDGET_SECONDS = 240       # share of that ceiling the serial second-chance pass may use
DISCOVERY_GLOBAL_CONCURRENCY = 48          # total simultaneous probes across all providers
DISCOVERY_PER_PROVIDER_CONCURRENCY = 6     # per-provider cap: stops a sweep from 429-ing itself
DISCOVERY_MAX_DYNAMIC_PER_PROVIDER = 0     # 0 = no cap; list everything the provider's /models returns
DISCOVERY_RATE_LIMIT_RETRIES = 3           # a 429 means "ask again", not "model is dead"
DISCOVERY_AUTH_FAILURE_THRESHOLD = 10      # consecutive *credential* rejections before a provider is abandoned
# A provider that answers 429 gets that many seconds of quiet from every worker on it. Small
# free hosts (BluesMinds throttles after ~5 requests) otherwise spend a whole sweep rejecting
# us, and every model behind the throttle is reported dead when it is merely queued.
DISCOVERY_PROVIDER_COOLDOWN_SECONDS = 4.0
DISCOVERY_MAX_COOLDOWN_SECONDS = 20.0
DISCOVERY_JOB_TTL_SECONDS = 3600

# Discovery is a long sweep (hundreds of models), so it runs as a background job that the
# wizard polls, rather than one blocking request that looks frozen for minutes.
DISCOVERY_JOBS: Dict[str, Dict[str, Any]] = {}

_PROBE_HTTP_RE = re.compile(r"HTTP\s+(\d{3})")
_RETRY_AFTER_RE = re.compile(r"retry[- ]after[\"']?\s*[:=]?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)


def _retry_after_seconds(resp: Any, default: float) -> float:
    """
    Honour a provider's own backoff hint when it sends one, clamped so a hostile or
    misconfigured `Retry-After: 3600` cannot stall the sweep.
    """
    raw = None
    try:
        raw = resp.headers.get("retry-after") or resp.headers.get("x-ratelimit-reset-after")
    except Exception:
        raw = None
    if raw is None:
        try:
            match = _RETRY_AFTER_RE.search(resp.text or "")
        except Exception:
            match = None
        raw = match.group(1) if match else None
    try:
        hinted = float(raw)
    except (TypeError, ValueError):
        return default
    if hinted <= 0:
        return default
    return min(hinted, DISCOVERY_MAX_COOLDOWN_SECONDS)


def classify_probe_failure(message: str) -> str:
    """
    Maps a `test_connectivity` failure message to a stable reason code.

    The wizard needs to distinguish "this model does not exist on this endpoint" (a fast 404,
    the overwhelmingly common case when sweeping a full catalogue) from "your key is bad"
    (401, affects every model on that provider) and "slow down" (429, which must be retried
    or working models get reported as dead).

    The body text is consulted BEFORE the status code, because the aggregator routers this app
    targets do not use 401/403 the way the HTTP spec suggests. Measured against the real
    fleet: XKiro answers "This is a paid model. The Free plan only allows free models" with
    403, and TokenRouter answers "User's credit limit is insufficient" with 403. Both are
    billing walls behind a perfectly valid key. Reading them as auth failures mislabelled
    them in the UI *and* fed the provider-wide auth short-circuit, which then skipped the rest
    of the catalogue - including the free models that do work.
    """
    text = (message or "").lower()
    code_match = _PROBE_HTTP_RE.search(message or "")
    code = code_match.group(1) if code_match else ""

    # --- Body semantics first: these are unambiguous regardless of the status code. ---
    # `plan` is tested before `billing` because it is the more specific claim and the two
    # overlap in wording. "This is a paid model. The Free plan only allows free models" also
    # says "top up your wallet", but the actionable advice is "use the :free variant", not
    # "you have spent your credits".
    if any(k in text for k in ("paid plan", "paid model", "free plan only allows", "not covered by a plan",
                               "plan restriction", "not available on your", "plan does not allow",
                               "subscribe to a plan", "upgrade your plan", "premium model")):
        return "plan"
    if any(k in text for k in ("balance depleted", "insufficient balance", "insufficient credit",
                               "insufficient_balance", "no credits", "payment required",
                               "out of credits", "requires credits", "credit limit is insufficient",
                               "top up your wallet", "deposited balance", "saldo tidak cukup",
                               "never purchased credits", "quota_exceeded")):
        return "billing"
    # OpenRouter refuses models that clash with the account's privacy/guardrail settings. It is
    # a 404, but it is fixable in one click, so it must not hide among the genuine 404s.
    if "data policy" in text or "guardrail restrictions" in text:
        return "policy"
    # A daily free-tier allowance is not a transient burst; retrying it is wasted work.
    if "per-day" in text or "per day" in text or "daily limit" in text:
        return "quota"
    if any(k in text for k in ("unauthorized client", "invalid token", "token not provided",
                               "invalid api key", "no auth credentials", "user not found")):
        return "auth"

    # --- Status codes second. ---
    if code == "402":
        return "billing"
    if code in ("401", "403") or "unauthorized" in text:
        return "auth"
    if code == "429" or "rate limit" in text:
        return "rate_limited"
    # 409 is a router telling us an identical request is still in flight. It literally says
    # "please try again", so it belongs with the retryable answers, not with dead models.
    if code == "409" or "duplicate request" in text:
        return "rate_limited"
    if code == "404" or "not found" in text or "does not exist" in text or "no such model" in text:
        return "missing"
    # Not every entry on a /models list is a chat model: TTS, image, batch-only and
    # "Interactions API only" endpoints answer 400. They are not broken, they are the wrong
    # shape, and saying so keeps them out of the "something is wrong" bucket.
    if any(k in text for k in ("only supports", "only available through", "response modalities",
                               "invalid argument", "not supported by the model",
                               "unsupported model", "does not support chat")):
        return "unsupported"
    if "timeout" in text or "timed out" in text or "readtimeout" in text or "connecttimeout" in text:
        return "timeout"
    if code.startswith("5"):
        return "server"
    if "empty token content" in text or "no choices" in text:
        return "empty"
    return "other"


# Reasons that mean "the credential itself was rejected". Only these may count toward the
# provider-wide auth short-circuit; a billing or plan wall says nothing about the key.
AUTH_SHORTCIRCUIT_REASONS = {"auth"}
# Reasons worth a second attempt. A daily quota or a billing wall will not change on retry.
RETRYABLE_REASONS = {"rate_limited", "server", "timeout"}
# Reasons that survive the inline retries but are still only evidence of congestion, never of a
# broken model. These entries are held back from the results and re-probed serially once the
# sweep has finished and the provider is quiet again - the inline retries happen while five
# sibling workers are still hammering the same host, so they frequently cannot succeed.
DEFERRABLE_REASONS = {"rate_limited", "server", "timeout"}
# Consecutive "this account never purchased credits" answers before the sweep stops probing
# that provider's *paid* models. Free models keep being probed.
DISCOVERY_BILLING_FAILURE_THRESHOLD = 12
# A "free-models-per-day" cap is an account-level fact, so a second one confirms the first.
DISCOVERY_QUOTA_FAILURE_THRESHOLD = 2


def _looks_free(model_id: str, display_name: str, raw_item: Any) -> bool:
    """Best-effort free-tier detection so a billing failure reads as a billing failure."""
    haystack = f"{model_id} {display_name}".lower()
    if ":free" in haystack or "(free)" in haystack or "free" in haystack.split("/")[-1].split("-"):
        return True
    if isinstance(raw_item, dict):
        pricing = raw_item.get("pricing")
        if isinstance(pricing, dict):
            values = [pricing.get("prompt"), pricing.get("completion")]
            parsed = []
            for v in values:
                try:
                    parsed.append(float(v))
                except (TypeError, ValueError):
                    parsed = []
                    break
            if parsed and all(v == 0 for v in parsed):
                return True
    return False


# --- Capability tiering -----------------------------------------------------------------
# A verified-online list of 90 models is not usable if the person choosing has to recognise
# 90 names. Tier is derived from the model's *identity*, not its latency: what predicts the
# quality of a debate turn is which model family answered, and a 4b safety classifier that
# replies in 700ms would top any speed-based ranking while being useless as a debater.
# Latency is surfaced separately in the UI so it stays a distinct axis.
#
# Matched on the id and display name, most specific signal first. Deliberately conservative:
# anything unrecognised lands in "mid" rather than being flattered into "top" or buried in
# "low", because an unknown name is far more likely to be a general chat model than either.
#
# Size tokens are written dash-delimited (`-mini-`, not `mini`) and matched against a haystack
# whose separators have been collapsed to dashes. Bare substrings do not work here: `mini` is
# inside both `minimax` and `gemini`, so `minimax/minimax-m2.7` and `gemini-3.5-pro` were both
# being demoted as small variants of themselves.
_TIER_SPECIAL_PURPOSE = (
    # Bare substrings here, not dash-delimited: vendors glue these onto family names
    # (`diffusiongemma`, `nemoguard`), so requiring a delimiter would miss them.
    "guard", "safety", "moderation", "shield", "translate", "tts", "-stt", "whisper",
    "embed", "rerank", "ocr", "image", "imagen", "lyria", "veo", "diffusion", "clip",
    "music", "audio", "speech", "sora", "vision-only",
)
_TIER_FLAGSHIP = (
    "opus", "gpt-5.6", "gpt-5.5", "gpt-5-pro", "o3-pro", "grok-4", "grok-5",
    "deepseek-v4", "deepseek-r2", "qwen3.7-max", "qwen3.8-max", "qwen-max",
    "mistral-large", "minimax-m2", "glm-5", "kimi-k2", "command-a",
    "llama-4-maverick", "ox-alpha",
    "gemini-3.5-pro", "gemini-3.6-pro", "gemini-3.7-pro", "gemini-3-pro",
)
_TIER_STRONG_MID = (
    "sonnet", "gpt-5.4", "gpt-oss-120b", "-120b-", "-70b-", "-72b-", "-90b-",
    "-pro-", "qwen3.7-plus", "qwen-plus", "-medium-", "nemotron-3-super", "mimo-v2",
    "glm-4", "step-3",
)
_TIER_SMALL = (
    "-haiku-", "-nano-", "-mini-", "-lite-", "-tiny-", "-small-", "-1b-", "-2b-", "-3b-",
    "-4b-", "-7b-", "-8b-", "-9b-", "-1.5b-", "-0.5b-", "gemma", "phi-", "instruct-v1",
)
# Parameter count is a family-independent capability signal, and named-family lists cannot keep
# up with router catalogues: the live sweep surfaced `nvidia/nemotron-3-ultra-550b-a55b:free`,
# which no flagship token matched and which sat in "mid" next to 27b models. The threshold reads
# the *total* count and ignores the MoE active count (the `a55b` half), because that is the
# figure that tracks how much knowledge the model carries into a debate.
_TIER_HUGE_PARAMS_RE = re.compile(r"-(\d{3,4})b-")
_TIER_HUGE_PARAMS_MIN = 300


def classify_model_tier(model_id: str, display_name: str = "") -> str:
    """
    Returns "top" | "mid" | "low" for the wizard's pre-classification.

    Order matters:

    1. Special-purpose first, because names like
       `nvidia/llama-3.1-nemoguard-8b-content-safety` carry a flagship family token
       (`llama-3.1`) and would otherwise be tiered on the strength of a model they merely
       resemble. A safety classifier is not a debater at any size.
    2. Flagship next, by named family or by sheer parameter count, but a flagship family
       shipped as a small variant is demoted to mid: `gpt-5.6-nano` argues nothing like
       `gpt-5.6`, so carrying both signals means mid.
    3. Small-variant tokens on a non-flagship family mean low.
    4. Everything else is mid - including unrecognised names, which are far more likely to be
       ordinary chat models than either frontier or trivial.
    """
    # Separators collapse to dashes and the whole string is dash-wrapped, so a token written
    # `-mini-` matches `gpt-5.6-mini` and `Nemotron Mini 4B` but not `minimax` or `gemini`.
    # Dots survive on purpose: version numbers like `gpt-5.6` and `qwen3.7-max` are the signal.
    haystack = "-" + re.sub(r"[^a-z0-9.]+", "-", f"{model_id} {display_name}".lower()).strip("-") + "-"

    if any(token in haystack for token in _TIER_SPECIAL_PURPOSE):
        return "low"

    huge = any(int(m) >= _TIER_HUGE_PARAMS_MIN for m in _TIER_HUGE_PARAMS_RE.findall(haystack))
    small = any(token in haystack for token in _TIER_SMALL)
    if huge or any(token in haystack for token in _TIER_FLAGSHIP):
        # A flagship family shipped in a small variant is a mid-tier debater, not a frontier
        # one: `gpt-5.6-nano` argues nothing like `gpt-5.6`.
        return "mid" if small else "top"
    if small:
        return "low"
    if any(token in haystack for token in _TIER_STRONG_MID):
        return "mid"
    return "mid"


def _prune_discovery_jobs() -> None:
    now = time.time()
    for job_id in [j for j, rec in DISCOVERY_JOBS.items()
                   if now - rec.get("created_at", now) > DISCOVERY_JOB_TTL_SECONDS]:
        DISCOVERY_JOBS.pop(job_id, None)
    while len(DISCOVERY_JOBS) > 12:
        DISCOVERY_JOBS.pop(next(iter(DISCOVERY_JOBS)))


async def _fetch_provider_catalogue(template: dict, key: str) -> Dict[str, Any]:
    """
    Lists every model a provider advertises on GET {base_url}/models.

    This used to run with a 4s timeout inside a bare `except Exception: pass`, so a provider
    that was merely slow - or, far more commonly on Windows, whose TLS chain could not be
    verified because a local security suite intercepts HTTPS - had its entire catalogue
    silently discarded and the wizard fell back to the 1-5 curated entries with no indication
    anything had been lost. The outcome is now reported per provider.

    Two provider behaviours discovered by probing the real fleet are handled here:

    * AgentRouter fingerprints the client. A request carrying our own User-Agent is answered
      with `401 {"error":{"message":"unauthorized client detected"}}` even though the key is
      valid, while the exact same request carrying the UA in UNIVERSAL_HEADERS returns 200.
      That is why chat completions worked while the catalogue 401'd - the two code paths were
      sending different headers. They now share one header set.
    * TokenRouter rate-limits GET /models itself, so a single 429 used to cost its entire
      128-model catalogue. Retried with backoff.
    """
    base_url = template["base_url"].rstrip("/")
    report = {
        "provider_id": template["provider_id"],
        "provider_name": template["provider_name"],
        "dynamic_listed": 0,
        "curated_count": len(template["models"]),
        "error": None,
    }
    dynamic: List[dict] = []

    try:
        headers = dict(UniversalAIClient.UNIVERSAL_HEADERS)
        headers.pop("Content-Type", None)   # no body on a GET
        headers["Authorization"] = f"Bearer {key}"

        resp = None
        async with build_async_client(timeout=DISCOVERY_CATALOGUE_TIMEOUT_SECONDS) as client:
            for attempt in range(DISCOVERY_CATALOGUE_RETRIES + 1):
                resp = await client.get(f"{base_url}/models", headers=headers)
                if resp.status_code not in (429, 500, 502, 503, 504):
                    break
                if attempt == DISCOVERY_CATALOGUE_RETRIES:
                    break
                await asyncio.sleep(_retry_after_seconds(resp, 1.5 * (attempt + 1)))

        if resp is None or resp.status_code != 200:
            code = resp.status_code if resp is not None else "?"
            body = resp.text[:160] if resp is not None else ""
            report["error"] = f"HTTP {code} listing /models: {body}"
            return {"report": report, "models": dynamic}

        payload = resp.json()
        if isinstance(payload, list):
            raw_list = payload
        elif isinstance(payload, dict):
            raw_list = payload.get("data") or payload.get("models") or []
        else:
            raw_list = []
        if not isinstance(raw_list, list):
            report["error"] = "Provider returned an unexpected /models payload shape."
            return {"report": report, "models": dynamic}

        if DISCOVERY_MAX_DYNAMIC_PER_PROVIDER > 0:
            raw_list = raw_list[:DISCOVERY_MAX_DYNAMIC_PER_PROVIDER]

        curated_ids = {str(t.get("model_id")) for t in template["models"]}
        for item in raw_list:
            m_id = item.get("id") if isinstance(item, dict) else item
            if not isinstance(m_id, str) or not m_id.strip():
                continue
            m_id = m_id.strip()
            # Google lists ids as "models/gemini-3-flash-preview" but accepts either form on
            # chat/completions. Left prefixed, every curated Gemini entry was probed twice
            # because "gemini-3.5-flash-lite" != "models/gemini-3.5-flash-lite".
            if m_id.startswith("models/"):
                m_id = m_id[len("models/"):]
            if not m_id or m_id in curated_ids:
                continue
            raw_name = item.get("name") if isinstance(item, dict) else None
            display_name = (
                raw_name.strip()
                if isinstance(raw_name, str) and raw_name.strip()
                else m_id.split("/")[-1].replace("-", " ").title()
            )
            dynamic.append({
                "id": m_id.replace("/", "-").replace(":", "-"),
                "name": display_name,
                "model_id": m_id,
                "fallback_models": [],
                "is_dynamic": True,
                "is_free": _looks_free(m_id, display_name, item),
            })
        report["dynamic_listed"] = len(dynamic)
    except Exception as e:
        report["error"] = f"{type(e).__name__}: {e}"

    return {"report": report, "models": dynamic}


async def _build_discovery_plan(provider_keys: Dict[str, str], scope: str = "all"):
    """
    Phase 1: build the full probe plan. Cheap - one GET /models per provider, in parallel.

    `scope` is "all" (probe every advertised model) or "quick" (curated favourites plus
    free-flagged models only). The catalogue is always listed in full either way, so the
    wizard can tell the user exactly how many models a quick scan chose not to probe.

    Returns (test_tasks, catalogue_reports, discovery_refs, skipped_by_scope).
    """
    templates_by_id = {t["provider_id"]: t for t in PROVIDER_TEMPLATES}

    # A provider id the wizard sends that we have no template for used to reach
    # `next(item for item in PROVIDER_TEMPLATES if ...)` with no default, raising
    # StopIteration and surfacing as a bare 500 "Internal Server Error".
    unknown_providers = sorted(p for p, k in provider_keys.items() if k and p not in templates_by_id)

    discovery_refs = {
        provider: secrets.token_urlsafe(18)
        for provider, key in provider_keys.items()
        if key and provider in templates_by_id
    }
    for provider, ref in discovery_refs.items():
        DISCOVERY_CREDENTIALS[ref] = {
            "key": provider_keys[provider],
            "base_url": templates_by_id[provider]["base_url"],
        }
    while len(DISCOVERY_CREDENTIALS) > 128:
        DISCOVERY_CREDENTIALS.pop(next(iter(DISCOVERY_CREDENTIALS)))

    try:
        admin_configs = await UserConfigStorage.get_user_config()
    except Exception as e:
        print(f"[auto-discover] Could not load admin config, continuing without favorites: {e}")
        admin_configs = []
    admin_model_ids = {m.model_id.lower() for m in admin_configs}
    admin_names = {m.name.lower() for m in admin_configs}

    active = [(templates_by_id[p], k) for p, k in provider_keys.items() if k and p in templates_by_id]
    catalogues = await asyncio.gather(
        *[_fetch_provider_catalogue(tmpl, key) for tmpl, key in active],
        return_exceptions=True
    )

    catalogue_reports = []
    for provider_id in unknown_providers:
        catalogue_reports.append({
            "provider_id": provider_id,
            "provider_name": provider_id,
            "dynamic_listed": 0,
            "curated_count": 0,
            "error": "Unknown provider id - no template is registered for it. Key ignored.",
        })

    test_tasks = []
    seen_model_keys = set()

    for (template, key), catalogue in zip(active, catalogues):
        p_id = template["provider_id"]
        base_url = template["base_url"].rstrip("/")

        if isinstance(catalogue, Exception):
            catalogue_reports.append({
                "provider_id": p_id,
                "provider_name": template["provider_name"],
                "dynamic_listed": 0,
                "curated_count": len(template["models"]),
                "error": f"{type(catalogue).__name__}: {catalogue}",
            })
            dynamic_models = []
        else:
            catalogue_reports.append(catalogue["report"])
            dynamic_models = catalogue["models"]

        # Curated entries first so the known-good fleet is probed before the long tail, then
        # free models ahead of paid ones. Two reasons: the wizard shows usable results sooner,
        # and on a mostly-paid catalogue (XKiro lists 92 models of which only the ":free" ones
        # are usable on a free plan) an early success permanently disarms the provider-wide
        # auth short-circuit instead of the sweep giving up on the provider first.
        ordered_dynamic = sorted(dynamic_models, key=lambda m: not bool(m.get("is_free")))
        for m_item in list(template["models"]) + ordered_dynamic:
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
                is_admin_fav = m_model_id.lower() in admin_model_ids or m_name.lower() in admin_names

                cfg = ModelConfig(
                    id=f"m_{p_id}_{m_slug}",
                    name=m_name,
                    base_url=template["base_url"],
                    api_key=key,
                    credential_ref=discovery_refs.get(p_id),
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
                # The probe also drops the curated fallback chain, deliberately. test_connectivity
                # walks every candidate id and reports the *last* error, so a curated row whose
                # primary id was merely throttled could be published with its fallback's verdict
                # instead - `gemini-3.7-flash` came back labelled "needs paid plan" from an error
                # raised against `gemini-3.5-flash`, and the throttle that actually happened never
                # reached the second-chance pass. Nothing is lost by probing one id: the sweep
                # already enumerates every id the provider advertises as its own row, and the
                # returned cfg still carries the fallbacks for debate-time resilience.
                probe_cfg = cfg.model_copy(update={
                    "timeout_seconds": DISCOVERY_PROBE_TIMEOUT_SECONDS,
                    "fallback_model_ids": [],
                })
                test_tasks.append({
                    "cfg": cfg,
                    "probe_cfg": probe_cfg,
                    "template": template,
                    "is_admin_favorite": is_admin_fav,
                    "is_dynamic": bool(m_item.get("is_dynamic", False)),
                    "is_free": bool(m_item.get("is_free", False)) or _looks_free(m_model_id, m_name, None),
                    "tier": classify_model_tier(m_model_id, m_name),
                })
            except Exception as e:
                print(f"[auto-discover] Skipped malformed model entry from {p_id}: {e}")
                continue

    skipped_by_scope = 0
    if scope == "quick":
        # Curated favourites plus anything the catalogue flags free. The paid long tail is what
        # makes a full sweep slow *and* uninformative on a free-plan key: 558 of the 822 rows in
        # the last full run were the same "no credits" answer. Favourites are kept regardless of
        # price because a paid-tier model the key genuinely reaches (AgentRouter's claude-opus-5)
        # is exactly what the user wants to find.
        kept = [e for e in test_tasks if e["is_admin_favorite"] or e["is_free"]]
        skipped_by_scope = len(test_tasks) - len(kept)
        test_tasks = kept

    return test_tasks, catalogue_reports, discovery_refs, skipped_by_scope


def _discovery_result(entry: dict, success: bool, latency_ms: float, message: str, reason: str) -> dict:
    return {
        "model": public_model(entry["cfg"]),
        "provider_name": entry["template"]["provider_name"],
        "provider_id": entry["template"]["provider_id"],
        "success": success,
        "latency_ms": round(latency_ms or 0.0, 2),
        "message": message,
        "reason": reason,
        "is_admin_favorite": entry["is_admin_favorite"],
        "is_dynamic": entry["is_dynamic"],
        "is_free": entry["is_free"],
        "tier": entry["tier"],
    }


async def _probe_discovery_entry(index: int, entry: dict, job: dict, global_sem: asyncio.Semaphore,
                                 provider_state: Dict[str, dict], allow_defer: bool = True,
                                 max_attempts: Optional[int] = None,
                                 probe_timeout: Optional[int] = None) -> None:
    p_id = entry["template"]["provider_id"]
    state = provider_state[p_id]

    if job.get("cancelled"):
        return

    # --- Account-level short-circuits ---------------------------------------------------
    # Each of these is a fact about the *account*, not about the model being probed, so once
    # established the answer for every remaining matching model is already known. Skipping
    # them is not just a speed win: a provider's free-model day allowance is a finite resource
    # that the sweep itself consumes, so continuing to spend it on requests whose answer is
    # already known is what makes genuinely working models look dead on the next run.
    skip_message: Optional[str] = None
    skip_reason = ""
    if state["auth_dead"]:
        # The provider rejected the *credential* on every model probed so far.
        skip_message = "Skipped: this provider rejected the API key on every model probed so far."
        skip_reason = "auth"
    elif state["quota_dead"] and entry["is_free"]:
        skip_message = ("Not probed: this provider's free-tier allowance for today is already "
                        "exhausted, so every remaining free model would answer the same. "
                        "Re-run the sweep after it resets.")
        skip_reason = "quota"
    elif state["billing_dead"] and not entry["is_free"]:
        skip_message = ("Not probed: this account has no credits, and every paid model probed so "
                        "far returned the same billing error.")
        # Only claimed when it is true. On a faucet-style provider where nothing is free-tier the
        # old unconditional "Free models were still tested." was simply a false statement.
        if state["has_free"]:
            skip_message += " Free models on this provider were still tested."
        skip_reason = "billing"

    if skip_message:
        result = _discovery_result(entry, False, 0.0, skip_message, skip_reason)
    else:
        probe_cfg = entry["probe_cfg"]
        if probe_timeout:
            probe_cfg = probe_cfg.model_copy(update={"timeout_seconds": probe_timeout})
        attempts = max_attempts if max_attempts else DISCOVERY_RATE_LIMIT_RETRIES + 1
        success, message, latency_ms, reason = False, "", 0.0, "other"
        async with global_sem:
            for attempt in range(attempts):
                if job.get("cancelled"):
                    return
                # Respect a cooldown another worker on this provider may have just set, so a
                # throttled host is not hammered by its remaining workers in lockstep.
                cooldown_left = state["cooldown_until"] - time.monotonic()
                if cooldown_left > 0:
                    await asyncio.sleep(min(cooldown_left, DISCOVERY_MAX_COOLDOWN_SECONDS))
                if job.get("cancelled"):
                    return
                try:
                    success, message, latency_ms, _key = await UniversalAIClient.test_connectivity(probe_cfg)
                except Exception as e:
                    success, message, latency_ms = False, f"Probe error: {type(e).__name__}: {e}", 0.0
                if success:
                    reason = "ok"
                    break
                reason = classify_probe_failure(message)
                if reason == "rate_limited":
                    backoff = min(
                        DISCOVERY_PROVIDER_COOLDOWN_SECONDS * (attempt + 1) + random.uniform(0.0, 1.0),
                        DISCOVERY_MAX_COOLDOWN_SECONDS,
                    )
                    state["cooldown_until"] = max(state["cooldown_until"], time.monotonic() + backoff)
                if reason not in RETRYABLE_REASONS or attempt == attempts - 1:
                    break
                await asyncio.sleep(1.5 * (attempt + 1) + random.uniform(0.0, 0.75))

        if success:
            state["successes"] += 1
            state["auth_failures"] = 0
            state["billing_failures"] = 0
            if not entry["is_free"]:
                state["paid_successes"] += 1
        elif reason in AUTH_SHORTCIRCUIT_REASONS:
            state["auth_failures"] += 1
            if (not state["auth_dead"]
                    and state["auth_failures"] >= DISCOVERY_AUTH_FAILURE_THRESHOLD
                    and state["successes"] == 0):
                state["auth_dead"] = True
                # Log only on the transition, never once per skipped model.
                print(f"[auto-discover] '{p_id}' rejected the key {state['auth_failures']}x with no "
                      f"successes; skipping its remaining models.")
        elif reason == "quota":
            state["quota_failures"] += 1
            state["auth_failures"] = 0
            if not state["quota_dead"] and state["quota_failures"] >= DISCOVERY_QUOTA_FAILURE_THRESHOLD:
                state["quota_dead"] = True
                print(f"[auto-discover] '{p_id}' reports its free-tier day allowance is spent; "
                      f"not spending further requests on its free models.")
        elif reason == "billing":
            state["billing_failures"] += 1
            state["auth_failures"] = 0
            if (not state["billing_dead"]
                    and state["billing_failures"] >= DISCOVERY_BILLING_FAILURE_THRESHOLD
                    and state["paid_successes"] == 0):
                state["billing_dead"] = True
                print(f"[auto-discover] '{p_id}' has no credit for paid models "
                      f"({state['billing_failures']} billing rejections, 0 paid successes); "
                      f"probing only its free models from here.")
        else:
            # A plan restriction or a missing model says nothing about the key, so it must not
            # push the provider toward the auth short-circuit. Before this, TokenRouter's 128
            # "credit limit is insufficient" 403s read as 128 auth failures and the provider was
            # abandoned after 6 - taking its working models with it.
            state["auth_failures"] = 0

        # Congestion is not a verdict. Hold the entry back for the quiet second-chance pass
        # instead of publishing "dead" for a model that was merely queued behind our own sweep.
        # The first-pass verdict travels with it, so if the retry pass runs out of time the model
        # is still reported with the real reason it failed rather than a vague "not verified".
        if allow_defer and not success and reason in DEFERRABLE_REASONS:
            job["deferred"].append((index, entry, message, reason, latency_ms))
            return

        result = _discovery_result(entry, success, latency_ms, message, reason)

    job["results"].append(result)
    job["done_indices"].add(index)
    if result["success"]:
        job["online"] += 1
    else:
        job["failed"] += 1


async def _run_discovery_job(job_id: str, test_tasks: List[dict]) -> None:
    job = DISCOVERY_JOBS.get(job_id)
    if job is None:
        return
    try:
        job["status"] = "probing"
        if not test_tasks:
            job["status"] = "finished"
            job["finished_at"] = time.time()
            return

        # Work is pulled by a bounded per-provider worker pool rather than fanned out as one
        # task per model. Creating 800+ tasks up front made every coroutine race past the
        # auth short-circuit check before the first 401 had even landed (so a dead key still
        # burned a probe on every model), and saturated the loop enough to drop the wizard's
        # own status polls. Workers re-check provider state on each iteration instead.
        queues: Dict[str, "asyncio.Queue"] = {}
        for i, entry in enumerate(test_tasks):
            p_id = entry["template"]["provider_id"]
            queues.setdefault(p_id, asyncio.Queue()).put_nowait((i, entry))

        global_sem = asyncio.Semaphore(DISCOVERY_GLOBAL_CONCURRENCY)
        free_per_provider = Counter(
            entry["template"]["provider_id"] for entry in test_tasks if entry["is_free"]
        )
        provider_state = {
            p: {
                "auth_failures": 0, "successes": 0, "auth_dead": False, "cooldown_until": 0.0,
                "billing_failures": 0, "paid_successes": 0, "billing_dead": False,
                "quota_failures": 0, "quota_dead": False,
                "has_free": free_per_provider.get(p, 0) > 0,
            }
            for p in queues
        }

        async def worker(queue: "asyncio.Queue") -> None:
            while not job.get("cancelled"):
                try:
                    index, entry = queue.get_nowait()
                except asyncio.QueueEmpty:
                    return
                await _probe_discovery_entry(index, entry, job, global_sem, provider_state)

        # Every provider gets its own lane, so one provider with 400 models can neither hog
        # the pool nor rate-limit itself into reporting working models as dead.
        workers = [
            asyncio.ensure_future(worker(queue))
            for queue in queues.values()
            for _ in range(min(DISCOVERY_PER_PROVIDER_CONCURRENCY, queue.qsize()))
        ]
        _done, pending = await asyncio.wait(workers, timeout=DISCOVERY_TOTAL_BUDGET_SECONDS)
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)

        # --- Second-chance pass -------------------------------------------------------------
        # Everything held back as congestion rather than failure, re-probed one provider-lane at
        # a time now that nothing else is competing for the host. Measured on the real fleet this
        # is where throttle-only false negatives were coming from - including curated favourites
        # like BluesMinds' claude-sonnet-5, which the parallel pass reported dead purely because
        # five sibling workers were saturating the same free-tier host.
        deferred = job.pop("deferred", [])
        job["deferred"] = []
        if deferred and not job.get("cancelled"):
            job["status"] = "retrying"
            elapsed = time.time() - job["created_at"]
            # Capped rather than "whatever is left of the 900s": on a real sweep the parallel pass
            # finished in 268s and an uncapped retry pass then spent 635s more on 51 models, which
            # is not a trade the person waiting on the wizard would choose.
            retry_budget = max(0.0, min(DISCOVERY_RETRY_BUDGET_SECONDS,
                                        DISCOVERY_TOTAL_BUDGET_SECONDS - elapsed))
            by_provider: Dict[str, List[tuple]] = {}
            for index, entry, _msg, _reason, _lat in deferred:
                by_provider.setdefault(entry["template"]["provider_id"], []).append((index, entry))
            for state in provider_state.values():
                state["cooldown_until"] = 0.0
            print(f"[auto-discover] Re-probing {len(deferred)} throttled models serially "
                  f"({len(by_provider)} providers, {round(retry_budget)}s cap).")

            async def retry_lane(items: List[tuple]) -> None:
                for index, entry in items:
                    if job.get("cancelled"):
                        return
                    await asyncio.sleep(1.0)
                    # One attempt, not the four-deep ladder: these entries already spent theirs
                    # in the parallel pass, and a second ladder each was what pushed the tail of
                    # this pass past the total budget (7 models published as "not verified").
                    # The timeout is raised instead, because nothing else is competing for the
                    # host now - BluesMinds' larger models (kimi-k2.5, gemma-4-26b) simply need
                    # longer than 25s to cold-start, and clipping them read as "dead".
                    await _probe_discovery_entry(index, entry, job, global_sem, provider_state,
                                                 allow_defer=False, max_attempts=1,
                                                 probe_timeout=DISCOVERY_RETRY_PROBE_TIMEOUT_SECONDS)

            retries = [asyncio.ensure_future(retry_lane(items)) for items in by_provider.values()]
            _rdone, rpending = await asyncio.wait(retries, timeout=retry_budget)
            for task in rpending:
                task.cancel()
            if rpending:
                await asyncio.gather(*rpending, return_exceptions=True)

        # Deferred entries the retry pass never reached keep their first-pass verdict. Falling
        # through to the "budget" branch below would replace a specific, actionable message
        # ("Rate Limited (HTTP 429)") with "not verified", which reads as our failure, not theirs.
        for index, entry, message, reason, latency_ms in deferred:
            if index in job["done_indices"]:
                continue
            job["results"].append(_discovery_result(entry, False, latency_ms, message, reason))
            job["done_indices"].add(index)
            job["failed"] += 1

        # Anything that never reported: budget elapsed or the sweep was cancelled.
        for i, entry in enumerate(test_tasks):
            if i in job["done_indices"]:
                continue
            if job.get("cancelled"):
                msg, reason = "Not probed: discovery was stopped.", "cancelled"
            else:
                msg = (f"Not verified: discovery budget of {DISCOVERY_TOTAL_BUDGET_SECONDS}s elapsed. "
                       f"Test this model individually.")
                reason = "budget"
                job["not_verified_count"] += 1
            job["results"].append(_discovery_result(entry, False, 0.0, msg, reason))
            job["done_indices"].add(i)
            job["failed"] += 1

        job["status"] = "cancelled" if job.get("cancelled") else "finished"
    except Exception as e:
        job["status"] = "error"
        job["error_message"] = f"{type(e).__name__}: {e}"
        print(f"[auto-discover] Job {job_id} crashed: {e}")
    finally:
        job["finished_at"] = time.time()


def _discovery_snapshot(job: dict, cursor: int = 0) -> dict:
    """Cursor-based so a 1s poll over a 300-model sweep stays a few KB, not 120KB."""
    results = job["results"]
    cursor = max(0, min(cursor, len(results)))
    new_results = results[cursor:]
    elapsed = (job.get("finished_at") or time.time()) - job["created_at"]
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "total": job["total"],
        "done": len(results),
        "online": job["online"],
        "failed": job["failed"],
        "not_verified_count": job["not_verified_count"],
        "elapsed_seconds": round(elapsed, 1),
        "catalogue": job["catalogue"],
        "results": new_results,
        "cursor": cursor + len(new_results),
        "finished": job["status"] in ("finished", "cancelled", "error"),
        "error_message": job.get("error_message"),
        "scope": job.get("scope", "all"),
        "skipped_by_scope": job.get("skipped_by_scope", 0),
    }


@app.post("/api/providers/auto-discover/start")
async def start_auto_discover(payload: Dict[str, Any] = {}):
    """
    Phase 1 (fast, awaited): list every model each provider advertises on GET /models.
    Phase 2 (background): live-probe all of them for availability and latency.

    `scope` in the body selects what phase 2 probes: "quick" (default - curated favourites plus
    free-flagged models) or "all" (every advertised model). Phase 1 always lists everything, so
    `skipped_by_scope` tells the wizard how many models a quick scan left untested.

    Returns immediately with a job_id and the total to probe; poll
    /api/providers/auto-discover/status/{job_id}?cursor=N for streamed results.
    """
    data = payload if isinstance(payload, dict) else {}
    raw_keys = data.get("provider_keys") or {}
    if not isinstance(raw_keys, dict):
        raw_keys = {}
    provider_keys = {
        str(k): (v.strip() if isinstance(v, str) else "")
        for k, v in raw_keys.items()
    }
    # Defaults to "quick": a full sweep is an 800-request, several-minute commitment that the
    # wizard now asks the user to confirm, so it must never be what an unspecified body gets.
    scope = "all" if str(data.get("scope") or "quick").lower() == "all" else "quick"

    test_tasks, catalogue_reports, _refs, skipped_by_scope = await _build_discovery_plan(
        provider_keys, scope
    )

    _prune_discovery_jobs()
    job_id = secrets.token_urlsafe(12)
    job = {
        "job_id": job_id,
        "created_at": time.time(),
        "finished_at": None,
        "status": "probing" if test_tasks else "finished",
        "total": len(test_tasks),
        "online": 0,
        "failed": 0,
        "not_verified_count": 0,
        "results": [],
        "done_indices": set(),
        # Entries held back from the parallel pass because their failure looked like congestion
        # rather than a verdict; drained serially by _run_discovery_job before it finishes.
        "deferred": [],
        "catalogue": catalogue_reports,
        "cancelled": False,
        "error_message": None,
        "scope": scope,
        "skipped_by_scope": skipped_by_scope,
    }
    DISCOVERY_JOBS[job_id] = job

    if test_tasks:
        asyncio.create_task(_run_discovery_job(job_id, test_tasks))
    else:
        job["finished_at"] = time.time()

    return _discovery_snapshot(job, 0)


@app.get("/api/providers/auto-discover/status/{job_id}")
async def auto_discover_status(job_id: str, cursor: int = 0):
    job = DISCOVERY_JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Discovery job not found or expired. Start a new sweep.")
    return _discovery_snapshot(job, cursor)


@app.post("/api/providers/auto-discover/cancel/{job_id}")
async def auto_discover_cancel(job_id: str):
    job = DISCOVERY_JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Discovery job not found or expired.")
    job["cancelled"] = True
    return {"job_id": job_id, "status": "cancelling", "done": len(job["results"]), "total": job["total"]}


@app.post("/api/providers/auto-discover")
async def auto_discover_models(payload: Dict[str, Any] = {}):
    """
    Blocking variant kept for compatibility: runs the same sweep and returns the completed
    split lists in one response. The wizard uses the /start + /status flow so it can show
    progress instead of appearing frozen for the length of a full sweep.
    """
    snapshot = await start_auto_discover(payload)
    job = DISCOVERY_JOBS.get(snapshot["job_id"])
    if job is None:
        raise HTTPException(status_code=500, detail="Discovery job vanished before it could run.")

    while job["status"] not in ("finished", "cancelled", "error"):
        await asyncio.sleep(0.4)

    available = sorted([r for r in job["results"] if r["success"]], key=lambda x: x["latency_ms"])
    unavailable = [r for r in job["results"] if not r["success"]]
    return {
        "available_models": available,
        "unavailable_models": unavailable,
        "discovered_models": available + unavailable,
        "admin_favorites_count": sum(1 for m in available if m["is_admin_favorite"]),
        "total_tested": job["total"],
        "not_verified_count": job["not_verified_count"],
        "catalogue": job["catalogue"],
    }


@app.post("/api/debate/start")
async def start_debate(req: StartDebateRequest):
    stored_models = {model.id: model for model in await UserConfigStorage.get_user_config()}
    hydrated_models = []
    used_credential_refs = set()
    for model in req.models:
        stored = stored_models.get(model.id)
        discovered_key = discovery_credential_for(model)
        if discovered_key and not model.api_key:
            model = model.model_copy(update={"api_key": discovered_key})
            used_credential_refs.add(model.credential_ref)
        if stored and not model.api_key:
            primary, backups = stored_credential_for(model, stored)
            model = model.model_copy(update={
                "api_key": primary,
                "backup_api_keys": model.backup_api_keys or backups,
            })
        hydrated_models.append(model)
    for ref in used_credential_refs:
        if ref:
            DISCOVERY_CREDENTIALS.pop(ref, None)
    req = req.model_copy(update={"models": hydrated_models})
    enabled_models = [m for m in req.models if m.enabled]
    if len(enabled_models) < 2:
        raise HTTPException(status_code=400, detail="At least 2 enabled participating AI models are required.")
    if len({m.id for m in req.models}) != len(req.models):
        raise HTTPException(status_code=400, detail="Model IDs must be unique.")
    if req.arbiter_model_id and req.backup_arbiter_model_id and req.arbiter_model_id == req.backup_arbiter_model_id:
        raise HTTPException(status_code=400, detail="Primary and backup arbiters must be distinct.")

    arbiter_id = req.arbiter_model_id
    if not arbiter_id or not any(m.id == arbiter_id and m.enabled for m in req.models):

        sol_model = next((m for m in req.models if m.id == "m3" or "gpt-5.6-sol" in m.model_id.lower() or m.is_arbiter), None)
        if sol_model and sol_model.enabled:
            arbiter_id = sol_model.id
        else:
            arbiter_model = next((m for m in req.models if m.is_arbiter and m.enabled), req.models[0])
            arbiter_id = arbiter_model.id

    backup_arbiter_id = req.backup_arbiter_model_id
    if not backup_arbiter_id:
        backup_candidate = next((m for m in req.models if (m.is_backup_arbiter or m.id == "m4" or "gemini-3.5-flash-lite" in m.model_id.lower()) and m.id != arbiter_id and m.enabled), None)
        if not backup_candidate:
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
        status="paused",
        current_phase_index=1,
        current_phase_title="Phase 1: Multi-Persona Genesis",
        current_pass_id="1.1",
        current_pass_title="Pass 1.1: Lead Architect Genesis",
        current_phase_prompt=full_problem_text
    )

    await SessionStorage.save_session(session)
    DebateOrchestrator.start_session(session.session_id, auto_advance=req.auto_advance)

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
    if not req.followup_prompt.strip():
        raise HTTPException(status_code=400, detail="followup_prompt is required.")
    current = await SessionStorage.get_session(session_id)
    if not current:
        raise HTTPException(status_code=404, detail="Debate session not found.")
    phase_title = req.phase_title or f"Phase {current.workspace_phase_number + 1} Specification"
    try:
        session = await DebateOrchestrator.start_followup(
            session_id,
            req.followup_prompt.strip(),
            phase_title,
            req.auto_advance,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "status": "running",
        "phase_index": session.workspace_phase_number,
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
                    "phases": [p.model_dump() for p in session.phases],
                    "models": [public_model(model) for model in session.models]
                })
            }

            while True:
                if await request.is_disconnected():
                    break

                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=5.0)
                    yield {
                        "event": event_data.get("event", "message"),
                        "data": json.dumps(event_data.get("data", {}), default=str)
                    }
                    if event_data.get("event") in {"DEBATE_COMPLETED", "DEBATE_ERROR", "SESSION_DELETED"}:
                        break
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
    return public_session(session)

@app.post("/api/debate/{session_id}/moderator")
async def handle_moderator_action(session_id: str, req: ModeratorActionRequest):
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")

    if req.action == "pause":
        await DebateOrchestrator.pause_debate(session_id)
    elif req.action == "resume":
        if session.status == "completed":
            raise HTTPException(status_code=409, detail="Completed sessions require a follow-up phase.")
        await DebateOrchestrator.resume_debate(session_id)
    elif req.action == "call_verdict":
        if session.status == "completed":
            raise HTTPException(status_code=409, detail="Session already has a completed verdict.")
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
    elif req.action == "enable_model":
        if not req.target_model_id:
            raise HTTPException(status_code=400, detail="target_model_id is required.")
        await DebateOrchestrator.enable_model(session_id, req.target_model_id)

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

@app.delete("/api/workspaces/{session_id}")
async def delete_workspace_endpoint(session_id: str):
    success = await DebateOrchestrator.stop_and_delete(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Debate session workspace not found.")
    return {"status": "success", "message": f"Deleted workspace for session {session_id}"}

@app.post("/api/debate/{session_id}/resume")
async def resume_debate_session(session_id: str):
    """
    Resumes a paused debate session. If the orchestrator background task
    has died (e.g. after backend restart), it re-spawns run_round_loop
    from the correct next pipeline step.
    """
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Session is already completed. Cannot resume.")

    await DebateOrchestrator.resume_debate(session_id, auto_advance=True)
    return {
        "status": "resuming",
        "session_id": session_id,
        "current_pass_id": session.current_pass_id,
        "current_pass_title": session.current_pass_title,
        "rounds_completed": len(session.rounds)
    }

@app.get("/api/debate/{session_id}/status")
async def get_session_status(session_id: str):
    """
    Lightweight endpoint returning only the current status fields.
    Used by the frontend for quick polling without fetching full session.
    """
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")
    score = 0
    if session.rounds:
        for r in reversed(session.rounds):
            if r.arbiter_eval and r.arbiter_eval.consensus_score:
                score = r.arbiter_eval.consensus_score
                break

    return {
        "session_id": session_id,
        "status": session.status,
        "current_phase_index": session.current_phase_index,
        "current_pass_id": session.current_pass_id,
        "current_pass_title": session.current_pass_title,
        "rounds_count": len(session.rounds),
        "consensus_score": score,
        "session_title": session.session_title,
        "ps_code": session.ps_code,
    }



@app.get("/api/workspaces/{session_id}/files/{filename}")
async def download_workspace_file(session_id: str, filename: str):
    session = await SessionStorage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debate session not found.")

    workspace_dir = SessionStorage.get_workspace_dir(session)
    safe_filename = os.path.basename(filename)
    if safe_filename == "session_state.json" or not safe_filename.lower().endswith((".md", ".txt", ".pdf")):
        raise HTTPException(status_code=403, detail="Only workspace deliverables can be downloaded.")
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

