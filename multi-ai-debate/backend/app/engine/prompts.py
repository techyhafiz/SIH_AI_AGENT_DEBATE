import json
from typing import List, Dict, Optional, Any, Tuple
from app.schemas import ModelConfig, RoundData, WorkspacePhase, DebaterResponse

# ==============================================================================
# ARCHITECTURAL DIRECTIVE (replaces the old blanket NO_CODE_RULE)
#
# The original rule ("DO NOT WRITE ANY CODE, SCRIPT SNIPPETS, OR PSEUDOCODE") sat
# next to prompts that demand algorithm pipelines and latency budgets. Models
# resolved the contradiction by gesturing at algorithms without specifying them,
# which loses exactly the precision SIH judges reward. This version keeps the
# original intent -- no boilerplate source code crowding out architecture -- while
# explicitly licensing algorithmic and mathematical rigour.
# ==============================================================================
NO_CODE_RULE = """
ARCHITECTURAL DIRECTIVE - NO IMPLEMENTATION BOILERPLATE:
1. DO NOT write application source code, repository scripts, class/function definitions,
   config files, or language-specific syntax (no Python/JS/C++/SQL file listings).
2. DO specify with full precision:
   - Algorithm names, step-by-step mathematical logic, and the data structures used.
   - Asymptotic complexity (e.g. Time O(N log N), Space O(K)) and measured/estimated latency.
   - Exact formulas, cost models, scaling equations, and numeric budgets.
   - Interface contracts as field lists (input -> output), protocol data units, network
     topologies, and (for hardware) component part numbers and pinouts.
Numbered procedural steps, equations, and tables are encouraged. Compilable code is not.
"""

# ==============================================================================
# DOMAIN CLASSIFICATION (D5)
#
# The old system prompt injected 45C ambient heat, dust, battery discharge curves
# and microcontroller BOMs into EVERY problem, including pure-software ones. Many
# SIH statements are genuinely hybrid cyber-physical, so this is a 3-way split
# rather than a software/hardware binary.
# ==============================================================================
DOMAIN_SOFTWARE = "software_cloud"
DOMAIN_HARDWARE = "hardware_iot"
DOMAIN_HYBRID = "hybrid_cyberphysical"

_HW_KEYWORDS = [
    "sensor", "sensors", "iot", "drone", "uav", "hardware", "microcontroller", "mcu",
    "stm32", "esp32", "arduino", "raspberry pi", "lora", "lorawan", "gsm", "gps module",
    "battery", "solar", "actuator", "rover", "wearable", "rfid", "plc", "scada",
    "telemetry", "embedded", "pcb", "antenna", "camera module", "robot", "robotics",
    "gateway node", "field device", "smart meter", "accelerometer", "gyroscope",
]
_SW_KEYWORDS = [
    "portal", "website", "web app", "web application", "blockchain", "smart contract",
    "nlp", "llm", "chatbot", "crypto", "cryptocurrency", "vasp", "api", "database",
    "dashboard", "mobile app", "android app", "ios app", "cyber", "cybersecurity",
    "fraud", "forensics", "analytics", "recommendation", "search engine", "cloud",
    "microservice", "saas", "erp", "workflow", "document", "ocr", "translation",
    "e-governance", "digital platform", "data pipeline", "machine learning model",
]


def classify_problem_domain(problem_statement: str) -> str:
    """
    Cheap deterministic 3-way classifier. Runs once per session; no LLM call, no
    network, no failure mode. Ties and empty input resolve to hybrid, which is the
    safe default because it keeps both lens sets available.
    """
    lower = (problem_statement or "").lower()
    if not lower.strip():
        return DOMAIN_HYBRID

    hw = sum(1 for kw in _HW_KEYWORDS if kw in lower)
    sw = sum(1 for kw in _SW_KEYWORDS if kw in lower)

    if hw == 0 and sw == 0:
        return DOMAIN_HYBRID
    if hw == 0:
        return DOMAIN_SOFTWARE
    if sw == 0:
        return DOMAIN_HARDWARE
    # Both present: hybrid unless one side clearly dominates (>= 3x and >= 3 hits).
    if hw >= 3 and hw >= sw * 3:
        return DOMAIN_HARDWARE
    if sw >= 3 and sw >= hw * 3:
        return DOMAIN_SOFTWARE
    return DOMAIN_HYBRID


def _normalize_domain(problem_domain: Optional[str]) -> str:
    if problem_domain in (DOMAIN_SOFTWARE, DOMAIN_HARDWARE, DOMAIN_HYBRID):
        return problem_domain
    return DOMAIN_HYBRID


# Per-domain wording for the third ("feasibility") lens. The JSON key stays
# `field_hardware_lens` for storage and frontend compatibility across the 25+
# existing workspaces; only its meaning is re-pointed per domain.
_FEASIBILITY_LENS_SPEC = {
    DOMAIN_SOFTWARE: (
        "Frugal Infrastructure & Cost Engineer: cloud/on-prem compute tiers, GPU/CPU sizing, "
        "database and storage growth, egress, third-party API quotas, and an itemised monthly "
        "and annual run-cost table in Indian Rupees at the stated user/transaction volume. "
        "State the data volumes, latency budget (p50/p95/p99) and the scaling ceiling."
    ),
    DOMAIN_HARDWARE: (
        "Frugal Field & BOM Engineer: exact ICs, MCUs, sensors, modems and power components with "
        "part numbers, an itemised Bill of Materials in Indian Rupees per unit and at scale, plus "
        "power budget (mA active/sleep, expected battery life). Ground it in real Indian field "
        "conditions: 45C ambient, dust ingress, monsoon humidity, erratic grid, 2G/intermittent backhaul."
    ),
    DOMAIN_HYBRID: (
        "Frugal Feasibility Engineer (cyber-physical): BOTH the edge-device Bill of Materials in "
        "Indian Rupees with part numbers and power budget, AND the cloud/backend run-cost table in "
        "Indian Rupees. Ground the edge tier in real Indian field conditions (45C, dust, erratic grid, "
        "2G backhaul) and the backend tier in data volume, latency budget and scaling limits."
    ),
}

_FEASIBILITY_LENS_LABEL = {
    DOMAIN_SOFTWARE: "Infrastructure Cost & Scale Feasibility",
    DOMAIN_HARDWARE: "Field Hardware, BOM & Power",
    DOMAIN_HYBRID: "Feasibility: Edge BOM + Cloud Cost",
}

_DOMAIN_IDENTITY = {
    DOMAIN_SOFTWARE: "Software, Cloud & Data Systems Architect",
    DOMAIN_HARDWARE: "Embedded, IoT & Hardware Systems Architect",
    DOMAIN_HYBRID: "Cyber-Physical Systems Architect (embedded edge + cloud backend)",
}

_DOMAIN_NOTE = {
    DOMAIN_SOFTWARE: (
        "This problem statement has been classified as SOFTWARE / CLOUD / AI. Do NOT introduce "
        "microcontrollers, sensor BOMs, battery budgets or ambient-temperature analysis unless the "
        "problem statement itself requires physical devices. Spend that effort on data models, "
        "algorithms, cost-at-scale, latency and security instead."
    ),
    DOMAIN_HARDWARE: (
        "This problem statement has been classified as HARDWARE / IoT / EMBEDDED. Physical component "
        "selection, power budgets, enclosure/environmental hardening and field logistics are in scope "
        "and expected."
    ),
    DOMAIN_HYBRID: (
        "This problem statement has been classified as HYBRID CYBER-PHYSICAL. Both tiers are in scope: "
        "the physical/edge tier (components, power, environment) and the software/cloud tier (data, "
        "algorithms, cost, latency). Make the boundary between them explicit."
    ),
}


def _budget_section_title(domain: str) -> str:
    if domain == DOMAIN_SOFTWARE:
        return "Infrastructure, Compute & Operating Cost Budget in Indian Rupees (INR)"
    if domain == DOMAIN_HARDWARE:
        return "Itemized Bill of Materials (BOM), Power Budget & Unit Economics in Indian Rupees (INR)"
    return "Itemized Edge BOM + Cloud Infrastructure Cost Budget in Indian Rupees (INR)"


# ==============================================================================
# OUTPUT CONTRACT
#
# Two structural changes from the original SCHEMA_GUIDE:
#  (P7) The scratchpad is now OUTSIDE the JSON in an XML tag. Previously thousands
#       of characters of free reasoning lived inside a JSON string value, so a
#       single unescaped quote invalidated the whole object -- taking the vote, the
#       solution and every lens down with it (28,565 chars of Qwen output was lost
#       this way).
#  (P3/P4) Every example value is a PLACEHOLDER with a rubric, never a literal
#       number. Literal `75`/`80`/`85`/`95` acted as anchors and drove the headline
#       consensus metric.
# ==============================================================================

