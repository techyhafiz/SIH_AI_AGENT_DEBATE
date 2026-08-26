import asyncio
import json
import os
import re
import shutil
from collections import OrderedDict
from typing import Dict, List, Optional

from app.schemas import DebateSession, ModelConfig


WORKSPACES_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "workspaces"))
USER_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "user_config.json"))
os.makedirs(WORKSPACES_ROOT, exist_ok=True)
os.makedirs(os.path.dirname(USER_CONFIG_PATH), exist_ok=True)


class PersistenceError(RuntimeError):
    pass


def _atomic_write_text(path: str, content: str) -> None:
    tmp_path = f"{path}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(tmp_path, path)
    except Exception as exc:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass
        raise PersistenceError(f"Could not persist {path}: {exc}") from exc


class UserConfigStorage:
    _lock = asyncio.Lock()

    @classmethod
    def _default_models(cls) -> List[ModelConfig]:
        defaults = [
            {
                "id": "m1",
                "name": "GPT 5.6 Sol",
                "base_url": "https://agentrouter.org/v1",
                "api_key": os.getenv("AGENTROUTER_API_KEY", ""),
                "model_id": "gpt-5.6-sol",
                "is_arbiter": True,
            },
            {
                "id": "m2",
                "name": "Gemini Flash",
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
                "api_key": os.getenv("GEMINI_API_KEY", ""),
                "model_id": "gemini-flash-latest",
                "is_backup_arbiter": True,
            },
        ]
        return [ModelConfig(**item) for item in defaults]

    @classmethod
    async def get_user_config(cls) -> List[ModelConfig]:
        async with cls._lock:
            if os.path.exists(USER_CONFIG_PATH):
                try:
                    data = await asyncio.to_thread(cls._read_json, USER_CONFIG_PATH)
                    if isinstance(data, list) and data:
                        return [ModelConfig(**cls._migrate_model_data(item)) for item in data]
                except Exception as exc:
                    raise PersistenceError(f"Could not load user configuration: {exc}") from exc
            return cls._default_models()

    @classmethod
    async def save_user_config(cls, models: List[ModelConfig]) -> None:
        payload = json.dumps([model.model_dump() for model in models], indent=2)
        async with cls._lock:
            await asyncio.to_thread(_atomic_write_text, USER_CONFIG_PATH, payload)

    @staticmethod
    def _read_json(path: str):
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _migrate_model_data(item: dict) -> dict:
        migrated = dict(item)
        if migrated.get("provider_type") == "gemini_native":
            migrated["provider_type"] = "openai_compatible"
        return migrated


def sanitize_folder_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_\-\s]", "", name).strip().replace(" ", "_")
    return cleaned[:40] if cleaned else "workspace"


