import json
from typing import List, Dict, Optional
from app.schemas import ModelConfig, RoundData, WorkspacePhase, DebaterResponse

NO_CODE_RULE = """
⚠️ STRICT ENFORCEMENT: DO NOT WRITE ANY CODE, SCRIPT SNIPPETS, OR PSEUDOCODE.
Focus exclusively on high-level system architecture, conceptual mechanisms, failure modes, data flows, operational viability, hardware component selection, and strategic logic.
"""

SCHEMA_GUIDE = """
Return your output as a valid JSON object matching this schema. You may include a `<deliberation_scratchpad>` before the JSON:
```json
{
  "deliberation_scratchpad": "Unconstrained step-by-step reasoning, mathematical stress-testing, and edge-case exploration...",
  "architect_lens": "System structure, data pipelines, and workflow.",
  "critic_lens": "Identified edge cases, failure modes, and fragile assumptions.",
  "field_hardware_lens": "Hardware ICs, microcontrollers, power budget, and itemized BOM in Indian Rupees (₹).",
  "security_compliance_lens": "Tamper-proofing, fault tolerance, and Indian standards compliance (ISRO, RDSO, NDMA).",
  "critiques": [
    {
      "target_model_id": "peer_model_id",
      "target_model_name": "Peer Model Name",
      "flaw_identified": "Specific vulnerability or false assumption",
      "counter_argument": "Rigorous technical counter-argument with citation"
    }
  ],
  "concessions_and_defenses": [
    {
      "conceded_point": "Point conceded or defended",
      "conceded_to": "Peer Model Name",
      "adaptation": "How solution was updated or defended"
    }
  ],
  "refined_solution": "Complete, hardened conceptual solution.",
  "positives_of_approach": ["Advantage 1", "Advantage 2"],
  "negatives_and_risks": ["Remaining challenge 1", "Remaining challenge 2"],
  "autonomous_research_calls": [
    {
      "stage": "fact_check",
      "target_engine": "tavily_web",
      "query_purpose": "Verify exact chip standby power",
      "search_query": "STM32WLE5CC deep sleep current microamps"
    },
    {
      "stage": "frontier_academic",
      "target_engine": "openalex_arxiv",
      "query_purpose": "Find SOTA edge TinyML anomaly filters",
      "search_query": "TinyML vibration anomaly detection INT8 STM32"
    }
  ],
  "consensus_vote": "AGREE or DISAGREE or NEEDS_REFINEMENT",
  "agreement_percentage": 75
}
```
"""

def build_system_prompt_for_debater(model_name: str, ministry_domain: str) -> str:
    return f"""You are '{model_name}', a world-class Grandmaster Software & Hardware Systems Architect competing in the Smart India Hackathon (SIH) for domain '{ministry_domain}'.

Your goal is to use your full, unconstrained intelligence across ALL critical cognitive personas to debate, challenge, stress-test, and collaboratively construct a winning sovereign deliverable for the problem statement.

You must simultaneously apply these 4 cognitive lenses:
1. 🏛️ Lead Architect: High-level vision, system decomposition, paradigms, workflow.
2. 😈 Murphy's Law Red-Team Critic: Spotting hidden race conditions, single points of failure, unfeasible bandwidth assumptions.
3. ⚙️ Frugal Field & BOM Engineer: Grounded in 45°C Indian summer, dust, battery discharge curves, and itemized ₹ BOM.
4. 🛡️ Fort Knox Security & Standards Officer: Physical tampering, offline FIFO ring-buffers, compliance with Indian statutory norms (ISRO Bhuvan, RDSO, NDMA).

🌐 GROUNDED CITATION PROTOCOL:
When a Live Research Dossier is attached, cite specific papers and sources using inline tags (e.g. `[Paper 1]`, `[Fact-Check 2]`, `[Feasibility 1]`) to substantiate all specs and component selections.

{NO_CODE_RULE}"""

# ==============================================================================
# PHASE 1: MULTI-PERSONA GENESIS (Internal 4-Pass Foundation)
# ==============================================================================

