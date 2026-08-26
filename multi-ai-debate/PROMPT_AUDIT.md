# PROMPT & SYSTEM AUDIT — Multi-AI Debate Engine

**Audited:** 2026-08-25
**Goal this audit is measured against:** *best use of AI, with best prompting, for SIH research and solution-making.*
**Status:** Report only. **No code has been changed.** Every fix below is a recommendation awaiting your decision.

---

## 0. Method & Verification Baseline

Before auditing behaviour, I established that nothing here is a syntax or type problem:

| Check | Result |
|---|---|
| `python -m compileall backend` | rc=0 — no syntax errors |
| `import app.main` | OK — no import/collection errors |
| `npx tsc --noEmit` | silent — no type errors |

**Therefore every finding in this document is a logic, runtime, or prompting defect — not a typo.**

Evidence sources:
1. Full read of `backend/app/engine/prompts.py` (581 lines), `consensus_eval.py` (204 lines), `universal_client.py`, `research_engine.py`, `orchestrator.py` (1220 lines).
2. **Empirical replay** of a real completed run: `backend/data/workspaces/SIH26183_Real_Time_Identification_o_397de6ca-6d4/session_state.json` (1.2 MB, 11 models, 4 rounds, `status=completed`).
3. The shipped deliverable `SIH_Master_Consensus_Verdict_397de6ca-6d4.md`.
4. Your own design blueprint `MULTI_AI_DEBATE_ARCHITECTURE.md` — used to separate *design intent* from *implementation drift*.

> **Note on line numbers.** `orchestrator.py` grew from ~955 → 1220 lines during this session because you applied some earlier fixes (`workspace_phase_number`, `rendered_sources`, the 30 000-char truncation, `drop_model(reason=...)`). All prompting line references below were **re-verified against the current files on disk**. A few line refs in the older architecture audit (Part D) are approximate for that reason.

---

## 1. Executive Verdict

The architecture is genuinely ambitious and mostly sound. The **prompting layer is where the value is leaking**, and it leaks in one consistent direction: *the system generates far more high-quality reasoning than it ever feeds back into the process or into your final document.*

Five systemic root causes explain almost every specific defect:

| # | Root cause | Consequence for SIH |
|---|---|---|
| **R1** | **The debate loop is open.** Critiques and arbiter guidance are produced, stored, and never delivered to the model they target. | It is not a debate. It is N parallel monologues with a scoreboard. |
| **R2** | **The deliverable is written almost blind.** 99.30% of deliberation content is discarded before the final report prompt. | Your submission document is generic and partly fabricated. |
| **R3** | **No output contract enforcement.** No provider-native JSON mode anywhere; format failures silently become fake data. | Real technical content is scored as `DISAGREE / 50`. |
| **R4** | **Template values act as anchors.** Literal example scores (`75`, `80`, `85`, `95`) and hard-coded fallbacks drive the headline metric. | Your consensus score is partly copied constants, not measurement. |
| **R5** | **Hardware/IoT bias is baked into the system prompt** for every problem, including pure-software ones. | Wasted tokens, irrelevant sections, misdirected engineering effort. |

---

## 2. Empirical Proof (from your real 397de6ca run)

This is the most important section. These are not opinions — they are measurements from a completed session.

### 2.1 — 87,546 characters of adversarial reasoning produced and thrown away

| Round | Critiques | Concessions |
|---|---|---|
| R2 | 26 | 18 |
| R3 | 25 | 25 |
| R4 | 25 | 29 |
| **Total** | **76** | **72** |

**~87.5 KB of targeted cross-model critique was generated, persisted to disk, and never rendered into any peer's prompt.** No model ever saw a criticism written about it. (See **P1**.)

### 2.2 — 99.30% of the deliberation never reaches the deliverable

```
Total deliberation content produced : 972,567 chars
  of which raw_text                 : 633,112
  of which critiques + concessions  :  87,546
Chars reaching final-report prompt  :   6,804
DISCARDED before the deliverable    :  99.30%
```

Mechanism: `prompts.py:545-546` renders each model's contribution as `sol[:200]` — **200 characters per model per round** — plus a `[:250]` synthesis at `prompts.py:542`. The arbiter writes your entire SIH submission from ~6.8 KB of fragments. (See **D1**.)

### 2.3 — The deliverable's academic citations are fabricated

`latest_research_dossier` for this session is **`None`**. No research was ever attached. Yet the shipped verdict contains a *"Peer-Reviewed Academic Research Grounding Matrix"* citing:

| Claimed citation | Present in session research data? |
|---|---|
| `arXiv:2204.08912` — *A Real-Time Framework for Tracking Illicit Crypto Flows* | **NOT IN DOSSIER** |
| *Heuristic Clustering of Exchange Deposit Addresses* (IEEE TIFS, 2023) | **NOT IN DOSSIER** |
| *De-anonymizing Cross-Chain Bridge Laundering* (NDSS) | **NOT IN DOSSIER** |
| *Secure Multi-Party Computation for Financial Intelligence* (ACM CCS) | **NOT IN DOSSIER** |

Plus **eleven `[Source 8]` inline markers** when zero sources existed.

