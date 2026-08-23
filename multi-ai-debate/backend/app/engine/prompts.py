import json
from typing import List, Dict, Optional
from app.schemas import ModelConfig, RoundData, WorkspacePhase

NO_CODE_RULE = """
⚠️ STRICT ENFORCEMENT: DO NOT WRITE ANY CODE, SCRIPT SNIPPETS, OR PSEUDOCODE.
Focus exclusively on high-level system architecture, conceptual mechanisms, failure modes, data flows, operational viability, trade-offs, and strategic logic.
"""

def build_system_prompt_for_debater(model_name: str, ministry_domain: str) -> str:
    return f"""You are '{model_name}', a world-class Grandmaster Software Architect and Chief Systems Strategist competing in the Smart India Hackathon (SIH) for domain '{ministry_domain}'.

Your goal is to use your full, unconstrained intelligence across ALL critical cognitive personas to debate, challenge, stress-test, and collaboratively construct a winning solution and design artifacts for the problem statement.

You must simultaneously apply these 4 cognitive lenses:
1. 🏛️ Lead Architect: High-level vision, system decomposition, paradigms, workflow.
2. 😈 Adversarial Critic / Devil's Advocate: Blind spots, hidden failure modes, fragile assumptions, scaling traps.
3. 🛡️ Security & Reliability Analyst: Data integrity, resilience, edge cases, single points of failure.
4. ⚙️ Pragmatic Implementer: Cost, friction, operational trade-offs, real-world deployment viability.

{NO_CODE_RULE}

You must return your response in clean JSON format matching the schema requested."""

def build_round_1_prompt(
    problem_statement: str,
    ministry_domain: str,
    phase_prompt: str = "",
    prior_phases: List[WorkspacePhase] = []
) -> str:
    prior_context = ""
    if prior_phases:
        prior_context = "### PREVIOUSLY AGREED CONSENSUS DELIVERABLES IN THIS WORKSPACE:\n"
        for p in prior_phases:
            prior_context += f"\n--- Phase {p.phase_index} Verdict ({p.phase_title}) ---\n{p.verdict_markdown[:1500]}...\n"

    active_goal = phase_prompt if phase_prompt else "Analyze the problem statement from all 4 cognitive lenses and propose your comprehensive solution architecture."

    return f"""### SMART INDIA HACKATHON (SIH) PROBLEM STATEMENT
**Domain / Ministry:** {ministry_domain}
**Core Problem Statement:**
\"\"\"{problem_statement}\"\"\"

{prior_context}

### CURRENT PHASE OBJECTIVE:
{active_goal}

{NO_CODE_RULE}

Return your output as a valid JSON object with the following structure:
```json
{{
  "architect_lens": "Your structural vision, primary conceptual components, and data workflow (NO CODE).",
  "critic_devil_advocate_lens": "Identified edge cases, subtle failure modes, and fragile assumptions.",
  "security_reliability_lens": "Security posture, fault tolerance, offline/fallback resilience, and integrity mechanisms.",
  "pragmatist_feasibility_lens": "Cost considerations, operational feasibility, and trade-offs.",
  "refined_solution": "Comprehensive overview of your proposed solution / specification artifact.",
  "positives_of_approach": [
    "Key advantage 1",
    "Key advantage 2"
  ],
  "negatives_and_risks": [
    "Key challenge / risk 1",
    "Key challenge / risk 2"
  ],
  "consensus_vote": "DISAGREE",
  "agreement_percentage": 50
}}
```"""