_CONTRACT_PREAMBLE = """OUTPUT CONTRACT (follow exactly):
Step 1 - Think in the open, outside the JSON:
<scratchpad>
Unconstrained reasoning: arithmetic, stress-testing, edge cases, rejected alternatives.
Quotes, newlines and backticks are safe in here. Nothing in this block needs escaping.
</scratchpad>

Step 2 - Then emit ONE JSON object inside a ```json fence. Rules:
- The JSON object MUST be complete and every bracket balanced. This matters more than length.
- If you are running low on output budget, shorten the scratchpad and the lens prose first.
  A truncated JSON object is discarded entirely and your turn scores as a non-submission.
- Angle-bracket text below (<like this>) is an INSTRUCTION describing what to write.
  Never copy it literally, and never copy an example number.
"""

_VOTE_RUBRIC = """  "consensus_vote": "<exactly one of AGREE | DISAGREE | NEEDS_REFINEMENT - your genuine position on the emerging shared solution>",
  "agreement_percentage": "<integer 0-100. Rubric: 90-100 = ready to build as specified; 70-89 = agree with the specific reservations you listed above; 40-69 = major redesign required; 0-39 = fundamental disagreement. Report your honest reading. Do not gravitate to a round number and do not copy any figure you have seen in this prompt.>\""""


def build_schema_guide(problem_domain: Optional[str] = None, include_vote: bool = True) -> str:
    """
    Full debate-round output contract. Per-field length budgets are stated inline (P9)
    so models stop spending their entire max_tokens on the first two fields and getting
    truncated mid-object.
    """
    domain = _normalize_domain(problem_domain)
    feasibility_desc = _FEASIBILITY_LENS_SPEC[domain]

    vote_block = f",\n{_VOTE_RUBRIC}" if include_vote else ""

    return f"""{_CONTRACT_PREAMBLE}
```json
{{
  "architect_lens": "<150-250 words: system structure, data/signal pipelines, component hierarchy, workflow>",
  "critic_lens": "<120-200 words: YOUR OWN design's edge cases, failure modes and fragile assumptions. Self-directed red-teaming only - attacks on peers belong in `critiques`.>",
  "field_hardware_lens": "<150-250 words: {feasibility_desc}>",
  "security_compliance_lens": "<120-200 words: threat model, tamper/abuse resistance, fail-safe degradation, and the specific Indian statutory standards that apply (name only those genuinely relevant to this problem)>",
  "critiques": [
    {{
      "target_model_id": "<the exact Model ID of the PEER you are challenging, copied from the peer transcript>",
      "target_model_name": "<that peer's display name>",
      "flaw_identified": "<the specific vulnerability, false assumption or arithmetic error - name it precisely>",
      "counter_argument": "<up to 80 words of rigorous technical reasoning, with numbers where possible>"
    }}
  ],
  "concessions_and_defenses": [
    {{
      "conceded_point": "<prefix with [CONCESSION] or [DEFENSE], then state the point>",
      "conceded_to": "<the peer who raised it>",
      "adaptation": "<if CONCESSION: exactly how your design changed. If DEFENSE: the evidence or arithmetic that refutes their objection.>"
    }}
  ],
  "refined_solution": "<400-600 words: the complete, hardened, end-to-end solution as it now stands after this round. This is the field the final deliverable is built from - make it self-contained and specific.>",
  "positives_of_approach": ["<concrete advantage>", "<concrete advantage>"],
  "negatives_and_risks": ["<honest remaining weakness>", "<honest remaining weakness>"],
  "autonomous_research_calls": [
    {{
      "stage": "<one of fact_check | frontier_academic | field_feasibility>",
      "target_engine": "<tavily_web for facts/prices/standards, openalex_arxiv for papers>",
      "query_purpose": "<the specific number or claim you need verified, and why it matters>",
      "search_query": "<the literal search string>"
    }}
  ],
  "research_queries_for_next_round": ["<open question you want evidence on>"]{vote_block}
}}
```
Emit 2-4 `critiques` when a peer transcript is present, and one `concessions_and_defenses`
entry for every critique that was directed at you."""


# Backwards-compatible module-level constant (some call sites import SCHEMA_GUIDE directly).
SCHEMA_GUIDE = build_schema_guide()


def build_system_prompt_for_debater(
    model_name: str,
    ministry_domain: str,
    problem_domain: Optional[str] = None,
) -> str:
    domain = _normalize_domain(problem_domain)
    identity = _DOMAIN_IDENTITY[domain]
    domain_note = _DOMAIN_NOTE[domain]
    feasibility_label = _FEASIBILITY_LENS_LABEL[domain]

    return f"""You are '{model_name}', a world-class {identity} competing in the Smart India Hackathon (SIH) for the domain '{ministry_domain}'.

Your goal is to debate, challenge, stress-test and collaboratively construct a winning sovereign deliverable for the problem statement.

DOMAIN SCOPE:
{domain_note}

YOUR FOUR COGNITIVE LENSES:
You possess four lenses. You do NOT apply all four on every turn - you apply them dynamically,
exactly as directed by the task instructions of the current phase or round.
1. Lead Architect: high-level vision, system decomposition, paradigms, workflow.
2. Murphy's Law Red-Team Critic: hidden race conditions, single points of failure, unfeasible
   bandwidth/latency/power assumptions, cascading failures.
3. {feasibility_label}: real-world cost, capacity and operating limits in Indian Rupees.
4. Security & Standards Officer: abuse and tamper resistance, graceful degradation, and the
   Indian statutory norms that genuinely apply to this problem.

DEBATE CONDUCT:
Be rigorous, specific and unsparing about technical flaws. Attack assumptions, arithmetic and
architecture - never the author. Concede immediately and explicitly when a peer is right: a
concession backed by reasoning scores higher here than a defended error. Prefer a number to an
adjective. If you do not know a figure, say so and request it via `autonomous_research_calls`
rather than inventing it.

GROUNDED CITATION PROTOCOL:
- When a Live Research Dossier is attached, cite its sources using their exact inline tags
  (e.g. [Paper 1], [Fact-Check 2], [Feasibility 1]) to substantiate specs and component choices.
- If NO dossier is attached, you MUST NOT cite any paper, arXiv identifier, journal, conference,
  standard number or source tag. State "unverified assumption" instead. Inventing a citation is
  the single most damaging thing you can do in this deliberation.
- If a dossier source CONTRADICTS your specification, you must either revise the specification or
  state explicitly why the source does not apply. Citing a source you contradict, without
  comment, is a scoring failure.

{NO_CODE_RULE}"""


def build_system_prompt_for_arbiter(
    arbiter_name: str,
    ministry_domain: str,
    problem_domain: Optional[str] = None,
) -> str:
    """
    P4: the arbiter previously received the DEBATER system prompt, i.e. it was told it
    was "competing" in the hackathon and to apply the four debater lenses. A judge with
    a competitor's identity writes its own third architecture instead of evaluating.
    """
    domain = _normalize_domain(problem_domain)
    return f"""You are '{arbiter_name}', the Master Arbiter and Chief Technical Juror of a Smart India Hackathon (SIH) deliberation in the domain '{ministry_domain}'.

Your mandate is strictly evaluative and synthesising. You are NOT a competitor. You do not
author your own rival architecture and you do not add unvetted ideas of your own.

Your responsibilities:
1. Weigh the debaters' proposals, cross-critiques, defenses and concessions impartially against
   Indian physical, regulatory and budgetary reality. Problem domain: {domain}.
2. Adjudicate each technical friction point as OPEN, RESOLVED or CONCEDED, based on what the
   transcript actually establishes.
3. Set a demanding, specific directive for the next round that forces the open disputes to close.
4. Measure genuine consensus as a calibrated number, not a flattering one.
5. When asked, synthesise the definitive Sovereign Master Consensus Deliverable.

EVIDENCE DISCIPLINE (this overrides any instinct to be generous):
- Report only what the transcript supports. Quote or paraphrase the specific submission you are
  crediting.
- If a model did not submit, submitted nothing usable, errored or timed out, say exactly that and
  assign it no credit and no contribution. Do not reconstruct what it "would have" argued.
- Do not describe infrastructure events (a retry, a key rotation, a format repair) as an
  intellectual contribution.
- Penalise vague hand-waving. Reward concrete arithmetic, fault-tolerant topologies, honest cost
  models and genuine statutory grounding.
- Never invent a citation, paper, standard number or source tag.

{NO_CODE_RULE}"""


