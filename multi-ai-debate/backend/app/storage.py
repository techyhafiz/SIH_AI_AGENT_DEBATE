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
        {
                "id": "m1",
                "name": "Claude Opus 4.8",
                "base_url": "https://agentrouter.org/v1",
                "api_key": "",
                "backup_api_keys": [
                        ""
                ],
                "model_id": "claude-opus-4-8",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m2",
                "name": "Claude Opus 5.0",
                "base_url": "https://agentrouter.org/v1",
                "api_key": "",
                "backup_api_keys": [
                        ""
                ],
                "model_id": "claude-opus-5",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.6
        },
        {
                "id": "m3",
                "name": "GPT 5.6 Sol",
                "base_url": "https://agentrouter.org/v1",
                "api_key": "sk-6FoEw2n9eRBjlyttLte6FOyhaeG1DNlmEnba1vcZhEHUuD77",
                "backup_api_keys": [
                        ""
                ],
                "model_id": "gpt-5.6-sol",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m4",
                "name": "Gemini 3.5 Flash Lite",
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "gemini-3.5-flash-lite",
                "fallback_model_ids": [
                        "gemini-flash-lite-latest"
                ],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": True,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m5",
                "name": "Gemini Flash Quota Pool (3.7 / 3.6 / 3.5)",
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "gemini-3.7-flash",
                "fallback_model_ids": [
                        "gemini-3.6-flash",
                        "gemini-3.5-flash"
                ],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m6",
                "name": "GLM 5.2 (Free)",
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "z-ai/glm-5.2:free",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m7",
                "name": "NVIDIA Nemotron 3 Super 120B (Free)",
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "nvidia/nemotron-3-super-120b-a12b:free",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m8",
                "name": "Stealth Ox-Alpha",
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "stealth/ox-alpha",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m9",
                "name": "NVIDIA Nemotron 3.5 Lightning (Free)",
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "nvidia/nemotron-3.5-lightning:free",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m10",
                "name": "Qwen 3.8 Max (Free)",
                "base_url": "https://api.tokenrouter.com/v1",
                "api_key": "",
                "backup_api_keys": [
                        ""
                ],
                "model_id": "qwen/qwen3.8-max-free",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m11",
                "name": "Claude Sonnet 5 (BluesMinds)",
                "base_url": "https://api.bluesminds.com/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "unlimited/claude-sonnet-5",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m12",
                "name": "Mimo v2.5 (TokenFaucet)",
                "base_url": "https://freetokenfaucet.com/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "mimo-v2.5",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m13",
                "name": "GPT 5.6 Terra (TokenFaucet)",
                "base_url": "https://freetokenfaucet.com/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "gpt-5.6-terra",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m14",
                "name": "GPT 5.6 Luna (TokenFaucet)",
                "base_url": "https://freetokenfaucet.com/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "gpt-5.6-luna",
                "fallback_model_ids": [],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m15",
                "name": "DeepSeek V4 Pro (XKiro)",
                "base_url": "https://api.xkiro.com/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "deepseek/deepseek-v4-pro",
                "fallback_model_ids": [
                        "deepseek/deepseek-v4-flash",
                        "deepseek/deepseek-chat-v3.1"
                ],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m16",
                "name": "Qwen 3.8 Max (XKiro)",
                "base_url": "https://api.xkiro.com/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "qwen/qwen3.8-max",
                "fallback_model_ids": [
                        "qwen/qwen3.7-max",
                        "qwen/qwen3.7-plus"
                ],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m17",
                "name": "Mistral Large 2512 (XKiro)",
                "base_url": "https://api.xkiro.com/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "mistralai/mistral-large-2512",
                "fallback_model_ids": [
                        "mistralai/mistral-medium-3.5",
                        "mistralai/codestral-2508"
                ],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m18",
                "name": "Qwen 3.7 Max (XKiro)",
                "base_url": "https://api.xkiro.com/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "qwen/qwen3.7-max",
                "fallback_model_ids": [
                        "qwen/qwen3.7-plus"
                ],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m19",
                "name": "MiniMax M2.7 (XKiro)",
                "base_url": "https://api.xkiro.com/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "minimax/minimax-m2.7",
                "fallback_model_ids": [
                        "minimax/minimax-m2.5-highspeed",
                        "minimax/minimax-m2.1-highspeed"
                ],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m20",
                "name": "Gemini 3.5 Flash Free (TokenIn)",
                "base_url": "https://tokenin.my.id/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "myt/gemini-3.5-flash-free",
                "fallback_model_ids": [
                        "myt/mimo-v2.5-free"
                ],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        },
        {
                "id": "m21",
                "name": "Claude Opus 4.8 Free (TokenIn)",
                "base_url": "https://tokenin.my.id/v1",
                "api_key": "",
                "backup_api_keys": [],
                "model_id": "myt/claude-opus-4-8-free",
                "fallback_model_ids": [
                        "myt/gpt-5.6-sol-free",
                        "myt/gemini-3.5-flash-free"
                ],
                "provider_type": "openai_compatible",
                "timeout_seconds": 600,
                "is_arbiter": False,
                "enabled": True,
                "temperature": 0.7
        }
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
        folder = session.workspace_folder
        if not folder:
            safe_title = sanitize_folder_name(session.session_title or session.ps_code or "SIH_Debate")
            folder = f"{session.session_id[:8]}_{safe_title}"
            session.workspace_folder = folder
        full_path = os.path.join(WORKSPACES_ROOT, folder)
        os.makedirs(full_path, exist_ok=True)
        os.makedirs(os.path.join(full_path, "research"), exist_ok=True)
        return full_path

    @classmethod
    async def save_session(cls, session: DebateSession):
        async with cls._lock:
            cls._memory_cache[session.session_id] = session
            workspace_dir = cls.get_workspace_dir(session)
            session_file = os.path.join(workspace_dir, "session_state.json")
            try:
                with open(session_file, "w", encoding="utf-8") as f:
                    f.write(session.model_dump_json(indent=2))
            except Exception as e:
                print(f"Error saving session state to {session_file}: {e}")

            # Save phase markdown deliverables to disk
            for phase in session.phases:
                if phase.verdict_filename and phase.verdict_markdown:
                    phase_file = os.path.join(workspace_dir, phase.verdict_filename)
                    try:
                        with open(phase_file, "w", encoding="utf-8") as pf:
                            pf.write(phase.verdict_markdown)
                    except Exception as e:
                        print(f"Error saving phase file {phase_file}: {e}")

            # Save latest consensus report to disk
            if session.final_markdown_report:
                verdict_file = os.path.join(workspace_dir, "LATEST_CONSENSUS_VERDICT.md")
                try:
                    with open(verdict_file, "w", encoding="utf-8") as vf:
                        vf.write(session.final_markdown_report)
                except Exception as e:
                    print(f"Error saving LATEST_CONSENSUS_VERDICT.md: {e}")

    @classmethod
    async def get_session(cls, session_id: str) -> Optional[DebateSession]:
        async with cls._lock:
            if session_id in cls._memory_cache:
                return cls._memory_cache[session_id]
            for folder in os.listdir(WORKSPACES_ROOT):
                session_file = os.path.join(WORKSPACES_ROOT, folder, "session_state.json")
                if os.path.exists(session_file):
                    try:
                        with open(session_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if data.get("session_id") == session_id:
                                session = DebateSession(**data)
                                cls._memory_cache[session_id] = session
                                return session
                    except Exception as e:
                        print(f"Error reading session file {session_file}: {e}")
            return None

    @classmethod
    async def list_workspaces(cls) -> List[dict]:
        async with cls._lock:
            results = []
            if not os.path.exists(WORKSPACES_ROOT):
                return results
            for folder in os.listdir(WORKSPACES_ROOT):
                folder_path = os.path.join(WORKSPACES_ROOT, folder)
                if os.path.isdir(folder_path):
                    session_file = os.path.join(folder_path, "session_state.json")
                    item = {
                        "folder": folder,
                        "path": folder_path,
                        "has_session": False,
                        "modified_time": os.path.getmtime(session_file) if os.path.exists(session_file) else os.path.getmtime(folder_path)
                    }
                    if os.path.exists(session_file):
                        try:
                            with open(session_file, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                item["has_session"] = True
                                item["session_id"] = data.get("session_id")
                                item["session_title"] = data.get("session_title") or data.get("ps_code") or folder
                                item["ps_code"] = data.get("ps_code", "")
                                item["status"] = data.get("status", "saved")
                                item["created_at"] = data.get("created_at")
                                item["rounds_count"] = len(data.get("rounds", []))
                                item["consensus_score"] = data.get("consensus_score", 0)
                        except Exception:
                            pass
                    results.append(item)
            
            # Sort newest first
            results.sort(key=lambda x: x.get("modified_time", 0), reverse=True)
            return results

    @classmethod
    async def delete_session(cls, session_id: str) -> bool:
        async with cls._lock:
            if session_id in cls._memory_cache:
                del cls._memory_cache[session_id]
            if not os.path.exists(WORKSPACES_ROOT):
                return False
            for folder in os.listdir(WORKSPACES_ROOT):
                folder_path = os.path.join(WORKSPACES_ROOT, folder)
                if os.path.isdir(folder_path):
                    session_file = os.path.join(folder_path, "session_state.json")
                    if os.path.exists(session_file):
                        try:
                            with open(session_file, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                if data.get("session_id") == session_id:
                                    import shutil
                                    shutil.rmtree(folder_path)
                                    return True
                        except Exception:
                            pass
            return False
