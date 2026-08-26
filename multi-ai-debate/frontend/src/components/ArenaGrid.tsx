'use client';

import React, { useState } from 'react';
import { DebaterResponse, ModelConfig } from '@/types/debate';
import {
  Cpu,
  Clock,
  Shield,
  Zap,
  Flame,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  ThumbsUp,
  AlertOctagon,
  Sparkles,
} from 'lucide-react';

interface ArenaGridProps {
  models: ModelConfig[];
  responses: Record<string, DebaterResponse>;
  activeTokens: Record<string, string>;
  roundNumber: number;
  arbiterModelId: string;
}

export function ArenaGrid({
  models,
  responses,
  activeTokens,
  roundNumber,
  arbiterModelId,
}: ArenaGridProps) {
  const [expandedSection, setExpandedSection] = useState<Record<string, string>>({});

  const toggleSection = (modelId: string, section: string) => {
    const key = `${modelId}_${section}`;
    setExpandedSection((prev) => ({
      ...prev,
      [key]: prev[key] ? '' : section,
    }));
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 w-full">
      {models.map((model) => {
        const resp = responses[model.id];
        const streamText = activeTokens[model.id];
        const isStreaming = streamText !== undefined && (!resp || resp.status === 'streaming');
        const isArbiter = model.id === arbiterModelId;

        return (
          <div
            key={model.id}
            className={`flex flex-col rounded-2xl border transition-all duration-300 shadow-xl overflow-hidden ${
              isStreaming
                ? 'border-indigo-500 bg-[#111827] shadow-indigo-500/10 ring-1 ring-indigo-500/30'
                : resp?.status === 'timeout'
                ? 'border-amber-500/50 bg-[#161219]'
                : resp?.status === 'error'
                ? 'border-rose-500/50 bg-[#191214]'
                : 'border-[#232f48] bg-[#111827]'
            }`}
          >
            {/* Model Card Header */}
            <div className="p-4 border-b border-[#232f48] bg-[#161f33] flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-[#090d16] border border-[#232f48] text-indigo-400">
                  <Cpu className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-xs font-bold text-white truncate max-w-[160px]">{model.name}</h3>
                    {isArbiter && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30">
                        Arbiter
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-gray-400 font-mono truncate max-w-[180px]">{model.model_id}</p>
                </div>
              </div>

              {/* Status Indicator */}
              <div className="flex items-center gap-1.5">
                {isStreaming ? (
                  <span className="flex items-center gap-1 text-[10px] text-indigo-300 bg-indigo-500/20 px-2 py-0.5 rounded-full border border-indigo-500/30 font-medium">
                    <Sparkles className="w-3 h-3 animate-spin text-cyan-400" /> Generating...
                  </span>
                ) : resp?.status === 'completed' ? (
                  <span className="flex items-center gap-1 text-[10px] text-emerald-300 bg-emerald-500/20 px-2 py-0.5 rounded-full border border-emerald-500/30 font-medium">
                    <CheckCircle className="w-3 h-3 text-emerald-400" /> Done ({resp.elapsed_seconds.toFixed(1)}s)
                  </span>
                ) : resp?.status === 'timeout' ? (
                  <span className="flex items-center gap-1 text-[10px] text-amber-300 bg-amber-500/20 px-2 py-0.5 rounded-full border border-amber-500/30 font-medium">
                    <Clock className="w-3 h-3 text-amber-400" /> Timed Out
                  </span>
                ) : (
                  <span className="text-[10px] text-gray-500 bg-[#090d16] px-2 py-0.5 rounded-full border border-[#232f48]">
                    Waiting
                  </span>
                )}
              </div>
            </div>

            {/* Content Body */}
            <div className="p-4 flex-1 flex flex-col space-y-3 overflow-y-auto max-h-[580px]">
              {/* Live Progress Status Indicator */}
              {isStreaming && (
                <div className="p-3.5 rounded-xl bg-[#090d16] border border-indigo-500/30 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5 text-xs font-bold text-indigo-300">
                      <Sparkles className="w-3.5 h-3.5 animate-spin text-cyan-400" /> Formulating Response...
                    </span>
                    <span className="text-[10px] font-mono font-bold text-cyan-400 animate-pulse">
                      Active
                    </span>
                  </div>
                  <div className="w-full bg-[#161f33] h-1.5 rounded-full overflow-hidden">
                    <div className="bg-indigo-500 h-full rounded-full animate-pulse w-3/4" />
                  </div>
                  <p className="text-[10px] text-gray-400 italic">
                    Synthesizing domain logic and architectural paradigms...
                  </p>
                </div>
              )}

              {/* Parsed Response & Multi-Personas */}
              {resp && resp.status === 'completed' && resp.structured && (
                <>
                  {/* Consensus Vote Pill. A null vote means the model never stated a readable
                      position - it is an abstention, not a DISAGREE, and it is excluded from the
                      consensus average, so it must not be painted red. */}
                  <div className="flex items-center justify-between p-2 rounded-xl bg-[#161f33] border border-[#232f48]">
                    <span className="text-[10px] text-gray-400 font-semibold uppercase">Debater Vote</span>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                          !resp.structured.consensus_vote
                            ? 'bg-slate-500/20 border-slate-500/30 text-slate-300'
                            : resp.structured.consensus_vote === 'AGREE'
                            ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-300'
                            : resp.structured.consensus_vote === 'NEEDS_REFINEMENT'
                            ? 'bg-amber-500/20 border-amber-500/30 text-amber-300'
                            : 'bg-rose-500/20 border-rose-500/30 text-rose-300'
                        }`}
                        title={
                          resp.structured.consensus_vote
                            ? undefined
                            : 'This turn did not return a readable position, so it is excluded from the consensus average.'
                        }
                      >
                        {resp.structured.consensus_vote
                          ? `${resp.structured.consensus_vote}${
                              resp.structured.agreement_percentage !== null &&
                              resp.structured.agreement_percentage !== undefined
                                ? ` (${resp.structured.agreement_percentage}%)`
                                : ''
                            }`
                          : 'NOT SCORED'}
                      </span>
                    </div>
                  </div>

                  {/* Refined Solution Summary */}
                  <div className="p-3 rounded-xl bg-[#161f33] border border-[#232f48] space-y-1">
                    <div className="text-[11px] font-bold text-indigo-300 flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5 text-cyan-400" /> Proposed SIH Solution & Insights
                    </div>
                    <p className="text-xs text-gray-200 leading-relaxed line-clamp-5">
                      {resp.structured.refined_solution || resp.structured.architect_lens || resp.structured.critic_lens || resp.structured.field_hardware_lens || resp.structured.security_compliance_lens || resp.raw_text}
                    </p>
                  </div>


                  {/* 4 Cognitive Personas Accordion */}
                  <div className="space-y-1.5 pt-1">
                    <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                      Cognitive Persona Lenses:
                    </div>

                    {/* Architect */}
                    {resp.structured.architect_lens && (
                      <div className="rounded-lg bg-[#090d16] border border-[#232f48] overflow-hidden text-xs">
                        <button
                          type="button"
                          onClick={() => toggleSection(model.id, 'architect')}
                          className="w-full px-2.5 py-1.5 flex items-center justify-between text-left hover:bg-[#161f33] text-gray-300 font-semibold"
                        >
                          <span className="flex items-center gap-1 text-[11px] text-cyan-300">
                            🏛️ Lead Architect
                          </span>
                          {expandedSection[`${model.id}_architect`] ? (
                            <ChevronUp className="w-3 h-3" />
                          ) : (
                            <ChevronDown className="w-3 h-3" />
                          )}
                        </button>
                        {expandedSection[`${model.id}_architect`] && (
                          <div className="p-2.5 text-[11px] text-gray-300 border-t border-[#232f48] leading-relaxed bg-[#111827]">
                            {resp.structured.architect_lens}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Critic */}
                    {resp.structured.critic_devil_advocate_lens && (
                      <div className="rounded-lg bg-[#090d16] border border-[#232f48] overflow-hidden text-xs">
                        <button
                          type="button"
                          onClick={() => toggleSection(model.id, 'critic')}
                          className="w-full px-2.5 py-1.5 flex items-center justify-between text-left hover:bg-[#161f33] text-gray-300 font-semibold"
                        >
                          <span className="flex items-center gap-1 text-[11px] text-amber-300">
                            😈 Devil&apos;s Advocate / Critic
                          </span>
                          {expandedSection[`${model.id}_critic`] ? (
                            <ChevronUp className="w-3 h-3" />
                          ) : (
                            <ChevronDown className="w-3 h-3" />
                          )}
                        </button>
                        {expandedSection[`${model.id}_critic`] && (
                          <div className="p-2.5 text-[11px] text-gray-300 border-t border-[#232f48] leading-relaxed bg-[#111827]">
                            {resp.structured.critic_devil_advocate_lens}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Security */}
                    {resp.structured.security_reliability_lens && (
                      <div className="rounded-lg bg-[#090d16] border border-[#232f48] overflow-hidden text-xs">
                        <button
                          type="button"
                          onClick={() => toggleSection(model.id, 'security')}
                          className="w-full px-2.5 py-1.5 flex items-center justify-between text-left hover:bg-[#161f33] text-gray-300 font-semibold"
                        >
                          <span className="flex items-center gap-1 text-[11px] text-emerald-300">
                            🛡️ Security & Reliability
                          </span>
                          {expandedSection[`${model.id}_security`] ? (
                            <ChevronUp className="w-3 h-3" />
                          ) : (
                            <ChevronDown className="w-3 h-3" />
                          )}
                        </button>
                        {expandedSection[`${model.id}_security`] && (
                          <div className="p-2.5 text-[11px] text-gray-300 border-t border-[#232f48] leading-relaxed bg-[#111827]">
                            {resp.structured.security_reliability_lens}
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Critiques Launched Against Peers */}
                  {resp.structured.critiques && resp.structured.critiques.length > 0 && (
                    <div className="space-y-1.5 pt-1">
                      <div className="text-[10px] font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1">
                        <Flame className="w-3 h-3" /> Counter-Arguments Launched:
                      </div>
                      {resp.structured.critiques.map((c, i) => (
                        <div
                          key={i}
                          className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-[11px] space-y-0.5"
                        >
                          <div className="font-bold text-rose-300 flex items-center justify-between">
                            <span>Against: {c.target_model_name}</span>
                          </div>
                          <div className="text-gray-300 font-medium">{c.flaw_identified}</div>
                          <div className="text-gray-400 text-[10px] italic">{c.counter_argument}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Concessions Made */}
                  {resp.structured.concessions_and_defenses &&
                    resp.structured.concessions_and_defenses.length > 0 && (
                      <div className="space-y-1.5 pt-1">
                        <div className="text-[10px] font-bold text-teal-400 uppercase tracking-wider flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" /> Concessions & Adaptations:
                        </div>
                        {resp.structured.concessions_and_defenses.map((cd, i) => (
                          <div
                            key={i}
                            className="p-2 rounded-lg bg-teal-500/10 border border-teal-500/20 text-[11px] space-y-0.5"
                          >
                            <div className="text-teal-300 font-semibold">
                              Conceded to {cd.conceded_to}: {cd.conceded_point}
                            </div>
                            <div className="text-gray-300 text-[10px]">{cd.adaptation}</div>
                          </div>
                        ))}
                      </div>
                    )}

                  {/* Positives & Negatives Pills */}
                  <div className="space-y-1.5 pt-1">
                    {resp.structured.positives_of_approach?.length > 0 && (
                      <div>
                        <span className="text-[10px] font-bold text-emerald-400 flex items-center gap-1 mb-1">
                          <ThumbsUp className="w-2.5 h-2.5" /> Positives:
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {resp.structured.positives_of_approach.map((p, i) => (
                            <span
                              key={i}
                              className="text-[10px] px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-300 border border-emerald-500/20"
                            >
                              {p}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {resp.structured.negatives_and_risks?.length > 0 && (
                      <div>
                        <span className="text-[10px] font-bold text-rose-400 flex items-center gap-1 mb-1">
                          <AlertOctagon className="w-2.5 h-2.5" /> Negatives / Risks:
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {resp.structured.negatives_and_risks.map((n, i) => (
                            <span
                              key={i}
                              className="text-[10px] px-2 py-0.5 rounded-md bg-rose-500/10 text-rose-300 border border-rose-500/20"
                            >
                              {n}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
