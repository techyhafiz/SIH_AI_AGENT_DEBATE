'use client';

import React, { useState, useEffect, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  ModelConfig,
  DebateSession,
  RoundData,
  DebaterResponse,
  ResearchDossierItem
} from '@/types/debate';
import { useDebateStream } from '@/hooks/useDebateStream';
import DEFAULT_PS_DATA from '@/data/extracted_problem_statements.json';
import {
  Bot,
  Layers,
  Sparkles,
  Play,
  Pause,
  SkipForward,
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
  FileCode,
  Shield,
  Cpu,
  Eye,
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
  Sliders,
  CheckSquare,
  Square,
  Activity,
  Globe,
  Sun,
  Moon,
  Radio,
  HelpCircle,
  Server,
  Database,
  ArrowRight,
  ArrowLeft,
  History,
  Power,
  PowerOff,
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
  { id: 'm1', name: 'Claude Opus 4.8', base_url: 'https://agentrouter.org/v1', api_key: '', backup_api_keys: [''], model_id: 'claude-opus-4-8', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm2', name: 'Claude Opus 5.0', base_url: 'https://agentrouter.org/v1', api_key: '', backup_api_keys: [''], model_id: 'claude-opus-5', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.6 },
  { id: 'm3', name: 'GPT 5.6 Sol', base_url: 'https://agentrouter.org/v1', api_key: 'sk-6FoEw2n9eRBjlyttLte6FOyhaeG1DNlmEnba1vcZhEHUuD77', backup_api_keys: [''], model_id: 'gpt-5.6-sol', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: true, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm4', name: 'Gemini 3.5 Flash Lite', base_url: 'https://generativelanguage.googleapis.com/v1beta/openai', api_key: '', backup_api_keys: [], model_id: 'gemini-3.5-flash-lite', fallback_model_ids: ['gemini-flash-lite-latest'], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: true, enabled: true, temperature: 0.7 },
  { id: 'm5', name: 'Gemini Flash Quota Pool (3.7 / 3.6 / 3.5)', base_url: 'https://generativelanguage.googleapis.com/v1beta/openai', api_key: '', backup_api_keys: [], model_id: 'gemini-3.7-flash', fallback_model_ids: ['gemini-3.6-flash', 'gemini-3.5-flash'], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: true, enabled: true, temperature: 0.7 },
  { id: 'm6', name: 'GLM 5.2 (Free)', base_url: 'https://openrouter.ai/api/v1', api_key: '', backup_api_keys: [], model_id: 'z-ai/glm-5.2:free', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm7', name: 'NVIDIA Nemotron 3 Super 120B (Free)', base_url: 'https://openrouter.ai/api/v1', api_key: '', backup_api_keys: [], model_id: 'nvidia/nemotron-3-super-120b-a12b:free', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm8', name: 'Stealth Ox-Alpha', base_url: 'https://openrouter.ai/api/v1', api_key: '', backup_api_keys: [], model_id: 'stealth/ox-alpha', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm9', name: 'NVIDIA Nemotron 3.5 Lightning (Free)', base_url: 'https://openrouter.ai/api/v1', api_key: '', backup_api_keys: [], model_id: 'nvidia/nemotron-3.5-lightning:free', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm10', name: 'Qwen 3.8 Max (Free)', base_url: 'https://api.tokenrouter.com/v1', api_key: '', backup_api_keys: [''], model_id: 'qwen/qwen3.8-max-free', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm11', name: 'Claude Sonnet 5 (BluesMinds)', base_url: 'https://api.bluesminds.com/v1', api_key: '', backup_api_keys: [], model_id: 'unlimited/claude-sonnet-5', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm12', name: 'Mimo v2.5 (TokenFaucet)', base_url: 'https://freetokenfaucet.com/v1', api_key: '', backup_api_keys: [], model_id: 'mimo-v2.5', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm13', name: 'GPT 5.6 Terra (TokenFaucet)', base_url: 'https://freetokenfaucet.com/v1', api_key: '', backup_api_keys: [], model_id: 'gpt-5.6-terra', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm14', name: 'GPT 5.6 Luna (TokenFaucet)', base_url: 'https://freetokenfaucet.com/v1', api_key: '', backup_api_keys: [], model_id: 'gpt-5.6-luna', fallback_model_ids: [], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm15', name: 'DeepSeek V4 Pro (XKiro)', base_url: 'https://api.xkiro.com/v1', api_key: '', backup_api_keys: [], model_id: 'deepseek/deepseek-v4-pro', fallback_model_ids: ['deepseek/deepseek-v4-flash', 'deepseek/deepseek-chat-v3.1'], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm16', name: 'Qwen 3.8 Max (XKiro)', base_url: 'https://api.xkiro.com/v1', api_key: '', backup_api_keys: [], model_id: 'qwen/qwen3.8-max', fallback_model_ids: ['qwen/qwen3.7-max', 'qwen/qwen3.7-plus'], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm17', name: 'Mistral Large 2512 (XKiro)', base_url: 'https://api.xkiro.com/v1', api_key: '', backup_api_keys: [], model_id: 'mistralai/mistral-large-2512', fallback_model_ids: ['mistralai/mistral-medium-3.5', 'mistralai/codestral-2508'], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm18', name: 'Qwen 3.7 Max (XKiro)', base_url: 'https://api.xkiro.com/v1', api_key: '', backup_api_keys: [], model_id: 'qwen/qwen3.7-max', fallback_model_ids: ['qwen/qwen3.7-plus'], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm19', name: 'MiniMax M2.7 (XKiro)', base_url: 'https://api.xkiro.com/v1', api_key: '', backup_api_keys: [], model_id: 'minimax/minimax-m2.7', fallback_model_ids: ['minimax/minimax-m2.5-highspeed', 'minimax/minimax-m2.1-highspeed'], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm20', name: 'Gemini 3.5 Flash Free (TokenIn)', base_url: 'https://tokenin.my.id/v1', api_key: '', backup_api_keys: [], model_id: 'myt/gemini-3.5-flash-free', fallback_model_ids: ['myt/mimo-v2.5-free'], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 },
  { id: 'm21', name: 'Claude Opus 4.8 Free (TokenIn)', base_url: 'https://tokenin.my.id/v1', api_key: '', backup_api_keys: [], model_id: 'myt/claude-opus-4-8-free', fallback_model_ids: ['myt/gpt-5.6-sol-free', 'myt/gemini-3.5-flash-free'], provider_type: 'openai_compatible', timeout_seconds: 600, is_arbiter: false, is_backup_arbiter: false, enabled: true, temperature: 0.7 }
];

const WIZARD_PROVIDERS = [
  {
    id: 'google_gemini',
    name: 'Google AI Studio (Gemini)',
    tier: 'Free Tier Available · High Speed',
    icon: '🌟',
    direct_link: 'https://aistudio.google.com/app/apikey',
    desc: 'Official Google AI Studio API for Gemini 3.5 Flash Lite (Primary Arbiter) and Gemini 3.7 Flash Pool.',
    placeholder: ''
  },
  {
    id: 'openrouter',
    name: 'OpenRouter (Free & Paid Fleet)',
    tier: 'Free GLM, Nemotron & Llama Models',
    icon: '🌐',
    direct_link: 'https://openrouter.ai/keys',
    desc: 'Provides GLM 5.2 Free, NVIDIA Nemotron 3 Super 120B Free, and Stealth Ox-Alpha models.',
    placeholder: ''
  },
  {
    id: 'agentrouter',
    name: 'AgentRouter (Flagship Reasoning)',
    tier: 'Claude Opus 4.8/5.0 & GPT 5.6 Sol',
    icon: '⚡',
    direct_link: 'https://agentrouter.org',
    desc: 'High-reasoning frontier models for deep architectural critique and math synthesis.',
    placeholder: ''
  },
  {
    id: 'xkiro',
    name: 'XKiro Router (DeepSeek & Qwen)',
    tier: 'DeepSeek V4 Pro, Qwen 3.8 Max, Mistral',
    icon: '🚀',
    direct_link: 'https://api.xkiro.com',
    desc: 'High-speed cluster for DeepSeek V4 Pro, Qwen 3.8/3.7 Max, and Mistral Large 2512.',
    placeholder: ''
  },
  {
    id: 'tokenin',
    name: 'TokenIn Free Hub',
    tier: 'Free Community Pool',
    icon: '🎁',
    direct_link: 'https://tokenin.my.id',
    desc: 'Free endpoints for Gemini 3.5 Flash and Claude Opus 4.8 backups.',
    placeholder: ''
  },
  {
    id: 'tokenfaucet',
    name: 'FreeTokenFaucet Hub',
    tier: 'Mimo v2.5, GPT Terra & Luna',
    icon: '💧',
    direct_link: 'https://freetokenfaucet.com',
    desc: 'Fast pooled models for high-throughput multi-perspective cross-examination.',
    placeholder: ''
  },
  {
    id: 'bluesminds',
    name: 'BluesMinds AI',
    tier: 'Claude Sonnet 5',
    icon: '💎',
    direct_link: 'https://api.bluesminds.com',
    desc: 'Direct routing for Claude Sonnet 5 reasoning and synthesis.',
    placeholder: ''
  },
  {
    id: 'tokenrouter',
    name: 'TokenRouter Free',
    tier: 'Qwen 3.8 Max Free',
    icon: '🛡️',
    direct_link: 'https://api.tokenrouter.com',
    desc: 'Dedicated free Qwen 3.8 Max router for security and compliance analysis.',
    placeholder: ''
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

export default function HomePage() {
  // Theme State: 'light' | 'dark'
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  
  // Fleet & Session State
  const [models, setModels] = useState<ModelConfig[]>(DEFAULT_FLEET);
  const [sessionSelectedModels, setSessionSelectedModels] = useState<Record<string, boolean>>({});
  const [arbiterModelId, setArbiterModelId] = useState<string>('m4');
  const [backupArbiterModelId, setBackupArbiterModelId] = useState<string>('m5');
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
  const [isPsDropdownOpen, setIsPsDropdownOpen] = useState(false);
  const [isLaunching, setIsLaunching] = useState(false);
  const [copiedVerdict, setCopiedVerdict] = useState(false);

  // Research Config State
  const [researchConfig, setResearchConfig] = useState({
    enabled: true,
    tavily_api_key: '',
    openalex_email: 'campusprintexpress@gmail.com',
    download_pdfs: true
  });

  // STEP-BY-STEP CARD-BASED WIZARD STATE
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

  // SSE streaming hook
  const {
    session,
    currentStatus,
    activeTokens,
    timeoutAlert,
    setTimeoutAlert,
    isArbiterThinking,
    sendModeratorAction
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
  }, []);

  // Auto-track latest round index
  useEffect(() => {
    if (session && session.rounds && session.rounds.length > 0) {
      setSelectedRoundIndex(session.rounds.length - 1);
    }
  }, [session?.rounds?.length]);

  const currentRound: RoundData | undefined = session?.rounds?.[selectedRoundIndex];

  // Dynamic Live Status details
  const liveStatusText = useMemo(() => {
    if (!sessionId || !session) return 'Ready to launch new deliberation session.';
    if (currentStatus === 'paused') return `⏸️ Session Paused at ${currentRound?.pass_or_round_title || 'Current Round'}. Click Resume to continue.`;
    if (currentStatus === 'completed') return '🏆 Deliberation Complete! Sovereign SIH Master Verdict is synthesized.';
    if (isArbiterThinking) return '👑 Master Arbiter Jury in Session: Calculating multi-model consensus & verifying friction points...';
    
    if (currentRound) {
      const total = models.filter((m) => sessionSelectedModels[m.id] ?? m.enabled).length;
      const completed = Object.values(currentRound.responses || {}).filter((r) => r.status === 'completed').length;
      const streaming = Object.keys(activeTokens).length;
      const timeouts = Object.values(currentRound.responses || {}).filter((r) => r.status === 'timeout').length;
      
      const pTitle = currentRound.pass_or_round_title || `Round ${currentRound.round_number}`;
      return `🟢 Active: ${pTitle} — [${completed}/${total} Completed${streaming > 0 ? ` · ${streaming} Generating` : ''}${timeouts > 0 ? ` · ${timeouts} Quarantined` : ''}]`;
    }
    return `Deliberation in progress (${currentStatus})...`;
  }, [sessionId, session, currentStatus, isArbiterThinking, currentRound, models, sessionSelectedModels, activeTokens]);

  const handleStartDebate = async () => {
    if (!problemStatement.trim()) {
      alert('Please enter or select a problem statement.');
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
        alert(`Error starting debate: ${err.detail || 'Server error'}`);
      }
    } catch (e: any) {
      alert(`Network error: ${e.message}`);
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
      alert('Master configurations and credentials saved permanently as default baseline.');
    } catch (e: any) {
      alert(`Save error: ${e.message}`);
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
      alert(`Test All error: ${e.message}`);
    } finally {
      setIsTestingAll(false);
    }
  };

  // Run dynamic discovery across all provider keys entered
  const handleExecuteDiscovery = async () => {
    setIsDiscovering(true);
    setAvailableDiscovered([]);
    setUnavailableDiscovered([]);
    try {
      const res = await fetch('/api/providers/auto-discover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider_keys: wizardKeys })
      });
      if (!res.ok) {
        const errText = (await res.text()).trim();
        if (res.status === 500 && /^internal server error$/i.test(errText)) {
          // Bare body = the Next dev proxy gave up on the backend, not a backend 500.
          throw new Error(
            'The backend did not respond in time. Confirm the API is running on http://127.0.0.1:8000 (open /health), then retry.'
          );
        }
        throw new Error(errText || `HTTP ${res.status}`);
      }
      const data = await res.json();
      const avail = data.available_models || [];
      const unavail = data.unavailable_models || [];
      setAvailableDiscovered(avail);
      setUnavailableDiscovered(unavail);

      // Default selection: Select all available Admin Favorites, or all available if none
      const sel: Record<string, boolean> = {};
      const hasFavs = avail.some((x: any) => x.is_admin_favorite);
      avail.forEach((item: any) => {
        if (hasFavs) {
          sel[item.model.id] = !!item.is_admin_favorite;
        } else {
          sel[item.model.id] = true;
        }
      });
      setSelectedDiscovered(sel);
      setWizardFlowState('results');
    } catch (e: any) {
      alert(`Discovery error: ${e.message}`);
    } finally {
      setIsDiscovering(false);
    }
  };

  // Quick select Admin Favorites only
  const handleSelectAdminFavorites = () => {
    const sel: Record<string, boolean> = {};
    availableDiscovered.forEach((item) => {
      if (item.is_admin_favorite) {
        sel[item.model.id] = true;
      }
    });
    setSelectedDiscovered(sel);
  };

  // Apply selected models to THIS session only (preserves user_config.json)
  const handleApplyToSession = () => {
    const chosen = availableDiscovered
      .filter((item) => selectedDiscovered[item.model.id])
      .map((item) => item.model);

    if (chosen.length === 0) {
      alert('Please select at least 1 verified model.');
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
    alert(`Selected ${chosen.length} verified models for your debate session!`);
  };

  const handleAddCustomModel = () => {
    if (!customForm.base_url || !customForm.model_id) {
      alert('Please enter a Base URL and Model ID.');
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
    alert(`Added "${newM.name}" to your fleet!`);
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
      alert('At least 2 participating AI models are required.');
      return;
    }
    setModels(models.filter((m) => m.id !== id));
  };

  const handleTestModel = async (model: ModelConfig) => {
    setTestingModelId(model.id);
    try {
      const res = await fetch('/api/models/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
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
    await sendModeratorAction('inject_prompt', { injection_text: injectionText.trim() });
    setInjectionText('');
    setIsInjectModalOpen(false);
  };

  const handleOpenHistory = async () => {
    setIsHistoryModalOpen(true);
    setIsLoadingHistory(true);
    try {
      const res = await fetch('/api/workspaces');
      const data = await res.json();
      setSavedWorkspaces(Array.isArray(data) ? data : []);
    } catch (e: any) {
      alert(`Error loading history: ${e.message}`);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const [historySearchFilter, setHistorySearchFilter] = useState('');
  const [historyStatusFilter, setHistoryStatusFilter] = useState<'All' | 'live' | 'completed' | 'paused'>('All');

  const handleLoadSavedSession = (targetSessionId: string) => {
    setSessionId(targetSessionId);
    localStorage.setItem('active_debate_session_id', targetSessionId);
    setIsHistoryModalOpen(false);
    setActiveTab('arena');
  };

  const handleDeleteSession = async (targetSessionId: string, folderName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Are you sure you want to delete workspace "${folderName}"?`)) return;
    try {
      const res = await fetch(`/api/workspaces/${targetSessionId}`, { method: 'DELETE' });
      if (res.ok) {
        setSavedWorkspaces((prev) => prev.filter((w) => w.session_id !== targetSessionId));
        if (sessionId === targetSessionId) {
          setSessionId('');
          localStorage.removeItem('active_debate_session_id');
        }
      } else {
        alert('Failed to delete workspace.');
      }
    } catch (err: any) {
      alert(`Error deleting workspace: ${err.message}`);
    }
  };

  const handleSendArbiterCommand = async (customCmd?: string) => {
    const cmd = customCmd || arbiterCommandText.trim();
    if (!cmd || !sessionId) {
      if (!sessionId) alert('Please start or select a debate session first.');
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
      const data = await res.json();
      if (res.ok) {
        setArbiterActionLogs((prev) => [
          ...prev,
          {
            sender: `${data.arbiter_model || 'GPT 5.6 Sol'} (Master Arbiter)`,
            text: data.response || 'Command executed.',
            time: new Date().toLocaleTimeString()
          }
        ]);
      } else {
        setArbiterActionLogs((prev) => [
          ...prev,
          {
            sender: 'System Alert',
            text: `Error: ${data.detail || 'Failed to execute command.'}`,
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
    const isCurrentlyDisabled = !!disabledSessionModels[modelId];
    const newDisabledState = !isCurrentlyDisabled;
    
    setDisabledSessionModels((prev) => ({
      ...prev,
      [modelId]: newDisabledState
    }));

    if (newDisabledState && sessionId) {
      try {
        await sendModeratorAction('drop_model', { target_model_id: modelId });
      } catch (e) {}
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
    return models.filter((m) => {
      if (fleetFilter === 'enabled') return sessionSelectedModels[m.id] !== false;
      if (fleetFilter === 'online') return testResults[m.id]?.success;
      return true;
    });
  }, [models, fleetFilter, sessionSelectedModels, testResults]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedVerdict(true);
    setTimeout(() => setCopiedVerdict(false), 2500);
  };

  const currentProvider = WIZARD_PROVIDERS[cardIndex];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors duration-200 selection:bg-indigo-100 dark:selection:bg-indigo-900/60 selection:text-indigo-900 dark:selection:text-indigo-100">
      
      {/* ========================================================================= */}
      {/* 1. TOP HEADER NAVIGATION BAR */}
      {/* ========================================================================= */}
      <header className="sticky top-0 z-40 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 shadow-sm px-4 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          
          {/* Logo & Title */}
          <div className="flex items-center gap-3.5 w-full md:w-auto justify-between md:justify-start">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-600 dark:bg-indigo-500 text-white shadow-md shadow-indigo-500/20">
                <Bot className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-lg font-black tracking-tight text-slate-900 dark:text-white">AI Consensus Arena</h1>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-indigo-50 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                    SIH Super-Engine
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                  4-Phase Deliberation · 3-Stage Pooled Hive-Mind · {models.length}-Model Gauntlet
                </p>
              </div>
            </div>

            {/* Dark / Light Mode Toggle Button */}
            <div className="flex items-center gap-2">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700 transition border border-slate-200 dark:border-slate-700 flex items-center gap-1 text-xs font-bold"
                title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
              >
                {theme === 'light' ? (
                  <>
                    <Moon className="w-4 h-4 text-indigo-600" />
                    <span className="hidden sm:inline">Dark</span>
                  </>
                ) : (
                  <>
                    <Sun className="w-4 h-4 text-amber-400" />
                    <span className="hidden sm:inline">Light</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Quick Action Controls */}
          <div className="flex items-center gap-2 w-full md:w-auto justify-end overflow-x-auto pb-1 md:pb-0 flex-wrap">
            {/* 👑 Command Master Arbiter Button */}
            <button
              type="button"
              onClick={() => setIsArbiterCommandOpen(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-black transition shadow-md shadow-purple-500/20 animate-pulse shrink-0"
              title="Command Supreme Master Arbiter (GPT 5.6 Sol)"
            >
              <Award className="w-4 h-4 text-amber-300" />
              <span>👑 Command Arbiter</span>
            </button>

            {/* 📂 Session History Button */}
            <button
              type="button"
              onClick={handleOpenHistory}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-bold transition border border-slate-200 dark:border-slate-700 shadow-xs shrink-0"
              title="Browse & Resume Saved Debate Workspaces"
            >
              <History className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <span>📂 History</span>
              {savedWorkspaces.length > 0 && (
                <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-extrabold">
                  {savedWorkspaces.length}
                </span>
              )}
            </button>

            {/* Active Session Live Controls */}
            {sessionId ? (
              <>
                {/* 🔍 Ask Arbiter to Check Fleet */}
                <button
                  type="button"
                  onClick={() => {
                    handleSendArbiterCommand("Scan all fleet models right now, diagnose hanging or failing nodes, report latencies, and optimize execution.");
                    setIsArbiterCommandOpen(true);
                  }}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-purple-50 dark:bg-purple-950/80 hover:bg-purple-100 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800 text-xs font-bold shadow-xs transition shrink-0"
                  title="Ask Master Arbiter (GPT 5.6 Sol) to inspect all fleet nodes"
                >
                  <Activity className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
                  <span className="hidden sm:inline">🔍 Check Fleet</span>
                </button>

                {currentStatus === 'running' ? (
                  <button
                    type="button"
                    onClick={() => sendModeratorAction('pause')}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-amber-50 dark:bg-amber-950/80 hover:bg-amber-100 text-amber-800 dark:text-amber-200 border border-amber-300 dark:border-amber-800 text-xs font-black shadow-xs transition shrink-0"
                    title="Pause Deliberation"
                  >
                    <Pause className="w-3.5 h-3.5" /> <span>⏸️ Pause</span>
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => sendModeratorAction('resume')}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-black shadow-md shadow-emerald-500/20 transition ring-2 ring-emerald-400/40 shrink-0"
                    title="Resume Deliberation"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" /> <span>▶️ Resume</span>
                  </button>
                )}

                <button
                  type="button"
                  onClick={() => setIsInjectModalOpen(true)}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 text-xs font-bold transition shrink-0"
                  title="Inject moderator direction"
                >
                  <MessageSquarePlus className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" /> <span className="hidden sm:inline">Inject</span>
                </button>

                <button
                  type="button"
                  onClick={() => sendModeratorAction('call_verdict')}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-purple-50 dark:bg-purple-950/60 hover:bg-purple-100 text-purple-700 dark:text-purple-200 border border-purple-200 dark:border-purple-800 text-xs font-bold transition shrink-0"
                  title="Force Master Arbiter Sovereign Deliverable"
                >
                  <Award className="w-3.5 h-3.5" /> <span className="hidden sm:inline">Final Verdict</span>
                </button>
              </>
            ) : null}

            {/* Quick Setup Wizard Button */}
            <button
              type="button"
              onClick={() => {
                setWizardFlowState('initial_choice');
                setCardIndex(0);
                setIsWizardOpen(true);
              }}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold shadow-xs transition shrink-0"
            >
              <Wand2 className="w-3.5 h-3.5" /> <span className="hidden sm:inline">Setup Wizard</span>
            </button>

            {/* Start Deliberation Button */}
            <button
              type="button"
              onClick={() => setIsStartModalOpen(true)}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-black shadow-md shadow-indigo-500/20 transition shrink-0"
            >
              <Sparkles className="w-3.5 h-3.5" /> <span>Start Deliberation</span>
            </button>
          </div>
        </div>

        {/* 5 Clean Navigation Tabs */}
        <div className="max-w-7xl mx-auto mt-3 pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between overflow-x-auto">
          <nav className="flex items-center gap-1">
            <button
              onClick={() => setActiveTab('arena')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
                activeTab === 'arena'
                  ? 'bg-indigo-50 dark:bg-indigo-950/80 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <Bot className="w-4 h-4 text-indigo-600 dark:text-indigo-400" /> 🏟️ Arena View
            </button>

            <button
              onClick={() => setActiveTab('research')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
                activeTab === 'research'
                  ? 'bg-amber-50 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <BookOpen className="w-4 h-4 text-amber-600 dark:text-amber-400" /> 🔬 Research Hub
              {session?.latest_research_dossier?.total_sources ? (
                <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-amber-200 dark:bg-amber-900 text-amber-900 dark:text-amber-100 font-bold">
                  {session.latest_research_dossier.total_sources}
                </span>
              ) : null}
            </button>

            <button
              onClick={() => setActiveTab('critiques')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
                activeTab === 'critiques'
                  ? 'bg-rose-50 dark:bg-rose-950/80 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <Swords className="w-4 h-4 text-rose-600 dark:text-rose-400" /> ⚔️ Critique Matrix
            </button>

            <button
              onClick={() => setActiveTab('verdict')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
                activeTab === 'verdict'
                  ? 'bg-purple-50 dark:bg-purple-950/80 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <Award className="w-4 h-4 text-purple-600 dark:text-purple-400" /> 👑 Verdict Studio
            </button>

            <button
              onClick={() => setActiveTab('config')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition ${
                activeTab === 'config'
                  ? 'bg-slate-200 dark:bg-slate-800 text-slate-900 dark:text-white border border-slate-300 dark:border-slate-700 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <Settings className="w-4 h-4 text-slate-700 dark:text-slate-300" /> ⚙️ Fleet & API Keys ({models.length})
            </button>
          </nav>

          {session && (
            <div className="hidden md:flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 font-medium">
              <span>Domain: <strong className="text-slate-800 dark:text-slate-200">{session.ministry_domain}</strong></span>
              <span>·</span>
              <span>Rounds: <strong className="text-slate-800 dark:text-slate-200">{session.rounds.length}</strong></span>
              <span>·</span>
              <span>Models: <strong className="text-slate-800 dark:text-slate-200">{models.filter((m) => sessionSelectedModels[m.id] ?? m.enabled).length}</strong> / {models.length} Active</span>
            </div>
          )}
        </div>
      </header>

      {/* ========================================================================= */}
      {/* 2. PROMINENT LIVE STATUS TICKER & 13-STEP PIPELINE STEPPER */}
      {/* ========================================================================= */}
      <section className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 lg:px-8 py-3.5 shadow-sm space-y-3">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
          
          <div className="flex items-center gap-3 w-full md:w-auto">
            <span className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider flex items-center gap-1.5 shrink-0 ${
              currentStatus === 'running'
                ? 'bg-emerald-50 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                : currentStatus === 'paused'
                ? 'bg-amber-50 dark:bg-amber-950/80 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
                : currentStatus === 'completed'
                ? 'bg-purple-50 dark:bg-purple-950/80 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
            }`}>
              <span className={`w-2 h-2 rounded-full ${
                currentStatus === 'running' ? 'bg-emerald-500 animate-pulse' : currentStatus === 'paused' ? 'bg-amber-500' : currentStatus === 'completed' ? 'bg-purple-500' : 'bg-slate-400'
              }`} />
              {currentStatus === 'running' ? '🟢 LIVE DEBATE' : currentStatus === 'paused' ? '⏸️ PAUSED' : currentStatus === 'completed' ? '🏆 COMPLETED' : 'READY'}
            </span>

            <p className="text-xs font-bold text-slate-800 dark:text-slate-200 leading-snug">
              {liveStatusText}
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {/* Quick Fleet Health Check Button */}
            <button
              type="button"
              onClick={() => {
                handleSendArbiterCommand("Scan all fleet models right now, diagnose hanging or failing nodes, report latencies, and optimize execution.");
                setIsArbiterCommandOpen(true);
              }}
              className="px-3 py-1.5 rounded-xl bg-purple-50 dark:bg-purple-950/80 hover:bg-purple-100 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800 text-xs font-bold transition flex items-center gap-1.5"
            >
              <Activity className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
              <span>🔍 Check Fleet Health</span>
            </button>

            {currentRound?.arbiter_eval && (
              <div className="flex items-center gap-1.5 bg-purple-50 dark:bg-purple-950/80 border border-purple-200 dark:border-purple-800 px-3 py-1.5 rounded-xl text-purple-900 dark:text-purple-200 text-xs font-bold">
                <span>Consensus:</span>
                <span className="text-sm font-black text-purple-700 dark:text-purple-300">{currentRound.arbiter_eval.consensus_score}%</span>
              </div>
            )}
          </div>
        </div>

        {/* 13-STEP INTERACTIVE DELIBERATION PIPELINE STEPPER */}
        <div className="max-w-7xl mx-auto pt-2.5 border-t border-slate-100 dark:border-slate-800/80">
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
            <span className="text-[10px] font-black uppercase tracking-wider text-slate-400 shrink-0 mr-1.5">
              Gauntlet Pipeline:
            </span>
            {PIPELINE_STEPS.map((step, idx) => {
              const roundIndex = session?.rounds ? session.rounds.findIndex((r) => r.pass_or_round_id === step.id) : -1;
              const isCompleted = roundIndex !== -1 && !!session?.rounds?.[roundIndex]?.completed_at;
              const isCurrent = session?.current_pass_id === step.id || (!isCompleted && session?.rounds && idx === session.rounds.length);
              const roundObj = (session?.rounds && roundIndex !== -1) ? session.rounds[roundIndex] : null;
              const consensus = roundObj?.arbiter_eval?.consensus_score;

              return (
                <button
                  key={step.id}
                  type="button"
                  onClick={() => {
                    if (roundIndex !== -1) {
                      setSelectedRoundIndex(roundIndex);
                      setActiveTab('arena');
                    }
                  }}
                  className={`px-3 py-1.5 rounded-xl text-xs font-extrabold whitespace-nowrap transition flex items-center gap-1.5 shrink-0 ${
                    isCurrent
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25 ring-2 ring-indigo-400/40 animate-pulse'
                      : isCompleted
                      ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 hover:bg-emerald-100 cursor-pointer'
                      : 'bg-slate-100 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700/60'
                  }`}
                  title={step.title}
                >
                  {isCompleted ? (
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                  ) : isCurrent ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-white" />
                  ) : (
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                  )}
                  <span>{step.short}</span>
                  {consensus ? (
                    <span className="px-1.5 py-0.2 rounded-full bg-emerald-200 dark:bg-emerald-900 text-emerald-900 dark:text-emerald-100 text-[10px] font-black">
                      {consensus}%
                    </span>
                  ) : null}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 3. MAIN DASHBOARD CONTENT (5 TABS) */}
      {/* ========================================================================= */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8 space-y-6">
        
        {/* TAB 1: 🏟️ ARENA VIEW */}
        {activeTab === 'arena' && (
          <div className="space-y-6">
            {session && session.rounds.length > 0 && (
              <div className="bg-white dark:bg-slate-900 p-3 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-2 overflow-x-auto">
                <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider pl-2 pr-1">Sub-Rounds:</span>
                {session.rounds.map((r, idx) => {
                  const isSelected = selectedRoundIndex === idx;
                  return (
                    <button
                      key={idx}
                      onClick={() => setSelectedRoundIndex(idx)}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition flex items-center gap-1.5 ${
                        isSelected
                          ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                      }`}
                    >
                      <span>{r.pass_or_round_title || `Round ${r.round_number}`}</span>
                      {r.arbiter_eval?.consensus_score && (
                        <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${
                          isSelected ? 'bg-indigo-800 text-indigo-100' : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
                        }`}>
                          {r.arbiter_eval.consensus_score}%
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {models.filter((m) => sessionSelectedModels[m.id] ?? m.enabled).map((m) => {
                const resp: DebaterResponse | undefined = currentRound?.responses?.[m.id];
                const isStreaming = resp?.status === 'streaming' || (activeTokens[m.id] && !resp?.status);
                const tokenStream = activeTokens[m.id] || '';
                const isArbiter = m.id === arbiterModelId;
                const isBackupArbiter = m.id === backupArbiterModelId;
                const isManuallyDisabled = !!disabledSessionModels[m.id];

                return (
                  <div
                    key={m.id}
                    className={`rounded-2xl border shadow-sm hover:shadow-md transition flex flex-col justify-between overflow-hidden ${
                      isManuallyDisabled
                        ? 'bg-slate-100/70 dark:bg-slate-900/40 border-rose-200 dark:border-rose-900/50 opacity-60'
                        : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800'
                    }`}
                  >
                    <div className={`p-4 border-b ${isManuallyDisabled ? 'bg-rose-50/50 dark:bg-rose-950/20 border-rose-100 dark:border-rose-900/30' : 'bg-slate-50/50 dark:bg-slate-800/40 border-slate-100 dark:border-slate-800'}`}>
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className={`font-extrabold text-sm ${isManuallyDisabled ? 'text-rose-900 dark:text-rose-300 line-through' : 'text-slate-900 dark:text-white'}`}>{m.name}</span>
                          {isArbiter && (
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-purple-100 dark:bg-purple-950 text-purple-800 dark:text-purple-300 border border-purple-200 dark:border-purple-800">
                              Primary Arbiter
                            </span>
                          )}
                          {isBackupArbiter && (
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                              Backup Arbiter
                            </span>
                          )}
                          {isManuallyDisabled && (
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-black uppercase bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
                              ⛔ Excluded
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-2">
                          {isManuallyDisabled ? (
                            <button
                              type="button"
                              onClick={() => handleToggleModelTurnOff(m.id)}
                              className="px-2 py-0.5 rounded-lg bg-emerald-100 hover:bg-emerald-200 text-emerald-800 text-[10px] font-bold flex items-center gap-1 transition"
                              title="Turn Model Back On"
                            >
                              <Power className="w-3 h-3" /> Turn On
                            </button>
                          ) : (
                            <>
                              {isStreaming ? (
                                <span className="flex items-center gap-1 text-[11px] font-bold text-indigo-600 dark:text-indigo-400">
                                  <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Generating...
                                </span>
                              ) : resp?.status === 'completed' ? (
                                <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-600 dark:text-emerald-400">
                                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Done
                                </span>
                              ) : resp?.status === 'timeout' ? (
                                <span className="flex items-center gap-1 text-[11px] font-bold text-amber-600 dark:text-amber-400">
                                  <AlertTriangle className="w-3.5 h-3.5" /> Timeout
                                </span>
                              ) : resp?.status === 'error' ? (
                                <span className="flex items-center gap-1 text-[11px] font-bold text-rose-600 dark:text-rose-400">
                                  <X className="w-3.5 h-3.5" /> Error
                                </span>
                              ) : (
                                <span className="text-[11px] text-slate-400 font-medium">Ready</span>
                              )}

                              <button
                                type="button"
                                onClick={() => handleToggleModelTurnOff(m.id)}
                                className="p-1 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition"
                                title="Turn Off / Exclude this AI from debate"
                              >
                                <PowerOff className="w-3.5 h-3.5" />
                              </button>
                            </>
                          )}
                        </div>
                      </div>

                      <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
                        <span className="truncate max-w-[180px] font-mono">{m.model_id}</span>
                        {resp?.elapsed_seconds ? (
                          <span className="font-bold text-slate-700 dark:text-slate-300">{resp.elapsed_seconds.toFixed(1)}s</span>
                        ) : null}
                      </div>
                    </div>

                    <div className="p-4 flex-1 space-y-3">
                      {isStreaming && tokenStream ? (
                        <div className="p-2.5 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900 text-xs font-mono text-indigo-900 dark:text-indigo-200 max-h-36 overflow-y-auto">
                          {tokenStream.slice(-300)}
                        </div>
                      ) : null}

                      {resp?.structured ? (
                        <div className="space-y-2.5">
                          <div className="flex items-center justify-between bg-slate-50 dark:bg-slate-800/60 p-2 rounded-xl border border-slate-200/60 dark:border-slate-700">
                            <span className="text-xs text-slate-600 dark:text-slate-400 font-semibold">Consensus Vote:</span>
                            <div className="flex items-center gap-2">
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-black ${
                                resp.structured.consensus_vote === 'AGREE'
                                  ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300'
                                  : resp.structured.consensus_vote === 'NEEDS_REFINEMENT'
                                  ? 'bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300'
                                  : 'bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-300'
                              }`}>
                                {resp.structured.consensus_vote}
                              </span>
                              <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                                {resp.structured.agreement_percentage}%
                              </span>
                            </div>
                          </div>

                          <div className="text-xs text-slate-700 dark:text-slate-300 line-clamp-3 leading-relaxed">
                            {resp.structured.refined_solution || resp.raw_text}
                          </div>

                          <div className="grid grid-cols-2 gap-1 text-[10px] text-slate-600 dark:text-slate-400">
                            {resp.structured.architect_lens && (
                              <div className="p-1.5 rounded-lg bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-100/80 dark:border-indigo-900 truncate" title={resp.structured.architect_lens}>
                                🏛️ <strong className="text-indigo-900 dark:text-indigo-300">Arch:</strong> {resp.structured.architect_lens}
                              </div>
                            )}
                            {(resp.structured.critic_lens || resp.structured.critic_devil_advocate_lens) && (
                              <div className="p-1.5 rounded-lg bg-rose-50/60 dark:bg-rose-950/40 border border-rose-100/80 dark:border-rose-900 truncate" title={resp.structured.critic_lens || resp.structured.critic_devil_advocate_lens}>
                                😈 <strong className="text-rose-900 dark:text-rose-300">Critic:</strong> {resp.structured.critic_lens || resp.structured.critic_devil_advocate_lens}
                              </div>
                            )}
                            {(resp.structured.field_hardware_lens || resp.structured.pragmatist_feasibility_lens) && (
                              <div className="p-1.5 rounded-lg bg-amber-50/60 dark:bg-amber-950/40 border border-amber-100/80 dark:border-amber-900 truncate" title={resp.structured.field_hardware_lens || resp.structured.pragmatist_feasibility_lens}>
                                ⚙️ <strong className="text-amber-900 dark:text-amber-300">BOM:</strong> {resp.structured.field_hardware_lens || resp.structured.pragmatist_feasibility_lens}
                              </div>
                            )}
                            {(resp.structured.security_compliance_lens || resp.structured.security_reliability_lens) && (
                              <div className="p-1.5 rounded-lg bg-emerald-50/60 dark:bg-emerald-950/40 border border-emerald-100/80 dark:border-emerald-900 truncate" title={resp.structured.security_compliance_lens || resp.structured.security_reliability_lens}>
                                🛡️ <strong className="text-emerald-900 dark:text-emerald-300">Sec:</strong> {resp.structured.security_compliance_lens || resp.structured.security_reliability_lens}
                              </div>
                            )}
                          </div>
                        </div>
                      ) : !isStreaming ? (
                        <div className="text-xs text-slate-400 italic py-6 text-center">
                          Awaiting model invocation for this pass...
                        </div>
                      ) : null}
                    </div>

                    <div className="p-3 border-t border-slate-100 dark:border-slate-800 bg-slate-50/30 dark:bg-slate-800/30 flex items-center justify-between">
                      <span className="text-[10px] text-slate-400 font-medium">
                        {resp?.active_key_used ? 'Key: Active' : 'Provider: Ready'}
                      </span>
                      {resp ? (
                        <button
                          onClick={() => setSelectedScratchpadModel(resp)}
                          className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/80 hover:bg-indigo-100 dark:hover:bg-indigo-900/80 text-indigo-700 dark:text-indigo-300 text-xs font-bold transition"
                        >
                          <Eye className="w-3.5 h-3.5" /> View Scratchpad
                        </button>
                      ) : null}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB 2: 🔬 RESEARCH HUB */}
        {activeTab === 'research' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-amber-600" /> Standardized 3-Stage Pooled Research Hive-Mind
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  OpenAlex (250M Papers Graph) · arXiv Preprints · Tavily Web Engine · Local PDF Download & Extraction
                </p>
              </div>

              <div className="flex items-center gap-3">
                <div className="bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800 px-3.5 py-1.5 rounded-xl text-xs font-bold text-amber-900 dark:text-amber-300">
                  Total Sources: <strong className="text-sm font-black text-amber-700 dark:text-amber-400">{session?.latest_research_dossier?.total_sources || 0}</strong>
                </div>
                <div className="bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 px-3.5 py-1.5 rounded-xl text-xs font-bold text-indigo-900 dark:text-indigo-300">
                  Downloaded PDFs: <strong className="text-sm font-black text-indigo-700 dark:text-indigo-400">{session?.latest_research_dossier?.downloaded_papers_count || 0}</strong>
                </div>
              </div>
            </div>

            {/* STAGE 1 */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <h3 className="text-sm font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <Search className="w-4 h-4 text-indigo-600" /> 🔍 STAGE 1: Pooled Fact-Check & Claim Verification
                </h3>
                <span className="text-xs text-slate-400 font-medium">Tavily Advanced Search</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {session?.latest_research_dossier?.stage_1_fact_checks?.map((item, idx) => (
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
                )) || (
                  <p className="text-xs text-slate-400 italic">No fact-check records gathered yet for this round.</p>
                )}
              </div>
            </div>

            {/* STAGE 2 */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <h3 className="text-sm font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-amber-600" /> 📚 STAGE 2: Frontier Academic & SOTA Algorithm Papers
                </h3>
                <span className="text-xs text-slate-400 font-medium">OpenAlex & arXiv Ingestion</span>
              </div>

              <div className="space-y-3">
                {session?.latest_research_dossier?.stage_2_academic_papers?.map((item, idx) => (
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
                            href={`/api/workspaces/${sessionId}/research/paper_p${session?.current_phase_index || 1}_r${session?.current_round_num || 1}_${idx+1}.pdf`}
                            download
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold shadow-sm transition"
                          >
                            <Download className="w-3.5 h-3.5" /> Download PDF
                          </a>
                          <a
                            href={`/api/workspaces/${sessionId}/research/paper_p${session?.current_phase_index || 1}_r${session?.current_round_num || 1}_${idx+1}.txt`}
                            target="_blank"
                            rel="noreferrer"
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 text-xs font-bold transition"
                          >
                            <FileText className="w-3.5 h-3.5" /> Plain TXT
                          </a>
                        </>
                      )}
                    </div>
                  </div>
                )) || (
                  <p className="text-xs text-slate-400 italic">No academic papers discovered yet for this round.</p>
                )}
              </div>
            </div>

            {/* STAGE 3 */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <h3 className="text-sm font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <Shield className="w-4 h-4 text-emerald-600" /> ⚙️ STAGE 3: Real-World Feasibility, Indian BOM & Standards
                </h3>
                <span className="text-xs text-slate-400 font-medium">Field Studies & Statutory Norms</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {session?.latest_research_dossier?.stage_3_field_benchmarks?.map((item, idx) => (
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
                )) || (
                  <p className="text-xs text-slate-400 italic">No field benchmarks gathered yet for this round.</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: ⚔️ CRITIQUE MATRIX */}
        {activeTab === 'critiques' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <h2 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <Swords className="w-5 h-5 text-rose-600" /> Peer-to-Peer Cross-Examination & Flaw Scrutiny Matrix
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Shows all peer attacks launched during Phase 2 & 3, identified vulnerabilities, counter-arguments, and concession adaptations.
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
                {currentRound?.responses && Object.values(currentRound.responses).some((r) => r.structured.critiques.length > 0 || r.structured.concessions_and_defenses.length > 0) ? (
                  Object.values(currentRound.responses).map((resp) => {
                    if (resp.structured.critiques.length === 0 && resp.structured.concessions_and_defenses.length === 0) return null;
                    return (
                      <div key={resp.model_id} className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 space-y-3">
                        <h4 className="font-black text-sm text-slate-900 dark:text-white flex items-center gap-2">
                          <Bot className="w-4 h-4 text-indigo-600 dark:text-indigo-400" /> {resp.model_name}
                        </h4>

                        {resp.structured.critiques.length > 0 && (
                          <div className="space-y-2">
                            <span className="text-[11px] font-bold uppercase tracking-wider text-rose-700 dark:text-rose-400">⚔️ Critiques Launched:</span>
                            {resp.structured.critiques.map((c, idx) => (
                              <div key={idx} className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-rose-100 dark:border-rose-900/60 space-y-1 text-xs">
                                <div className="font-bold text-rose-900 dark:text-rose-300">
                                  Target: <span className="text-slate-900 dark:text-white font-black">{c.target_model_name}</span> · Flaw: {c.flaw_identified}
                                </div>
                                <p className="text-slate-600 dark:text-slate-300">{c.counter_argument}</p>
                              </div>
                            ))}
                          </div>
                        )}

                        {resp.structured.concessions_and_defenses.length > 0 && (
                          <div className="space-y-2 pt-2">
                            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">🛡️ Concessions & Adaptations:</span>
                            {resp.structured.concessions_and_defenses.map((cd, idx) => (
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
        {activeTab === 'verdict' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-900 p-6 lg:p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
              
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-5">
                <div>
                  <h2 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                    <Award className="w-6 h-6 text-purple-600 dark:text-purple-400" /> Sovereign SIH Master Consensus Deliverable
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
                    Ratified by {models.filter((m) => sessionSelectedModels[m.id] ?? m.enabled).length} autonomous AI models with 0 fatal friction points.
                  </p>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  {models.filter((m) => sessionSelectedModels[m.id] ?? m.enabled).map((m) => (
                    <span key={m.id} className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-white dark:bg-slate-900 text-purple-900 dark:text-purple-300 border border-purple-200 dark:border-purple-800 shadow-xs flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-emerald-500" /> {m.name}
                    </span>
                  ))}
                </div>
              </div>

              {session?.final_markdown_report ? (
                <article className="prose prose-slate dark:prose-invert max-w-none prose-headings:font-black prose-h1:text-2xl prose-h2:text-lg prose-h3:text-sm prose-p:text-xs prose-p:leading-relaxed prose-table:text-xs prose-th:bg-slate-100 dark:prose-th:bg-slate-800 prose-th:p-2 prose-td:p-2 prose-td:border prose-td:border-slate-200 dark:prose-td:border-slate-700">
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
          <div className="space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider">Total Configured</span>
                <div className="text-2xl font-black text-slate-900 dark:text-white">{models.length}</div>
                <span className="text-[11px] text-slate-400">Master Fleet</span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-xs text-emerald-600 dark:text-emerald-400 font-bold uppercase tracking-wider">Active in Session</span>
                <div className="text-2xl font-black text-emerald-700 dark:text-emerald-300">{models.filter((m) => sessionSelectedModels[m.id] ?? m.enabled).length}</div>
                <span className="text-[11px] text-slate-400">Participating</span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-xs text-purple-600 dark:text-purple-400 font-bold uppercase tracking-wider">Primary Arbiter</span>
                <div className="text-sm font-black text-purple-900 dark:text-purple-300 truncate">
                  {models.find((m) => m.id === arbiterModelId)?.name || 'Gemini 3.5 Lite'}
                </div>
                <span className="text-[11px] text-purple-500 font-semibold">Chief Jury Foreman</span>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-1">
                <span className="text-xs text-amber-600 dark:text-amber-400 font-bold uppercase tracking-wider">Backup Arbiter</span>
                <div className="text-sm font-black text-amber-900 dark:text-amber-300 truncate">
                  {models.find((m) => m.id === backupArbiterModelId)?.name || 'Gemini Flash Pool'}
                </div>
                <span className="text-[11px] text-amber-500 font-semibold">Failover Redundancy</span>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-4">
                <div>
                  <h2 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                    <KeyRound className="w-5 h-5 text-indigo-600" /> Master Model Fleet & API Credentials
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    Manage baseline endpoints and credentials. Selection changes during debates are kept per-session.
                  </p>
                </div>

                <div className="flex items-center gap-2.5 flex-wrap">
                  <button
                    onClick={() => {
                      setWizardFlowState('initial_choice');
                      setCardIndex(0);
                      setIsWizardOpen(true);
                    }}
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

              {/* Research API Configuration */}
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
                    onClick={() => setSessionSelectedModels({})}
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
                              const updated = [...models];
                              const targetIdx = models.findIndex((m) => m.id === model.id);
                              if (targetIdx >= 0) {
                                updated[targetIdx].name = e.target.value;
                                setModels(updated);
                              }
                            }}
                            className="font-extrabold text-xs text-slate-900 dark:text-white bg-transparent border-b border-dashed border-slate-300 dark:border-slate-700 focus:outline-none focus:border-indigo-500"
                          />
                        </div>
                        <input
                          type="text"
                          value={model.model_id}
                          onChange={(e) => {
                            const updated = [...models];
                            const targetIdx = models.findIndex((m) => m.id === model.id);
                            if (targetIdx >= 0) {
                              updated[targetIdx].model_id = e.target.value;
                              setModels(updated);
                            }
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
                              const updated = [...models];
                              const targetIdx = models.findIndex((m) => m.id === model.id);
                              if (targetIdx >= 0) {
                                updated[targetIdx].api_key = e.target.value;
                                setModels(updated);
                              }
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
                              const updated = [...models];
                              const targetIdx = models.findIndex((m) => m.id === model.id);
                              if (targetIdx >= 0) {
                                updated[targetIdx].base_url = e.target.value;
                                setModels(updated);
                              }
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

      {/* ========================================================================= */}
      {/* 4. COMPREHENSIVE CARD-BY-CARD API SETUP WIZARD */}
      {/* ========================================================================= */}
      {isWizardOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl max-w-xl w-full p-6 lg:p-8 space-y-5 max-h-[90vh] overflow-y-auto">
            
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-2xl bg-amber-500/10 text-amber-600 flex items-center justify-center font-black text-sm">
                  <Wand2 className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-black text-slate-900 dark:text-white">
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
                      ? 'Choose from verified online models or 1-click Admin Favorites.'
                      : 'Add your custom endpoint (Ollama / vLLM).'}
                  </p>
                </div>
              </div>

              <button
                onClick={() => setIsWizardOpen(false)}
                className="p-1.5 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition"
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
                          onClick={() => setCardIndex(cardIndex + 1)}
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
                      <button
                        onClick={handleExecuteDiscovery}
                        disabled={isDiscovering}
                        className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-black shadow-md transition"
                      >
                        {isDiscovering ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                        {isDiscovering ? 'Benchmarking Models...' : '⚡ Finish & Discover Models'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* STAGE C: RESULTS & ADMIN FAVORITES SELECTION */}
            {wizardFlowState === 'results' && (
              <div className="space-y-4">
                
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

                {/* Action Filters */}
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-700 dark:text-slate-300">
                    Online Models ({availableDiscovered.length} Available · Sorted by Latency):
                  </span>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        const sel: Record<string, boolean> = {};
                        availableDiscovered.forEach((item) => { sel[item.model.id] = true; });
                        setSelectedDiscovered(sel);
                      }}
                      className="text-indigo-600 dark:text-indigo-400 font-bold hover:underline"
                    >
                      Select All
                    </button>
                    <span>·</span>
                    <button
                      onClick={() => {
                        const sel: Record<string, boolean> = {};
                        availableDiscovered.slice(0, 5).forEach((item) => { sel[item.model.id] = true; });
                        setSelectedDiscovered(sel);
                      }}
                      className="text-amber-600 dark:text-amber-400 font-bold hover:underline"
                    >
                      Top 5 Fastest
                    </button>
                    <span>·</span>
                    <button
                      onClick={() => setSelectedDiscovered({})}
                      className="text-slate-400 font-bold hover:underline"
                    >
                      Deselect
                    </button>
                  </div>
                </div>

                {/* Available Online Models List (Sorted by latency) */}
                <div className="max-h-56 overflow-y-auto space-y-2 border border-slate-200 dark:border-slate-800 rounded-2xl p-2 bg-slate-50/50 dark:bg-slate-800/40">
                  {availableDiscovered.map((item, idx) => {
                    const m = item.model;
                    const isChecked = !!selectedDiscovered[m.id];
                    return (
                      <div
                        key={idx}
                        onClick={() => setSelectedDiscovered({ ...selectedDiscovered, [m.id]: !isChecked })}
                        className={`p-3 rounded-xl border flex items-center justify-between gap-3 text-xs cursor-pointer transition ${
                          isChecked
                            ? 'bg-indigo-50 dark:bg-indigo-950/80 border-indigo-200 dark:border-indigo-800 ring-1 ring-indigo-500/20'
                            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => {}}
                            className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4 cursor-pointer"
                          />
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-extrabold text-slate-900 dark:text-white">{m.name}</span>
                              {item.is_admin_favorite && (
                                <span className="px-1.5 py-0.2 rounded text-[9px] font-black uppercase bg-purple-100 dark:bg-purple-950 text-purple-800 dark:text-purple-300 border border-purple-200 dark:border-purple-800 flex items-center gap-0.5">
                                  <Star className="w-2.5 h-2.5 fill-current" /> Admin Pick
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-2 text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                              <span>{item.provider_name} · {m.model_id}</span>
                              {item.message && (
                                <span className="text-emerald-600 dark:text-emerald-400">· {item.message.replace('Verified Online! Response: ', '✓ ')}</span>
                              )}
                            </div>
                          </div>
                        </div>

                        <div>
                          <span className="px-2.5 py-1 rounded-lg text-[10px] font-black uppercase bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300">
                            🟢 {item.latency_ms}ms
                          </span>
                        </div>
                      </div>
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
                        <span>Unavailable / Failed Models ({unavailableDiscovered.length})</span>
                      </div>
                      {showUnavailableAccordion ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    </button>

                    {showUnavailableAccordion && (
                      <div className="p-3 bg-white dark:bg-slate-900 space-y-2 max-h-36 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800">
                        {unavailableDiscovered.map((item, idx) => (
                          <div key={idx} className="pt-2 text-xs flex items-start justify-between gap-3 opacity-70">
                            <div>
                              <div className="font-bold text-slate-800 dark:text-slate-200">{item.model.name}</div>
                              <p className="text-[10px] text-rose-500 font-mono">{item.message}</p>
                            </div>
                            <span className="text-[10px] font-bold text-slate-400">{item.provider_name}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Bottom Action Footer */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
                  <button
                    onClick={() => setWizardFlowState('cards')}
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
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl max-w-2xl w-full p-6 lg:p-8 space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <h3 className="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-600" /> Launch Multi-AI Deliberation Gauntlet
              </h3>
              <button
                onClick={() => setIsStartModalOpen(false)}
                className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500"
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
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl max-w-lg w-full p-6 space-y-4">
            <h3 className="text-sm font-black text-slate-900 dark:text-white flex items-center gap-2">
              <MessageSquarePlus className="w-4 h-4 text-indigo-600" /> Inject Moderator Directive
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
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
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex justify-end">
          <div className="bg-white dark:bg-slate-900 w-full max-w-2xl h-full shadow-2xl p-6 lg:p-8 flex flex-col justify-between space-y-6 overflow-y-auto">
            
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
                <div>
                  <h3 className="text-base font-black text-slate-900 dark:text-white flex items-center gap-2">
                    <Bot className="w-5 h-5 text-indigo-600" /> {selectedScratchpadModel.model_name}
                  </h3>
                  <span className="text-xs text-slate-400">{selectedScratchpadModel.pass_or_round_title || `Round ${selectedScratchpadModel.round_number}`}</span>
                </div>

                <button
                  onClick={() => setSelectedScratchpadModel(null)}
                  className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500"
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
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl max-w-2xl w-full p-6 lg:p-8 space-y-5 max-h-[85vh] flex flex-col justify-between">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400">
                  <History className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-black text-slate-900 dark:text-white">
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
                            {w.consensus_score ? (
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
                          <button
                            type="button"
                            onClick={() => handleLoadSavedSession(w.session_id)}
                            className={`px-3.5 py-2 rounded-xl text-xs font-black transition flex items-center gap-1.5 ${
                              isCurrent
                                ? 'bg-indigo-600 text-white shadow-xs'
                                : 'bg-white dark:bg-slate-900 hover:bg-indigo-50 dark:hover:bg-indigo-950 text-indigo-600 dark:text-indigo-400 border border-slate-200 dark:border-slate-700'
                            }`}
                          >
                            <FolderOpen className="w-3.5 h-3.5" />
                            {isCurrent ? 'Viewing Now' : 'Open & Resume'}
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
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl border-2 border-purple-500/50 shadow-2xl max-w-2xl w-full p-6 lg:p-8 space-y-4 max-h-[88vh] flex flex-col justify-between">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300">
                  <Award className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h3 className="text-base font-black text-slate-900 dark:text-white flex items-center gap-2">
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
