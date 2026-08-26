# Available Models — Simple Guide

What these API keys actually reach, measured live. Last verified: **26 Aug 2026**.

---

## The short version

| | |
|---|---|
| Models the 8 providers **advertise** | **822** |
| Models that actually **answer** | **~43** on a quick scan, **~70–90** on a full sweep |
| Why the gap | Free-plan keys. ~617 of the 822 answer *"no credits / paid plan only"* |
| Quick scan | 79 probes, **~3 min** |
| Full sweep | 822 probes, **~8 min** |

Everything below is a real reply from a real request, not a catalogue listing.

---

## How to run a scan

In the setup wizard, on the last provider card:

- **⚡ Quick Scan — Free + Curated** → the curated fleet plus every model a provider flags free. This is the default and what you want 95% of the time.
- **Search All 800+ Models** → the whole catalogue. Asks you to confirm first, because most of the extra 743 will just say "no credits".

Results stream in as they arrive. You can hit **Stop & use what we have** at any point.

---

## The three tiers

Every model gets tiered automatically from its **model family** — not its speed. A 4b safety
classifier answers in 700ms and would top any speed ranking while being useless in a debate, so
**latency is shown as a separate badge**.

| Tier | What it means | Use it for |
|---|---|---|
| 🟡 **Top tier** | Frontier models — Opus, GPT-5.6, Qwen-max, DeepSeek-V4, 300B+ models | Your main debate fleet |
| 🔵 **Mid tier** | Capable general chat models. Also the default for anything unrecognised | Extra perspectives, cheap rounds |
| ⚪ **Light / special-purpose** | Small variants (`-mini`, `-lite`, `-nano`, ≤9b) and safety / translation / TTS / image endpoints | Avoid as debaters |

Unrecognised names land in **mid** on purpose — guessing "top" flatters them, "low" buries them.

---

## 🟡 Top tier — 13 verified

| Latency | Model | Provider | Free? |
|---:|---|---|---|
| 2.1s | `mistralai/mistral-large-2512` | XKiro Router | paid ⭐ |
| 2.1s | `claude-opus-4-8` | AgentRouter | paid ⭐ |
| 3.9s | `qwen/qwen3.5-397b-a17b:free` | XKiro Router | **free** |
| 4.2s | `minimax/minimax-m2.7:free` | OpenRouter | **free** |
| 4.3s | `qwen/qwen3.8-max:free` | XKiro Router | **free** |
| 4.5s | `deepseek/deepseek-v4-pro` | XKiro Router | paid ⭐ |
| 6.6s | `qwen/qwen3.7-max:free` | XKiro Router | **free** |
| 7.7s | `minimax/minimax-m2.7` | XKiro Router | paid ⭐ |
| 14.1s | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | **free** |
| 18.4s | `gpt-5.6-sol` | BluesMinds AI | paid ⭐ |
| 19.4s | `gpt-5.6-terra` | BluesMinds AI | paid ⭐ |
| 20.4s | `claude-opus-5` | AgentRouter | paid ⭐ |
| 38.4s | `stealth/ox-alpha` | OpenRouter | paid ⭐ |

⭐ = curated Admin Favorite.

**Suggested 5-model debate fleet** — different vendors, so the debate has genuinely different
priors, and all under ~8s:

```
claude-opus-4-8              (Anthropic, AgentRouter)
mistralai/mistral-large-2512 (Mistral,   XKiro)
deepseek/deepseek-v4-pro     (DeepSeek,  XKiro)
qwen/qwen3.8-max:free        (Alibaba,   XKiro)
minimax/minimax-m2.7:free    (MiniMax,   OpenRouter)
```

Add `claude-opus-5` and `gpt-5.6-sol` if you can accept ~20s turns — the Arbiter role in
particular is worth spending latency on.

---

## 🔵 Mid tier — 23 verified

All free. The XKiro Qwen range dominates here and is the most reliable free block in the fleet.

| Latency | Model | Provider |
|---:|---|---|
| 1.2s | `openrouter/free` | OpenRouter |
| 1.2s | `nvidia/nemotron-3-super-120b-a12b:free` ⭐ | OpenRouter |
| 1.5s | `poolside/laguna-xs-2.1:free` | OpenRouter |
| 1.5s | `thinkingmachines/inkling:free` | OpenRouter |
| 1.6s | `minimax/minimax-m3:free` | OpenRouter |
| 2.3s | `liquid/lfm-2.5-2.6b:free` | OpenRouter |
| 2.7s | `nvidia/nemotron-3.5-lightning:free` ⭐ | OpenRouter |
| 2.8s | `poolside/laguna-s-2.1:free` | OpenRouter |
| 3.1s | `qwen/qwen3-omni-flash:free` | XKiro Router |
| 3.4s | `qwen/qwen3.6-35b-a3b:free` | XKiro Router |
| 3.5s | `qwen/qwen3.6-27b:free` | XKiro Router |
| 3.5s | `qwen/qwen3.5-omni-flash:free` | XKiro Router |
| 3.5s | `qwen/qwen3-vl-plus:free` | XKiro Router |
| 3.9s | `qwen/qwen-plus-2025-07-28:free` | XKiro Router |
| 4.0s | `qwen/qwen3-coder-plus:free` | XKiro Router |
| 4.2s | `qwen/qwen3.5-plus:free` | XKiro Router |
| 4.2s | `qwen/qwen3.5-flash:free` | XKiro Router |
| 4.3s | `qwen/qwen3.6-max-preview:free` | XKiro Router |
| 4.6s | `qwen/qwen3-max:free` | XKiro Router |
| 4.6s | `qwen/qwen3.7-plus:free` | XKiro Router |
| 4.8s | `qwen/qwen3.5-omni-plus:free` | XKiro Router |
| 5.6s | `qwen/qwen3.6-plus:free` | XKiro Router |
| 21.7s | `dots-studio/dots-3-note-preview:free` | OpenRouter |