class SessionStorage:
    _lock = asyncio.Lock()
    _memory_cache: "OrderedDict[str, DebateSession]" = OrderedDict()
    _deleted_session_ids: set[str] = set()
    _cache_limit = 32

    @classmethod
    def get_workspace_dir(cls, session: DebateSession, create: bool = True) -> str:
        folder = session.workspace_folder
        if not folder:
            domain_slug = sanitize_folder_name(session.ministry_domain or "domain")
            ps_slug = sanitize_folder_name(session.ps_code or "ps")
            title_slug = sanitize_folder_name(session.session_title or "debate")
            folder = f"{domain_slug}_{ps_slug}_{title_slug}_{session.session_id[:8]}"
            session.workspace_folder = folder
        full_path = os.path.abspath(os.path.join(WORKSPACES_ROOT, os.path.basename(folder)))
        if create:
            os.makedirs(full_path, exist_ok=True)
            os.makedirs(os.path.join(full_path, "research"), exist_ok=True)
        return full_path

    @classmethod
    def _cache_session(cls, session: DebateSession) -> None:
        cls._memory_cache[session.session_id] = session
        cls._memory_cache.move_to_end(session.session_id)
        while len(cls._memory_cache) > cls._cache_limit:
            cls._memory_cache.popitem(last=False)

    @classmethod
    async def save_session(cls, session: DebateSession) -> None:
        async with cls._lock:
            if session.session_id in cls._deleted_session_ids:
                raise PersistenceError(f"Session {session.session_id} has been deleted")
            workspace_dir = cls.get_workspace_dir(session)
            disk_session = session.model_copy(deep=True)
            for model in disk_session.models:
                model.api_key = ""
                model.backup_api_keys = []
            session_payload = disk_session.model_dump_json(indent=2)
            phase_files = [
                (os.path.join(workspace_dir, os.path.basename(phase.verdict_filename)), phase.verdict_markdown)
                for phase in session.phases
                if phase.verdict_filename and phase.verdict_markdown
            ]
            if session.final_markdown_report:
                phase_files.append((os.path.join(workspace_dir, "LATEST_CONSENSUS_VERDICT.md"), session.final_markdown_report))

            def write_all() -> None:
                _atomic_write_text(os.path.join(workspace_dir, "session_state.json"), session_payload)
                for path, content in phase_files:
                    _atomic_write_text(path, content)

            await asyncio.to_thread(write_all)
            cls._cache_session(session)

    @classmethod
    def _migrate_session_data(cls, raw: dict) -> dict:
        data = dict(raw)
        data["models"] = [
            UserConfigStorage._migrate_model_data(item)
            for item in (data.get("models") or [])
            if isinstance(item, dict)
        ]
        rounds = []
        for index, raw_round in enumerate(data.get("rounds") or [], start=1):
            if not isinstance(raw_round, dict):
                continue
            item = dict(raw_round)
            item.setdefault("round_number", index)
            item.setdefault("workspace_phase_number", 1)
            if not item.get("pass_or_round_id"):
                item["pass_or_round_id"] = str(item.get("round_type") or item["round_number"])
            rounds.append(item)
        data["rounds"] = rounds
        phases = data.get("phases") or []
        data.setdefault("workspace_phase_number", max(1, len(phases)))
        data.setdefault("completed_research_steps", [])
        return data

    @classmethod
    async def get_session(cls, session_id: str) -> Optional[DebateSession]:
        async with cls._lock:
            cached = cls._memory_cache.get(session_id)
            if cached is not None:
                cls._memory_cache.move_to_end(session_id)
                return cached
            for folder in await asyncio.to_thread(os.listdir, WORKSPACES_ROOT):
                session_file = os.path.join(WORKSPACES_ROOT, folder, "session_state.json")
                if not os.path.exists(session_file):
                    continue
                try:
                    data = await asyncio.to_thread(UserConfigStorage._read_json, session_file)
                    if data.get("session_id") == session_id:
                        session = DebateSession(**cls._migrate_session_data(data))
                        stored_models = {model.id: model for model in await UserConfigStorage.get_user_config()}
                        for model in session.models:
                            stored = stored_models.get(model.id)
                            if stored and not model.api_key:
                                model.api_key = stored.api_key
                                model.backup_api_keys = list(stored.backup_api_keys)
                        cls._cache_session(session)
                        return session
                except Exception as exc:
                    print(f"Error reading session file {session_file}: {exc}")
            return None

    @classmethod
    async def list_workspaces(cls) -> List[dict]:
        async with cls._lock:
            results = []
            for folder in await asyncio.to_thread(os.listdir, WORKSPACES_ROOT):
                folder_path = os.path.join(WORKSPACES_ROOT, folder)
                if not os.path.isdir(folder_path):
                    continue
                session_file = os.path.join(folder_path, "session_state.json")
                item = {
                    "folder": folder,
                    "path": folder_path,
                    "has_session": False,
                    "loadable": False,
                    "modified_time": os.path.getmtime(session_file) if os.path.exists(session_file) else os.path.getmtime(folder_path),
                }
                if os.path.exists(session_file):
                    try:
                        data = await asyncio.to_thread(UserConfigStorage._read_json, session_file)
                        session = DebateSession(**cls._migrate_session_data(data))
                        item.update({
                            "has_session": True,
                            "loadable": True,
                            "session_id": session.session_id,
                            "session_title": session.session_title or session.ps_code or folder,
                            "ps_code": session.ps_code or "",
                            "status": session.status,
                            "created_at": session.created_at,
                            "rounds_count": len(session.rounds),
                            "consensus_score": next(
                                (round_data.arbiter_eval.consensus_score for round_data in reversed(session.rounds) if round_data.arbiter_eval),
                                0,
                            ),
                        })
                    except Exception as exc:
                        item["migration_error"] = str(exc)
                results.append(item)
            results.sort(key=lambda value: value.get("modified_time", 0), reverse=True)
            return results

    @classmethod
    async def delete_session(cls, session_id: str) -> bool:
        async with cls._lock:
            cls._deleted_session_ids.add(session_id)
            while len(cls._deleted_session_ids) > 256:
                cls._deleted_session_ids.pop()
            cls._memory_cache.pop(session_id, None)
            for folder in await asyncio.to_thread(os.listdir, WORKSPACES_ROOT):
                folder_path = os.path.join(WORKSPACES_ROOT, folder)
                session_file = os.path.join(folder_path, "session_state.json")
                if not os.path.exists(session_file):
                    continue
                try:
                    data = await asyncio.to_thread(UserConfigStorage._read_json, session_file)
                    if data.get("session_id") == session_id:
                        await asyncio.to_thread(shutil.rmtree, folder_path)
                        return True
                except Exception as exc:
                    raise PersistenceError(f"Could not delete session {session_id}: {exc}") from exc
            return False
