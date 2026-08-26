'use client';

import { useMemo } from 'react';
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  ChevronDown,
  Circle,
  Eye,
  Flame,
  Power,
  PowerOff,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Timer,
  Wrench,
} from 'lucide-react';
import { DebaterResponse, ModelConfig } from '@/types/debate';

interface DebaterCardProps {
  model: ModelConfig;
  response?: DebaterResponse;
  streamText?: string;
  isStreaming: boolean;
  isArbiter: boolean;
  isBackupArbiter: boolean;
  isDisabled: boolean;
  passTitle?: string;
  onToggle: () => void;
  onInspect: (response: DebaterResponse) => void;
}

type Lens = {
  label: string;
  shortLabel: string;
  value?: string;
  tone: 'indigo' | 'rose' | 'amber' | 'emerald';
};

function toneClasses(tone: Lens['tone']) {
  return {
    indigo: 'debater-lens debater-lens-indigo',
    rose: 'debater-lens debater-lens-rose',
    amber: 'debater-lens debater-lens-amber',
    emerald: 'debater-lens debater-lens-emerald',
  }[tone];
}

function responseStatus(response: DebaterResponse | undefined, isStreaming: boolean) {
  if (isStreaming) return { label: 'Generating', tone: 'live' as const };
  if (response?.status === 'completed') return { label: 'Complete', tone: 'success' as const };
  if (response?.status === 'timeout' || response?.status === 'quarantined') {
    return { label: response.status === 'timeout' ? 'Timed out' : 'Quarantined', tone: 'warning' as const };
  }
  if (response?.status === 'error') return { label: 'Error', tone: 'danger' as const };
  return { label: 'Waiting', tone: 'neutral' as const };
}