---

## ⚪ Light / special-purpose — 7 verified

Fast, but not debaters. `nemotron-3.5-content-safety` is a moderation classifier;
`north-mini-code` is a code-completion model; `gemma-4` and `-nano-` variants are small.

| Latency | Model | Provider |
|---:|---|---|
| 1.2s | `gemini-3.5-flash-lite` ⭐ | Google AI Studio |
| 1.3s | `google/gemma-4-26b-a4b-it:free` | OpenRouter |
| 1.3s | `google/gemma-4-31b-it:free` | OpenRouter |
| 1.3s | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | OpenRouter |
| 1.3s | `cohere/north-mini-code:free` | OpenRouter |
| 2.1s | `thinkingmachines/inkling-small:free` | OpenRouter |
| 2.2s | `nvidia/nemotron-3.5-content-safety:free` | OpenRouter |

`gemini-3.5-flash-lite` is tiered low by family but is a solid, extremely cheap fast model —
good for the research/summarisation side roles, not for carrying a debate position.

---

## Per-provider reality check

From the last full 822-model sweep:

| Provider | Online / listed | State of the account |
|---|---:|---|
| **XKiro Router** | 35 / 92 | Healthy. Free Qwen block + some paid flagships reachable |
| **BluesMinds AI** | 16 / 29 | Healthy, but slow to cold-start large models |
| **Google AI Studio** | 9 / 51 | Healthy. Older `gemini-2.5-*` ids are retired for new users |
| **AgentRouter** | 4 / 4 | Healthy — reaches `claude-opus-5` and `claude-opus-4-8` |
| **OpenRouter** | 2–17 / 418 | Key valid, **no credits purchased**. Free models only, and there is a free-models-per-day cap |
| **TokenIn Free Hub** | 2 / 80 | Balance empty — HTTP 402 *"Saldo tidak cukup"* |
| **TokenRouter** | 1 / 128 | Credit limit ￥0.000000 |
| **FreeTokenFaucet** | 0 / 19 | `INSUFFICIENT_BALANCE` — needs a daily check-in on their site to top up |

These are **account states, not bugs**. Adding credits to OpenRouter or checking in on
FreeTokenFaucet would immediately raise the online count.

---

## Why a model shows as unavailable

The failed list is collapsed by default. Each row carries a plain-English reason:

| Label | What actually happened |
|---|---|
| **Out of credits** | Key is fine, wallet is empty |
| **Needs paid plan** | Key is fine, model is behind a paid tier |
| **Daily cap reached** | Free-models-per-day allowance spent (resets) |
| **Rate limited** | Momentary throttle — retried once serially before being reported |
| **Not on this endpoint** | Model id retired or never existed on this router |
| **Not a chat model** | Embedding / TTS / image endpoint |
| **Key rejected** | The only one that means the key itself is bad |
| **Provider error / Timed out** | Their side. Re-run the scan |

Only **Key rejected** means you need to do something about the key.

---

## Things worth knowing

- **Counts move between runs.** OpenRouter has a free-models-per-day allowance that the sweep
  itself consumes, so a second full sweep on the same day returns fewer OpenRouter models than
  the first. Expect ±5 models run to run; BluesMinds' `claude-sonnet-5` in particular flips
  between online and a provider-side error.
- **Latency is a single cold-start measurement**, not a benchmark. The 38s on `ox-alpha` and
  ~20s on the GPT-5.6 / Opus rows is largely reasoning-model warm-up.
- **Quick scan can't find everything.** It only probes curated favourites plus free-flagged
  models, so a paid model that isn't a favourite won't appear. Run the full sweep for that.
- **Known tiering quirk:** `qwen3.8-max` and `qwen3.7-max` are top tier, but `qwen3-max` and
  `qwen3.6-max-preview` land in mid — the flagship list names specific versions rather than
  matching the `-max` suffix generally. Treat any Qwen `*-max` as top tier when picking by hand.
- **Providers are probed with a shared browser-like User-Agent.** AgentRouter returns
  `401 unauthorized client detected` to any UA it does not recognise, which is why its models
  previously looked dead while the same key worked fine in an IDE.
