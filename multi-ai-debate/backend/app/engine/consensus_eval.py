import json
import asyncio
from typing import List, Tuple, Optional
from app.schemas import (
    DebateSession,
    RoundData,
    ArbiterEvaluation,
    FrictionPoint,
    ModelConfig
)
from app.engine.prompts import (
    build_arbiter_evaluation_prompt,
    build_final_markdown_report_prompt,
    build_system_prompt_for_debater
)
from app.providers.universal_client import UniversalAIClient, extract_and_repair_json

async def evaluate_round_consensus(
    session: DebateSession,
    arbiter_config: ModelConfig,
    round_number: int,
    phase_prompt: str = ""
) -> ArbiterEvaluation:
    user_prompt = build_arbiter_evaluation_prompt(
        round_number=round_number,
        problem_statement=session.problem_statement,
        rounds=session.rounds,
        phase_prompt=phase_prompt
    )
    system_prompt = build_system_prompt_for_debater(
        model_name="Master Arbiter & Jury",
        ministry_domain=session.ministry_domain
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    full_text = ""
    try:
        async for chunk in UniversalAIClient.stream_chat(
            config=arbiter_config,
            messages=messages,
            temperature=0.3
        ):
            full_text += chunk
    except Exception as e:
        full_text = f'{{"round_number": {round_number}, "consensus_score": 75, "is_unanimous": false, "executive_synthesis": "Arbiter note: Connection warning: {str(e)}", "friction_points": []}}'

    parsed = extract_and_repair_json(full_text)
    
    score = parsed.get("consensus_score", 70)
    try:
        score = int(score)
    except Exception:
        score = 70

    # Pure Democratic Collective Voting Across All 11 Debaters (No single AI is a decider)
    current_round = session.rounds[-1]
    completed_resps = [r for r in current_round.responses.values() if r.status == "completed"]
    if completed_resps:
        debater_scores = [r.structured.agreement_percentage for r in completed_resps]
        agree_votes = [r for r in completed_resps if r.structured.consensus_vote == "AGREE"]
        avg_debater_pct = sum(debater_scores) / len(completed_resps)
        
        # Consensus score is the democratic average across all debaters
        score = int(avg_debater_pct)
        agree_ratio = len(agree_votes) / len(completed_resps)
        if agree_ratio >= 0.80 and avg_debater_pct >= 85:
            is_unanimous = True
        else:
            is_unanimous = False

    friction_list = []
    for fp in parsed.get("friction_points", []):
        if isinstance(fp, dict):
            status = fp.get("status", "OPEN")
            if status not in ["OPEN", "RESOLVED", "CONCEDED"]:
                status = "OPEN"
            friction_list.append(FrictionPoint(
                issue=str(fp.get("issue", "")),
                raised_by=str(fp.get("raised_by", "")),
                challenged_by=str(fp.get("challenged_by", "")),
                status=status,
                resolution_notes=str(fp.get("resolution_notes", ""))
            ))

    return ArbiterEvaluation(
        round_number=round_number,
        consensus_score=score,
        is_unanimous=is_unanimous,
        executive_synthesis=str(parsed.get("executive_synthesis", "")),
        friction_points=friction_list,
        next_round_challenge=parsed.get("next_round_challenge")
    )

async def generate_final_markdown_report(
    session: DebateSession,
    arbiter_config: ModelConfig,
    phase_title: str = "Master Consensus Solution",
    phase_prompt: str = ""
) -> str:
    user_prompt = build_final_markdown_report_prompt(
        problem_statement=session.problem_statement,
        ministry_domain=session.ministry_domain,
        total_rounds=len(session.rounds),
        rounds=session.rounds,
        all_models=session.models,
        phase_title=phase_title,
        phase_prompt=phase_prompt
    )
    system_prompt = build_system_prompt_for_debater(
        model_name="Master Arbiter & Jury",
        ministry_domain=session.ministry_domain
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    report = ""
    try:
        async for chunk in UniversalAIClient.stream_chat(
            config=arbiter_config,
            messages=messages,
            temperature=0.4
        ):
            report += chunk
    except Exception as e:
        report = f"# 🏆 SIH Master Consensus Report: {phase_title}\n\n**Note**: Generated with fallback synthesis.\n\n## 1. Final Agreed Solution\n{session.rounds[-1].arbiter_eval.executive_synthesis if session.rounds and session.rounds[-1].arbiter_eval else 'Consensus reached on architecture.'}"

    return report
