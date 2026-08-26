'use client';

import { Award, BookOpen, Bot, History, Moon, Plus, Settings, Sun, Swords, Wand2 } from 'lucide-react';
import { DebateSession } from '@/types/debate';

type WorkspaceTab = 'arena' | 'research' | 'critiques' | 'verdict' | 'config';

interface WorkspaceHeaderProps {
  activeTab: WorkspaceTab;
  onTabChange: (tab: WorkspaceTab) => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  session: DebateSession | null;
  modelCount: number;
  activeModelCount: number;
  savedWorkspaceCount: number;
  researchSourceCount?: number;
  onOpenHistory: () => void;
  onOpenSetup: () => void;
  onNewSession: () => void;
}

export function WorkspaceHeader({
  activeTab,
  onTabChange,
  theme,
  onToggleTheme,
  session,
  modelCount,
  activeModelCount,
  savedWorkspaceCount,
  researchSourceCount,
  onOpenHistory,
  onOpenSetup,
  onNewSession,
}: WorkspaceHeaderProps) {
  const tabs: Array<{ id: WorkspaceTab; label: string; icon: typeof Bot; count?: number }> = [
    { id: 'arena', label: 'Arena', icon: Bot },
    { id: 'research', label: 'Research', icon: BookOpen, count: researchSourceCount },
    { id: 'critiques', label: 'Critique matrix', icon: Swords },
    { id: 'verdict', label: 'Verdict', icon: Award },
    { id: 'config', label: 'Fleet & keys', icon: Settings, count: modelCount },
  ];

  return (
    <header className="app-header">
      <div className="app-header-inner">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex min-w-0 items-center justify-between gap-4">
            <div className="brand-lockup">
              <div className="brand-mark" aria-hidden="true"><Bot className="h-5 w-5" /></div>
              <div className="min-w-0">
                <span className="brand-kicker">SIH deliberation workspace</span>
                <h1 className="brand-title">AI Consensus Arena</h1>
                <p className="brand-subtitle">Structured multi-model review for high-stakes engineering decisions</p>
              </div>
            </div>
            <button type="button" onClick={onToggleTheme} className="toolbar-button shrink-0" title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`} aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}>
              {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
              <span className="hidden sm:inline">{theme === 'light' ? 'Dark' : 'Light'}</span>
            </button>
          </div>

          <div className="header-actions">
            <button type="button" onClick={onOpenHistory} className="toolbar-button" title="Browse saved debate workspaces"><History className="h-3.5 w-3.5" /><span>History</span>{savedWorkspaceCount > 0 && <span className="count-badge">{savedWorkspaceCount}</span>}</button>
            <button type="button" onClick={onOpenSetup} className="toolbar-button toolbar-button-warning"><Wand2 className="h-3.5 w-3.5" /><span>Setup</span></button>
            <button type="button" onClick={onNewSession} className="toolbar-button toolbar-button-primary" title="Start a new deliberation"><Plus className="h-4 w-4" /><span>New session</span></button>
          </div>
        </div>

        <nav className="nav-strip" aria-label="Workspace sections">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button key={tab.id} type="button" onClick={() => onTabChange(tab.id)} className={`nav-item ${activeTab === tab.id ? 'nav-item-active' : ''}`} aria-current={activeTab === tab.id ? 'page' : undefined}>
                <Icon className="h-3.5 w-3.5" /><span>{tab.label}</span>{tab.count ? <span className="count-badge">{tab.count}</span> : null}
              </button>
            );
          })}
          {session && <div className="session-meta"><span>{session.ps_code || 'Custom brief'}</span><span><strong>{activeModelCount}</strong> models</span><span><strong>{session.rounds.length}</strong> passes</span></div>}
        </nav>
      </div>
    </header>
  );
}
