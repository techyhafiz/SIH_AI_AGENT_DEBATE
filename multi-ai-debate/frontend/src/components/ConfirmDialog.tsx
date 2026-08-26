'use client';

import { AlertTriangle } from 'lucide-react';

interface ConfirmDialogProps {
  title: string;
  description: string;
  confirmLabel: string;
  tone?: 'default' | 'danger';
  onCancel: () => void;
  onConfirm: () => void;
}

export function ConfirmDialog({
  title,
  description,
  confirmLabel,
  tone = 'default',
  onCancel,
  onConfirm,
}: ConfirmDialogProps) {
  return (
    <div className="modal-backdrop fixed inset-0 z-[75] flex items-center justify-center p-4">
      <div
        className="modal-panel w-full max-w-md overflow-hidden"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirmation-title"
        aria-describedby="confirmation-description"
      >
        <div className="flex items-start gap-3 border-b border-[var(--line)] p-5">
          <div className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg ${tone === 'danger' ? 'bg-rose-500/10 text-[var(--danger)]' : 'bg-blue-500/10 text-[var(--primary)]'}`}>
            <AlertTriangle className="h-4 w-4" />
          </div>
          <div>
            <h2 id="confirmation-title" className="text-sm font-semibold text-[var(--foreground)]">{title}</h2>
            <p id="confirmation-description" className="mt-1.5 text-xs leading-relaxed text-[var(--muted)]">{description}</p>
          </div>
        </div>
        <div className="flex justify-end gap-2 bg-[var(--surface-muted)] p-4">
          <button type="button" onClick={onCancel} className="secondary-button" autoFocus>Cancel</button>
          <button
            type="button"
            onClick={onConfirm}
            className={tone === 'danger' ? 'toolbar-button !border-rose-500 !bg-rose-600 !text-white hover:!bg-rose-700' : 'primary-button'}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
