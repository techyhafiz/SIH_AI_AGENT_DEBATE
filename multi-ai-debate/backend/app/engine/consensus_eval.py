import json
import re
import asyncio
from typing import List, Tuple, Optional, Set, Any
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
    build_system_prompt_for_arbiter
)
from app.providers.universal_client import UniversalAIClient, extract_and_repair_json

# Budget ceilings. Raised from the old 30k/40k because the previous limits, combined with
# head-truncation, were amputating the output contract that sits at the tail of the prompt.
ARBITER_EVAL_PROMPT_LIMIT = 90000
FINAL_REPORT_PROMPT_LIMIT = 140000


def fit_prompt(prompt: str, limit: int) -> str:
    """
    Trims from the MIDDLE, never the tail.

    `prompt[:30000]` silently deleted the output contract (the JSON schema and the honesty
    constraints) whenever the transcript grew, because the contract is the last thing in the
    prompt. The model then answered in free prose and the whole turn failed to parse. Keeping
    the head (role + directive) and the tail (contract) is always the right trade.
    """
    if len(prompt) <= limit:
        return prompt
    head_len = int(limit * 0.55)
    tail_len = limit - head_len - 200
    notice = (
        "\n\n[...evidence body truncated in the middle to fit the provider context window. "
        "The material above and below is intact. Reason only from what is present....]\n\n"
    )
    return prompt[:head_len] + notice + prompt[-tail_len:]


def _get_arbiter_candidates(session: DebateSession, primary_config: Optional[ModelConfig] = None) -> List[ModelConfig]:
    candidates = []
    if primary_config and primary_config.enabled:
        candidates.append(primary_config)

    # Check designated primary by id
    p_cfg = next((m for m in session.models if m.id == session.arbiter_model_id and m.enabled and m not in candidates), None)
    if p_cfg:
        candidates.append(p_cfg)

    # Check designated backup arbiter
    b_cfg = next((m for m in session.models if (m.id == session.backup_arbiter_model_id or m.is_backup_arbiter) and m.enabled and m not in candidates), None)
    if b_cfg:
        candidates.append(b_cfg)

    # Any other model marked is_arbiter
    for m in session.models:
        if m.is_arbiter and m.enabled and m not in candidates:
            candidates.append(m)

    # Fallback to any enabled model in fleet
    for m in session.models:
        if m.enabled and m not in candidates:
            candidates.append(m)

    return candidates