def build_round_n_prompt(
    round_number: int,
    problem_statement: str,
    my_model_config: ModelConfig,
    all_models: List[ModelConfig],
    previous_rounds: List[RoundData],
    moderator_injection: str = "",
    phase_prompt: str = ""
) -> str:
    prev_round = previous_rounds[-1]
    peers_transcripts = []
    my_prev_response = ""

    for m_id, resp in prev_round.responses.items():
        if m_id == my_model_config.id:
            my_prev_response = resp.structured.refined_solution or resp.raw_text
        else:
            m_name = resp.model_name
            peers_transcripts.append(f"""---
### Peer Proposal from: [{m_name}] (Model ID: {m_id})
- **Architect View:** {resp.structured.architect_lens}
- **Critic View:** {resp.structured.critic_devil_advocate_lens}
- **Security View:** {resp.structured.security_reliability_lens}
- **Pragmatist View:** {resp.structured.pragmatist_feasibility_lens}
- **Proposed Solution:** {resp.structured.refined_solution}
- **Claimed Positives:** {json.dumps(resp.structured.positives_of_approach)}
- **Identified Negatives:** {json.dumps(resp.structured.negatives_and_risks)}
""")

    peers_text = "\n".join(peers_transcripts)
    
    injection_block = ""
    if moderator_injection:
        injection_block = f"""
### 🔔 MODERATOR INTERVENTION & NEW CONSTRAINTS:
\"{moderator_injection}\"
You MUST incorporate and address this moderator direction into your updated response.
"""

    active_prompt_desc = f"Active Goal: {phase_prompt}" if phase_prompt else "Universal Cross-Critique, Concessions & Hardening"

    return f"""### SMART INDIA HACKATHON (SIH) DEBATE - ROUND {round_number}
**Problem Statement:**
\"\"\"{problem_statement}\"\"\"
**{active_prompt_desc}**

### YOUR PREVIOUS POSITION IN ROUND {round_number - 1}:
{my_prev_response}

### PEER PROPOSALS & COUNTERS IN ROUND {round_number - 1}:
{peers_text}
{injection_block}

### YOUR OBJECTIVE FOR ROUND {round_number}:
1. **Universal Cross-Critique**: Listen to each peer's points and formulate direct, rigorous counter-arguments against their specific flaws, blind spots, or unrealistic assumptions.
2. **Concessions & Defenses**: Review criticisms against your own ideas. Concede valid points and defend strong positions with technical logic.
3. **Harmonized Refinement**: Update your deliverable to absorb the best ideas from all models while eliminating weaknesses.
4. **Consensus Vote**: Rate your alignment with the emerging collective direction (`AGREE`, `DISAGREE`, or `NEEDS_REFINEMENT`) and estimate your agreement percentage (0% to 100%).

{NO_CODE_RULE}

Return your output as a valid JSON object matching this exact schema:
```json
{{
  "architect_lens": "Updated architectural perspectives incorporating peer insights.",
  "critic_devil_advocate_lens": "Remaining subtle risks or stress points in the collective direction.",
  "security_reliability_lens": "Hardened reliability & fallback consensus.",
  "pragmatist_feasibility_lens": "Cost and operational viability consensus.",
  "critiques": [
    {{
      "target_model_id": "ID of peer model being critiqued",
      "target_model_name": "Name of peer model",
      "flaw_identified": "Specific vulnerability, flaw, or unrealistic assumption",
      "counter_argument": "Rigorous technical counter-argument explaining why this fails"
    }}
  ],
  "concessions_and_defenses": [
    {{
      "conceded_point": "Point conceded or defended",
      "conceded_to": "Peer model name",
      "adaptation": "How you have updated your solution or defended it"
    }}
  ],
  "refined_solution": "Your battle-tested, refined complete conceptual deliverable for SIH.",
  "positives_of_approach": [
    "Refined key positive 1",
    "Refined key positive 2"
  ],
  "negatives_and_risks": [
    "Remaining trade-off 1",
    "Remaining trade-off 2"
  ],
  "consensus_vote": "AGREE or DISAGREE or NEEDS_REFINEMENT",
  "agreement_percentage": 90
}}
```"""

