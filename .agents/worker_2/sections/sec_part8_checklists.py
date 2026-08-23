CONTENT = """# PART 8: BATTLE-TESTED CHECKLISTS & QUICK REFERENCE CARDS

This section provides compact, high-density operational checklists designed for instant reference by team leads, developers, and presenters before and during the hackathon.

---

## 8.1 Phase 1 & Phase 2 Gatekeeper Checklist

```
+---------------------------------------------------------------------------------------------------+
|                              PHASE 1 & PHASE 2 GATEKEEPER CHECKLIST                               |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
| [ PROBLEM STATEMENT SELECTION ]                                                                   |
| [ ] Verified PS Type: Prioritized Student Innovation / Workflow Automation over Generic ML traps. |
| [ ] Evaluated Competition Ratio: Selected PS with <15 expected national competitor teams.         |
| [ ] Verified Data Availability: Authenticated real CSV/JSON data sources on data.gov.in / OGD.     |
| [ ] Downloaded Ministry Annual Report, operational circulars, and identified target bureaucrat.   |
|                                                                                                   |
| [ COLLEGE INTERNAL SCREENING ]                                                                    |
| [ ] Built working 3-screen clickable prototype BEFORE internal college hackathon.                 |
| [ ] Sourced official college letterhead for NOC; confirmed SPOC portal nomination submission.     |
| [ ] Ensured strict 6-member roster compliance with at least 1 female team member.                 |
|                                                                                                   |
| [ CENTRAL PPT SHORTLISTING SUBMISSION ]                                                           |
| [ ] Strictly adhered to official 7-slide AICTE PowerPoint template structure.                    |
| [ ] Slide 3 features formal C4 Level 2 Container Architecture + DFD Level 1 diagrams.            |
| [ ] Slide 4 explicitly details feasible, air-gapped tech stack (PostgreSQL, FastAPI, Docker).    |
| [ ] Slide 5 includes detailed Risk & Mitigation matrix with DPDP Act 2023 compliance.            |
| [ ] Slide 6 contains quantitative ROI, turnaround time reduction %, and 3-tier persona impact.    |
| [ ] Exported crisp, high-resolution PDF (<10MB); verified formatting on multiple screens.        |
+---------------------------------------------------------------------------------------------------+
```

---

## 8.2 Phase 3 & 4 Battlefield Checklist

```
+---------------------------------------------------------------------------------------------------+
|                              PHASE 3 & 4 BATTLEFIELD CHECKLIST                                    |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
| [ PRE-HACKATHON HARDENING & LOGISTICS ]                                                           |
| [ ] Confirmed nodal center allocation on AICTE portal within 48-72 hours.                         |
| [ ] Booked train/flight tickets arriving 18-24 hours before Day 1, 08:00 AM.                      |
| [ ] Created offline Pip wheelhouse, NPM offline cache, and exported Docker images to SSD.        |
| [ ] Pre-pulled `postgis/postgis:16-3.4-alpine`, `redis:7.2-alpine`, and `minio/minio:latest`.    |
| [ ] Downloaded quantized GGUF / ONNX models and offline documentation docsets (Zeal/Dash).       |
| [ ] Prepared database seed script with 500+ realistic Indian demographic records.                 |
| [ ] Conducted full mock pitch and cross-examination drills with all 6 team members.              |
|                                                                                                   |
| [ 36-HOUR NODAL CENTER BATTLEFIELD ]                                                              |
| [ ] Set up desk with surge protector spike buster, Ethernet dongles, and local Docker stack.      |
| [ ] Actively welcomed Round 1 Mentoring curveballs; logged requirements verbatim in tracker.      |
| [ ] Enforced Trunk-Based Micro-Branching (<90 min lifespan) for mentor curveball features.        |
| [ ] Executed Round 2 Graveyard Shift Battle Stations (01:00-04:00 AM) with all core leads awake.  |
| [ ] Maintained 4 awake desk sentinels at all times; observed caffeine ban before sleep shifts.    |
| [ ] Executed HARD FEATURE FREEZE at 06:00 AM Day 2; zero new feature code merged.                 |
| [ ] Executed Forensic Git Audit Suite (`git shortlog -sn --all`) to ensure balanced commits.      |
| [ ] Recorded 1080p OBS uncut screen recording safety net video at 10:00 AM Day 2.                 |
| [ ] Took 10:30 AM strategic morning caffeine dose for peak alertness during the final pitch.      |
| [ ] Delivered disciplined 5-minute 3-tier persona pitch with balanced technical defense.          |
+---------------------------------------------------------------------------------------------------+
```

---

## 8.3 Hardware & Packing Checklist

```
+---------------------------------------------------------------------------------------------------+
|                               HARDWARE & PACKING ESSENTIALS CHECKLIST                             |
+---------------------------------------------------------------------------------------------------+
| [ ] 2x Surge-protected 6-socket Spike Busters with 3-meter heavy cords.                           |
| [ ] 2x 5-meter heavy-duty extension cords.                                                        |
| [ ] 4x USB-C / USB-A to RJ45 Gigabit Ethernet adapters + 4x Cat6 Ethernet patch cables.           |
| [ ] 2x 65W+ GaN fast laptop power banks.                                                          |
| [ ] 2x 1TB+ NVMe External SSDs with Docker images, pip wheels, and datasets.                      |
| [ ] Multi-carrier 5G backup phones (Airtel + Jio).                                                |
| [ ] HDMI cable + USB-C multi-port hub.                                                            |
| [ ] Multi-layer warm clothing (thermals, hoodie, beanie, socks) for cold December halls.         |
| [ ] Noise-canceling earplugs / headphones.                                                        |
| [ ] Medical kit: Eye drops, ORS sachets, Paracetamol, Antacids, Pain relief spray.                |
+---------------------------------------------------------------------------------------------------+
```

---

## 8.4 Emergency Troubleshooting Runbook

```
+---------------------------------------------------------------------------------------------------+
|                              EMERGENCY TROUBLESHOOTING RUNBOOK                                    |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
| SCENARIO 1: NODAL CENTER WI-FI CRASHES COMPLETELY                                                 |
| - Action: Immediately disconnect from venue Wi-Fi.                                                |
| - Plug into local Docker Compose stack on `localhost:3000` / `localhost:8000`.                    |
| - Verify `apiClient.ts` mock fallback switch is enabled. Everything runs 100% locally.            |
|                                                                                                   |
| SCENARIO 2: LIVE DEMO THROWS AN UNEXPECTED EXCEPTION DURING JURY EVALUATION                       |
| - Action: Presenter does NOT pause or apologize.                                                  |
| - Presenter immediately switches to the minimized 1080p OBS screen recording in VLC Player:       |
|   "While our local node completes background indexing, let us show you this exact real-time       |
|   transaction executed on our staging build."                                                     |
| - Narrate the uncut video smoothly without missing a beat.                                        |
|                                                                                                   |
| SCENARIO 3: JURY ACCUSES TEAM OF USING A PRE-BUILT STATIC TEMPLATE                                |
| - Action: Open terminal immediately.                                                              |
| - Run: `git log --graph --oneline --decorate --all -n 20`                                         |
| - Point out the dedicated branch: `feat/mentor-curveball-dag-approval` merged during Sprint 2.   |
| - Open PostgreSQL / `psql` console and run a live SQL `INSERT` query in front of the judge.       |
|                                                                                                   |
| SCENARIO 4: JURY CHALLENGES PUBLIC CLOUD COST & GOVERNMENT FEASIBILITY                            |
| - Action: Switch directly to Slide 6 / Documentation Appendix.                                    |
| - Present the itemized MeghRaj / State Data Centre Bill of Materials (~₹12,500/mo) based on       |
|   NICSI rate cards, proving an 88% OpEx reduction without claiming unrealistic "$0" costs.        |
+---------------------------------------------------------------------------------------------------+
```

---

## 8.5 Official Guidelines, Statutes & Bibliography

1. **Ministry of Education's Innovation Cell (MIC) & AICTE**: *Smart India Hackathon Official Operational Guidelines, Rules & Regulations (2020–2026).*
2. **Ministry of Law and Justice, Government of India**: *The Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023).*
3. **Unique Identification Authority of India (UIDAI)**: *Aadhaar (Authentication and Offline Verification) Regulations, 2019 & Circulars on Paperless Offline e-KYC.*
4. **Ministry of Electronics and Information Technology (MeitY)**: *Guidelines for Indian Government Websites (GIGW 3.0) & National Open Digital Ecosystem (NODE) Framework.*
5. **National Informatics Centre (NIC / NICSI)**: *Application Security, e-Governance Service Integration Standards & MeghRaj GI Cloud Rate Card.*
6. **Open Government Data (OGD) Platform India**: *National Data Sharing and Accessibility Policy (NDSAP) - data.gov.in.*
7. **Bhashini — National Language Translation Mission**: *MeitY Indic Language Speech & Machine Translation APIs Specification.*
8. **Beckn Protocol & Open Network for Digital Commerce (ONDC)**: *Decentralized Open Network Transaction Protocols Specification v1.1.*
"""