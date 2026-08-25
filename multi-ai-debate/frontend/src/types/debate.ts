export interface ModelConfig {
  id: string;
  name: string;
  base_url: string;
  api_key: string;
  backup_api_keys?: string[];
  model_id: string;
  fallback_model_ids?: string[];
  provider_type: 'openai_compatible' | 'gemini_native';
  timeout_seconds: number;
  is_arbiter: boolean;
  is_backup_arbiter?: boolean;
  enabled: boolean;
  temperature: number;
}

export interface CritiqueItem {
  target_model_id: string;
  target_model_name: string;
  flaw_identified: string;
  counter_argument: string;
}

export interface ConcessionItem {
  conceded_point: string;
  conceded_to: string;
  adaptation: string;
}

export interface AutonomousResearchCall {
  stage: 'fact_check' | 'frontier_academic' | 'field_feasibility';
  target_engine: 'openalex_arxiv' | 'tavily_web';
  query_purpose: string;
  search_query: string;
}

export interface StructuredDebateTurn {
  deliberation_scratchpad?: string;
  architect_lens: string;
  critic_lens?: string;
  critic_devil_advocate_lens?: string;
  field_hardware_lens?: string;
  pragmatist_feasibility_lens?: string;
  security_compliance_lens?: string;
  security_reliability_lens?: string;
  critiques: CritiqueItem[];
  concessions_and_defenses: ConcessionItem[];
  refined_solution: string;
  positives_of_approach: string[];
  negatives_and_risks: string[];
  autonomous_research_calls?: AutonomousResearchCall[];
  research_queries_for_next_round?: string[];
  consensus_vote: 'AGREE' | 'DISAGREE' | 'NEEDS_REFINEMENT';
  agreement_percentage: number;
}

export interface DebaterResponse {
  model_id: string;
  model_name: string;
  phase_index?: number;
  pass_or_round_id?: string;
  pass_or_round_title?: string;
  round_number: number;
  raw_text: string;
  structured: StructuredDebateTurn;
  status: 'streaming' | 'completed' | 'timeout' | 'error' | 'quarantined';
  elapsed_seconds: number;
  error_message?: string;
  active_key_used?: string;
}

export interface FrictionPoint {
  issue: string;
  raised_by: string;
  challenged_by: string;
  status: 'OPEN' | 'RESOLVED' | 'CONCEDED';
  resolution_notes: string;
}

export interface ArbiterEvaluation {
  round_number: number;
  phase_index?: number;
  phase_title?: string;
  consensus_score: number;
  is_unanimous: boolean;
  executive_synthesis: string;
  friction_points: FrictionPoint[];
  next_round_challenge?: string;
  arbiter_model_used?: string;
}

export interface ResearchDossierItem {
  tag: string;
  title: string;
  url: string;
  type: string;
  year?: number | string;
  citations?: number;
  summary: string;
  local_pdf_path?: string;
  local_txt_path?: string;
}

export interface PooledResearchDossier {
  round_num: number;
  phase_index: number;
  stage_1_fact_checks: ResearchDossierItem[];
  stage_2_academic_papers: ResearchDossierItem[];
  stage_3_field_benchmarks: ResearchDossierItem[];
  dossier_text: string;
  web_summary: string;
  total_sources: number;
  downloaded_papers_count: number;
}

export interface RoundData {
  round_number: number;
  phase_index: number;
  phase_title: string;
  pass_or_round_id?: string;
  pass_or_round_title?: string;
  responses: Record<string, DebaterResponse>;
  arbiter_eval?: ArbiterEvaluation;
  research_dossier?: PooledResearchDossier;
  moderator_injection?: string;
  started_at: number;
  completed_at?: number;
}

export interface WorkspacePhase {
  phase_index: number;
  prompt: string;
  phase_title: string;
  verdict_filename: string;
  verdict_markdown: string;
  completed_at: number;
}

export interface DebateSession {
  session_id: string;
  workspace_folder?: string;
  session_title?: string;
  ps_code?: string;
  problem_statement: string;
  additional_prompt?: string;
  ministry_domain: string;
  models: ModelConfig[];
  arbiter_model_id: string;
  backup_arbiter_model_id?: string;
  phases?: WorkspacePhase[];
  current_phase_index: number;
  current_phase_title?: string;
  current_pass_id?: string;
  current_pass_title?: string;
  current_phase_prompt?: string;
  rounds: RoundData[];
  status: 'idle' | 'running' | 'paused' | 'completed' | 'error';
  current_round_num: number;
  final_markdown_report?: string;
  latest_research_dossier?: PooledResearchDossier;
  created_at: number;
}

export interface TimeoutAlert {
  model_id: string;
  model_name: string;
  round_number: number;
  timeout_seconds: number;
  elapsed_seconds: number;
  error_message: string;
}