def build_phase_1_pass_prompt(
    pass_id: str,
    problem_statement: str,
    ministry_domain: str,
    my_prior_passes: Dict[str, str],
    prior_phases: List[WorkspacePhase] = []
) -> str:
    prior_context = ""
    if prior_phases:
        prior_context = "### PREVIOUSLY AGREED CONSENSUS DELIVERABLES IN THIS WORKSPACE:\n"
        for p in prior_phases:
            prior_context += f"\n--- Phase {p.phase_index} Verdict ({p.phase_title}) ---\n{p.verdict_markdown[:1500]}...\n"

    prior_pass_text = ""
    if my_prior_passes:
        prior_pass_text = "### YOUR PREVIOUS INTERNAL PASSES IN PHASE 1:\n"
        for pid, pcontent in my_prior_passes.items():
            prior_pass_text += f"\n--- Output of Pass {pid} ---\n{pcontent[:2000]}\n"

    mission_desc = ""
    if pass_id == "1.1":
        mission_desc = """🎯 **PASS 1.1: 🏛️ ARCHITECT GENESIS (Unconstrained Theoretical Maximum)**
- Formulate your 100x theoretical maximum architectural vision for the SIH problem statement.
- Define the end-to-end conceptual data pipelines, ingestion topologies, and system decomposition.
- Outline the initial multi-tier workflow from edge sensors to cloud dashboard."""
    elif pass_id == "1.2":
        mission_desc = """🎯 **PASS 1.2: 😈 MURPHY'S LAW INVERSION (Ruthless Self-Assassination)**
- Attack your own Pass 1.1 architecture with zero mercy.
- Identify hidden race conditions, single points of failure, edge-case bottlenecks, and unrealistic bandwidth/storage assumptions.
- Where will this system break down under 1000x load or severe signal degradation?"""
    elif pass_id == "1.3":
        mission_desc = """🎯 **PASS 1.3: ⚙️ FRUGAL FIELD & BOM REALITY (Indian Terrain Grounding)**
- Re-engineer the system for extreme Indian conditions: 45°C ambient heat, dust, erratic grid power, 2G/intermittent connectivity.
- Specify exact real-world hardware ICs (MCUs, LoRa/GSM modems, power management ICs).
- Itemize a realistic Bill of Materials (BOM) in Indian Rupees (₹) for a commercial-grade deployment."""
    elif pass_id == "1.4":
        mission_desc = """🎯 **PASS 1.4: 🛡️ FORT KNOX SECURITY & STATUTORY COMPLIANCE**
- Hardening against physical tampering, man-in-the-middle attacks, and memory corruption.
- Implement offline-first FIFO ring buffers with store-and-forward telemetry.
- Enforce full statutory compliance with Indian Ministry standards (ISRO Bhuvan geospatial protocols, RDSO railway specs, NDMA disaster guidelines)."""

    return f"""### SMART INDIA HACKATHON (SIH) — PHASE 1: MULTI-PERSONA GENESIS
**Domain / Ministry:** {ministry_domain}
**Core Problem Statement:**
\"\"\"{problem_statement}\"\"\"

{prior_context}
{prior_pass_text}

### CURRENT COGNITIVE MISSION:
{mission_desc}

{NO_CODE_RULE}
{SCHEMA_GUIDE}"""

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
    moderator_injection: str = ""
) -> str:
    prev_round = previous_rounds[-1] if previous_rounds else None
    peers_transcripts = []
    my_prev_response = ""

    if prev_round:
        for m_id, resp in prev_round.responses.items():
            if m_id == my_model_config.id:
                my_prev_response = resp.structured.refined_solution or resp.raw_text
            else:
                m_name = resp.model_name
                peers_transcripts.append(f"""---
### Peer Proposal from: [{m_name}] (Model ID: {m_id})
- **Architect Lens:** {resp.structured.architect_lens}
- **Critic Lens:** {resp.structured.critic_lens or resp.structured.critic_devil_advocate_lens}
- **Field & BOM Lens:** {resp.structured.field_hardware_lens or resp.structured.pragmatist_feasibility_lens}
- **Security Lens:** {resp.structured.security_compliance_lens or resp.structured.security_reliability_lens}
- **Proposed Solution:** {resp.structured.refined_solution}
- **Claimed Positives:** {json.dumps(resp.structured.positives_of_approach)}
- **Identified Risks:** {json.dumps(resp.structured.negatives_and_risks)}
""")

    peers_text = "\n".join(peers_transcripts)
    
    injection_block = ""
    if moderator_injection:
        injection_block = f"""
### 🔔 MODERATOR INTERVENTION & NEW CONSTRAINTS:
\"{moderator_injection}\"
You MUST incorporate and address this moderator direction into your updated response.
"""

    round_mission = ""
    if round_id == "2.1":
        round_mission = """🎯 **ROUND 2.1: OPENING CROSS-EXAMINATION & FLAW HUNTING**
- Scrutinize the Phase 1 battle dossiers of all peer models.
- Attack unrealistic bandwidth assumptions, naive pricing, power-draw traps, and theoretical fallacies.
- Zero politeness: Name specific peer models and formulate rigorous counter-arguments."""
    elif round_id == "2.2":
        round_mission = """🎯 **ROUND 2.2: DEFENSE, REBUTTAL & COUNTER-ATTACK**
- Defend your architectural choices against peer attacks using concrete technical math and research citations.
- If a peer's critique was based on faulty assumptions, expose their error.
- If a peer identified a genuine flaw, concede gracefully and demonstrate your architectural adaptation."""
    elif round_id == "2.3":
        round_mission = """🎯 **ROUND 2.3: FINAL CLOSING CRITIQUE & FATAL FLAW SCRUTINY**
- Conduct the jury-grade test: Which peer defenses held up vs. which collapsed?
- Lock in the definitive list of **Verified Fatal Vulnerabilities** that ANY viable system MUST fix.
- Prepare the ground for Phase 3 engineering solutions."""

    return f"""### SMART INDIA HACKATHON (SIH) — PHASE 2: ADVERSARIAL CRUCIBLE
**Problem Statement:**
\"\"\"{problem_statement}\"\"\"

### CURRENT ROUND OBJECTIVE:
{round_mission}

### YOUR PREVIOUS POSITION:
{my_prev_response}

### PEER PROPOSALS & CRITIQUES:
{peers_text}
{injection_block}

{NO_CODE_RULE}
{SCHEMA_GUIDE}"""

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
    moderator_injection: str = ""
) -> str:
    prev_round = previous_rounds[-1] if previous_rounds else None
    peers_transcripts = []
    my_prev_response = ""

    if prev_round:
        for m_id, resp in prev_round.responses.items():
            if m_id == my_model_config.id:
                my_prev_response = resp.structured.refined_solution or resp.raw_text
            else:
                m_name = resp.model_name
                peers_transcripts.append(f"""---
### Peer Innovation from: [{m_name}] (Model ID: {m_id})
- **Architect:** {resp.structured.architect_lens}
- **Hardware & ₹ BOM:** {resp.structured.field_hardware_lens or resp.structured.pragmatist_feasibility_lens}
- **Security & Compliance:** {resp.structured.security_compliance_lens or resp.structured.security_reliability_lens}
- **Refined Solution:** {resp.structured.refined_solution}
""")

    peers_text = "\n".join(peers_transcripts)
    
    injection_block = ""
    if moderator_injection:
        injection_block = f"\n### 🔔 MODERATOR INTERVENTION:\n\"{moderator_injection}\"\n"

    round_mission = ""
    if round_id == "3.1":
        round_mission = """🎯 **ROUND 3.1: THE 10x QUANTUM LEAP (The 4 Pillars of Innovation)**
You must advance your solution across all 4 Pillars adapted specifically to the domain of the problem statement:
1. **Flaw Inversion:** Directly solve every single Verified Fatal Vulnerability and edge-case from Phase 2.
2. **Frugal Architecture & ₹ INR Budget:** Itemized cost optimization in Indian Rupees (exact ICs/sensors/battery if hardware/IoT; cloud hosting/API/server compute budget if software/AI).
3. **Core SOTA Algorithms & Performance Pipeline:** State-of-the-art algorithmic models adapted to the domain (e.g. TinyML/Kalman for IoT; Transformers/vector indexing for NLP/search; CV for imagery; zero-knowledge/consensus for blockchain).
4. **Sovereign Indian Ecosystem & Compliance:** Integration with Indian platforms and standards relevant to the ministry (e.g., ISRO Bhuvan, DigiLocker, IndiaStack, ONDC, RDSO, NDMA, DPDP Act 2023)."""
    elif round_id == "3.2":
        round_mission = """🎯 **ROUND 3.2: MICRO-OPTIMIZATION & CROSS-POLLINATION**
- Review peer breakthroughs from Round 3.1 and cross-pollinate superior ideas.
- Inject minute, neglected engineering details: Graceful degradation, brownout/offline store-and-forward buffers, auto-calibration, rate-limit resilience, and zero-trust recovery."""

    return f"""### SMART INDIA HACKATHON (SIH) — PHASE 3: 10x ADVANCED SOLUTIONS
**Problem Statement:**
\"\"\"{problem_statement}\"\"\"

### CURRENT ROUND OBJECTIVE:
{round_mission}

### YOUR PREVIOUS POSITION:
{my_prev_response}

### PEER INNOVATIONS:
{peers_text}
{injection_block}

{NO_CODE_RULE}
{SCHEMA_GUIDE}"""

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
    moderator_injection: Optional[str] = None
) -> str:
    last_round = previous_rounds[-1] if previous_rounds else None
    
    my_prev_response = ""
    peers_transcripts = []

    if last_round:
        for m_id, resp in last_round.responses.items():
            if m_id == my_model_config.id:
                my_prev_response = resp.structured.refined_solution or resp.raw_text
            else:
                peers_transcripts.append(f"""### {resp.model_name} Position:
- **Refined Solution:** {resp.structured.refined_solution}
- **Consensus Vote:** {resp.structured.consensus_vote} ({resp.structured.agreement_percentage}%)
""")

    peers_text = "\n".join(peers_transcripts)
    
    injection_block = ""
    if moderator_injection:
        injection_block = f"\n### 🔔 MODERATOR DIRECTIVE:\n\"{moderator_injection}\"\n"

    round_mission = ""
    if round_id == "4.1":
        round_mission = """🎯 **ROUND 4.1: CONCESSION TREATY & MASTER BLUEPRINT ASSEMBLY**
- Review all peer positions and formally sign off on the Master Architecture.
- Declare your final Consensus Vote: AGREE, DISAGREE, or NEEDS_REFINEMENT.
- Integrate all resolved concessions into a unified, rock-solid engineering specification."""
    elif round_id == "4.2":
        round_mission = """🎯 **ROUND 4.2: TARGETED DISPUTE DUEL (Final Dispute Resolution)**
- Focus exclusively on the remaining dispute logged in the Jury Friction Log.
- Propose a mathematical, structural, or pragmatic compromise to reach unanimous consensus."""

    return f"""### SMART INDIA HACKATHON (SIH) — PHASE 4: CONVERGENCE CRUCIBLE
**Problem Statement:**
\"\"\"{problem_statement}\"\"\"

### CURRENT ROUND OBJECTIVE:
{round_mission}

### YOUR PREVIOUS POSITION:
{my_prev_response}

### PEER POSITIONS:
{peers_text}
{injection_block}

{NO_CODE_RULE}
{SCHEMA_GUIDE}"""