**This is the single highest-risk defect in the system.** Fabricated academic references in a Ministry-facing submission are a disqualification-class problem. Structural cause: `build_final_markdown_report_prompt` (`prompts.py:522`) **has no dossier parameter at all** — the final document is written with zero research grounding — while its system prompt (`consensus_eval.py:173-176` → `prompts.py:68-69`) actively instructs the model to cite papers. (See **D2**.)

### 2.4 — Sign-offs attributed to a model that emitted zero bytes

`Claude Opus 5.0` produced `raw_text = 0 chars` in **both Round 1 and Round 2**, yet was marked `status=completed`. The deliverable states:

> **Claude Opus 5.0:** Approved (Core architecture and graph data flow validation)

and closes with *"All participating models unanimously ratify this document."*

Structural cause: `prompts.py:579` mandates a sign-off "with notes from **every** participating AI model". A model with no output still requires a note, so the arbiter invents a plausible one. Two further entries describe *infrastructure events* as intellectual contributions ("Fallback routed via robust JSON schema synthesis", "Prompt token optimization"). (See **D3**.)

### 2.5 — Format failures silently become fake consensus data

| Model | Raw output | Parsed lens content | Recorded verdict |
|---|---|---|---|
| NVIDIA Nemotron 3 Super 120B | 9,361 chars | 1,558 chars | `DISAGREE / 50` (default) |
| NVIDIA Nemotron 3.5 Lightning | 7,969 chars | 1,134 chars | `DISAGREE / 50` (default) |
| Qwen 3.8 Max | **28,565 chars** | **0 chars** | `DISAGREE / 50` (default) |

Three models did real work and were recorded as hard dissent at exactly the fallback value. Score impact:

```
Round 1 consensus as scored          : 66.8  (n=8, includes three default-50s)
Round 1 excluding parse failures     : 76.8  (n=5)
Headline metric understated by       : 10.0 points
```

Zero-byte responses also contribute a fabricated `DISAGREE/50` to `avg_debater_pct`. (See **P7**, **P3**.)

### 2.6 — Score clustering consistent with framing inflation

Round 4 agreement percentages: `[90, 88, 90, 88, 85, 88]`. Near-identical high scores across independent models is the signature of anchoring plus "OMNISCIENT/salvage" framing, not of independent convergence. (See **P3**, **P16**.)

---

## 3. Part A — Prompting Defects

Format for each: **file:line → failure mechanism → recommended fix.**

### CRITICAL

---

#### P1 — Cross-model critiques are generated, stored, and never delivered to their target
**Where:** `prompts.py:225-234` (Phase 2 peer transcript), `303-309` (Phase 3), `370-373` (Phase 4). Schema that produces them: `prompts.py:19-33`.

**Mechanism:** The peer transcript rendered into each debater's prompt includes only: Architect Lens, Critic Lens, Field & BOM Lens, Security Lens, Proposed Solution, Claimed Positives, Identified Risks. It **omits `critiques` and `concessions_and_defenses` entirely.** Those fields appear only inside the *arbiter's* prompt (`prompts.py:441-445`). So a model is never shown the argument made against it, and cannot rebut. Phase 3 and Phase 4 transcripts are thinner still.

**This is a regression against your own blueprint,** which states at `MULTI_AI_DEBATE_ARCHITECTURE.md:74`:
> *"Each AI is presented with all counter-arguments targeted at its original proposal."*

and at lines 75-78 requires models to categorise **Concessions / Rebuttals / Updated Solution v2.0**.

**Fix:** In the peer-transcript builder, add a per-model section:
```
### ⚔️ CRITIQUES DIRECTED AT YOU (you must respond to each)
- From {critic_name}: {flaw_identified} → {counter_argument}
```
Filter `critiques` where `target_model_id == this model's id`, and require in the instruction block that every listed critique be answered in `concessions_and_defenses` with an explicit `CONCEDE` or `REBUT` label. Keep the full text for critiques *aimed at this model*; summarise others.

---

#### P2 — The arbiter feedback loop is open
**Where:** `prompts.py:404-519` produces `next_round_challenge`, `friction_points`, `executive_synthesis`. Round prompt builders: `prompts.py:206-278`, `284-345`, `351-402`.

**Mechanism:** A grep for `next_round_challenge` across the backend returns only the schema declaration, the assignment, and the JSON example — **it is never read into a subsequent prompt.** The arbiter writes a directive for the next round; the next round never receives it. Same for `friction_points` and `executive_synthesis`. The arbiter is a commentator, not a moderator.

**Fix:** Inject at the top of every round prompt after round 1:
```
### 👑 ARBITER DIRECTIVE FOR THIS ROUND (mandatory)
{prev.arbiter_eval.next_round_challenge}

### UNRESOLVED FRICTION POINTS — you must take a position on each
{numbered friction_points}
```
Place it **before** the peer transcript so it frames the reading, and require the response to reference each friction point by number.

---

#### P3 — The consensus score is anchored by literal template values
**Where:** `prompts.py:51-52`, `88-89`, `110-111`, `124-125`, `138-139`; blending at `consensus_eval.py:109-117`; defaults at `universal_client.py:129-137`.

**Mechanism:** Two compounding problems.

1. **Anchoring.** Every schema example ships a concrete number, escalating by stage:
   | Line | Example vote | Example % |
   |---|---|---|
   | 51-52 | `AGREE or DISAGREE or NEEDS_REFINEMENT` | `75` |
   | 88-89 | `AGREE or DISAGREE or NEEDS_REFINEMENT` | `80` |
   | 110-111 | `NEEDS_REFINEMENT` | `65` |
   | 124-125 | `AGREE` | `85` |
   | 138-139 | `AGREE` | `95` |
   LLMs copy in-context numerals. The prompt is not asking for a judgement — it is suggesting one, and the suggestion rises toward 95.

