# 🏛️ AI Consensus Arena: Multi-LLM Collaborative Engine (SIH Edition)
> **Autonomous Multi-Model Deliberation, 226+ SIH Problem Statements, Multi-Key Failover & Workspace Deliverables**

Welcome to the **AI Consensus Arena**! This repository contains the complete multi-agent debate platform tailored for Smart India Hackathon.

---

## 📚 Guides & Documentation

- 👨‍💻 **[Human User & Setup Guide](./multi-ai-debate/README.md)**: 60-second quickstart, white-theme UI tour, API setup guide, and feature explanations.
- 🤖 **[AI Agent Integration Guide](./multi-ai-debate/AGENTS_GUIDE.md)**: Operational manual for AI assistants (Antigravity, Cursor, Claude Code, GitHub Copilot, Roo Code, Windsurf) on updating `user_config.json` automatically from user chat messages and running tests.
- 🏗️ **[System Architecture Specification](./MULTI_AI_DEBATE_ARCHITECTURE.md)**: Complete mathematical consensus scoring, cognitive persona lenses, and barrier synchronization architecture.

---

## 🔑 Required API Keys & Where to Get Them

You can obtain keys from any of the verified gateways below:

| # | Provider Gateway | Base URL Endpoint | Recommended AI Models | Key Registration Link |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **AgentRouter** | `https://agentrouter.org/v1` | Claude Opus 4.8 / 5.0, GPT 5.6 Sol | [👉 Register on AgentRouter](https://agentrouter.org/register?aff=cHl5) |
| **2** | **Google Gemini (AI Studio)** | `https://generativelanguage.googleapis.com/v1beta/openai` | Gemini 3.7 Flash Pool, 3.5 Flash Lite | [👉 Get Gemini Key](https://aistudio.google.com/) |
| **3** | **OpenRouter** | `https://openrouter.ai/api/v1` | GLM 5.2 (Free), Nemotron 120B Super, Stealth Ox-Alpha | [👉 Get OpenRouter Key](https://openrouter.ai/keys) |
| **4** | **TokenRouter** | `https://api.tokenrouter.com/v1` | Qwen 3.8 Max (Free Deep Reasoning) | [👉 Get TokenRouter Key](https://tokenrouter.com/) |
| **5** | **BluesMinds** | `https://api.bluesminds.com/v1` | Claude Sonnet 5 Unlimited, Llama 3.3 | [👉 Get BluesMinds Key](https://bluesminds.com/) |

> 💡 **For Users with AI Coding Assistants (Antigravity / Cursor / Claude Code / Copilot)**:  
> You can simply paste your API keys directly in the chat with your AI assistant! The AI agent will automatically configure, test, and save them into `backend/data/user_config.json` without requiring you to manually edit files.

---

## ⚡ Fast Run (60 Seconds)

```powershell
cd multi-ai-debate\backend
pip install -r requirements.txt
python run.py
```

Then open your browser at:
👉 **`http://localhost:8000/`**