def build_arbiter_evaluation_prompt(
    problem_statement: str,
    round_number: int,
    phase_index: int,
    phase_title: str,
    round_responses: Dict[str, DebaterResponse],
    models: List[ModelConfig],
    phase_prompt: Optional[str] = None
) -> str:
    debater_summaries = []
    for m in models:
        if m.id in round_responses:
            resp = round_responses[m.id]
            st = resp.structured
            debater_summaries.append(f"""### Model: {m.name} ({m.model_id})
- **Status:** {resp.status} (Elapsed: {resp.elapsed_seconds:.1f}s)
- **Consensus Vote:** {st.consensus_vote} ({st.agreement_percentage}%)
- **Solution Summary:** {st.refined_solution[:400]}...
- **Critiques Launched:** {len(st.critiques)}
- **Concessions & Adaptations:** {len(st.concessions_and_defenses)}
""")

    summary_text = "\n".join(debater_summaries)

    return f"""You are the Master Arbiter and Jury Foreman in a high-stakes Smart India Hackathon (SIH) deliberation.
Evaluate the current round across all participating AI models.

**Problem Statement:**
\"\"\"{problem_statement}\"\"\"

**Phase {phase_index}:** {phase_title}
**Round Number:** {round_number}

### ROUND PARTICIPANT SUMMARIES:
{summary_text}

### YOUR TASK:
Evaluate alignment, measure consensus, identify open vs resolved technical friction points, and provide a synthesis.
Return your evaluation strictly in the following JSON format:

```json
{{
  "round_number": {round_number},
  "phase_index": {phase_index},
  "phase_title": "{phase_title}",
  "consensus_score": 88,
  "is_unanimous": false,
  "executive_synthesis": "Detailed 2-3 paragraph objective synthesis of where the models agree, key breakthroughs, and what disputes remain.",
  "friction_points": [
    {{
      "issue": "Brief description of technical conflict",
      "raised_by": "Model Name",
      "challenged_by": "Model Name",
      "status": "OPEN",
      "resolution_notes": "Current state of compromise or mathematical proof"
    }}
  ],
  "next_round_challenge": "Specific technical question or directive for the next round."
}}
```"""