# ==============================================================================
# SHARED PROMPT-ASSEMBLY HELPERS
# ==============================================================================

def _tagged(tag: str, content: str) -> str:
    """P13: wrap interpolated free text so quotes/braces/backticks in a problem
    statement cannot corrupt the surrounding contract or close a fence early."""
    return f"<{tag}>\n{content}\n</{tag}>"


def _is_critique_aimed_at(c: Any, my_id: str, my_name: str) -> bool:
    tid = (getattr(c, "target_model_id", "") or "").strip()
    tname = (getattr(c, "target_model_name", "") or "").strip().lower()
    if tid and tid == my_id:
        return True
    if not tname:
        return False
    mine = (my_name or "").strip().lower()
    if not mine:
        return False
    return tname == mine or tname in mine or mine in tname


def render_targeted_critiques_block(
    prev_round: Optional[RoundData],
    my_model_config: ModelConfig,
) -> str:
    """
    P1 - the defect that made this "N parallel monologues with a scoreboard".
    76 targeted critiques (87.5 KB) were generated and persisted across rounds 2-4 of
    the real 397de6ca run and never shown to the model they were written about.
    """
    targeted: List[str] = []
    cross_traffic: List[str] = []

    if prev_round:
        for m_id, resp in prev_round.responses.items():
            if m_id == my_model_config.id:
                continue
            st = getattr(resp, "structured", None)
            if not st or not st.critiques:
                continue
            for c in st.critiques:
                if not (c.flaw_identified or c.counter_argument):
                    continue
                if _is_critique_aimed_at(c, my_model_config.id, my_model_config.name):
                    targeted.append(
                        f"- **From {resp.model_name}**\n"
                        f"  - Flaw alleged: {c.flaw_identified}\n"
                        f"  - Their counter-argument: {c.counter_argument}"
                    )
                else:
                    cross_traffic.append(
                        f"- {resp.model_name} -> {c.target_model_name or 'a peer'}: {c.flaw_identified[:160]}"
                    )

    if targeted:
        block = (
            "### CRITIQUES DIRECTED AT YOUR ARCHITECTURE - MANDATORY RESPONSE\n"
            "Each item below was written specifically about your proposal. You MUST answer every one\n"
            "in `concessions_and_defenses`, prefixing each with `[CONCESSION]` (you accept it - state\n"
            "exactly how your design changes) or `[DEFENSE]` (you reject it - give the arithmetic or\n"
            "evidence that refutes it). Ignoring a critique counts as conceding it silently.\n\n"
            + "\n".join(targeted[:12])
        )
    else:
        block = (
            "### CRITIQUES DIRECTED AT YOUR ARCHITECTURE\n"
            "No peer launched a direct counter-argument against your proposal in the previous round.\n"
            "Do not invent one to answer. Instead, cross-examine the peer proposals below and pressure-test\n"
            "your own weakest assumption."
        )

    if cross_traffic:
        block += (
            "\n\n### OTHER CROSS-CRITIQUE TRAFFIC IN THE ROOM (context only)\n"
            + "\n".join(cross_traffic[:15])
        )
    return block


def render_arbiter_directive_block(prev_round: Optional[RoundData]) -> str:
    """
    P2 - `next_round_challenge`, `friction_points` and `executive_synthesis` were
    produced every round and never read into any subsequent prompt. Placed BEFORE the
    peer transcript so it frames how the transcript is read.
    """
    if not prev_round or not prev_round.arbiter_eval:
        return ""

    ae = prev_round.arbiter_eval
    parts: List[str] = []

    challenge = (ae.next_round_challenge or "").strip()
    if challenge:
        parts.append(f"### ARBITER DIRECTIVE FOR THIS ROUND (mandatory)\n{challenge}")

    synthesis = (ae.executive_synthesis or "").strip()
    if synthesis:
        parts.append(
            "### ARBITER'S READING OF THE PREVIOUS ROUND\n"
            f"Measured consensus: {ae.consensus_score}%\n{synthesis[:1800]}"
        )

    open_points = [fp for fp in ae.friction_points if fp.status == "OPEN"]
    settled = [fp for fp in ae.friction_points if fp.status != "OPEN"]

    if open_points:
        lines = []
        for idx, fp in enumerate(open_points, start=1):
            lines.append(
                f"F{idx}. **{fp.issue}**\n"
                f"    - raised by {fp.raised_by or 'unattributed'}, challenged by {fp.challenged_by or 'unattributed'}\n"
                f"    - state of play: {fp.resolution_notes or 'unresolved'}"
            )
        parts.append(
            "### UNRESOLVED FRICTION POINTS - TAKE A POSITION ON EACH\n"
            "Reference each by its F-number in your response and state your technical stance. "
            "An unaddressed friction point cannot be closed.\n\n" + "\n".join(lines)
        )

    if settled:
        parts.append(
            "### ALREADY SETTLED (do not relitigate)\n"
            + "\n".join(f"- [{fp.status}] {fp.issue}" for fp in settled[:10])
        )

    return "\n\n".join(parts)


def render_my_previous_position(my_prev_response: str, submitted: bool) -> str:
    """
    P12 - when a model failed/timed out, this block rendered empty under a heading
    asserting a position existed, so the model confabulated one and then defended it.
    That is how a zero-byte model acquired an architecture it never proposed.
    """
    if submitted and my_prev_response.strip():
        return "### YOUR PREVIOUS POSITION\n" + my_prev_response.strip()
    return (
        "### YOUR PREVIOUS POSITION\n"
        "You did NOT submit a usable response in the previous round. You therefore have no prior\n"
        "position on record. Do not claim one and do not defend one. Build your proposal fresh from\n"
        "the problem statement and the peer transcript below."
    )


def render_position_history(
    previous_rounds: List[RoundData],
    my_model_id: str,
    max_rounds: int = 3,
) -> str:
    """
    P10 - Round 2.3 asks how positions evolved across the phase but was only ever shown
    the single preceding round, so the trajectory was invented. This is a compact digest:
    one line per model per prior round.
    """
    if len(previous_rounds) < 2:
        return ""

    lines: List[str] = []
    for r in previous_rounds[-max_rounds:]:
        label = r.pass_or_round_title or f"Round {r.round_number}"
        for m_id, resp in r.responses.items():
            if resp.status != "completed":
                continue
            st = getattr(resp, "structured", None)
            if not st:
                continue
            vote = st.consensus_vote or "no stated vote"
            pct = f"{st.agreement_percentage}%" if st.agreement_percentage is not None else "unscored"
            gist = (st.refined_solution or st.architect_lens or "").strip().replace("\n", " ")
            who = f"{resp.model_name}{' (you)' if m_id == my_model_id else ''}"
            lines.append(f"- [{label}] {who}: {vote} / {pct} - {gist[:220]}")

    if not lines:
        return ""
    return (
        "### POSITION TRAJECTORY ACROSS THIS PHASE (for measuring who moved and who held)\n"
        + "\n".join(lines[:60])
    )


def _render_peer_block(resp: DebaterResponse, m_id: str, detail: str = "full") -> str:
    st = resp.structured
    header = f"---\n### Peer: {resp.model_name}  (Model ID: {m_id})"
    if detail == "brief":
        vote = st.consensus_vote or "no stated vote"
        pct = f"{st.agreement_percentage}%" if st.agreement_percentage is not None else "unscored"
        return (
            f"{header}\n"
            f"- Stated position: {vote} ({pct})\n"
            f"- Solution: {st.refined_solution}\n"
        )

    lines = [header]
    if st.architect_lens:
        lines.append(f"- Architecture: {st.architect_lens}")
    critic = st.critic_lens or st.critic_devil_advocate_lens
    if critic:
        lines.append(f"- Their own stated risks: {critic}")
    feas = st.field_hardware_lens or st.pragmatist_feasibility_lens
    if feas:
        lines.append(f"- Feasibility / cost: {feas}")
    sec = st.security_compliance_lens or st.security_reliability_lens
    if sec:
        lines.append(f"- Security & compliance: {sec}")
    if st.refined_solution:
        lines.append(f"- Proposed solution: {st.refined_solution}")
    if st.positives_of_approach:
        lines.append(f"- Claimed advantages: {json.dumps(st.positives_of_approach)}")
    if st.negatives_and_risks:
        lines.append(f"- Admitted weaknesses: {json.dumps(st.negatives_and_risks)}")
    if st.concessions_and_defenses:
        cds = "; ".join(
            f"{cd.conceded_point} (to {cd.conceded_to}) -> {cd.adaptation}"[:220]
            for cd in st.concessions_and_defenses[:4]
        )
        lines.append(f"- Their concessions/defenses last round: {cds}")
    return "\n".join(lines) + "\n"