async def evaluate_round_consensus(
    session: DebateSession,
    arbiter_config: ModelConfig,
    round_number: int,
    phase_index: int = 1,
    phase_title: str = "",
    phase_prompt: str = ""
) -> ArbiterEvaluation:
    user_prompt = build_arbiter_evaluation_prompt(
        round_number=round_number,
        phase_index=phase_index,
        phase_title=phase_title or f"Phase {phase_index}",
        problem_statement=session.problem_statement,
        rounds=session.rounds,
        models=session.models,
        phase_prompt=phase_prompt,
        arbiter_name=arbiter_config.name,
        problem_domain=session.problem_domain
    )
    user_prompt = fit_prompt(user_prompt, ARBITER_EVAL_PROMPT_LIMIT)

    # P4: the arbiter used to be given the DEBATER system prompt, i.e. it was told it was
    # "competing in the SIH" and to apply the four debater lenses. A judge wearing a
    # competitor's identity writes a rival architecture instead of adjudicating one.
    system_prompt = build_system_prompt_for_arbiter(
        arbiter_name=arbiter_config.name,
        ministry_domain=session.ministry_domain,
        problem_domain=session.problem_domain
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    candidates = _get_arbiter_candidates(session, arbiter_config)
    full_text = ""
    working_arbiter_name = "Unavailable"

    for candidate in candidates:
        try:
            full_text = ""
            async for chunk in UniversalAIClient.stream_chat(
                config=candidate,
                messages=messages,
                temperature=0.3,
                require_json=True
            ):
                full_text += chunk
            if full_text.strip():
                working_arbiter_name = candidate.name
                break
        except Exception as e:
            print(f"[ARBITER FAILOVER] Arbiter candidate '{candidate.name}' failed: {e}. Trying next candidate...")

    arbiter_responded = bool(full_text.strip())
    if not arbiter_responded:
        full_text = f'{{"round_number": {round_number}, "phase_index": {phase_index}, "consensus_score": 0, "is_unanimous": false, "executive_synthesis": "Arbiter evaluation unavailable.", "friction_points": []}}'

    parsed = extract_and_repair_json(full_text)

    arbiter_score: Optional[int] = None
    raw_score = parsed.get("consensus_score")
    if raw_score is not None and not isinstance(raw_score, bool):
        try:
            if isinstance(raw_score, str):
                m = re.search(r"-?\d+", raw_score)
                raw_score = m.group(0) if m else None
            if raw_score is not None:
                arbiter_score = max(0, min(100, int(float(raw_score))))
        except Exception:
            arbiter_score = None

    raw_unanimous = parsed.get("is_unanimous", False)
    arbiter_unanimous = raw_unanimous is True or (isinstance(raw_unanimous, str) and raw_unanimous.strip().lower() == "true")

    # ------------------------------------------------------------------------------
    # P3 / P7: only responses that actually stated a readable position may contribute
    # to the consensus metric.
    #
    # Previously every `status == "completed"` response contributed, and the parser
    # manufactured DISAGREE/50 for anything whose JSON failed. On the observed run that
    # dragged Round 1 from 76.8 down to 66.8 - a 10-point understatement caused entirely
    # by parse failures being scored as dissent. Zero-byte responses counted too.
    # ------------------------------------------------------------------------------
    current_round = session.rounds[-1] if session.rounds else None
    is_unanimous = False
    score = arbiter_score if arbiter_score is not None else 50

    if current_round:
        substantive = [
            r for r in current_round.responses.values()
            if r.status == "completed" and (r.raw_text or "").strip()
        ]
        scored = [
            r for r in substantive
            if r.structured.parse_ok and r.structured.agreement_percentage is not None
        ]
        voted = [
            r for r in substantive
            if r.structured.parse_ok and r.structured.consensus_vote is not None
        ]
        agree_votes = [r for r in voted if r.structured.consensus_vote == "AGREE"]

        skipped = len(substantive) - len(scored)
        if skipped > 0:
            print(f"[CONSENSUS] Round {round_number}: excluded {skipped} unreadable/unscored "
                  f"response(s) from the consensus average ({len(scored)} counted).")

        if scored and arbiter_score is not None:
            avg_debater_pct = sum(r.structured.agreement_percentage for r in scored) / len(scored)
            score = int(round((avg_debater_pct * 0.6) + (arbiter_score * 0.4)))
        elif scored:
            score = int(round(sum(r.structured.agreement_percentage for r in scored) / len(scored)))

        # Unanimity requires that everyone who submitted actually voted, and voted AGREE.
        # An abstention (unreadable position) is not agreement.
        if (
            voted
            and len(voted) == len(substantive)
            and len(agree_votes) == len(voted)
            and arbiter_unanimous
            and arbiter_score is not None
            and arbiter_score >= 80
            and not any(fp for fp in parsed.get("friction_points", [])
                        if isinstance(fp, dict) and str(fp.get("status", "OPEN")).upper() == "OPEN")
        ):
            is_unanimous = True

    score = max(0, min(100, score))

    friction_list = []
    for fp in parsed.get("friction_points", []):
        if isinstance(fp, dict):
            status = str(fp.get("status", "OPEN")).strip().upper()
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
        phase_index=phase_index,
        phase_title=phase_title or f"Phase {phase_index}",
        consensus_score=score,
        is_unanimous=is_unanimous,
        executive_synthesis=str(parsed.get("executive_synthesis", "")),
        friction_points=friction_list,
        next_round_challenge=parsed.get("next_round_challenge"),
        arbiter_model_used=working_arbiter_name
    )


# ==============================================================================
# DELIVERABLE POST-PROCESSING
# ==============================================================================

_WRAPPER_KEYS = (
    "consensus_document", "final_report", "deliverable", "markdown_report",
    "report", "content", "markdown", "document", "final_markdown_report",
    "master_consensus_deliverable", "output",
)


