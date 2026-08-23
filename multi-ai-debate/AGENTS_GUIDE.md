# 🤖 AI Agent Technical Integration & Automation Guide
> **Operational Guide for AI Coding Agents (Antigravity, Cursor, Claude Code, GitHub Copilot, Windsurf, Roo Code)**

---

## 🎯 Purpose of this Document
This guide instructs AI Coding Assistants on how to automate, execute, test, and manage the **AI Consensus Arena (SIH Edition)** on behalf of a human user.

---

## 🏗️ System Architecture & File Layout

```
SIH_AI_AGENT_DEBATE/
├── multi-ai-debate/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── engine/
│   │   │   │   ├── prompts.py            # 4 Personas, NO-CODE rules, multi-phase prompts
│   │   │   │   ├── orchestrator.py       # Barrier sync engine, 10m watchdog, key promotion
│   │   │   │   └── consensus_eval.py     # 0-100% agreement math & markdown synthesizer
│   │   │   ├── providers/
│   │   │   │   └── universal_client.py   # Multi-key failover client & JSON repair parser
│   │   │   ├── static/
│   │   │   │   └── index.html            # Zero-dependency White-Theme SPA dashboard
│   │   │   ├── main.py                   # FastAPI app, CORS, SSE streaming, workspace routes
│   │   │   ├── schemas.py                # Pydantic v2 schemas
│   │   │   └── storage.py                # Workspace folder manager & UserConfigStorage
│   │   ├── data/
│   │   │   ├── extracted_problem_statements.json  # 226 Stored SIH Problem Statements
│   │   │   ├── user_config.json                   # Permanent User Credentials & Endpoints
│   │   │   └── workspaces/                        # Dedicated conversation directories
│   │   ├── run.py                        # Uvicorn entrypoint (Port 8000)
│   │   ├── test_e2e_simulation.py        # End-to-End automated test suite
│   │   └── test_backend.py               # Unit test suite
│   ├── README.md                         # Human user guide
│   └── AGENTS_GUIDE.md                   # This technical manual
└── extracted_problem_statements.json     # Master SIH dataset
```

---

## 🚀 Execution & Verification Protocols for AI Agents

### Protocol 1: Launch the Backend Server
When the user asks to "run the app" or "start the server":
```powershell
cd multi-ai-debate\backend
python run.py
```
*Note: Uvicorn starts on `http://127.0.0.1:8000`.*

### Protocol 2: Run End-to-End Verification
To verify health, PS search, permanent user credentials, session initialization, follow-up phases, and workspace folder creation without needing real API keys:
```powershell
python multi-ai-debate\backend\test_e2e_simulation.py
```
*Expected Output:* `[SUCCESS] ALL MULTI-KEY & WORKSPACE TESTS PASSED SUCCESSFULLY!`

---

## 🔑 Protocol for AI Agents: Auto-Configuring Models from User Chat Messages

When the human user provides API keys, endpoints, or asks to add models in chat:

1. **Do NOT ask the user to manually edit JSON files**.
2. **Directly load and update `multi-ai-debate/backend/data/user_config.json`** using your file tools.
3. Supported Gateway Endpoints:
   - **AgentRouter**: `https://agentrouter.org/v1` (Register: [https://agentrouter.org/register?aff=cHl5](https://agentrouter.org/register?aff=cHl5))
   - **Google Gemini**: `https://generativelanguage.googleapis.com/v1beta/openai` (Get Key: [https://aistudio.google.com/](https://aistudio.google.com/))
   - **OpenRouter**: `https://openrouter.ai/api/v1` (Get Key: [https://openrouter.ai/keys](https://openrouter.ai/keys))
   - **TokenRouter**: `https://api.tokenrouter.com/v1` (Get Key: [https://tokenrouter.com/](https://tokenrouter.com/))
   - **BluesMinds**: `https://api.bluesminds.com/v1` (Get Key: [https://bluesminds.com/](https://bluesminds.com/))
4. **Probe & Validate Latency**: Always test connectivity via `POST /api/models/test` or python probe to ensure the keys and endpoints respond with HTTP 200.
5. **Never Commit Keys to Git**: Ensure real keys reside exclusively in `user_config.json` (which is `.gitignore`d). Tracked source files like `storage.py` and `index.html` must always have `api_key: ""` placeholders.

---

## 📡 API Contract & Automation Reference

### 1. Retrieve Stored SIH Problem Statements
```http
GET /api/problem-statements?query={searchTerm}
```
**Response Sample:**
```json
[
  {
    "s_no": 1,
    "ps_code": "SIH26001",
    "ps_id": "26001",
    "title": "AI-Based early warning and landslide Risk Monitoring System in NER",
    "organization": "Ministry of Development of North Eastern Region (MDoNER)",
    "category": "Software",
    "theme": "Disaster Management",
    "description": "Background...",
    "expected_solution": "A scalable AI-based software platform..."
  }
]
```

### 2. Save Permanent User API Keys & Models
```http
POST /api/user/config
Content-Type: application/json

[
  {
    "id": "m1",
    "name": "Claude 3.5 Sonnet",
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": "sk-or-v1-primary...",
    "backup_api_keys": ["sk-or-v1-backup-1..."],
    "model_id": "anthropic/claude-3.5-sonnet",
    "timeout_seconds": 600,
    "is_arbiter": true,
    "enabled": true,
    "temperature": 0.7
  }
]
```

### 3. Probe Model Connectivity & Failover
```http
POST /api/models/test
Content-Type: application/json

{
  "base_url": "https://openrouter.ai/api/v1",
  "api_key": "sk-primary",
  "backup_api_keys": ["sk-backup-1"],
  "model_id": "anthropic/claude-3.5-sonnet",
  "provider_type": "openai_compatible",
  "timeout_seconds": 10
}
```

### 4. Start a Multi-AI Debate Session
```http
POST /api/debate/start
Content-Type: application/json

{
  "ps_code": "SIH26001",
  "session_title": "SIH26001_Landslide_Monitoring",
  "ministry_domain": "Ministry of Development of North Eastern Region (MDoNER)",
  "problem_statement": "Full description...",
  "additional_prompt": "Must operate under Rs 5,000 per node with LoRa sync.",
  "models": [...],
  "arbiter_model_id": "m1",
  "auto_advance": true
}
```
**Response Sample:**
```json
{
  "session_id": "01e07463-930",
  "workspace_folder": "C:\\...\\data\\workspaces\\SIH26001_Landslide_Monitoring_01e07463-930",
  "status": "running",
  "current_round": 0,
  "current_phase": 1
}
```

### 5. Launch a Follow-Up Debate Phase
```http
POST /api/debate/{session_id}/followup
Content-Type: application/json

{
  "followup_prompt": "Now generate complete Technical Specification list in MD",
  "phase_title": "Technical_Specification",
  "auto_advance": true
}
```

---

## 🔒 Security & Git Safety Guidelines for Agents

1. **NEVER Hardcode Keys in Code**: Never commit plaintext API keys into Python files, test files, or HTML.
2. **Always Use `user_config.json` or Environment Variables**: Credentials belong strictly in `backend/data/user_config.json` (which is git-ignored).
3. **Pydantic v2 Best Practices**: Do not use `model_config` as a field name in Pydantic models (reserved in Pydantic v2). Use `ai_model_config`.
4. **Encoding on Windows**: When logging to stdout, use ASCII indicators like `[OK]`, `[ERROR]`, `[SUCCESS]` rather than unescaped Unicode emojis to avoid `UnicodeEncodeError` on Windows `cp1252` console environments.