2. **Constant contamination.** `universal_client.py:133-137` defaults `pct = 50` on any parse miss, and `129-131` defaults `vote = "DISAGREE"`. `consensus_eval.py:109-117` then computes `score = int((avg_debater_pct * 0.6) + (arbiter_score * 0.4))`. **60% of your headline metric is a weighted average that includes copied constants and fallback values.** §2.5 shows this cost 10.0 points in a single round.

**Fix:**
- Replace numeric examples with a **rubric**, not a value: `"agreement_percentage": <integer 0-100; 90+ = ready to build as-is, 70-89 = agree with named reservations, 40-69 = major redesign needed, <40 = fundamental disagreement>`.
- Use a **placeholder** (`<int>`) in every example rather than a live number.
- **Never fabricate a vote.** On parse failure set `consensus_vote = None` and **exclude** the response from `avg_debater_pct`; surface `parse_failed` in the UI instead of laundering it into the score.
- Exclude zero-byte and `status != completed` responses from the average.

---

#### P4 — The arbiter is given a competitor's system prompt
**Where:** `consensus_eval.py:~62-65` (evaluation) and `consensus_eval.py:173-176` (final report), both calling `build_system_prompt_for_debater(...)` → `prompts.py:57-71`.

**Mechanism:** The judge is told *"You are a world-class Grandmaster Systems Architect **competing** in the Smart India Hackathon"* and to apply the four debater lenses. A neutral evaluator is thereby given a competitor's identity and incentives. In the evaluation path the model name is literally passed as `"Master Arbiter & Jury"`, producing a self-contradictory persona. `arbiter_name` is never passed through, so `prompts.py:479` falls back to a generic default.

**Fix:** Add `build_system_prompt_for_arbiter(arbiter_name, ministry_domain)` with a genuinely evaluative identity: impartial chair, no solution authorship, explicit instruction to reward evidence and penalise unsupported assertion, and no "competing" framing. Pass the real arbiter name through so it can be attributed honestly.

---

### HIGH

---

#### P5 — The output contract is not last, and truncation amputates it
**Where:** `orchestrator.py:747-748` and `751-752`.

**Mechanism:**
```python
if latest_research_dossier and latest_research_dossier.dossier_text:
    usr_prompt = f"{usr_prompt}\n\n{latest_research_dossier.dossier_text}"   # 747-748
if len(usr_prompt) > 30000:
    usr_prompt = usr_prompt[:30000] + "\n\n[Context truncated to provider-safe length.]"  # 751-752
```
Two failures. (a) The dossier is appended **after** `SCHEMA_GUIDE`, so the JSON contract is no longer in the recency-privileged final position. (b) `[:30000]` keeps the **head** and discards the **tail** — the schema is the first thing cut. The model is then asked for strict JSON while the JSON spec has been deleted from its prompt. This is a direct contributor to the P7 parse failures in §2.5.

**Fix:** Assemble in this order — role/task → problem → arbiter directive → peer transcript → research dossier → **output contract last**. Truncate the *middle* (peer transcript and dossier, oldest/lowest-value first), never the contract. Better: budget each block explicitly (`transcript ≤ 12k`, `dossier ≤ 8k`) and re-append `SCHEMA_GUIDE` after any truncation. A latent instance of the same bug exists at `consensus_eval.py:172` (`user_prompt[:40000]`), which would cut the 8-section spec and the "pure Markdown" instruction on longer runs.

---

#### P6 — System prompt and schema disagree about the four lenses
**Where:** `prompts.py:62-66` (system: 4 lenses always) vs `prompts.py:77-142` (per-pass Phase-1 schemas exposing subsets).

**Mechanism:** The system prompt mandates all four lenses on every turn; the Phase-1 pass schemas ask for one or two. The model resolves the conflict by over-answering. **Note — the content is not lost:** `parse_structured_turn` (`universal_client.py:85-190`) reads all four fields unconditionally. The real cost is wasted tokens against a fixed `max_tokens: 8192`, and inconsistent depth between passes.

**Fix:** Make the system prompt describe the lenses as an available toolkit, and let each pass prompt state authoritatively which lenses are in scope *for this turn* ("Apply ONLY the Architect and Critic lenses in this pass; the others come later").

---

#### P7 — Reasoning is placed inside a JSON string, and parse failure is recorded as real dissent
**Where:** `prompts.py:11-14`; parse at `universal_client.py:85-190`; defaults at `129-137`.

**Mechanism:** `deliberation_scratchpad` asks for long free-form reasoning **inside a JSON string value**. Any unescaped quote, newline, or stray backtick in thousands of characters of reasoning invalidates the whole object — and the object carries the vote, the solution, and every lens. There is no provider-native JSON enforcement (P8) and no repair-then-retry. The failure is then **laundered into data** as `DISAGREE / 50`.

`prompts.py:11` also contradicts itself: *"You may include a `<deliberation_scratchpad>` **before** the JSON"* while line 14 defines `deliberation_scratchpad` as a **field inside** the JSON.

