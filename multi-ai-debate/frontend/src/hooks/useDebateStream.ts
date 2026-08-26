'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { DebateSession, DebaterResponse, RoundData, TimeoutAlert } from '@/types/debate';

export type SSEConnectionStatus = 'connected' | 'reconnecting' | 'disconnected';
export type StreamingModelState = {
  model_id: string;
  phase_index?: number;
  pass_id?: string;
  round_number?: number;
  state: 'starting' | 'streaming' | 'retrying';
};
export type DebateActivityEvent = {
  event: string;
  message: string;
  severity: 'info' | 'warning' | 'error';
  timestamp: number;
};

const MAX_BACKOFF_MS = 60_000;
const INITIAL_BACKOFF_MS = 3_000;

function parseEvent(event: MessageEvent): Record<string, any> {
  try {
    const parsed = JSON.parse(event.data);
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch {
    return {};
  }
}

export function useDebateStream(sessionId: string | null) {
  const [session, setSession] = useState<DebateSession | null>(null);
  const [activeTokens, setActiveTokens] = useState<Record<string, string>>({});
  const [streamingModels, setStreamingModels] = useState<Record<string, StreamingModelState>>({});
  const [currentStatus, setCurrentStatus] = useState<string>('idle');
  const [timeoutAlert, setTimeoutAlert] = useState<TimeoutAlert | null>(null);
  const [isArbiterThinking, setIsArbiterThinking] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<SSEConnectionStatus>('disconnected');
  const [activity, setActivity] = useState<DebateActivityEvent[]>([]);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const fetchAbortRef = useRef<AbortController | null>(null);
  const sessionIdRef = useRef<string | null>(null);
  const epochRef = useRef(0);
  const backoffRef = useRef(INITIAL_BACKOFF_MS);
  const tokenBuffersRef = useRef<Record<string, string>>({});
  const pendingTokenChunksRef = useRef<Record<string, string[]>>({});
  const rafRef = useRef<number | null>(null);

  const addActivity = useCallback((event: string, message: string, severity: DebateActivityEvent['severity'] = 'info') => {
    setActivity((previous) => [...previous, { event, message, severity, timestamp: Date.now() }].slice(-50));
  }, []);

  const flushTokens = useCallback(() => {
    rafRef.current = null;
    const pending = pendingTokenChunksRef.current;
    pendingTokenChunksRef.current = {};
    setActiveTokens((previous) => {
      const next = { ...previous };
      Object.entries(pending).forEach(([modelId, chunks]) => {
        next[modelId] = (next[modelId] || '') + chunks.join('');
      });
      return next;
    });
  }, []);

  const queueToken = useCallback((modelId: string, delta: string) => {
    (pendingTokenChunksRef.current[modelId] ||= []).push(delta);
    if (rafRef.current === null) {
      rafRef.current = requestAnimationFrame(flushTokens);
    }
  }, [flushTokens]);

  const clearTransient = useCallback(() => {
    if (rafRef.current !== null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    pendingTokenChunksRef.current = {};
    tokenBuffersRef.current = {};
    setActiveTokens({});
    setStreamingModels({});
    setIsArbiterThinking(false);
  }, []);

  const fetchSession = useCallback(async (id: string, epoch: number) => {
    fetchAbortRef.current?.abort();
    const controller = new AbortController();
    fetchAbortRef.current = controller;
    try {
      const response = await fetch(`/api/debate/${encodeURIComponent(id)}`, { signal: controller.signal });
      if (!response.ok) throw new Error(`Session fetch failed (${response.status})`);
      const data: DebateSession = await response.json();
      if (epochRef.current !== epoch || sessionIdRef.current !== id) return;
      setSession(data);
      setCurrentStatus(data.status);
    } catch (error: any) {
      if (error?.name !== 'AbortError' && epochRef.current === epoch) {
        addActivity('SESSION_FETCH_ERROR', error?.message || 'Could not refresh session state.', 'error');
      }
    }
  }, [addActivity]);

  const connect = useCallback((id: string, epoch: number) => {
    eventSourceRef.current?.close();
    const source = new EventSource(`/api/debate/stream/${encodeURIComponent(id)}`);
    eventSourceRef.current = source;
    const valid = () => epochRef.current === epoch && sessionIdRef.current === id && eventSourceRef.current === source;
    const reconcile = () => { if (valid()) void fetchSession(id, epoch); };

    source.addEventListener('CONNECTED', () => {
      if (!valid()) return;
      setConnectionStatus('connected');
      backoffRef.current = INITIAL_BACKOFF_MS;
      reconcile();
    });
    source.addEventListener('HEARTBEAT', () => { if (valid()) setConnectionStatus('connected'); });
    source.onerror = () => {
      if (!valid()) return;
      source.close();
      eventSourceRef.current = null;
      clearTransient();
      setConnectionStatus('reconnecting');
      reconcile();
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      const wait = backoffRef.current;
      reconnectTimerRef.current = setTimeout(() => {
        if (sessionIdRef.current === id && epochRef.current === epoch) connect(id, epoch);
      }, wait);
      backoffRef.current = Math.min(wait * 2, MAX_BACKOFF_MS);
    };

    source.addEventListener('ROUND_START', (event: MessageEvent) => {
      if (!valid()) return;
      const data = parseEvent(event);
      setSession((previous) => {
        if (!previous || previous.rounds.some((round) => round.round_number === data.round_number && round.pass_or_round_id === data.pass_id)) return previous;
        const round: RoundData = {
          round_number: data.round_number,
          workspace_phase_number: previous.workspace_phase_number,
          phase_index: data.phase_index || previous.current_phase_index,
          phase_title: data.phase_title || previous.current_phase_title || 'Deliberation',
          pass_or_round_id: data.pass_id,
          pass_or_round_title: data.pass_title,
          responses: {},
          started_at: Date.now() / 1000,
          moderator_injection: data.moderator_injection,
        };
        return { ...previous, current_round_num: data.round_number, current_phase_index: round.phase_index, current_phase_title: round.phase_title, current_pass_id: data.pass_id, current_pass_title: data.pass_title, rounds: [...previous.rounds, round] };
      });
    });
    source.addEventListener('MODEL_STREAM_START', (event: MessageEvent) => {
      if (!valid()) return;
      const data = parseEvent(event);
      tokenBuffersRef.current[data.model_id] = '';
      setStreamingModels((previous) => ({ ...previous, [data.model_id]: { model_id: data.model_id, phase_index: data.phase_index, pass_id: data.pass_id, round_number: data.round_number, state: 'starting' } }));
    });
    source.addEventListener('MODEL_TOKEN_DELTA', (event: MessageEvent) => {
      if (!valid()) return;
      const data = parseEvent(event);
      tokenBuffersRef.current[data.model_id] = (tokenBuffersRef.current[data.model_id] || '') + String(data.delta || '');
      setStreamingModels((previous) => ({
        ...previous,
        [data.model_id]: previous[data.model_id]
          ? { ...previous[data.model_id], state: 'streaming' }
          : { model_id: data.model_id, round_number: data.round_number, pass_id: data.pass_id, state: 'streaming' },
      }));
      queueToken(data.model_id, String(data.delta || ''));
    });
    source.addEventListener('MODEL_RETRY_ATTEMPT', (event: MessageEvent) => {
      if (!valid()) return;
      const data = parseEvent(event);
      setStreamingModels((previous) => previous[data.model_id] ? { ...previous, [data.model_id]: { ...previous[data.model_id], state: 'retrying' } } : previous);
      addActivity('MODEL_RETRY_ATTEMPT', data.message || 'Model retry started.', 'warning');
    });
    source.addEventListener('MODEL_STREAM_END', (event: MessageEvent) => {
      if (!valid()) return;
      const data = parseEvent(event);
      delete pendingTokenChunksRef.current[data.model_id];
      const rawText = tokenBuffersRef.current[data.model_id] || '';
      delete tokenBuffersRef.current[data.model_id];
      setStreamingModels((previous) => { const next = { ...previous }; delete next[data.model_id]; return next; });
      setActiveTokens((previous) => { const next = { ...previous }; delete next[data.model_id]; return next; });
      setSession((previous) => {
        if (!previous) return previous;
        const response: DebaterResponse = data.response || {
          model_id: data.model_id, model_name: data.model_name, phase_index: data.phase_index, pass_or_round_id: data.pass_id, pass_or_round_title: data.pass_title,
          round_number: data.round_number, raw_text: rawText, structured: data.structured, status: data.status, elapsed_seconds: data.elapsed_seconds || 0,
        };
        const rounds = [...previous.rounds];
        let index = rounds.findIndex((round) => round.round_number === data.round_number && round.pass_or_round_id === data.pass_id);
        if (index < 0) {
          rounds.push({ round_number: data.round_number, phase_index: data.phase_index || 1, phase_title: data.phase_title || '', pass_or_round_id: data.pass_id, pass_or_round_title: data.pass_title, responses: {}, started_at: Date.now() / 1000 });
          index = rounds.length - 1;
        }
        rounds[index] = { ...rounds[index], responses: { ...rounds[index].responses, [data.model_id]: response } };
        return { ...previous, rounds };
      });
    });
    source.addEventListener('MODEL_TIMEOUT_ALERT', (event: MessageEvent) => {
      if (!valid()) return;
      const data = parseEvent(event);
      setTimeoutAlert({
        model_id: data.model_id,
        model_name: data.model_name,
        round_number: data.round_number,
        timeout_seconds: data.timeout_seconds,
        elapsed_seconds: data.elapsed_seconds,
        error_message: data.error_message || 'The model exceeded its response window.',
      });
      addActivity('MODEL_TIMEOUT_ALERT', `${data.model_name || 'A model'} exceeded its response window.`, 'warning');
    });
    source.addEventListener('RESEARCH_BLOCK_START', (event: MessageEvent) => {
      if (!valid()) return;
      const data = parseEvent(event);
      setSession((previous) => previous ? { ...previous, current_phase_index: data.phase_index, current_pass_id: data.pass_id, current_pass_title: data.pass_title } : previous);
    });
    source.addEventListener('RESEARCH_DOSSIER_UPDATED', (event: MessageEvent) => {
      if (!valid()) return;
      const data = parseEvent(event);
      setSession((previous) => previous ? { ...previous, latest_research_dossier: data.dossier } : previous);
    });
    source.addEventListener('ARBITER_EVALUATING', () => { if (valid()) setIsArbiterThinking(true); });
    source.addEventListener('ARBITER_EVAL_COMPLETE', (event: MessageEvent) => {
      if (!valid()) return;
      const data = parseEvent(event);
      setIsArbiterThinking(false);
      setSession((previous) => previous ? { ...previous, rounds: previous.rounds.map((round) => round.round_number === data.round_number ? { ...round, arbiter_eval: data.arbiter_eval } : round) } : previous);
    });
    source.addEventListener('DEBATE_STATUS_CHANGE', (event: MessageEvent) => {
      if (!valid()) return;
      const data = parseEvent(event);
      setCurrentStatus(data.status);
      setSession((previous) => previous ? { ...previous, status: data.status } : previous);
    });
    const paused = (event: MessageEvent) => { if (!valid()) return; const data = parseEvent(event); clearTransient(); setCurrentStatus('paused'); addActivity(event.type, data.message || 'Debate paused.', 'warning'); reconcile(); };
    source.addEventListener('ALL_MODELS_UNAVAILABLE', paused);
    source.addEventListener('ROUND_FAILED', paused);
    source.addEventListener('DEBATE_PAUSED_AWAITING_USER', paused);
    source.addEventListener('DEBATE_ERROR', (event: MessageEvent) => { if (!valid()) return; const data = parseEvent(event); clearTransient(); setCurrentStatus('error'); addActivity('DEBATE_ERROR', data.message || 'Debate failed.', 'error'); void fetchSession(id, epoch); source.close(); eventSourceRef.current = null; setConnectionStatus('disconnected'); });
    source.addEventListener('ARBITER_SUPERVISOR_ACTION', (event: MessageEvent) => { if (valid()) { const data = parseEvent(event); addActivity('ARBITER_SUPERVISOR_ACTION', data.message || 'Arbiter action completed.', 'warning'); } });
    source.addEventListener('MODEL_DROPPED', (event: MessageEvent) => {
      if (!valid()) return;
      const data = parseEvent(event);
      setStreamingModels((previous) => { const next = { ...previous }; delete next[data.model_id]; return next; });
      setActiveTokens((previous) => { const next = { ...previous }; delete next[data.model_id]; return next; });
      reconcile();
    });
    source.addEventListener('MODEL_ENABLED', () => { if (valid()) reconcile(); });
    source.addEventListener('DEBATE_COMPLETED', () => { if (valid()) { clearTransient(); setCurrentStatus('completed'); void fetchSession(id, epoch); source.close(); eventSourceRef.current = null; setConnectionStatus('disconnected'); } });
  }, [addActivity, clearTransient, fetchSession, flushTokens, queueToken]);

  useEffect(() => {
    const epoch = ++epochRef.current;
    sessionIdRef.current = sessionId;
    fetchAbortRef.current?.abort();
    eventSourceRef.current?.close();
    if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    clearTransient();
    setCurrentStatus(sessionId ? 'loading' : 'idle');
    setTimeoutAlert(null);
    setActivity([]);
    if (!sessionId) {
      setSession(null);
      setCurrentStatus('idle');
      setConnectionStatus('disconnected');
      return;
    }
    setSession(null);
    setConnectionStatus('reconnecting');
    void fetchSession(sessionId, epoch);
    connect(sessionId, epoch);
    return () => {
      fetchAbortRef.current?.abort();
      eventSourceRef.current?.close();
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    };
  }, [clearTransient, connect, fetchSession, sessionId]);

  const sendModeratorAction = useCallback(async (action: string, payload: any = {}) => {
    if (!sessionIdRef.current) throw new Error('No active session.');
    const response = await fetch(`/api/debate/${encodeURIComponent(sessionIdRef.current)}/moderator`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action, ...payload }) });
    const text = await response.text();
    let data: any = {};
    try { data = text ? JSON.parse(text) : {}; } catch { data = { detail: text }; }
    if (!response.ok) throw new Error(data.detail || data.message || `Moderator action failed (${response.status})`);
    const currentId = sessionIdRef.current;
    if (currentId) void fetchSession(currentId, epochRef.current);
    return data;
  }, [fetchSession]);

  return { session, currentStatus, activeTokens, streamingModels, timeoutAlert, setTimeoutAlert, isArbiterThinking, connectionStatus, activity, sendModeratorAction, refreshSession: () => sessionIdRef.current ? fetchSession(sessionIdRef.current, epochRef.current) : undefined };
}
