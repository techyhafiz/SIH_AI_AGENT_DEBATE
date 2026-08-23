'use client';

import React from 'react';
import { RoundData, ArbiterEvaluation } from '@/types/debate';
import { CheckCircle2, ShieldAlert, Sparkles, MessageSquare } from 'lucide-react';

interface RoundTimelineProps {
  rounds: RoundData[];
  selectedRound: number;
  onSelectRound: (roundNumber: number) => void;
  currentRoundNum: number;
  latestArbiterEval?: ArbiterEvaluation;
  isArbiterThinking: boolean;
  status: string;
}

export function RoundTimeline({
  rounds,
  selectedRound,
  onSelectRound,
  currentRoundNum,
  latestArbiterEval,
  isArbiterThinking,
  status,
}: RoundTimelineProps) {
  const consensusScore = latestArbiterEval?.consensus_score || 0;
  const isUnanimous = latestArbiterEval?.is_unanimous || false;

  return (
    <div className="w-full bg-[#111827] border border-[#232f48] rounded-2xl p-4 shadow-xl space-y-4">
      {/* Top Bar: Status and Consensus Gauge */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-[#232f48] pb-3.5">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-sm">
              R{currentRoundNum}
            </div>
            {status === 'running' && (
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full animate-ping" />
            )}
          </div>
          <div>
            <div className="text-xs font-bold text-white flex items-center gap-2">
              <span>Debate Round {currentRoundNum}</span>
              {isArbiterThinking ? (
                <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-semibold flex items-center gap-1 border border-amber-500/30">
                  <Sparkles className="w-3 h-3 animate-spin" /> Arbiter Evaluating Consensus...
                </span>
              ) : isUnanimous ? (
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-semibold flex items-center gap-1 border border-emerald-500/30">
                  <CheckCircle2 className="w-3 h-3" /> Unanimous Consensus (100%)
                </span>
              ) : (
                <span className="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px] font-semibold border border-indigo-500/30">
                  {status === 'running' ? 'Active Cross-Critique' : status.toUpperCase()}
                </span>
              )}
            </div>
            <p className="text-[11px] text-gray-400 mt-0.5">
              {rounds.length === 1
                ? 'Round 1: Initial 360° Multi-Persona Proposals'
                : `Round ${currentRoundNum}: Universal Cross-Critique, Concessions & Hardening`}
            </p>
          </div>
        </div>

        {/* Consensus Meter */}
        <div className="flex items-center gap-3 bg-[#161f33] px-4 py-2 rounded-xl border border-[#232f48]">
          <div className="text-right">
            <div className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">Consensus Alignment</div>
            <div className="text-sm font-black text-white font-mono">{consensusScore}%</div>
          </div>
          <div className="w-28 bg-[#090d16] h-2.5 rounded-full overflow-hidden border border-[#232f48] relative">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                consensusScore >= 90
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                  : consensusScore >= 65
                  ? 'bg-gradient-to-r from-indigo-500 to-cyan-400'
                  : 'bg-gradient-to-r from-amber-500 to-rose-400'
              }`}
              style={{ width: `${consensusScore}%` }}
            />
          </div>
        </div>
      </div>

      {/* Horizontal Round Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {rounds.map((r) => {
          const isSelected = r.round_number === selectedRound;
          const isRoundCompleted = Boolean(r.completed_at || r.arbiter_eval);

          return (
            <button
              key={r.round_number}
              onClick={() => onSelectRound(r.round_number)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition border ${
                isSelected
                  ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-600/20'
                  : 'bg-[#161f33] border-[#232f48] text-gray-400 hover:text-white hover:border-gray-600'
              }`}
            >
              <span>Round {r.round_number}</span>
              {r.arbiter_eval?.is_unanimous ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              ) : isRoundCompleted ? (
                <span className="text-[10px] opacity-75 font-mono">({r.arbiter_eval?.consensus_score || 0}%)</span>
              ) : (
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