Empirically (§2.5) this destroyed 28,565 chars of Qwen output entirely and mis-scored three models.

**Fix:**
- Resolve the contradiction: put reasoning **outside** the JSON in a real delimiter block, and remove the field from the schema:
  ```
  <scratchpad> ...free reasoning, no escaping needed... </scratchpad>
  ```json
  { ...structured output only... }
  ```
  ```
- On parse failure: retry once with the error message and the offending fragment, then fall back to `parse_failed` — **never** to a fabricated vote.

---

#### P8 — No provider-native structured-output enforcement anywhere
**Where:** all `stream_chat` call sites in `universal_client.py`.

**Mechanism:** Grep confirms `response_format`, `json_object`, `json_schema`, and tool/function-calling appear **nowhere in the codebase**. Compliance is requested in prose and then repaired with regex. Most models in your fleet are OpenAI-compatible and support `response_format={"type":"json_schema", ...}`, which makes malformed JSON structurally impossible.

**Fix:** Add per-model capability flags (`supports_json_schema`, `supports_json_object`). Send strict `json_schema` where supported, `json_object` as second choice, prose-only as last resort. This alone would eliminate most of P7. Keep the regex repair as a final safety net, not the primary mechanism.

---

#### P9 — No length budget, against a hard-coded `max_tokens: 8192`
**Where:** `max_tokens: 8192` hard-coded at three sites in `universal_client.py`; no per-field guidance in any prompt.

**Mechanism:** The schema asks for a scratchpad, four lenses, N critiques, N concessions, a full refined solution, positives, risks, research calls, and a vote — with no length guidance. Models spend the budget on early fields (scratchpad, lenses) and get truncated mid-object. **A truncated JSON object is an unparseable JSON object**, feeding straight into P7. The two Nemotron failures in §2.5 (9,361 and 7,969 raw chars against an 8192-token cap) are consistent with exactly this.

**Fix:** State explicit budgets in the schema comments (`architect_lens: 150-250 words`, `refined_solution: 400-600 words`, `critiques: 2-4 items, ≤80 words each`), instruct "if you must shorten, shorten the scratchpad first — the JSON structure must always close", and raise/parameterise `max_tokens` per model.

---

#### P10 — Round 2.3 is asked to compare across rounds but shown only one
**Where:** `prompts.py:206-278`.

**Mechanism:** The prompt asks the model to weigh how positions have evolved, but the transcript block contains only the immediately preceding round. Asked to compare against information it does not have, the model invents the trajectory.

**Fix:** Either supply a compact per-model position-history digest (one line per model per prior round), or remove the cross-round comparison demand from the instruction.

---

#### P11 — Phase 1 demands a consensus vote with no peers to agree with
**Where:** `prompts.py:77-142` — every Phase-1 pass schema includes `consensus_vote` and `agreement_percentage`.

**Mechanism:** Phase 1 is solo foundation work; there is nothing to consent to. The model votes on its own proposal, producing meaningless self-agreement that then enters `avg_debater_pct`.

**Fix:** Remove both fields from all Phase-1 pass schemas. Compute consensus only from rounds where peers were actually visible.

---

#### P12 — Empty "YOUR PREVIOUS POSITION" invites fabrication
**Where:** round prompt builders, `prompts.py:206-278`, `284-345`, `351-402`.

**Mechanism:** When a model failed, timed out, or was quarantined in the prior round, its "previous position" block renders empty or near-empty. The heading still asserts a position exists, so the model confabulates one — and then "defends" it. This is how a zero-byte model (§2.4) acquires a position it never stated.

**Fix:** Branch explicitly: `"⚠️ You did not submit a response in the previous round. Do not claim a prior position. Begin fresh from the peer transcript below."`

---

### MODERATE

---

#### P13 — Delimiter collisions in interpolated text
**Where:** `prompts.py:504` interpolates `{phase_title}` **inside a JSON example**; problem statements and peer text are interpolated into prompts containing fenced code blocks.

