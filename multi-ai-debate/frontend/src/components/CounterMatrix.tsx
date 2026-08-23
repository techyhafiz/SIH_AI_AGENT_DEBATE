'use client';

import React from 'react';
import { RoundData } from '@/types/debate';
import { Swords, ArrowRight, ShieldCheck, Flame } from 'lucide-react';

interface CounterMatrixProps {
  currentRoundData?: RoundData;
}

export function CounterMatrix({ currentRoundData }: CounterMatrixProps) {
  if (!currentRoundData || !currentRoundData.responses) return null;

  const allCritiques: {
    sourceName: string;
    targetName: string;
    flaw: string;
    counter: string;
  }[] = [];

  Object.values(currentRoundData.responses).forEach((resp) => {
    if (resp.structured && resp.structured.critiques) {
      resp.structured.critiques.forEach((c) => {
        allCritiques.push({
          sourceName: resp.model_name,
          targetName: c.target_model_name || 'Peer Model',
          flaw: c.flaw_identified,
          counter: c.counter_argument,
        });
      });
    }
  });

  if (allCritiques.length === 0) return null;

  return (
    <div className="w-full bg-[#111827] border border-[#232f48] rounded-2xl p-5 shadow-xl space-y-3">
      <div className="flex items-center gap-2 text-xs font-bold text-white uppercase tracking-wider">
        <Swords className="w-4 h-4 text-rose-400" />
        <span>Universal Cross-Critique Friction Matrix (Round {currentRoundData.round_number})</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-[#232f48] text-gray-400 font-semibold bg-[#161f33]/50">
              <th className="p-3">Source Challenger</th>
              <th className="p-3">Targeted Peer</th>
              <th className="p-3">Identified Architectural Flaw</th>
              <th className="p-3">Rigorous Counter-Argument</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#232f48]">
            {allCritiques.map((item, idx) => (
              <tr key={idx} className="hover:bg-[#161f33]/30 transition text-gray-300">
                <td className="p-3 font-semibold text-rose-300 flex items-center gap-1.5 whitespace-nowrap">
                  <Flame className="w-3.5 h-3.5 text-rose-400" /> {item.sourceName}
                </td>
                <td className="p-3 text-cyan-300 font-medium whitespace-nowrap">
                  <div className="flex items-center gap-1">
                    <ArrowRight className="w-3 h-3 text-gray-500" /> {item.targetName}
                  </div>
                </td>
                <td className="p-3 text-gray-200 font-medium max-w-xs">{item.flaw}</td>
                <td className="p-3 text-gray-400 text-[11px] leading-relaxed max-w-sm italic">
                  {item.counter}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
