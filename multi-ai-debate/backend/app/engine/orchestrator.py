import asyncio
import time
import json
import os
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
    build_final_markdown_report_prompt
)
from app.engine.consensus_eval import (
    evaluate_round_consensus,
    generate_final_markdown_report
)
from app.storage import SessionStorage, UserConfigStorage, sanitize_folder_name
from app.providers.research_engine import ResearchEngine

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

class DebateOrchestrator:
    _event_queues: Dict[str, Set[asyncio.Queue]] = {}
    _running_tasks: Dict[str, asyncio.Task] = {}
    _quarantined_models: Dict[str, Set[str]] = {}
    _pending_injections: Dict[str, str] = {}
    _pause_flags: Dict[str, asyncio.Event] = {}

    @classmethod
    def get_event_queue(cls, session_id: str) -> asyncio.Queue:
        if session_id not in cls._event_queues:
            cls._event_queues[session_id] = set()
        q = asyncio.Queue()
        cls._event_queues[session_id].add(q)
        return q

    @classmethod
    def remove_event_queue(cls, session_id: str, q: asyncio.Queue):
        if session_id in cls._event_queues and q in cls._event_queues[session_id]:
            cls._event_queues[session_id].remove(q)

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
                await q.put(payload)
            except Exception:
                pass

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
                        break
                await SessionStorage.save_session(session)

            try:
                user_models = await UserConfigStorage.get_user_config()
                for m in user_models:
                    if m.id == cfg.id or m.name == cfg.name:
                        m.api_key = working_key
                        break
                await UserConfigStorage.save_user_config(user_models)
            except Exception as err:
                print(f"Error persisting promoted key: {err}")

            await cls.broadcast_event(session_id, "BACKUP_KEY_PROMOTED", {
                "model_id": cfg.id,
                "model_name": cfg.name,
                "promoted_key_masked": working_key[:6] + "..." + working_key[-4:] if len(working_key) > 10 else "***"
            })

        try:
            total_timeout = float(model_config.timeout_seconds or 600)
            FIRST_TOKEN_TIMEOUT = 120.0

            for attempt in [1, 2]:
                accumulated_text = ""
                first_token_event = asyncio.Event()

                async def _stream_collector(attempt_num: int):
                    nonlocal accumulated_text
                    async for token in UniversalAIClient.stream_chat(
                        config=model_config,
                        messages=messages,
                        temperature=model_config.temperature,
                        on_key_promoted_cb=_on_key_promoted
                    ):
                        if not first_token_event.is_set():
                            first_token_event.set()
                        accumulated_text += token
                        await cls.broadcast_event(session_id, "MODEL_TOKEN_DELTA", {
                            "model_id": model_config.id,
                            "delta": token,
                            "round_number": round_number,
                            "pass_id": pass_id
                        })

                collector_task = asyncio.create_task(_stream_collector(attempt))

                if attempt == 1:
                    try:
                        await asyncio.wait_for(first_token_event.wait(), timeout=FIRST_TOKEN_TIMEOUT)
                        remaining = max(10.0, total_timeout - (time.time() - start_time))
                        await asyncio.wait_for(collector_task, timeout=remaining)
                        break
                    except asyncio.TimeoutError:
                        collector_task.cancel()
                        if not first_token_event.is_set():
                            rotated_key_msg = ""
                            if model_config.backup_api_keys and len(model_config.backup_api_keys) > 0:
                                old_key = model_config.api_key
                                new_key = model_config.backup_api_keys.pop(0)
                                model_config.backup_api_keys.append(old_key)
                                model_config.api_key = new_key
                                await _on_key_promoted(model_config, new_key)
                                rotated_key_msg = f" (switched to backup key {new_key[:6]}...)"

                            print(f"[AUTO-RETRY] Model '{model_config.name}' sent 0 words in 2 mins. Retrying on Attempt 2{rotated_key_msg}...")
                            await cls.broadcast_event(session_id, "MODEL_RETRY_ATTEMPT", {
                                "model_id": model_config.id,
                                "model_name": model_config.name,
                                "round_number": round_number,
                                "attempt": 2,
                                "message": f"Auto-retrying on Attempt 2{rotated_key_msg}..."
                            })
                            continue
                        else:
                            raise asyncio.TimeoutError()
                else:
                    remaining = max(15.0, total_timeout - (time.time() - start_time))
                    await asyncio.wait_for(collector_task, timeout=remaining)
                    break
            
            clean_text = accumulated_text.strip()
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
                elapsed_seconds=elapsed,
                active_key_used=model_config.api_key
            )

            await cls.broadcast_event(session_id, "MODEL_STREAM_END", {
                "model_id": model_config.id,
                "model_name": model_config.name,
                "phase_index": phase_index,
                "pass_id": pass_id,
                "pass_title": pass_title,
                "round_number": round_number,
                "status": "completed",
                "structured": structured.model_dump(),
                "elapsed_seconds": elapsed
            })

            # Atomic turn persistence
            try:
                live_sess = await SessionStorage.get_session(session_id)
                if live_sess and live_sess.rounds and live_sess.rounds[-1].round_number == round_number:
                    live_sess.rounds[-1].responses[resp.model_id] = resp
                    await SessionStorage.save_session(live_sess)
            except Exception:
                pass

            return resp

        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            err_msg = f"Model '{model_config.name}' exceeded timeout ({model_config.timeout_seconds}s)."
            
            if session_id not in cls._quarantined_models:
                cls._quarantined_models[session_id] = set()
            cls._quarantined_models[session_id].add(model_config.id)

            resp = DebaterResponse(
                model_id=model_config.id,
                model_name=model_config.name,
                phase_index=phase_index,
                pass_or_round_id=pass_id,
                pass_or_round_title=pass_title,
                round_number=round_number,
                raw_text="",
                structured=StructuredDebateTurn(refined_solution=err_msg),
                status="timeout",
                elapsed_seconds=elapsed,
                error_message=err_msg
            )

            await cls.broadcast_event(session_id, "MODEL_STREAM_END", {
                "model_id": model_config.id,
                "model_name": model_config.name,
                "phase_index": phase_index,
                "pass_id": pass_id,
                "pass_title": pass_title,
                "round_number": round_number,
                "status": "timeout",
                "error_message": err_msg
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
            
            if session_id not in cls._quarantined_models:
                cls._quarantined_models[session_id] = set()
            cls._quarantined_models[session_id].add(model_config.id)

            resp = DebaterResponse(
                model_id=model_config.id,
                model_name=model_config.name,
                phase_index=phase_index,
                pass_or_round_id=pass_id,
                pass_or_round_title=pass_title,
                round_number=round_number,
                raw_text="",
                structured=StructuredDebateTurn(refined_solution=err_msg),
                status="error",
                elapsed_seconds=elapsed,
                error_message=err_msg
            )

            await cls.broadcast_event(session_id, "MODEL_STREAM_END", {
                "model_id": model_config.id,
                "model_name": model_config.name,
                "phase_index": phase_index,
                "pass_id": pass_id,
                "pass_title": pass_title,
                "round_number": round_number,
                "status": "error",
                "error_message": err_msg
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
        session = await SessionStorage.get_session(session_id)
        if not session:
            return

        if session_id not in cls._pause_flags:
            cls._pause_flags[session_id] = asyncio.Event()
        cls._pause_flags[session_id].set()

        arbiter_config = next((m for m in session.models if m.id == session.arbiter_model_id or m.is_arbiter), session.models[0])

        session.status = "running"
        await SessionStorage.save_session(session)
        await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "running"})

        # Map existing rounds to determine next step in pipeline
        pipeline_index = 0
        if session.rounds:
            completed_pass_ids = [r.pass_or_round_id for r in session.rounds if r.completed_at]
            for idx, step in enumerate(DELIBERATION_PIPELINE):
                if step["pass_id"] not in completed_pass_ids:
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
                except Exception as re_err:
                    print(f"Error in research block {pass_id}: {re_err}")

                pipeline_index += 1
                continue

            # --- 2. DEBATER ROUND / PASS STEP ---
            current_round_num = len(session.rounds) + 1
            session.current_round_num = current_round_num
            moderator_injection = cls._pending_injections.pop(session_id, "")

            new_round = RoundData(
                round_number=current_round_num,
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
                await cls.broadcast_event(session_id, "ALL_MODELS_UNAVAILABLE", {
                    "message": "All models are currently quarantined or disabled."
                })
                cls._pause_flags[session_id].clear()
                session.status = "paused"
                await SessionStorage.save_session(session)
                break

            tasks = []
            for m in active_models:
                sys_prompt = build_system_prompt_for_debater(m.name, session.ministry_domain)
                
                # Build specific prompt according to phase
                if phase_index == 1:
                    # Gather model's own prior passes in Phase 1
                    my_prior_passes: Dict[str, str] = {}
                    for r in session.rounds[:-1]:
                        if r.phase_index == 1 and m.id in r.responses:
                            my_prior_passes[r.pass_or_round_id] = r.responses[m.id].structured.refined_solution or r.responses[m.id].raw_text
                    usr_prompt = build_phase_1_pass_prompt(
                        pass_id=pass_id,
                        problem_statement=session.problem_statement,
                        ministry_domain=session.ministry_domain,
                        my_prior_passes=my_prior_passes,
                        prior_phases=session.phases
                    )
                elif phase_index == 2:
                    usr_prompt = build_phase_2_round_prompt(
                        round_id=pass_id,
                        round_number=current_round_num,
                        problem_statement=session.problem_statement,
                        my_model_config=m,
                        all_models=session.models,
                        previous_rounds=session.rounds[:-1],
                        moderator_injection=moderator_injection
                    )
                elif phase_index == 3:
                    usr_prompt = build_phase_3_round_prompt(
                        round_id=pass_id,
                        round_number=current_round_num,
                        problem_statement=session.problem_statement,
                        my_model_config=m,
                        all_models=session.models,
                        previous_rounds=session.rounds[:-1],
                        moderator_injection=moderator_injection
                    )
                else: # Phase 4
                    usr_prompt = build_phase_4_round_prompt(
                        round_id=pass_id,
                        round_number=current_round_num,
                        problem_statement=session.problem_statement,
                        my_model_config=m,
                        all_models=session.models,
                        previous_rounds=session.rounds[:-1],
                        moderator_injection=moderator_injection
                    )

                # Inject latest pooled research dossier into user prompt if available
                if latest_research_dossier and latest_research_dossier.dossier_text:
                    usr_prompt = f"{usr_prompt}\n\n{latest_research_dossier.dossier_text}"

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
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=False)
            
            for resp in results:
                new_round.responses[resp.model_id] = resp

            new_round.completed_at = time.time()
            await SessionStorage.save_session(session)

            completed_responses = [r for r in results if r.status == "completed"]
            if not completed_responses:
                cls._pause_flags[session_id].clear()
                session.status = "paused"
                await SessionStorage.save_session(session)
                await cls.broadcast_event(session_id, "ROUND_FAILED", {
                    "round_number": current_round_num,
                    "message": "All models failed or timed out in this round."
                })
                break

            # Arbiter evaluation for rounds (Phases 2, 3, 4)
            if phase_index > 1:
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
                break

            await asyncio.sleep(2)

        # If completed all pipeline steps, synthesize Sovereign Deliverable
        if pipeline_index >= len(DELIBERATION_PIPELINE):
            await cls.broadcast_event(session_id, "GENERATING_FINAL_VERDICT", {})
            
            final_md = await generate_final_markdown_report(
                session=session,
                arbiter_config=arbiter_config,
                phase_title=session.session_title,
                phase_prompt=session.current_phase_prompt
            )
            
            phase_slug = sanitize_folder_name(session.current_phase_title or f"Phase_{session.current_phase_index}")
            filename = f"phase_{session.current_phase_index}_{phase_slug}.md"
            phase_obj = WorkspacePhase(
                phase_index=session.current_phase_index,
                prompt=session.current_phase_prompt or session.problem_statement,
                phase_title=session.current_phase_title or "Sovereign SIH Master Consensus Deliverable",
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
                "phase_index": session.current_phase_index,
                "phase_title": phase_obj.phase_title,
                "filename": filename,
                "workspace_folder": session.workspace_folder
            })

    @classmethod
    async def pause_debate(cls, session_id: str):
        if session_id in cls._pause_flags:
            cls._pause_flags[session_id].clear()
        session = await SessionStorage.get_session(session_id)
        if session:
            session.status = "paused"
            await SessionStorage.save_session(session)
            await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "paused"})

    @classmethod
    async def resume_debate(cls, session_id: str, auto_advance: bool = True):
        session = await SessionStorage.get_session(session_id)
        if not session:
            return

        if session_id not in cls._pause_flags:
            cls._pause_flags[session_id] = asyncio.Event()
        cls._pause_flags[session_id].set()

        session.status = "running"
        await SessionStorage.save_session(session)
        await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "running"})

        if session_id not in cls._running_tasks or cls._running_tasks[session_id].done():
            task = asyncio.create_task(cls.run_round_loop(session_id, auto_advance=auto_advance))
            cls._running_tasks[session_id] = task

    @classmethod
    async def force_call_verdict(cls, session_id: str):
        session = await SessionStorage.get_session(session_id)
        if not session:
            return

        if session_id in cls._pause_flags:
            cls._pause_flags[session_id].clear()

        arbiter_config = next((m for m in session.models if m.id == session.arbiter_model_id or m.is_arbiter), session.models[0])
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
            phase_index=session.current_phase_index,
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
        session = await SessionStorage.get_session(session_id)
        if not session:
            return

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

    @classmethod
    async def drop_model(cls, session_id: str, model_id: str):
        session = await SessionStorage.get_session(session_id)
        if not session:
            return
        for m in session.models:
            if m.id == model_id:
                m.enabled = False
                break
        if session_id in cls._quarantined_models and model_id in cls._quarantined_models[session_id]:
            cls._quarantined_models[session_id].remove(model_id)
        await SessionStorage.save_session(session)
        await cls.broadcast_event(session_id, "MODEL_DROPPED", {"model_id": model_id})

