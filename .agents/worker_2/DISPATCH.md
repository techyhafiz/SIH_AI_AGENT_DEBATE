# Dispatch Assignment — Worker 2

## 2026-08-23T10:10:21Z

### Task Overview
You are Worker 2 on the Smart India Hackathon (SIH) Ground Reality Dossier project.
Working directory: c:/Users/mujaw/Downloads/SIH/.agents/worker_2
Path to Original Request: c:/Users/mujaw/Downloads/SIH/ORIGINAL_REQUEST.md
Target Deliverable to Update: c:/Users/mujaw/Downloads/SIH/SIH_GROUND_REALITY_HANDBOOK.md

### Feedback to Integrate from Challenger 1 and Challenger 2:
1. **Sleep Schedule & Evaluation Collision (Section 4.4)**:
   - Reschedule the 90-minute sleep rotations so the Team Leader, Lead Backend Developer, and ML Lead are 100% alert and at the desk during the 01:00–04:00 AM Evaluation Round 2 window.
   - Move non-critical sleep slots to 22:30–01:00 AM and 04:15–06:45 AM, ensuring 4 awake desk sentinels at all times and a 15-minute wake-up/wash-face transition buffer before taking the jury.
2. **Ministry Curveball Tactical Upgrades (Section 4.2)**:
   - Add the **"Facade / JSONB Shadow Schema"** pattern for handling sudden structural DB pivots (fractional co-ownership, dynamic multi-tier DAG approvals) without breaking relational foreign keys during late-night rounds.
   - Add the **"Smartphone-as-Edge-Probe" MQTT Gateway** pattern for instantly satisfying surprise IoT/hardware requirements on software tracks using Web Bluetooth/Sensors and local MQTT brokers.
3. **Trunk-Based Micro-Branching Git Strategy (Section 5.3)**:
   - Upgrade the branching model to **Trunk-Based Micro-Branching** (lifespans <90 min, feature toggles, continuous rebasing/merging into `main`). This prevents catastrophic 05:00 AM merge conflicts and generates an authentic, distributed git log that passes rigorous evaluator git audits.
4. **Regulatory, Compliance & Financial Q&A Hardening (Section 6.4)**:
   - Upgrade Aadhaar handling from simple SHA-256 to **UIDAI Paperless Offline XML e-KYC & Secure QR Code Verification** to strictly comply with UIDAI statutory regulations.
   - Expand DPDP Act 2023 defense with the **Electronic Consent Artefact**, purpose limitation, right to erasure, and Data Protection Board of India compliance.
   - Replace naive "zero cost" claims with an **Itemized MeghRaj Cloud / State Data Centre (SDC) Monthly Bill of Materials (~₹12,500/mo)** breaking down 4 vCPU/16GB RAM VMs, managed PostgreSQL/PostGIS, S3 storage, and NIC-grade SSL endpoints.
   - Include the **Legacy NIC SOAP 1.2 / WS-Security Proxy Adapter** pattern for seamless integration with legacy government backends without breaking ancient XML endpoints.
5. **Docker Offline Cache & MinIO Healthcheck Alignment (Sections 3.3 & 6.2)**:
   - Fix Section 3.3 offline cache bundle command to explicitly pull `postgis/postgis:16-3.4-alpine` (matching `docker-compose.yml` in Section 6.2).
   - Fix MinIO healthcheck in `docker-compose.yml` to use `["CMD-SHELL", "mc ready local || exit 1"]` or native TCP socket probe rather than relying on `curl` in distroless images.

### Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. Maintain full completeness, verified depth, and zero placeholders.