**Mechanism:** A problem statement containing `"`, `{`, `}`, or ``` corrupts the surrounding example or closes the fence early, degrading contract clarity.

**Fix:** Wrap all interpolated free text in unambiguous XML-style tags (`<problem_statement>…</problem_statement>`), and never interpolate variables inside JSON examples — use a static placeholder.

---

#### P14 — `NO_CODE_RULE` conflicts with what the prompts demand, and is duplicated
**Where:** `prompts.py:5-8`, injected via `prompts.py:71` (system) **and** again at `prompts.py:569` (final report), among others.

**Mechanism:** "DO NOT WRITE ANY CODE, SCRIPT SNIPPETS, OR PSEUDOCODE" sits alongside demands for algorithm pipelines, preprocessing stages, inference latency budgets, and query pipelines (`prompts.py:576`). Models resolve this by writing prose that gestures at algorithms without specifying them — losing exactly the technical precision SIH judges reward. Duplicate injection also wastes tokens and doubles the emphasis on the wrong constraint.

**Fix:** Replace with a precise rule: *"Do not write implementation code. **Do** specify algorithms by name, complexity, parameters, data structures, and I/O contracts. Numbered step lists and equations are encouraged; language-specific syntax is not."* Inject once.

---

#### P15 — Fake `self_pass_1_1` target id
**Where:** Phase-1 critique scaffolding, `prompts.py:77-142`.

**Mechanism:** A synthetic target id is presented as though it were a peer model id, teaching the model that self-critique and peer-critique share an addressing space. This pollutes the `critiques` array with self-referential entries that P1's fix would then try to route to a nonexistent peer.

**Fix:** Use a distinct field for self-critique (`self_identified_weaknesses: [...]`) and reserve `critiques[].target_model_id` for real peers only.

---

#### P16 — "OMNISCIENT" / "salvage" framing inflates confidence
**Where:** arbiter prompt `prompts.py:404-519`; superlative framing in `prompts.py:58`.

**Mechanism:** Instructing the arbiter to be omniscient and to "salvage insights from failed nodes" biases it toward finding merit everywhere, including in models that produced nothing. This is the mechanism behind the fabricated sign-offs in §2.4 and the score clustering in §2.6.

**Fix:** Replace with calibrated-judge framing: *"Report only what the transcript supports. If a model did not respond, state 'no submission' and assign no credit. Unsupported claims must be flagged, not repaired."*

---

#### P17 — "Zero politeness" optimizes rhetoric over substance
**Where:** debate round prompts, `prompts.py:206-402`.

**Mechanism:** Aggression directives produce confident dismissals rather than calibrated technical objections, and discourage the concessions the pipeline explicitly wants (`concessions_and_defenses`). Adversarial *rigour* and adversarial *tone* are different levers; only the first improves output quality.

**Fix:** *"Be rigorous, specific, and unsparing about technical flaws. Attack assumptions, not authors. Concede immediately when a peer is right — a concession backed by reasoning scores higher than a defended error."*

---

#### P18 — `critic_lens` carries two different meanings
**Where:** `prompts.py:16` (schema: "edge cases, failure modes, fragile assumptions" — self-directed) vs the debate rounds, where the same field is used to critique peers.

**Mechanism:** One field must hold both self-critique and peer-critique, so it holds an unpredictable mix, weakening both the transcript rendering and the arbiter's read.

**Fix:** Split into `self_critique_lens` and route peer critique exclusively through the structured `critiques` array.

---

#### P19 — The Arbiter Command Console is regex-only but attributed to the model
**Where:** `orchestrator.py:1159-1243` (`execute_arbiter_command`).

**Mechanism:** The function is **entirely keyword matching — there is no LLM call anywhere in it** — yet every reply is prefixed `👑 **Master Arbiter ({arbiter_config.name})**`. The user believes they are talking to the arbiter. Worse, the keyword sets overlap: *"retry the dropped model"* matches both `is_disable_cmd` (`drop`) and `is_enable_cmd` (`retry`), and **disable is evaluated first** — so a retry request disables the model instead.

**Fix:** Either route the command through the arbiter model with a tool/function-calling schema (correct fix, and it makes the attribution honest), or relabel to `⚙️ System Command` and resolve precedence by scoring intent rather than first-match.

---

#### P20 — No instruction for handling a source that contradicts the model
**Where:** dossier construction `research_engine.py:405-445`; citation protocol `prompts.py:68-69`.

**Mechanism:** The dossier ends with a "DEBATER MANDATORY CITATION PROTOCOL" but never says what to do when a retrieved source **refutes** the model's own spec. Models default to citing supportively and ignoring contradictions — the opposite of research grounding.

**Fix:** Add: *"If a source contradicts your specification, you must either revise the spec or state explicitly why the source does not apply. Citing a source you contradict without comment is a scoring failure."*

---

#### P21 — Emoji density in machine-parsed prompts
**Where:** throughout `prompts.py`.

**Mechanism:** Heavy emoji use in section markers consumes tokens, and emoji adjacent to JSON fences occasionally leaks into model output where it interferes with the regex repair path.

**Fix:** Keep emoji for UI-facing strings; use plain ASCII headers in model-facing prompts.

---

## 4. Part B — Deliverable-Layer Defects (new)

These concern the artifact you actually submit, and were found by auditing the shipped verdict file against the code that produces it.

---

#### D1 — CRITICAL: the final deliverable is written from 0.7% of the deliberation
**Where:** `prompts.py:537-552` (history assembly), specifically `545-546` (`sol[:200]`) and `542` (`[:250]`).

**Mechanism:** Per §2.2 — 972,567 chars produced, 6,804 chars delivered, **99.30% discarded**. The document that represents your entire multi-model debate is synthesized from 200-character fragments. The arbiter cannot possibly reproduce the technical depth the models generated, so it fills the gap with generic content and plausible invention. This is the root cause of D2 and D3.

**Fix:** Restructure the final-report context. Instead of uniform truncation:
- Pass the **full** `refined_solution` of the top-scoring 2-3 models from the final round.
- Pass the **full** `friction_points` and `executive_synthesis` from every round's arbiter eval (these are already dense summaries — that is what they are for).
- Pass the resolved critique/concession ledger (which side won each argument).
- Drop the per-round × per-model 200-char fragments entirely; they are noise.
- Consider a two-stage write: section-by-section generation with the relevant evidence for each section, then a coherence pass. This also removes the `max_tokens` ceiling on a long document.

---

#### D2 — CRITICAL: the deliverable is written with zero research grounding while being told to cite
**Where:** `prompts.py:522-532` (no dossier parameter); `consensus_eval.py:173-176` (system prompt) → `prompts.py:68-69` (citation protocol).

**Mechanism:** `build_final_markdown_report_prompt` accepts `problem_statement`, `phase_title`, rounds, models, `ministry_domain`, `phase_prompt` — **and no research dossier.** Meanwhile the system prompt it is paired with instructs the model to cite `[Paper 1]`, `[Fact-Check 2]`, `[Feasibility 1]` tags. The citation instruction is conditional ("When a Live Research Dossier is attached") but there is no *negative* instruction, and no validation of emitted citations against any source list. Result: §2.3 — four fabricated academic references and eleven `[Source 8]` markers in a run where `latest_research_dossier` was `None`.

**Fix (three layers, all needed):**
1. **Pass the dossier** into the final report prompt, with its real tags.
2. **Hard negative instruction:** *"You may cite ONLY the tagged sources listed below. If no sources are listed, you MUST NOT cite any paper, arXiv id, journal, or conference. Write 'No external sources were retrieved for this run' in place of a research section."*
3. **Validate before saving:** extract every `[...]` citation tag from the generated report and assert each resolves to a dossier item. On failure, strip the citation or regenerate. A fabricated citation must never reach disk.

---

#### D3 — HIGH: the sign-off certificate structurally requires fabrication
**Where:** `prompts.py:579`; interacts with `prompts.py:544-550`.

**Mechanism:** The section spec demands "a formal sign-off certificate with notes from **every** participating AI model". A model that returned zero bytes but is marked `status=completed` (§2.4) renders at `prompts.py:545-546` as `- **Claude Opus 5.0 [COMPLETED]:** ` with nothing after it. The arbiter, required to produce a note for it, invents one. Note that `prompts.py:547-548` *does* correctly render `[ERROR]`/`[TIMEOUT]`/`[QUARANTINED]` states — the hole is specifically the **zero-byte-but-`completed`** case.

**Fix:**
- Treat empty output as a failure at the source: if `raw_text.strip()` is empty, set `status = "error"`, not `completed` (this also fixes its contribution to `avg_debater_pct` — see P3).
- Change the spec to: *"Sign-off must list only models that submitted substantive content. For each, quote or paraphrase the specific contribution from the transcript. Models that did not submit must be listed separately under 'Non-participating (no submission)'. Do not invent contributions."*
- Drop the word "unanimously" unless unanimity is computed and true.

---

#### D4 — HIGH: no output-format validation — the deliverable reached disk as raw JSON
**Where:** `consensus_eval.py:186-204`; saved as-is.

**Mechanism:** `SIH_Master_Consensus_Verdict_397de6ca-6d4.md` is **not markdown.** Its entire content is:
````
```json
{
  "consensus_document": "# 🏆 SIH Master Consensus Deliverable: Phase 1\n\n## 1. ...
}
```
````
— a JSON wrapper with literal `\n` escapes, despite `prompts.py:581` instructing *"Generate ONLY the pure Markdown content."* Your headline artifact is unreadable as markdown.

*Honest caveat:* this file was generated under an **earlier** prompt revision — its nine section titles differ from the current eight-section spec at `prompts.py:571-579`, so I cannot attribute the JSON wrapping to today's exact prompt text. **What is current and unambiguous is the absence of any guard:** `consensus_eval.py:202` does `report = best_report` with only an empty-string fallback. Nothing checks that the output is markdown, nothing strips a fence, nothing unwraps a JSON envelope. Whenever a model does wrap (and it demonstrably does), the corrupt artifact is saved silently.

**Fix:** Post-process before saving: detect and strip a leading ```` ```json ```` / ```` ``` ```` fence; if the payload parses as JSON with a single long string value, unwrap it and un-escape; assert the result starts with `#` and contains the expected `## ` section headings; on failure, retry once with an explicit correction. Also note `consensus_eval.py:195-198` intends "keep the longest candidate" but `if len(best_report.strip()) > 200: break` exits after the first adequate one — the comparison is effectively dead.

