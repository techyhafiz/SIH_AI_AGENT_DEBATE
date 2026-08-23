'use client';

import React, { useState } from 'react';
import { ModelConfig } from '@/types/debate';
import { Settings, Plus, Trash2, CheckCircle2, XCircle, Loader2, Key, Globe, Cpu, Clock, ShieldCheck, Eye, EyeOff } from 'lucide-react';

interface ModelConfigDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  models: ModelConfig[];
  onSaveModels: (models: ModelConfig[]) => void;
  arbiterModelId: string;
  onSetArbiterId: (id: string) => void;
}

const PRESET_ENDPOINTS = [
  { name: 'OpenRouter', base_url: 'https://openrouter.ai/api/v1', sample_model: 'anthropic/claude-3.5-sonnet' },
  { name: 'Groq Cloud', base_url: 'https://api.groq.com/openai/v1', sample_model: 'llama-3.3-70b-versatile' },
  { name: 'Local Ollama', base_url: 'http://localhost:11434/v1', sample_model: 'deepseek-r1:latest' },
  { name: 'DeepSeek Official', base_url: 'https://api.deepseek.com', sample_model: 'deepseek-reasoner' },
  { name: 'OpenAI Direct', base_url: 'https://api.openai.com/v1', sample_model: 'gpt-4o' },
];

