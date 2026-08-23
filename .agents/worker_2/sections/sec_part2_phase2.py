"""
Section: Part 2 — Phase 2: Central PPT Shortlisting & Idea Submission
"""

CONTENT = """# PART 2: PHASE 2 — CENTRAL PPT SHORTLISTING & IDEA SUBMISSION

Once your college SPOC uploads your team's nomination to the national AICTE portal, your proposal enters the **Central PPT Evaluation Phase**. This is the highest attrition filter in the entire hackathon. Across India, between 18,000 and 22,000 nominated team presentations are evaluated, and only **4 to 6 teams per Problem Statement** are selected for the Grand Finale.

---

## 2.1 Central Evaluator Psychology & The 60–90 Second Triage Window

Understanding the evaluator's operational reality is the single most critical factor in crafting a qualifying slide deck.

```
+-----------------------------------------------------------------------------------------------+
|                             CENTRAL EVALUATOR OPERATIONAL REALITY                             |
+-----------------------------------------------------------------------------------------------+
|  * Workload: 1 Senior Evaluator (IIT/NIT Professor or NIC Scientist) reviews 80 to 150 PPTs   |
|    in a single 3-hour evening window after their regular working hours.                       |
|  * Time Per Slide Deck: Exactly 60 to 90 seconds.                                             |
|  * Evaluation Environment: Browser-based portal with PDF viewer; evaluators scroll rapidly.   |
|  * First-Pass Scan Pattern:                                                                   |
|    1. Check Slide 1: Is PS Code, Ministry, and Team structure compliant? (5 seconds)         |
|    2. Check Slide 3: Is there a legitimate Architecture Diagram or a generic flowchart? (15s)|
|    3. Check Slide 4: Is the Tech Stack realistic or buzzword salad? (10 seconds)              |
|    4. Check Slide 2 & 6: Does the solution solve the Ministry's exact pain point? (20 seconds)|
|    5. Assign Score & Move to next deck.                                                       |
+-----------------------------------------------------------------------------------------------+
```

If your architecture is unreadable, if your slides are dense walls of text, or if you use vague buzzwords without engineering specifics, your deck is dismissed in the first 30 seconds.

---

## 2.2 The Official National Portal Scoring Rubric (100-Point Formula)

Central evaluators grade submissions across five standardized parameters on the AICTE portal:

```
+-----------------------------------------------------------------------------------------------+
|                           NATIONAL PORTAL CENTRAL EVALUATION RUBRIC                           |
+-----------------------------------------------------------------------------------------------+
|  1. Problem Understanding & Proposed Solution Novelty ............. [ 20 Points ]             |
|     - Clarity of problem framing and alignment with Ministry objectives.                      |
|     - Uniqueness of the approach compared to conventional off-the-shelf products.            |
|                                                                                               |
|  2. Technical Architecture & Engineering Feasibility .............. [ 25 Points ]             |
|     - Depth and clarity of C4 / DFD system architecture diagram.                              |
|     - Realistic end-to-end data pipeline from ingestion to storage and presentation.         |
|                                                                                               |
|  3. Technology Stack Choice & Implementation Realism ............. [ 20 Points ]             |
|     - Appropriate selection of frameworks, databases, and communication protocols.           |
|     - Evidence of offline resilience, local caching, and low-latency optimization.            |
|                                                                                               |
|  4. Impact, Scalability & Government Viability ..................... [ 25 Points ]             |
|     - Quantitative ROI, cost-benefit analysis, and user reach (rural/urban).                  |
|     - Alignment with Indian statutory compliance (DPDP Act 2023, NIC Guidelines).            |
|                                                                                               |
|  5. Presentation Polish, Clarity & Visual Structure ............... [ 10 Points ]             |
|     - Adherence to official AICTE template format, typography, and visual hierarchy.          |
|                                                                                               |
|  TOTAL SCORE ....................................................... [ 100 Points ]          |
+-----------------------------------------------------------------------------------------------+
```

---

## 2.3 The 7 Instant-Rejection Red Flags ("Trash-Bin" Triggers)

Central evaluators immediately discard proposals that exhibit any of the following seven red flags:

```
+-----------------------------------------------------------------------------------------------+
|                         THE 7 INSTANT-REJECTION "TRASH-BIN" RED FLAGS                         |
+-----------------------------------------------------------------------------------------------+
|                                                                                               |
| 1. BUZZWORD SALAD (The "Crypto-Quantum-AI" Trap)                                              |
|    - Stating: "We utilize Blockchain, Quantum AI, IoT, Web3, and Deep Learning to solve X."   |
|    - Evaluator reaction: "The team has no idea how any of these technologies work together." |
|                                                                                               |
| 2. THE HAND-WAVY "AI/ML MAGIC BOX"                                                           |
|    - Submitting an architecture diagram with an unexplained rectangle labeled "AI Engine".   |
|    - Evaluators demand exact models: e.g., "Fine-tuned IndicBERT ONNX runtime + Faiss vector  |
|      index" instead of "AI Magic".                                                            |
|                                                                                               |
| 3. IGNORING THE INDIAN GROUND REALITY                                                         |
|    - Building a mobile app that requires continuous 100 Mbps 5G connectivity and a 100MB     |
|      React bundle for rural ASHA or Anganwadi workers operating in remote hilly terrains.     |
|                                                                                               |
| 4. MISSING DATA PIPELINE & TRAINING SOURCE                                                    |
|    - Claiming 99.4% model accuracy without mentioning the specific dataset name, number of   |
|      samples, ground-truth annotation strategy, or train-test split validation methodology.   |
|                                                                                               |
| 5. ZERO FEASIBILITY & UNIT ECONOMICS MATH                                                     |
|    - Proposing high-cost cloud infrastructures (e.g., streaming 1,000 CCTV video feeds to     |
|      AWS Rekognition at $0.10/min) that would bankrupt the sponsoring municipal department.   |
|                                                                                               |
| 6. GENERIC CANVA / CLIPART FLOWCHARTS                                                         |
|    - Using cartoon cliparts and vague circular arrows instead of formal C4 Container diagrams|
|      or ISO 5807 Data Flow Diagrams (DFDs) with explicit protocol labels (REST, gRPC, MQTT).  |
|                                                                                               |
| 7. DENSE WALLS OF TEXT (Font Size 10 Pt)                                                      |
|    - Pasting 500-word paragraphs into PPT slides. If the evaluator cannot read the slide in   |
|      15 seconds of visual scanning, it receives a zero for presentation polish.               |
+-----------------------------------------------------------------------------------------------+
```

---

## 2.4 Forensic Slide-by-Slide Deconstruction of the Official SIH PPT Template

AICTE provides a strict, mandatory **7-Slide PowerPoint Template**. Modifying the sequence or adding excess slides risks instant disqualification. Below is the forensic blueprint for maximizing points on each slide.

```
+-----------------------------------------------------------------------------------------------+
|                       OFFICIAL SIH PPT TEMPLATE: SLIDE-BY-SLIDE GUIDE                         |
+-----------------------------------------------------------------------------------------------+
|  SLIDE 1: Title & Metadata Slide                                                              |
|  - Mandatory Fields: Problem Statement ID & Title, Ministry/Department Name, Category (SW/HW)|
|  - Team Details: Team Name, Institute Name, Team Leader + 5 Member Names with ASSIGNED ROLES  |
|    (e.g., "Aarav Sharma — Lead Backend Architect", "Priya Nair — AI/ML & Pipeline Engineer").|
|  - Visual: Official SIH Logo (left), Ministry Emblem (right), College Logo (center top).      |
|                                                                                               |
|  SLIDE 2: Proposed Solution & Core Innovation                                                 |
|  - Format: 3-Column Visual Layout (No long paragraphs).                                       |
|    * Column 1: Core Problem & Bureaucratic Bottleneck (Quantified with real data).           |
|    * Column 2: Proposed Technological Mechanism (Specific algorithm / workflow).             |
|    * Column 3: Key Differentiators vs Existing Systems (Tabular comparison matrix).           |
|                                                                                               |
|  SLIDE 3: Detailed Technical Architecture Diagram (The 25-Point Slide)                        |
|  - Must contain a formal C4 Level 2 Container Architecture Diagram.                           |
|  - Explicitly depict Client Tier (PWA/Mobile), Gateway Tier (FastAPI/Nginx), Service Tier,    |
|    Data Tier (PostgreSQL + PostGIS, Redis), and Asynchronous Task Worker Tier (Celery/BullMQ).|
|  - Annotate every single connector line with the exact protocol: e.g., HTTPS REST, WSS, MQTT. |
|                                                                                               |
|  SLIDE 4: Technology Stack & Production Tooling Matrix                                        |
|  - Grid Layout categorizing every layer:                                                      |
|    * Frontend: Next.js 14, Tailwind CSS, TypeScript, Workbox (PWA Offline Sync)               |
|    * Backend & API: FastAPI (Python 3.11) / Express (Node.js LTS), Redis 7.2 (Cache/Queue)    |
|    * Database & Storage: PostgreSQL 16 + PostGIS, MinIO S3-Compatible Local Object Store       |
|    * AI/ML & Analytics: PyTorch, ONNX Runtime, Faiss, OpenCV, FastEmbed                       |
|    * Edge & Offline: SQLite / IndexedDB, WebAssembly, Bhashini Offline Indic Models           |
|    * DevOps & Infra: Docker Compose, Nginx Reverse Proxy, Prometheus & Grafana Telemetry      |
|                                                                                               |
|  SLIDE 5: Feasibility, Viability & Risk Mitigation Matrix                                     |
|  - Structured Table with 4 Columns:                                                           |
|    [ Operational / Technical Risk ] -> [ Severity (H/M/L) ] -> [ Mitigation Strategy ] ->     |
|    [ Compliance Verification (e.g., DPDP Act 2023, ISO 27001, MeitY Guidelines) ]             |
|                                                                                               |
|  SLIDE 6: Impact, Scalability & Government Value Proposition                                 |
|  - Quantified Impact Metrics:                                                                 |
|    * 70% Reduction in Administrative Turnaround Time (TAT).                                   |
|    * 100% Offline Operational Capability for Remote District Field Officers.                   |
|    * Zero Cloud Egress Cost via Localized Edge Inference Architecture.                        |
|  - 3-Tier Stakeholder Persona Map: Citizen -> District Collector / Officer -> State Secretary.|
|                                                                                               |
|  SLIDE 7: Team Credentials, Domain Research & References                                      |
|  - Prior Projects / Hackathons / Relevant GitHub Repositories of team members.                |
|  - Formal Academic & Government Citations:                                                    |
|    * Research Papers (IEEE/Springer/arXiv citations for ML models).                           |
|    * Official Ministry Reports & Data.gov.in Dataset Catalog IDs.                             |
+-----------------------------------------------------------------------------------------------+
```

---

## 2.5 C4 Architecture Model & Data Flow Diagram (DFD) Blueprints

A generic box-and-arrow diagram loses 15 out of 25 points on Slide 3. Below are production-grade ASCII blueprints representing the gold standard for SIH architecture slides.

### C4 Level 2 Container Architecture Diagram

```
+---------------------------------------------------------------------------------------------------+
|                                C4 LEVEL 2 CONTAINER ARCHITECTURE                                  |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [ CLIENT LAYER ]                                                                                 |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
|  | Citizen Mobile PWA        |  | Field Officer Mobile App  |  | Ministry Admin Dashboard      |  |
|  | Next.js / Tailwind / PWA  |  | React Native / Kotlin     |  | Next.js 14 / Tremor / ChartJS |  |
|  | Offline IndexedDB Cache   |  | Local SQLite / Encrypted  |  | Granular RBAC Role Views      |  |
|  +-------------+-------------+  +-------------+-------------+  +---------------+---------------+  |
|                |                              |                                |                  |
|                | HTTPS / WSS                  | HTTPS REST / mTLS              | HTTPS REST / 2FA |
|                v                              v                                v                  |
|  +---------------------------------------------------------------------------------------------+  |
|  |                            API GATEWAY & LOAD BALANCER (Nginx / Envoy)                      |  |
|  |  - Rate Limiting (Token Bucket) | JWT Bearer Auth | SSL Termination | Request Sanitization   |  |
|  +----------------------------------------------+----------------------------------------------+  |
|                                                 |                                                 |
|                                                 v Internal gRPC / HTTP REST                       |
|  [ APPLICATION SERVICES LAYER ]                                                                   |
|  +-----------------------------+  +----------------------------+  +----------------------------+  |
|  | Core Workflow Engine        |  | AI/ML Inference Service    |  | Sync & Notification Worker |  |
|  | FastAPI (Python 3.11)       |  | FastAPI + ONNX Runtime     |  | Node.js / BullMQ Engine    |  |
|  | Business Logic & Validation |  | Quantized Local Model (<1s)|  | SMS/WhatsApp Webhook Queue|  |
|  +--------------+--------------+  +--------------+-------------+  +--------------+-------------+  |
|                 |                                |                               |                |
|                 +--------------------------------+-------------------------------+                |
|                                                  |                                                |
|                                                  v                                                |
|  [ DATA & PERSISTENCE LAYER ]                                                                     |
|  +-----------------------------+  +----------------------------+  +----------------------------+  |
|  | Relational & Geospatial DB  |  | High-Speed In-Memory Cache |  | Object & Artifact Store    |  |
|  | PostgreSQL 16 + PostGIS     |  | Redis 7.2 Cluster          |  | MinIO S3-Compatible Storage|  |
|  | Normalized Ledger Schemas   |  | Session Cache & Job Queues |  | GeoTIFFs, PDFs, Audit Logs |  |
|  +-----------------------------+  +----------------------------+  +----------------------------+  |
+---------------------------------------------------------------------------------------------------+
```

### Data Flow Diagram (DFD Level 1)

```
+---------------------------------------------------------------------------------------------------+
|                                      DATA FLOW DIAGRAM (DFD LEVEL 1)                              |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [Citizen / Officer]                                                                              |
|          |                                                                                        |
|          | (1) Submits Form / Sensor Data + Geolocation (Offline Queue if No Network)             |
|          v                                                                                        |
|  [Client PWA Local Storage] <---> (2) Local Validation & SHA-256 Hash Generation                  |
|          |                                                                                        |
|          | (3) Auto-Sync when Connectivity Restored (HTTPS POST /api/v1/ingest)                   |
|          v                                                                                        |
|  [API Gateway & Auth Validator]                                                                   |
|          |                                                                                        |
|          | (4) Verified Payload (JWT Token Validated)                                             |
|          v                                                                                        |
|  [Core Ingestion Pipeline]                                                                        |
|     |                   |                                                                         |
|     | (5a) Write Record | (5b) Async Prediction Request                                           |
|     v                   v                                                                         |
|  [PostgreSQL DB]     [Local AI/ML Service] ---> (6) Returns Score & Anomaly Flag                  |
|     |                           |                                                                 |
|     | (7) State Update Event    +--------------------------------+                                |
|     v                                                            v                                |
|  [Event Message Queue (Redis)] ------------> [Notification Service]                               |
|                                                      |                                            |
|                                                      | (8) Dispatch SMS / Push Alert              |
|                                                      v                                            |
|                                              [Ministry Officer / Citizen]                         |
+---------------------------------------------------------------------------------------------------+
```

---

## 2.6 Feasible Tech Stacks vs. Buzzword Traps (Production Realism over Hype)

Evaluators grade harshly when teams propose over-engineered, fragile tech stacks. The winning rule is: **Choose boring, rugged, high-performance technology that you can run locally on an air-gapped laptop.**

| Dimension | The Buzzword Trap (Guaranteed Disqualification) | The Winning Production Stack (Maximum Evaluator Points) |
| :--- | :--- | :--- |
| **Database** | Public Ethereum / Solana Smart Contracts for government records | **PostgreSQL 16 + PostGIS** with cryptographic SHA-256 row-hash chaining and append-only audit tables |
| **Backend** | 18 Microservices orchestrated across Kubernetes clusters | **FastAPI (Python)** or **Fastify/Express (Node.js LTS)** in a clean modular monolith architecture |
| **AI / Machine Learning** | Cloud API calls to GPT-4o / Claude 3.5 Sonnet (fails when Wi-Fi drops) | **Quantized ONNX Runtime / GGUF (TinyLlama / Mistral 7B / IndicBERT)** running locally on CPU/GPU in sub-1.5 seconds |
| **Frontend & UI** | Heavy Three.js 3D animations and unoptimized WebGL | **Next.js 14 / Tailwind CSS** with Workbox Service Worker PWA for full offline-first mobile responsiveness |
| **Authentication** | Web3 MetaMask Wallet Auth for rural government officers | **Aadhaar e-KYC Simulation + Mobile OTP (Redis TTL) + JWT RBAC** (Citizen, Officer, Ministry Admin) |
| **Deployment** | Multi-region AWS CloudFormation with proprietary SaaS tools | Single-command **Docker Compose** containerization that spins up in 45 seconds on any air-gapped machine |
"""