---

#### D5 — MODERATE: hardware/IoT bias is injected into every problem, including software-only ones
**Where:** `prompts.py:58` ("Software **& Hardware** Systems Architect"), `65` ("45°C Indian summer, dust, battery discharge curves"), `17` ("Hardware ICs, microcontrollers, power budget"), `120` (same, with "intermittent grid/2G connectivity"), `575` (BOM section).

**Mechanism:** For a **crypto-forensics** problem statement, the models were still instructed to reason about ambient heat, dust, and battery curves, and to itemise microcontrollers. The deliverable shows the cost directly — it contains a section titled *"## 4. Edge AI & TinyML Anomaly Detection Pipeline"* and a *"Hardware Bill of Materials (BOM) & Power Budget"*, each opening with an apology for its own existence:

> *"Note: Given that this is a cloud-native and secure on-premise government datacenter deployment rather than a remote field sensor network, the BOM outlines…"*
> *"Note: Adapted for server-side real-time stream processing…"*

Tokens and attention were spent reconciling an irrelevant mandate. `prompts.py:575` and `120` do carry "…if hardware / …if software" conditionals — good — but the **system prompt and lens names do not**, and the system prompt wins on identity framing. Many SIH problem statements are pure software; this bias degrades all of them.

**Fix:** Add a problem-domain classification step (hardware / software / hybrid) at session start — either a cheap LLM call or a keyword heuristic — and select a domain-appropriate system prompt, lens set, and section spec. Rename `field_hardware_lens` to `feasibility_lens` with domain-conditional guidance. For software problems: cloud cost model, data volumes, latency budgets, and scaling limits replace BOM and power.

