'use client';

import React, { useState } from 'react';
import { TimeoutAlert, ModelConfig } from '@/types/debate';
import { AlertTriangle, Clock, RefreshCw, XCircle, Settings, Check, Key, Globe, Cpu } from 'lucide-react';

interface TimeoutAlertModalProps {
  alert: TimeoutAlert | null;
  models: ModelConfig[];
  onClose: () => void;
  onUpdateAndRetry: (updatedConfig: ModelConfig) => void;
  onDropModel: (modelId: string) => void;
}

export function TimeoutAlertModal({
  alert,
  models,
  onClose,
  onUpdateAndRetry,
  onDropModel,
}: TimeoutAlertModalProps) {
  const [isEditing, setIsEditing] = useState(false);
  
  if (!alert) return null;

  const currentModel = models.find((m) => m.id === alert.model_id) || {
    id: alert.model_id,
    name: alert.model_name,
    base_url: 'https://openrouter.ai/api/v1',
    api_key: '',
    model_id: 'deepseek/deepseek-r1',
    provider_type: 'openai_compatible' as const,
    timeout_seconds: alert.timeout_seconds,
    is_arbiter: false,
    enabled: true,
    temperature: 0.7,
  };

  const [editConfig, setEditConfig] = useState<ModelConfig>(currentModel);

  const handleSaveAndRetry = () => {
    onUpdateAndRetry(editConfig);
    onClose();
  };

  const handleDrop = () => {
    onDropModel(alert.model_id);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-lg bg-[#111827] border border-amber-500/40 rounded-2xl shadow-2xl overflow-hidden shadow-amber-500/10">
        {/* Header */}
        <div className="p-5 bg-amber-500/10 border-b border-amber-500/20 flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">AI Debater Latency Alert</h3>
            <p className="text-xs text-amber-300/80">
              Model <strong>{alert.model_name}</strong> exceeded response threshold in Round {alert.round_number}
            </p>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <div className="p-3.5 rounded-xl bg-[#161f33] border border-[#232f48] space-y-2 text-xs">
            <div className="flex items-center justify-between text-gray-300">
              <span className="flex items-center gap-1.5 text-gray-400">
                <Clock className="w-4 h-4 text-amber-400" /> Elapsed Duration:
              </span>
              <strong className="text-amber-300 font-mono">
                {Math.round(alert.elapsed_seconds)}s / {alert.timeout_seconds}s limit
              </strong>
            </div>
            <p className="text-gray-400 text-[11px] leading-relaxed">
              Third-party API latency or provider queue delay triggered the timeout watchdog. The remaining debaters are paused waiting for your action.
            </p>
          </div>

          {isEditing ? (
            <div className="space-y-3 p-4 rounded-xl bg-[#090d16] border border-[#232f48] text-xs">
              <h4 className="font-bold text-gray-200 flex items-center gap-1.5">
                <Settings className="w-4 h-4 text-indigo-400" /> Update Connection Settings
              </h4>

              <div>
                <label className="text-gray-400 mb-1 flex items-center gap-1">
                  <Globe className="w-3 h-3 text-indigo-400" /> Base URL
                </label>
                <input
                  type="text"
                  value={editConfig.base_url}
                  onChange={(e) => setEditConfig({ ...editConfig, base_url: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-[#161f33] border border-[#232f48] text-white font-mono text-[11px]"
                />
              </div>

              <div>
                <label className="text-gray-400 mb-1 flex items-center gap-1">
                  <Cpu className="w-3 h-3 text-cyan-400" /> Model ID
                </label>
                <input
                  type="text"
                  value={editConfig.model_id}
                  onChange={(e) => setEditConfig({ ...editConfig, model_id: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-[#161f33] border border-[#232f48] text-white font-mono text-[11px]"
                />
              </div>

              <div>
                <label className="text-gray-400 mb-1 flex items-center gap-1">
                  <Key className="w-3 h-3 text-amber-400" /> API Key
                </label>
                <input
                  type="password"
                  value={editConfig.api_key}
                  onChange={(e) => setEditConfig({ ...editConfig, api_key: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-[#161f33] border border-[#232f48] text-white font-mono text-[11px]"
                  placeholder="New API Key..."
                />
              </div>

              <div>
                <label className="text-gray-400 mb-1 flex items-center gap-1">
                  <Clock className="w-3 h-3 text-emerald-400" /> Timeout (Seconds)
                </label>
                <input
                  type="number"
                  value={editConfig.timeout_seconds}
                  onChange={(e) => setEditConfig({ ...editConfig, timeout_seconds: parseInt(e.target.value) || 600 })}
                  className="w-full px-3 py-2 rounded-lg bg-[#161f33] border border-[#232f48] text-white font-mono text-[11px]"
                />
              </div>
            </div>
          ) : null}

          {/* Action Buttons */}
          <div className="space-y-2 pt-2">
            {!isEditing ? (
              <button
                type="button"
                onClick={() => setIsEditing(true)}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-[#161f33] hover:bg-[#1f2b47] border border-indigo-500/30 text-indigo-300 font-semibold text-xs transition"
              >
                <Settings className="w-4 h-4" /> Edit Model API Settings & Retry
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSaveAndRetry}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition"
              >
                <Check className="w-4 h-4" /> Save Settings & Re-Run Turn
              </button>
            )}

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={handleSaveAndRetry}
                className="flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-[#161f33] hover:bg-[#1f2b47] border border-[#232f48] text-gray-300 font-medium text-xs transition"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Rejoin Round
              </button>

              <button
                type="button"
                onClick={handleDrop}
                className="flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 font-medium text-xs transition"
              >
                <XCircle className="w-3.5 h-3.5" /> Drop Model & Continue
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
