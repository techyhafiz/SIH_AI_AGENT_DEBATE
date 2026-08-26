'use client';

import React, { useEffect, useState } from 'react';
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

  const fallbackModel: ModelConfig = {
    id: alert?.model_id || '',
    name: alert?.model_name || 'Timed-out model',
    base_url: 'https://openrouter.ai/api/v1',
    api_key: '',
    model_id: 'deepseek/deepseek-r1',
    provider_type: 'openai_compatible' as const,
    timeout_seconds: alert?.timeout_seconds || 600,
    is_arbiter: false,
    enabled: true,
    temperature: 0.7,
  };
  const currentModel = alert ? models.find((model) => model.id === alert.model_id) || fallbackModel : fallbackModel;
  const [editConfig, setEditConfig] = useState<ModelConfig>(currentModel);

  useEffect(() => {
    if (!alert) return;
    const model = models.find((candidate) => candidate.id === alert.model_id) || {
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
    setEditConfig(model);
    setIsEditing(false);
  }, [alert, models]);

  const handleSaveAndRetry = () => {
    onUpdateAndRetry(editConfig);
    onClose();
  };

  const handleDrop = () => {
    if (!alert) return;
    onDropModel(alert.model_id);
    onClose();
  };

  if (!alert) return null;

  return (
    <div className="modal-backdrop fixed inset-0 z-[70] flex items-center justify-center p-4">
      <div className="modal-panel w-full max-w-lg overflow-hidden" role="alertdialog" aria-modal="true" aria-labelledby="timeout-dialog-title" aria-describedby="timeout-dialog-description">
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-[var(--line)] bg-amber-500/10 p-5">
          <div className="rounded-xl bg-amber-500/15 p-2.5 text-[var(--warning)]">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h3 id="timeout-dialog-title" className="text-base font-semibold text-[var(--foreground)]">Model response timed out</h3>
            <p className="mt-1 text-xs text-[var(--muted)]">
              <strong>{alert.model_name}</strong> exceeded its response window in round {alert.round_number}.
            </p>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <div className="space-y-2 rounded-xl border border-[var(--line)] bg-[var(--surface-muted)] p-3.5 text-xs">
            <div className="flex items-center justify-between text-[var(--muted-strong)]">
              <span className="flex items-center gap-1.5 text-[var(--muted)]">
                <Clock className="w-4 h-4 text-[var(--warning)]" /> Elapsed duration
              </span>
              <strong className="font-mono text-[var(--warning)]">
                {Math.round(alert.elapsed_seconds)}s / {alert.timeout_seconds}s limit
              </strong>
            </div>
            <p id="timeout-dialog-description" className="text-[11px] leading-relaxed text-[var(--muted)]">
              The provider may be queued or unavailable. Retry with the current settings, update the endpoint, or exclude this model so the session can continue.
            </p>
          </div>

          {isEditing ? (
            <div className="space-y-3 rounded-xl border border-[var(--line)] bg-[var(--surface-muted)] p-4 text-xs">
              <h4 className="flex items-center gap-1.5 font-semibold text-[var(--foreground)]">
                <Settings className="w-4 h-4 text-[var(--primary)]" /> Update connection settings
              </h4>

              <div>
                  <label className="mb-1 flex items-center gap-1 text-[var(--muted)]">
                    <Globe className="w-3 h-3 text-[var(--primary)]" /> Base URL
                </label>
                <input
                  type="text"
                  value={editConfig.base_url}
                  onChange={(e) => setEditConfig({ ...editConfig, base_url: e.target.value })}
                    className="w-full rounded-lg border border-[var(--line)] bg-[var(--surface)] px-3 py-2 font-mono text-[11px] text-[var(--foreground)]"
                />
              </div>

              <div>
                  <label className="mb-1 flex items-center gap-1 text-[var(--muted)]">
                    <Cpu className="w-3 h-3 text-[var(--accent)]" /> Model ID
                </label>
                <input
                  type="text"
                  value={editConfig.model_id}
                  onChange={(e) => setEditConfig({ ...editConfig, model_id: e.target.value })}
                    className="w-full rounded-lg border border-[var(--line)] bg-[var(--surface)] px-3 py-2 font-mono text-[11px] text-[var(--foreground)]"
                />
              </div>

              <div>
                  <label className="mb-1 flex items-center gap-1 text-[var(--muted)]">
                    <Key className="w-3 h-3 text-[var(--warning)]" /> API key
                </label>
                <input
                  type="password"
                  value={editConfig.api_key}
                  onChange={(e) => setEditConfig({ ...editConfig, api_key: e.target.value })}
                    className="w-full rounded-lg border border-[var(--line)] bg-[var(--surface)] px-3 py-2 font-mono text-[11px] text-[var(--foreground)]"
                  placeholder="New API Key..."
                />
              </div>

              <div>
                  <label className="mb-1 flex items-center gap-1 text-[var(--muted)]">
                    <Clock className="w-3 h-3 text-[var(--success)]" /> Timeout (seconds)
                </label>
                <input
                  type="number"
                  value={editConfig.timeout_seconds}
                  onChange={(e) => setEditConfig({ ...editConfig, timeout_seconds: parseInt(e.target.value) || 600 })}
                    className="w-full rounded-lg border border-[var(--line)] bg-[var(--surface)] px-3 py-2 font-mono text-[11px] text-[var(--foreground)]"
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
                className="secondary-button w-full"
              >
                <Settings className="w-4 h-4" /> Edit connection settings
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSaveAndRetry}
                className="primary-button w-full"
              >
                <Check className="w-4 h-4" /> Save and retry turn
              </button>
            )}

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={handleSaveAndRetry}
                className="secondary-button"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Retry now
              </button>

              <button
                type="button"
                onClick={handleDrop}
                className="toolbar-button !text-[var(--danger)]"
              >
                <XCircle className="w-3.5 h-3.5" /> Exclude and continue
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
