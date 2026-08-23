import json
import os
import re
import asyncio
from typing import Dict, Optional, List
from app.schemas import DebateSession, ModelConfig, WorkspacePhase

WORKSPACES_ROOT = os.path.join(os.path.dirname(__file__), "..", "data", "workspaces")
USER_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "user_config.json")
os.makedirs(WORKSPACES_ROOT, exist_ok=True)
os.makedirs(os.path.dirname(USER_CONFIG_PATH), exist_ok=True)

class UserConfigStorage:
    _lock = asyncio.Lock()
    _default_models = [
        { "id": "m1", "name": "Claude Opus 4.8", "base_url": "https://agentrouter.org/v1", "api_key": "", "backup_api_keys": [], "model_id": "claude-opus-4-8", "timeout_seconds": 600, "is_arbiter": True, "enabled": True, "temperature": 0.7 },
        { "id": "m2", "name": "Claude Opus 5.0", "base_url": "https://agentrouter.org/v1", "api_key": "", "backup_api_keys": [], "model_id": "claude-opus-5", "timeout_seconds": 600, "is_arbiter": False, "enabled": True, "temperature": 0.6 },
        { "id": "m3", "name": "GPT 5.6 Sol", "base_url": "https://agentrouter.org/v1", "api_key": "", "backup_api_keys": [], "model_id": "gpt-5.6-sol", "timeout_seconds": 600, "is_arbiter": False, "enabled": True, "temperature": 0.7 },
        { "id": "m4", "name": "Gemini 3.5 Flash Lite", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "api_key": "", "backup_api_keys": [], "model_id": "gemini-3.5-flash-lite", "fallback_model_ids": ["gemini-flash-lite-latest"], "timeout_seconds": 600, "is_arbiter": False, "enabled": True, "temperature": 0.7 },
        { "id": "m5", "name": "Gemini Flash Quota Pool (3.7 / 3.6 / 3.5)", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "api_key": "", "backup_api_keys": [], "model_id": "gemini-3.7-flash", "fallback_model_ids": ["gemini-3.6-flash", "gemini-3.5-flash"], "timeout_seconds": 600, "is_arbiter": False, "enabled": True, "temperature": 0.7 },
        { "id": "m6", "name": "GLM 5.2 (Free)", "base_url": "https://openrouter.ai/api/v1", "api_key": "", "backup_api_keys": [], "model_id": "z-ai/glm-5.2:free", "timeout_seconds": 600, "is_arbiter": False, "enabled": True, "temperature": 0.7 },
        { "id": "m7", "name": "NVIDIA Nemotron 3 Super 120B (Free)", "base_url": "https://openrouter.ai/api/v1", "api_key": "", "backup_api_keys": [], "model_id": "nvidia/nemotron-3-super-120b-a12b:free", "timeout_seconds": 600, "is_arbiter": False, "enabled": True, "temperature": 0.7 },
        { "id": "m8", "name": "Stealth Ox-Alpha", "base_url": "https://openrouter.ai/api/v1", "api_key": "", "backup_api_keys": [], "model_id": "stealth/ox-alpha", "timeout_seconds": 600, "is_arbiter": False, "enabled": True, "temperature": 0.7 },
        { "id": "m9", "name": "NVIDIA Nemotron 3.5 Lightning (Free)", "base_url": "https://openrouter.ai/api/v1", "api_key": "", "backup_api_keys": [], "model_id": "nvidia/nemotron-3.5-lightning:free", "timeout_seconds": 600, "is_arbiter": False, "enabled": True, "temperature": 0.7 },
        { "id": "m10", "name": "Qwen 3.8 Max (Free)", "base_url": "https://api.tokenrouter.com/v1", "api_key": "", "backup_api_keys": [], "model_id": "qwen/qwen3.8-max-free", "timeout_seconds": 600, "is_arbiter": False, "enabled": True, "temperature": 0.7 },
        { "id": "m11", "name": "Claude Sonnet 5 (BluesMinds)", "base_url": "https://api.bluesminds.com/v1", "api_key": "", "backup_api_keys": [], "model_id": "unlimited/claude-sonnet-5", "timeout_seconds": 600, "is_arbiter": False, "enabled": True, "temperature": 0.7 }
    ]

    @classmethod
    async def get_user_config(cls) -> List[ModelConfig]:
        async with cls._lock:
            if os.path.exists(USER_CONFIG_PATH):
                try:
                    with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list) and len(data) > 0:
                            return [ModelConfig(**m) for m in data]
                except Exception as e:
                    print(f"Error loading user_config.json: {e}")
            return [ModelConfig(**m) for m in cls._default_models]

    @classmethod
    async def save_user_config(cls, models: List[ModelConfig]):
        async with cls._lock:
            try:
                with open(USER_CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump([m.model_dump() for m in models], f, indent=2)
            except Exception as e:
                print(f"Error saving user_config.json: {e}")

def sanitize_folder_name(name: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9_\-\s]', '', name).strip().replace(' ', '_')
    return cleaned[:40] if cleaned else "workspace"

class SessionStorage:
    _memory_cache: Dict[str, DebateSession] = {}
    _lock = asyncio.Lock()

    @classmethod
    def get_workspace_dir(cls, session: DebateSession) -> str:
        folder_slug = f"{sanitize_folder_name(session.session_title)}_{session.session_id}"
        workspace_path = os.path.join(WORKSPACES_ROOT, folder_slug)
        os.makedirs(workspace_path, exist_ok=True)
        session.workspace_folder = workspace_path
        return workspace_path

    @classmethod
    async def save_session(cls, session: DebateSession):
        async with cls._lock:
            cls._memory_cache[session.session_id] = session
            workspace_dir = cls.get_workspace_dir(session)
            
            # 1. Save JSON session state
            state_file = os.path.join(workspace_dir, "session_state.json")
            try:
                with open(state_file, "w", encoding="utf-8") as f:
                    json.dump(session.model_dump(), f, indent=2)
            except Exception as e:
                print(f"Error persisting session state to disk: {e}")

            # 2. Save Phase Markdown files into the workspace folder
            for phase in session.phases:
                phase_filename = phase.verdict_filename or f"phase_{phase.phase_index}_{sanitize_folder_name(phase.phase_title)}.md"
                phase_path = os.path.join(workspace_dir, phase_filename)
                try:
                    with open(phase_path, "w", encoding="utf-8") as f:
                        f.write(phase.verdict_markdown)
                except Exception as e:
                    print(f"Error saving phase file {phase_filename}: {e}")

            # 3. Save latest final report
            if session.final_markdown_report:
                main_verdict_path = os.path.join(workspace_dir, "LATEST_CONSENSUS_VERDICT.md")
                try:
                    with open(main_verdict_path, "w", encoding="utf-8") as f:
                        f.write(session.final_markdown_report)
                except Exception as e:
                    print(f"Error saving main verdict file: {e}")

    @classmethod
    async def get_session(cls, session_id: str) -> Optional[DebateSession]:
        async with cls._lock:
            if session_id in cls._memory_cache:
                return cls._memory_cache[session_id]
            
            # Search workspace folders
            if os.path.exists(WORKSPACES_ROOT):
                for folder in os.listdir(WORKSPACES_ROOT):
                    folder_path = os.path.join(WORKSPACES_ROOT, folder)
                    if os.path.isdir(folder_path):
                        state_path = os.path.join(folder_path, "session_state.json")
                        if os.path.exists(state_path):
                            try:
                                with open(state_path, "r", encoding="utf-8") as f:
                                    data = json.load(f)
                                    if data.get("session_id") == session_id:
                                        session = DebateSession(**data)
                                        cls._memory_cache[session_id] = session
                                        return session
                            except Exception as e:
                                print(f"Error reading session {session_id}: {e}")
            return None

    @classmethod
    async def list_workspaces(cls) -> List[Dict]:
        async with cls._lock:
            workspaces = []
            if not os.path.exists(WORKSPACES_ROOT):
                return []

            for folder in os.listdir(WORKSPACES_ROOT):
                folder_path = os.path.join(WORKSPACES_ROOT, folder)
                if os.path.isdir(folder_path):
                    state_path = os.path.join(folder_path, "session_state.json")
                    if os.path.exists(state_path):
                        try:
                            with open(state_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                files = [f for f in os.listdir(folder_path) if f.endswith(".md") or f.endswith(".json")]
                                workspaces.append({
                                    "session_id": data.get("session_id"),
                                    "session_title": data.get("session_title", folder),
                                    "folder_name": folder,
                                    "folder_path": folder_path,
                                    "problem_statement": data.get("problem_statement", "")[:90] + "...",
                                    "current_phase": data.get("current_phase_index", 1),
                                    "phases_count": len(data.get("phases", [])),
                                    "total_rounds": data.get("current_round_num", 0),
                                    "status": data.get("status", "completed"),
                                    "files": files,
                                    "created_at": data.get("created_at")
                                })
                        except Exception:
                            pass
            return workspaces
