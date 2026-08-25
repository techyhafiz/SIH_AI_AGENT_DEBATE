from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
import uuid
import time

class ModelConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str  # Display name e.g., "Claude 3.5 Sonnet", "DeepSeek R1"
    base_url: str  # Custom Base URL
    api_key: str = ""  # Primary API Key
    backup_api_keys: List[str] = Field(default_factory=list)  # List of backup API keys
    model_id: str  # Model ID string
    fallback_model_ids: List[str] = Field(default_factory=list)  # Optional fallback model IDs to pool message quotas
    provider_type: Literal["openai_compatible", "gemini_native"] = "openai_compatible"
    timeout_seconds: int = 600  # Default 10 minutes
    is_arbiter: bool = False
    is_backup_arbiter: bool = False
    enabled: bool = True
    temperature: float = 0.7

class CritiqueItem(BaseModel):
    target_model_id: str = ""
    target_model_name: str = ""
    flaw_identified: str = ""
    counter_argument: str = ""

class ConcessionItem(BaseModel):
    conceded_point: str = ""
    conceded_to: str = ""
    adaptation: str = ""

class AutonomousResearchCall(BaseModel):
    stage: Literal["fact_check", "frontier_academic", "field_feasibility"] = "fact_check"
    target_engine: Literal["openalex_arxiv", "tavily_web"] = "tavily_web"
    query_purpose: str = ""
    search_query: str = ""

class StructuredDebateTurn(BaseModel):
    deliberation_scratchpad: str = ""
    architect_lens: str = ""
    critic_lens: str = ""
    critic_devil_advocate_lens: str = ""
    field_hardware_lens: str = ""
    pragmatist_feasibility_lens: str = ""
    security_compliance_lens: str = ""
    security_reliability_lens: str = ""
    critiques: List[CritiqueItem] = Field(default_factory=list)
    concessions_and_defenses: List[ConcessionItem] = Field(default_factory=list)
    refined_solution: str = ""
    positives_of_approach: List[str] = Field(default_factory=list)
    negatives_and_risks: List[str] = Field(default_factory=list)
    autonomous_research_calls: List[AutonomousResearchCall] = Field(default_factory=list)
    research_queries_for_next_round: List[str] = Field(default_factory=list)
    consensus_vote: Literal["AGREE", "DISAGREE", "NEEDS_REFINEMENT"] = "DISAGREE"
    agreement_percentage: int = 50

class DebaterResponse(BaseModel):
    model_id: str
    model_name: str
    phase_index: int = 1
    pass_or_round_id: str = "1.1"
    pass_or_round_title: str = "Architect Genesis"
    round_number: int = 1
    raw_text: str = ""
    structured: StructuredDebateTurn
    status: Literal["streaming", "completed", "timeout", "error", "quarantined"] = "completed"
    elapsed_seconds: float = 0.0
    error_message: Optional[str] = None
    active_key_used: Optional[str] = None

class FrictionPoint(BaseModel):
    issue: str
    raised_by: str
    challenged_by: str
    status: Literal["OPEN", "RESOLVED", "CONCEDED"] = "OPEN"
    resolution_notes: str = ""

class ArbiterEvaluation(BaseModel):
    round_number: int
    phase_index: int = 1
    phase_title: str = ""
    consensus_score: int = 50
    is_unanimous: bool = False
    executive_synthesis: str = ""
    friction_points: List[FrictionPoint] = Field(default_factory=list)
    next_round_challenge: Optional[str] = None
    arbiter_model_used: str = ""

class ResearchDossierItem(BaseModel):
    tag: str = ""
    title: str = ""
    url: str = ""
    type: str = "Web"
    year: Optional[Any] = None
    citations: Optional[int] = None
    summary: str = ""
    local_pdf_path: Optional[str] = None
    local_txt_path: Optional[str] = None

class PooledResearchDossier(BaseModel):
    round_num: int = 1
    phase_index: int = 1
    stage_1_fact_checks: List[ResearchDossierItem] = Field(default_factory=list)
    stage_2_academic_papers: List[ResearchDossierItem] = Field(default_factory=list)
    stage_3_field_benchmarks: List[ResearchDossierItem] = Field(default_factory=list)
    dossier_text: str = ""
    web_summary: str = ""
    total_sources: int = 0
    downloaded_papers_count: int = 0

class RoundData(BaseModel):
    round_number: int
    phase_index: int = 1
    phase_title: str = "Phase 1: Multi-Persona Genesis"
    pass_or_round_id: str = "1.1"
    pass_or_round_title: str = "Pass 1.1: Lead Architect Genesis"
    responses: Dict[str, DebaterResponse] = Field(default_factory=dict)
    arbiter_eval: Optional[ArbiterEvaluation] = None
    research_dossier: Optional[PooledResearchDossier] = None
    moderator_injection: Optional[str] = None
    started_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None

class WorkspacePhase(BaseModel):
    phase_index: int
    prompt: str
    phase_title: str
    verdict_filename: str
    verdict_markdown: str
    completed_at: float = Field(default_factory=time.time)

class DebateSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    workspace_folder: str = ""
    session_title: str = "SIH Debate Session"
    ps_code: Optional[str] = None
    problem_statement: str
    additional_prompt: Optional[str] = None
    ministry_domain: str = "Smart India Hackathon (General)"
    models: List[ModelConfig]
    arbiter_model_id: str
    backup_arbiter_model_id: Optional[str] = None
    phases: List[WorkspacePhase] = Field(default_factory=list)
    current_phase_index: int = 1
    current_phase_title: str = "Phase 1: Multi-Persona Genesis"
    current_pass_id: str = "1.1"
    current_pass_title: str = "Pass 1.1: Lead Architect Genesis"
    current_phase_prompt: str = ""
    rounds: List[RoundData] = Field(default_factory=list)
    status: Literal["idle", "running", "paused", "completed", "error"] = "idle"
    current_round_num: int = 0
    final_markdown_report: Optional[str] = None
    latest_research_dossier: Optional[PooledResearchDossier] = None
    created_at: float = Field(default_factory=time.time)

class StartDebateRequest(BaseModel):
    problem_statement: str
    ps_code: Optional[str] = None
    additional_prompt: Optional[str] = None
    session_title: Optional[str] = None
    ministry_domain: Optional[str] = "Smart India Hackathon (General)"
    models: List[ModelConfig]
    arbiter_model_id: Optional[str] = None
    backup_arbiter_model_id: Optional[str] = None
    auto_advance: bool = True

class FollowUpDebateRequest(BaseModel):
    followup_prompt: str
    phase_title: Optional[str] = "Follow-up Specification"
    auto_advance: bool = True

class ModeratorActionRequest(BaseModel):
    action: Literal["pause", "resume", "call_verdict", "next_round", "inject_prompt", "update_model_and_retry", "drop_model"]
    injection_text: Optional[str] = None
    ai_model_config: Optional[ModelConfig] = None
    target_model_id: Optional[str] = None

class ModelTestRequest(BaseModel):
    base_url: str
    api_key: str = ""
    backup_api_keys: List[str] = Field(default_factory=list)
    model_id: str
    provider_type: Literal["openai_compatible", "gemini_native"] = "openai_compatible"
    timeout_seconds: int = 30