def _split_prev_round(
    prev_round: Optional[RoundData],
    my_model_config: ModelConfig,
    detail: str = "full",
) -> Tuple[str, str, bool]:
    """Returns (my_prev_response, peers_text, i_submitted)."""
    my_prev = ""
    i_submitted = False
    peers: List[str] = []

    if prev_round:
        for m_id, resp in prev_round.responses.items():
            if m_id == my_model_config.id:
                if resp.status == "completed" and (resp.structured.refined_solution or resp.raw_text).strip():
                    my_prev = resp.structured.refined_solution or resp.raw_text
                    i_submitted = True
                continue
            if resp.status != "completed":
                peers.append(
                    f"---\n### Peer: {resp.model_name}  (Model ID: {m_id})\n"
                    f"- NO SUBMISSION this round (status: {resp.status}). This peer has no position on "
                    f"record. Do not critique or attribute a position to it.\n"
                )
                continue
            peers.append(_render_peer_block(resp, m_id, detail=detail))

    return my_prev, "\n".join(peers), i_submitted


def _assemble_round_prompt(
    header: str,
    problem_statement: str,
    round_mission: str,
    arbiter_block: str,
    critiques_block: str,
    my_position_block: str,
    peers_text: str,
    history_block: str,
    injection_block: str,
    schema_guide: str,
) -> str:
    """
    P5 - assembly order matters. Role/task -> problem -> arbiter directive -> critiques
    aimed at me -> my position -> peer transcript -> moderator -> OUTPUT CONTRACT LAST.
    The contract must occupy the recency-privileged final position, and (in the
    orchestrator) must be re-appended after any truncation rather than being the first
    thing cut.
    """
    sections = [
        header,
        "**Problem statement:**\n" + _tagged("problem_statement", problem_statement),
        "### CURRENT ROUND OBJECTIVE\n" + round_mission,
    ]
    for block in (arbiter_block, critiques_block, my_position_block):
        if block and block.strip():
            sections.append(block)
    if peers_text and peers_text.strip():
        sections.append("### PEER SUBMISSIONS FROM THE PREVIOUS ROUND\n" + peers_text)
    for block in (history_block, injection_block):
        if block and block.strip():
            sections.append(block)
    sections.append(schema_guide)
    return "\n\n".join(sections)


def _injection_block(moderator_injection: Optional[str]) -> str:
    if not moderator_injection or not moderator_injection.strip():
        return ""
    return (
        "### HUMAN MODERATOR INTERVENTION - NEW BINDING CONSTRAINT\n"
        + _tagged("moderator_directive", moderator_injection.strip())
        + "\nYou MUST incorporate and explicitly address this direction in your response."
    )


# ==============================================================================
# PHASE 1: MULTI-PERSONA GENESIS (Internal 4-Pass Foundation)
#
# The 4-pass split is retained deliberately: sequential Architect -> Red-Team ->
# Feasibility -> Security passes produce materially more depth than asking for all
# four at once. What changed is that the passes no longer demand a consensus vote
# (P11: there are no peers yet to agree with), and self-critique no longer
# masquerades as a peer critique (P15).
# ==============================================================================

def get_phase_1_schema_guide(pass_id: str, problem_domain: Optional[str] = None) -> str:
    domain = _normalize_domain(problem_domain)

    if pass_id == "1.1":
        return f"""{_CONTRACT_PREAMBLE}
This pass covers your CORE ARCHITECTURE ONLY. Leave the critic, feasibility and security
lenses for the dedicated later passes - do not pre-empt them here.
```json
{{
  "architect_lens": "<250-400 words: conceptual system decomposition, ingestion and data-flow topology, multi-tier component hierarchy, and the boundary between tiers>",
  "refined_solution": "<400-600 words: your initial end-to-end architectural proposal for this problem statement>",
  "positives_of_approach": ["<architectural strength>", "<architectural strength>"],
  "negatives_and_risks": ["<architectural risk or scaling bottleneck you already foresee>"],
  "autonomous_research_calls": [
    {{
      "stage": "<fact_check | frontier_academic | field_feasibility>",
      "target_engine": "<tavily_web | openalex_arxiv>",
      "query_purpose": "<the specific claim or figure you need verified>",
      "search_query": "<the literal search string>"
    }}
  ],
  "research_queries_for_next_round": ["<open question you want evidence on>"]
}}
```"""

    if pass_id == "1.2":
        return f"""{_CONTRACT_PREAMBLE}
This pass is RED-TEAMING YOUR OWN Pass 1.1 design. You are attacking yourself, not any peer -
so `critiques` stays empty and your self-attacks go in `self_identified_flaws`.
```json
{{
  "critic_lens": "<250-400 words: a ruthless attack on your own Pass 1.1 design - single points of failure, unfeasible latency/bandwidth assumptions, race conditions, cascading failures, edge-case crashes>",
  "self_identified_flaws": [
    "<a specific fatal vulnerability or unrealistic assumption in your Pass 1.1, followed by why it fails under stress - be concrete and quantitative>",
    "<another>"
  ],
  "critiques": [],
  "refined_solution": "<400-600 words: your updated, hardened architecture that addresses each flaw above>",
  "positives_of_approach": ["<resilience gained>"],
  "negatives_and_risks": ["<vulnerability that remains unresolved>"]
}}
```"""

    if pass_id == "1.3":
        return f"""{_CONTRACT_PREAMBLE}
This pass covers FEASIBILITY AND COST ONLY, in Indian Rupees.
```json
{{
  "field_hardware_lens": "<250-400 words: {_FEASIBILITY_LENS_SPEC[domain]} Present the cost breakdown as a markdown table with real figures and state your assumptions.>",
  "refined_solution": "<400-600 words: the cost-optimised, deployment-hardened specification with its INR budget>",
  "positives_of_approach": ["<cost or durability advantage>"],
  "negatives_and_risks": ["<supply-chain, lead-time, quota or scaling constraint>"]
}}
```"""

    if pass_id == "1.4":
        return f"""{_CONTRACT_PREAMBLE}
This pass covers SECURITY, RESILIENCE AND STATUTORY COMPLIANCE ONLY.
```json
{{
  "security_compliance_lens": "<250-400 words: threat model and abuse cases, tamper/intrusion resistance, encrypted store-and-forward buffering, fail-safe degradation, and compliance with the Indian statutory norms that genuinely apply here (e.g. DPDP Act 2023, MeitY guidelines, CERT-In directions, and sector norms such as RDSO, NDMA, ISRO Bhuvan or ABDM only where actually relevant). Do not cite a standard number you are not certain of.>",
  "refined_solution": "<400-600 words: the fully fortified specification>",
  "positives_of_approach": ["<compliance or resilience strength>"],
  "negatives_and_risks": ["<residual compliance or audit burden>"]
}}
```"""

    return build_schema_guide(problem_domain)