export function DebaterCard({
  model,
  response,
  streamText,
  isStreaming,
  isArbiter,
  isBackupArbiter,
  isDisabled,
  passTitle,
  onToggle,
  onInspect,
}: DebaterCardProps) {
  const status = responseStatus(response, isStreaming);
  const structured = response?.structured;
  const summary = structured?.refined_solution
    || structured?.architect_lens
    || structured?.critic_lens
    || structured?.critic_devil_advocate_lens
    || structured?.field_hardware_lens
    || structured?.pragmatist_feasibility_lens
    || structured?.security_compliance_lens
    || structured?.security_reliability_lens
    || response?.raw_text;

  const lenses = useMemo<Lens[]>(() => ([
    { label: 'Lead architect', shortLabel: 'Architecture', value: structured?.architect_lens, tone: 'indigo' },
    { label: "Devil's advocate", shortLabel: 'Critical risks', value: structured?.critic_lens || structured?.critic_devil_advocate_lens, tone: 'rose' },
    { label: 'Field feasibility', shortLabel: 'BOM & delivery', value: structured?.field_hardware_lens || structured?.pragmatist_feasibility_lens, tone: 'amber' },
    { label: 'Security & reliability', shortLabel: 'Security', value: structured?.security_compliance_lens || structured?.security_reliability_lens, tone: 'emerald' },
  ] satisfies Lens[]).filter((lens) => Boolean(lens.value)), [structured]);

  const vote = structured?.consensus_vote;
  // A null vote is an abstention (the turn returned no readable position), not a soft
  // "needs review" - it is excluded from the consensus average, so keep it neutral.
  const voteTone = !vote ? 'neutral' : vote === 'AGREE' ? 'success' : vote === 'DISAGREE' ? 'danger' : 'warning';
  const hasScore = structured?.agreement_percentage !== null && structured?.agreement_percentage !== undefined;
  const critiqueCount = structured?.critiques?.length || 0;
  const riskCount = structured?.negatives_and_risks?.length || 0;

  return (
    <article className={`debater-card ${isDisabled ? 'debater-card-disabled' : ''} ${isStreaming ? 'debater-card-live' : ''}`}>
      <header className="debater-card-header">
        <div className="min-w-0 flex items-start gap-3">
          <div className={`debater-avatar ${isArbiter ? 'debater-avatar-arbiter' : ''}`} aria-hidden="true">
            <Bot className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-1.5">
              <h3 className={`truncate text-sm font-semibold ${isDisabled ? 'line-through' : ''}`}>{model.name}</h3>
              {isArbiter && <span className="role-chip role-chip-primary"><ShieldCheck className="h-3 w-3" /> Arbiter</span>}
              {isBackupArbiter && <span className="role-chip role-chip-backup"><RefreshCw className="h-3 w-3" /> Backup</span>}
              {isDisabled && <span className="role-chip role-chip-danger">Excluded</span>}
            </div>
            <p className="mt-1 truncate font-mono text-[11px] text-[var(--muted)]" title={model.model_id}>{model.model_id}</p>
          </div>
        </div>

        <div className={`status-badge status-badge-${status.tone}`} aria-live="polite">
          {status.tone === 'live' && <Sparkles className="h-3 w-3 animate-spin" />}
          {status.tone === 'success' && <CheckCircle2 className="h-3 w-3" />}
          {status.tone === 'warning' && <AlertTriangle className="h-3 w-3" />}
          {status.tone === 'danger' && <AlertTriangle className="h-3 w-3" />}
          {status.tone === 'neutral' && <Circle className="h-3 w-3" />}
          <span>{status.label}</span>
        </div>
      </header>

      <div className="debater-card-body">
        {isStreaming && (
          <section className="live-response" aria-live="polite">
            <div className="flex items-center justify-between gap-3">
              <div className="flex min-w-0 items-center gap-2 text-xs font-semibold text-[var(--accent-strong)]">
                <Sparkles className="h-3.5 w-3.5 shrink-0 animate-pulse" />
                <span className="truncate">Working on {passTitle || 'the current pass'}</span>
              </div>
              <span className="shrink-0 font-mono text-[10px] uppercase tracking-wider text-[var(--accent)]">Live</span>
            </div>
            <div className="live-progress" aria-hidden="true"><span /></div>
            {streamText ? (
              <pre className="live-stream-text">{streamText.slice(-520)}</pre>
            ) : (
              <p className="text-[11px] text-[var(--muted)]">Connecting to the model stream...</p>
            )}
          </section>
        )}

        {response?.status === 'error' && (
          <section className="response-notice response-notice-danger">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <p>{response.error_message || 'The model returned an error for this pass.'}</p>
          </section>
        )}

        {response?.status === 'timeout' && (
          <section className="response-notice response-notice-warning">
            <Timer className="h-4 w-4 shrink-0" />
            <p>This model exceeded its response window. Review the recovery options in the alert.</p>
          </section>
        )}

        {structured && response?.status === 'completed' ? (
          <>
            <div className="vote-row">
              <div>
                <span className="eyebrow">Model position</span>
                <p className="mt-1 text-xs text-[var(--muted)]">
                  {vote || hasScore
                    ? 'Agreement with the emerging solution'
                    : 'No readable position returned - excluded from the consensus average'}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`status-badge status-badge-${voteTone}`}>{vote || 'Not scored'}</span>
                <strong className="text-sm tabular-nums">
                  {hasScore ? `${structured.agreement_percentage}%` : '—'}
                </strong>
              </div>
            </div>

            {summary && (
              <section className="response-summary">
                <div className="section-kicker"><Wrench className="h-3.5 w-3.5" /> Proposed direction</div>
                <p>{summary}</p>
              </section>
            )}

            {lenses.length > 0 && (
              <div className="space-y-2">
                <span className="eyebrow">Four decision lenses</span>
                <div className="space-y-2">
                  {lenses.map((lens) => (
                    <details key={lens.label} className={toneClasses(lens.tone)}>
                      <summary>
                        <span>{lens.shortLabel}</span>
                        <ChevronDown className="h-3.5 w-3.5" />
                      </summary>
                      <p>{lens.value}</p>
                    </details>
                  ))}
                </div>
              </div>
            )}

            {(critiqueCount > 0 || riskCount > 0) && (
              <div className="flex flex-wrap gap-2 border-t border-[var(--line)] pt-3">
                {critiqueCount > 0 && (
                  <details className="compact-disclosure">
                    <summary><Flame className="h-3.5 w-3.5 text-rose-500" /> {critiqueCount} peer critique{critiqueCount === 1 ? '' : 's'}</summary>
                    <div className="disclosure-content">
                      {structured.critiques?.map((critique, index) => (
                        <div key={`${critique.target_model_id}-${index}`} className="space-y-1">
                          <strong>Against {critique.target_model_name}</strong>
                          <p>{critique.flaw_identified}</p>
                          <p className="text-[var(--muted)]">{critique.counter_argument}</p>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
                {riskCount > 0 && (
                  <details className="compact-disclosure">
                    <summary><AlertTriangle className="h-3.5 w-3.5 text-amber-500" /> {riskCount} identified risk{riskCount === 1 ? '' : 's'}</summary>
                    <div className="disclosure-content">
                      <ul className="list-disc space-y-1 pl-4">
                        {structured.negatives_and_risks?.map((risk, index) => <li key={`${risk}-${index}`}>{risk}</li>)}
                      </ul>
                    </div>
                  </details>
                )}
              </div>
            )}
          </>
        ) : !isStreaming && !response ? (
          <div className="empty-card-state">
            <Circle className="h-5 w-5" />
            <p>Waiting for this model to join the current pass.</p>
          </div>
        ) : null}
      </div>

      <footer className="debater-card-footer">
        <span className="flex min-w-0 items-center gap-1.5 truncate text-[11px] text-[var(--muted)]">
          <span className={`health-dot ${response?.status === 'completed' ? 'health-dot-good' : ''}`} />
          {response?.status === 'completed' ? 'Provider responded' : 'Endpoint configured'}
          {response?.elapsed_seconds ? <span className="font-mono">· {response.elapsed_seconds.toFixed(1)}s</span> : null}
        </span>
        <div className="flex items-center gap-1.5">
          {response && (
            <button type="button" onClick={() => onInspect(response)} className="icon-text-button" aria-label={`Inspect ${model.name} response`}>
              <Eye className="h-3.5 w-3.5" /> Inspect
            </button>
          )}
          <button
            type="button"
            onClick={onToggle}
            className={`icon-button ${isDisabled ? 'icon-button-success' : 'icon-button-danger'}`}
            aria-label={isDisabled ? `Re-enable ${model.name}` : `Exclude ${model.name} from this session`}
            title={isDisabled ? 'Re-enable model' : 'Exclude model from this session'}
          >
            {isDisabled ? <Power className="h-3.5 w-3.5" /> : <PowerOff className="h-3.5 w-3.5" />}
          </button>
        </div>
      </footer>
    </article>
  );
}
