import asyncio
import time
import json
import os
import re
from typing import Dict, List, Optional, Set
from app.schemas import (
    DebateSession,
    RoundData,
    DebaterResponse,
    StructuredDebateTurn,
    ModelConfig,
    ArbiterEvaluation,
    WorkspacePhase,
    PooledResearchDossier,
    AutonomousResearchCall
)
from app.providers.universal_client import (
    UniversalAIClient,
    parse_structured_turn
)
from app.engine.prompts import (
    build_system_prompt_for_debater,
    build_phase_1_pass_prompt,
    build_phase_2_round_prompt,
    build_phase_3_round_prompt,
    build_phase_4_round_prompt,
    build_arbiter_evaluation_prompt,
    build_final_markdown_report_prompt,
    build_schema_guide,
    get_phase_1_schema_guide,
    classify_problem_domain
)
from app.engine.consensus_eval import (
    evaluate_round_consensus,
    generate_final_markdown_report
)
from app.storage import SessionStorage, sanitize_folder_name
from app.providers.research_engine import ResearchEngine

# A heading-ish line: at least one leading marker (#, **, "3.", or an emoji) followed by a
# lens keyword. Requiring a marker keeps ordinary prose that merely begins with the word
# "Security" from being mistaken for a section heading.
_HEAL_HEADING_PREFIX = (
    r"^[ \t]{0,3}(?:#{1,6}[ \t]*|\*{2}[ \t]*|\d{1,2}[.)][ \t]*"
    r"|[\U0001F300-\U0001FAFF☀-➿️][ \t]*)+"
)
_HEAL_HEADING_RES = [
    (label, re.compile(_HEAL_HEADING_PREFIX + keyword, re.IGNORECASE | re.MULTILINE))
    for label, keyword in [
        ("architect", r"(?:Lead\s+)?Architect"),
        ("critic", r"(?:Critic|Devil|Red[-\s]?Team|Murphy)"),
        ("field", r"(?:Field|Hardware|BOM|Bill\s+of\s+Materials|Frugal|Pragmatist|Feasibilit)"),
        ("security", r"(?:Security|Compliance|Fort\s+Knox|Reliabilit)"),
        # Terminates the last lens without itself becoming a lens.
        ("__end__", r"(?:Refined|Final\s+Solution|Conclusion|Consensus|Vote)"),
    ]
]


def _extract_markdown_lenses(raw_text: str) -> Dict[str, str]:
    """
    Maps lens label -> section body for a response that came back as Markdown prose.

    Each section runs from its own heading to the NEXT recognised heading, or to end-of-text.
    The previous implementation used a lookahead that required a following `##` heading, so
    whichever lens happened to be last - which is exactly what happens when output is cut off
    mid-answer - matched nothing and was silently discarded.
    """
    found = []
    for label, rx in _HEAL_HEADING_RES:
        m = rx.search(raw_text)
        if m:
            found.append((m.start(), label))
    found.sort()

    out: Dict[str, str] = {}
    for i, (start, label) in enumerate(found):
        end = found[i + 1][0] if i + 1 < len(found) else len(raw_text)
        if label != "__end__":
            out[label] = raw_text[start:end].strip()
    return out


def heal_unstructured_turn(raw_text: str, model_name: str, ministry_domain: str = "Smart India Hackathon") -> StructuredDebateTurn:
    """
    Converts a raw unformatted or partial debater response into a StructuredDebateTurn so
    prose that missed the JSON contract is not thrown away.

    What this function must NEVER do is invent a position. The previous version guessed a
    `consensus_vote` and `agreement_percentage` from keyword matching ("agree" anywhere in
    the text -> AGREE/85) and filled empty lenses with strings like "Security controls
    integrated." Both fabrications then flowed into the consensus score and into the
    arbiter's prompt as if they were the model's actual analysis. Healing recovers CONTENT
    only; the position stays unset and `parse_ok` stays False.
    """
    if not raw_text or not raw_text.strip():
        return StructuredDebateTurn(
            refined_solution="",
            consensus_vote=None,
            agreement_percentage=None,
            parse_ok=False
        )

    # First attempt standard parse
    st = parse_structured_turn(raw_text)
    if st.architect_lens or st.critic_lens or st.field_hardware_lens or st.security_compliance_lens:
        return st

    # Markdown Section Extraction Heuristics
    sections = _extract_markdown_lenses(raw_text)
    architect = sections.get("architect", "")
    critic = sections.get("critic", "")
    hardware = sections.get("field", "")
    security = sections.get("security", "")
    solution = raw_text

    # Recover the vote ONLY if the model stated it explicitly and unambiguously in prose.
    # Anything less stays None: an abstention is excluded from the consensus average, a
    # guessed vote silently corrupts it.
    vote = None
    pct = None
    explicit_vote = re.search(
        r"consensus[_\s]*vote\s*[\"']?\s*[:=]\s*[\"']?\s*(AGREE|DISAGREE|NEEDS[_\s]?REFINEMENT)",
        raw_text, re.IGNORECASE
    )
    if explicit_vote:
        vote = explicit_vote.group(1).upper().replace(" ", "_")
    explicit_pct = re.search(
        r"agreement[_\s]*percentage\s*[\"']?\s*[:=]\s*[\"']?\s*(\d{1,3})",
        raw_text, re.IGNORECASE
    )
    if explicit_pct:
        try:
            pct = max(0, min(100, int(explicit_pct.group(1))))
        except Exception:
            pct = None

    return StructuredDebateTurn(
        architect_lens=architect[:4000],
        critic_lens=critic[:4000],
        critic_devil_advocate_lens=critic[:4000],
        field_hardware_lens=hardware[:4000],
        pragmatist_feasibility_lens=hardware[:4000],
        security_compliance_lens=security[:4000],
        security_reliability_lens=security[:4000],
        refined_solution=solution,
        consensus_vote=vote,
        agreement_percentage=pct,
        parse_ok=False
    )