def build_phase_1_pass_prompt(
    pass_id: str,
    problem_statement: str,
    ministry_domain: str,
    my_prior_passes: Dict[str, str],
    prior_phases: List[WorkspacePhase] = [],
    problem_domain: Optional[str] = None,
) -> str:
    prior_context = ""
    if prior_phases:
        chunks = []
        for p in prior_phases:
            chunks.append(f"--- Phase {p.phase_index} verdict ({p.phase_title}) ---\n{p.verdict_markdown[:2500]}")
        prior_context = (
            "### ALREADY-AGREED CONSENSUS DELIVERABLES IN THIS WORKSPACE\n"
            "These are settled. Build on them; do not contradict them without saying so explicitly.\n\n"
            + "\n\n".join(chunks)
        )

    prior_pass_text = ""
    if my_prior_passes:
        chunks = [f"--- Your Pass {pid} output ---\n{pcontent[:4000]}" for pid, pcontent in my_prior_passes.items()]
        prior_pass_text = "### YOUR OWN EARLIER PASSES IN PHASE 1\n" + "\n\n".join(chunks)

    mission_desc = ""
    if pass_id == "1.1":
        mission_desc = """**PASS 1.1 - ARCHITECT GENESIS (core architecture only)**
- Focus entirely on your high-level architectural vision.
- Define the conceptual data pipelines, ingestion topology and system decomposition.
- Trace the multi-tier workflow end to end, from first capture to final user-facing output.
- Do NOT write the feasibility, critic or security sections - each has its own dedicated pass."""
    elif pass_id == "1.2":
        mission_desc = """**PASS 1.2 - MURPHY'S LAW INVERSION (red-team your own Pass 1.1)**
- Re-read your Pass 1.1 architecture above and attack it as an adversary would.
- Find the hidden race conditions, single points of failure, and unrealistic
  bandwidth/storage/power/latency assumptions.
- Where exactly does it break under 1000x load, 30% packet loss, or a network partition?
- Then propose the specific architectural defense for each failure mode you found."""
    elif pass_id == "1.3":
        mission_desc = """**PASS 1.3 - FEASIBILITY & INR BUDGET REALITY**
- Re-engineer your design against real Indian deployment conditions and real prices.
- Give concrete figures: part numbers and unit costs, or instance types and monthly run cost.
- Itemise the budget in Indian Rupees for a production deployment at a stated scale, and say
  what that scale assumption is."""
    elif pass_id == "1.4":
        mission_desc = """**PASS 1.4 - SECURITY, RESILIENCE & STATUTORY COMPLIANCE**
- Harden against tampering, unauthorised access, data corruption and abuse.
- Specify offline-first store-and-forward buffering and graceful degradation behaviour.
- Map the design onto the Indian statutory standards that genuinely apply to this problem."""

    header = f"""### SMART INDIA HACKATHON (SIH) - PHASE 1: MULTI-PERSONA GENESIS
**Domain / Ministry:** {ministry_domain}
This is solo foundation work. No peers are visible yet, so there is nothing to vote on and no
consensus to declare in this phase."""

    sections = [
        header,
        "**Problem statement:**\n" + _tagged("problem_statement", problem_statement),
    ]
    if prior_context:
        sections.append(prior_context)
    if prior_pass_text:
        sections.append(prior_pass_text)
    sections.append("### CURRENT COGNITIVE MISSION\n" + mission_desc)
    sections.append(get_phase_1_schema_guide(pass_id, problem_domain))
    return "\n\n".join(sections)


# ==============================================================================
# PHASE 2: THE ADVERSARIAL CRUCIBLE (3-Round Courtroom Cross-Debate)
# ==============================================================================

def build_phase_2_round_prompt(
    round_id: str,
    round_number: int,
    problem_statement: str,
    my_model_config: ModelConfig,
    all_models: List[ModelConfig],
    previous_rounds: List[RoundData],
    moderator_injection: str = "",
    problem_domain: Optional[str] = None,
) -> str:
    prev_round = previous_rounds[-1] if previous_rounds else None
    my_prev, peers_text, i_submitted = _split_prev_round(prev_round, my_model_config, detail="full")

    round_mission = ""
    if round_id == "2.1":
        round_mission = """**ROUND 2.1 - OPENING CROSS-EXAMINATION & FLAW HUNTING**
- Scrutinise every peer's Phase 1 dossier below.
- Go after unrealistic bandwidth and latency claims, naive pricing, power-draw traps, ignored
  failure modes and unsupported assertions.
- Name the specific peer and their specific claim in each critique. Bring arithmetic. A critique
  without a number or a named mechanism is not a critique.
- Attack the engineering, never the model."""
    elif round_id == "2.2":
        round_mission = """**ROUND 2.2 - DEFENSE, REBUTTAL & COUNTER-ATTACK**
- Answer every critique aimed at you (see the mandatory section above).
- Where a peer's objection rests on a faulty assumption, expose the specific error with numbers.
- Where a peer found a genuine flaw, concede it plainly and show exactly how your design adapts.
  A reasoned concession scores higher than a defended error.
- Then continue cross-examining the peer claims that still look unsupported."""
    elif round_id == "2.3":
        round_mission = """**ROUND 2.3 - CLOSING SCRUTINY & FATAL-FLAW LOCKING**
- Apply the jury test using the trajectory digest below: whose defenses actually held across the
  phase, and whose collapsed? Cite the round in which each position moved.
- Lock in the definitive list of VERIFIED FATAL VULNERABILITIES that any viable system must fix.
  Put these in `negatives_and_risks`.
- Judge only from what is on the record below. If the record does not show a position, say so
  rather than reconstructing it."""

    history_block = render_position_history(previous_rounds, my_model_config.id) if round_id == "2.3" else ""

    return _assemble_round_prompt(
        header="### SMART INDIA HACKATHON (SIH) - PHASE 2: ADVERSARIAL CRUCIBLE",
        problem_statement=problem_statement,
        round_mission=round_mission,
        arbiter_block=render_arbiter_directive_block(prev_round),
        critiques_block=render_targeted_critiques_block(prev_round, my_model_config),
        my_position_block=render_my_previous_position(my_prev, i_submitted),
        peers_text=peers_text,
        history_block=history_block,
        injection_block=_injection_block(moderator_injection),
        schema_guide=build_schema_guide(problem_domain),
    )


# ==============================================================================
# PHASE 3: THE 10x ADVANCED SOLUTION ENGINE (2-Round Progressive Polish)
# ==============================================================================

def build_phase_3_round_prompt(
    round_id: str,
    round_number: int,
    problem_statement: str,
    my_model_config: ModelConfig,
    all_models: List[ModelConfig],
    previous_rounds: List[RoundData],
    moderator_injection: str = "",
    problem_domain: Optional[str] = None,
) -> str:
    prev_round = previous_rounds[-1] if previous_rounds else None
    my_prev, peers_text, i_submitted = _split_prev_round(prev_round, my_model_config, detail="full")
    domain = _normalize_domain(problem_domain)

    if domain == DOMAIN_SOFTWARE:
        pillar_2 = ("**Frugal architecture & INR budget:** itemised cloud/on-prem compute, storage, "
                    "database, egress and third-party API costs, monthly and annual, at a stated scale.")
        pillar_3 = ("**Core SOTA algorithms & performance pipeline:** the state-of-the-art models and "
                    "algorithms for this domain, with complexity bounds, indexing/retrieval strategy, "
                    "and a p50/p95/p99 latency budget.")
    elif domain == DOMAIN_HARDWARE:
        pillar_2 = ("**Frugal architecture & INR budget:** exact ICs, sensors, modems, power components "
                    "with part numbers and unit costs, plus the power budget and expected battery life.")
        pillar_3 = ("**Core SOTA algorithms & performance pipeline:** on-device signal processing and "
                    "inference (e.g. TinyML quantisation, Kalman/complementary filtering, anomaly "
                    "detection), with memory footprint, duty cycle and compute budget.")
    else:
        pillar_2 = ("**Frugal architecture & INR budget:** BOTH the per-unit edge BOM with part numbers "
                    "AND the cloud/backend run cost, monthly and annual, at a stated fleet size.")
        pillar_3 = ("**Core SOTA algorithms & performance pipeline:** the edge/cloud split of inference, "
                    "on-device filtering and backend models, with complexity, footprint and end-to-end "
                    "latency budget.")

    round_mission = ""
    if round_id == "3.1":
        round_mission = f"""**ROUND 3.1 - THE 10x LEAP (four pillars, adapted to this problem's domain)**
1. **Flaw inversion:** solve every verified fatal vulnerability and edge case locked in from Phase 2.
   Address them individually, not as a general claim of robustness.
2. {pillar_2}
3. {pillar_3}
4. **Sovereign Indian ecosystem & compliance:** integration with the Indian platforms and standards
   that genuinely apply here (e.g. IndiaStack, DigiLocker, ONDC, Bhashini, ISRO Bhuvan, RDSO, NDMA,
   ABDM, DPDP Act 2023). Name only what is actually relevant - a padded list is a weakness."""
    elif round_id == "3.2":
        round_mission = """**ROUND 3.2 - MICRO-OPTIMISATION & CROSS-POLLINATION**
- Read the peer breakthroughs from Round 3.1 and openly adopt the ones that beat yours. Credit the
  peer you took each idea from in `concessions_and_defenses`.
- Then add the neglected engineering detail that separates a demo from a deployment: graceful
  degradation, brownout and offline store-and-forward behaviour, auto-calibration and drift
  correction, rate-limit and backpressure handling, idempotent retry, and zero-trust recovery.
- Be specific about thresholds, buffer sizes and timeouts."""

    return _assemble_round_prompt(
        header="### SMART INDIA HACKATHON (SIH) - PHASE 3: 10x ADVANCED SOLUTIONS",
        problem_statement=problem_statement,
        round_mission=round_mission,
        arbiter_block=render_arbiter_directive_block(prev_round),
        critiques_block=render_targeted_critiques_block(prev_round, my_model_config),
        my_position_block=render_my_previous_position(my_prev, i_submitted),
        peers_text=peers_text,
        history_block="",
        injection_block=_injection_block(moderator_injection),
        schema_guide=build_schema_guide(problem_domain),
    )