def unwrap_markdown_deliverable(text: str) -> str:
    """
    D4: the final deliverable is supposed to be raw Markdown, but nothing checked.
    A real saved verdict in this repo was a JSON object with the whole document stuffed
    into a `consensus_document` string, complete with literal `\\n` escapes - unreadable
    in the UI and unusable as a submission. There was no guard at all: whatever the model
    returned was written straight to disk.
    """
    if not text:
        return text
    out = text.strip()

    # Strip a single wrapping code fence.
    fence = re.match(r"^```[a-zA-Z]*\s*\n([\s\S]*?)\n?```\s*$", out)
    if fence:
        out = fence.group(1).strip()

    # Unwrap a JSON envelope around the document.
    if out.startswith("{"):
        payload: Optional[Any] = None
        try:
            payload = json.loads(out)
        except Exception:
            try:
                payload = extract_and_repair_json(out)
            except Exception:
                payload = None
        if isinstance(payload, dict):
            for key in _WRAPPER_KEYS:
                val = payload.get(key)
                if isinstance(val, str) and val.strip():
                    out = val.strip()
                    break
            else:
                # No known key: take the longest markdown-looking string value.
                best = ""
                for val in payload.values():
                    if isinstance(val, str) and "#" in val and len(val) > len(best):
                        best = val
                if best.strip():
                    out = best.strip()

    # Un-escape a document that was serialised as a JSON string body.
    if "\\n" in out and "\n" not in out[:400]:
        out = out.replace("\\r\\n", "\n").replace("\\n", "\n").replace('\\"', '"').replace("\\t", "\t")

    return out.strip()


def _looks_like_deliverable(text: str) -> Tuple[bool, str]:
    """Returns (ok, reason). Used to reject a candidate before it is written to disk."""
    if not text or not text.strip():
        return False, "empty"
    stripped = text.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        return False, "still a JSON envelope"
    if "#" not in stripped[:2000]:
        return False, "no Markdown heading in the opening section"
    if len(stripped) < 800:
        return False, f"too short to be a deliverable ({len(stripped)} chars)"
    return True, "ok"


_CITATION_LIKE = re.compile(
    r"\[((?:paper|fact[\s\-_]?check|feasibility|source|src|ref|reference|citation|cite|doc)"
    r"[\s\-_:]*\d{1,3}[a-z]?)\]",
    re.IGNORECASE,
)
_BARE_ACADEMIC = re.compile(
    r"\b(?:arxiv\s*:\s*\d{4}\.\d{4,5}(?:v\d+)?|doi\s*:\s*10\.\d{4,9}/\S+)",
    re.IGNORECASE,
)


def _allowed_citation_tags(dossier: Optional[Any]) -> Set[str]:
    tags: Set[str] = set()
    if not dossier:
        return tags
    for attr in ("stage_1_fact_checks", "stage_2_academic_papers", "stage_3_field_benchmarks"):
        for item in (getattr(dossier, attr, None) or []):
            raw = (getattr(item, "tag", "") or "").strip()
            if not raw:
                continue
            tags.add(re.sub(r"[\s\-_:]+", "", raw.strip("[]")).lower())
    return tags


def sanitize_hallucinated_citations(report: str, dossier: Optional[Any]) -> Tuple[str, int]:
    """
    D2: strips every bracketed citation tag that does not resolve to a real retrieved source.

    Evidence this is needed: session 397de6ca ran with `latest_research_dossier = None` - no
    research was retrieved at all - and the saved deliverable still cited arXiv:2204.08912,
    IEEE TIFS 2023, NDSS, ACM CCS and eleven distinct `[Source 8]` markers. A fabricated
    academic citation in a Ministry-facing submission is disqualification-class.
    """
    if not report:
        return report, 0

    allowed = _allowed_citation_tags(dossier)
    removed = 0

    def _replace_tag(m: "re.Match") -> str:
        nonlocal removed
        # Never touch a markdown link: [text](url)
        tail = m.string[m.end():m.end() + 1]
        if tail == "(":
            return m.group(0)
        normalized = re.sub(r"[\s\-_:]+", "", m.group(1)).lower()
        if normalized in allowed:
            return m.group(0)
        removed += 1
        return "[unverified assumption]"

    cleaned = _CITATION_LIKE.sub(_replace_tag, report)

    if not allowed:
        # No sources were retrieved, so no bare arXiv id or DOI can be genuine either.
        def _replace_bare(m: "re.Match") -> str:
            nonlocal removed
            removed += 1
            return "(unverified reference removed)"
        cleaned = _BARE_ACADEMIC.sub(_replace_bare, cleaned)

    if removed:
        note = (
            "\n\n---\n\n> **Citation integrity notice:** "
            f"{removed} citation marker(s) in this document did not resolve to any source in the "
            "verified research ledger for this run and were replaced. Treat the affected claims as "
            "unverified engineering assumptions.\n"
        )
        cleaned = cleaned.rstrip() + note

    return cleaned, removed


