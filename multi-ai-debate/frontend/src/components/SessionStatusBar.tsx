'use client';

import { Activity, Award, CheckCircle, Clock, MessageSquarePlus, MoreHorizontal, Pause, Play, RefreshCw } from 'lucide-react';
import { DebateSession, RoundData } from '@/types/debate';

interface PipelineStep {
  id: string;
  phase: number;
  title: string;
  short: string;
}

interface SessionStatusBarProps {
  status: string;
  statusText: string;
  connectionStatus: string;
  session: DebateSession | null;
  currentRound?: RoundData;
  pipelineSteps: PipelineStep[];
  completedResponseCount: number;
  modelCount: number;
  onSelectRound: (index: number) => void;
  onPause: () => void;
  onResume: () => void;
  onInject: () => void;
  onFleetHealth: () => void;
  onCallVerdict: () => void;
  onOpenArbiter: () => void;
}

export function SessionStatusBar({
  status,
  statusText,
  connectionStatus,
  session,
  currentRound,
  pipelineSteps,
  completedResponseCount,
  modelCount,
  onSelectRound,
  onPause,
  onResume,
  onInject,
  onFleetHealth,
  onCallVerdict,
  onOpenArbiter,
}: SessionStatusBarProps) {
  const progress = modelCount > 0 ? Math.min(100, Math.round((completedResponseCount / modelCount) * 100)) : 0;
  const currentStep = session ? pipelineSteps.findIndex((step) => step.id === session.current_pass_id) + 1 : 0;

  return (
    <section className="status-bar">
      <div className="content-width status-bar-inner">
        <div className="status-summary">
          <div className="status-copy">
            <span className={`status-label status-label-${status}`}>{status === 'running' ? 'Live' : status === 'paused' ? 'Paused' : status === 'completed' ? 'Complete' : status === 'error' ? 'Needs attention' : status === 'loading' ? 'Loading' : 'Ready'}</span>
            <p className="status-message">{statusText}</p>
          </div>
          <div className="status-actions">
            <span className={`connection-indicator connection-indicator-${connectionStatus}`}>{!session ? 'No active stream' : status === 'completed' ? 'Session archived' : connectionStatus === 'connected' ? 'Stream connected' : connectionStatus === 'reconnecting' ? 'Reconnecting' : 'Stream offline'}</span>
            {currentRound?.arbiter_eval && <span className="data-badge">Consensus <strong>{currentRound.arbiter_eval.consensus_score}%</strong></span>}
            {session && (status === 'running' || status === 'paused') && (
              <>
                {status === 'running' ? (
                  <button type="button" onClick={onPause} className="toolbar-button toolbar-button-warning"><Pause className="h-3.5 w-3.5" /> Pause</button>
                ) : (
                  <button type="button" onClick={onResume} className="toolbar-button toolbar-button-accent"><Play className="h-3.5 w-3.5" /> Resume</button>
                )}
                <button type="button" onClick={onInject} className="toolbar-button"><MessageSquarePlus className="h-3.5 w-3.5" /> Inject</button>
                <details className="action-menu">
                  <summary className="toolbar-button"><MoreHorizontal className="h-4 w-4" /><span>More</span></summary>
                  <div className="action-menu-popover">
                    <button type="button" onClick={onFleetHealth}><Activity className="h-4 w-4" /><span><strong>Check fleet health</strong><small>Ask the arbiter to inspect model availability.</small></span></button>
                    <button type="button" onClick={onOpenArbiter}><Award className="h-4 w-4" /><span><strong>Open arbiter console</strong><small>Issue advanced natural-language commands.</small></span></button>
                    <button type="button" onClick={onCallVerdict} className="action-menu-danger"><Award className="h-4 w-4" /><span><strong>Call final verdict</strong><small>Synthesize from currently completed responses.</small></span></button>
                  </div>
                </details>
              </>
            )}
          </div>
        </div>

        {session && (
          <div className="progress-panel">
            <div className="progress-heading"><h2>{currentRound?.pass_or_round_title || session.current_pass_title || 'Deliberation progress'}</h2><span>{completedResponseCount} of {modelCount} models complete · {progress}%</span></div>
            <div className="progress-track" role="progressbar" aria-label={`${progress}% of models complete`} aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}><span style={{ width: `${progress}%` }} /></div>
          </div>
        )}

        <div className="progress-panel">
          <div className="progress-heading"><h2>Deliberation pipeline</h2><span>{session ? `${Math.max(0, currentStep)} / ${pipelineSteps.length} passes` : `${pipelineSteps.length} structured passes`}</span></div>
          <div className="pipeline-scroll">
            {pipelineSteps.map((step, index) => {
              const matchingRounds = session?.rounds
                .map((round, roundIndex) => ({ round, roundIndex }))
                .filter(({ round }) => round.pass_or_round_id === step.id
                  && (!session.workspace_phase_number || round.workspace_phase_number === session.workspace_phase_number)) || [];
              const roundIndex = matchingRounds.length ? matchingRounds[matchingRounds.length - 1].roundIndex : -1;
              const isDirectlyComplete = roundIndex !== -1 && Boolean(session?.rounds[roundIndex]?.completed_at);
              const isLaterComplete = session?.rounds.some((round) => {
                if (session.workspace_phase_number && round.workspace_phase_number !== session.workspace_phase_number) return false;
                const roundStepIndex = pipelineSteps.findIndex((candidate) => candidate.id === round.pass_or_round_id);
                return roundStepIndex > index && Boolean(round.completed_at);
              }) ?? false;
              const researchComplete = session?.completed_research_steps?.includes(`${session.workspace_phase_number || 1}:${step.id}`) || false;
              const isComplete = isDirectlyComplete || isLaterComplete || researchComplete;
              const isCurrent = (session?.status === 'running' || session?.status === 'paused') && session?.current_pass_id === step.id;
              return (
                <button key={step.id} type="button" onClick={() => { if (roundIndex !== -1) onSelectRound(roundIndex); }} className={`pipeline-step ${isCurrent ? 'pipeline-step-current' : isComplete ? 'pipeline-step-complete' : ''}`} title={step.title}>
                  {isComplete ? <CheckCircle className="h-3.5 w-3.5" /> : isCurrent ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Clock className="h-3.5 w-3.5" />}
                  <span>{step.short}</span>
                  {session?.rounds[roundIndex]?.arbiter_eval?.consensus_score != null && <span className="pipeline-score">{session.rounds[roundIndex].arbiter_eval?.consensus_score}%</span>}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