# ==============================================================================
# PHASE 4: THE CONVERGENCE CRUCIBLE & SOVEREIGN MASTER DELIVERABLE
# ==============================================================================

def build_phase_4_round_prompt(
    round_id: str,
    round_number: int,
    problem_statement: str,
    my_model_config: ModelConfig,
    all_models: List[ModelConfig],
    previous_rounds: List[RoundData],
    moderator_injection: Optional[str] = None,
    problem_domain: Optional[str] = None,
) -> str:
    prev_round = previous_rounds[-1] if previous_rounds else None
    my_prev, peers_text, i_submitted = _split_prev_round(prev_round, my_model_config, detail="full")

    round_mission = """**ROUND 4.1 - CONCESSION TREATY & MASTER BLUEPRINT ASSEMBLY**
- Integrate every resolved concession into one unified engineering specification. `refined_solution`
  here is the primary source for the final deliverable, so make it complete and self-contained.
- Close out every remaining friction point listed above: state your final technical position on each.
- Then declare your genuine consensus vote and agreement percentage against the rubric. This is a
  measurement, not a courtesy: if real disagreement remains, record it and name it in
  `negatives_and_risks`. An honest DISAGREE is more valuable to this process than a polite AGREE."""

    return _assemble_round_prompt(
        header="### SMART INDIA HACKATHON (SIH) - PHASE 4: CONVERGENCE CRUCIBLE",
        problem_statement=problem_statement,
        round_mission=round_mission,
        arbiter_block=render_arbiter_directive_block(prev_round),
        critiques_block=render_targeted_critiques_block(prev_round, my_model_config),
        my_position_block=render_my_previous_position(my_prev, i_submitted),
        peers_text=peers_text,
        history_block=render_position_history(previous_rounds, my_model_config.id),
        injection_block=_injection_block(moderator_injection),
        schema_guide=build_schema_guide(problem_domain),
    )


# ==============================================================================
# ARBITER ROUND EVALUATION
# ==============================================================================

def build_arbiter_evaluation_prompt(
    problem_statement: str = "",
    round_number: int = 1,
    phase_index: int = 1,
    phase_title: str = "",
    round_responses: Optional[Dict[str, DebaterResponse]] = None,
    rounds: Optional[List[RoundData]] = None,
    models: Optional[List[ModelConfig]] = None,
    all_models: Optional[List[ModelConfig]] = None,
    phase_prompt: Optional[str] = None,
    **kwargs
) -> str:
    # Resolve round responses
    effective_responses: Dict[str, DebaterResponse] = {}
    if round_responses:
        effective_responses = round_responses
    elif rounds and len(rounds) > 0:
        target_r = next((r for r in rounds if r.round_number == round_number), rounds[-1])
        effective_responses = target_r.responses or {}

    effective_models = models or all_models or []
    debater_summaries = []

    # D6: lens excerpts were capped at 200 chars, so the arbiter scored summaries rather
    # than solutions. Budgets raised to match orchestrator.py's own [:1500] healing cap.
    LENS_BUDGET = 1200
    SOLUTION_BUDGET = 2500

    all_response_model_ids = set(effective_responses.keys())
    seen_model_ids = set()

    for m in effective_models:
        seen_model_ids.add(m.id)
        if m.id in effective_responses:
            resp = effective_responses[m.id]
            st = resp.structured
            status_tag = resp.status.upper()

            # D3: a zero-byte response must never be presented as a participant.
            if resp.status == "completed" and not (resp.raw_text or "").strip():
                debater_summaries.append(f"""### Model: {m.name} [NO SUBMISSION]
- Produced zero bytes of output. It has no position, no argument and no contribution this round.
- Assign it no credit and do not infer what it would have said.
""")
                continue

            if resp.status == "completed":
                critiques_summary = ""
                if st.critiques:
                    items = "; ".join(
                        f"vs {c.target_model_name or 'peer'}: {c.flaw_identified[:220]}"
                        for c in st.critiques[:6]
                    )
                    critiques_summary = f"\n- Critiques launched: {items}"

                concessions_summary = ""
                if st.concessions_and_defenses:
                    items = "; ".join(
                        f"{c.conceded_point[:180]} (to {c.conceded_to}) -> {c.adaptation[:180]}"
                        for c in st.concessions_and_defenses[:6]
                    )
                    concessions_summary = f"\n- Concessions / defenses: {items}"

                if st.consensus_vote is None or st.agreement_percentage is None:
                    vote_line = ("- Stated position: NONE RECORDED (the model's output could not be read as a "
                                 "structured position). Judge its argument on the content below; do not treat "
                                 "the missing vote as dissent.")
                else:
                    vote_line = f"- Stated position: {st.consensus_vote} ({st.agreement_percentage}%)"

                debater_summaries.append(f"""### Model: {m.name} [{status_tag} - {resp.elapsed_seconds:.1f}s]
{vote_line}
- Solution as it now stands: {st.refined_solution[:SOLUTION_BUDGET]}
- Architecture: {st.architect_lens[:LENS_BUDGET] if st.architect_lens else 'not separately stated'}
- Self-identified risks: {(st.critic_lens or st.critic_devil_advocate_lens or 'none stated')[:LENS_BUDGET]}
- Feasibility / cost: {(st.field_hardware_lens or st.pragmatist_feasibility_lens or 'not addressed')[:LENS_BUDGET]}
- Security / compliance: {(st.security_compliance_lens or st.security_reliability_lens or 'not addressed')[:LENS_BUDGET]}{critiques_summary}{concessions_summary}
""")
            elif resp.status in ["error", "timeout", "quarantined"]:
                error_detail = resp.error_message or "Execution timed out or was aborted"
                if (resp.raw_text or "").strip():
                    partial = f"Partial output before the failure (incomplete, may be mid-sentence): \"{resp.raw_text[:600]}\""
                else:
                    partial = "No output was produced before the failure."
                debater_summaries.append(f"""### Model: {m.name} [{status_tag} - DID NOT COMPLETE]
- Failure cause: {error_detail}
- {partial}
- This model did not validate anything this round. Assign it no credit in the consensus.
""")
        elif m.enabled:
            debater_summaries.append(f"""### Model: {m.name} [NO SUBMISSION]
- Did not return a turn in this round. No position on record.
""")

    for m_id, resp in effective_responses.items():
        if m_id not in seen_model_ids:
            st = resp.structured
            status_tag = resp.status.upper()
            vote_txt = (f"{st.consensus_vote} ({st.agreement_percentage}%)"
                        if st.consensus_vote and st.agreement_percentage is not None
                        else "no readable position")
            debater_summaries.append(f"""### Model: {resp.model_name} [{status_tag}]
- Stated position: {vote_txt}
- Notes: {st.refined_solution[:SOLUTION_BUDGET]}
""")

    summary_text = "\n".join(debater_summaries)
    arbiter_name = kwargs.get("arbiter_name") or "Master Arbiter"
    phase_prompt_block = ""
    if phase_prompt and phase_prompt.strip():
        phase_prompt_block = (
            "\n### STRATEGIC FOCUS / FOLLOW-UP REQUIREMENTS FOR THIS PHASE\n"
            + _tagged("phase_requirements", phase_prompt.strip()) + "\n"
        )

    # P13: phase_title is NOT interpolated into the JSON example below. A title
    # containing a quote or brace would corrupt the contract. It is passed as prose
    # and the example uses a static placeholder.
    return f"""You are the Master Arbiter ({arbiter_name}) of this Smart India Hackathon (SIH) deliberation.

EVALUATION DIRECTIVE:
Judge strictly on the record below. Weigh the arguments that were actually made, the critiques that
landed, and the concessions that were earned. Where a model did not submit, record that as a
non-participation - do not salvage, reconstruct or credit an argument it never made. Do not describe
a retry, key rotation or format repair as an intellectual contribution. Your consensus number must be
a calibrated measurement of genuine technical agreement, not a summary of goodwill.

**Problem statement:**
{_tagged("problem_statement", problem_statement)}
{phase_prompt_block}
**Phase {phase_index}:** {phase_title}
**Round number:** {round_number}

### ROUND PARTICIPANT SUBMISSIONS
{summary_text}

### YOUR TASK
Assess alignment, measure the consensus score, separate resolved friction from open friction, and
write an authoritative synthesis. Then set the directive that the next round must answer - it will be
delivered verbatim to every debater, so make it specific and demanding.

Return ONLY this JSON object inside a ```json fence. Angle-bracket text is an instruction: never copy
it literally, and never copy an example number.

```json
{{
  "round_number": {round_number},
  "phase_index": {phase_index},
  "phase_title": "<echo the phase title given above>",
  "consensus_score": "<integer 0-100 measuring genuine technical agreement across the submissions that actually landed. Rubric: 90-100 = one design, no material dispute left; 70-89 = agreed shape with named open trade-offs; 40-69 = competing designs still on the table; 0-39 = no shared architecture. Non-participating models neither raise nor lower this - judge the submissions on the record.>",
  "is_unanimous": "<true only if every model that submitted explicitly agreed and no OPEN friction point remains; otherwise false>",
  "executive_synthesis": "<2-3 paragraphs: where the submissions converge, the specific technical breakthroughs of this round and who authored them, which critiques landed and which were successfully rebutted, and what remains disputed. Quote or paraphrase specific submissions. Name non-participating models plainly as non-participating.>",
  "friction_points": [
    {{
      "issue": "<the specific technical conflict, stated so a third party could adjudicate it>",
      "raised_by": "<model name>",
      "challenged_by": "<model name>",
      "status": "<OPEN | RESOLVED | CONCEDED>",
      "resolution_notes": "<what the record establishes so far - the arithmetic, evidence or compromise>"
    }}
  ],
  "next_round_challenge": "<the single most valuable directive for the next round: a specific technical question or decision the debaters must resolve. Be concrete enough that a model can act on it without further context.>"
}}
```"""