# Complete Deliberation Pipeline Definition
DELIBERATION_PIPELINE = [
    # Phase 1: Multi-Persona Genesis (Internal 4-Pass Foundation)
    {"phase_index": 1, "phase_title": "Phase 1: Multi-Persona Genesis", "pass_id": "1.1", "pass_title": "Pass 1.1: 🏛️ Lead Architect Genesis", "is_research": False},
    {"phase_index": 1, "phase_title": "Phase 1: Multi-Persona Genesis", "pass_id": "1.2", "pass_title": "Pass 1.2: 😈 Murphy's Law Inversion", "is_research": False},
    {"phase_index": 1, "phase_title": "Phase 1: Multi-Persona Genesis", "pass_id": "1.3", "pass_title": "Pass 1.3: ⚙️ Frugal Field & BOM Reality", "is_research": False},
    {"phase_index": 1, "phase_title": "Phase 1: Multi-Persona Genesis", "pass_id": "1.4", "pass_title": "Pass 1.4: 🛡️ Fort Knox Security & Compliance", "is_research": False},
    
    # Research Block 1
    {"phase_index": 1, "phase_title": "Research Block 1", "pass_id": "R1", "pass_title": "🔬 Research Block 1: Pooled Peer Fact-Check & Frontier Papers", "is_research": True},
    
    # Phase 2: Adversarial Crucible (3-Round Courtroom Debate)
    {"phase_index": 2, "phase_title": "Phase 2: Adversarial Crucible", "pass_id": "2.1", "pass_title": "Round 2.1: 🥊 Opening Cross-Examination", "is_research": False},
    {"phase_index": 2, "phase_title": "Phase 2: Adversarial Crucible", "pass_id": "2.2", "pass_title": "Round 2.2: 🛡️ Rebuttal, Defense & Counter-Attack", "is_research": False},
    {"phase_index": 2, "phase_title": "Phase 2: Adversarial Crucible", "pass_id": "2.3", "pass_title": "Round 2.3: ⚖️ Closing Flaw Scrutiny & Vulnerability Locking", "is_research": False},
    
    # Research Block 2
    {"phase_index": 2, "phase_title": "Research Block 2", "pass_id": "R2", "pass_title": "🔬 Research Block 2: Pooled Hardware IC & SOTA Algorithm Scan", "is_research": True},
    
    # Phase 3: The 10x Advanced Solution Engine (2 Rounds)
    {"phase_index": 3, "phase_title": "Phase 3: 10x Advanced Solutions", "pass_id": "3.1", "pass_title": "Round 3.1: 🚀 The 10x Quantum Leap (4 Pillars)", "is_research": False},
    {"phase_index": 3, "phase_title": "Phase 3: 10x Advanced Solutions", "pass_id": "3.2", "pass_title": "Round 3.2: 🔬 Micro-Optimization & Cross-Pollination", "is_research": False},
    
    # Research Block 3
    {"phase_index": 3, "phase_title": "Research Block 3", "pass_id": "R3", "pass_title": "🔬 Research Block 3: Final Standards & Citation Audit", "is_research": True},
    
    # Phase 4: Convergence Crucible & Sovereign Master Blueprint
    {"phase_index": 4, "phase_title": "Phase 4: Convergence Crucible", "pass_id": "4.1", "pass_title": "Round 4.1: 🤝 Concession Treaty & Master Assembly", "is_research": False}
]

# Character ceiling for an assembled debater prompt. Raised from the old 30,000 because that
# limit was routinely hit once peer transcripts and the research dossier were included, and
# the excess was cut from the tail - which is exactly where the output contract lives.
DEBATER_PROMPT_LIMIT = 80000

