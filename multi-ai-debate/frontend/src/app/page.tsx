'use client';

import React, { useState, useEffect } from 'react';
import { ModelConfig } from '@/types/debate';
import { useDebateStream } from '@/hooks/useDebateStream';
import { ProblemInput } from '@/components/ProblemInput';
import { RoundTimeline } from '@/components/RoundTimeline';
import { ArenaGrid } from '@/components/ArenaGrid';
import { CounterMatrix } from '@/components/CounterMatrix';
import { ModeratorControls } from '@/components/ModeratorControls';
import { TimeoutAlertModal } from '@/components/TimeoutAlertModal';
import { ModelConfigDrawer } from '@/components/ModelConfigDrawer';
import { VerdictViewer } from '@/components/VerdictViewer';
import { Sparkles, Bot, Layers, ArrowLeft } from 'lucide-react';

const DEFAULT_MODELS: ModelConfig[] = [
  {
    id: 'm_claude',
    name: 'Claude 3.5 Sonnet',
    base_url: 'https://openrouter.ai/api/v1',
    api_key: '',
    model_id: 'anthropic/claude-3.5-sonnet',
    provider_type: 'openai_compatible',
    timeout_seconds: 600,
    is_arbiter: true,
    enabled: true,
    temperature: 0.7,
  },
  {
    id: 'm_deepseek',
    name: 'DeepSeek R1',
    base_url: 'https://openrouter.ai/api/v1',
    api_key: '',
    model_id: 'deepseek/deepseek-r1',
    provider_type: 'openai_compatible',
    timeout_seconds: 600,
    is_arbiter: false,
    enabled: true,
    temperature: 0.6,
  },
  {
    id: 'm_gemini',
    name: 'Gemini 2.0 Flash',
    base_url: 'https://openrouter.ai/api/v1',
    api_key: '',
    model_id: 'google/gemini-2.0-flash-001',
    provider_type: 'openai_compatible',
    timeout_seconds: 600,
    is_arbiter: false,
    enabled: true,
    temperature: 0.7,
  },
];

export default function HomePage() {
  const [models, setModels] = useState<ModelConfig[]>(DEFAULT_MODELS);
  const [arbiterModelId, setArbiterModelId] = useState<string>('m_claude');
  const [isConfigDrawerOpen, setIsConfigDrawerOpen] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedRound, setSelectedRound] = useState<number>(1);
  const [isLaunching, setIsLaunching] = useState(false);

  // Connect SSE streaming hook
  const {
    session,
    currentStatus,
    activeTokens,
    timeoutAlert,
    setTimeoutAlert,
    isArbiterThinking,
    sendModeratorAction,
  } = useDebateStream(sessionId);

  // Auto-track latest round
  useEffect(() => {
    if (session && session.current_round_num > 0) {
      setSelectedRound(session.current_round_num);
    }
  }, [session?.current_round_num]);

  const handleStartDebate = async (
    problemStatement: string,
    ministryDomain: string,
    autoAdvance: boolean
  ) => {
    setIsLaunching(true);
    try {
      const res = await fetch('/api/debate/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_statement: problemStatement,
          ministry_domain: ministryDomain,
          models: models,
          arbiter_model_id: arbiterModelId,
          auto_advance: autoAdvance,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setSessionId(data.session_id);
      } else {
        const err = await res.json();
        alert(`Error starting debate: ${err.detail || 'Server error'}`);
      }
    } catch (e: any) {
      alert(`Network error: ${e.message}`);
    } finally {
      setIsLaunching(false);
    }
  };

  const currentRoundData = session?.rounds?.find((r) => r.round_number === selectedRound);

  return (
    <main className="min-h-screen p-4 md:p-8 flex flex-col space-y-6 max-w-7xl mx-auto">
      {/* Top Navbar */}
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#232f48] pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-cyan-500 text-white shadow-xl shadow-indigo-500/20">
            <Bot className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-white tracking-tight">AI Consensus Arena</h1>
              <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-[11px] font-bold border border-indigo-500/30">
                SIH Edition
              </span>
            </div>
            <p className="text-xs text-gray-400">
              Multi-LLM Synchronous Cross-Critique, Rebuttal & Consensus Synthesis Engine
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {sessionId && (
            <button
              onClick={() => setSessionId(null)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#161f33] hover:bg-[#1f2b47] border border-[#232f48] text-gray-300 text-xs font-semibold transition"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> New Debate
            </button>
          )}

          <button
            onClick={() => setIsConfigDrawerOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/25 transition"
          >
            <Layers className="w-4 h-4" />
            <span>Configure AI Models ({models.filter((m) => m.enabled).length})</span>
          </button>
        </div>
      </header>

      {/* Main View: Setup OR Active Arena */}
      {!sessionId || !session ? (
        <div className="flex-1 flex flex-col justify-center py-6">
          <ProblemInput
            onStartDebate={handleStartDebate}
            isLoading={isLaunching}
            modelsCount={models.filter((m) => m.enabled).length}
          />
        </div>
      ) : (
        <div className="flex-1 flex flex-col space-y-6">
          {/* Moderator Control Toolbar */}
          <ModeratorControls
            status={currentStatus}
            onPause={() => sendModeratorAction('pause')}
            onResume={() => sendModeratorAction('resume')}
            onCallVerdict={() => sendModeratorAction('call_verdict')}
            onInjectPrompt={(text) => sendModeratorAction('inject_prompt', { injection_text: text })}
            onOpenConfig={() => setIsConfigDrawerOpen(true)}
            modelsCount={models.filter((m) => m.enabled).length}
          />

          {/* Round Timeline & Consensus Progress */}
          <RoundTimeline
            rounds={session.rounds}
            selectedRound={selectedRound}
            onSelectRound={setSelectedRound}
            currentRoundNum={session.current_round_num}
            latestArbiterEval={session.rounds[session.rounds.length - 1]?.arbiter_eval}
            isArbiterThinking={isArbiterThinking}
            status={currentStatus}
          />

          {/* Live Arena Debater Cards Grid */}
          <ArenaGrid
            models={session.models.filter((m) => m.enabled)}
            responses={currentRoundData?.responses || {}}
            activeTokens={activeTokens}
            roundNumber={selectedRound}
            arbiterModelId={session.arbiter_model_id}
          />

          {/* Cross-Critique Friction Matrix */}
          <CounterMatrix currentRoundData={currentRoundData} />

          {/* Final Consensus Verdict Report Viewer */}
          {session.final_markdown_report && (
            <div className="pt-4">
              <VerdictViewer
                markdownReport={session.final_markdown_report}
                sessionId={session.session_id}
                totalRounds={session.rounds.length}
              />
            </div>
          )}
        </div>
      )}

      {/* Timeout Alert Watchdog Modal */}
      <TimeoutAlertModal
        alert={timeoutAlert}
        models={models}
        onClose={() => setTimeoutAlert(null)}
        onUpdateAndRetry={(cfg) => {
          sendModeratorAction('update_model_and_retry', { ai_model_config: cfg });
        }}
        onDropModel={(mId) => {
          sendModeratorAction('drop_model', { target_model_id: mId });
        }}
      />

      {/* Dynamic Model Configuration Drawer */}
      <ModelConfigDrawer
        isOpen={isConfigDrawerOpen}
        onClose={() => setIsConfigDrawerOpen(false)}
        models={models}
        onSaveModels={setModels}
        arbiterModelId={arbiterModelId}
        onSetArbiterId={setArbiterModelId}
      />
    </main>
  );
}