# ==============================================================================
# FINAL SOVEREIGN DELIVERABLE
# ==============================================================================

def _collect_source_ledger(research_dossier: Optional[Any]) -> Tuple[str, int]:
    """Renders the tagged source list the report is permitted to cite from (D2)."""
    if not research_dossier:
        return "", 0

    groups = [
        ("Fact-checks", getattr(research_dossier, "stage_1_fact_checks", []) or []),
        ("Academic papers", getattr(research_dossier, "stage_2_academic_papers", []) or []),
        ("Field / feasibility benchmarks", getattr(research_dossier, "stage_3_field_benchmarks", []) or []),
    ]

    lines: List[str] = []
    count = 0
    for label, items in groups:
        rendered = []
        for it in items:
            tag = (getattr(it, "tag", "") or "").strip()
            title = (getattr(it, "title", "") or "").strip()
            if not tag and not title:
                continue
            count += 1
            year = getattr(it, "year", None)
            url = (getattr(it, "url", "") or "").strip()
            summary = (getattr(it, "summary", "") or "").strip()
            rendered.append(
                f"- [{tag}] {title}"
                + (f" ({year})" if year else "")
                + (f"\n  URL: {url}" if url else "")
                + (f"\n  Finding: {summary[:400]}" if summary else "")
            )
        if rendered:
            lines.append(f"**{label}:**\n" + "\n".join(rendered))

    return "\n\n".join(lines), count


