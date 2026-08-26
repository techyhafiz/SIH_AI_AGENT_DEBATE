import type { LucideIcon } from 'lucide-react';
import { Plus, Wand2 } from 'lucide-react';

interface WorkspaceEmptyStateProps {
  icon: LucideIcon;
  eyebrow: string;
  title: string;
  description: string;
  onNewSession: () => void;
  onSetup: () => void;
}

export function WorkspaceEmptyState({
  icon: Icon,
  eyebrow,
  title,
  description,
  onNewSession,
  onSetup,
}: WorkspaceEmptyStateProps) {
  return (
    <section className="empty-workspace">
      <div className="empty-workspace-content">
        <div className="empty-workspace-icon" aria-hidden="true"><Icon className="h-6 w-6" /></div>
        <span className="eyebrow">{eyebrow}</span>
        <h2 className="mt-2">{title}</h2>
        <p>{description}</p>
        <div className="empty-workspace-actions">
          <button type="button" onClick={onNewSession} className="primary-button"><Plus className="h-4 w-4" /> Start a deliberation</button>
          <button type="button" onClick={onSetup} className="secondary-button"><Wand2 className="h-4 w-4" /> Configure model fleet</button>
        </div>
      </div>
    </section>
  );
}
