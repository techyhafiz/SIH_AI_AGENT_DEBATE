export interface ModelConfig {
  id: string;
  name: string;
  base_url: string;
  api_key: string;
  model_id: string;
  provider_type: 'openai_compatible' | 'gemini_native';
  timeout_seconds: number;
  is_arbiter: boolean;
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

export interface StructuredDebateTurn {
  architect_lens: string;
  critic_devil_advocate_lens: string;
  security_reliability_lens: string;
  pragmatist_feasibility_lens: string;
  critiques: CritiqueItem[];
  concessions_and_defenses: ConcessionItem[];
  refined_solution: string;
  positives_of_approach: string[];
  negatives_and_risks: string[];
  consensus_vote: 'AGREE' | 'DISAGREE' | 'NEEDS_REFINEMENT';
  agreement_percentage: number;
}

export interface DebaterResponse {
  model_id: string;
  model_name: string;
  round_number: number;
  raw_text: string;
  structured: StructuredDebateTurn;
  status: 'streaming' | 'completed' | 'timeout' | 'error' | 'quarantined';
  elapsed_seconds: number;
  error_message?: string;
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
  consensus_score: number;
  is_unanimous: boolean;
  executive_synthesis: string;
  friction_points: FrictionPoint[];
  next_round_challenge?: string;
}

export interface RoundData {
  round_number: number;
  responses: Record<string, DebaterResponse>;
  arbiter_eval?: ArbiterEvaluation;
  moderator_injection?: string;
  started_at: number;
  completed_at?: number;
}

export interface DebateSession {
  session_id: string;
  problem_statement: string;
  ministry_domain: string;
  models: ModelConfig[];
  arbiter_model_id: string;
  rounds: RoundData[];
  status: 'idle' | 'running' | 'paused' | 'completed' | 'error';
  current_round_num: number;
  final_markdown_report?: string;
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
