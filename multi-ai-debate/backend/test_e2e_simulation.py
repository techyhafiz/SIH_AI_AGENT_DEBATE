import asyncio
import json
import httpx
from app.main import app
from app.schemas import ModelConfig
from app.storage import SessionStorage

async def run_e2e_simulation():
    print("[E2E TEST] Starting Multi-Key & Follow-up Workspace Simulation...")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health Check
        resp = await client.get("/health")
        assert resp.status_code == 200
        print("  [OK] Health check passed")

        # 2. Test Problem Statements Search API
        resp_ps = await client.get("/api/problem-statements?query=SIH26001")
        assert resp_ps.status_code == 200
        ps_results = resp_ps.json()
        assert len(ps_results) > 0
        assert ps_results[0]["ps_code"] == "SIH26001"
        print(f"  [OK] Stored PS Search API passed: Found {len(ps_results)} items ({ps_results[0]['title'][:40]}...)")

        # 3. Test Permanent User Config API (Global User-Level Keys)
        user_cfg_payload = [
            {
                "id": "m1",
                "name": "Claude 3.5 Sonnet",
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": "user-saved-primary-key",
                "backup_api_keys": ["user-backup-1", "user-backup-2"],
                "model_id": "anthropic/claude-3.5-sonnet",
                "timeout_seconds": 600,
                "is_arbiter": True,
                "enabled": True,
                "temperature": 0.7
            }
        ]
        resp_save_user = await client.post("/api/user/config", json=user_cfg_payload)
        assert resp_save_user.status_code == 200
        
        resp_get_user = await client.get("/api/user/config")
        assert resp_get_user.status_code == 200
        saved_user_cfg = resp_get_user.json()
        assert saved_user_cfg[0]["api_key"] == "user-saved-primary-key"
        print("  [OK] Permanent User-Level Config API passed (Persistent across all sessions)")

        # 2. Test Multi-Key Connectivity Probe
        probe_payload = {
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": "invalid-primary-key",
            "backup_api_keys": ["backup-key-1", "backup-key-2"],
            "model_id": "anthropic/claude-3.5-sonnet",
            "provider_type": "openai_compatible",
            "timeout_seconds": 5
        }
        resp_probe = await client.post("/api/models/test", json=probe_payload)
        assert resp_probe.status_code == 200
        print("  [OK] Multi-key failover probe tested")

        # 3. Create Session with Workspace Folder
        test_models = [
            ModelConfig(
                id="m1",
                name="Claude 3.5 Sonnet",
                base_url="https://openrouter.ai/api/v1",
                api_key="key-1",
                backup_api_keys=["backup-key-1"],
                model_id="anthropic/claude-3.5-sonnet",
                timeout_seconds=600,
                is_arbiter=True
            ),
            ModelConfig(
                id="m2",
                name="DeepSeek R1",
                base_url="https://openrouter.ai/api/v1",
                api_key="key-2",
                backup_api_keys=[],
                model_id="deepseek/deepseek-r1",
                timeout_seconds=600,
                is_arbiter=False
            )
        ]

        start_req = {
            "session_title": "Test_Disaster_NDRF",
            "problem_statement": "Design offline LoRa mesh network for cyclone response.",
            "ministry_domain": "Ministry of Home Affairs",
            "models": [m.model_dump() for m in test_models],
            "arbiter_model_id": "m1",
            "auto_advance": False
        }

        resp_start = await client.post("/api/debate/start", json=start_req)
        assert resp_start.status_code == 200
        data = resp_start.json()
        session_id = data["session_id"]
        assert "workspace_folder" in data
        print(f"  [OK] Session initialized in workspace folder: {data['workspace_folder']}")

        # 4. Mock Phase 1 Verdict and Test Follow-up Phase Launch
        session = await SessionStorage.get_session(session_id)
        session.final_markdown_report = "# Phase 1 Verdict\nAgreed on LoRa 868MHz Mesh architecture."
        await SessionStorage.save_session(session)

        followup_req = {
            "followup_prompt": "Now generate complete Technical Specification list in MD",
            "phase_title": "Technical_Specification",
            "auto_advance": False
        }
        resp_followup = await client.post(f"/api/debate/{session_id}/followup", json=followup_req)
        assert resp_followup.status_code == 200
        print("  [OK] Follow-up debate phase triggered successfully")

        # 5. List Workspaces
        resp_workspaces = await client.get("/api/workspaces")
        assert resp_workspaces.status_code == 200
        workspaces = resp_workspaces.json()
        assert len(workspaces) > 0
        print(f"  [OK] Workspace directories listed ({len(workspaces)} workspaces found)")

    print("\n[SUCCESS] ALL MULTI-KEY & WORKSPACE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_e2e_simulation())