---

#### D6 — MODERATE: the arbiter evaluates on 200-char excerpts
**Where:** `prompts.py:452` — `st.field_hardware_lens[:200]`, with sibling truncations in the same block.

**Mechanism:** The arbiter — which produces the consensus score, friction points, and next-round challenge — reads each lens at 200 characters. It is scoring summaries, not solutions. This weakens the 40% arbiter component of the blended score (`consensus_eval.py:109-117`) and explains why arbiter synthesis stays high-level.

**Fix:** Raise per-lens budgets substantially (1,000-1,500 chars, consistent with `orchestrator.py:97-98` which already uses `[:1500]`), and prioritise: full text for the round's key disputes, tighter truncation elsewhere.

---

## 5. Part C — Alignment Against Your Own Blueprint

Checked against `MULTI_AI_DEBATE_ARCHITECTURE.md`. This distinguishes *deliberate design choices* from *implementation drift* — and the finding is that **the most damaging prompting defects are drift, not design.**

| Blueprint requirement | Line | Implemented? |
|---|---|---|
| "Each AI is presented with all counter-arguments targeted at its original proposal" | 74 | **NO** — this is P1. Your design was right; the code lost it. |
| Models categorise Concessions / Rebuttals / Updated Solution v2.0 | 75-78 | **PARTIAL** — the schema fields exist, but with nothing to respond to (P1) they cannot be used as intended. |
| Arbiter evaluates the full chain: initial proposals → counter-arguments → rebuttals | 84 | **NO** — the chain is never assembled; the arbiter sees 200-char excerpts (D6). |
| `CounterMatrix.tsx` — "Interactive cross-critique graph / cards" | 126 | **DEAD CODE** — the file exists (2,856 bytes) and is **never imported**. |
| Deliverable section: **Comparative Debate Matrix** | 168 | **MISSING** from the 8-section spec (`prompts.py:571-579`). |
| Deliverable section: **Pre-Empted Risks & Mitigations** | 170 | **MISSING** from the 8-section spec. |
| Deliverable section: **Implementation Action Plan** | 171 | **MISSING** from the 8-section spec. |

**Five blueprint components exist as files but are imported nowhere:** `CounterMatrix.tsx`, `RoundTimeline.tsx`, `ModeratorControls.tsx`, `VerdictViewer.tsx`, `ProblemInput.tsx` (grep-verified against `page.tsx`).

**Combined effect:** the 87.5 KB of cross-critique from §2.1 is invisible **twice** — never delivered to peers (P1) and never rendered to you (dead `CounterMatrix`). The single most valuable output of a multi-model debate is currently write-only.

**Recommendation:** restoring the three missing deliverable sections is high-value and cheap. *Comparative Debate Matrix* and *Pre-Empted Risks & Mitigations* are exactly what SIH judges probe for, and — critically — they can be built from **structured data you already have** (`critiques`, `concessions_and_defenses`, `friction_points`) rather than from model invention. That makes them both more useful and more trustworthy than the sections currently being generated.

---

## 6. Part D — Architecture & Runtime Defects

Retained from the line-by-line architecture audit. **Line references here are approximate** where `orchestrator.py` has since changed. Per your instruction, security is out of scope (local app) — hardcoded keys, `verify=False`, and CORS wildcard are noted once and not itemised.

### CRITICAL

**C1 — Un-registered `run_round_loop` task** (`main.py:~630`). The task is created without being tracked. Two consequences: `force_call_verdict` cannot cancel it, and a pause→resume cycle spawns a **second concurrent loop** — doubling API spend and interleaving writes into one session. *Fix:* store the task handle on the session registry; cancel-then-replace on resume; assert single-loop invariant.

**C2 — No top-level exception guard in `run_round_loop`.** Any unhandled exception kills the loop with `status` left `"running"` forever, and no `DEBATE_ERROR` event is emitted, so the UI waits indefinitely. *Fix:* wrap the loop body in `try/except`, set `status="error"`, persist `error_message`, and emit a terminal SSE event.

**C3 — `/followup` runs zero rounds.** `pipeline_index` is set past the end (→13), so the `while` loop never executes; control jumps straight to the final verdict and appends a duplicate phase. *Fix:* reset `pipeline_index` to the start of the new phase and set the correct target round count.

**C4 — `current_phase_index` collision.** **Already fixed by you** via `workspace_phase_number` (visible at `consensus_eval.py:167`).

**C5 — Temperature-retry uses a closed response** (`universal_client.py:~381-386`). The retry assigns a response object that was closed on `with`-block exit, so models that reject the requested temperature **never stream at all**. *Fix:* re-issue the request inside a fresh context manager.

### HIGH (summary)

