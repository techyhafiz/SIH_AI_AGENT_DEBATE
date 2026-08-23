# 🛡️ PROJECT PROPOSAL & PITCH REPORT
## Smart India Hackathon (SIH) — Software Edition
### Problem Statement Code: `SIH26183`
### Organization: Ministry of Home Affairs (MHA) — Indian Cyber Crime Coordination Centre (I4C)
### Project Working Title: **CryptoTrace-AI / KAVACH-BLOCK** *(Sovereign Real-Time Crypto Fraud Attribution & Asset Recovery Platform)*

---

## 📌 1. EXECUTIVE SUMMARY (The 60-Second Pitch)

### The Problem:
Every day, thousands of Indian citizens lose crores in **task-based frauds, fake investment schemes, sextortion, and ransomware**. When victims report a scammer's crypto wallet to the **1930 Cyber Helpline / NCRP Portal**, police sub-inspectors cannot trace the money. Scammers rapidly hop stolen funds across 3–5 intermediate burner wallets to reach KYC-enabled exchanges (**Binance, CoinDCX, WazirX**) and cash out to Indian bank accounts / P2P merchants. 

Currently, manual tracking takes **3 to 7 days**, by which time the funds are already liquidated. Existing foreign software (Chainalysis) costs **₹60+ Lakhs/year per license**, making it impossible to equip India's 16,000+ police stations.

### Our Solution:
We are building **CryptoTrace-AI**—an open-architecture, sovereign blockchain forensic and real-time attribution platform:
1. An investigating officer pastes **1 victim-reported wallet address**.
2. Our recursive graph-traversal engine automatically traces multi-hop peeling chains in **under 3 seconds**.
3. It identifies the destination **Centralized Exchange / VASP** and deposit account UID.
4. In **1-click**, it auto-generates a legally compliant **Section 91 CrPC (Section 94 BNSS) Emergency Freezing Requisition Notice PDF** addressed to the exchange's legal compliance team to freeze assets within the "Golden Hour" before liquidation.

---

## 🎯 2. WHY THIS PROJECT WILL WIN SIH (Our Competitive Moat)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        THE 4 WINNING PILLARS                           │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Direct Ministry Alignment   │ Directly solves MHA / I4C / 1930      │
│                                │ National Cyber Crime Portal workflow. │
├────────────────────────────────┼───────────────────────────────────────┤
│ 2. Visual "Wow" Factor         │ Animated real-time money-trail node   │
│                                │ graph (Cytoscape/D3.js).              │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. 100% Offline Demo-Ready     │ Fully Dockerized; pre-loaded local    │
│                                │ test cases; zero reliance on Wi-Fi.   │
├────────────────────────────────┼───────────────────────────────────────┤
│ 4. Massively Low Competition   │ Only a handful of teams nationwide    │
│                                │ tackle MHA blockchain forensics.      │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 🏗️ 3. SYSTEM ARCHITECTURE & DATA FLOW

```
[Victim Wallet Input / NCRP ID]
               │
               ▼
[Recursive Blockchain Traversal Engine (Python)]
   ├── Ingests Public Ledgers (Ethereum, Tron, Bitcoin, Polygon)
   ├── Peeling-Chain & Multi-Hop Detection Algorithm
   └── Known Exchange Wallet Attribution Database (5,000+ Tags)
               │
               ▼
[Interactive Graph Visualizer (Cytoscape / Next.js)]
   ├── Node 0: Victim Source ($5,000 USDT)
   ├── Hop 1 & 2: Intermediate Layering / Splitter Wallets
   └── Hop 3: [MATCH] Binance Hot Wallet / CoinDCX Deposit UID
               │
               ▼
[Automated Legal Compliance Engine]
   └── Generates Section 91 CrPC / Section 102 CrPC Seizure Notice PDF
```

---

## 💻 4. TECH STACK (Lightweight, Modern & Open-Source)

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | **Next.js (React) + Tailwind CSS + Shadcn UI** | High-polish modern police dashboard (Dark/Light mode). |
| **Graph Visualizer** | **Cytoscape.js / D3.js** | Interactive, zoomable, color-coded transaction flow nodes. |
| **Backend API** | **Python (FastAPI)** | High-throughput async transaction parsing & heuristic clustering. |
| **Database** | **PostgreSQL / SQLite + Neo4j** (or in-memory graph) | Storing wallet tags, cluster heuristics, and complaint logs. |
| **Blockchain Data** | **Web3.py + Free Public RPC / Etherscan / Tronscan APIs** | Fetching public on-chain transfers. |
| **Legal PDF Generator** | **ReportLab / WeasyPrint** | Instant generation of formal court/police requisition PDFs. |

---

## 👥 5. TEAM ROLES & RESPONSIBILITIES (6 Members)

| Role # | Title | Core Deliverable for SIH |
| :---: | :--- | :--- |
| **1** | **Team Leader & Pitch Lead** | Coordinates presentation, slides, Indian cyber law compliance (CrPC/BNSS/FIU-IND), and jury Q&A defense. |
| **2** | **Frontend & Graph Specialist** | Builds the responsive React dashboard and interactive Cytoscape.js animated transaction money-trail. |
| **3** | **Backend & API Engineer** | Builds FastAPI server, recursive BFS hop-tracing logic, and database schemas. |
| **4** | **Blockchain / Web3 Engineer** | Integrates Web3.py / Tron / EVM transaction parsing and exchange wallet attribution databases. |
| **5** | **AI / Data & Heuristics Engineer** | Implements transaction clustering, peeling-chain anomaly scoring, and risk categorization. |
| **6** | **Product / Legal & QA Engineer** | Builds the 1-click Section 91 CrPC PDF generator, test cases, offline mock seed datasets, and video backup. |

---

## 📅 6. 4-WEEK ROADMAP (From Zero to SIH Internal Qualification)

```
Week 1: UI Mockups & Static Graph UI (Next.js + Cytoscape dummy nodes)
Week 2: Backend Traversal Logic (Python script tracing multi-hop wallets via Etherscan/Tron)
Week 3: Legal Notice Generator + SQLite Database of 5,000+ Exchange Addresses
Week 4: End-to-End Polish, Seed 5 Real-World Scam Cases, Record 1080p Demo & Finalize 5-Slide PPT
```

---

## 🎤 7. KEY TALKING POINTS FOR COLLEGE MENTORS / FACULTY

1. **Why our college should nominate this**:
   - It targets the **Ministry of Home Affairs (MHA)**, which carries the highest prestige in SIH.
   - It tackles real national cybersecurity priorities (Indian Cyber Crime Coordination Centre - I4C).
2. **Feasibility**:
   - Does **not** require expensive paid hardware, GPUs, or proprietary APIs.
   - 100% achievable using standard Python and modern web technologies.
3. **Career / Placement Value**:
   - Teaches the team enterprise Graph Theory, Web3 protocols, DFIR forensics, and AppSec—guaranteeing top-tier portfolio projects for every team member.

---

*Report prepared for SIH Team Alignment & College Internal Hackathon Submission.*