def build_final_markdown_report_prompt(
    problem_statement: str = "",
    phase_title: str = "Master Consensus Solution",
    all_rounds: Optional[List[RoundData]] = None,
    rounds: Optional[List[RoundData]] = None,
    models: Optional[List[ModelConfig]] = None,
    all_models: Optional[List[ModelConfig]] = None,
    ministry_domain: str = "Smart India Hackathon",
    phase_prompt: Optional[str] = None,
    research_dossier: Optional[Any] = None,
    problem_domain: Optional[str] = None,
    **kwargs
) -> str:
    """
    D1 - this prompt previously rendered each model's entire contribution as `sol[:200]`
    and each arbiter synthesis as `[:250]`. On the real 397de6ca run that delivered 6,804
    of 972,567 produced characters (99.30% discarded) and the arbiter filled the gap with
    generic content and plausible invention. The context is now built from the dense,
    high-value artifacts instead: full final solutions, the complete friction ledger, the
    resolved critique/concession record, and every round's arbiter synthesis.
    """
    effective_rounds = all_rounds if all_rounds is not None else (rounds or [])
    effective_models = models if models is not None else (all_models or [])
    domain = _normalize_domain(problem_domain)

    # --- Participation ledger (D3) -------------------------------------------------
    substantive: Dict[str, Dict[str, Any]] = {}
    non_participants: Dict[str, str] = {}

    for r in effective_rounds:
        for m_id, resp in r.responses.items():
            has_content = bool((resp.raw_text or "").strip()) and bool(
                (resp.structured.refined_solution or resp.structured.architect_lens or "").strip()
            )
            if resp.status == "completed" and has_content:
                rec = substantive.setdefault(m_id, {"name": resp.model_name, "rounds": 0, "last": None, "vote": None, "pct": None})
                rec["rounds"] += 1
                rec["last"] = resp
                if resp.structured.consensus_vote is not None:
                    rec["vote"] = resp.structured.consensus_vote
                    rec["pct"] = resp.structured.agreement_percentage
            else:
                if m_id not in substantive:
                    reason = resp.error_message or (
                        "returned zero usable output" if resp.status == "completed" else f"status {resp.status}"
                    )
                    non_participants[m_id] = f"{resp.model_name} - {reason}"

    for m_id in list(non_participants.keys()):
        if m_id in substantive:
            non_participants.pop(m_id, None)

    # --- Final converged proposals, in full ----------------------------------------
    final_solutions: List[str] = []
    if effective_rounds:
        ranked = sorted(
            substantive.values(),
            key=lambda rec: (rec["pct"] if rec["pct"] is not None else -1),
            reverse=True,
        )
        for rec in ranked[:5]:
            resp = rec["last"]
            if not resp:
                continue
            st = resp.structured
            block = [f"### Final converged proposal - {resp.model_name}"]
            if st.refined_solution:
                block.append(st.refined_solution)
            feas = st.field_hardware_lens or st.pragmatist_feasibility_lens
            if feas:
                block.append(f"\n**Its feasibility / cost position:**\n{feas}")
            sec = st.security_compliance_lens or st.security_reliability_lens
            if sec:
                block.append(f"\n**Its security / compliance position:**\n{sec}")
            if st.positives_of_approach:
                block.append("\n**Claimed strengths:** " + "; ".join(st.positives_of_approach))
            if st.negatives_and_risks:
                block.append("\n**Admitted residual risks:** " + "; ".join(st.negatives_and_risks))
            final_solutions.append("\n".join(block))

    # --- Round-by-round arbiter syntheses, in full ---------------------------------
    synthesis_blocks: List[str] = []
    for r in effective_rounds:
        if not r.arbiter_eval:
            continue
        ae = r.arbiter_eval
        label = r.pass_or_round_title or f"Round {r.round_number}"
        chunk = [f"### {label} - measured consensus {ae.consensus_score}%"]
        if ae.executive_synthesis:
            chunk.append(ae.executive_synthesis)
        synthesis_blocks.append("\n".join(chunk))

    # --- Friction ledger: the debate's actual outcome ------------------------------
    friction_rows: List[str] = []
    seen_issues = set()
    for r in effective_rounds:
        if not r.arbiter_eval:
            continue
        for fp in r.arbiter_eval.friction_points:
            key = (fp.issue or "").strip().lower()[:120]
            if not key or key in seen_issues:
                continue
            seen_issues.add(key)
            friction_rows.append(
                f"- **{fp.issue}** [{fp.status}]\n"
                f"  - raised by {fp.raised_by or 'unattributed'}, challenged by {fp.challenged_by or 'unattributed'}\n"
                f"  - outcome on the record: {fp.resolution_notes or 'not recorded'}"
            )

    # --- Critique / concession record ----------------------------------------------
    debate_rows: List[str] = []
    for r in effective_rounds:
        label = r.pass_or_round_title or f"Round {r.round_number}"
        for m_id, resp in r.responses.items():
            st = resp.structured
            if resp.status != "completed" or not st:
                continue
            for c in st.critiques[:4]:
                if not (c.flaw_identified or "").strip():
                    continue
                debate_rows.append(
                    f"- [{label}] {resp.model_name} challenged {c.target_model_name or 'a peer'}: "
                    f"{c.flaw_identified[:300]} | their argument: {c.counter_argument[:300]}"
                )
            for cd in st.concessions_and_defenses[:4]:
                if not (cd.conceded_point or "").strip():
                    continue
                debate_rows.append(
                    f"- [{label}] {resp.model_name} -> {cd.conceded_to or 'peer'}: "
                    f"{cd.conceded_point[:250]} | adaptation: {cd.adaptation[:250]}"
                )

    # --- Research grounding (D2) ----------------------------------------------------
    ledger_text, source_count = _collect_source_ledger(research_dossier)
    if source_count > 0:
        research_block = (
            "### VERIFIED RESEARCH SOURCE LEDGER - THE ONLY SOURCES YOU MAY CITE\n"
            "Cite these using their exact bracketed tags, and only these. Every citation in your "
            "document must resolve to an entry in this list.\n\n" + ledger_text
        )
        citation_rule = (
            "CITATION RULE: You may cite ONLY the tagged sources in the Verified Research Source Ledger "
            "above, using their exact tags. You MUST NOT introduce any other paper title, arXiv "
            "identifier, DOI, journal, conference or author name. Any citation that does not resolve to "
            "the ledger will be stripped before publication."
        )
        research_section = (
            f"`## 10. Research Grounding & Source Ledger` - map each key design decision to the specific "
            f"ledger tag that supports it, and reproduce the ledger as a markdown table "
            f"(Tag | Title | Year | Relevance). Only the {source_count} ledger sources may appear."
        )
    else:
        research_block = (
            "### VERIFIED RESEARCH SOURCE LEDGER\n"
            "EMPTY. No external research was retrieved for this run."
        )
        citation_rule = (
            "CITATION RULE - ABSOLUTE: No research sources were retrieved for this run. You MUST NOT "
            "cite any paper, arXiv identifier, DOI, journal, conference, author, standard number or "
            "bracketed source tag anywhere in this document. Do not write [Source 1], [Paper 2] or any "
            "similar marker. Where you would have cited evidence, write 'unverified engineering "
            "assumption' instead. A fabricated academic citation in a Ministry-facing submission is "
            "disqualification-class misconduct, and this instruction overrides any habit of citing."
        )
        research_section = (
            "`## 10. Research Grounding & Evidence Status` - state plainly: 'No external research "
            "sources were retrieved for this run. The specifications below rest on the participating "
            "models' engineering judgement and are marked as unverified assumptions where they depend "
            "on external figures.' List which specific figures in this document would need external "
            "verification. Cite nothing."
        )

    # --- Sign-off spec (D3) ---------------------------------------------------------
    if substantive:
        ratifier_lines = "\n".join(
            f"- {rec['name']} - submitted in {rec['rounds']} round(s); final recorded position: "
            + (f"{rec['vote']} ({rec['pct']}%)" if rec["vote"] else "no readable vote")
            for rec in substantive.values()
        )
    else:
        ratifier_lines = "- (none)"
    non_participant_lines = "\n".join(f"- {v}" for v in non_participants.values()) or "- (none)"

    all_agree = bool(substantive) and all(rec["vote"] == "AGREE" for rec in substantive.values())
    unanimity_note = (
        "Every model that submitted recorded AGREE, so you may describe the ratification as unanimous "
        "among participating models (and must still say how many did not participate)."
        if all_agree else
        "Ratification was NOT unanimous. You must NOT use the words 'unanimous' or 'unanimously'. "
        "State the actual split and name the reservations."
    )

    phase_prompt_block = ""
    if phase_prompt and phase_prompt.strip():
        phase_prompt_block = (
            "\n### STRATEGIC FOCUS / FOLLOW-UP REQUIREMENTS FOR THIS PHASE\n"
            + _tagged("phase_requirements", phase_prompt.strip()) + "\n"
        )

    model_names = ", ".join(rec["name"] for rec in substantive.values()) or "none"

    # Assemble the evidence body.
    evidence: List[str] = []
    if final_solutions:
        evidence.append("## FINAL CONVERGED PROPOSALS (full text - this is your primary source)\n\n"
                        + "\n\n".join(final_solutions))
    if synthesis_blocks:
        evidence.append("## ARBITER SYNTHESIS OF EVERY ROUND\n\n" + "\n\n".join(synthesis_blocks))
    if friction_rows:
        evidence.append("## TECHNICAL FRICTION LEDGER (what was disputed and how it ended)\n\n"
                        + "\n".join(friction_rows))
    if debate_rows:
        evidence.append("## CROSS-CRITIQUE AND CONCESSION RECORD\n\n" + "\n".join(debate_rows[:120]))
    evidence.append("## PARTICIPATION RECORD (authoritative - do not contradict it)\n\n"
                    f"**Models that submitted substantive content:**\n{ratifier_lines}\n\n"
                    f"**Models that did NOT participate substantively:**\n{non_participant_lines}\n\n"
                    f"{unanimity_note}")
    evidence.append(research_block)

    evidence_text = "\n\n".join(evidence)

    return f"""You are the Master Arbiter, synthesising the definitive Sovereign SIH Master Consensus Deliverable for this problem statement.

**Problem statement:**
{_tagged("problem_statement", problem_statement)}
{phase_prompt_block}
**Domain / Ministry:** {ministry_domain}
**Problem domain classification:** {domain}
**Models that contributed substantively:** {model_names}

{evidence_text}

### YOUR OBJECTIVE
Write the authoritative, pitch-winning Sovereign SIH Master Consensus Deliverable in clean
GitHub-flavored Markdown, synthesised from the evidence above.

### OUTPUT FORMAT - ABSOLUTE
- Emit raw Markdown text and nothing else.
- Do NOT wrap the document in a JSON object. Do NOT put it inside a `consensus_document` field.
- Do NOT wrap it in a ```markdown or ```json fence.
- The very first character of your reply must be `#`.

### HONESTY CONSTRAINTS - ABSOLUTE
- {citation_rule}
- Credit only the contributions recorded in the evidence above, and attribute each to the model that
  actually made it. Never credit a model listed as non-participating.
- Do not present a retry, key rotation, timeout or format repair as an intellectual contribution.
- Where the deliberation did not settle a question, say so and give the options with their trade-offs.
  An honest open question is stronger than a confident invention.
- Every number you state must trace to the evidence above or be explicitly labelled an estimate.

{NO_CODE_RULE}

### REQUIRED STRUCTURE - use exactly these sections, in this order
1. `# SIH Master Consensus Deliverable: {phase_title}`
2. `## 1. Executive Summary & 1-Minute Innovation Hook` - the unified breakthrough, and why it wins.
3. `## 2. End-to-End System Architecture & Data Flow` - component hierarchy, tier boundaries,
   network topology, and offline/degraded-mode behaviour. Include an ASCII or mermaid-style block
   diagram described in text.
4. `## 3. Core Algorithms, AI Pipeline & Performance Budget` - named algorithms, complexity bounds,
   model architectures, and the measured or estimated latency/throughput budget.
5. `## 4. {_budget_section_title(domain)}` - a markdown table with real line items and figures,
   totals, and the scale assumption behind them.
6. `## 5. Comparative Debate Matrix` - a markdown table of the significant technical disputes:
   Issue | Position A (model) | Position B (model) | Evidence that decided it | Outcome. Build this
   from the friction ledger and cross-critique record above, not from imagination.
7. `## 6. Pre-Empted Risks & Mitigations` - a markdown table: Risk | Likelihood | Impact |
   Mitigation designed in | Residual exposure. Draw from the admitted risks and the red-team record.
8. `## 7. Fault-Tolerance, Chaos Recovery & High Availability` - degradation ladder, power/network
   loss handling, store-and-forward buffering, recovery objectives.
9. `## 8. Statutory & Ministry Standards Compliance` - only the Indian standards that genuinely
   apply, each with the specific obligation it imposes on this design.
10. `## 9. Implementation Action Plan` - phased milestones with a realistic timeline, team roles,
    dependencies, and the demo/PoC scope for the hackathon itself.
11. {research_section}
12. `## 11. Multi-Model Consensus Ratification` - list ONLY the models recorded above as substantive
    contributors, each with the specific contribution the evidence attributes to them. Then a
    separate subsection `### Non-participating nodes` listing the models that did not submit and why.
    Invent nothing here.

Begin now with the `#` heading."""