| ID | Defect |
|---|---|
| H1 | Mid-stream failure duplicates or discards partial output depending on failover path |
| H2 | Live-config mutation persists key rotation globally, leaking across sessions |
| H3 | `except (asyncio.CancelledError, Exception)` swallows cancellation, breaking pause/abort |
| H4 | 2-second auto-abort supervisor produces an SSE event flood |
| H5 | Pause does not stop in-flight streams — tokens keep arriving and billing continues |
| H6 | `/moderator` resume lacks the completed-guard that `/resume` has |
| H7-H8 | Retry/quarantine bookkeeping diverges between failover paths |
| H9 | Arena renders from client-side `models`, not `session.models` — UI desyncs from truth |
| H10 | Completed responses silently discarded on race with round advance |
| H11-H14 | Stream/queue lifecycle and reconnect edge cases |
| H15 | One Pydantic-unloadable workspace (`78b84bb9`, `rounds.0.round_number | Field required`) is still listed in History → permanent 404 + infinite SSE reconnect loop. Empirically: **LOADABLE: 25, UNLOADABLE: 1.** *Fix:* validate on list, mark corrupt entries, and add a schema-migration shim for legacy records. |

Also identified: 21 MODERATE and 11 LOW findings (state-sync, logging, and UX-consistency issues), unchanged from the architecture audit.

**Recommended runtime fix order:** `C1 → C2 → C5 → H9 → C3`.

---

## 7. Part E — What Is Genuinely Good (do not break these)

Worth stating plainly, because the fixes above should preserve all of it:

1. **The 13-step pipeline design is excellent** — separating solo genesis (Phase 1) from adversarial rounds, with research injection at R1/R2/R3, is the right shape for research-grounded solution-making.
2. **The four-lens cognitive decomposition is a strong idea.** Forcing architect / red-team / feasibility / compliance perspectives is exactly how you get past shallow LLM output. It needs domain conditioning (D5), not removal.
3. **Structured output with a typed schema** is the right call over free prose — it just needs native enforcement (P8).
4. **Multi-key × multi-model failover with quarantine** is genuinely robust engineering, and the reason the 11-model run completed at all.
5. **Atomic `tmp` + `os.replace` persistence** is correct, and the shared-cache identity in `SessionStorage._memory_cache` means there are **no lost-update races** — a real design win.
6. **`autonomous_research_calls`** — letting debaters request their own evidence is the most sophisticated idea in the system and is underexploited rather than broken.
7. **Explicit `[ERROR]`/`[TIMEOUT]`/`[QUARANTINED]` rendering** at `prompts.py:547-548` shows the right instinct about honesty in transcripts; it just needs extending to the zero-byte case (D3).

---

## 8. Part F — Prioritized Fix Plan

Ordered by *value per unit of effort toward winning SIH*, not by severity label.

### Tier 1 — Stop producing untrustworthy documents (do first)
| Fix | ID | Why first |
|---|---|---|
| Never emit uncited-source citations; validate every tag before save | **D2** | Fabricated academic references are disqualification-class risk |
| Stop fabricating sign-offs; treat zero-byte as error | **D3** | False attestation in a Ministry-facing document |
| Validate/unwrap the final report format before saving | **D4** | Your headline artifact is currently corrupt |
| Never fabricate votes on parse failure | **P3/P7** | Removes constants from the headline metric |

### Tier 2 — Make it an actual debate (highest quality gain)
| Fix | ID |
|---|---|
| Deliver targeted critiques to the models they target | **P1** |
| Inject `next_round_challenge` + `friction_points` into round prompts | **P2** |
| Give the deliverable real context (full solutions + friction ledger) | **D1** |
| Give the arbiter a neutral evaluator system prompt | **P4** |

### Tier 3 — Structural reliability of output
| Fix | ID |
|---|---|
| Provider-native `json_schema` / `json_object` enforcement | **P8** |
| Move reasoning outside the JSON; resolve the scratchpad contradiction | **P7** |
| Contract last + truncate the middle, never the schema | **P5** |
| Per-field length budgets; parameterise `max_tokens` | **P9** |

### Tier 4 — Calibration & domain fit
`P3` (rubric anchoring) · `D5` (domain classification) · `D6` (arbiter truncation) · `P16` (calibrated framing) · `P17` (rigour over aggression) · `P11` (drop Phase-1 votes) · `P12` (missing-position branch)

### Tier 5 — Hygiene & restoration
`P6` · `P10` · `P13` · `P14` · `P15` · `P18` · `P19` · `P20` · `P21` · restore the three missing deliverable sections and wire up `CounterMatrix.tsx` (Part C)

### Runtime track (parallel, independent of prompting)
`C1 → C2 → C5 → H9 → C3`, then `H15`.

---

## 9. Appendix — Reproducing the Evidence

```bash
cd backend/data/workspaces/SIH26183_Real_Time_Identification_o_397de6ca-6d4
python -c "import json,io; d=json.load(io.open('session_state.json',encoding='utf-8')); print(d['latest_research_dossier'])"
```

Key reproducible facts:
- `latest_research_dossier` → `None` (proves the citations in the deliverable are fabricated)
- Critiques/concessions per round: R2 `26/18`, R3 `25/25`, R4 `25/29` → 87,546 chars serialized
- `Claude Opus 5.0` → `raw_text` length `0` in rounds 1 and 2, `status="completed"`
- `Qwen 3.8 Max` → `raw_text` 28,565 chars, parsed lens content 0 chars, recorded `DISAGREE/50`
- Content reaching the final-report prompt: 6,804 of 972,567 chars → **99.30% discarded**

*On Windows, use `io.open(..., encoding='utf-8')` — the default cp1252 codec raises `UnicodeEncodeError` on the emoji in these files.*

---

**End of audit. No fixes applied — awaiting your instructions on what to implement.**