export function ModelConfigDrawer({
  isOpen,
  onClose,
  models,
  onSaveModels,
  arbiterModelId,
  onSetArbiterId,
}: ModelConfigDrawerProps) {
  const [localModels, setLocalModels] = useState<ModelConfig[]>(models);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; msg: string; latency?: number }>>({});
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});

  if (!isOpen) return null;

  const handleAddModel = () => {
    const newId = 'm_' + Math.random().toString(36).substring(2, 8);
    const newModel: ModelConfig = {
      id: newId,
      name: `Debater Model ${localModels.length + 1}`,
      base_url: 'https://openrouter.ai/api/v1',
      api_key: '',
      model_id: 'deepseek/deepseek-r1',
      provider_type: 'openai_compatible',
      timeout_seconds: 600,
      is_arbiter: localModels.length === 0,
      enabled: true,
      temperature: 0.7,
    };
    setLocalModels([...localModels, newModel]);
    if (localModels.length === 0) {
      onSetArbiterId(newId);
    }
  };

  const handleRemoveModel = (id: string) => {
    const filtered = localModels.filter((m) => m.id !== id);
    setLocalModels(filtered);
    if (arbiterModelId === id && filtered.length > 0) {
      onSetArbiterId(filtered[0].id);
    }
  };

  const handleUpdateField = (id: string, field: keyof ModelConfig, value: any) => {
    setLocalModels((prev) =>
      prev.map((m) => (m.id === id ? { ...m, [field]: value } : m))
    );
  };

  const handleTestConnection = async (model: ModelConfig) => {
    setTestingId(model.id);
    setTestResults((prev) => ({ ...prev, [model.id]: { success: false, msg: 'Testing connection...' } }));
    try {
      const res = await fetch('/api/models/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_url: model.base_url,
          api_key: model.api_key,
          model_id: model.model_id,
          provider_type: model.provider_type,
          timeout_seconds: 30,
        }),
      });
      const data = await res.json();
      setTestResults((prev) => ({
        ...prev,
        [model.id]: {
          success: data.success,
          msg: data.message,
          latency: data.latency_ms,
        },
      }));
    } catch (e: any) {
      setTestResults((prev) => ({
        ...prev,
        [model.id]: { success: false, msg: `Error: ${e.message}` },
      }));
    } finally {
      setTestingId(null);
    }
  };

  const handleSaveAndClose = () => {
    onSaveModels(localModels);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/70 backdrop-blur-sm transition-opacity">
      <div className="w-full max-w-2xl h-full bg-[#111827] border-l border-[#232f48] shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-[#232f48] flex items-center justify-between bg-[#161f33]">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Settings className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">AI Debater Endpoints & Models</h2>
              <p className="text-xs text-gray-400">Configure independent Base URLs, API keys & latency timeouts per AI</p>
            </div>
          </div>
          <button
            onClick={handleAddModel}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition"
          >
            <Plus className="w-4 h-4" /> Add AI Model
          </button>
        </div>

        {/* Models List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {localModels.map((model, idx) => (
            <div
              key={model.id}
              className={`p-5 rounded-xl border transition ${
                model.id === arbiterModelId
                  ? 'border-amber-500/50 bg-[#161f33]/90 shadow-lg shadow-amber-500/10'
                  : 'border-[#232f48] bg-[#161f33]/50'
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-bold flex items-center justify-center border border-indigo-500/30">
                    {idx + 1}
                  </span>
                  <input
                    type="text"
                    value={model.name}
                    onChange={(e) => handleUpdateField(model.id, 'name', e.target.value)}
                    className="bg-transparent text-white font-bold text-sm border-b border-transparent hover:border-gray-600 focus:border-indigo-500 focus:outline-none px-1"
                    placeholder="AI Model Name"
                  />
                  {model.id === arbiterModelId && (
                    <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold border border-amber-500/30 flex items-center gap-1">
                      <ShieldCheck className="w-3 h-3" /> Master Arbiter
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onSetArbiterId(model.id)}
                    className={`text-xs px-2.5 py-1 rounded-md border transition ${
                      model.id === arbiterModelId
                        ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
                        : 'border-[#232f48] text-gray-400 hover:text-white'
                    }`}
                  >
                    Set as Arbiter
                  </button>
                  {localModels.length > 2 && (
                    <button
                      onClick={() => handleRemoveModel(model.id)}
                      className="p-1 text-gray-500 hover:text-rose-400 transition"
                      title="Remove AI"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* Endpoint Preset Pills */}
              <div className="flex flex-wrap gap-1.5 mb-3">
                <span className="text-[11px] text-gray-400 mr-1 flex items-center">Presets:</span>
                {PRESET_ENDPOINTS.map((preset) => (
                  <button
                    key={preset.name}
                    type="button"
                    onClick={() => {
                      handleUpdateField(model.id, 'base_url', preset.base_url);
                      handleUpdateField(model.id, 'model_id', preset.sample_model);
                    }}
                    className="text-[10px] px-2 py-0.5 rounded bg-[#090d16] hover:bg-[#232f48] text-gray-300 border border-[#232f48] transition"
                  >
                    {preset.name}
                  </button>
                ))}
              </div>

              {/* Input Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                {/* Base URL */}
                <div>
                  <label className="text-gray-400 flex items-center gap-1 mb-1 font-medium">
                    <Globe className="w-3.5 h-3.5 text-indigo-400" /> Base URL
                  </label>
                  <input
                    type="text"
                    value={model.base_url}
                    onChange={(e) => handleUpdateField(model.id, 'base_url', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[#090d16] border border-[#232f48] text-white focus:outline-none focus:border-indigo-500 font-mono text-[11px]"
                    placeholder="https://openrouter.ai/api/v1"
                  />
                </div>

                {/* Model ID */}
                <div>
                  <label className="text-gray-400 flex items-center gap-1 mb-1 font-medium">
                    <Cpu className="w-3.5 h-3.5 text-cyan-400" /> Model ID
                  </label>
                  <input
                    type="text"
                    value={model.model_id}
                    onChange={(e) => handleUpdateField(model.id, 'model_id', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[#090d16] border border-[#232f48] text-white focus:outline-none focus:border-indigo-500 font-mono text-[11px]"
                    placeholder="deepseek/deepseek-r1"
                  />
                </div>

                {/* API Key */}
                <div>
                  <label className="text-gray-400 flex items-center justify-between mb-1 font-medium">
                    <span className="flex items-center gap-1">
                      <Key className="w-3.5 h-3.5 text-amber-400" /> API Key
                    </span>
                    <button
                      type="button"
                      onClick={() => setShowKeys((p) => ({ ...p, [model.id]: !p[model.id] }))}
                      className="text-gray-500 hover:text-gray-300"
                    >
                      {showKeys[model.id] ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                    </button>
                  </label>
                  <input
                    type={showKeys[model.id] ? 'text' : 'password'}
                    value={model.api_key}
                    onChange={(e) => handleUpdateField(model.id, 'api_key', e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[#090d16] border border-[#232f48] text-white focus:outline-none focus:border-indigo-500 font-mono text-[11px]"
                    placeholder="sk-... (Leave empty for local Ollama)"
                  />
                </div>

                {/* Timeout Limit */}
                <div>
                  <label className="text-gray-400 flex items-center gap-1 mb-1 font-medium">
                    <Clock className="w-3.5 h-3.5 text-emerald-400" /> Timeout (Seconds)
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      value={model.timeout_seconds}
                      onChange={(e) => handleUpdateField(model.id, 'timeout_seconds', parseInt(e.target.value) || 600)}
                      className="w-full px-3 py-2 rounded-lg bg-[#090d16] border border-[#232f48] text-white focus:outline-none focus:border-indigo-500 font-mono text-[11px]"
                    />
                    <span className="text-[10px] text-gray-500 whitespace-nowrap">
                      ({Math.round(model.timeout_seconds / 60)} min)
                    </span>
                  </div>
                </div>
              </div>

              {/* Probe Test Connection Button & Result */}
              <div className="mt-3 pt-3 border-t border-[#232f48] flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => handleTestConnection(model)}
                  disabled={testingId === model.id}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#090d16] hover:bg-[#232f48] border border-[#232f48] text-gray-300 text-xs transition disabled:opacity-50"
                >
                  {testingId === model.id ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" /> Testing Probe...
                    </>
                  ) : (
                    'Probe Test Endpoint'
                  )}
                </button>

                {testResults[model.id] && (
                  <div
                    className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-md border ${
                      testResults[model.id].success
                        ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                        : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                    }`}
                  >
                    {testResults[model.id].success ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <XCircle className="w-3.5 h-3.5 text-rose-400" />
                    )}
                    <span className="truncate max-w-[280px]">{testResults[model.id].msg}</span>
                    {testResults[model.id].latency && (
                      <span className="text-[10px] text-gray-400">({testResults[model.id].latency}ms)</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-5 border-t border-[#232f48] bg-[#161f33] flex items-center justify-between">
          <p className="text-xs text-gray-400">All endpoints will wait synchronously on each debate round.</p>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-[#090d16] hover:bg-[#232f48] text-gray-300 text-xs font-semibold transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveAndClose}
              className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition"
            >
              Save Configuration
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
