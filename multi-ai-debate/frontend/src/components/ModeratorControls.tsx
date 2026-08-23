'use client';

import React, { useState } from 'react';
import { Play, Pause, Gavel, MessageSquarePlus, Settings, Sparkles, Send } from 'lucide-react';

interface ModeratorControlsProps {
  status: string;
  onPause: () => void;
  onResume: () => void;
  onCallVerdict: () => void;
  onInjectPrompt: (text: string) => void;
  onOpenConfig: () => void;
  modelsCount: number;
}

export function ModeratorControls({
  status,
  onPause,
  onResume,
  onCallVerdict,
  onInjectPrompt,
  onOpenConfig,
  modelsCount,
}: ModeratorControlsProps) {
  const [showInjectModal, setShowInjectModal] = useState(false);
  const [injectText, setInjectText] = useState('');

  const handleSendInjection = (e: React.FormEvent) => {
    e.preventDefault();
    if (!injectText.trim()) return;
    onInjectPrompt(injectText.trim());
    setInjectText('');
    setShowInjectModal(false);
  };

  return (
    <>
      <div className="w-full bg-[#111827]/90 backdrop-blur-md border border-[#232f48] rounded-2xl p-3.5 shadow-2xl flex flex-wrap items-center justify-between gap-3 sticky top-4 z-40">
        {/* Left: Status & AI count */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span
              className={`w-3 h-3 rounded-full ${
                status === 'running'
                  ? 'bg-emerald-500 animate-pulse ring-4 ring-emerald-500/20'
                  : status === 'paused'
                  ? 'bg-amber-500 ring-4 ring-amber-500/20'
                  : status === 'completed'
                  ? 'bg-cyan-500'
                  : 'bg-gray-500'
              }`}
            />
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              {status === 'running' ? 'Live Debate Active' : status.toUpperCase()}
            </span>
          </div>

          <span className="text-xs text-gray-500">|</span>
          <span className="text-xs text-gray-400 font-medium">{modelsCount} Debater Endpoints</span>
        </div>

        {/* Right: Moderator Control Buttons */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Pause / Resume */}
          {status === 'running' ? (
            <button
              onClick={onPause}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-bold transition shadow-sm"
            >
              <Pause className="w-3.5 h-3.5 fill-current" /> Pause Debate
            </button>
          ) : status === 'paused' ? (
            <button
              onClick={onResume}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition shadow-lg shadow-emerald-600/20"
            >
              <Play className="w-3.5 h-3.5 fill-current" /> Resume Debate
            </button>
          ) : null}

          {/* Inject Moderator Directive */}
          <button
            onClick={() => setShowInjectModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#161f33] hover:bg-[#1f2b47] text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition"
          >
            <MessageSquarePlus className="w-3.5 h-3.5" /> Inject Directive
          </button>

          {/* Call Verdict Button */}
          <button
            onClick={onCallVerdict}
            disabled={status === 'completed' || status === 'idle'}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-white text-xs font-bold shadow-lg shadow-amber-600/20 transition disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Gavel className="w-3.5 h-3.5" /> Call Final Verdict
          </button>

          {/* Model Config Drawer Toggle */}
          <button
            onClick={onOpenConfig}
            className="p-2 rounded-xl bg-[#161f33] hover:bg-[#1f2b47] border border-[#232f48] text-gray-300 hover:text-white transition"
            title="Configure AI Models & Endpoints"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Modal for injecting moderator constraint */}
      {showInjectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-lg bg-[#111827] border border-indigo-500/40 rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <MessageSquarePlus className="w-5 h-5 text-indigo-400" />
              <span>Inject Moderator Directive / Extra Constraints</span>
            </div>
            <p className="text-xs text-gray-400">
              This prompt will be injected into all debaters&apos; context for the upcoming round.
            </p>

            <form onSubmit={handleSendInjection} className="space-y-4">
              <textarea
                rows={3}
                value={injectText}
                onChange={(e) => setInjectText(e.target.value)}
                placeholder="e.g. 'Consider a strict requirement where the system must function for 48 hours without grid power...'"
                className="w-full p-3 rounded-xl bg-[#090d16] border border-[#232f48] text-white text-xs focus:outline-none focus:border-indigo-500 placeholder-gray-500"
                required
              />

              <div className="flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowInjectModal(false)}
                  className="px-4 py-2 rounded-lg bg-[#161f33] hover:bg-[#232f48] text-gray-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30"
                >
                  <Send className="w-3.5 h-3.5" /> Inject into Debate
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