class DebateOrchestrator:
    _event_queues: Dict[str, Set[asyncio.Queue]] = {}
    _running_tasks: Dict[str, asyncio.Task] = {}
    _running_round_tasks: Dict[str, Dict[str, asyncio.Task]] = {}
    _quarantined_models: Dict[str, Set[str]] = {}
    _pending_injections: Dict[str, str] = {}
    _pause_flags: Dict[str, asyncio.Event] = {}
    _quarantine_strikes: Dict[str, Dict[str, int]] = {}
    _control_locks: Dict[str, asyncio.Lock] = {}

    @classmethod
    def get_event_queue(cls, session_id: str) -> asyncio.Queue:
        if session_id not in cls._event_queues:
            cls._event_queues[session_id] = set()
        q = asyncio.Queue(maxsize=1000)
        cls._event_queues[session_id].add(q)
        return q

    @classmethod
    def remove_event_queue(cls, session_id: str, q: asyncio.Queue):
        if session_id in cls._event_queues and q in cls._event_queues[session_id]:
            cls._event_queues[session_id].remove(q)
            if not cls._event_queues[session_id]:
                cls._event_queues.pop(session_id, None)

    @classmethod
    async def broadcast_event(cls, session_id: str, event_type: str, data: dict):
        if session_id not in cls._event_queues:
            return
        payload = {
            "event": event_type,
            "data": data,
            "timestamp": time.time()
        }
        for q in list(cls._event_queues[session_id]):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                if event_type == "MODEL_TOKEN_DELTA":
                    continue
                try:
                    q.get_nowait()
                    q.put_nowait(payload)
                except (asyncio.QueueEmpty, asyncio.QueueFull):
                    pass
            except Exception:
                pass

    @staticmethod
    def _fit_debater_prompt(assembled: str, contract_tail: str, limit: int) -> str:
        """
        Guarantees two invariants for every debater prompt:
          1. The output contract is the LAST thing the model reads (recency position).
          2. Truncation removes evidence from the middle, never the contract from the tail.

        The research dossier used to be appended after the contract, and any overflow was cut
        with `[:30000]`, so on a long round the model received a transcript with no schema at
        all and answered in prose. Every such turn was scored as a non-submission.
        """
        core = assembled
        if contract_tail and contract_tail in core:
            core = core.replace(contract_tail, "").rstrip()

        reserve = len(contract_tail) + 200
        budget = max(2000, limit - reserve)
        if len(core) > budget:
            head_len = int(budget * 0.55)
            tail_len = budget - head_len - 200
            notice = (
                "\n\n[...middle of the evidence body truncated to fit the provider context window. "
                "Everything above and below is intact; reason only from what is present....]\n\n"
            )
            core = core[:head_len] + notice + core[-tail_len:]

        return f"{core}\n\n{contract_tail}" if contract_tail else core

    @classmethod
    def start_session(cls, session_id: str, auto_advance: bool = True) -> asyncio.Task:
        existing = cls._running_tasks.get(session_id)
        if existing and not existing.done():
            return existing
        task = asyncio.create_task(cls.run_round_loop(session_id, auto_advance=auto_advance))
        cls._running_tasks[session_id] = task
        return task

    @classmethod
    async def ensure_stopped(cls, session_id: str) -> None:
        await cls._cancel_active_tasks(session_id)
        task = cls._running_tasks.get(session_id)
        if task and not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        if cls._running_tasks.get(session_id) is task:
            cls._running_tasks.pop(session_id, None)

    @classmethod
    def control_lock(cls, session_id: str) -> asyncio.Lock:
        return cls._control_locks.setdefault(session_id, asyncio.Lock())

    @classmethod
    async def _cancel_active_tasks(cls, session_id: str) -> None:
        children = list(cls._running_round_tasks.get(session_id, {}).values())
        for child in children:
            if not child.done():
                child.cancel()
        if children:
            await asyncio.gather(*children, return_exceptions=True)

        parent = cls._running_tasks.get(session_id)
        current = asyncio.current_task()
        if parent and parent is not current and not parent.done():
            parent.cancel()
            await asyncio.gather(parent, return_exceptions=True)

    @classmethod
    def cleanup_session(cls, session_id: str, remove_subscribers: bool = False) -> None:
        cls._running_round_tasks.pop(session_id, None)
        cls._pause_flags.pop(session_id, None)
        cls._quarantined_models.pop(session_id, None)
        cls._quarantine_strikes.pop(session_id, None)
        cls._pending_injections.pop(session_id, None)
        if remove_subscribers:
            cls._event_queues.pop(session_id, None)

    @classmethod
    async def _execute_single_model_turn(
        cls,
        session_id: str,
        model_config: ModelConfig,
        phase_index: int,
        pass_id: str,
        pass_title: str,
        round_number: int,
        messages: list
    ) -> DebaterResponse:
        start_time = time.time()
        accumulated_text = ""
        
        await cls.broadcast_event(session_id, "MODEL_STREAM_START", {
            "model_id": model_config.id,
            "model_name": model_config.name,
            "phase_index": phase_index,
            "pass_id": pass_id,
            "pass_title": pass_title,
            "round_number": round_number
        })

        async def _on_key_promoted(cfg: ModelConfig, working_key: str):
            session = await SessionStorage.get_session(session_id)
            if session:
                for m in session.models:
                    if m.id == cfg.id:
                        m.api_key = working_key
                        m.model_id = cfg.model_id
                        break
                await SessionStorage.save_session(session)

            await cls.broadcast_event(session_id, "BACKUP_KEY_PROMOTED", {
                "model_id": cfg.id,
                "model_name": cfg.name,
                "promoted_key_masked": working_key[:6] + "..." + working_key[-4:] if len(working_key) > 10 else "***"
            })

        try:
            total_timeout = float(model_config.timeout_seconds or 600)
            FIRST_TOKEN_TIMEOUT = min(120.0, total_timeout)

            deadline = asyncio.get_running_loop().time() + total_timeout
            last_attempt_text: list[str] = []
            for attempt in [1, 2]:
                # Create a fresh text buffer and event for each attempt
                attempt_accumulated: list[str] = []
                last_attempt_text = attempt_accumulated
                attempt_event = asyncio.Event()

                # IMPORTANT: pass event and buffer as default arguments to avoid Python closure capture bug.
                async def _stream_collector(
                    _evt: asyncio.Event = attempt_event,
                    _buf: list = attempt_accumulated,
                ):
                    async for token in UniversalAIClient.stream_chat(
                        config=model_config,
                        messages=messages,
                        temperature=model_config.temperature,
                        on_key_promoted_cb=_on_key_promoted
                    ):
                        if not _evt.is_set():
                            _evt.set()
                        _buf.append(token)
                        await cls.broadcast_event(session_id, "MODEL_TOKEN_DELTA", {
                            "model_id": model_config.id,
                            "delta": token,
                            "round_number": round_number,
                            "pass_id": pass_id
                        })

                collector_task = asyncio.create_task(_stream_collector())

                if attempt == 1:
                    try:
                        remaining = deadline - asyncio.get_running_loop().time()
                        if remaining <= 0:
                            raise asyncio.TimeoutError
                        first_token_task = asyncio.create_task(attempt_event.wait())
                        done, _ = await asyncio.wait(
                            {first_token_task, collector_task},
                            timeout=min(FIRST_TOKEN_TIMEOUT, remaining),
                            return_when=asyncio.FIRST_COMPLETED,
                        )
                        if collector_task in done:
                            first_token_task.cancel()
                            await asyncio.gather(first_token_task, return_exceptions=True)
                            await collector_task
                        elif first_token_task not in done:
                            first_token_task.cancel()
                            await asyncio.gather(first_token_task, return_exceptions=True)
                            raise asyncio.TimeoutError
                        remaining = deadline - asyncio.get_running_loop().time()
                        if remaining <= 0:
                            raise asyncio.TimeoutError
                        await asyncio.wait_for(collector_task, timeout=remaining)
                        accumulated_text = "".join(attempt_accumulated)
                        break
                    except asyncio.TimeoutError:
                        collector_task.cancel()
                        try:
                            await collector_task
                        except asyncio.CancelledError:
                            if not collector_task.cancelled():
                                raise
                        except Exception:
                            pass
                        accumulated_text = "".join(attempt_accumulated)

                        if not attempt_event.is_set():
                            print(f"[AUTO-RETRY] Model '{model_config.name}' sent 0 words before its first-token deadline. Retrying once...")
                            await cls.broadcast_event(session_id, "MODEL_RETRY_ATTEMPT", {
                                "model_id": model_config.id,
                                "model_name": model_config.name,
                                "round_number": round_number,
                                "attempt": 2,
                                "message": "Auto-retrying once within the configured turn deadline..."
                            })
                            continue
                        else:
                            print(f"[PARTIAL] Model '{model_config.name}' timed out mid-stream after {len(accumulated_text)} chars.")
                            raise asyncio.TimeoutError
                else:
                    remaining = deadline - asyncio.get_running_loop().time()
                    if remaining <= 0:
                        raise asyncio.TimeoutError
                    try:
                        await asyncio.wait_for(collector_task, timeout=remaining)
                    except asyncio.TimeoutError:
                        collector_task.cancel()
                        try:
                            await collector_task
                        except asyncio.CancelledError:
                            if not collector_task.cancelled():
                                raise
                        except Exception:
                            pass
                        raise
                    accumulated_text = "".join(attempt_accumulated)

                    break
            
            clean_text = accumulated_text.strip()
            if not clean_text:
                raise RuntimeError("Model returned no usable token content.")
            if clean_text.startswith("[error:") or "Upstream error for model" in clean_text or clean_text.startswith('{"error":'):
                raise RuntimeError(clean_text)

            elapsed = time.time() - start_time
            structured = parse_structured_turn(accumulated_text)

            resp = DebaterResponse(
                model_id=model_config.id,
                model_name=model_config.name,
                phase_index=phase_index,
                pass_or_round_id=pass_id,
                pass_or_round_title=pass_title,
                round_number=round_number,
                raw_text=accumulated_text,
                structured=structured,
                status="completed",
                elapsed_seconds=elapsed
            )

            live_sess = await SessionStorage.get_session(session_id)
            if live_sess and live_sess.rounds and live_sess.rounds[-1].round_number == round_number:
                live_sess.rounds[-1].responses[resp.model_id] = resp
                await SessionStorage.save_session(live_sess)

            await cls.broadcast_event(session_id, "MODEL_STREAM_END", {
                "model_id": model_config.id,
                "model_name": model_config.name,
                "phase_index": phase_index,
                "pass_id": pass_id,
                "pass_title": pass_title,
                "round_number": round_number,
                "status": "completed",
                "structured": structured.model_dump(),
                "elapsed_seconds": elapsed,
                "response": resp.model_dump()
            })

            return resp

        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            err_msg = f"Model '{model_config.name}' exceeded timeout ({model_config.timeout_seconds}s)."
            partial_text = "".join(locals().get("last_attempt_text", [])).strip()
            
            resp = DebaterResponse(
                model_id=model_config.id,
                model_name=model_config.name,
                phase_index=phase_index,
                pass_or_round_id=pass_id,
                pass_or_round_title=pass_title,
                round_number=round_number,
                raw_text=partial_text,
                structured=parse_structured_turn(partial_text) if partial_text else StructuredDebateTurn(refined_solution=err_msg),
                status="timeout",
                elapsed_seconds=elapsed,
                error_message=err_msg
            )

            live_sess = await SessionStorage.get_session(session_id)
            if live_sess and live_sess.rounds and live_sess.rounds[-1].round_number == round_number:
                live_sess.rounds[-1].responses[resp.model_id] = resp
                await SessionStorage.save_session(live_sess)

            await cls.broadcast_event(session_id, "MODEL_STREAM_END", {
                "model_id": model_config.id,
                "model_name": model_config.name,
                "phase_index": phase_index,
                "pass_id": pass_id,
                "pass_title": pass_title,
                "round_number": round_number,
                "status": "timeout",
                "structured": resp.structured.model_dump(),
                "elapsed_seconds": elapsed,
                "error_message": err_msg,
                "response": resp.model_dump()
            })

            await cls.broadcast_event(session_id, "MODEL_TIMEOUT_ALERT", {
                "model_id": model_config.id,
                "model_name": model_config.name,
                "round_number": round_number,
                "timeout_seconds": model_config.timeout_seconds,
                "elapsed_seconds": elapsed,
                "error_message": err_msg
            })

            return resp

        except Exception as e:
            elapsed = time.time() - start_time
            err_msg = f"Error for Model '{model_config.name}': {str(e)}"
            partial_text = "".join(locals().get("last_attempt_text", [])).strip()
            
            resp = DebaterResponse(
                model_id=model_config.id,
                model_name=model_config.name,
                phase_index=phase_index,
                pass_or_round_id=pass_id,
                pass_or_round_title=pass_title,
                round_number=round_number,
                raw_text=partial_text,
                structured=parse_structured_turn(partial_text) if partial_text else StructuredDebateTurn(refined_solution=err_msg),
                status="error",
                elapsed_seconds=elapsed,
                error_message=err_msg
            )

            live_sess = await SessionStorage.get_session(session_id)
            if live_sess and live_sess.rounds and live_sess.rounds[-1].round_number == round_number:
                live_sess.rounds[-1].responses[resp.model_id] = resp
                await SessionStorage.save_session(live_sess)

            await cls.broadcast_event(session_id, "MODEL_STREAM_END", {
                "model_id": model_config.id,
                "model_name": model_config.name,
                "phase_index": phase_index,
                "pass_id": pass_id,
                "pass_title": pass_title,
                "round_number": round_number,
                "status": "error",
                "structured": resp.structured.model_dump(),
                "elapsed_seconds": elapsed,
                "error_message": err_msg,
                "response": resp.model_dump()
            })

            await cls.broadcast_event(session_id, "MODEL_ERROR_ALERT", {
                "model_id": model_config.id,
                "model_name": model_config.name,
                "round_number": round_number,
                "error_message": err_msg
            })

            return resp

    @classmethod
    async def run_round_loop(cls, session_id: str, auto_advance: bool = True):
        try:
            await cls._run_round_loop(session_id, auto_advance=auto_advance)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            session = await SessionStorage.get_session(session_id)
            if session:
                session.status = "error"
                session.error_message = str(exc)
                try:
                    await SessionStorage.save_session(session)
                except Exception:
                    pass
            await cls.broadcast_event(session_id, "DEBATE_ERROR", {"message": str(exc), "status": "error"})
        finally:
            await cls._cancel_active_tasks(session_id)
            current = asyncio.current_task()
            if cls._running_tasks.get(session_id) is current:
                cls._running_tasks.pop(session_id, None)
            cls._running_round_tasks.pop(session_id, None)
            final_session = await SessionStorage.get_session(session_id)
            if final_session and final_session.status in {"completed", "error"}:
                cls.cleanup_session(session_id)

    @classmethod
    async def _run_round_loop(cls, session_id: str, auto_advance: bool = True):
        session = await SessionStorage.get_session(session_id)
        if not session:
            return

        if session_id not in cls._pause_flags:
            cls._pause_flags[session_id] = asyncio.Event()
        cls._pause_flags[session_id].set()

        # D5: classify once, lazily, so sessions created before this field existed also get
        # a domain. The classifier picks which lens set and which cost/BOM section spec the
        # prompts use - a pure-software problem should not be asked for battery discharge
        # curves and a 45C ambient analysis.
        if not session.problem_domain:
            session.problem_domain = classify_problem_domain(
                f"{session.problem_statement}\n{session.ministry_domain}\n{session.additional_prompt or ''}"
            )
            print(f"[DOMAIN] Session {session_id} classified as '{session.problem_domain}'.")
            await SessionStorage.save_session(session)

        arbiter_config = next(
            (m for m in session.models if m.id == session.arbiter_model_id or m.is_arbiter),
            (session.models[0] if session.models else ModelConfig(id="arbiter", name="Supreme Arbiter", base_url="", api_key="", model_id=""))
        )

        session.status = "running"
        await SessionStorage.save_session(session)
        await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "running"})

        # Map existing rounds to determine next step in pipeline (including research blocks)
        pipeline_index = 0
        if session.rounds:
            completed_pass_ids = {
                r.pass_or_round_id
                for r in session.rounds
                if r.completed_at and r.workspace_phase_number == session.workspace_phase_number
            }
            completed_pass_ids.update({
                item.split(":", 1)[1]
                for item in session.completed_research_steps
                if item.startswith(f"{session.workspace_phase_number}:")
            })
            for idx, step in enumerate(DELIBERATION_PIPELINE):
                # Step is done if its own pass_id is completed or if any subsequent step was completed
                is_step_done = (step["pass_id"] in completed_pass_ids) or any(
                    later_step["pass_id"] in completed_pass_ids
                    for later_step in DELIBERATION_PIPELINE[idx + 1:]
                )
                if not is_step_done:
                    pipeline_index = idx
                    break
            else:
                pipeline_index = len(DELIBERATION_PIPELINE)


        latest_research_dossier: Optional[PooledResearchDossier] = session.latest_research_dossier

        while pipeline_index < len(DELIBERATION_PIPELINE):
            # Check pause event before each step
            await cls._pause_flags[session_id].wait()

            step = DELIBERATION_PIPELINE[pipeline_index]
            phase_index = step["phase_index"]
            phase_title = step["phase_title"]
            pass_id = step["pass_id"]
            pass_title = step["pass_title"]
            is_research = step["is_research"]

            session.current_phase_index = phase_index
            session.current_phase_title = phase_title
            session.current_pass_id = pass_id
            session.current_pass_title = pass_title
            await SessionStorage.save_session(session)

            # --- 1. RESEARCH BLOCK STEP ---
            if is_research:
                await cls.broadcast_event(session_id, "RESEARCH_BLOCK_START", {
                    "phase_index": phase_index,
                    "pass_id": pass_id,
                    "pass_title": pass_title
                })

                # Harvest all AI research calls from prior rounds
                ai_research_calls: List[AutonomousResearchCall] = []
                frictions: List[str] = []
                for r in session.rounds:
                    for resp in r.responses.values():
                        if resp.structured:
                            ai_research_calls.extend(resp.structured.autonomous_research_calls)
                            frictions.extend(resp.structured.negatives_and_risks)

                try:
                    workspace_dir = SessionStorage.get_workspace_dir(session)
                    dossier = await ResearchEngine.conduct_pooled_research(
                        workspace_dir=workspace_dir,
                        phase_index=phase_index,
                        round_num=len(session.rounds) + 1,
                        session_title=session.session_title,
                        problem_statement=session.problem_statement,
                        debater_research_calls=ai_research_calls,
                        previous_friction=frictions[-6:]
                    )
                    latest_research_dossier = dossier
                    session.latest_research_dossier = dossier
                    await SessionStorage.save_session(session)

                    await cls.broadcast_event(session_id, "RESEARCH_DOSSIER_UPDATED", {
                        "phase_index": phase_index,
                        "pass_id": pass_id,
                        "dossier": dossier.model_dump()
                    })
                    research_key = f"{session.workspace_phase_number}:{pass_id}"
                    if research_key not in session.completed_research_steps:
                        session.completed_research_steps.append(research_key)
                    await SessionStorage.save_session(session)
                except Exception as re_err:
                    print(f"Error in research block {pass_id}: {re_err}")
                    session.status = "paused"
                    await SessionStorage.save_session(session)
                    await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "paused"})
                    await cls.broadcast_event(session_id, "ROUND_FAILED", {"message": f"Research block {pass_id} failed: {re_err}"})
                    break

                pipeline_index += 1
                continue

            # --- 2. DEBATER ROUND / PASS STEP ---
            current_round_num = len(session.rounds) + 1
            session.current_round_num = current_round_num
            moderator_injection = cls._pending_injections.pop(session_id, "")

            new_round = RoundData(
                round_number=current_round_num,
                workspace_phase_number=session.workspace_phase_number,
                phase_index=phase_index,
                phase_title=phase_title,
                pass_or_round_id=pass_id,
                pass_or_round_title=pass_title,
                research_dossier=latest_research_dossier,
                moderator_injection=moderator_injection if moderator_injection else None
            )
            session.rounds.append(new_round)
            await SessionStorage.save_session(session)

            await cls.broadcast_event(session_id, "ROUND_START", {
                "round_number": current_round_num,
                "phase_index": phase_index,
                "phase_title": phase_title,
                "pass_id": pass_id,
                "pass_title": pass_title,
                "moderator_injection": moderator_injection
            })

            quarantined = cls._quarantined_models.get(session_id, set())
            active_models = [m for m in session.models if m.enabled and m.id not in quarantined]

            if not active_models:
                session.rounds.pop()
                await cls.broadcast_event(session_id, "ALL_MODELS_UNAVAILABLE", {
                    "message": "All models are currently quarantined or disabled."
                })
                cls._pause_flags[session_id].clear()
                session.status = "paused"
                await SessionStorage.save_session(session)
                await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "paused"})
                break

            effective_problem = session.current_phase_prompt if (session.current_phase_prompt and session.current_phase_prompt.strip()) else session.problem_statement

            model_tasks: Dict[str, asyncio.Task] = {}
            for m in active_models:
                sys_prompt = build_system_prompt_for_debater(
                    m.name, session.ministry_domain, problem_domain=session.problem_domain
                )

                # Build specific prompt according to phase
                if phase_index == 1:
                    my_prior_passes: Dict[str, str] = {}
                    for r in session.rounds[:-1]:
                        if r.workspace_phase_number == session.workspace_phase_number and r.phase_index == 1 and m.id in r.responses:
                            my_prior_passes[r.pass_or_round_id] = r.responses[m.id].structured.refined_solution or r.responses[m.id].raw_text
                    usr_prompt = build_phase_1_pass_prompt(
                        pass_id=pass_id,
                        problem_statement=effective_problem,
                        ministry_domain=session.ministry_domain,
                        my_prior_passes=my_prior_passes,
                        prior_phases=session.phases,
                        problem_domain=session.problem_domain
                    )
                    contract_tail = get_phase_1_schema_guide(pass_id, session.problem_domain)
                elif phase_index == 2:
                    usr_prompt = build_phase_2_round_prompt(
                        round_id=pass_id,
                        round_number=current_round_num,
                        problem_statement=effective_problem,
                        my_model_config=m,
                        all_models=session.models,
                        previous_rounds=[r for r in session.rounds[:-1] if r.workspace_phase_number == session.workspace_phase_number],
                        moderator_injection=moderator_injection,
                        problem_domain=session.problem_domain
                    )
                    contract_tail = build_schema_guide(session.problem_domain)
                elif phase_index == 3:
                    usr_prompt = build_phase_3_round_prompt(
                        round_id=pass_id,
                        round_number=current_round_num,
                        problem_statement=effective_problem,
                        my_model_config=m,
                        all_models=session.models,
                        previous_rounds=[r for r in session.rounds[:-1] if r.workspace_phase_number == session.workspace_phase_number],
                        moderator_injection=moderator_injection,
                        problem_domain=session.problem_domain
                    )
                    contract_tail = build_schema_guide(session.problem_domain)
                else: # Phase 4
                    usr_prompt = build_phase_4_round_prompt(
                        round_id=pass_id,
                        round_number=current_round_num,
                        problem_statement=effective_problem,
                        my_model_config=m,
                        all_models=session.models,
                        previous_rounds=[r for r in session.rounds[:-1] if r.workspace_phase_number == session.workspace_phase_number],
                        moderator_injection=moderator_injection,
                        problem_domain=session.problem_domain
                    )
                    contract_tail = build_schema_guide(session.problem_domain)

                if latest_research_dossier and latest_research_dossier.dossier_text:
                    usr_prompt = f"{usr_prompt}\n\n{latest_research_dossier.dossier_text}"

                # P5: the output contract lives at the TAIL of every prompt, so a blind
                # `usr_prompt[:30000]` deleted it - the model then answered in free prose and
                # the entire turn failed to parse. Truncate the evidence body from the middle
                # and re-append the contract so it always survives and always occupies the
                # recency-privileged final position.
                usr_prompt = cls._fit_debater_prompt(usr_prompt, contract_tail, DEBATER_PROMPT_LIMIT)

                messages = [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": usr_prompt}
                ]

                task = asyncio.create_task(
                    cls._execute_single_model_turn(
                        session_id=session_id,
                        model_config=m,
                        phase_index=phase_index,
                        pass_id=pass_id,
                        pass_title=pass_title,
                        round_number=current_round_num,
                        messages=messages
                    )
                )
                model_tasks[m.id] = task

            cls._running_round_tasks[session_id] = model_tasks

            # ==============================================================
            # AUTONOMOUS ARBITER ROUND SUPERVISOR LOOP (NEVER STALLS)
            # ==============================================================
            round_start_time = time.time()
            results: List[DebaterResponse] = []
            last_heartbeat_save = time.time()
            aborted_models: Set[str] = set()
            
            while True:
                # 1. Check for pause condition
                if not cls._pause_flags[session_id].is_set():
                    await cls._pause_flags[session_id].wait()

                # 2. Check if all tasks finished
                all_done = all(t.done() for t in model_tasks.values())
                if all_done:
                    break

                elapsed_round = time.time() - round_start_time
                done_tasks = [t for t in model_tasks.values() if t.done()]
                done_count = len(done_tasks)
                total_count = len(model_tasks)

                # 3. Heartbeat save every 30s so mid-stream progress survives crashes
                now = time.time()
                if now - last_heartbeat_save >= 30.0:
                    try:
                        await SessionStorage.save_session(session)
                    except Exception:
                        pass
                    last_heartbeat_save = now

                # 4. Super-Arbiter Auto-Abort Lagging Models Check (after 10 minutes / 600s if majority completed)
                # If >=50% (and >=1 for small fleets) completed and elapsed > 600.0s:
                min_done = 1 if total_count <= 2 else max(2, int(total_count * 0.5))
                if done_count >= min_done and elapsed_round > 600.0:
                    for m_id, task in list(model_tasks.items()):
                        if not task.done() and m_id not in aborted_models:
                            aborted_models.add(m_id)
                            task.cancel()
                            if session_id not in cls._quarantined_models:
                                cls._quarantined_models[session_id] = set()
                            cls._quarantined_models[session_id].add(m_id)
                            
                            m_obj = next((x for x in session.models if x.id == m_id), None)
                            m_name = m_obj.name if m_obj else m_id
                            
                            print(f"[ARBITER AUTO-ABORT] Master Arbiter '{arbiter_config.name}' aborted lagging model '{m_name}' after {elapsed_round:.1f}s.")
                            await cls.broadcast_event(session_id, "ARBITER_SUPERVISOR_ACTION", {
                                "arbiter_model": arbiter_config.name,
                                "action": "auto_abort_lagging_model",
                                "target_model_id": m_id,
                                "target_model_name": m_name,
                                "reason": f"Model exceeded 600s (10 min) response threshold while {done_count}/{total_count} fleet debaters completed.",
                                "message": f"👑 Master Arbiter {arbiter_config.name}: Aborted lagging model '{m_name}' after 10-minute timeout."
                            })

                await asyncio.sleep(2.0)


            # Harvest results from tasks
            for m_id, task in model_tasks.items():
                m_obj = next((x for x in session.models if x.id == m_id), None)
                m_name = m_obj.name if m_obj else m_id
                if task.cancelled():
                    resp = DebaterResponse(
                        model_id=m_id,
                        model_name=m_name,
                        phase_index=phase_index,
                        pass_or_round_id=pass_id,
                        pass_or_round_title=pass_title,
                        round_number=current_round_num,
                        raw_text="",
                        structured=StructuredDebateTurn(refined_solution=f"Aborted by Master Arbiter {arbiter_config.name} (latency protection)."),
                        status="timeout",
                        error_message=f"Aborted by Master Arbiter {arbiter_config.name}."
                    )
                    results.append(resp)
                elif task.exception():
                    resp = DebaterResponse(
                        model_id=m_id,
                        model_name=m_name,
                        phase_index=phase_index,
                        pass_or_round_id=pass_id,
                        pass_or_round_title=pass_title,
                        round_number=current_round_num,
                        raw_text="",
                        structured=StructuredDebateTurn(refined_solution=f"Error: {task.exception()}"),
                        status="error",
                        error_message=str(task.exception())
                    )
                    results.append(resp)
                else:
                    resp = task.result()
                    # Apply Auto-Healing if response was raw/unstructured. Checks all four
                    # lenses so a legitimately single-lens Phase-1 pass is not re-parsed.
                    _st = resp.structured
                    if resp.raw_text and not (
                        _st.architect_lens or _st.critic_lens
                        or _st.field_hardware_lens or _st.security_compliance_lens
                    ):
                        resp.structured = heal_unstructured_turn(resp.raw_text, resp.model_name, session.ministry_domain)
                    results.append(resp)

            for resp in results:
                new_round.responses[resp.model_id] = resp

            completed_responses = [r for r in results if r.status == "completed"]
            if not completed_responses:
                session.rounds.pop()
                cls._pause_flags[session_id].clear()
                session.status = "paused"
                await SessionStorage.save_session(session)
                await cls.broadcast_event(session_id, "ROUND_FAILED", {
                    "round_number": current_round_num,
                    "message": "All models failed or timed out in this round."
                })
                await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "paused"})
                break

            new_round.completed_at = time.time()
            strikes = cls._quarantine_strikes.setdefault(session_id, {})
            for response in results:
                if response.status == "completed":
                    strikes.pop(response.model_id, None)
                else:
                    strikes[response.model_id] = strikes.get(response.model_id, 0) + 1
                    if strikes[response.model_id] >= 2:
                        cls._quarantined_models.setdefault(session_id, set()).add(response.model_id)
                    elif response.model_id in aborted_models:
                        cls._quarantined_models.get(session_id, set()).discard(response.model_id)
            await SessionStorage.save_session(session)


            # Arbiter evaluation for every completed pass.
            if completed_responses:
                await cls.broadcast_event(session_id, "ARBITER_EVALUATING", {"round_number": current_round_num})
                
                arbiter_eval = await evaluate_round_consensus(
                    session=session,
                    arbiter_config=arbiter_config,
                    round_number=current_round_num,
                    phase_index=phase_index,
                    phase_title=phase_title,
                    phase_prompt=session.current_phase_prompt
                )
                new_round.arbiter_eval = arbiter_eval
                await SessionStorage.save_session(session)

                await cls.broadcast_event(session_id, "ARBITER_EVAL_COMPLETE", {
                    "round_number": current_round_num,
                    "arbiter_eval": arbiter_eval.model_dump()
                })

            pipeline_index += 1

            if not auto_advance:
                cls._pause_flags[session_id].clear()
                session.status = "paused"
                await SessionStorage.save_session(session)
                await cls.broadcast_event(session_id, "DEBATE_PAUSED_AWAITING_USER", {
                    "round_number": current_round_num,
                    "pass_id": pass_id
                })
                await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "paused"})
                break

            await asyncio.sleep(2)

        # If completed all pipeline steps, synthesize Sovereign Deliverable
        if pipeline_index >= len(DELIBERATION_PIPELINE):
            await cls.broadcast_event(session_id, "GENERATING_FINAL_VERDICT", {})
            
            final_md = await generate_final_markdown_report(
                session=session,
                arbiter_config=arbiter_config,
                phase_title=session.workspace_phase_title or session.session_title,
                phase_prompt=session.current_phase_prompt
            )
            
            phase_slug = sanitize_folder_name(session.workspace_phase_title or f"Phase_{session.workspace_phase_number}")
            filename = f"phase_{session.workspace_phase_number}_{phase_slug}.md"
            phase_obj = WorkspacePhase(
                phase_index=session.workspace_phase_number,
                prompt=session.current_phase_prompt or session.problem_statement,
                phase_title=session.workspace_phase_title or "Sovereign SIH Master Consensus Deliverable",
                verdict_filename=filename,
                verdict_markdown=final_md
            )
            session.phases.append(phase_obj)
            session.final_markdown_report = final_md
            session.status = "completed"
            await SessionStorage.save_session(session)

            await cls.broadcast_event(session_id, "DEBATE_COMPLETED", {
                "final_markdown_report": final_md,
                "total_rounds": len(session.rounds),
                "phase_index": session.workspace_phase_number,
                "phase_title": phase_obj.phase_title,
                "filename": filename,
                "workspace_folder": session.workspace_folder
            })

    @classmethod
    async def pause_debate(cls, session_id: str):
        if session_id in cls._pause_flags:
            cls._pause_flags[session_id].clear()
        await cls._cancel_active_tasks(session_id)
        session = await SessionStorage.get_session(session_id)
        if session:
            if session.rounds and not session.rounds[-1].completed_at:
                session.rounds.pop()
            session.status = "paused"
            await SessionStorage.save_session(session)
            await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "paused"})

    @classmethod
    async def resume_debate(cls, session_id: str, auto_advance: bool = True):
        async with cls.control_lock(session_id):
            await cls.ensure_stopped(session_id)
            session = await SessionStorage.get_session(session_id)
            if not session:
                return
            if session.status == "completed":
                raise ValueError("Completed sessions require a follow-up phase")

            if session_id not in cls._pause_flags:
                cls._pause_flags[session_id] = asyncio.Event()
            cls._pause_flags[session_id].set()

            session.status = "running"
            await SessionStorage.save_session(session)
            await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "running"})
            cls.start_session(session_id, auto_advance=auto_advance)

    @classmethod
    async def start_followup(cls, session_id: str, prompt: str, title: str, auto_advance: bool) -> DebateSession:
        async with cls.control_lock(session_id):
            await cls.ensure_stopped(session_id)
            session = await SessionStorage.get_session(session_id)
            if not session:
                raise ValueError("Debate session not found")
            if session.status not in {"paused", "completed"}:
                raise ValueError("Only paused or completed sessions can start a follow-up")
            session.workspace_phase_number += 1
            session.workspace_phase_title = title
            session.current_phase_index = 1
            session.current_phase_title = "Phase 1: Multi-Persona Genesis"
            session.current_pass_id = "1.1"
            session.current_pass_title = "Pass 1.1: Lead Architect Genesis"
            session.current_phase_prompt = prompt
            session.final_markdown_report = None
            session.latest_research_dossier = None
            session.status = "running"
            await SessionStorage.save_session(session)
            await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "running"})
            cls.start_session(session_id, auto_advance=auto_advance)
            return session

    @classmethod
    async def force_call_verdict(cls, session_id: str):
        session = await SessionStorage.get_session(session_id)
        if not session:
            return

        if session_id in cls._pause_flags:
            cls._pause_flags[session_id].clear()

        await cls._cancel_active_tasks(session_id)
        if session.rounds and not session.rounds[-1].completed_at:
            session.rounds.pop()

        arbiter_config = next((m for m in session.models if m.id == session.arbiter_model_id or m.is_arbiter), (session.models[0] if session.models else ModelConfig(id="arbiter", name="Supreme Arbiter", base_url="", api_key="", model_id="")))
        phase_title = "Sovereign SIH Master Consensus Deliverable"
        
        await cls.broadcast_event(session_id, "GENERATING_FINAL_VERDICT", {"forced_by_user": True})
        final_md = await generate_final_markdown_report(
            session=session,
            arbiter_config=arbiter_config,
            phase_title=phase_title,
            phase_prompt=session.current_phase_prompt
        )
        
        filename = f"LATEST_CONSENSUS_VERDICT.md"
        phase_obj = WorkspacePhase(
            phase_index=session.workspace_phase_number,
            prompt=session.current_phase_prompt,
            phase_title=phase_title,
            verdict_filename=filename,
            verdict_markdown=final_md
        )
        session.phases.append(phase_obj)
        session.final_markdown_report = final_md
        session.status = "completed"
        await SessionStorage.save_session(session)

        await cls.broadcast_event(session_id, "DEBATE_COMPLETED", {
            "final_markdown_report": final_md,
            "total_rounds": len(session.rounds),
            "forced_by_user": True,
            "filename": filename,
            "workspace_folder": session.workspace_folder
        })

    @classmethod
    async def inject_moderator_prompt(cls, session_id: str, text: str):
        cls._pending_injections[session_id] = text
        await cls.broadcast_event(session_id, "MODERATOR_INJECTION_QUEUED", {"text": text})

    @classmethod
    async def update_and_retry_model(cls, session_id: str, updated_config: ModelConfig):
        await cls.ensure_stopped(session_id)
        session = await SessionStorage.get_session(session_id)
        if not session:
            raise ValueError("Debate session not found")

        existing = next((model for model in session.models if model.id == updated_config.id), None)
        if not existing:
            raise ValueError(f"Unknown model ID: {updated_config.id}")
        if not updated_config.api_key:
            updated_config = updated_config.model_copy(update={
                "api_key": existing.api_key,
                "backup_api_keys": updated_config.backup_api_keys or existing.backup_api_keys,
            })
        for i, m in enumerate(session.models):
            if m.id == updated_config.id:
                session.models[i] = updated_config
                break

        if session_id in cls._quarantined_models and updated_config.id in cls._quarantined_models[session_id]:
            cls._quarantined_models[session_id].remove(updated_config.id)

        await SessionStorage.save_session(session)
        await cls.broadcast_event(session_id, "MODEL_UPDATED_UNQUARANTINED", {
            "model_id": updated_config.id,
            "model_name": updated_config.name
        })
        if session.rounds and session.rounds[-1].pass_or_round_id == session.current_pass_id:
            session.rounds.pop()
        session.status = "paused"
        await SessionStorage.save_session(session)
        await cls.resume_debate(session_id, auto_advance=True)

    @classmethod
    async def drop_model(cls, session_id: str, model_id: str, reason: str = "Excluded by user/moderator"):
        session = await SessionStorage.get_session(session_id)
        if not session:
            return
        for m in session.models:
            if m.id == model_id:
                m.enabled = False
                break
        if session_id in cls._quarantined_models and model_id in cls._quarantined_models[session_id]:
            cls._quarantined_models[session_id].remove(model_id)
        
        # Immediately cancel any active asyncio task for this model
        if session_id in cls._running_round_tasks and model_id in cls._running_round_tasks[session_id]:
            task = cls._running_round_tasks[session_id][model_id]
            if not task.done():
                task.cancel()
                print(f"[CANCELLED TASK] Terminated background task for dropped model '{model_id}'")

        await SessionStorage.save_session(session)
        await cls.broadcast_event(session_id, "MODEL_DROPPED", {
            "model_id": model_id,
            "reason": reason
        })

    @classmethod
    async def enable_model(cls, session_id: str, model_id: str):
        session = await SessionStorage.get_session(session_id)
        if not session:
            raise ValueError("Debate session not found")
        model = next((item for item in session.models if item.id == model_id), None)
        if not model:
            raise ValueError(f"Unknown model ID: {model_id}")
        model.enabled = True
        cls._quarantined_models.get(session_id, set()).discard(model_id)
        cls._quarantine_strikes.get(session_id, {}).pop(model_id, None)
        await SessionStorage.save_session(session)
        await cls.broadcast_event(session_id, "MODEL_ENABLED", {"model_id": model_id})

    @classmethod
    async def stop_and_delete(cls, session_id: str) -> bool:
        await cls._cancel_active_tasks(session_id)
        cls._running_tasks.pop(session_id, None)
        await cls.broadcast_event(session_id, "SESSION_DELETED", {"session_id": session_id})
        cls.cleanup_session(session_id, remove_subscribers=True)
        return await SessionStorage.delete_session(session_id)

    @classmethod
    async def execute_arbiter_command(cls, session_id: str, command_text: str) -> dict:
        """
        Deterministic moderator command interpreter.

        P19: this is pure keyword matching over the live session - no LLM is consulted at any
        point - yet every reply used to be signed "Master Arbiter (<model name>)", which made a
        regex look like the judge model reasoning about the fleet. It is now labelled as the
        engine it is. The arbiter model's name is still reported separately as the model the
        actions apply to.
        """
        session = await SessionStorage.get_session(session_id)
        if not session:
            return {"status": "error", "message": "Debate session not found."}

        arbiter_config = next((m for m in session.models if m.id == session.arbiter_model_id or m.is_arbiter), (session.models[0] if session.models else ModelConfig(id="arbiter", name="Supreme Arbiter", base_url="", api_key="", model_id="")))
        cmd_lower = command_text.lower()
        actions_taken = []
        explanation_parts = []

        is_abort_cmd = bool(re.search(r"\b(abort|kill|cancel\s+tasks?|stop\s+turns?|stuck|hang)\b", cmd_lower))
        is_enable_cmd = bool(re.search(r"\b(turn\s+on|enable|re-?enable|retry|bring\s+back|restore|include|reinstate|unquarantine)\b", cmd_lower))
        # P19: "retry the dropped model" matched BOTH patterns and disable was evaluated first,
        # so the command did the exact opposite of what it said. Enable now wins the tie,
        # because a restore instruction is never a request to remove.
        is_disable_cmd = (not is_enable_cmd) and bool(
            re.search(r"\b(turn\s+off|disable|exclude|drop|remove|eject|kick)\b", cmd_lower)
        )
        is_verdict_cmd = bool(re.search(r"\b(force\s+verdict|call\s+verdict|finalize\s+verdict|synthesize\s+now|generate\s+final\s+verdict|finish\s+debate|end\s+debate)\b", cmd_lower))
        is_heal_cmd = bool(re.search(r"\b(heal|format|convert|repair|fix\s+format)\b", cmd_lower))

        # 1. Action: Abort/Kill Lagging Models
        if is_abort_cmd:
            if session_id in cls._running_round_tasks:
                for m_id, task in list(cls._running_round_tasks[session_id].items()):
                    if not task.done():
                        task.cancel()
                        m_obj = next((x for x in session.models if x.id == m_id), None)
                        m_name = m_obj.name if m_obj else m_id
                        actions_taken.append(f"Aborted running turn for '{m_name}' ({m_id})")
                        if session_id not in cls._quarantined_models:
                            cls._quarantined_models[session_id] = set()
                        cls._quarantined_models[session_id].add(m_id)
                explanation_parts.append("Terminated the lagging background worker tasks and quarantined the unresponsive models.")

        # 2. Action: Exclude / Turn Off or Enable Specific Model
        for m in session.models:
            if m.name.lower() in cmd_lower or m.id.lower() in cmd_lower:
                if is_enable_cmd:
                    m.enabled = True
                    if session_id in cls._quarantined_models and m.id in cls._quarantined_models[session_id]:
                        cls._quarantined_models[session_id].remove(m.id)
                    cls._quarantine_strikes.get(session_id, {}).pop(m.id, None)
                    await SessionStorage.save_session(session)
                    actions_taken.append(f"Re-enabled and unquarantined '{m.name}' ({m.id})")
                elif is_disable_cmd:
                    await cls.drop_model(session_id, m.id, reason="Excluded by moderator command")
                    actions_taken.append(f"Excluded '{m.name}' ({m.id}) from future debate rounds")

        # 3. Action: Force Advance / Call Verdict
        if is_verdict_cmd:
            await cls.force_call_verdict(session_id)
            actions_taken.append("Synthesized Final Sovereign Consensus Verdict immediately")
            explanation_parts.append("Summoned the arbiter and synthesized the final sovereign markdown deliverable.")

        # 4. Action: Auto-Heal Unstructured Outputs
        if is_heal_cmd:
            if session.rounds:
                healed_count = 0
                for resp in session.rounds[-1].responses.values():
                    _st = resp.structured
                    if resp.raw_text and not (
                        _st.architect_lens or _st.critic_lens
                        or _st.field_hardware_lens or _st.security_compliance_lens
                    ):
                        resp.structured = heal_unstructured_turn(resp.raw_text, resp.model_name, session.ministry_domain)
                        healed_count += 1
                await SessionStorage.save_session(session)
                actions_taken.append(f"Recovered {healed_count} unstructured debater response(s) into the schema")
                explanation_parts.append(
                    f"Recovered content from {healed_count} unformatted turn(s). Note: recovery restores text only - "
                    "a consensus vote that was never stated stays unset and is excluded from the score rather than guessed."
                )

        # 5. Build Final Response
        engine_label = "⚙️ **System Moderator Engine** (direct execution - no model was queried)"
        if not actions_taken:
            explanation = (
                f"{engine_label}\n\nDirective received: *\"{command_text}\"* - no matching action pattern, so nothing was changed.\n\n"
                f"Recognised commands: abort stuck turns, enable/re-enable <model>, disable/drop <model>, "
                f"heal unformatted responses, force the final verdict.\n\n"
                f"Current arbiter model for this session: **{arbiter_config.name}**."
            )
        else:
            explanation = (
                f"{engine_label}\n\n" + "\n".join([f"- ✅ {a}" for a in actions_taken])
                + ("\n\n" + " ".join(explanation_parts) if explanation_parts else "")
            )

        await cls.broadcast_event(session_id, "ARBITER_SUPERVISOR_ACTION", {
            "arbiter_model": arbiter_config.name,
            "command": command_text,
            "actions_taken": actions_taken,
            "message": explanation
        })

        return {
            "status": "success",
            "arbiter_model": arbiter_config.name,
            "response": explanation,
            "actions_taken": actions_taken,
            "session_status": session.status
        }