async def generate_final_markdown_report(
    session: DebateSession,
    arbiter_config: ModelConfig,
    phase_title: str = "Master Consensus Solution",
    phase_prompt: str = ""
) -> str:
    dossier = session.latest_research_dossier
    user_prompt = build_final_markdown_report_prompt(
        problem_statement=session.problem_statement,
        ministry_domain=session.ministry_domain,
        all_rounds=[round_data for round_data in session.rounds if round_data.workspace_phase_number == session.workspace_phase_number],
        models=session.models,
        phase_title=phase_title,
        phase_prompt=phase_prompt,
        research_dossier=dossier,
        problem_domain=session.problem_domain
    )
    user_prompt = fit_prompt(user_prompt, FINAL_REPORT_PROMPT_LIMIT)
    system_prompt = build_system_prompt_for_arbiter(
        arbiter_name=arbiter_config.name,
        ministry_domain=session.ministry_domain,
        problem_domain=session.problem_domain
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    candidates = _get_arbiter_candidates(session, arbiter_config)
    best_report = ""
    best_reason = "no candidate produced output"

    for candidate in candidates:
        try:
            curr_report = ""
            async for chunk in UniversalAIClient.stream_chat(
                config=candidate,
                messages=messages,
                temperature=0.4
            ):
                curr_report += chunk

            # D4: unwrap and validate BEFORE accepting. The old loop compared raw lengths
            # and then broke at >200 chars, so the "longest candidate" comparison was dead
            # code and an unusable JSON-wrapped blob was accepted as the deliverable.
            unwrapped = unwrap_markdown_deliverable(curr_report)
            ok, reason = _looks_like_deliverable(unwrapped)
            if ok:
                best_report = unwrapped
                best_reason = "ok"
                print(f"[ARBITER REPORT] Accepted deliverable from '{candidate.name}' ({len(unwrapped)} chars).")
                break

            print(f"[ARBITER REPORT] Rejected output from '{candidate.name}': {reason}. Trying next candidate...")
            # Keep the least-bad candidate in case every model fails validation.
            if len(unwrapped.strip()) > len(best_report.strip()):
                best_report = unwrapped
                best_reason = reason
        except Exception as e:
            print(f"[ARBITER REPORT FAILOVER] Candidate '{candidate.name}' failed: {e}. Trying next...")

    report = best_report.strip()
    ok, _reason = _looks_like_deliverable(report)

    if not report:
        last_synthesis = session.rounds[-1].arbiter_eval.executive_synthesis if session.rounds and session.rounds[-1].arbiter_eval else "No arbiter synthesis was recorded."
        report = (
            f"# SIH Master Consensus Deliverable: {phase_title}\n\n"
            "## Verification Status\n"
            "This deliverable could not be generated: no arbiter candidate returned a usable report. "
            "Nothing below has been synthesised or verified.\n\n"
            "## Available Notes From The Last Evaluated Round\n"
            f"{last_synthesis}\n"
        )
    elif not ok:
        report = (
            f"# SIH Master Consensus Deliverable: {phase_title}\n\n"
            "## Verification Status\n"
            f"The arbiter's output failed the deliverable format check ({best_reason}). "
            "The raw output is preserved below unmodified so nothing is lost, but it has not been "
            "validated as a submission-ready document.\n\n"
            "## Raw Arbiter Output\n\n"
            f"{report}\n"
        )

    report, removed = sanitize_hallucinated_citations(report, dossier)
    if removed:
        print(f"[CITATION GUARD] Stripped {removed} unverifiable citation marker(s) from the deliverable "
              f"(ledger had {len(_allowed_citation_tags(dossier))} valid tag(s)).")

    return report