def build_arbiter_evaluation_prompt(
    round_number: int,
    problem_statement: str,
    rounds: List[RoundData],
    phase_prompt: str = ""
) -> str:
    current_round = rounds[-1]
    responses_text = []
    
    for m_id, resp in current_round.responses.items():
        votes = resp.structured.consensus_vote
        pct = resp.structured.agreement_percentage
        responses_text.append(f"""
### Debater: {resp.model_name}
- Vote: {votes} ({pct}% Agreement)
- Refined Solution: {resp.structured.refined_solution}
- Critiques Launched: {json.dumps([c.model_dump() for c in resp.structured.critiques])}
- Concessions/Defenses: {json.dumps([cd.model_dump() for cd in resp.structured.concessions_and_defenses])}
- Positives: {json.dumps(resp.structured.positives_of_approach)}
- Negatives: {json.dumps(resp.structured.negatives_and_risks)}
""")

    all_resp_block = "\n".join(responses_text)

    return f"""You are the Master Arbiter & Chief Jury for the Smart India Hackathon (SIH) Debate Arena.

**Problem Statement:**
\"\"\"{problem_statement}\"\"\"
**Current Phase Goal:** {phase_prompt or "Solution Consensus"}

### DEBATE TRANSCRIPT FOR ROUND {round_number}:
{all_resp_block}

### YOUR OBJECTIVE:
Evaluate the degree of convergence, measure consensus percentage (0 to 100), identify resolved vs open friction points, and determine if unanimous consensus (100% agreement on all major architectural trade-offs) has been reached.

{NO_CODE_RULE}

Return a valid JSON object matching:
```json
{{
  "round_number": {round_number},
  "consensus_score": 85,
  "is_unanimous": false,
  "executive_synthesis": "Synthesis of where all models currently stand and key points of agreement.",
  "friction_points": [
    {{
      "issue": "Specific point of contention",
      "raised_by": "Model Name",
      "challenged_by": "Model Name",
      "status": "OPEN or RESOLVED or CONCEDED",
      "resolution_notes": "How this was resolved or why it remains contested"
    }}
  ],
  "next_round_challenge": "If not unanimous, the specific core question all debaters must resolve in the next round."
}}
```"""

def build_final_markdown_report_prompt(
    problem_statement: str,
    ministry_domain: str,
    total_rounds: int,
    rounds: List[RoundData],
    all_models: List[ModelConfig],
    phase_title: str = "Master Consensus Solution",
    phase_prompt: str = ""
) -> str:
    summary_history = []
    for r in rounds:
        r_num = r.round_number
        responses_brief = []
        for m_id, resp in r.responses.items():
            responses_brief.append(f"  * {resp.model_name}: {resp.structured.refined_solution[:250]}...")
        summary_history.append(f"Round {r_num}:\n" + "\n".join(responses_brief))

    history_text = "\n\n".join(summary_history)
    model_names = ", ".join([m.name for m in all_models])

    return f"""You are the Grand Jury & Chief Architect of the Smart India Hackathon (SIH).

The multi-model debate for Phase: **{phase_title}** has completed after {total_rounds} rounds.

**Problem Statement:**
\"\"\"{problem_statement}\"\"\"
**Domain / Ministry:** {ministry_domain}
**Phase Focus / Prompt:** {phase_prompt or "Comprehensive Solution & Architecture"}
**Participating AIs:** {model_names}

### DEBATE HISTORY SUMMARY:
{history_text}

### OBJECTIVE:
Generate an authoritative, definitive, Grand-Finale winning **Consensus Deliverable Document** in clean GitHub-flavored Markdown specifically fulfilling the Phase Focus.

{NO_CODE_RULE}

Include these key sections:
1. `# 🏆 SIH Consensus Deliverable: {phase_title}`
2. `## 1. Executive Summary & Verdict` (Unified conclusion all models agreed upon).
3. `## 2. In-Depth Technical Specification / Architecture Blueprint` (Conceptual mechanisms, component decomposition, data flows without code).
4. `## 3. Positives & Negatives Trade-Off Matrix` (Detailed breakdown of **Positives (Pros)** and **Negatives (Cons / Risks)** for each approach considered).
5. `## 4. Friction Points & Resolution Log` (Table of debated challenges and consensus resolutions).
6. `## 5. Deployment Feasibility & Ground Realities` (Resilience, scalability, offline tolerance, and operational viability).
7. `## 6. Official Unanimous Sign-Off Certificate` (Confirmation from each debater model).

Generate ONLY the pure Markdown content."""
