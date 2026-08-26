'use client';

import React, { useState, useEffect, useMemo, useRef } from 'react';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  ModelConfig,
  DebateSession,
  RoundData,
  DebaterResponse,
} from '@/types/debate';
import { useDebateStream } from '@/hooks/useDebateStream';
import DEFAULT_PS_DATA from '@/data/extracted_problem_statements.json';
import { DebaterCard } from '@/components/DebaterCard';
import { WorkspaceHeader } from '@/components/WorkspaceHeader';
import { SessionStatusBar } from '@/components/SessionStatusBar';
import { TimeoutAlertModal } from '@/components/TimeoutAlertModal';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { WorkspaceEmptyState } from '@/components/WorkspaceEmptyState';
import {
  Bot,
  Layers,
  Sparkles,
  Play,
  Pause,
  Award,
  BookOpen,
  Swords,
  Settings,
  Flame,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Download,
  Copy,
  Search,
  ExternalLink,
  FileText,
  Shield,
  Cpu,
  MessageSquarePlus,
  RefreshCw,
  Zap,
  Check,
  X,
  Plus,
  Trash2,
  ChevronRight,
  ChevronDown,
  Wand2,
  KeyRound,
  Activity,
  Globe,
  Database,
  ArrowRight,
  ArrowLeft,
  History,
  FolderOpen,
  Star,
  CheckCircle
} from 'lucide-react';


const PIPELINE_STEPS = [
  { id: '1.1', phase: 1, title: 'Pass 1.1: 🏛️ Architect Genesis', short: '1.1 Arch' },
  { id: '1.2', phase: 1, title: "Pass 1.2: 😈 Murphy's Critic", short: '1.2 Critic' },
  { id: '1.3', phase: 1, title: 'Pass 1.3: ⚙️ BOM Reality', short: '1.3 BOM' },
  { id: '1.4', phase: 1, title: 'Pass 1.4: 🛡️ Security & Compliance', short: '1.4 Sec' },
  { id: 'R1', phase: 1, title: '🔬 Research Block 1: Fact-Check & arXiv', short: 'R1 Research' },
  { id: '2.1', phase: 2, title: 'Round 2.1: 🥊 Cross-Examination', short: '2.1 Cross' },
  { id: '2.2', phase: 2, title: 'Round 2.2: 🛡️ Rebuttal & Defense', short: '2.2 Defend' },
  { id: '2.3', phase: 2, title: 'Round 2.3: ⚖️ Flaw Locking', short: '2.3 Lock' },
  { id: 'R2', phase: 2, title: '🔬 Research Block 2: IC & Algorithm Scan', short: 'R2 Research' },
  { id: '3.1', phase: 3, title: 'Round 3.1: 🚀 10x Quantum Leap', short: '3.1 10x' },
  { id: '3.2', phase: 3, title: 'Round 3.2: 🔬 Micro-Optimization', short: '3.2 Opt' },
  { id: 'R3', phase: 3, title: '🔬 Research Block 3: Standards & Citations', short: 'R3 Research' },
  { id: '4.1', phase: 4, title: 'Round 4.1: 🤝 Concession & Sovereign Verdict', short: '4.1 Verdict' },
];

