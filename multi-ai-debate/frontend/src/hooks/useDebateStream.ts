'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { DebateSession, RoundData, DebaterResponse, TimeoutAlert } from '@/types/debate';

export function useDebateStream(sessionId: string | null) {
  const [session, setSession] = useState<DebateSession | null>(null);
  const [activeTokens, setActiveTokens] = useState<Record<string, string>>({});
  const [currentStatus, setCurrentStatus] = useState<string>('idle');
  const [timeoutAlert, setTimeoutAlert] = useState<TimeoutAlert | null>(null);
  const [isArbiterThinking, setIsArbiterThinking] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Fetch complete session state initially or on reconnect
  const fetchSession = useCallback(async (id: string) => {
    try {
      const res = await fetch(`/api/debate/${id}`);
      if (res.ok) {
        const data: DebateSession = await res.json();
        setSession(data);
        setCurrentStatus(data.status);
      }
    } catch (e) {
      console.error('Error fetching session:', e);
    }
  }, []);

  useEffect(() => {
    if (!sessionId) {
      setSession(null);
      setCurrentStatus('idle');
      return;
    }

    fetchSession(sessionId);

    // Establish SSE Connection
    const es = new EventSource(`/api/debate/stream/${sessionId}`);
    eventSourceRef.current = es;

    es.addEventListener('CONNECTED', () => {
      console.log('SSE Connected to debate session:', sessionId);
    });

    es.addEventListener('HEARTBEAT', () => {
      // Keep-alive acknowledgment
    });

    es.addEventListener('ROUND_START', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setActiveTokens({});
      setIsArbiterThinking(false);
      setSession((prev) => {
        if (!prev) return prev;
        const exists = prev.rounds.some((r) => r.round_number === data.round_number);
        if (exists) return prev;
        const newRound: RoundData = {
          round_number: data.round_number,
          phase_index: data.phase_index || prev.current_phase_index || 1,
          phase_title: data.phase_title || prev.current_phase_title || 'Deliberation',
          pass_or_round_id: data.pass_id,
          pass_or_round_title: data.pass_title,
          responses: {},
          moderator_injection: data.moderator_injection,
          started_at: Date.now() / 1000,
        };
        return {
          ...prev,
          current_round_num: data.round_number,
          current_phase_index: data.phase_index || prev.current_phase_index,
          current_phase_title: data.phase_title || prev.current_phase_title,
          current_pass_id: data.pass_id || prev.current_pass_id,
          current_pass_title: data.pass_title || prev.current_pass_title,
          rounds: [...prev.rounds, newRound],
        };
      });
    });

    es.addEventListener('RESEARCH_BLOCK_START', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setSession((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          current_phase_index: data.phase_index,
          current_pass_id: data.pass_id,
          current_pass_title: data.pass_title,
        };
      });
    });

    es.addEventListener('RESEARCH_DOSSIER_UPDATED', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setSession((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          latest_research_dossier: data.dossier || data,
        };
      });
    });

    es.addEventListener('MODEL_STREAM_START', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setActiveTokens((prev) => ({ ...prev, [data.model_id]: '' }));
    });

    es.addEventListener('MODEL_TOKEN_DELTA', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setActiveTokens((prev) => ({
        ...prev,
        [data.model_id]: (prev[data.model_id] || '') + data.delta,
      }));
    });

    es.addEventListener('MODEL_STREAM_END', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setSession((prev) => {
        if (!prev) return prev;
        const updatedRounds = prev.rounds.map((r) => {
          if (r.round_number === data.round_number) {
            const resp: DebaterResponse = {
              model_id: data.model_id,
              model_name: data.model_name,
              phase_index: data.phase_index,
              pass_or_round_id: data.pass_id,
              pass_or_round_title: data.pass_title,
              round_number: data.round_number,
              raw_text: activeTokens[data.model_id] || '',
              structured: data.structured,
              status: data.status,
              elapsed_seconds: data.elapsed_seconds,
            };
            return {
              ...r,
              responses: {
                ...r.responses,
                [data.model_id]: resp,
              },
            };
          }
          return r;
        });
        return { ...prev, rounds: updatedRounds };
      });
    });

    es.addEventListener('MODEL_TIMEOUT_ALERT', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setTimeoutAlert({
        model_id: data.model_id,
        model_name: data.model_name,
        round_number: data.round_number,
        timeout_seconds: data.timeout_seconds,
        elapsed_seconds: data.elapsed_seconds,
        error_message: data.error_message,
      });
    });

    es.addEventListener('ARBITER_EVALUATING', () => {
      setIsArbiterThinking(true);
    });

    es.addEventListener('ARBITER_EVAL_COMPLETE', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setIsArbiterThinking(false);
      setSession((prev) => {
        if (!prev) return prev;
        const updatedRounds = prev.rounds.map((r) => {
          if (r.round_number === data.round_number) {
            return {
              ...r,
              arbiter_eval: data.arbiter_eval,
            };
          }
          return r;
        });
        return { ...prev, rounds: updatedRounds };
      });
    });

    es.addEventListener('DEBATE_STATUS_CHANGE', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setCurrentStatus(data.status);
      setSession((prev) => (prev ? { ...prev, status: data.status } : prev));
    });

    es.addEventListener('DEBATE_COMPLETED', (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      setCurrentStatus('completed');
      setIsArbiterThinking(false);
      setSession((prev) =>
        prev
          ? {
              ...prev,
              status: 'completed',
              final_markdown_report: data.final_markdown_report,
            }
          : prev
      );
    });

    return () => {
      es.close();
    };
  }, [sessionId, fetchSession]);

  const sendModeratorAction = async (
    action: 'pause' | 'resume' | 'call_verdict' | 'inject_prompt' | 'update_model_and_retry' | 'drop_model',
    payload: any = {}
  ) => {
    if (!sessionId) return;
    try {
      await fetch(`/api/debate/${sessionId}/moderator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, ...payload }),
      });
    } catch (e) {
      console.error('Moderator action error:', e);
    }
  };

  return {
    session,
    currentStatus,
    activeTokens,
    timeoutAlert,
    setTimeoutAlert,
    isArbiterThinking,
    sendModeratorAction,
    refreshSession: () => sessionId && fetchSession(sessionId),
  };
}
