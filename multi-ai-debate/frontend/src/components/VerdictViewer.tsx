'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Download, Copy, Check, Trophy, FileText, Share2, Sparkles } from 'lucide-react';

interface VerdictViewerProps {
  markdownReport: string;
  sessionId: string;
  totalRounds: number;
}

export function VerdictViewer({ markdownReport, sessionId, totalRounds }: VerdictViewerProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(markdownReport);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleDownload = () => {
    const blob = new Blob([markdownReport], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `SIH_Master_Consensus_Verdict_${sessionId}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="w-full max-w-5xl mx-auto bg-[#111827] border border-amber-500/40 rounded-3xl p-6 md:p-8 shadow-2xl space-y-6 relative overflow-hidden shadow-amber-500/10">
      {/* Decorative Golden Glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#232f48] pb-6">
        <div className="flex items-center gap-3.5">
          <div className="p-3 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-600 text-black shadow-lg shadow-amber-500/30">
            <Trophy className="w-7 h-7 fill-current" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-extrabold text-white">Smart India Hackathon Master Consensus Verdict</h2>
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-500/30">
                100% Unanimous Agreement
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              Debate successfully converged after <strong>{totalRounds}</strong> rigorous cross-examination rounds
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#161f33] hover:bg-[#1f2b47] border border-[#232f48] text-gray-200 text-xs font-semibold transition"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" /> Copied to Clipboard
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-indigo-400" /> Copy Markdown
              </>
            )}
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black font-bold text-xs shadow-lg shadow-amber-500/25 transition"
          >
            <Download className="w-4 h-4" /> Download .md File
          </button>
        </div>
      </div>

      {/* Rendered Markdown Body */}
      <div className="relative z-10 p-6 md:p-8 rounded-2xl bg-[#090d16] border border-[#232f48] text-gray-200 text-sm leading-relaxed prose prose-invert max-w-none prose-headings:text-white prose-a:text-indigo-400 prose-table:border-collapse prose-th:border prose-th:border-[#232f48] prose-th:p-2 prose-td:border prose-td:border-[#232f48] prose-td:p-2">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdownReport}</ReactMarkdown>
      </div>
    </div>
  );
}
