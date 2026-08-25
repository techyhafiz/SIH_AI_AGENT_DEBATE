# Free AI Gateways & Verified Working Models Guide

This document tracks all tested OpenAI-compatible API gateways, their working API keys, base URLs, and complete lists of free models verified with latency measurements.

---

## 1. TokenIn Gateway

- **Base URL:** `https://tokenin.my.id/v1`
- **Chat Endpoint:** `https://tokenin.my.id/v1/chat/completions`
- **API Key:** `sk-d3cd882c62a494944a75df3ee7cbfa29b12664e3`
- **Header:** `Authorization: Bearer sk-d3cd882c62a494944a75df3ee7cbfa29b12664e3`

### Added to User Config (`user_config.json`):
- **`m20` — `myt/gemini-3.5-flash-free`** (Latency: **~1.95s**) — Google Gemini 3.5 Flash with reasoning support.

### All Working Free Models on TokenIn:
| Model ID | Latency | Model Type / Notes |
| :--- | :---: | :--- |
| **`myt/gemini-3.5-flash-free`** | **~1.95s – 2.65s** | Google Gemini 3.5 Flash |
| **`myt/mimo-v2.5-free`** | **~4.49s – 6.32s** | Xiaomi Mimo Reasoning Model |
| **`myt/gpt-5.6-sol-free`** | **~5.40s** | GPT 5.6 Sol (*Subject to 429 rate limit when concurrent*) |

---

## 2. XKiro Gateway

- **Base URL:** `https://api.xkiro.com/v1`
- **Chat Endpoint:** `https://api.xkiro.com/v1/chat/completions`
- **API Key:** `sk-xt-548e4395a57de23cd4c78b65a26a99fff3629a1335663663`
- **Header:** `Authorization: Bearer sk-xt-548e4395a57de23cd4c78b65a26a99fff3629a1335663663`

### Added to User Config (`user_config.json`):
- **`m15` — `deepseek/deepseek-v4-pro`** (Latency: **2.74s**) — Frontier Reasoning & Logic
- **`m16` — `qwen/qwen3.8-max`** (Latency: **2.36s**) — Alibaba Flagship Max Model
- **`m17` — `mistralai/mistral-large-2512`** (Latency: **1.19s**) — High-Speed European Flagship
- **`m18` — `qwen/qwen3.7-max`** (Latency: **1.92s**) — Advanced Reasoning & Analysis
- **`m19` — `minimax/minimax-m2.7`** (Latency: **3.20s**) — Deep Chain-of-Thought

### All 37 Working Free Models on XKiro:

#### A. Frontier Reasoning & Flagships
- `deepseek/deepseek-v4-pro` (2.74s)
- `qwen/qwen3.8-max` (2.36s)
- `mistralai/mistral-large-2512` (1.19s)
- `qwen/qwen3.7-max` (1.92s)
- `minimax/minimax-m2.7` (3.20s)
- `qwen/qwen3.6-max-preview` (1.68s)
- `qwen/qwen3-max` (4.25s)

#### B. Specialized Coding & Developer Models
- `mistralai/codestral-2508` (607 ms — Ultra-fast code generation)
- `qwen/qwen3-coder-plus` (1.56s — Full-stack code engine)
- `mistralai/devstral-medium` (1.46s — Developer tooling)

#### C. MoE & High-Throughput Workhorses
- `qwen/qwen3.5-397b-a17b` (1.62s — Massive 397B MoE)
- `qwen/qwen3.7-plus` (1.55s)
- `deepseek/deepseek-chat-v3.1` (1.90s)
- `deepseek/deepseek-v3.2` (2.19s)
- `deepseek/deepseek-v4-flash` (2.90s)
- `mistralai/mistral-medium-3.5` (704 ms)
- `qwen/qwen-plus-2025-07-28` (1.90s)
- `qwen/qwen3.6-35b-a3b` (2.21s)
- `qwen/qwen3.6-27b` (2.48s)
- `qwen/qwen3.5-plus` (2.52s)
- `qwen/qwen3.5-flash` (2.56s)
- `qwen/qwen3.6-plus` (2.96s)

#### D. Vision & Multimodal
- `qwen/qwen3-vl-plus` (2.40s — Vision-Language)
- `qwen/qwen3-omni-flash` (2.46s — Multimodal Omni)
- `qwen/qwen3.5-omni-flash` (3.55s)
- `qwen/qwen3.5-omni-plus` (3.58s)

#### E. Ultra-Fast Lightweights (Sub-Second)
- `mistralai/ministral-14b` (625 ms)
- `mistralai/ministral-3b` (660 ms)
- `mistralai/ministral-8b` (833 ms)
- `mistralai/mistral-small-2603` (932 ms)

#### F. MiniMax & General Models
- `minimax/minimax-m2.1-highspeed` (2.02s)
- `minimax/minimax-m2.5-highspeed` (2.82s)
- `minimax/minimax-m2.5` (3.12s)
- `minimax/minimax-m2` (4.16s)
- `minimax/minimax-m2.1` (5.88s)
- `minimax/minimax-m2.7-highspeed` (7.39s)
- `stealth/ox-alpha-free` (12.29s)

---

## 3. FreeTokenFaucet Gateway

- **Base URL:** `https://freetokenfaucet.com/v1`
- **Chat Endpoint:** `https://freetokenfaucet.com/v1/chat/completions`
- **API Key:** `tf_41af4ac54610496f84a119d881a10c1a`
- **Header:** `Authorization: Bearer tf_41af4ac54610496f84a119d881a10c1a`

### Added to User Config (`user_config.json`):
- **`m12` — `mimo-v2.5`** (Latency: **~1.71s**) — Xiaomi Mimo Reasoning Model
- **`m13` — `gpt-5.6-terra`** (Latency: **~3.17s**) — Fast GPT 5.6
- **`m14` — `gpt-5.6-luna`** (Latency: **~4.65s**) — Standard GPT 5.6

---

## Quick Python Verification Snippet

```python
from openai import OpenAI

# Example: Calling TokenIn
client_tokenin = OpenAI(
    base_url="https://tokenin.my.id/v1",
    api_key="sk-d3cd882c62a494944a75df3ee7cbfa29b12664e3"
)
resp = client_tokenin.chat.completions.create(
    model="myt/gemini-3.5-flash-free",
    messages=[{"role": "user", "content": "Hello!"}]
)
print("TokenIn Gemini:", resp.choices[0].message.content)
```
