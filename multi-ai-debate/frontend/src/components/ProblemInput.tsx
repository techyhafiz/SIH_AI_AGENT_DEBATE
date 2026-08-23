'use client';

import React, { useState } from 'react';
import { Sparkles, Play, BookOpen, Layers, Flame } from 'lucide-react';

interface ProblemInputProps {
  onStartDebate: (problemStatement: string, ministryDomain: string, autoAdvance: boolean) => void;
  isLoading: boolean;
  modelsCount: number;
}

const SIH_SAMPLE_PRESETS = [
  {
    title: 'Disaster Management (MHA)',
    domain: 'Ministry of Home Affairs & NDRF',
    problem:
      'Design a resilient, zero-internet-tolerant communication and resource dispatch system for disaster response teams during complete cellular blackout in cyclone/flood-hit zones.',
  },
  {
    title: 'Precision Agriculture',
    domain: 'Ministry of Agriculture & Farmers Welfare',
    problem:
      'Develop an edge-AI multimodal diagnostic solution for low-end Android smartphones to identify 50+ crop diseases in vernacular Indian languages with zero server latency.',
  },
  {
    title: 'Railway Safety & Acoustics',
    domain: 'Ministry of Railways (RDSO)',
    problem:
      'Architect an acoustic AI sensory gateway along railway tracks capable of detecting minute wheel bearings and hairline rail fractures under 120 km/h train speeds with sub-second alert dispatch.',
  },
];

export function ProblemInput({ onStartDebate, isLoading, modelsCount }: ProblemInputProps) {
  const [problemStatement, setProblemStatement] = useState('');
  const [ministryDomain, setMinistryDomain] = useState('Smart India Hackathon (General)');
  const [autoAdvance, setAutoAdvance] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!problemStatement.trim()) return;
    onStartDebate(problemStatement.trim(), ministryDomain, autoAdvance);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-[#111827] border border-[#232f48] rounded-2xl shadow-2xl relative overflow-hidden">
      {/* Decorative gradient blur */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      <form onSubmit={handleSubmit} className="relative z-10 space-y-5">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-[#232f48] pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500 text-white shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-wide">Smart India Hackathon (SIH) Problem Brief</h1>
              <p className="text-xs text-gray-400">All configured AIs will debate across infinite rounds to construct an authoritative solution</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-400 flex items-center gap-1.5 cursor-pointer bg-[#161f33] px-3 py-1.5 rounded-lg border border-[#232f48]">
              <input
                type="checkbox"
                checked={autoAdvance}
                onChange={(e) => setAutoAdvance(e.target.checked)}
                className="rounded border-gray-700 text-indigo-600 focus:ring-indigo-500 bg-[#090d16]"
              />
              <span className="font-medium text-gray-300">Continuous Infinite Rounds</span>
            </label>
          </div>
        </div>

        {/* SIH Presets */}
        <div className="space-y-1.5">
          <div className="flex items-center gap-1.5 text-xs text-gray-400 font-medium">
            <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
            <span>Load Quick SIH Preset Problem:</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            {SIH_SAMPLE_PRESETS.map((preset) => (
              <button
                key={preset.title}
                type="button"
                onClick={() => {
                  setProblemStatement(preset.problem);
                  setMinistryDomain(preset.domain);
                }}
                className="text-left p-3 rounded-xl bg-[#161f33] hover:bg-[#1f2b47] border border-[#232f48] hover:border-indigo-500/40 transition group"
              >
                <div className="text-xs font-semibold text-gray-200 group-hover:text-indigo-400 transition truncate">
                  {preset.title}
                </div>
                <div className="text-[11px] text-gray-400 truncate mt-0.5">{preset.domain}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Ministry / Domain Input */}
        <div>
          <label className="block text-xs font-medium text-gray-300 mb-1">
            Target Ministry / Organization / Domain
          </label>
          <input
            type="text"
            value={ministryDomain}
            onChange={(e) => setMinistryDomain(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-[#090d16] border border-[#232f48] text-white focus:outline-none focus:border-indigo-500 text-xs font-medium"
            placeholder="e.g. Ministry of Power / Healthcare / Smart Cities"
          />
        </div>

        {/* Problem Statement Textarea */}
        <div>
          <label className="block text-xs font-medium text-gray-300 mb-1">
            Problem Statement & Constraints
          </label>
          <textarea
            rows={4}
            value={problemStatement}
            onChange={(e) => setProblemStatement(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-[#090d16] border border-[#232f48] text-white focus:outline-none focus:border-indigo-500 text-sm placeholder-gray-500"
            placeholder="Describe the problem statement, ground reality requirements, scale, and constraints..."
            required
          />
        </div>

        {/* Launch Button */}
        <div className="flex items-center justify-between pt-2">
          <div className="text-xs text-gray-400 flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>
              <strong>{modelsCount}</strong> AI Debaters Ready
            </span>
          </div>

          <button
            type="submit"
            disabled={isLoading || !problemStatement.trim() || modelsCount < 2}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white text-sm font-bold shadow-lg shadow-indigo-600/30 transition disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <Flame className="w-4 h-4 animate-spin text-amber-300" /> Initializing Debate Arena...
              </span>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current group-hover:translate-x-0.5 transition" />
                Launch Multi-AI Debate
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