const DEFAULT_FLEET: ModelConfig[] = [
  { id: 'm1', name: 'Claude Opus 4.8', base_url: 'https://agentrouter.org/v1', api_key: '', backup_api_keys: [], model_id: 'claude-opus-4-8', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm2', name: 'Claude Opus 5.0', base_url: 'https://agentrouter.org/v1', api_key: '', backup_api_keys: [], model_id: 'claude-opus-5', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.6 },
  { id: 'm3', name: 'GPT 5.6 Sol', base_url: 'https://agentrouter.org/v1', api_key: '', backup_api_keys: [], model_id: 'gpt-5.6-sol', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: true, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm4', name: 'Gemini 3.5 Flash Lite', base_url: 'https://generativelanguage.googleapis.com/v1beta/openai', api_key: '', backup_api_keys: [], model_id: 'gemini-3.5-flash-lite', fallback_model_ids: ['gemini-flash-lite-latest'], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: true, enabled: true, temperature: 0.7 },
  { id: 'm5', name: 'Gemini Flash Quota Pool (3.7 / 3.6 / 3.5)', base_url: 'https://generativelanguage.googleapis.com/v1beta/openai', api_key: '', backup_api_keys: [], model_id: 'gemini-3.7-flash', fallback_model_ids: ['gemini-3.6-flash', 'gemini-3.5-flash'], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: true, enabled: true, temperature: 0.7 },
  ...[
    ['m6', 'GLM 5.2 (Free)', 'https://openrouter.ai/api/v1', 'z-ai/glm-5.2:free'],
    ['m7', 'NVIDIA Nemotron 3 Super 120B (Free)', 'https://openrouter.ai/api/v1', 'nvidia/nemotron-3-super-120b-a12b:free'],
    ['m8', 'Stealth Ox-Alpha', 'https://openrouter.ai/api/v1', 'stealth/ox-alpha'],
    ['m9', 'NVIDIA Nemotron 3.5 Lightning (Free)', 'https://openrouter.ai/api/v1', 'nvidia/nemotron-3.5-lightning:free'],
    ['m10', 'Qwen 3.8 Max (Free)', 'https://api.tokenrouter.com/v1', 'qwen/qwen3.8-max-free'],
    ['m11', 'Claude Sonnet 5 (BluesMinds)', 'https://api.bluesminds.com/v1', 'unlimited/claude-sonnet-5'],
    ['m12', 'Mimo v2.5 (TokenFaucet)', 'https://freetokenfaucet.com/v1', 'mimo-v2.5'],
    ['m13', 'GPT 5.6 Terra (TokenFaucet)', 'https://freetokenfaucet.com/v1', 'gpt-5.6-terra'],
    ['m14', 'GPT 5.6 Luna (TokenFaucet)', 'https://freetokenfaucet.com/v1', 'gpt-5.6-luna'],
    ['m15', 'DeepSeek V4 Pro (XKiro)', 'https://api.xkiro.com/v1', 'deepseek/deepseek-v4-pro'],
    ['m16', 'Qwen 3.8 Max (XKiro)', 'https://api.xkiro.com/v1', 'qwen/qwen3.8-max'],
    ['m17', 'Mistral Large 2512 (XKiro)', 'https://api.xkiro.com/v1', 'mistralai/mistral-large-2512'],
    ['m18', 'Qwen 3.7 Max (XKiro)', 'https://api.xkiro.com/v1', 'qwen/qwen3.7-max'],
    ['m19', 'MiniMax M2.7 (XKiro)', 'https://api.xkiro.com/v1', 'minimax/minimax-m2.7'],
    ['m20', 'Gemini 3.5 Flash Free (TokenIn)', 'https://tokenin.my.id/v1', 'myt/gemini-3.5-flash-free'],
    ['m21', 'Claude Opus 4.8 Free (TokenIn)', 'https://tokenin.my.id/v1', 'myt/claude-opus-4-8-free'],
  ].map(([id, name, base_url, model_id]) => ({ id, name, base_url, model_id, api_key: '', backup_api_keys: [], fallback_model_ids: [], provider_type: 'openai_compatible' as const, timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: id !== 'm21', temperature: 0.7 }))
];

const WIZARD_PROVIDERS = [
  {
    id: 'google_gemini',
    name: 'Google AI Studio (Gemini)',
    tier: 'Free Tier Available · High Speed',
    icon: '🌟',
    direct_link: 'https://aistudio.google.com/app/apikey',
    desc: 'Official Google AI Studio API for Gemini 3.5 Flash Lite (Primary Arbiter) and Gemini 3.7 Flash Pool.',
    placeholder: 'Paste Google AI Studio key'
  },
  {
    id: 'openrouter',
    name: 'OpenRouter (Free & Paid Fleet)',
    tier: 'Free GLM, Nemotron & Llama Models',
    icon: '🌐',
    direct_link: 'https://openrouter.ai/keys',
    desc: 'Provides GLM 5.2 Free, NVIDIA Nemotron 3 Super 120B Free, and Stealth Ox-Alpha models.',
    placeholder: 'Paste OpenRouter key'
  },
  {
    id: 'agentrouter',
    name: 'AgentRouter (Flagship Reasoning)',
    tier: 'Claude Opus 4.8/5.0 & GPT 5.6 Sol',
    icon: '⚡',
    direct_link: 'https://agentrouter.org',
    desc: 'High-reasoning frontier models for deep architectural critique and math synthesis.',
    placeholder: 'Paste AgentRouter key'
  },
  {
    id: 'xkiro',
    name: 'XKiro Router (DeepSeek & Qwen)',
    tier: 'DeepSeek V4 Pro, Qwen 3.8 Max, Mistral',
    icon: '🚀',
    direct_link: 'https://api.xkiro.com',
    desc: 'High-speed cluster for DeepSeek V4 Pro, Qwen 3.8/3.7 Max, and Mistral Large 2512.',
    placeholder: 'Paste XKiro key'
  },
  {
    id: 'tokenin',
    name: 'TokenIn Free Hub',
    tier: 'Free Community Pool',
    icon: '🎁',
    direct_link: 'https://tokenin.my.id',
    desc: 'Free endpoints for Gemini 3.5 Flash and Claude Opus 4.8 backups.',
    placeholder: 'Paste TokenIn key'
  },
  {
    id: 'tokenfaucet',
    name: 'FreeTokenFaucet Hub',
    tier: 'Mimo v2.5, GPT Terra & Luna',
    icon: '💧',
    direct_link: 'https://freetokenfaucet.com',
    desc: 'Fast pooled models for high-throughput multi-perspective cross-examination.',
    placeholder: 'Paste TokenFaucet key'
  },
  {
    id: 'bluesminds',
    name: 'BluesMinds AI',
    tier: 'Claude Sonnet 5',
    icon: '💎',
    direct_link: 'https://api.bluesminds.com',
    desc: 'Direct routing for Claude Sonnet 5 reasoning and synthesis.',
    placeholder: 'Paste BluesMinds key'
  },
  {
    id: 'tokenrouter',
    name: 'TokenRouter Free',
    tier: 'Qwen 3.8 Max Free',
    icon: '🛡️',
    direct_link: 'https://api.tokenrouter.com',
    desc: 'Dedicated free Qwen 3.8 Max router for security and compliance analysis.',
    placeholder: 'Paste TokenRouter key'
  },
  {
    id: 'research',
    name: 'Autonomous Research Engine',
    tier: 'Tavily Search & OpenAlex (250M Papers)',
    icon: '🔬',
    direct_link: 'https://tavily.com',
    desc: 'Enables live factual verification, Indian BOM norms lookup, and arXiv paper extraction.',
    placeholder: 'tvly-...'
  }
];

// Free-text + provider + free-tier + tier filter over a discovery sweep. A full sweep can return
// several hundred models, so the wizard list is searchable rather than a flat scroll.
function matchesDiscoveryQuery(item: any, query: string, providerId: string, freeOnly: boolean, tier: string) {
  if (providerId !== 'all' && item?.provider_id !== providerId) return false;
  if (freeOnly && !item?.is_free) return false;
  if (tier !== 'all' && (item?.tier || 'mid') !== tier) return false;
  if (!query) return true;
  const haystack = `${item?.model?.name || ''} ${item?.model?.model_id || ''} ${item?.provider_name || ''}`.toLowerCase();
  return query.split(/\s+/).filter(Boolean).every((token) => haystack.includes(token));
}

// The backend pre-classifies every probed model by family (see classify_model_tier), because a
// verified list of ~90 names is unusable if picking from it means recognising all 90. Tier and
// latency are deliberately separate axes: a 4b content-safety classifier answers in 700ms and
// would top any speed ranking while being useless in a debate.
const DISCOVERY_TIER_META: Record<string, { label: string; blurb: string; rank: number; chip: string; badge: string }> = {
  top: {
    label: 'Top tier',
    blurb: 'Frontier models - pick your main debate fleet from here',
    rank: 0,
    chip: 'bg-amber-500 border-amber-500 text-white',
    badge: 'bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800'
  },
  mid: {
    label: 'Mid tier',
    blurb: 'Capable general models - good for extra perspectives',
    rank: 1,
    chip: 'bg-sky-600 border-sky-600 text-white',
    badge: 'bg-sky-100 dark:bg-sky-950 text-sky-800 dark:text-sky-300 border-sky-200 dark:border-sky-800'
  },
  low: {
    label: 'Light / special-purpose',
    blurb: 'Small variants and safety, translation or media endpoints - weak debaters',
    rank: 2,
    chip: 'bg-slate-600 border-slate-600 text-white',
    badge: 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'
  }
};
// Anything the backend could not tier is treated as mid, matching its own conservative default.
const discoveryTierOf = (item: any): string => (DISCOVERY_TIER_META[item?.tier] ? item.tier : 'mid');
const discoveryTierRank = (item: any): number => DISCOVERY_TIER_META[discoveryTierOf(item)].rank;


// Human-readable label for the backend's probe failure reason codes.
const DISCOVERY_REASON_LABELS: Record<string, string> = {
  auth: 'Key rejected',
  billing: 'Out of credits',
  plan: 'Needs paid plan',
  quota: 'Daily cap reached',
  policy: 'Blocked by data policy',
  rate_limited: 'Rate limited',
  missing: 'Not on this endpoint',
  unsupported: 'Not a chat model',
  timeout: 'Timed out',
  server: 'Provider error',
  empty: 'Empty reply',
  budget: 'Not verified',
  cancelled: 'Not probed',
  other: 'Failed'
};

export default function HomePage() {
  // Theme State: 'light' | 'dark'
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  
  // Fleet & Session State
  const [models, setModels] = useState<ModelConfig[]>(DEFAULT_FLEET);
  const [sessionSelectedModels, setSessionSelectedModels] = useState<Record<string, boolean>>({});
  const [arbiterModelId, setArbiterModelId] = useState<string>('m3');
  const [backupArbiterModelId, setBackupArbiterModelId] = useState<string>('m4');
  const [activeTab, setActiveTab] = useState<'arena' | 'research' | 'critiques' | 'verdict' | 'config'>('arena');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedRoundIndex, setSelectedRoundIndex] = useState<number>(0);
  
  // Modals & Drawers
  const [isStartModalOpen, setIsStartModalOpen] = useState(false);
  const [isInjectModalOpen, setIsInjectModalOpen] = useState(false);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [isArbiterCommandOpen, setIsArbiterCommandOpen] = useState(false);
  const [arbiterCommandText, setArbiterCommandText] = useState('');
  const [isSendingArbiterCmd, setIsSendingArbiterCmd] = useState(false);
  const [arbiterActionLogs, setArbiterActionLogs] = useState<Array<{ sender: string; text: string; time: string }>>([
    {
      sender: 'GPT 5.6 Sol (Master Arbiter)',
      text: '👑 Supreme Master Arbiter online. I am supervising all 21 AI models across 4 deliberation phases. You can command me to abort lagging models, rotate keys, heal unformatted outputs, or force consensus synthesis.',
      time: 'Ready'
    }
  ]);
  const [savedWorkspaces, setSavedWorkspaces] = useState<any[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [disabledSessionModels, setDisabledSessionModels] = useState<Record<string, boolean>>({});
  const [selectedScratchpadModel, setSelectedScratchpadModel] = useState<DebaterResponse | null>(null);
  const [injectionText, setInjectionText] = useState('');
  
  // Start Debate Form State
  const [problemStatement, setProblemStatement] = useState('');
  const [psCode, setPsCode] = useState('');
  const [ministryDomain, setMinistryDomain] = useState('Smart India Hackathon (General)');
  const [additionalPrompt, setAdditionalPrompt] = useState('');
  const [autoAdvance, setAutoAdvance] = useState(true);
  const [psList, setPsList] = useState<any[]>(Array.isArray(DEFAULT_PS_DATA) ? DEFAULT_PS_DATA : []);
  const [psFilter, setPsFilter] = useState('');
  const [selectedPsObj, setSelectedPsObj] = useState<any | null>(null);
  const [psCategoryFilter, setPsCategoryFilter] = useState<'All' | 'Software' | 'Hardware'>('All');
  const [isLaunching, setIsLaunching] = useState(false);
  const [copiedVerdict, setCopiedVerdict] = useState(false);
  const [notice, setNotice] = useState<{ message: string; tone: 'info' | 'success' | 'error' } | null>(null);
  const [confirmation, setConfirmation] = useState<{
    title: string;
    description: string;
    confirmLabel: string;
    tone?: 'default' | 'danger';
    onConfirm: () => void;
  } | null>(null);

  // Research Config State (Preloaded with Recovered Master Keys)
  const [researchConfig, setResearchConfig] = useState({
    enabled: true,
    tavily_api_key: '',
    openalex_email: 'campusprintexpress@gmail.com',
    download_pdfs: true
  });

  // STEP-BY-STEP CARD-BASED WIZARD STATE (Preloaded with Recovered Master Keys)
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [wizardFlowState, setWizardFlowState] = useState<'initial_choice' | 'cards' | 'results' | 'custom'>('initial_choice');
  const [cardIndex, setCardIndex] = useState(0);
  const [wizardKeys, setWizardKeys] = useState<Record<string, string>>({
    google_gemini: '',
    openrouter: '',
    agentrouter: '',
    xkiro: '',
    tokenin: '',
    tokenfaucet: '',
    bluesminds: '',
    tokenrouter: ''
  });
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [availableDiscovered, setAvailableDiscovered] = useState<any[]>([]);
  const [unavailableDiscovered, setUnavailableDiscovered] = useState<any[]>([]);
  const [selectedDiscovered, setSelectedDiscovered] = useState<Record<string, boolean>>({});
  const [showUnavailableAccordion, setShowUnavailableAccordion] = useState(false);
  // Discovery now sweeps every model each provider advertises, so it streams progress
  // instead of blocking on one long request.
  const [discoveryProgress, setDiscoveryProgress] = useState<{
    jobId: string;
    status: string;
    total: number;
    done: number;
    online: number;
    failed: number;
    elapsed: number;
    finished: boolean;
    scope: string;
    skippedByScope: number;
  } | null>(null);
  const [discoveryCatalogue, setDiscoveryCatalogue] = useState<any[]>([]);
  const [discoverySearch, setDiscoverySearch] = useState('');
  const [discoveryProvider, setDiscoveryProvider] = useState('all');
  const [discoveryFreeOnly, setDiscoveryFreeOnly] = useState(false);
  const [discoveryTier, setDiscoveryTier] = useState('all');
  const discoveryAbortRef = useRef(false);
  const discoveryTouchedRef = useRef(false);
  const discoveryJobIdRef = useRef<string | null>(null);

  // Abandon an in-flight sweep if the wizard is dismissed, so polling never outlives the UI.
  useEffect(() => {
    if (isWizardOpen) return;
    discoveryAbortRef.current = true;
    const jobId = discoveryJobIdRef.current;
    discoveryJobIdRef.current = null;
    if (jobId) {
      fetch(`/api/providers/auto-discover/cancel/${encodeURIComponent(jobId)}`, { method: 'POST' }).catch(() => {});
    }
  }, [isWizardOpen]);

  const discoveryProviderOptions = useMemo(() => {
    const names = new Map<string, string>();
    [...availableDiscovered, ...unavailableDiscovered].forEach((item) => {
      if (item?.provider_id) names.set(item.provider_id, item.provider_name || item.provider_id);
    });
    return Array.from(names, ([id, name]) => ({ id, name })).sort((a, b) => a.name.localeCompare(b.name));
  }, [availableDiscovered, unavailableDiscovered]);

  const discoveryQuery = discoverySearch.trim().toLowerCase();

  const filteredAvailable = useMemo(
    () => availableDiscovered.filter((item) => matchesDiscoveryQuery(item, discoveryQuery, discoveryProvider, discoveryFreeOnly, discoveryTier)),
    [availableDiscovered, discoveryQuery, discoveryProvider, discoveryFreeOnly, discoveryTier]
  );
  const filteredUnavailable = useMemo(
    () => unavailableDiscovered.filter((item) => matchesDiscoveryQuery(item, discoveryQuery, discoveryProvider, discoveryFreeOnly, discoveryTier)),
    [unavailableDiscovered, discoveryQuery, discoveryProvider, discoveryFreeOnly, discoveryTier]
  );
  // Counts come from the unfiltered online list so the tier chips keep showing the real totals
  // while a chip is active - otherwise selecting "Top tier" would zero out the other two labels.
  const discoveryTierCounts = useMemo(() => {
    const counts: Record<string, number> = { top: 0, mid: 0, low: 0 };
    availableDiscovered.forEach((item) => { counts[discoveryTierOf(item)] += 1; });
    return counts;
  }, [availableDiscovered]);
  const discoveryCatalogueErrors = useMemo(
    () => discoveryCatalogue.filter((entry) => entry?.error),
    [discoveryCatalogue]
  );

  // Custom Endpoint Form State
  const [customForm, setCustomForm] = useState({
    name: 'Custom LLM Server',
    base_url: 'http://localhost:11434/v1',
    model_id: 'llama3:latest',
    api_key: ''
  });

  // Fleet Manager Latency Testing
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string; latency_ms: number }>>({});
  const [isTestingAll, setIsTestingAll] = useState(false);
  const [testingModelId, setTestingModelId] = useState<string | null>(null);
  const [fleetFilter, setFleetFilter] = useState<'all' | 'enabled' | 'online'>('all');

  // SSE streaming hook with auto-reconnect and connectionStatus
  const {
    session,
    currentStatus,
    activeTokens,
    streamingModels,
    timeoutAlert,
    setTimeoutAlert,
    isArbiterThinking,
    connectionStatus,
    sendModeratorAction,
    refreshSession,
    activity
  } = useDebateStream(sessionId);

  // Initialize theme & active session from localStorage
  useEffect(() => {
    const savedTheme = (localStorage.getItem('arena-theme') as 'light' | 'dark') || 'light';
    setTheme(savedTheme);
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }

    // Auto-restore active session if reloaded
    const savedSessionId = localStorage.getItem('active_debate_session_id');
    if (savedSessionId && !sessionId) {
      setSessionId(savedSessionId);
    }
  }, []);

  const hasOpenOverlay = isStartModalOpen
    || isInjectModalOpen
    || isHistoryModalOpen
    || isArbiterCommandOpen
    || isWizardOpen
    || Boolean(timeoutAlert)
    || Boolean(confirmation)
    || Boolean(selectedScratchpadModel);

  useEffect(() => {
    if (!hasOpenOverlay) return;
    const previousOverflow = document.body.style.overflow;
    const previouslyFocused = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    document.body.style.overflow = 'hidden';

    const getActiveDialog = () => {
      const dialogs = Array.from(document.querySelectorAll<HTMLElement>('[role="dialog"], [role="alertdialog"]'));
      return dialogs
        .filter((dialog) => dialog.getClientRects().length > 0)
        .sort((first, second) => {
          const firstLayer = Number.parseInt(window.getComputedStyle(first.parentElement || first).zIndex, 10) || 0;
          const secondLayer = Number.parseInt(window.getComputedStyle(second.parentElement || second).zIndex, 10) || 0;
          return firstLayer - secondLayer;
        })
        .at(-1) || null;
    };

    const focusDialog = window.requestAnimationFrame(() => {
      const dialog = getActiveDialog();
      const preferredTarget = dialog?.querySelector<HTMLElement>('[autofocus], input:not([type="hidden"]), textarea, button, [href], [tabindex]:not([tabindex="-1"])');
      (preferredTarget || dialog)?.focus();
    });

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (confirmation) setConfirmation(null);
        else if (timeoutAlert) setTimeoutAlert(null);
        else if (selectedScratchpadModel) setSelectedScratchpadModel(null);
        else if (isArbiterCommandOpen) setIsArbiterCommandOpen(false);
        else if (isHistoryModalOpen) setIsHistoryModalOpen(false);
        else if (isInjectModalOpen) setIsInjectModalOpen(false);
        else if (isStartModalOpen) setIsStartModalOpen(false);
        else if (isWizardOpen) setIsWizardOpen(false);
        return;
      }

      if (event.key !== 'Tab') return;
      const dialog = getActiveDialog();
      if (!dialog) return;
      const focusable = Array.from(dialog.querySelectorAll<HTMLElement>('button:not([disabled]), [href], input:not([disabled]):not([type="hidden"]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'));
      if (focusable.length === 0) {
        event.preventDefault();
        dialog.focus();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.cancelAnimationFrame(focusDialog);
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyDown);
      previouslyFocused?.focus();
    };
  }, [confirmation, hasOpenOverlay, isArbiterCommandOpen, isHistoryModalOpen, isInjectModalOpen, isStartModalOpen, isWizardOpen, selectedScratchpadModel, setTimeoutAlert, timeoutAlert]);

  // Update localStorage when sessionId changes
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('active_debate_session_id', sessionId);
    }
  }, [sessionId]);

  const toggleTheme = () => {
    const nextTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    localStorage.setItem('arena-theme', nextTheme);
    if (nextTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  // Load user config and research config on mount
  useEffect(() => {
    fetch('/api/user/config')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setModels(data);
          const initialSel: Record<string, boolean> = {};
          data.forEach((m: ModelConfig) => {
            initialSel[m.id] = m.enabled !== false;
          });
          setSessionSelectedModels(initialSel);

          const arb = data.find((m: any) => m.is_arbiter);
          if (arb) setArbiterModelId(arb.id);
          const bk = data.find((m: any) => m.is_backup_arbiter);
          if (bk) setBackupArbiterModelId(bk.id);

          // Preload wizard keys from loaded backend configuration
          setWizardKeys((prev) => {
            const updated = { ...prev };
            data.forEach((m: ModelConfig) => {
              if (!m.api_key) return;
              const url = (m.base_url || '').toLowerCase();
              if (url.includes('generativelanguage.googleapis.com')) updated.google_gemini = m.api_key;
              else if (url.includes('openrouter.ai')) updated.openrouter = m.api_key;
              else if (url.includes('agentrouter.org')) updated.agentrouter = m.api_key;
              else if (url.includes('xkiro.com')) updated.xkiro = m.api_key;
              else if (url.includes('tokenin.my.id')) updated.tokenin = m.api_key;
              else if (url.includes('freetokenfaucet.com')) updated.tokenfaucet = m.api_key;
              else if (url.includes('bluesminds.com')) updated.bluesminds = m.api_key;
              else if (url.includes('tokenrouter.com')) updated.tokenrouter = m.api_key;
            });
            return updated;
          });
        }
      })
      .catch(() => {});

    fetch('/api/research/config')
      .then((res) => res.json())
      .then((data) => setResearchConfig(data))
      .catch(() => {});

    fetch('/api/problem-statements')
      .then((res) => res.json())
      .then((data) => setPsList(Array.isArray(data) ? data : []))
      .catch(() => {});

    // Eagerly fetch saved workspaces for live count badge & instant history opening
    fetch('/api/workspaces')
      .then((res) => res.json())
      .then((data) => setSavedWorkspaces(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, []);

  const userManuallySelectedRoundRef = useRef(false);

  useEffect(() => {
    setDisabledSessionModels({});
    setSelectedRoundIndex(0);
    userManuallySelectedRoundRef.current = false;
  }, [sessionId]);

  // Auto-track latest round index unless user explicitly navigated to a previous round
  useEffect(() => {
    if (session && session.rounds && session.rounds.length > 0) {
      if (!userManuallySelectedRoundRef.current || selectedRoundIndex >= session.rounds.length - 2) {
        setSelectedRoundIndex(session.rounds.length - 1);
      }
    }
  }, [session?.rounds?.length]);


  const currentRound: RoundData | undefined = session?.rounds?.[selectedRoundIndex];

  // Dynamic Live Status details
  const liveStatusText = useMemo(() => {
    if (!sessionId) return 'Ready to launch a new deliberation session.';
    if (!session) return 'Restoring the saved workspace and live event stream.';
    if (currentStatus === 'paused') return `Paused at ${currentRound?.pass_or_round_title || 'the current pass'}. Resume when you are ready.`;
    if (currentStatus === 'completed') return 'Deliberation complete. The master consensus verdict is ready.';
    if (isArbiterThinking) return 'The master arbiter is evaluating alignment and unresolved friction.';
    
    if (currentRound) {
      const total = session.models.filter((model) => model.enabled && !disabledSessionModels[model.id]).length;
      const completed = Object.values(currentRound.responses || {}).filter((r) => r.status === 'completed').length;
      const streaming = Object.keys(activeTokens).length;
      const timeouts = Object.values(currentRound.responses || {}).filter((r) => r.status === 'timeout').length;
      
      const pTitle = currentRound.pass_or_round_title || `Round ${currentRound.round_number}`;
      return `${pTitle}: ${completed} of ${total} complete${streaming > 0 ? ` · ${streaming} generating` : ''}${timeouts > 0 ? ` · ${timeouts} timed out` : ''}.`;
    }
    return `Deliberation in progress (${currentStatus})...`;
  }, [sessionId, session, currentStatus, isArbiterThinking, currentRound, activeTokens, disabledSessionModels]);

  const handleStartDebate = async () => {
    if (!problemStatement.trim()) {
      notify('Select an SIH problem statement or enter a custom brief before launching.', 'error');
      return;
    }
    const selectedCount = models.filter((model) => sessionSelectedModels[model.id] ?? model.enabled).length;
    if (selectedCount < 2) {
      notify('Select at least two participating models before launching.', 'error');
      return;
    }
    setIsLaunching(true);
    try {
      const activeFleet = models.map((m) => ({
        ...m,
        enabled: sessionSelectedModels[m.id] !== false,
        is_arbiter: m.id === arbiterModelId,
        is_backup_arbiter: m.id === backupArbiterModelId
      }));

      const res = await fetch('/api/debate/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_statement: problemStatement,
          ps_code: psCode,
          ministry_domain: ministryDomain,
          additional_prompt: additionalPrompt,
          models: activeFleet,
          arbiter_model_id: arbiterModelId,
          backup_arbiter_model_id: backupArbiterModelId,
          auto_advance: autoAdvance
        })
      });

      if (res.ok) {
        const data = await res.json();
        setSessionId(data.session_id);
        setIsStartModalOpen(false);
        setActiveTab('arena');
      } else {
        const err = await res.json();
        notify(`Could not start the deliberation: ${err.detail || 'Server error'}`, 'error');
      }
    } catch (e: any) {
      notify(`Could not reach the debate service: ${e.message}`, 'error');
    } finally {
      setIsLaunching(false);
    }
  };

  const handleSaveMasterConfig = async () => {
    try {
      await fetch('/api/user/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(models)
      });
      await fetch('/api/research/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(researchConfig)
      });
      notify('Default model and research configuration saved.', 'success');
    } catch (e: any) {
      notify(`Could not save the configuration: ${e.message}`, 'error');
    }
  };

  const handleTestAllModels = async () => {
    setIsTestingAll(true);
    try {
      const res = await fetch('/api/models/test-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(models)
      });
      const data = await res.json();
      setTestResults(data);
    } catch (e: any) {
      notify(`Fleet test failed: ${e.message}`, 'error');
    } finally {
      setIsTestingAll(false);
    }
  };

  // Run dynamic discovery across all provider keys entered.
  // Two phases: the backend first lists every model each provider advertises on /models
  // (fast), then live-probes all of them for latency in the background. We poll with a
  // cursor so results stream into the list instead of the wizard freezing for minutes.
  //
  // `scope` is what the two buttons choose between. "quick" probes the curated fleet plus every
  // model a provider flags free - measured live, that is ~80 probes in ~3 minutes. "all" probes
  // the entire advertised catalogue: ~820 probes in ~7.5 minutes, and on free-plan keys most of
  // the extra 740 answer with the same "no credits" error. The full sweep is therefore confirmed
  // first rather than being the default.
  const handleExecuteDiscovery = async (scope: 'quick' | 'all' = 'quick') => {
    setIsDiscovering(true);
    setAvailableDiscovered([]);
    setUnavailableDiscovered([]);
    setSelectedDiscovered({});
    setDiscoveryCatalogue([]);
    setDiscoveryProgress(null);
    setDiscoverySearch('');
    setDiscoveryProvider('all');
    setDiscoveryFreeOnly(false);
    setDiscoveryTier('all');
    discoveryAbortRef.current = false;
    discoveryTouchedRef.current = false;

    const readError = async (res: Response) => {
      const errText = (await res.text()).trim();
      if (res.status === 500 && /^internal server error$/i.test(errText)) {
        return 'The backend did not respond in time. Confirm the API is running on http://127.0.0.1:8000 (open /health), then retry.';
      }
      return errText || `HTTP ${res.status}`;
    };

    try {
      const startRes = await fetch('/api/providers/auto-discover/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider_keys: wizardKeys, scope })
      });
      if (!startRes.ok) throw new Error(await readError(startRes));
      const start = await startRes.json();

      discoveryJobIdRef.current = start.job_id;
      setDiscoveryCatalogue(start.catalogue || []);
      setDiscoveryProgress({
        jobId: start.job_id,
        status: start.status,
        total: start.total || 0,
        done: 0,
        online: 0,
        failed: 0,
        elapsed: 0,
        finished: !!start.finished,
        scope: start.scope || scope,
        skippedByScope: start.skipped_by_scope || 0
      });
      // Show the results stage right away so the sweep is visible as it runs.
      setWizardFlowState('results');

      if (!start.total) {
        notify('No models to test. Add at least one provider key first.', 'error');
        return;
      }

      let cursor = 0;
      let sawFavorite = false;
      let onlineCount = 0;
      let snapshot = start;
      let consecutivePollErrors = 0;

      while (!discoveryAbortRef.current) {
        await new Promise((resolve) => setTimeout(resolve, 900));

        // A sweep can run for minutes, so a single dropped poll must not throw away the run.
        let pollRes: Response;
        try {
          pollRes = await fetch(
            `/api/providers/auto-discover/status/${encodeURIComponent(start.job_id)}?cursor=${cursor}`
          );
        } catch (pollError: any) {
          consecutivePollErrors += 1;
          if (consecutivePollErrors >= 5) {
            throw new Error(`Lost contact with the backend during the sweep: ${pollError?.message || pollError}`);
          }
          continue;
        }
        if (pollRes.status === 404) throw new Error('The discovery job expired. Start a new sweep.');
        if (!pollRes.ok) {
          consecutivePollErrors += 1;
          if (consecutivePollErrors >= 5) throw new Error(await readError(pollRes));
          continue;
        }
        consecutivePollErrors = 0;
        snapshot = await pollRes.json();
        cursor = snapshot.cursor;

        const batch: any[] = snapshot.results || [];
        const fresh = batch.filter((item) => item.success);
        const failed = batch.filter((item) => !item.success);

        if (fresh.length) {
          onlineCount += fresh.length;
          // Strongest family first, then fastest inside each tier. Pure latency ordering put a
          // 762ms 4b safety classifier above claude-opus-5 at the head of the list, which is the
          // opposite of what someone assembling a debate fleet should see first.
          setAvailableDiscovered((prev) => [...prev, ...fresh].sort(
            (a, b) => discoveryTierRank(a) - discoveryTierRank(b) || a.latency_ms - b.latency_ms
          ));
          const favorites = fresh.filter((item) => item.is_admin_favorite);
          if (favorites.length) {
            sawFavorite = true;
            setSelectedDiscovered((prev) => {
              const next = { ...prev };
              favorites.forEach((item) => { next[item.model.id] = true; });
              return next;
            });
          }
        }
        if (failed.length) setUnavailableDiscovered((prev) => [...prev, ...failed]);

        setDiscoveryProgress({
          jobId: snapshot.job_id,
          status: snapshot.status,
          total: snapshot.total,
          done: snapshot.done,
          online: snapshot.online,
          failed: snapshot.failed,
          elapsed: snapshot.elapsed_seconds,
          finished: !!snapshot.finished,
          scope: snapshot.scope || scope,
          skippedByScope: snapshot.skipped_by_scope || 0
        });
        if (snapshot.catalogue) setDiscoveryCatalogue(snapshot.catalogue);

        if (snapshot.finished) break;
      }

      if (snapshot.status === 'error') {
        notify(`Discovery ended early: ${snapshot.error_message || 'unknown backend error'}`, 'error');
      } else if (!sawFavorite && onlineCount > 0 && !discoveryTouchedRef.current) {
        // No curated favorite came back online - fall back to selecting everything that did.
        setAvailableDiscovered((prev) => {
          const sel: Record<string, boolean> = {};
          prev.forEach((item) => { sel[item.model.id] = true; });
          setSelectedDiscovered(sel);
          return prev;
        });
      }
    } catch (e: any) {
      notify(`Model discovery failed: ${e.message}`, 'error');
    } finally {
      setIsDiscovering(false);
      discoveryJobIdRef.current = null;
    }
  };

  // A full sweep is ~820 live requests and several minutes, so it is always confirmed first -
  // including when it is launched as an upgrade from the quick-scan results screen.
  const confirmFullDiscovery = (listedTotal?: number) => {
    const listed = listedTotal && listedTotal > 0 ? listedTotal : null;
    setConfirmation({
      title: 'Search every advertised model?',
      description: `This probes ${listed ? `all ${listed}` : 'all 800+'} models these keys advertise, one live request each. `
        + 'It took about 7 to 8 minutes on the last full run, and on free-plan keys most of the extra models answer '
        + '"no credits" - the quick scan already covers the curated fleet and everything flagged free. '
        + 'Results stream in as they arrive and you can stop the sweep at any point.',
      confirmLabel: 'Search all models',
      onConfirm: () => {
        setConfirmation(null);
        void handleExecuteDiscovery('all');
      }
    });
  };

  const handleCancelDiscovery = async () => {
    const jobId = discoveryProgress?.jobId || discoveryJobIdRef.current;
    discoveryAbortRef.current = true;
    discoveryJobIdRef.current = null;
    setIsDiscovering(false);
    setDiscoveryProgress((prev) => (prev ? { ...prev, status: 'cancelled', finished: true } : prev));
    if (!jobId) return;
    try {
      await fetch(`/api/providers/auto-discover/cancel/${encodeURIComponent(jobId)}`, { method: 'POST' });
    } catch {
      // The sweep is already abandoned client-side; a failed cancel just leaves it to expire.
    }
  };

  // Quick select Admin Favorites only
  const handleSelectAdminFavorites = () => {
    discoveryTouchedRef.current = true;
    const sel: Record<string, boolean> = {};
    availableDiscovered.forEach((item) => {
      if (item.is_admin_favorite) {
        sel[item.model.id] = true;
      }
    });
    setSelectedDiscovered(sel);
  };

  const handleOpenSetupWizard = () => {
    const keys: Record<string, string> = {
      google_gemini: '',
      openrouter: '',
      agentrouter: '',
      xkiro: '',
      tokenin: '',
      tokenfaucet: '',
      bluesminds: '',
      tokenrouter: ''
    };
    models.forEach((m: ModelConfig) => {
      if (!m.api_key) return;
      const url = (m.base_url || '').toLowerCase();
      if (url.includes('generativelanguage.googleapis.com')) keys.google_gemini = m.api_key;
      else if (url.includes('openrouter.ai')) keys.openrouter = m.api_key;
      else if (url.includes('agentrouter.org')) keys.agentrouter = m.api_key;
      else if (url.includes('xkiro.com')) keys.xkiro = m.api_key;
      else if (url.includes('tokenin.my.id')) keys.tokenin = m.api_key;
      else if (url.includes('freetokenfaucet.com')) keys.tokenfaucet = m.api_key;
      else if (url.includes('bluesminds.com')) keys.bluesminds = m.api_key;
      else if (url.includes('tokenrouter.com')) keys.tokenrouter = m.api_key;
    });
    setWizardKeys((prev) => ({ ...prev, ...keys }));
    setWizardFlowState('initial_choice');
    setCardIndex(0);
    setIsWizardOpen(true);
  };

  // Apply selected models to THIS session only (preserves user_config.json)
  const handleApplyToSession = () => {
    const chosen = availableDiscovered
      .filter((item) => selectedDiscovered[item.model.id])
      .map((item) => item.model);

    if (chosen.length === 0) {
      notify('Select at least one verified model to continue.', 'error');
      return;
    }

    setModels(chosen);
    const newSel: Record<string, boolean> = {};
    chosen.forEach((m: ModelConfig) => { newSel[m.id] = true; });
    setSessionSelectedModels(newSel);

    const arb = chosen.find((m: any) => m.is_arbiter) || chosen[0];
    setArbiterModelId(arb.id);
    const bk = chosen.find((m: any) => m.is_backup_arbiter && m.id !== arb.id) || chosen[1] || chosen[0];
    setBackupArbiterModelId(bk.id);

    setIsWizardOpen(false);
    notify(`${chosen.length} verified models added to this session.`, 'success');
  };

  const handleAddCustomModel = () => {
    if (!customForm.base_url || !customForm.model_id) {
      notify('Enter both a base URL and model ID.', 'error');
      return;
    }
    const newId = `m_custom_${Date.now()}`;
    const newM: ModelConfig = {
      id: newId,
      name: customForm.name || 'Custom Model',
      base_url: customForm.base_url,
      model_id: customForm.model_id,
      api_key: customForm.api_key,
      backup_api_keys: [],
      fallback_model_ids: [],
      provider_type: 'openai_compatible',
      timeout_seconds: 600,
      is_arbiter: false,
      is_backup_arbiter: false,
      enabled: true,
      temperature: 0.7
    };
    const updated = [...models, newM];
    setModels(updated);
    setSessionSelectedModels({ ...sessionSelectedModels, [newId]: true });
    setIsWizardOpen(false);
    notify(`${newM.name} added to the fleet.`, 'success');
  };

  const handleAddModel = () => {
    const newId = `m_${Date.now()}`;
    const newModel: ModelConfig = {
      id: newId,
      name: `Custom Model ${models.length + 1}`,
      base_url: 'https://openrouter.ai/api/v1',
      api_key: '',
      backup_api_keys: [],
      model_id: 'custom-model-id',
      fallback_model_ids: [],
      provider_type: 'openai_compatible',
      timeout_seconds: 600,
      is_arbiter: false,
      is_backup_arbiter: false,
      enabled: true,
      temperature: 0.7
    };
    setModels([...models, newModel]);
    setSessionSelectedModels({ ...sessionSelectedModels, [newId]: true });
  };

  const handleDeleteModel = (id: string) => {
    if (models.length <= 2) {
      notify('The fleet must retain at least two models.', 'error');
      return;
    }
    setModels(models.filter((m) => m.id !== id));
    if (arbiterModelId === id) setArbiterModelId('');
    if (backupArbiterModelId === id) setBackupArbiterModelId('');
  };

  const handleTestModel = async (model: ModelConfig) => {
    setTestingModelId(model.id);
    try {
      const res = await fetch('/api/models/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config_id: model.id,
          base_url: model.base_url,
          api_key: model.api_key,
          backup_api_keys: model.backup_api_keys || [],
          model_id: model.model_id,
          provider_type: model.provider_type,
          timeout_seconds: 30
        })
      });
      const data = await res.json();
      setTestResults((prev) => ({ ...prev, [model.id]: data }));
    } catch (e: any) {
      setTestResults((prev) => ({
        ...prev,
        [model.id]: { success: false, message: e.message, latency_ms: 0 }
      }));
    } finally {
      setTestingModelId(null);
    }
  };

  const handleInjectDirective = async () => {
    if (!injectionText.trim()) return;
    try {
      await sendModeratorAction('inject_prompt', { injection_text: injectionText.trim() });
      setInjectionText('');
      setIsInjectModalOpen(false);
      notify('Directive queued for the next deliberation pass.', 'success');
    } catch (error: any) {
      notify(`Could not inject the directive: ${error.message}`, 'error');
    }
  };

  const handleOpenHistory = async () => {
    setIsHistoryModalOpen(true);
    setIsLoadingHistory(true);
    try {
      const res = await fetch('/api/workspaces');
      const data = await res.json();
      setSavedWorkspaces(Array.isArray(data) ? data : []);
    } catch (e: any) {
      notify(`Could not load session history: ${e.message}`, 'error');
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const [historySearchFilter, setHistorySearchFilter] = useState('');
  const [historyStatusFilter, setHistoryStatusFilter] = useState<'All' | 'live' | 'completed' | 'paused'>('All');

  const openNewSession = () => {
    setSessionId(null);
    localStorage.removeItem('active_debate_session_id');
    setProblemStatement('');
    setPsCode('');
    setSelectedPsObj(null);
    setAdditionalPrompt('');
    setArbiterModelId('m3');
    setBackupArbiterModelId('m4');
    setIsStartModalOpen(true);
  };

  const handleNewSession = () => {
    if (sessionId && currentStatus === 'running') {
      setConfirmation({
        title: 'Start a new session?',
        description: 'The current deliberation will remain saved in session history and may continue on the server. You can return to it at any time.',
        confirmLabel: 'Start new session',
        onConfirm: () => {
          setConfirmation(null);
          openNewSession();
        },
      });
      return;
    }
    openNewSession();
  };


  const handleLoadSavedSession = async (targetSessionId: string, shouldResume = false) => {
    setSessionId(targetSessionId);
    localStorage.setItem('active_debate_session_id', targetSessionId);
    setIsHistoryModalOpen(false);
    setActiveTab('arena');

    try {
      const res = await fetch(`/api/debate/${targetSessionId}`);
      if (res.ok) {
        const data: DebateSession = await res.json();
        if (data.problem_statement) setProblemStatement(data.problem_statement);
        if (data.ps_code) setPsCode(data.ps_code);
        if (data.ministry_domain) setMinistryDomain(data.ministry_domain);
        if (data.additional_prompt) setAdditionalPrompt(data.additional_prompt);

      if (shouldResume) {
        await fetch(`/api/debate/${targetSessionId}/resume`, { method: 'POST' });
        }
      }
    } catch (e: any) {
      notify(`Could not load the session: ${e.message}`, 'error');
    }
  };

  const deleteSession = async (targetSessionId: string) => {
    try {
      const res = await fetch(`/api/workspaces/${targetSessionId}`, { method: 'DELETE' });
      if (res.ok) {
        setSavedWorkspaces((prev) => prev.filter((w) => w.session_id !== targetSessionId));
        if (sessionId === targetSessionId) {
          setSessionId(null);
          localStorage.removeItem('active_debate_session_id');
        }
      } else {
        notify('The workspace could not be deleted.', 'error');
      }
    } catch (err: any) {
      notify(`Could not delete the workspace: ${err.message}`, 'error');
    }
  };

  const handleDeleteSession = (targetSessionId: string, folderName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setConfirmation({
      title: 'Delete this workspace?',
      description: `This permanently removes “${folderName}” and its saved deliverables from disk. This action cannot be undone.`,
      confirmLabel: 'Delete workspace',
      tone: 'danger',
      onConfirm: () => {
        setConfirmation(null);
        void deleteSession(targetSessionId);
      },
    });
  };

  const handleSendArbiterCommand = async (customCmd?: string) => {
    const cmd = customCmd || arbiterCommandText.trim();
    if (!cmd || !sessionId) {
      if (!sessionId) notify('Start or select a debate session before commanding the arbiter.', 'error');
      return;
    }
    
    setIsSendingArbiterCmd(true);
    const userMsg = { sender: 'You (Fleet Commander)', text: cmd, time: new Date().toLocaleTimeString() };
    setArbiterActionLogs((prev) => [...prev, userMsg]);
    if (!customCmd) setArbiterCommandText('');

    try {
      const res = await fetch(`/api/debate/${sessionId}/arbiter/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd })
      });
      const rawText = await res.text();
      let data: any = {};
      try {
        data = JSON.parse(rawText);
      } catch {
        data = { detail: rawText || `Server responded with HTTP ${res.status}` };
      }
      if (res.ok) {
        setArbiterActionLogs((prev) => [
          ...prev,
          {
            sender: `${data.arbiter_model || 'GPT 5.6 Sol'} (Master Arbiter)`,
            text: data.response || 'Command executed successfully.',
            time: new Date().toLocaleTimeString()
          }
        ]);
      } else {
        setArbiterActionLogs((prev) => [
          ...prev,
          {
            sender: 'System Alert',
            text: `Error: ${data.detail || data.message || 'Failed to execute command.'}`,
            time: new Date().toLocaleTimeString()
          }
        ]);
      }

    } catch (e: any) {
      setArbiterActionLogs((prev) => [
        ...prev,
        {
          sender: 'System Error',
          text: `Network error: ${e.message}`,
          time: new Date().toLocaleTimeString()
        }
      ]);
    } finally {
      setIsSendingArbiterCmd(false);
    }
  };

  const handleToggleModelTurnOff = async (modelId: string) => {
    const sessionModel = session?.models.find((model) => model.id === modelId);
    const isCurrentlyDisabled = Object.prototype.hasOwnProperty.call(disabledSessionModels, modelId)
      ? !!disabledSessionModels[modelId]
      : sessionModel?.enabled === false;
    const newDisabledState = !isCurrentlyDisabled;
    
    setDisabledSessionModels((prev) => ({
      ...prev,
      [modelId]: newDisabledState
    }));

    if (sessionId) {
      try {
        await sendModeratorAction(newDisabledState ? 'drop_model' : 'enable_model', { target_model_id: modelId });
      } catch (e: any) {
        setDisabledSessionModels((prev) => ({ ...prev, [modelId]: isCurrentlyDisabled }));
        notify(`Could not update the model: ${e.message}`, 'error');
      }
    }
  };

  const filteredPs = useMemo(() => {
    let list = psList;
    if (psCategoryFilter !== 'All') {
      list = list.filter((ps) => (ps.category || '').toLowerCase() === psCategoryFilter.toLowerCase());
    }
    if (!psFilter.trim()) {
      return list.slice(0, 25);
    }
    const tokens = psFilter.toLowerCase().trim().split(/\s+/).filter(Boolean);
    return list.filter((ps) => {
      const haystack = `${ps.ps_code || ''} ${ps.ps_id || ''} ${ps.title || ''} ${ps.organization || ''} ${ps.department || ''} ${ps.theme || ''} ${ps.category || ''} ${ps.description || ''}`.toLowerCase();
      return tokens.every((t) => haystack.includes(t));
    }).slice(0, 30);
  }, [psList, psFilter, psCategoryFilter]);

  const filteredFleet = useMemo(() => {
    return models.filter((model) => {
      if (fleetFilter === 'enabled') return sessionSelectedModels[model.id] !== false;
      if (fleetFilter === 'online') return testResults[model.id]?.success;
      return true;
    });
  }, [models, fleetFilter, sessionSelectedModels, testResults]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
      .then(() => {
        setCopiedVerdict(true);
        setTimeout(() => setCopiedVerdict(false), 2500);
      })
      .catch(() => notify('Could not access the clipboard. Download the report instead.', 'error'));
  };

  const currentProvider = WIZARD_PROVIDERS[cardIndex];

  const isSessionModelDisabled = (model: ModelConfig) => session
    ? (Object.prototype.hasOwnProperty.call(disabledSessionModels, model.id)
      ? Boolean(disabledSessionModels[model.id])
      : model.enabled === false)
    : !(sessionSelectedModels[model.id] ?? model.enabled);
  const activeModelCount = (session?.models || models).filter((model) => !isSessionModelDisabled(model)).length;
  const completedResponseCount = currentRound
    ? Object.values(currentRound.responses || {}).filter((response) => response.status === 'completed').length
    : 0;
  const currentRoundModelCount = activeModelCount;
  const notify = (message: string, tone: 'info' | 'success' | 'error' = 'info') => {
    setNotice({ message, tone });
    window.setTimeout(() => setNotice((previous) => previous?.message === message ? null : previous), 4200);
  };

  const runModeratorAction = (action: string, payload: any = {}) => {
    void sendModeratorAction(action, payload).catch((error: Error) => notify(error.message, 'error'));
  };

  return (
    <div className="app-shell flex flex-col">
      <WorkspaceHeader
        activeTab={activeTab}
        onTabChange={setActiveTab}
        theme={theme}
        onToggleTheme={toggleTheme}
        session={session}
        modelCount={models.length}
        activeModelCount={activeModelCount}
        savedWorkspaceCount={savedWorkspaces.length}
        researchSourceCount={session?.latest_research_dossier?.total_sources}
        onOpenHistory={handleOpenHistory}
        onOpenSetup={handleOpenSetupWizard}
        onNewSession={handleNewSession}
      />
      <SessionStatusBar
        status={currentStatus}
        statusText={liveStatusText}
        connectionStatus={connectionStatus}
        session={session}
        currentRound={currentRound}
        pipelineSteps={PIPELINE_STEPS}
        completedResponseCount={completedResponseCount}
        modelCount={currentRoundModelCount}
        onSelectRound={(index) => {
          userManuallySelectedRoundRef.current = true;
          setSelectedRoundIndex(index);
          setActiveTab('arena');
        }}
        onPause={() => runModeratorAction('pause')}
        onResume={() => runModeratorAction('resume')}
        onInject={() => setIsInjectModalOpen(true)}
        onFleetHealth={() => {
          void handleSendArbiterCommand('Scan all fleet models right now, diagnose hanging or failing nodes, report latencies, and optimize execution.');
          setIsArbiterCommandOpen(true);
        }}
        onCallVerdict={() => runModeratorAction('call_verdict')}
        onOpenArbiter={() => setIsArbiterCommandOpen(true)}
      />
      <main className="workspace flex-1">
        {activeTab === 'arena' && (
          <div className="workspace-stack">
            {!sessionId ? (
              <section className="empty-workspace">
                <div className="empty-workspace-content">
                  <div className="empty-workspace-icon"><Layers className="h-6 w-6" /></div>
                  <span className="eyebrow">Decision workspace</span>
                  <h2 className="mt-2">Build a defensible solution, not another single-model answer</h2>
                  <p>Select an official SIH brief or enter a custom challenge. The fleet will research the domain, challenge assumptions, test feasibility, and synthesize one evidence-backed verdict.</p>
                  <div className="empty-workspace-actions">
                    <button type="button" onClick={handleNewSession} className="primary-button"><Plus className="h-4 w-4" /> Start a deliberation</button>
                    <button type="button" onClick={handleOpenSetupWizard} className="secondary-button"><Wand2 className="h-4 w-4" /> Configure model fleet</button>
                    {savedWorkspaces.length > 0 && <button type="button" onClick={handleOpenHistory} className="quiet-button"><History className="h-4 w-4" /> Open recent work</button>}
                  </div>
                  <div className="mt-8 grid grid-cols-1 gap-3 text-left sm:grid-cols-3">
                    <div className="metric-card"><span className="eyebrow">01 · Frame</span><p className="!mx-0 !mt-2 text-xs">Start from an official problem statement and add real operating constraints.</p></div>
                    <div className="metric-card"><span className="eyebrow">02 · Stress-test</span><p className="!mx-0 !mt-2 text-xs">Compare architecture, risk, field feasibility, and security across the fleet.</p></div>
                    <div className="metric-card"><span className="eyebrow">03 · Decide</span><p className="!mx-0 !mt-2 text-xs">Resolve friction and export the final implementation-ready verdict.</p></div>
                  </div>
                </div>
              </section>
            ) : !session ? (
              <section className="empty-workspace" aria-live="polite">
                <div className="empty-workspace-content">
                  <RefreshCw className="mx-auto h-6 w-6 animate-spin text-[var(--primary)]" />
                  <h2 className="mt-4">Restoring the deliberation</h2>
                  <p>Loading the saved workspace and reconnecting to the live event stream.</p>
                  {activity.some((event) => event.severity === 'error') && (
                    <button type="button" onClick={() => void refreshSession()} className="secondary-button mt-5"><RefreshCw className="h-4 w-4" /> Retry now</button>
                  )}
                </div>
              </section>
            ) : (
              <>
                <section className="surface-panel debate-context">
                  <div className="min-w-0">
                    <span className="eyebrow">{session.ps_code || 'Custom challenge'} · {session.ministry_domain}</span>
                    <h2 className="mt-2">{session.session_title || session.current_phase_title || 'Active deliberation'}</h2>
                    <p className="line-clamp-3">{session.problem_statement}</p>
                  </div>
                  <div className="context-badges">
                    <span className="data-badge"><Bot className="h-3.5 w-3.5" /><strong>{activeModelCount}</strong> models</span>
                    <span className="data-badge"><Layers className="h-3.5 w-3.5" /><strong>{session.rounds.length}</strong> passes</span>
                    {currentRound?.arbiter_eval && <span className="data-badge"><Activity className="h-3.5 w-3.5" /><strong>{currentRound.arbiter_eval.consensus_score}%</strong> alignment</span>}
                  </div>
                </section>

                {activity.length > 0 && activity[activity.length - 1].severity !== 'info' && (
                  <section className={`response-notice ${activity[activity.length - 1].severity === 'error' ? 'response-notice-danger' : 'response-notice-warning'}`} role="status">
                    <AlertTriangle className="h-4 w-4 shrink-0" />
                    <div className="flex flex-1 items-start justify-between gap-4"><p>{activity[activity.length - 1].message}</p><button type="button" onClick={() => void refreshSession()} className="font-semibold underline underline-offset-2">Refresh</button></div>
                  </section>
                )}

                {session.rounds.length > 0 && (
                  <nav className="surface-panel round-selector" aria-label="Completed and active passes">
                    <span className="round-selector-label">Pass history</span>
                    {session.rounds.map((round, index) => {
                      const isSelected = selectedRoundIndex === index;
                      return (
                        <button key={`${round.workspace_phase_number || 1}-${round.pass_or_round_id || round.round_number}-${index}`} type="button" onClick={() => { userManuallySelectedRoundRef.current = true; setSelectedRoundIndex(index); }} className={`round-chip ${isSelected ? 'round-chip-active' : ''}`} aria-current={isSelected ? 'step' : undefined}>
                          <span>{round.pass_or_round_title || `Round ${round.round_number}`}</span>
                          {round.arbiter_eval?.consensus_score != null && <span className="count-badge">{round.arbiter_eval.consensus_score}%</span>}
                        </button>
                      );
                    })}
                  </nav>
                )}

                <section aria-labelledby="fleet-responses-title">
                  <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                    <div>
                      <span className="eyebrow">Fleet responses</span>
                      <h2 id="fleet-responses-title" className="mt-1 text-base font-semibold tracking-tight">{currentRound?.pass_or_round_title || 'Preparing the next pass'}</h2>
                    </div>
                    <p className="text-xs text-[var(--muted)]">{completedResponseCount} complete · {Object.keys(streamingModels).length} generating · {currentRoundModelCount - completedResponseCount - Object.keys(streamingModels).length > 0 ? currentRoundModelCount - completedResponseCount - Object.keys(streamingModels).length : 0} waiting</p>
                  </div>
                  <div className="debater-grid">
                    {session.models.map((model) => {
                      const isDisabled = Object.prototype.hasOwnProperty.call(disabledSessionModels, model.id)
                        ? !!disabledSessionModels[model.id]
                        : model.enabled === false;
                      return (
                      <DebaterCard
                        key={model.id}
                        model={model}
                        response={currentRound?.responses?.[model.id]}
                        streamText={activeTokens[model.id]}
                        isStreaming={Boolean(streamingModels[model.id])}
                        isArbiter={model.id === session.arbiter_model_id}
                        isBackupArbiter={model.id === session.backup_arbiter_model_id}
                        isDisabled={isDisabled}
                        passTitle={currentRound?.pass_or_round_title}
                        onToggle={() => void handleToggleModelTurnOff(model.id)}
                        onInspect={setSelectedScratchpadModel}
                      />
                      );
                    })}
                  </div>
                </section>
              </>
            )}
          </div>
        )}
        {/* TAB 2: 🔬 RESEARCH HUB */}
        {activeTab === 'research' && !session && (
          <WorkspaceEmptyState
            icon={BookOpen}
            eyebrow="Evidence workspace"
            title="Research begins with a deliberation brief"
            description="Start a session to collect fact checks, academic papers, field benchmarks, and applicable standards in one source-linked dossier."
            onNewSession={handleNewSession}
            onSetup={handleOpenSetupWizard}
          />
        )}
        {activeTab === 'research' && session && (
          <div className="workspace-stack">
            <div className="surface-panel p-5 sm:p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <span className="eyebrow">Evidence workspace</span>
                <h2 className="section-title mt-2">
                  <BookOpen className="w-5 h-5 text-[var(--warning)]" /> Pooled research dossier
                </h2>
                <p className="section-description">
                  Fact checks, academic evidence, field benchmarks, and statutory standards gathered across the deliberation.
                </p>
              </div>

              <div className="summary-badges">
                <div className="data-badge">Sources <strong>{session?.latest_research_dossier?.rendered_sources ?? session?.latest_research_dossier?.total_sources ?? 0}</strong> / {session?.latest_research_dossier?.total_sources || 0}</div>
                <div className="data-badge">PDFs <strong>{session?.latest_research_dossier?.downloaded_papers_count || 0}</strong></div>
              </div>
            </div>

            {/* STAGE 1 */}
            <div className="surface-panel p-5 sm:p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <h3 className="text-sm font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <Search className="w-4 h-4 text-[var(--primary)]" /> Stage 1 · Fact-check and claim verification
                </h3>
                <span className="text-xs text-slate-400 font-medium">Tavily Advanced Search</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(session?.latest_research_dossier?.stage_1_fact_checks?.length ?? 0) > 0 ? session?.latest_research_dossier?.stage_1_fact_checks.map((item, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-indigo-100 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300">
                        {item.tag}
                      </span>
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 font-bold"
                      >
                        Source Link <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    <h4 className="font-bold text-xs text-slate-900 dark:text-white leading-snug">{item.title}</h4>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{item.summary}</p>
                  </div>
                )) : (
                  <div className="col-span-full py-10 text-center text-xs text-slate-400"><Search className="mx-auto mb-2 h-5 w-5" /><p>No fact-check records gathered yet for this round.</p></div>
                )}
              </div>
            </div>

            {/* STAGE 2 */}
            <div className="surface-panel p-5 sm:p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <h3 className="text-sm font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-[var(--warning)]" /> Stage 2 · Academic and frontier research
                </h3>
                <span className="text-xs text-slate-400 font-medium">OpenAlex & arXiv Ingestion</span>
              </div>

              <div className="space-y-3">
                {(session?.latest_research_dossier?.stage_2_academic_papers?.length ?? 0) > 0 ? session?.latest_research_dossier?.stage_2_academic_papers.map((item, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300">
                          {item.tag}
                        </span>
                        <span className="text-xs text-slate-500 dark:text-slate-400 font-semibold">
                          {item.year ? `${item.year} · ` : ''}{item.citations ? `${item.citations} citations · ` : ''}{item.type}
                        </span>
                      </div>
                      <h4 className="font-bold text-xs text-slate-900 dark:text-white">{item.title}</h4>
                      <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{item.summary}</p>
                    </div>

                    <div className="flex items-center gap-2 self-end md:self-center shrink-0">
                      {sessionId && (
                        <>
                          <a
                            href={item.local_pdf_path ? `/api/workspaces/${encodeURIComponent(sessionId)}/research/${encodeURIComponent(item.local_pdf_path)}` : undefined}
                            download
                            aria-disabled={!item.local_pdf_path}
                            className={!item.local_pdf_path ? 'hidden' : 'flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold shadow-sm transition'}
                          >
                            <Download className="w-3.5 h-3.5" /> Download PDF
                          </a>
                          <a
                            href={item.local_txt_path ? `/api/workspaces/${encodeURIComponent(sessionId)}/research/${encodeURIComponent(item.local_txt_path)}` : undefined}
                            target="_blank"
                            rel="noreferrer"
                            className={!item.local_txt_path ? 'hidden' : 'flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 text-xs font-bold transition'}
                          >
                            <FileText className="w-3.5 h-3.5" /> Plain TXT
                          </a>
                        </>
                      )}
                    </div>
                  </div>
                )) : (
                  <div className="py-10 text-center text-xs text-slate-400"><BookOpen className="mx-auto mb-2 h-5 w-5" /><p>No academic papers discovered yet for this round.</p></div>
                )}
              </div>
            </div>

            {/* STAGE 3 */}
            <div className="surface-panel p-5 sm:p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <h3 className="text-sm font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <Shield className="w-4 h-4 text-[var(--success)]" /> Stage 3 · Field feasibility, BOM, and standards
                </h3>
                <span className="text-xs text-slate-400 font-medium">Field Studies & Statutory Norms</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(session?.latest_research_dossier?.stage_3_field_benchmarks?.length ?? 0) > 0 ? session?.latest_research_dossier?.stage_3_field_benchmarks.map((item, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300">
                        {item.tag}
                      </span>
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-1 font-bold"
                      >
                        Norms Link <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    <h4 className="font-bold text-xs text-slate-900 dark:text-white leading-snug">{item.title}</h4>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{item.summary}</p>
                  </div>
                )) : (
                  <div className="col-span-full py-10 text-center text-xs text-slate-400"><Shield className="mx-auto mb-2 h-5 w-5" /><p>No field benchmarks gathered yet for this round.</p></div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: ⚔️ CRITIQUE MATRIX */}
        {activeTab === 'critiques' && !session && (
          <WorkspaceEmptyState
            icon={Swords}
            eyebrow="Adversarial review"
            title="No cross-examination to review yet"
            description="Start a session to see where models disagree, which assumptions remain unresolved, and how each proposal adapts under challenge."
            onNewSession={handleNewSession}
            onSetup={handleOpenSetupWizard}
          />
        )}
        {activeTab === 'critiques' && session && (
          <div className="workspace-stack">
            <div className="surface-panel p-5 sm:p-6 space-y-4">
              <span className="eyebrow">Adversarial review</span>
              <h2 className="section-title">
                <Swords className="w-5 h-5 text-[var(--danger)]" /> Cross-examination and friction log
              </h2>
              <p className="section-description">
                Peer challenges, unresolved assumptions, counter-arguments, and the adaptations each model made in response.
              </p>

              {currentRound?.arbiter_eval?.friction_points && currentRound.arbiter_eval.friction_points.length > 0 && (
                <div className="p-4 rounded-2xl bg-purple-50/70 dark:bg-purple-950/50 border border-purple-200/80 dark:border-purple-800 space-y-3">
                  <h3 className="text-xs font-black text-purple-900 dark:text-purple-300 uppercase tracking-wider flex items-center gap-2">
                    <Award className="w-4 h-4 text-purple-600 dark:text-purple-400" /> Master Arbiter Jury Friction Log
                  </h3>
                  <div className="space-y-2">
                    {currentRound.arbiter_eval.friction_points.map((fp, idx) => (
                      <div key={idx} className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-purple-100 dark:border-purple-800/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${
                              fp.status === 'RESOLVED' ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300' : fp.status === 'CONCEDED' ? 'bg-indigo-100 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300' : 'bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300'
                            }`}>
                              {fp.status}
                            </span>
                            <span className="font-bold text-slate-800 dark:text-slate-200">{fp.issue}</span>
                          </div>
                          <p className="text-slate-500 dark:text-slate-400 text-[11px]">{fp.resolution_notes}</p>
                        </div>
                        <div className="text-[11px] text-slate-400 shrink-0">
                          Raised by <strong>{fp.raised_by}</strong> · Challenged by <strong>{fp.challenged_by}</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-4 pt-2">
                {currentRound?.responses && Object.values(currentRound.responses).some((r) => (r.structured?.critiques?.length ?? 0) > 0 || (r.structured?.concessions_and_defenses?.length ?? 0) > 0) ? (
                  Object.values(currentRound.responses).map((resp) => {
                    if ((resp.structured?.critiques?.length ?? 0) === 0 && (resp.structured?.concessions_and_defenses?.length ?? 0) === 0) return null;
                    return (
                      <div key={resp.model_id} className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-3">
                        <h4 className="font-black text-sm text-slate-900 dark:text-white flex items-center gap-2">
                          <Bot className="w-4 h-4 text-indigo-600 dark:text-indigo-400" /> {resp.model_name}
                        </h4>

                        {(resp.structured?.critiques?.length ?? 0) > 0 && (
                          <div className="space-y-2">
                            <span className="text-[11px] font-bold uppercase tracking-wider text-rose-700 dark:text-rose-400">⚔️ Critiques Launched:</span>
                            {resp.structured?.critiques?.map((c, idx) => (
                              <div key={idx} className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-rose-100 dark:border-rose-900/60 space-y-1 text-xs">
                                <div className="font-bold text-rose-900 dark:text-rose-300">
                                  Target: <span className="text-slate-900 dark:text-white font-black">{c.target_model_name}</span> · Flaw: {c.flaw_identified}
                                </div>
                                <p className="text-slate-600 dark:text-slate-300">{c.counter_argument}</p>
                              </div>
                            ))}
                          </div>
                        )}

                        {(resp.structured?.concessions_and_defenses?.length ?? 0) > 0 && (
                          <div className="space-y-2 pt-2">
                            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">🛡️ Concessions & Adaptations:</span>
                            {resp.structured?.concessions_and_defenses?.map((cd, idx) => (
                              <div key={idx} className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-emerald-100 dark:border-emerald-900/60 space-y-1 text-xs">
                                <div className="font-bold text-emerald-900 dark:text-emerald-300">
                                  Conceded to: <span className="text-slate-900 dark:text-white font-black">{cd.conceded_to}</span> · Point: {cd.conceded_point}
                                </div>
                                <p className="text-slate-600 dark:text-slate-300">{cd.adaptation}</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })
                ) : (
                  <p className="text-xs text-slate-400 italic">No critiques recorded in this sub-round yet.</p>
                )}
              </div>

            </div>
          </div>
        )}

        {/* TAB 4: 👑 VERDICT STUDIO */}
        {activeTab === 'verdict' && !session && (
          <WorkspaceEmptyState
            icon={Award}
            eyebrow="Decision document"
            title="Your consensus deliverable will appear here"
            description="Start a deliberation to synthesize the fleet’s strongest architecture, evidence, risks, concessions, and implementation guidance."
            onNewSession={handleNewSession}
            onSetup={handleOpenSetupWizard}
          />
        )}
        {activeTab === 'verdict' && session && (
          <div className="workspace-stack">
            <div className="surface-panel p-5 sm:p-6 lg:p-8 space-y-6">
              
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-5">
                <div>
                  <span className="eyebrow">Decision document</span>
                  <h2 className="section-title mt-2">
                    <Award className="w-6 h-6 text-[var(--primary)]" /> Master consensus deliverable
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    Definitive multi-model ratified blueprint with itemized ₹ BOM and specifications.
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => copyToClipboard(session?.final_markdown_report || '')}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold transition shadow-sm"
                  >
                    {copiedVerdict ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
                    {copiedVerdict ? 'Copied!' : 'Copy Markdown'}
                  </button>

                  {sessionId && (
                    <a
                      href={`/api/workspaces/${sessionId}/files/LATEST_CONSENSUS_VERDICT.md`}
                      download
                      className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition shadow-md shadow-purple-500/20"
                    >
                      <Download className="w-4 h-4" /> Download .MD
                    </a>
                  )}
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-950/40 dark:to-indigo-950/40 border border-purple-200 dark:border-purple-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <span className="text-xs font-black text-purple-900 dark:text-purple-300 uppercase tracking-wider">
                    🏆 Multi-Model Consensus Ratification Certificate
                  </span>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    {currentRound?.arbiter_eval?.is_unanimous ? 'Ratified' : 'Synthesized'} from {(session?.models || models).filter((m) => m.enabled).length} AI models with {currentRound?.arbiter_eval?.friction_points?.filter((point) => point.status === 'OPEN').length || 0} open friction points.
                  </p>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  {(session?.models || models).filter((m) => m.enabled).map((m) => (
                    <span key={m.id} className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-white dark:bg-slate-900 text-purple-900 dark:text-purple-300 border border-purple-200 dark:border-purple-800 shadow-xs flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-emerald-500" /> {m.name}
                    </span>
                  ))}
                </div>
              </div>

              {session?.final_markdown_report ? (
                <article className="verdict-document prose prose-slate dark:prose-invert max-w-none prose-headings:font-bold prose-h1:text-2xl prose-h2:text-lg prose-h3:text-base prose-p:text-sm prose-p:leading-7 prose-li:text-sm prose-li:leading-7 prose-table:text-xs prose-th:bg-slate-100 dark:prose-th:bg-slate-800 prose-th:p-2 prose-td:p-2 prose-td:border prose-td:border-slate-200 dark:prose-td:border-slate-700">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {session.final_markdown_report}
                  </ReactMarkdown>
                </article>
              ) : (
                <div className="py-16 text-center space-y-3">
                  <div className="p-4 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 w-14 h-14 mx-auto flex items-center justify-center">
                    <Award className="w-7 h-7" />
                  </div>
                  <h3 className="font-bold text-sm text-slate-700 dark:text-slate-300">Deliberation in Progress</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
                    The Grand Finale Sovereign Blueprint is synthesized once all 4 Deliberation Phases complete or when you click <strong>Final Verdict</strong> above.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 5: ⚙️ FLEET & MASTER CONFIG */}
        {activeTab === 'config' && (
          <div className="workspace-stack">
            <div className="metric-row">
              <div className="metric-card">
                <span className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider">Total Configured</span>
                <div className="text-2xl font-black text-slate-900 dark:text-white">{models.length}</div>
                <span className="text-[11px] text-slate-400">Master Fleet</span>
              </div>

              <div className="metric-card">
                <span className="text-xs text-emerald-600 dark:text-emerald-400 font-bold uppercase tracking-wider">Active in Session</span>
                <div className="text-2xl font-black text-emerald-700 dark:text-emerald-300">{models.filter((m) => sessionSelectedModels[m.id] ?? m.enabled).length}</div>
                <span className="text-[11px] text-slate-400">Participating</span>
              </div>

              <div className="metric-card">
                <span className="text-xs text-purple-600 dark:text-purple-400 font-bold uppercase tracking-wider">Primary Arbiter</span>
                <div className="text-sm font-black text-purple-900 dark:text-purple-300 truncate">
                  {models.find((m) => m.id === arbiterModelId)?.name || 'Gemini 3.5 Lite'}
                </div>
                <span className="text-[11px] text-purple-500 font-semibold">Chief Jury Foreman</span>
              </div>

              <div className="metric-card">
                <span className="text-xs text-amber-600 dark:text-amber-400 font-bold uppercase tracking-wider">Backup Arbiter</span>
                <div className="text-sm font-black text-amber-900 dark:text-amber-300 truncate">
                  {models.find((m) => m.id === backupArbiterModelId)?.name || 'Gemini Flash Pool'}
                </div>
                <span className="text-[11px] text-amber-500 font-semibold">Failover Redundancy</span>
              </div>
            </div>

            <div className="surface-panel p-5 sm:p-6 space-y-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-4">
                <div>
                  <span className="eyebrow">Infrastructure</span>
                  <h2 className="section-title mt-2">
                    <KeyRound className="w-5 h-5 text-[var(--primary)]" /> Model fleet and API credentials
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    Manage baseline endpoints and credentials. Selection changes during debates are kept per-session.
                  </p>
                </div>

                <div className="flex items-center gap-2.5 flex-wrap">
                  <button
                    onClick={handleOpenSetupWizard}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-50 dark:bg-amber-950 hover:bg-amber-100 dark:hover:bg-amber-900 text-amber-900 dark:text-amber-200 border border-amber-200 dark:border-amber-800 text-xs font-bold transition shadow-sm"
                  >
                    <Wand2 className="w-4 h-4 text-amber-600" /> API Setup Wizard
                  </button>

                  <button
                    onClick={handleTestAllModels}
                    disabled={isTestingAll}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold transition shadow-sm"
                  >
                    {isTestingAll ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4 text-amber-600" />}
                    {isTestingAll ? 'Testing Fleet...' : 'Test All Latencies'}
                  </button>

                  <button
                    onClick={handleAddModel}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold transition shadow-sm"
                  >
                    <Plus className="w-4 h-4 text-indigo-600" /> Add Model
                  </button>

                  <button
                    onClick={handleSaveMasterConfig}
                    className="flex items-center gap-1.5 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-500/20 transition"
                  >
                    <Check className="w-4 h-4" /> Save Default Config
                  </button>
                </div>
              </div>
              <div className="p-5 rounded-2xl bg-amber-50/50 dark:bg-amber-950/30 border border-amber-200/80 dark:border-amber-900/60 space-y-4">
                <h3 className="text-xs font-black text-amber-900 dark:text-amber-300 uppercase tracking-wider flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-amber-600" /> Autonomous Research Engine Credentials
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Tavily API Key (Live Web & Standards):</label>
                    <input
                      type="password"
                      value={researchConfig.tavily_api_key}
                      onChange={(e) => setResearchConfig({ ...researchConfig, tavily_api_key: e.target.value })}
                      placeholder="tvly-..."
                      className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono focus:ring-2 focus:ring-amber-400 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">OpenAlex Polite Pool Email (250M Papers Graph):</label>
                    <input
                      type="email"
                      value={researchConfig.openalex_email}
                      onChange={(e) => setResearchConfig({ ...researchConfig, openalex_email: e.target.value })}
                      placeholder="user@example.com"
                      className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono focus:ring-2 focus:ring-amber-400 focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Filter Tabs for Fleet */}
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setFleetFilter('all')}
                    className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                      fleetFilter === 'all' ? 'bg-slate-800 dark:bg-slate-700 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                    }`}
                  >
                    All ({models.length})
                  </button>
                  <button
                    onClick={() => setFleetFilter('enabled')}
                    className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                      fleetFilter === 'enabled' ? 'bg-indigo-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                    }`}
                  >
                    Active ({models.filter((m) => sessionSelectedModels[m.id] ?? m.enabled).length})
                  </button>
                  <button
                    onClick={() => setFleetFilter('online')}
                    className={`px-3 py-1 rounded-lg text-xs font-bold transition ${
                      fleetFilter === 'online' ? 'bg-emerald-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                    }`}
                  >
                    Online ({Object.values(testResults).filter((r) => r.success).length})
                  </button>
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                  <span>Session Fleet:</span>
                  <button
                    onClick={() => {
                      const allOn: Record<string, boolean> = {};
                      models.forEach((m) => { allOn[m.id] = true; });
                      setSessionSelectedModels(allOn);
                    }}
                    className="text-indigo-600 dark:text-indigo-400 font-bold hover:underline"
                  >
                    Enable All
                  </button>
                  <span>·</span>
                  <button
                    onClick={() => {
                      const allOff: Record<string, boolean> = {};
                      models.forEach((model) => { allOff[model.id] = false; });
                      setSessionSelectedModels(allOff);
                    }}
                    className="text-slate-500 font-bold hover:underline"
                  >
                    Disable All
                  </button>
                </div>
              </div>

              {/* Model Fleet Table */}
              <div className="space-y-3">
                {filteredFleet.map((model, idx) => {
                  const isArb = model.id === arbiterModelId;
                  const isBkArb = model.id === backupArbiterModelId;
                  const test = testResults[model.id];
                  const isChecked = sessionSelectedModels[model.id] ?? model.enabled;

                  return (
                    <div
                      key={model.id}
                      className={`p-4 rounded-2xl border transition flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
                        isChecked ? 'bg-slate-50/70 dark:bg-slate-850 border-slate-200 dark:border-slate-800' : 'bg-slate-100/50 dark:bg-slate-900/50 border-slate-200 dark:border-slate-800 opacity-60'
                      }`}
                    >
                      <div className="space-y-1.5 md:w-1/4">
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={(e) => {
                              setSessionSelectedModels({
                                ...sessionSelectedModels,
                                [model.id]: e.target.checked
                              });
                            }}
                            className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4 cursor-pointer"
                          />
                          <input
                            type="text"
                            value={model.name}
                            onChange={(e) => {
                              setModels((previous) => previous.map((item) => item.id === model.id ? { ...item, name: e.target.value } : item));
                            }}
                            className="font-extrabold text-xs text-slate-900 dark:text-white bg-transparent border-b border-dashed border-slate-300 dark:border-slate-700 focus:outline-none focus:border-indigo-500"
                          />
                        </div>
                        <input
                          type="text"
                          value={model.model_id}
                          onChange={(e) => {
                              setModels((previous) => previous.map((item) => item.id === model.id ? { ...item, model_id: e.target.value } : item));
                          }}
                          className="text-[11px] text-slate-500 dark:text-slate-400 font-mono pl-6 bg-transparent border-b border-dashed border-slate-300 dark:border-slate-700 focus:outline-none focus:border-indigo-500 w-full"
                        />
                      </div>

                      <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-2 w-full md:w-auto">
                        <div>
                          <input
                            type="password"
                            placeholder="Primary API Key..."
                            value={model.api_key}
                            onChange={(e) => {
                              setModels((previous) => previous.map((item) => item.id === model.id ? { ...item, api_key: e.target.value } : item));
                            }}
                            className="w-full px-3 py-1.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono focus:ring-2 focus:ring-indigo-400 focus:outline-none"
                          />
                        </div>

                        <div className="flex items-center gap-2">
                          <input
                            type="text"
                            placeholder="Base URL..."
                            value={model.base_url}
                            onChange={(e) => {
                              setModels((previous) => previous.map((item) => item.id === model.id ? { ...item, base_url: e.target.value } : item));
                            }}
                            className="w-full px-3 py-1.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono focus:ring-2 focus:ring-indigo-400 focus:outline-none"
                          />
                          {test && (
                            <span className={`px-2 py-1 rounded-lg text-[10px] font-black uppercase whitespace-nowrap ${
                              test.success ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300' : 'bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300'
                            }`}>
                              {test.success ? `🟢 ${test.latency_ms}ms` : '🔴 Error'}
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2.5 w-full md:w-auto justify-end">
                        <label className="flex items-center gap-1 text-xs text-slate-700 dark:text-slate-300 cursor-pointer font-bold">
                          <input
                            type="radio"
                            name="arbiterRadio"
                            checked={isArb}
                            onChange={() => setArbiterModelId(model.id)}
                            className="text-purple-600 focus:ring-purple-500"
                          />
                          Primary
                        </label>

                        <label className="flex items-center gap-1 text-xs text-slate-700 dark:text-slate-300 cursor-pointer font-bold">
                          <input
                            type="radio"
                            name="backupArbiterRadio"
                            checked={isBkArb}
                            onChange={() => setBackupArbiterModelId(model.id)}
                            className="text-amber-600 focus:ring-amber-500"
                          />
                          Backup
                        </label>

                        <button
                          onClick={() => handleTestModel(model)}
                          disabled={testingModelId === model.id}
                          className="px-2.5 py-1.5 rounded-xl bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold transition flex items-center gap-1"
                        >
                          {testingModelId === model.id ? (
                            <RefreshCw className="w-3 h-3 animate-spin" />
                          ) : (
                            <Zap className="w-3 h-3 text-amber-600" />
                          )}
                          Test
                        </button>

                        <button
                          onClick={() => handleDeleteModel(model.id)}
                          className="p-1.5 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/60 transition"
                          title="Remove Model"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </main>

      {notice && (
        <div className={`notice-toast notice-toast-${notice.tone}`} role={notice.tone === 'error' ? 'alert' : 'status'} aria-live="polite">
          {notice.tone === 'success' ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[var(--success)]" /> : notice.tone === 'error' ? <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-[var(--danger)]" /> : <Activity className="mt-0.5 h-4 w-4 shrink-0 text-[var(--primary)]" />}
          <span>{notice.message}</span>
          <button type="button" onClick={() => setNotice(null)} className="ml-auto text-[var(--muted)]" aria-label="Dismiss notification"><X className="h-4 w-4" /></button>
        </div>
      )}

      <TimeoutAlertModal
        alert={timeoutAlert}
        models={session?.models || models}
        onClose={() => setTimeoutAlert(null)}
        onUpdateAndRetry={(updatedConfig) => {
          void sendModeratorAction('update_model_and_retry', { ai_model_config: updatedConfig })
            .then(() => notify(`${updatedConfig.name} queued for retry.`, 'success'))
            .catch((error: Error) => notify(`Could not retry ${updatedConfig.name}: ${error.message}`, 'error'));
        }}
        onDropModel={(modelId) => {
          void handleToggleModelTurnOff(modelId);
        }}
      />

      {confirmation && (
        <ConfirmDialog
          title={confirmation.title}
          description={confirmation.description}
          confirmLabel={confirmation.confirmLabel}
          tone={confirmation.tone}
          onCancel={() => setConfirmation(null)}
          onConfirm={confirmation.onConfirm}
        />
      )}

      {/* ========================================================================= */}
      {/* 4. COMPREHENSIVE CARD-BY-CARD API SETUP WIZARD */}
      {/* ========================================================================= */}
      {isWizardOpen && (
        <div className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="modal-panel max-h-[90vh] w-full max-w-xl space-y-5 overflow-y-auto p-6 lg:p-8" role="dialog" aria-modal="true" aria-labelledby="setup-dialog-title" tabIndex={-1}>
            
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-2xl bg-amber-500/10 text-amber-600 flex items-center justify-center font-black text-sm">
                  <Wand2 className="w-5 h-5" />
                </div>
                <div>
                  <h3 id="setup-dialog-title" className="text-base font-black text-slate-900 dark:text-white">
                    {wizardFlowState === 'initial_choice'
                      ? 'AI Provider Setup Wizard'
                      : wizardFlowState === 'cards'
                      ? `Provider ${cardIndex + 1} of ${WIZARD_PROVIDERS.length}`
                      : wizardFlowState === 'results'
                      ? 'Select Models for Deliberation'
                      : 'Custom LLM Endpoint'}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {wizardFlowState === 'initial_choice'
                      ? 'Choose your preferred setup method.'
                      : wizardFlowState === 'cards'
                      ? 'Enter API key or click redirect link to get a free key.'
                      : wizardFlowState === 'results'
                      ? 'Search every discovered model, or 1-click Admin Favorites.'
                      : 'Add your custom endpoint (Ollama / vLLM).'}
                  </p>
                </div>
              </div>

              <button
                onClick={() => setIsWizardOpen(false)}
                className="p-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition"
                aria-label="Close setup wizard"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* STAGE A: INITIAL CHOICE SCREEN (EASY vs CUSTOM) */}
            {wizardFlowState === 'initial_choice' && (
              <div className="space-y-4 py-2">
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  How would you like to set up your AI models and API credentials?
                </p>

                <div className="grid grid-cols-1 gap-3.5">
                  {/* Option 1: Easy Setup Card */}
                  <button
                    onClick={() => {
                      setCardIndex(0);
                      setWizardFlowState('cards');
                    }}
                    className="p-5 rounded-2xl bg-gradient-to-r from-amber-500/10 via-indigo-500/10 to-transparent border-2 border-amber-500/30 hover:border-amber-500 hover:shadow-lg transition text-left space-y-2 group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 font-black text-sm text-slate-900 dark:text-white">
                        <span className="text-xl">🌟</span>
                        <span>Easy Setup (Recommended)</span>
                      </div>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-black uppercase bg-amber-500 text-white shadow-xs">
                        Fast & Automated
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                      Guided step-by-step card tour for each provider. Includes 1-click redirect links to get free API keys, automatic model speed benchmarking, and instant 1-click <strong>Admin's Favorites</strong> selection!
                    </p>
                    <div className="flex items-center gap-1.5 text-xs font-bold text-amber-600 dark:text-amber-400 group-hover:translate-x-1 transition pt-1">
                      <span>Start Guided Tour</span>
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  </button>

                  {/* Option 2: Custom Setup Card */}
                  <button
                    onClick={() => setWizardFlowState('custom')}
                    className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 hover:border-slate-400 dark:hover:border-slate-600 hover:shadow-md transition text-left space-y-2 group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 font-black text-sm text-slate-900 dark:text-white">
                        <span className="text-xl">⚙️</span>
                        <span>Custom Endpoint Setup</span>
                      </div>
                      <span className="text-xs text-slate-400 font-semibold">Self-Hosted / Local</span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                      Directly enter a custom OpenAI-compatible Base URL (e.g. Local Ollama, vLLM, private GPU server) with your custom Model ID and parameters.
                    </p>
                    <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700 dark:text-slate-300 group-hover:translate-x-1 transition pt-1">
                      <span>Configure Custom Endpoint</span>
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  </button>
                </div>
              </div>
            )}

            {/* STAGE B: ONE-BY-ONE PROVIDER CARD TOUR */}
            {wizardFlowState === 'cards' && currentProvider && (
              <div className="space-y-5">
                
                {/* Visual Progress Bar */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 font-bold">
                    <span>Provider {cardIndex + 1} of {WIZARD_PROVIDERS.length}</span>
                    <span className="text-amber-600 dark:text-amber-400">{Math.round(((cardIndex + 1) / WIZARD_PROVIDERS.length) * 100)}% Completed</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-500 transition-all duration-300 rounded-full"
                      style={{ width: `${((cardIndex + 1) / WIZARD_PROVIDERS.length) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Main Provider Card */}
                <div className="p-5 rounded-3xl bg-slate-50/80 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-4 shadow-sm">
                  
                  {/* Card Header & Redirect Link */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <span className="text-3xl p-2 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs">
                        {currentProvider.icon}
                      </span>
                      <div>
                        <h4 className="font-extrabold text-sm text-slate-900 dark:text-white leading-tight">
                          {currentProvider.name}
                        </h4>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300">
                          {currentProvider.tier}
                        </span>
                      </div>
                    </div>

                    <a
                      href={currentProvider.direct_link}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-indigo-600 dark:text-indigo-400 border border-slate-200 dark:border-slate-700 text-xs font-bold shadow-xs transition shrink-0"
                    >
                      <span>Get API Key</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>

                  <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                    {currentProvider.desc}
                  </p>

                  {/* API Key Input Box */}
                  {currentProvider.id === 'research' ? (
                    <div className="space-y-3 pt-1">
                      <div>
                        <label className="block text-xs font-bold text-slate-800 dark:text-slate-200 mb-1">
                          Tavily Web Search Key:
                        </label>
                        <input
                          type="password"
                          value={researchConfig.tavily_api_key}
                          onChange={(e) => setResearchConfig({ ...researchConfig, tavily_api_key: e.target.value })}
                          placeholder="tvly-..."
                          className="w-full px-3.5 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono focus:ring-2 focus:ring-amber-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-800 dark:text-slate-200 mb-1">
                          OpenAlex Research Email (250M Papers Graph):
                        </label>
                        <input
                          type="email"
                          value={researchConfig.openalex_email}
                          onChange={(e) => setResearchConfig({ ...researchConfig, openalex_email: e.target.value })}
                          placeholder="campusprintexpress@gmail.com"
                          className="w-full px-3.5 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono focus:ring-2 focus:ring-amber-500 focus:outline-none"
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-1.5 pt-1">
                      <label className="block text-xs font-bold text-slate-800 dark:text-slate-200">
                        Paste {currentProvider.name} Key:
                      </label>
                      <input
                        type="password"
                        value={wizardKeys[currentProvider.id] || ''}
                        onChange={(e) => setWizardKeys({ ...wizardKeys, [currentProvider.id]: e.target.value })}
                        placeholder={currentProvider.placeholder}
                        className="w-full px-3.5 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono focus:ring-2 focus:ring-amber-500 focus:outline-none shadow-inner"
                      />
                    </div>
                  )}
                </div>

                {/* Bottom Navigation Buttons */}
                <div className="flex items-center justify-between pt-2">
                  <div>
                    {cardIndex > 0 ? (
                      <button
                        onClick={() => setCardIndex(cardIndex - 1)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-bold transition"
                      >
                        <ArrowLeft className="w-3.5 h-3.5" /> Previous
                      </button>
                    ) : (
                      <button
                        onClick={() => setWizardFlowState('initial_choice')}
                        className="px-3 py-2 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs font-bold transition"
                      >
                        Back
                      </button>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {cardIndex < WIZARD_PROVIDERS.length - 1 ? (
                      <>
                        <button
                          onClick={() => {
                            if (currentProvider.id === 'research') setResearchConfig((previous) => ({ ...previous, tavily_api_key: '' }));
                            else setWizardKeys((previous) => ({ ...previous, [currentProvider.id]: '' }));
                            setCardIndex(cardIndex + 1);
                          }}
                          className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-bold transition"
                        >
                          Skip ↷
                        </button>

                        <button
                          onClick={() => setCardIndex(cardIndex + 1)}
                          className="flex items-center gap-1.5 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-black shadow-md transition"
                        >
                          Next <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </>
                    ) : (
                      <div className="flex flex-col items-stretch gap-1.5">
                        <button
                          onClick={() => void handleExecuteDiscovery('quick')}
                          disabled={isDiscovering}
                          className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 disabled:opacity-60 text-white text-xs font-black shadow-md transition"
                        >
                          {isDiscovering ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                          {isDiscovering ? 'Listing Catalogues...' : '⚡ Quick Scan — Free + Curated'}
                        </button>
                        <button
                          onClick={() => confirmFullDiscovery()}
                          disabled={isDiscovering}
                          className="flex items-center justify-center gap-1.5 px-6 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-60 text-slate-700 dark:text-slate-200 text-[11px] font-bold transition"
                        >
                          <Search className="w-3.5 h-3.5" /> Search All 800+ Models
                        </button>
                        <p className="text-[10px] text-slate-400 text-center max-w-[15rem]">
                          Quick scan takes ~3 min. The full sweep takes ~8 min and asks to confirm first.
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* STAGE C: RESULTS & ADMIN FAVORITES SELECTION */}
            {wizardFlowState === 'results' && (
              <div className="space-y-4">
                
                {/* Live sweep progress: a full catalogue sweep can run for minutes */}
                {discoveryProgress && (
                  <div className="p-3.5 rounded-2xl border-2 border-indigo-500/30 bg-indigo-50/60 dark:bg-indigo-950/30 space-y-2">
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-2 text-xs font-black text-indigo-900 dark:text-indigo-300">
                        {discoveryProgress.finished
                          ? <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                          : <RefreshCw className="w-4 h-4 animate-spin" />}
                        <span>
                          {discoveryProgress.finished
                            ? (discoveryProgress.status === 'cancelled' ? 'Sweep stopped' : 'Sweep complete')
                            : discoveryProgress.status === 'retrying'
                              ? 'Re-testing throttled models one at a time...'
                              : discoveryProgress.scope === 'quick'
                                ? 'Quick scan: benchmarking curated + free models...'
                                : 'Full sweep: benchmarking every advertised model...'}
                        </span>
                      </div>
                      {!discoveryProgress.finished && (
                        <button
                          onClick={handleCancelDiscovery}
                          className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 text-[11px] font-black transition hover:bg-rose-200 dark:hover:bg-rose-900"
                        >
                          <X className="w-3 h-3" /> Stop &amp; use what we have
                        </button>
                      )}
                    </div>

                    <div className="h-2 w-full rounded-full bg-indigo-200/60 dark:bg-indigo-900/60 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-indigo-500 transition-all duration-500"
                        style={{
                          width: `${discoveryProgress.total
                            ? Math.min(100, Math.round((discoveryProgress.done / discoveryProgress.total) * 100))
                            : 0}%`
                        }}
                      />
                    </div>

                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] font-mono text-slate-600 dark:text-slate-400">
                      <span className="font-bold text-slate-800 dark:text-slate-200">
                        {discoveryProgress.done} / {discoveryProgress.total} tested
                      </span>
                      <span className="text-emerald-600 dark:text-emerald-400">🟢 {discoveryProgress.online} online</span>
                      <span className="text-rose-500">🔴 {discoveryProgress.failed} failed</span>
                      <span>· {discoveryProgress.elapsed.toFixed(0)}s elapsed</span>
                    </div>

                    {/* A quick scan deliberately leaves the paid long tail untested. Say so, with
                        the exact count, rather than letting the list imply it covered everything. */}
                    {discoveryProgress.scope === 'quick' && discoveryProgress.skippedByScope > 0 && (
                      <div className="flex flex-wrap items-center gap-2 pt-1.5 border-t border-indigo-500/20 text-[11px] text-slate-600 dark:text-slate-400">
                        <span>
                          <span className="font-bold text-slate-800 dark:text-slate-200">{discoveryProgress.skippedByScope}</span>
                          {' '}paid models were listed but not probed by this quick scan.
                        </span>
                        {discoveryProgress.finished && !isDiscovering && (
                          <button
                            onClick={() => confirmFullDiscovery(discoveryProgress.total + discoveryProgress.skippedByScope)}
                            className="font-black text-indigo-600 dark:text-indigo-400 hover:underline"
                          >
                            Search all {discoveryProgress.total + discoveryProgress.skippedByScope} instead →
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* Providers whose /models listing itself failed - previously swallowed silently */}
                {discoveryCatalogueErrors.length > 0 && (
                  <div className="p-3 rounded-2xl border border-amber-300 dark:border-amber-800 bg-amber-50/70 dark:bg-amber-950/30 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-[11px] font-black text-amber-800 dark:text-amber-300">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      <span>{discoveryCatalogueErrors.length} provider catalogue(s) could not be listed</span>
                    </div>
                    {discoveryCatalogueErrors.map((entry) => (
                      <p key={entry.provider_id} className="text-[10px] font-mono text-amber-700 dark:text-amber-400">
                        {entry.provider_name}: {entry.error}
                        {entry.curated_count > 0 && ` (fell back to ${entry.curated_count} curated model(s))`}
                      </p>
                    ))}
                  </div>
                )}

                {/* 1-Click Admin Favorites Button Banner */}
                <div className="p-3.5 rounded-2xl bg-gradient-to-r from-purple-500/10 via-amber-500/10 to-indigo-500/10 border-2 border-purple-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-sm">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-1.5 font-black text-xs text-purple-900 dark:text-purple-300">
                      <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
                      <span>Admin's Favorites ({availableDiscovered.filter((x) => x.is_admin_favorite).length} Available)</span>
                    </div>
                    <p className="text-[11px] text-slate-600 dark:text-slate-400">
                      Instantly select our curated top-tier debate fleet across verified keys.
                    </p>
                  </div>

                  <button
                    onClick={handleSelectAdminFavorites}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-black shadow-md transition shrink-0"
                  >
                    <CheckCircle className="w-3.5 h-3.5" /> Select Admin's Favorites
                  </button>
                </div>

                {/* Search + provider filter over the full catalogue */}
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
                    <input
                      type="text"
                      value={discoverySearch}
                      onChange={(e) => setDiscoverySearch(e.target.value)}
                      placeholder="Search models by name, id or provider (e.g. gemini flash)"
                      className="w-full pl-9 pr-8 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
                    />
                    {discoverySearch && (
                      <button
                        onClick={() => setDiscoverySearch('')}
                        aria-label="Clear model search"
                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>

                  <select
                    value={discoveryProvider}
                    onChange={(e) => setDiscoveryProvider(e.target.value)}
                    className="px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-bold text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
                  >
                    <option value="all">All providers</option>
                    {discoveryProviderOptions.map((option) => (
                      <option key={option.id} value={option.id}>{option.name}</option>
                    ))}
                  </select>

                  <button
                    onClick={() => setDiscoveryFreeOnly(!discoveryFreeOnly)}
                    className={`px-3 py-2 rounded-xl border text-xs font-bold transition shrink-0 ${
                      discoveryFreeOnly
                        ? 'bg-emerald-600 border-emerald-600 text-white'
                        : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300'
                    }`}
                  >
                    Free tier only
                  </button>
                </div>

                {/* Tier chips. Every probed model carries a family-based pre-classification, so
                    the list can be narrowed to "just the frontier models" without reading 90 ids. */}
                <div className="flex flex-wrap items-center gap-1.5">
                  <button
                    onClick={() => setDiscoveryTier('all')}
                    className={`px-2.5 py-1 rounded-lg border text-[11px] font-bold transition ${
                      discoveryTier === 'all'
                        ? 'bg-indigo-600 border-indigo-600 text-white'
                        : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300'
                    }`}
                  >
                    All tiers ({availableDiscovered.length})
                  </button>
                  {(['top', 'mid', 'low'] as const).map((tier) => (
                    <button
                      key={tier}
                      onClick={() => setDiscoveryTier(discoveryTier === tier ? 'all' : tier)}
                      title={DISCOVERY_TIER_META[tier].blurb}
                      className={`px-2.5 py-1 rounded-lg border text-[11px] font-bold transition ${
                        discoveryTier === tier
                          ? DISCOVERY_TIER_META[tier].chip
                          : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300'
                      }`}
                    >
                      {DISCOVERY_TIER_META[tier].label} ({discoveryTierCounts[tier]})
                    </button>
                  ))}
                  {discoveryTierCounts.top > 0 && (
                    <button
                      onClick={() => {
                        discoveryTouchedRef.current = true;
                        const sel: Record<string, boolean> = {};
                        availableDiscovered
                          .filter((item) => discoveryTierOf(item) === 'top')
                          .forEach((item) => { sel[item.model.id] = true; });
                        setSelectedDiscovered(sel);
                      }}
                      className="ml-auto px-2.5 py-1 rounded-lg bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800 text-[11px] font-black transition hover:bg-amber-200 dark:hover:bg-amber-900"
                    >
                      Select all {discoveryTierCounts.top} top-tier
                    </button>
                  )}
                </div>

                {/* Action Filters */}
                <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                  <span className="font-bold text-slate-700 dark:text-slate-300">
                    Online Models ({filteredAvailable.length}
                    {filteredAvailable.length !== availableDiscovered.length && ` of ${availableDiscovered.length}`}
                    {' '}· Strongest tier first, fastest within each):
                  </span>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        discoveryTouchedRef.current = true;
                        const sel: Record<string, boolean> = { ...selectedDiscovered };
                        filteredAvailable.forEach((item) => { sel[item.model.id] = true; });
                        setSelectedDiscovered(sel);
                      }}
                      className="text-indigo-600 dark:text-indigo-400 font-bold hover:underline"
                    >
                      {discoveryQuery || discoveryProvider !== 'all' || discoveryFreeOnly || discoveryTier !== 'all' ? 'Select Shown' : 'Select All'}
                    </button>
                    <span>·</span>
                    <button
                      onClick={() => {
                        discoveryTouchedRef.current = true;
                        const sel: Record<string, boolean> = {};
                        // Re-sorted by latency here on purpose: the list itself is ordered by tier
                        // first, so slicing it directly would have given the 5 fastest *top-tier*
                        // models under a label that promises the 5 fastest overall.
                        [...filteredAvailable]
                          .sort((a, b) => a.latency_ms - b.latency_ms)
                          .slice(0, 5)
                          .forEach((item) => { sel[item.model.id] = true; });
                        setSelectedDiscovered(sel);
                      }}
                      className="text-amber-600 dark:text-amber-400 font-bold hover:underline"
                    >
                      Top 5 Fastest
                    </button>
                    <span>·</span>
                    <button
                      onClick={() => {
                        discoveryTouchedRef.current = true;
                        setSelectedDiscovered({});
                      }}
                      className="text-slate-400 font-bold hover:underline"
                    >
                      Deselect
                    </button>
                  </div>
                </div>

                {/* Available Online Models List (Sorted by latency) */}
                <div className="max-h-72 overflow-y-auto space-y-2 border border-slate-200 dark:border-slate-800 rounded-2xl p-2 bg-slate-50/50 dark:bg-slate-800/40">
                  {filteredAvailable.length === 0 && (
                    <p className="p-4 text-center text-[11px] text-slate-500 dark:text-slate-400">
                      {availableDiscovered.length === 0
                        ? (isDiscovering ? 'Probing models... verified endpoints will appear here as they respond.' : 'No models came back online for these keys.')
                        : 'No online model matches this search.'}
                    </p>
                  )}
                  {filteredAvailable.map((item, idx) => {
                    const m = item.model;
                    const isChecked = !!selectedDiscovered[m.id];
                    const tier = discoveryTierOf(item);
                    // The list is tier-ordered, so a header appears whenever the tier changes. It
                    // carries the blurb too: "Top tier" alone does not tell anyone what to do with
                    // the 25 mid-tier rows underneath it.
                    const startsTierGroup = idx === 0 || discoveryTierOf(filteredAvailable[idx - 1]) !== tier;
                    return (
                      <React.Fragment key={m.id || idx}>
                        {startsTierGroup && (
                          <div className="flex items-baseline gap-2 px-1 pt-1.5 pb-0.5">
                            <span className={`px-1.5 py-0.5 rounded text-[9px] font-black uppercase border ${DISCOVERY_TIER_META[tier].badge}`}>
                              {DISCOVERY_TIER_META[tier].label}
                            </span>
                            <span className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
                              {DISCOVERY_TIER_META[tier].blurb}
                            </span>
                          </div>
                        )}
                      <div
                        onClick={() => {
                          discoveryTouchedRef.current = true;
                          setSelectedDiscovered({ ...selectedDiscovered, [m.id]: !isChecked });
                        }}
                        className={`p-3 rounded-xl border flex items-center justify-between gap-3 text-xs cursor-pointer transition ${
                          isChecked
                            ? 'bg-indigo-50 dark:bg-indigo-950/80 border-indigo-200 dark:border-indigo-800 ring-1 ring-indigo-500/20'
                            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800'
                        }`}
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => {}}
                            className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4 cursor-pointer shrink-0"
                          />
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="font-extrabold text-slate-900 dark:text-white truncate">{m.name}</span>
                              <span className={`px-1.5 py-0.2 rounded text-[9px] font-black uppercase border shrink-0 ${DISCOVERY_TIER_META[tier].badge}`}>
                                {DISCOVERY_TIER_META[tier].label}
                              </span>
                              {item.is_admin_favorite && (
                                <span className="px-1.5 py-0.2 rounded text-[9px] font-black uppercase bg-purple-100 dark:bg-purple-950 text-purple-800 dark:text-purple-300 border border-purple-200 dark:border-purple-800 flex items-center gap-0.5 shrink-0">
                                  <Star className="w-2.5 h-2.5 fill-current" /> Admin Pick
                                </span>
                              )}
                              {item.is_free && (
                                <span className="px-1.5 py-0.2 rounded text-[9px] font-black uppercase bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 shrink-0">
                                  Free
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-2 text-[10px] text-slate-500 dark:text-slate-400 font-mono truncate">
                              <span className="truncate">{item.provider_name} · {m.model_id}</span>
                            </div>
                          </div>
                        </div>

                        <div className="shrink-0">
                          <span className="px-2.5 py-1 rounded-lg text-[10px] font-black uppercase bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 tabular-nums">
                            🟢 {Math.round(item.latency_ms)}ms
                          </span>
                        </div>
                      </div>
                      </React.Fragment>
                    );
                  })}
                </div>

                {/* Collapsed Accordion for Unavailable Models */}
                {unavailableDiscovered.length > 0 && (
                  <div className="border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden">
                    <button
                      onClick={() => setShowUnavailableAccordion(!showUnavailableAccordion)}
                      className="w-full p-3 bg-slate-100/70 dark:bg-slate-800/40 text-left text-xs font-bold text-slate-600 dark:text-slate-400 flex items-center justify-between transition"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-rose-500">🔴</span>
                        <span>
                          Unavailable / Failed Models ({filteredUnavailable.length}
                          {filteredUnavailable.length !== unavailableDiscovered.length && ` of ${unavailableDiscovered.length}`})
                        </span>
                      </div>
                      {showUnavailableAccordion ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    </button>

                    {showUnavailableAccordion && (
                      <div className="p-3 bg-white dark:bg-slate-900 space-y-2 max-h-48 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800">
                        {filteredUnavailable.length === 0 && (
                          <p className="text-[11px] text-slate-500 dark:text-slate-400">No failed model matches this search.</p>
                        )}
                        {filteredUnavailable.map((item, idx) => (
                          <div key={item.model?.id || idx} className="pt-2 text-xs flex items-start justify-between gap-3 opacity-80">
                            <div className="min-w-0">
                              <div className="flex items-center gap-1.5 min-w-0">
                                <span className="font-bold text-slate-800 dark:text-slate-200 truncate">{item.model.name}</span>
                                <span className={`px-1.5 py-0.5 rounded text-[9px] font-black uppercase border shrink-0 ${DISCOVERY_TIER_META[discoveryTierOf(item)].badge}`}>
                                  {DISCOVERY_TIER_META[discoveryTierOf(item)].label}
                                </span>
                              </div>
                              <p className="text-[10px] text-slate-400 font-mono truncate">{item.model.model_id}</p>
                              <p className="text-[10px] text-rose-500 font-mono">{item.message}</p>
                            </div>
                            <div className="flex flex-col items-end gap-1 shrink-0">
                              <span className="px-1.5 py-0.5 rounded text-[9px] font-black uppercase bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
                                {DISCOVERY_REASON_LABELS[item.reason] || 'Failed'}
                              </span>
                              <span className="text-[10px] font-bold text-slate-400">{item.provider_name}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Bottom Action Footer */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
                  <button
                    onClick={() => {
                      discoveryAbortRef.current = true;
                      setWizardFlowState('cards');
                    }}
                    className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold transition"
                  >
                    Edit Keys
                  </button>

                  <button
                    onClick={handleApplyToSession}
                    className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-black shadow-md transition"
                  >
                    <Check className="w-4 h-4" /> Use Selected ({Object.values(selectedDiscovered).filter(Boolean).length}) for This Session
                  </button>
                </div>
              </div>
            )}

            {/* STAGE D: CUSTOM ENDPOINT FORM */}
            {wizardFlowState === 'custom' && (
              <div className="space-y-4">
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-300">Model Name:</label>
                  <input
                    type="text"
                    value={customForm.name}
                    onChange={(e) => setCustomForm({ ...customForm, name: e.target.value })}
                    placeholder="e.g. Local Llama 3 70B"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-300">Base URL (OpenAI-Compatible):</label>
                  <input
                    type="text"
                    value={customForm.base_url}
                    onChange={(e) => setCustomForm({ ...customForm, base_url: e.target.value })}
                    placeholder="http://localhost:11434/v1"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-300">Model ID:</label>
                  <input
                    type="text"
                    value={customForm.model_id}
                    onChange={(e) => setCustomForm({ ...customForm, model_id: e.target.value })}
                    placeholder="llama3:latest"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-300">API Key (Optional for local):</label>
                  <input
                    type="password"
                    value={customForm.api_key}
                    onChange={(e) => setCustomForm({ ...customForm, api_key: e.target.value })}
                    placeholder="sk-... (or leave empty)"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-mono focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
                  <button
                    onClick={() => setWizardFlowState('initial_choice')}
                    className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold transition"
                  >
                    Back
                  </button>

                  <button
                    onClick={handleAddCustomModel}
                    className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-black shadow-md transition"
                  >
                    ➕ Add Custom Model to Fleet
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* START NEW DEBATE MODAL */}
      {isStartModalOpen && (
        <div className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="modal-panel max-h-[90vh] w-full max-w-2xl space-y-5 overflow-y-auto p-6 lg:p-8" role="dialog" aria-modal="true" aria-labelledby="start-dialog-title" tabIndex={-1}>
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <h3 id="start-dialog-title" className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-600" /> Launch Multi-AI Deliberation Gauntlet
              </h3>
              <button
                onClick={() => setIsStartModalOpen(false)}
                className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500"
                aria-label="Close new deliberation dialog"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* SIH PROBLEM STATEMENT SELECTOR / SEARCH */}
            <div className="space-y-3 p-4 rounded-2xl bg-indigo-50/40 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded-md bg-indigo-600 text-white text-[11px] font-black uppercase tracking-wider flex items-center gap-1">
                    <Database className="w-3.5 h-3.5" /> SIH Database
                  </span>
                  <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                    {psList.length > 0 ? `${psList.length} Official Statements Available` : 'Loading statements...'}
                  </span>
                </div>

                {selectedPsObj && (
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedPsObj(null);
                      setProblemStatement('');
                      setPsCode('');
                      setMinistryDomain('Smart India Hackathon (General)');
                    }}
                    className="text-xs font-bold text-rose-500 hover:text-rose-600 flex items-center gap-1 transition"
                  >
                    <X className="w-3.5 h-3.5" /> Clear Selected
                  </button>
                )}
              </div>

              {/* SEARCH & CATEGORY FILTER */}
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <div className="flex items-center gap-1.5">
                    {(['All', 'Software', 'Hardware'] as const).map((cat) => (
                      <button
                        key={cat}
                        type="button"
                        onClick={() => setPsCategoryFilter(cat)}
                        className={`px-3 py-1 rounded-xl text-xs font-black transition ${
                          psCategoryFilter === cat
                            ? 'bg-indigo-600 text-white shadow-xs'
                            : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800'
                        }`}
                      >
                        {cat}
                      </button>
                    ))}
                  </div>

                  <span className="text-[11px] text-slate-400 font-medium">
                    Showing {filteredPs.length} matches (Click any to select)
                  </span>
                </div>

                <div className="relative">
                  <input
                    type="text"
                    value={psFilter}
                    onChange={(e) => setPsFilter(e.target.value)}
                    placeholder="Search 226 statements by code (26001), keyword (landslide, AI, drone), ministry..."
                    className="w-full px-3.5 py-2.5 rounded-xl border border-indigo-200 dark:border-indigo-800 bg-white dark:bg-slate-900 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none pr-8 shadow-xs"
                  />
                  {psFilter && (
                    <button
                      type="button"
                      onClick={() => setPsFilter('')}
                      className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* INTERACTIVE PS LIST */}
              <div className="max-h-60 overflow-y-auto border border-slate-200 dark:border-slate-800 rounded-xl divide-y divide-slate-100 dark:divide-slate-800 bg-white dark:bg-slate-900 shadow-xs">
                {filteredPs.length > 0 ? (
                  filteredPs.map((ps, idx) => {
                    const isSelected = selectedPsObj && (selectedPsObj.ps_code === ps.ps_code || selectedPsObj.ps_id === ps.ps_id);
                    return (
                      <div
                        key={idx}
                        onClick={() => {
                          setSelectedPsObj(ps);
                          setPsCode(ps.ps_code || ps.ps_id || '');
                          setMinistryDomain(ps.organization || ps.department || ps.theme || 'Smart India Hackathon');
                          const formatted = `[${ps.ps_code || ps.ps_id}] ${ps.title}\n\nOrganization: ${ps.organization}\nTheme: ${ps.theme} | Category: ${ps.category}\n\nProblem Description:\n${ps.description}\n\nExpected Solution Deliverables:\n${ps.expected_solution || ''}`;
                          setProblemStatement(formatted);
                        }}
                        className={`p-3 text-left text-xs cursor-pointer transition flex flex-col gap-1.5 ${
                          isSelected
                            ? 'bg-indigo-50 dark:bg-indigo-950/80 border-l-4 border-indigo-600'
                            : 'hover:bg-slate-50 dark:hover:bg-slate-800/60'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-black ${
                              isSelected ? 'bg-indigo-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-indigo-700 dark:text-indigo-400 border border-slate-200 dark:border-slate-700'
                            }`}>
                              {ps.ps_code || ps.ps_id}
                            </span>
                            <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400">
                              {ps.category} · {ps.theme}
                            </span>
                            <span className="text-[10px] text-slate-400 truncate max-w-xs">
                              · 🏢 {ps.organization}
                            </span>
                          </div>

                          <div className="flex items-center gap-1 shrink-0">
                            {isSelected ? (
                              <span className="px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 text-[10px] font-black flex items-center gap-1">
                                <CheckCircle className="w-3 h-3 text-emerald-600" /> SELECTED
                              </span>
                            ) : (
                              <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 opacity-80 hover:opacity-100">
                                Click to Select ➔
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="font-extrabold text-slate-900 dark:text-white leading-snug">
                          {ps.title}
                        </div>

                        <div className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
                          {ps.description}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="p-6 text-center text-xs text-slate-400 space-y-1">
                    <p>No SIH problem statements found matching "{psFilter}".</p>
                    <p className="text-[11px]">Try searching with a shorter keyword or switch category to 'All'.</p>
                  </div>
                )}
              </div>

              {/* ACTIVE SELECTION SUMMARY BANNER */}
              {selectedPsObj && (
                <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span className="text-xs font-extrabold text-emerald-950 dark:text-emerald-200 truncate">
                      Selected: [{selectedPsObj.ps_code || selectedPsObj.ps_id}] {selectedPsObj.title}
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-emerald-200 dark:bg-emerald-900 text-emerald-900 dark:text-emerald-200 text-[10px] font-black shrink-0">
                    READY TO LAUNCH
                  </span>
                </div>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300">Problem Statement:</label>
              <textarea
                rows={4}
                value={problemStatement}
                onChange={(e) => setProblemStatement(e.target.value)}
                placeholder="Enter complete SIH problem statement and operational requirements..."
                className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-bold text-slate-700 dark:text-slate-300">Additional Constraints & Focus (Optional):</label>
              <input
                type="text"
                value={additionalPrompt}
                onChange={(e) => setAdditionalPrompt(e.target.value)}
                placeholder="e.g. Must run on sub-₹1500 BOM, LiFePO4 batteries, and NavIC positioning..."
                className="w-full px-3.5 py-2 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Participating Fleet Models (Per-Session):</span>
                <span className="text-xs text-indigo-700 dark:text-indigo-400 font-bold">{models.filter((m) => sessionSelectedModels[m.id] ?? m.enabled).length} of {models.length} Selected</span>
              </div>
              <div className="flex items-center gap-1.5 flex-wrap max-h-24 overflow-y-auto">
                {models.map((m) => {
                  const isChecked = sessionSelectedModels[m.id] ?? m.enabled;
                  return (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => {
                        setSessionSelectedModels({
                          ...sessionSelectedModels,
                          [m.id]: !isChecked
                        });
                      }}
                      className={`px-2 py-0.5 rounded-lg text-[10px] font-bold border transition ${
                        isChecked ? 'bg-indigo-50 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800' : 'bg-slate-100 dark:bg-slate-800 text-slate-400 border-slate-200 dark:border-slate-700 line-through'
                      }`}
                    >
                      {m.name}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Auto-Advance Across 4 Phases:</span>
              <input
                type="checkbox"
                checked={autoAdvance}
                onChange={(e) => setAutoAdvance(e.target.checked)}
                className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4 cursor-pointer"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
              <button
                onClick={() => setIsStartModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-bold transition"
              >
                Cancel
              </button>
              <button
                onClick={handleStartDebate}
                disabled={isLaunching}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-500/20 transition"
              >
                {isLaunching ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                Launch Deliberation
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODERATOR DIRECTIVE INJECTION MODAL */}
      {isInjectModalOpen && (
        <div className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="modal-panel w-full max-w-lg space-y-4 p-6" role="dialog" aria-modal="true" aria-labelledby="inject-dialog-title" aria-describedby="inject-dialog-description" tabIndex={-1}>
            <h3 id="inject-dialog-title" className="text-sm font-black text-slate-900 dark:text-white flex items-center gap-2">
              <MessageSquarePlus className="w-4 h-4 text-indigo-600" /> Inject Moderator Directive
            </h3>
            <p id="inject-dialog-description" className="text-xs text-slate-500 dark:text-slate-400">
              This constraint will be injected into all debater models in the next sub-round.
            </p>
            <textarea
              rows={4}
              value={injectionText}
              onChange={(e) => setInjectionText(e.target.value)}
              placeholder="e.g. All models must recalculate battery life assuming 10 days of continuous monsoon rain..."
              className="w-full p-3 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setIsInjectModalOpen(false)}
                className="px-3.5 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold"
              >
                Cancel
              </button>
              <button
                onClick={handleInjectDirective}
                className="px-4 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-bold shadow-sm"
              >
                Inject Directive
              </button>
            </div>
          </div>
        </div>
      )}

      {/* FULL-SCREEN DELIBERATION SCRATCHPAD DRAWER */}
      {selectedScratchpadModel && (
        <div className="modal-backdrop fixed inset-0 z-50 flex justify-end">
          <div className="h-full w-full max-w-2xl space-y-6 overflow-y-auto bg-[var(--surface)] p-6 shadow-2xl lg:p-8" role="dialog" aria-modal="true" aria-labelledby="response-inspector-title" tabIndex={-1}>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
                <div>
                  <h3 id="response-inspector-title" className="text-base font-black text-slate-900 dark:text-white flex items-center gap-2">
                    <Bot className="w-5 h-5 text-indigo-600" /> {selectedScratchpadModel.model_name}
                  </h3>
                  <span className="text-xs text-slate-400">{selectedScratchpadModel.pass_or_round_title || `Round ${selectedScratchpadModel.round_number}`}</span>
                </div>

                <button
                  onClick={() => setSelectedScratchpadModel(null)}
                  className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500"
                  aria-label="Close response inspector"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {selectedScratchpadModel.structured.deliberation_scratchpad && (
                <div className="p-4 rounded-2xl bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900 space-y-2">
                  <h4 className="text-xs font-black uppercase tracking-wider text-indigo-900 dark:text-indigo-300 flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-indigo-600" /> &lt;deliberation_scratchpad&gt; Internal Reasoning:
                  </h4>
                  <p className="text-xs text-indigo-950 dark:text-indigo-200 font-mono whitespace-pre-wrap leading-relaxed">
                    {selectedScratchpadModel.structured.deliberation_scratchpad}
                  </p>
                </div>
              )}

              <div className="space-y-2">
                <h4 className="text-xs font-black uppercase tracking-wider text-slate-900 dark:text-white">
                  Refined Deliverable:
                </h4>
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-wrap">
                  {selectedScratchpadModel.structured.refined_solution || selectedScratchpadModel.raw_text}
                </div>
              </div>

              <div className="space-y-3 pt-2">
                <h4 className="text-xs font-black uppercase tracking-wider text-slate-900 dark:text-white">4-Persona Analysis:</h4>
                
                {selectedScratchpadModel.structured.architect_lens && (
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                    <strong className="text-indigo-900 dark:text-indigo-300">🏛️ Lead Architect Lens:</strong>
                    <p className="text-slate-700 dark:text-slate-300">{selectedScratchpadModel.structured.architect_lens}</p>
                  </div>
                )}

                {(selectedScratchpadModel.structured.critic_lens || selectedScratchpadModel.structured.critic_devil_advocate_lens) && (
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                    <strong className="text-rose-900 dark:text-rose-300">😈 Murphy's Law Critic Lens:</strong>
                    <p className="text-slate-700 dark:text-slate-300">{selectedScratchpadModel.structured.critic_lens || selectedScratchpadModel.structured.critic_devil_advocate_lens}</p>
                  </div>
                )}

                {(selectedScratchpadModel.structured.field_hardware_lens || selectedScratchpadModel.structured.pragmatist_feasibility_lens) && (
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                    <strong className="text-amber-900 dark:text-amber-300">⚙️ Frugal Field & BOM Lens:</strong>
                    <p className="text-slate-700 dark:text-slate-300">{selectedScratchpadModel.structured.field_hardware_lens || selectedScratchpadModel.structured.pragmatist_feasibility_lens}</p>
                  </div>
                )}

                {(selectedScratchpadModel.structured.security_compliance_lens || selectedScratchpadModel.structured.security_reliability_lens) && (
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                    <strong className="text-emerald-900 dark:text-emerald-300">🛡️ Fort Knox Security & Compliance Lens:</strong>
                    <p className="text-slate-700 dark:text-slate-300">{selectedScratchpadModel.structured.security_compliance_lens || selectedScratchpadModel.structured.security_reliability_lens}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="border-t border-slate-100 dark:border-slate-800 pt-4 flex justify-end">
              <button
                onClick={() => setSelectedScratchpadModel(null)}
                className="px-5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold transition"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}

      {/* SESSION HISTORY / SAVED WORKSPACES MODAL */}
      {isHistoryModalOpen && (
        <div className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="modal-panel flex max-h-[85vh] w-full max-w-2xl flex-col justify-between space-y-5 p-6 lg:p-8" role="dialog" aria-modal="true" aria-labelledby="history-dialog-title" tabIndex={-1}>
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400">
                  <History className="w-5 h-5" />
                </div>
                <div>
                  <h3 id="history-dialog-title" className="text-base font-black text-slate-900 dark:text-white">
                    Saved Debate Sessions & History
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Switch between active live sessions or resume previous debate workspaces from disk.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleOpenHistory}
                  className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-600 dark:text-slate-400 text-xs font-bold transition"
                  title="Refresh List"
                >
                  <RefreshCw className={`w-4 h-4 ${isLoadingHistory ? 'animate-spin' : ''}`} />
                </button>
                <button
                  type="button"
                  onClick={() => setIsHistoryModalOpen(false)}
                  className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500"
                  aria-label="Close session history"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Search & Filter Bar */}
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <input
                type="text"
                value={historySearchFilter}
                onChange={(e) => setHistorySearchFilter(e.target.value)}
                placeholder="Search history by title, problem code, or folder..."
                className="flex-1 px-3.5 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />

              <div className="flex items-center gap-1">
                {(['All', 'live', 'completed', 'paused'] as const).map((st) => (
                  <button
                    key={st}
                    type="button"
                    onClick={() => setHistoryStatusFilter(st)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                      historyStatusFilter === st
                        ? 'bg-indigo-600 text-white shadow-xs'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
                    }`}
                  >
                    {st === 'All' ? 'All' : st.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {/* List Container */}
            <div className="flex-1 overflow-y-auto space-y-3 pr-1 max-h-96">
              {isLoadingHistory ? (
                <div className="py-12 text-center text-xs text-slate-400 flex flex-col items-center gap-2">
                  <RefreshCw className="w-5 h-5 animate-spin text-indigo-600" />
                  <span>Scanning saved workspaces on disk...</span>
                </div>
              ) : savedWorkspaces.filter((w) => {
                const searchMatch = !historySearchFilter || `${w.session_title || ''} ${w.ps_code || ''} ${w.folder || ''}`.toLowerCase().includes(historySearchFilter.toLowerCase());
                const statusMatch = historyStatusFilter === 'All' || (w.status || 'saved').toLowerCase().includes(historyStatusFilter.toLowerCase());
                return searchMatch && statusMatch;
              }).length === 0 ? (
                <div className="py-12 text-center text-xs text-slate-400 space-y-2">
                  <FolderOpen className="w-8 h-8 mx-auto text-slate-300 dark:text-slate-700" />
                  <p>No matching debate workspaces found.</p>
                </div>
              ) : (
                savedWorkspaces
                  .filter((w) => {
                    const searchMatch = !historySearchFilter || `${w.session_title || ''} ${w.ps_code || ''} ${w.folder || ''}`.toLowerCase().includes(historySearchFilter.toLowerCase());
                    const statusMatch = historyStatusFilter === 'All' || (w.status || 'saved').toLowerCase().includes(historyStatusFilter.toLowerCase());
                    return searchMatch && statusMatch;
                  })
                  .map((w, idx) => {
                    const isCurrent = w.session_id === sessionId;
                    const isLive = w.status === 'running' || w.status === 'live';
                    const isCompleted = w.status === 'completed';
                    return (
                      <div
                        key={idx}
                        className={`p-4 rounded-2xl border transition flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                          isCurrent
                            ? 'bg-indigo-50/80 dark:bg-indigo-950/50 border-indigo-300 dark:border-indigo-800 ring-2 ring-indigo-500/20'
                            : 'bg-slate-50/80 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800 hover:bg-white dark:hover:bg-slate-800/80'
                        }`}
                      >
                        <div className="space-y-1 min-w-0 flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <h4 className="font-extrabold text-xs text-slate-900 dark:text-white truncate max-w-sm">
                              {w.session_title || w.folder || 'Debate Session'}
                            </h4>
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider ${
                              isLive
                                ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 animate-pulse'
                                : isCompleted
                                ? 'bg-purple-100 dark:bg-purple-950 text-purple-800 dark:text-purple-300'
                                : 'bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300'
                            }`}>
                              {w.status || 'saved'}
                            </span>
                            {w.consensus_score != null && w.consensus_score > 0 ? (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300">
                                {w.consensus_score}% Consensus
                              </span>
                            ) : null}

                            {isCurrent && (
                              <span className="px-1.5 py-0.2 rounded text-[9px] font-black bg-indigo-600 text-white">
                                Active
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-3 text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                            <span>Rounds: <b>{w.rounds_count || 0}</b></span>
                            <span>·</span>
                            <span className="truncate max-w-xs">{w.folder}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          {isCompleted ? (
                            <button
                              type="button"
                              onClick={() => {
                                handleLoadSavedSession(w.session_id, false);
                                setActiveTab('verdict');
                              }}
                              className="px-3.5 py-2 rounded-xl text-xs font-black bg-purple-50 dark:bg-purple-950/80 hover:bg-purple-100 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800 transition flex items-center gap-1.5 shadow-xs"
                              title="View Master Verdict Deliverable"
                            >
                              <Award className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
                              <span>View Verdict</span>
                            </button>
                          ) : (
                            <button
                              type="button"
                              onClick={() => handleLoadSavedSession(w.session_id, true)}
                              className="px-3.5 py-2 rounded-xl text-xs font-black bg-emerald-600 hover:bg-emerald-500 text-white shadow-xs transition flex items-center gap-1.5"
                              title="Resume debate from next pending pass on disk"
                            >
                              <Play className="w-3.5 h-3.5 fill-current" />
                              <span>{isCurrent ? 'Resume Active' : 'Resume & Continue'}</span>
                            </button>
                          )}

                          <button
                            type="button"
                            onClick={() => handleLoadSavedSession(w.session_id, false)}
                            className={`px-3 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
                              isCurrent
                                ? 'bg-indigo-600 text-white'
                                : 'bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
                            }`}
                            title="Inspect workspace in Arena View"
                          >
                            <FolderOpen className="w-3.5 h-3.5" />
                            <span>{isCurrent ? 'Viewing' : 'Inspect'}</span>
                          </button>

                          <button
                            type="button"
                            onClick={(e) => handleDeleteSession(w.session_id, w.folder, e)}
                            className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition"
                            title="Delete this workspace from disk"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    );
                  })
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <button
                type="button"
                onClick={() => {
                  setIsHistoryModalOpen(false);
                  setIsStartModalOpen(true);
                }}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-black transition shadow-xs flex items-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5" /> Start New Deliberation
              </button>

              <button
                type="button"
                onClick={() => setIsHistoryModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-bold transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 👑 MASTER ARBITER INTERACTIVE COMMAND CONSOLE */}
      {isArbiterCommandOpen && (
        <div className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="modal-panel flex max-h-[88vh] w-full max-w-2xl flex-col justify-between space-y-4 p-6 lg:p-8" role="dialog" aria-modal="true" aria-labelledby="arbiter-dialog-title" tabIndex={-1}>
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300">
                  <Award className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h3 id="arbiter-dialog-title" className="text-base font-black text-slate-900 dark:text-white flex items-center gap-2">
                    Command Master Arbiter (GPT 5.6 Sol)
                    <span className="px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 text-[10px] font-black">
                      ACTIVE SUPERVISOR
                    </span>
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Supreme Fleet Controller: Supervises all 21 models, auto-heals formats, and enforces consensus progression.
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setIsArbiterCommandOpen(false)}
                className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500"
                aria-label="Close arbiter console"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* QUICK ACTION DIRECTIVE PILLS */}
            <div className="space-y-1.5">
              <span className="text-[11px] font-black uppercase tracking-wider text-slate-400">
                1-Click Arbiter Commands:
              </span>
              <div className="flex items-center gap-1.5 flex-wrap">
                <button
                  type="button"
                  onClick={() => handleSendArbiterCommand('Abort all lagging and stuck models and advance to verdict synthesis now')}
                  className="px-3 py-1.5 rounded-xl bg-rose-50 dark:bg-rose-950/60 hover:bg-rose-100 text-rose-700 dark:text-rose-300 text-xs font-bold border border-rose-200 dark:border-rose-800 transition flex items-center gap-1"
                >
                  <Zap className="w-3.5 h-3.5" /> ⚡ Abort Stuck Models & Advance
                </button>

                <button
                  type="button"
                  onClick={() => handleSendArbiterCommand('Auto-heal and convert all unformatted debater responses in this round into standard JSON schema')}
                  className="px-3 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 text-indigo-700 dark:text-indigo-300 text-xs font-bold border border-indigo-200 dark:border-indigo-800 transition flex items-center gap-1"
                >
                  <Sparkles className="w-3.5 h-3.5" /> 🔄 Auto-Heal Formats
                </button>

                <button
                  type="button"
                  onClick={() => handleSendArbiterCommand('Synthesize the final sovereign consensus verdict immediately with the completed fleet')}
                  className="px-3 py-1.5 rounded-xl bg-purple-50 dark:bg-purple-950/60 hover:bg-purple-100 text-purple-700 dark:text-purple-300 text-xs font-bold border border-purple-200 dark:border-purple-800 transition flex items-center gap-1"
                >
                  <Award className="w-3.5 h-3.5" /> 🏆 Force Final Verdict Now
                </button>

                <button
                  type="button"
                  onClick={() => handleSendArbiterCommand('Re-enable and unquarantine all fleet models for the next round')}
                  className="px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 text-emerald-700 dark:text-emerald-300 text-xs font-bold border border-emerald-200 dark:border-emerald-800 transition flex items-center gap-1"
                >
                  <RefreshCw className="w-3.5 h-3.5" /> 🛠️ Re-enable All Models
                </button>
              </div>
            </div>

            {/* LIVE ARBITER DIALOGUE / LOGS */}
            <div className="flex-1 overflow-y-auto space-y-3 p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 max-h-64 font-mono text-xs">
              {arbiterActionLogs.map((log, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-xl space-y-1 ${
                    log.sender.includes('You')
                      ? 'bg-indigo-100/70 dark:bg-indigo-950/80 border border-indigo-200 dark:border-indigo-800 text-indigo-950 dark:text-indigo-200 ml-6'
                      : 'bg-white dark:bg-slate-900 border border-purple-200 dark:border-purple-900/60 text-slate-800 dark:text-slate-200 mr-6 shadow-xs'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] font-bold text-slate-400">
                    <span className={log.sender.includes('You') ? 'text-indigo-600 dark:text-indigo-400' : 'text-purple-600 dark:text-purple-400'}>
                      {log.sender}
                    </span>
                    <span>{log.time}</span>
                  </div>
                  <div className="whitespace-pre-wrap leading-relaxed">
                    {log.text}
                  </div>
                </div>
              ))}
              {isSendingArbiterCmd && (
                <div className="p-3 rounded-xl bg-purple-50 dark:bg-purple-950/60 border border-purple-200 dark:border-purple-800 text-purple-900 dark:text-purple-300 flex items-center gap-2">
                  <RefreshCw className="w-4 h-4 animate-spin text-purple-600" />
                  <span>Master Arbiter GPT 5.6 Sol is executing your directive...</span>
                </div>
              )}
            </div>

            {/* NATURAL LANGUAGE COMMAND INPUT */}
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={arbiterCommandText}
                onChange={(e) => setArbiterCommandText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendArbiterCommand();
                  }
                }}
                placeholder="Command Arbiter in plain English (e.g. 'Abort GLM 5.2 and retry Nemotron on backup key for lower latency')..."
                className="flex-1 px-4 py-3 rounded-xl border border-purple-300 dark:border-purple-800 bg-white dark:bg-slate-900 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:outline-none shadow-xs"
              />

              <button
                type="button"
                onClick={() => handleSendArbiterCommand()}
                disabled={isSendingArbiterCmd || !arbiterCommandText.trim()}
                className="px-5 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-xs font-black transition shadow-xs flex items-center gap-1.5 shrink-0"
              >
                {isSendingArbiterCmd ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                <span>Send Command</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
