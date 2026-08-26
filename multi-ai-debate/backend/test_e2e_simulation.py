import asyncio
import tempfile
from pathlib import Path

import httpx

from app.main import app
from app.schemas import ModelConfig
from app.storage import SessionStorage


async def run_e2e_simulation():
    """Run read/write API checks against an isolated temporary workspace."""
    original_root = __import__("app.storage", fromlist=["WORKSPACES_ROOT"]).WORKSPACES_ROOT
    storage_module = __import__("app.storage", fromlist=["WORKSPACES_ROOT"])

    with tempfile.TemporaryDirectory(prefix="multi-ai-debate-e2e-") as temp_dir:
        storage_module.WORKSPACES_ROOT = str(Path(temp_dir) / "workspaces")
        Path(storage_module.WORKSPACES_ROOT).mkdir(parents=True, exist_ok=True)
        SessionStorage._memory_cache.clear()
        SessionStorage._deleted_session_ids.clear()
        try:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                health = await client.get("/health")
                assert health.status_code == 200

                model_data = [
                    ModelConfig(id="m1", name="Mock One", base_url="http://127.0.0.1:1/v1", model_id="mock-1", is_arbiter=True),
                    ModelConfig(id="m2", name="Mock Two", base_url="http://127.0.0.1:1/v1", model_id="mock-2"),
                ]
                # Persist and list storage directly without starting live provider work.
                from app.schemas import DebateSession
                session = DebateSession(
                    problem_statement="Isolated persistence test",
                    models=model_data,
                    arbiter_model_id="m1",
                    status="paused",
                )
                await SessionStorage.save_session(session)

                response = await client.get(f"/api/debate/{session.session_id}")
                assert response.status_code == 200
                assert all(model["api_key"] == "" for model in response.json()["models"])

                raw_state = await client.get(f"/api/workspaces/{session.session_id}/files/session_state.json")
                assert raw_state.status_code == 403

                workspaces = await client.get("/api/workspaces")
                assert workspaces.status_code == 200
                assert any(item.get("session_id") == session.session_id for item in workspaces.json())

                deleted = await client.delete(f"/api/workspaces/{session.session_id}")
                assert deleted.status_code == 200
        finally:
            storage_module.WORKSPACES_ROOT = original_root
            SessionStorage._memory_cache.clear()
            SessionStorage._deleted_session_ids.clear()

    print("[SUCCESS] Isolated API and workspace tests passed")


if __name__ == "__main__":
    asyncio.run(run_e2e_simulation())
