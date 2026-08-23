import asyncio
import time
import json
from typing import Dict, List, Optional, Set
from app.schemas import (
    DebateSession,
    RoundData,
    DebaterResponse,
    StructuredDebateTurn,
    ModelConfig,
    ArbiterEvaluation,
    WorkspacePhase
)
from app.providers.universal_client import (
    UniversalAIClient,
    parse_structured_turn
)
from app.engine.prompts import (
    build_system_prompt_for_debater,
    build_round_1_prompt,
    build_round_n_prompt
)
from app.engine.consensus_eval import (
    evaluate_round_consensus,
    generate_final_markdown_report
)
from app.storage import SessionStorage, UserConfigStorage, sanitize_folder_name
from app.providers.research_engine import ResearchEngine

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
        round_number: int,
        messages: list
    ) -> DebaterResponse:
        start_time = time.time()
        accumulated_text = ""
        
        await cls.broadcast_event(session_id, "MODEL_STREAM_START", {
            "model_id": model_config.id,
            "model_name": model_config.name,
            "round_number": round_number
        })

        async def _on_key_promoted(cfg: ModelConfig, working_key: str):
            # 1. Save updated promoted key in session
            session = await SessionStorage.get_session(session_id)
            if session:
                for m in session.models:
                    if m.id == cfg.id:
                        m.api_key = working_key
                        break
                await SessionStorage.save_session(session)

            # 2. Save permanently in global user configuration
            try:
                user_models = await UserConfigStorage.get_user_config()
                for m in user_models:
                    if m.id == cfg.id or m.name == cfg.name:
                        m.api_key = working_key
                        break
                await UserConfigStorage.save_user_config(user_models)
            except Exception as err:
                print(f"Error persisting promoted key to user config: {err}")

            await cls.broadcast_event(session_id, "BACKUP_KEY_PROMOTED", {
                "model_id": cfg.id,
                "model_name": cfg.name,
                "promoted_key_masked": working_key[:6] + "..." + working_key[-4:] if len(working_key) > 10 else "***"
            })

        try:
            total_timeout = float(model_config.timeout_seconds or 600)
            FIRST_TOKEN_TIMEOUT = 120.0  # 2 minutes first-token guard

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
                            "round_number": round_number
                        })

                collector_task = asyncio.create_task(_stream_collector(attempt))

                if attempt == 1:
                    # Wait up to 2 mins for first token
                    try:
                        await asyncio.wait_for(first_token_event.wait(), timeout=FIRST_TOKEN_TIMEOUT)
                        # First token received! Now wait for remainder of total_timeout to finish
                        remaining = max(10.0, total_timeout - (time.time() - start_time))
                        await asyncio.wait_for(collector_task, timeout=remaining)
                        break  # Completed successfully on Attempt 1
                    except asyncio.TimeoutError:
                        collector_task.cancel()
                        if not first_token_event.is_set():
                            # Check if a backup key is present to rotate for Attempt 2
                            rotated_key_msg = ""
                            if model_config.backup_api_keys and len(model_config.backup_api_keys) > 0:
                                old_key = model_config.api_key
                                new_key = model_config.backup_api_keys.pop(0)
                                model_config.backup_api_keys.append(old_key)
                                model_config.api_key = new_key
                                await _on_key_promoted(model_config, new_key)
                                rotated_key_msg = f" (switched to backup key {new_key[:6]}...)"

                            print(f"[AUTO-RETRY] Model '{model_config.name}' sent 0 words in 2 mins. Resending request for Attempt 2{rotated_key_msg}...")
                            await cls.broadcast_event(session_id, "MODEL_RETRY_ATTEMPT", {
                                "model_id": model_config.id,
                                "model_name": model_config.name,
                                "round_number": round_number,
                                "attempt": 2,
                                "message": f"No response in 2 mins. Auto-retrying on Attempt 2{rotated_key_msg}..."
                            })
                            continue
                        else:
                            raise asyncio.TimeoutError()
                else:
                    # Attempt 2: wait with remaining timeout
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
                "round_number": round_number,
                "status": "completed",
                "structured": structured.model_dump(),
                "elapsed_seconds": elapsed
            })
            return resp

        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            err_msg = f"Model '{model_config.name}' exceeded 10-minute timeout ({model_config.timeout_seconds}s)."
            
            if session_id not in cls._quarantined_models:
                cls._quarantined_models[session_id] = set()
            cls._quarantined_models[session_id].add(model_config.id)

            resp = DebaterResponse(
                model_id=model_config.id,
                model_name=model_config.name,
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
            err_msg = f"All candidate API keys failed for Model '{model_config.name}': {str(e)}"
            
            if session_id not in cls._quarantined_models:
                cls._quarantined_models[session_id] = set()
            cls._quarantined_models[session_id].add(model_config.id)

            resp = DebaterResponse(
                model_id=model_config.id,
                model_name=model_config.name,
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

        arbiter_config = next((m for m in session.models if m.id == session.arbiter_model_id or m.is_arbiter), None)
        if not arbiter_config:
            arbiter_config = session.models[0]

        session.status = "running"
        await SessionStorage.save_session(session)
        await cls.broadcast_event(session_id, "DEBATE_STATUS_CHANGE", {"status": "running"})

        phase_title = session.phases[-1].phase_title if session.phases and session.status == "running" else f"Phase {session.current_phase_index}"
        phase_prompt = session.current_phase_prompt

        while True:
            await cls._pause_flags[session_id].wait()

            # Check if there is an existing incomplete round from a previous run
            if session.rounds and not session.rounds[-1].completed_at:
                new_round = session.rounds[-1]
                current_round_num = new_round.round_number
                moderator_injection = new_round.moderator_injection or cls._pending_injections.pop(session_id, "")
                new_round.moderator_injection = moderator_injection if moderator_injection else None
            else:
                current_round_num = len(session.rounds) + 1
                session.current_round_num = current_round_num
                moderator_injection = cls._pending_injections.pop(session_id, "")
                new_round = RoundData(
                    round_number=current_round_num,
                    phase_index=session.current_phase_index,
                    phase_title=phase_title,
                    moderator_injection=moderator_injection if moderator_injection else None
                )
                session.rounds.append(new_round)

            await SessionStorage.save_session(session)

            await cls.broadcast_event(session_id, "ROUND_START", {
                "round_number": current_round_num,
                "phase_index": session.current_phase_index,
                "phase_title": phase_title,
                "moderator_injection": moderator_injection
            })

            quarantined = cls._quarantined_models.get(session_id, set())
            active_models = [m for m in session.models if m.enabled and m.id not in quarantined]

            if not active_models:
                await cls.broadcast_event(session_id, "ALL_MODELS_UNAVAILABLE", {
                    "message": "All models are currently quarantined or disabled. Please update settings/keys to continue."
                })
                cls._pause_flags[session_id].clear()
                session.status = "paused"
                await SessionStorage.save_session(session)
                break

            # EVERY ROUND: Execute targeted multi-engine research (Tavily + OpenAlex + arXiv)
            # Harvest specific technical topics, limits, and questions demanded by the debaters
            ai_demanded_topics = []
            previous_frictions = []
            if len(session.rounds) > 1:
                last_round = session.rounds[-2]
                for r in last_round.responses.values():
                    if r.structured:
                        if r.structured.research_queries_for_next_round:
                            ai_demanded_topics.extend(r.structured.research_queries_for_next_round)
                        if r.structured.negatives_and_risks:
                            previous_frictions.extend(r.structured.negatives_and_risks)

            try:
                research_data = await ResearchEngine.conduct_round_research(
                    round_num=current_round_num,
                    session_title=session.session_title,
                    problem_statement=session.problem_statement,
                    additional_prompt=session.additional_prompt or "",
                    previous_friction=previous_frictions[:4],
                    ai_requested_queries=ai_demanded_topics[:6]
                )
                await cls.broadcast_event(session_id, "RESEARCH_DOSSIER_UPDATED", {
                    "round_number": current_round_num,
                    "web_summary": research_data.get("web_summary", ""),
                    "sources": research_data.get("sources", []),
                    "total_sources": research_data.get("total_sources", 0)
                })
            except Exception as re_err:
                print(f"Research pass error in round {current_round_num}: {re_err}")
                research_data = {"dossier_text": "", "sources": [], "total_sources": 0}

            tasks = []
            for m in active_models:
                sys_prompt = build_system_prompt_for_debater(m.name, session.ministry_domain)
                # If this is round 1 of the session or round 1 of a new phase
                is_phase_start_round = (len(session.rounds) == 1) or (len(session.rounds) > 1 and session.rounds[-2].phase_index != session.current_phase_index)

                if is_phase_start_round:
                    usr_prompt = build_round_1_prompt(
                        problem_statement=session.problem_statement,
                        ministry_domain=session.ministry_domain,
                        phase_prompt=phase_prompt,
                        prior_phases=session.phases
                    )
                else:
                    usr_prompt = build_round_n_prompt(
                        round_number=current_round_num,
                        problem_statement=session.problem_statement,
                        my_model_config=m,
                        all_models=session.models,
                        previous_rounds=session.rounds[:-1],
                        moderator_injection=moderator_injection,
                        phase_prompt=phase_prompt
                    )

                # Inject the live round's research dossier into the prompt
                if research_data.get("dossier_text"):
                    usr_prompt = f"{usr_prompt}\n\n{research_data['dossier_text']}"

                messages = [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": usr_prompt}
                ]

                task = asyncio.create_task(
                    cls._execute_single_model_turn(session_id, m, current_round_num, messages)
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
                    "message": "All models failed or timed out. Please check API keys."
                })
                break

            await cls.broadcast_event(session_id, "ARBITER_EVALUATING", {"round_number": current_round_num})
            
            arbiter_eval = await evaluate_round_consensus(
                session=session,
                arbiter_config=arbiter_config,
                round_number=current_round_num,
                phase_prompt=phase_prompt
            )
            new_round.arbiter_eval = arbiter_eval
            await SessionStorage.save_session(session)

            await cls.broadcast_event(session_id, "ARBITER_EVAL_COMPLETE", {
                "round_number": current_round_num,
                "arbiter_eval": arbiter_eval.model_dump()
            })

            # Check if unanimous consensus reached for this phase
            if arbiter_eval.is_unanimous:
                await cls.broadcast_event(session_id, "GENERATING_FINAL_VERDICT", {})
                final_md = await generate_final_markdown_report(
                    session=session,
                    arbiter_config=arbiter_config,
                    phase_title=phase_title,
                    phase_prompt=phase_prompt
                )
                
                # Save into workspace phases
                filename = f"phase_{session.current_phase_index}_{sanitize_folder_name(phase_title)}.md"
                phase_obj = WorkspacePhase(
                    phase_index=session.current_phase_index,
                    prompt=phase_prompt,
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
                    "total_rounds": current_round_num,
                    "phase_index": session.current_phase_index,
                    "phase_title": phase_title,
                    "filename": filename,
                    "workspace_folder": session.workspace_folder
                })
                break

            if not auto_advance:
                cls._pause_flags[session_id].clear()
                session.status = "paused"
                await SessionStorage.save_session(session)
                await cls.broadcast_event(session_id, "DEBATE_PAUSED_AWAITING_USER", {
                    "round_number": current_round_num
                })
                break

            await asyncio.sleep(2)

    @classmethod
    async def start_followup_phase(cls, session_id: str, followup_prompt: str, phase_title: str, auto_advance: bool = True):
        session = await SessionStorage.get_session(session_id)
        if not session:
            return

        session.current_phase_index += 1
        session.current_phase_prompt = followup_prompt
        session.status = "running"
        await SessionStorage.save_session(session)

        await cls.broadcast_event(session_id, "FOLLOWUP_PHASE_STARTED", {
            "phase_index": session.current_phase_index,
            "phase_title": phase_title,
            "prompt": followup_prompt
        })

        if session_id not in cls._pause_flags:
            cls._pause_flags[session_id] = asyncio.Event()
        cls._pause_flags[session_id].set()

        task = asyncio.create_task(cls.run_round_loop(session_id, auto_advance=auto_advance))
        cls._running_tasks[session_id] = task

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

        arbiter_config = next((m for m in session.models if m.id == session.arbiter_model_id or m.is_arbiter), None)
        if not arbiter_config:
            arbiter_config = session.models[0]

        phase_title = session.phases[-1].phase_title if session.phases and session.status == "running" else f"Phase {session.current_phase_index}"
        
        await cls.broadcast_event(session_id, "GENERATING_FINAL_VERDICT", {"forced_by_user": True})
        final_md = await generate_final_markdown_report(
            session=session,
            arbiter_config=arbiter_config,
            phase_title=phase_title,
            phase_prompt=session.current_phase_prompt
        )
        
        filename = f"phase_{session.current_phase_index}_{sanitize_folder_name(phase_title)}.md"
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
            "total_rounds": session.current_round_num,
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

        if session.rounds:
            current_round = session.rounds[-1]
            sys_prompt = build_system_prompt_for_debater(updated_config.name, session.ministry_domain)
            is_first = (len(session.rounds) == 1)
            
            if is_first:
                usr_prompt = build_round_1_prompt(
                    problem_statement=session.problem_statement,
                    ministry_domain=session.ministry_domain,
                    phase_prompt=session.current_phase_prompt,
                    prior_phases=session.phases
                )
            else:
                usr_prompt = build_round_n_prompt(
                    round_number=current_round.round_number,
                    problem_statement=session.problem_statement,
                    my_model_config=updated_config,
                    all_models=session.models,
                    previous_rounds=session.rounds[:-1],
                    moderator_injection=current_round.moderator_injection or "",
                    phase_prompt=session.current_phase_prompt
                )

            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": usr_prompt}
            ]

            async def _retry_task():
                resp = await cls._execute_single_model_turn(
                    session_id, updated_config, current_round.round_number, messages
                )
                current_round.responses[resp.model_id] = resp
                await SessionStorage.save_session(session)

            asyncio.create_task(_retry_task())

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