def build_final_markdown_report_prompt(
    problem_statement: str,
    phase_title: str,
    all_rounds: List[RoundData],
    models: List[ModelConfig],
    ministry_domain: str,
    phase_prompt: Optional[str] = None
) -> str:
    model_names = ", ".join([m.name for m in models if m.enabled])
    
    history_snippets = []
    for r in all_rounds:
        history_snippets.append(f"### {r.pass_or_round_title or f'Round {r.round_number}'} (Phase {r.phase_index}):")
        if r.arbiter_eval:
            history_snippets.append(f"- **Consensus Score:** {r.arbiter_eval.consensus_score}% (Unanimous: {r.arbiter_eval.is_unanimous})")
            history_snippets.append(f"- **Synthesis:** {r.arbiter_eval.executive_synthesis[:250]}...")
        for m_id, resp in r.responses.items():
            if resp.structured and resp.structured.refined_solution:
                history_snippets.append(f"- **{resp.model_name}:** {resp.structured.refined_solution[:180]}...")

    history_text = "\n".join(history_snippets)

    return f"""You are the Master Arbiter synthesizing the definitive, unified Sovereign SIH Deliverable for this hackathon problem statement.

**Problem Statement:**
\"\"\"{problem_statement}\"\"\"
**Domain / Ministry:** {ministry_domain}
**Participating Flagship AI Models:** {model_names}

### DELIBERATION HISTORY SUMMARY:
{history_text}

### YOUR OBJECTIVE:
Generate an authoritative, definitive, pitch-winning **Sovereign SIH Master Consensus Deliverable** in clean GitHub-flavored Markdown.

{NO_CODE_RULE}

Structure the document with these exact 8 comprehensive, highly-detailed sections adapted to the problem domain:
1. `# 🏆 SIH Master Consensus Deliverable: {phase_title}`
2. `## 1. Executive Summary & 1-Minute Innovation Hook` (Unified breakthrough representing the collective intelligence of all participating models).
3. `## 2. End-to-End System Architecture & Data Signal Flow` (Component hierarchy, network topology, compute boundaries, and offline resilience).
4. `## 3. Itemized Bill of Materials (BOM) & Infrastructure Budget in Indian Rupees (₹)` (Markdown table with exact hardware components/ICs/sensors if hardware; cloud hosting/database/API server compute budget in ₹ if software/AI).
5. `## 4. Core Algorithms, AI Pipeline & Performance Optimization` (Preprocessing, model architectures, inference latency, anomaly filters, or data query pipelines appropriate to the problem domain).
6. `## 5. Fault-Tolerance, Chaos Recovery & High-Availability Protocols` (Graceful degradation, power/network loss handling, store-and-forward buffers, and fail-safe recovery).
7. `## 6. Statutory & Ministry Standards Compliance` (Relevant Indian statutory standards: e.g. MeitY, ISRO Bhuvan, RDSO, NDMA, DPDP Act 2023, ABDM).
8. `## 7. Official Multi-Model Consensus Ratification Sign-Off` (Formal sign-off certificate with notes from every participating AI model).

Generate ONLY the pure Markdown content."""
