CONTENT = """# PART 4: PHASE 4 — THE 36-HOUR NODAL CENTER BATTLEFIELD & EVALUATION CYCLES

The 36-Hour Grand Finale at the nodal center is an intense physical, intellectual, and psychological pressure cooker. Between the opening bell at 08:00 AM on Day 1 and the closing evaluations on Day 2, teams must navigate three distinct judging rounds, survive severe sleep deprivation, and adapt to sudden ministerial curveballs.

---

## 4.1 The Master 0h–36h Hour-by-Hour Battle Timeline

```
+---------------------------------------------------------------------------------------------------+
|                            THE 36-HOUR NODAL CENTER MASTER SCHEDULE                               |
+---------------------------------------------------------------------------------------------------+
|  DAY 1: FOUNDATION & THE REALITY CHECK                                                            |
|  08:00 - 10:00 (Hour 00-02) : Arrival, Registration, Desk Setup, Spike Buster Wiring, Docker Up. |
|  10:00 - 13:00 (Hour 02-05) : Sprint 1 (Foundation): Seed DB, Scaffold REST Routes, Setup UI.     |
|  13:00 - 14:00 (Hour 05-06) : Lunch & Strategy Alignment.                                         |
|  14:00 - 18:00 (Hour 06-10) : EVALUATION ROUND 1 (Mentoring & Architecture Review).                |
|  18:00 - 21:00 (Hour 10-13) : Sprint 2 (The Curveball Sprint): Implement R1 Mentor Feedback.      |
|  21:00 - 22:30 (Hour 13-14.5): Dinner, Strategy Sync & Pre-Graveyard Shift Briefing.              |
|                                                                                                   |
|  NIGHT 1 / DAY 2: THE GRAVEYARD SHIFT & ROUND 2 HARDENING                                         |
|  22:30 - 01:00 (Hour 14.5-17): Sleep Rotation Shift 1 (Pair A: Frontend Lead + Co-Presenter).    |
|                                4 Active Desk Sentinels (TL, Backend Lead, ML Lead, DevOps).      |
|  01:00 - 04:00 (Hour 17-20) : ALL-HANDS BATTLE STATIONS — EVALUATION ROUND 2                      |
|                                (Midnight Pressure Test, Live PostgreSQL Inspection & Edge Audits)|
|                                *TL, Backend Lead, and ML Lead 100% ALERT AT DESK*.                |
|  04:15 - 06:45 (Hour 20.25-22.75): Sleep Rotation Shift 2 (Pair B: Backend Lead + DevOps Lead).   |
|                                (TL & Pitcher Power-Nap 04:30 - 06:00 AM; 4 Sentinels on Desk).    |
|  06:00 SHARP   (Hour 22)    : HARD FEATURE FREEZE (Zero New Features Permitted Under Any Reason). |
|                                                                                                   |
|  DAY 2: POLISH, SAFETY NET & THE GRAND FINALE                                                     |
|  06:00 - 09:00 (Hour 22-25) : UI Polish, Seeding Realistic Data, Resetting DB to Clean State.     |
|  09:00 - 10:00 (Hour 25-26) : Breakfast, Shower / Face-Wash & Team Mental Reset.                  |
|  10:00 - 10:30 (Hour 26-26.5): 1080p OBS Screen Recording Safety Net Captured in Uncut MP4.       |
|  10:30 SHARP   (Hour 26.5)  : Strategic Morning Caffeine Intake (90 min pre-pitch peak).         |
|  10:30 - 12:00 (Hour 26.5-28): Pitch Rehearsals & Anti-Tokenism Cross-Examination Drills.         |
|  12:00 - 16:00 (Hour 28-32) : FINAL EVALUATION POWER ROUND (The Make-or-Break Jury Pitch).         |
|  16:00 - 19:00 (Hour 32-35) : Jury Deliberations & Consolidation of Scores.                       |
|  19:00 - 20:00 (Hour 35-36) : Valedictory Ceremony & Victory Announcements.                      |
+---------------------------------------------------------------------------------------------------+
```

---

## 4.2 Round 1 Mentoring: The Reality Check & The 4-Step "Ministry Curveball" Playbook

Round 1 typically occurs between **14:00 and 18:00 on Day 1**. Mentors (a mix of Ministry officials and industry engineers) visit your desk.

### The Purpose of Round 1
Mentors do not expect a fully finished application in Round 1. They are evaluating:
1. **Architecture Viability**: Is your database schema normalized? Is your backend modular?
2. **Domain Understanding**: Do you understand the Ministry's real-world operating hierarchy?
3. **The Litmus Test for Pre-Built Code**: To prevent teams from simply downloading a pre-existing project and presenting it unchanged, mentors deliberately throw a **"Ministry Curveball"** — an unannounced requirement or operational pivot.

### Common Examples of the "Ministry Curveball"
- *"Your subsidy disbursement portal looks good, but agricultural land in this state is frequently co-owned fractionally by 4 family members. Can your database handle dynamic multi-party fractional co-ownership and dynamic multi-tier approval DAGs?"*
- *"We don't just need a web dashboard. Can you prove right now that your system ingests real physical sensor telemetry (e.g. soil moisture, ambient vibration, GPS cold-chain tracking) over IoT protocols rather than static fake inputs?"*
- *"What happens if the District Collector wants to reassign an inspection ticket to a sub-divisional officer with a 48-hour SLA countdown timer?"*

```
+-----------------------------------------------------------------------------------------------+
|                       THE 4-STEP TACTICAL CURVEBALL RESPONSE PLAYBOOK                         |
+-----------------------------------------------------------------------------------------------+
|                                                                                               |
|  STEP 1: ACTIVE VALIDATION & EMPATHY (Never Argue or Say "That's Out of Scope")               |
|  - Incorrect Response: "Sir, that was not in the original PDF problem statement." (Death sentence) |
|  - Correct Response: "Sir, that is a fantastic insight into the ground operational reality.   |
|    We completely understand why fractional co-ownership and dynamic DAG approvals are vital." |
|                                                                                               |
|  STEP 2: MODULAR ARCHITECTURAL MAPPING (During Sprint 2: 18:00 - 21:00)                       |
|  - Do NOT rewrite your entire backend. Map the curveball into your existing architecture      |
|    using Battle-Tested Tactical Patterns (JSONB Shadow Schemas & MQTT Gateways).              |
|                                                                                               |
|  STEP 3: PROTOTYPE LITE & SEED REALISTIC DATA                                                 |
|  - Build a clean UI card or dashboard toggle representing the feature with realistic data.   |
|                                                                                               |
|  STEP 4: THE ROUND 2 SHOWCASE HOOK                                                            |
|  - When the evaluator returns in Round 2, open with:                                          |
|    "Sir, you gave us invaluable feedback in Round 1 regarding fractional co-ownership DAGs.   |
|    We prioritized that during Sprint 2. Let us show you the live automated approval engine."  |
|  - Result: Evaluator feels personal ownership of your solution and gives maximum score.      |
+-----------------------------------------------------------------------------------------------+
```

---

### Tactical Curveball Upgrade 1: The "Facade / JSONB Shadow Schema" Pattern
When evaluators demand sudden structural database rewrites (e.g., dynamic multi-tier DAG approvals, fractional co-ownership, or polymorphic inspection fields), **never execute destructive SQL migrations** (`ALTER TABLE DROP/ADD COLUMN`) late at night. Modifying Prisma/SQLAlchemy models mid-hackathon invariably breaks foreign key constraints, crashes ORM relations, and causes API routes to throw HTTP 500 errors.

Instead, implement the **JSONB Shadow Schema & Facade Pattern**:
1. Every core relational table is created upfront with an extensible `metadata JSONB DEFAULT '{}'::jsonb` column and a GIN index.
2. Complex, unexpected nested entities (like dynamic approval DAG nodes or fractional co-owners) are persisted directly into `metadata` without altering the rigid relational table structure.
3. A lightweight Pydantic / TypeScript facade validates and exposes these dynamic structures over dedicated REST endpoints.

```sql
-- 1. Upfront Extensible PostgreSQL Schema with GIN Indexing
CREATE TABLE subsidy_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_number VARCHAR(64) UNIQUE NOT NULL,
    applicant_name VARCHAR(255) NOT NULL,
    base_amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(32) DEFAULT 'PENDING_REVIEW',
    -- Extensible JSONB column for late-night structural pivots:
    metadata JSONB DEFAULT '{
        "fractional_owners": [],
        "approval_dag": {
            "current_step": 1,
            "total_steps": 3,
            "steps": [
                {"step_id": 1, "role": "VILLAGE_PATWARI", "status": "APPROVED", "timestamp": "2026-08-23T14:30:00Z"},
                {"step_id": 2, "role": "TEHSILDAR", "status": "PENDING", "sla_hours_remaining": 36},
                {"step_id": 3, "role": "DISTRICT_COLLECTOR", "status": "LOCKED", "sla_hours_remaining": 72}
            ]
        }
    }'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- GIN index enables sub-millisecond JSONB query performance for evaluators:
CREATE INDEX idx_subsidy_metadata_gin ON subsidy_applications USING GIN (metadata);
```

```python
# 2. FastAPI Pydantic Facade for Late-Night Dynamic Curveballs
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncpg

class FractionalOwner(BaseModel):
    name: str
    relation: str
    share_percentage: float = Field(..., ge=1.0, le=100.0)
    aadhaar_ref_id: str

class DAGApprovalStep(BaseModel):
    step_id: int
    role: str
    status: str
    sla_hours_remaining: int

class CurveballUpdatePayload(BaseModel):
    fractional_owners: Optional[List[FractionalOwner]] = None
    approval_dag_steps: Optional[List[DAGApprovalStep]] = None

@app.patch("/api/v1/applications/{app_id}/curveball-update")
async def update_application_curveball(
    app_id: str,
    payload: CurveballUpdatePayload,
    db_pool = Depends(get_db_pool)
):
    # Safely integrates surprise evaluator DAGs or fractional ownership
    # into the JSONB shadow schema without modifying relational foreign keys.
    async with db_pool.acquire() as conn:
        record = await conn.fetchrow("SELECT metadata FROM subsidy_applications WHERE id = $1", app_id)
        if not record:
            raise HTTPException(status_code=404, detail="Application not found")
        
        current_meta = record["metadata"]
        if payload.fractional_owners is not None:
            current_meta["fractional_owners"] = [owner.dict() for owner in payload.fractional_owners]
        if payload.approval_dag_steps is not None:
            current_meta["approval_dag"]["steps"] = [step.dict() for step in payload.approval_dag_steps]
            
        await conn.execute(
            "UPDATE subsidy_applications SET metadata = $1 WHERE id = $2",
            current_meta, app_id
        )
        return {"status": "SUCCESS", "updated_metadata": current_meta}
```

---

### Tactical Curveball Upgrade 2: The "Smartphone-as-Edge-Probe" MQTT Gateway
When an evaluator on a software track demands: *"This is just a static web simulation. How do you prove this handles live physical hardware sensor feeds (e.g. soil moisture, ambient vibration, GPS cold-chain tracking)?"*, do not panic or scramble to find Arduino boards.

**The Solution**: Turn any team member's smartphone into a real-time hardware IoT edge probe streaming live telemetry over MQTT to your local Docker stack.

```
+---------------------------------------------------------------------------------------------------+
|                        SMARTPHONE-AS-EDGE-PROBE ARCHITECTURE                                      |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [ PHYSICAL HARDWARE PROBE ]                                                                      |
|  Team Member's Android / iPhone                                                                   |
|  - HTML5 Web Sensors API or Free "MQTT Sensors" Mobile App                                        |
|  - Captures Real Physical Sensors: Accelerometer, Gyroscope, Ambient Light, GPS Coordinates       |
|                                         |                                                         |
|                                         v (Local Wi-Fi Hotspot / USB Tether: Port 1883)           |
|                                                                                                   |
|  [ LOCAL MQTT BROKER ]                                                                            |
|  Dockerized Eclipse Mosquitto Container (`eclipse-mosquitto:2.0-alpine`)                         |
|  - Ingests MQTT topic: `sih/sensors/telemetry/device_01`                                          |
|                                         |                                                         |
|                                         v (Sub-10ms Ingest Stream)                                |
|                                                                                                   |
|  [ BACKEND ASYNC INGESTION & WEBSOCKET ENGINE ]                                                   |
|  FastAPI + `asyncio-mqtt` Background Task                                                         |
|  - Enriches sensor payloads -> Broadcasts WebSocket events to Next.js UI                         |
|                                         |                                                         |
|                                         v (Live UI Graph Updates)                                 |
|                                                                                                   |
|  [ LIVE DASHBOARD OSCILLOSCOPE ]                                                                  |
|  Evaluator physically lifts or shakes the phone on the desk -> Real-time graph spikes live!       |
+---------------------------------------------------------------------------------------------------+
```

#### Step-by-Step Edge Probe Deployment:
1. Add Eclipse Mosquitto to `docker-compose.yml`:
   ```yaml
   mosquitto:
     image: eclipse-mosquitto:2.0-alpine
     container_name: sih_mosquitto
     ports:
       - "1883:1883"
       - "9001:9001"
     volumes:
       - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
   ```
2. Configure `mosquitto.conf`:
   ```text
   listener 1883
   allow_anonymous true
   ```
3. Open a lightweight HTML5 sensor probe on the mobile browser (`http://<laptop_ip>:3000/probe.html`):
   ```html
   <script>
     // HTML5 Device Motion Sensor -> Streams real phone physics over WebSocket
     const ws = new WebSocket('ws://' + window.location.hostname + ':8000/ws/telemetry');
     window.addEventListener('devicemotion', (event) => {
       const payload = {
         accel_x: event.accelerationIncludingGravity.x || 0,
         accel_y: event.accelerationIncludingGravity.y || 0,
         accel_z: event.accelerationIncludingGravity.z || 0,
         timestamp: Date.now()
       };
       if (ws.readyState === WebSocket.OPEN) {
         ws.send(JSON.stringify(payload));
       }
     });
   </script>
   ```
4. **The Live Demo Kill Shot**: When the evaluator visits, hand them the smartphone: *"Sir, tilt this phone to simulate a grain silo tipping or a cold-chain truck accelerating."* As they tilt the phone, the dashboard needle moves in real time with 15ms latency. The evaluator's "fake simulation" objection is instantly annihilated.

---

## 4.3 Round 2 Midnight Pressure Tests (01:00–04:00 AM Graveyard Shift)

Round 2 occurs in the dead of night. Evaluators are tired, caffeinated, and irritable. They have visited 20 desks and have zero patience for fluff or slideshows.

### Evaluator Mindset & Midnight Scrutiny
- **Zero Tolerance for Slides**: If you open a PowerPoint presentation at 02:00 AM, the evaluator will close your laptop lid. **Show running software immediately.**
- **Live Database Inspection**: Evaluators will ask you to perform a real-time transaction on the frontend (e.g., submit a form or trigger an alert) and then say: *"Show me the new row in PostgreSQL right now."* If your database is hardcoded or mocked, you are eliminated on the spot.
- **Edge-Case Grilling**: *"What happens if I upload a corrupted 50MB PDF?"*, *"What happens if the GPS coordinate is outside India?"*, *"How does your system handle two officers approving the same claim simultaneously?"*

### Tactical Rules for Surviving Round 2:
1. Keep the developer tools console open (`F12`) and a PostgreSQL GUI / terminal (`psql` or pgAdmin) open on a split screen.
2. Demonstrate error handling gracefully (e.g., toast notifications: "Invalid Aadhaar format", "File exceeds 5MB limit").
3. **Mandatory Attendance**: The Team Leader, Lead Backend Developer, and ML Lead MUST be fully awake and at the desk during this entire window.

---

## 4.4 Team Energy, Caffeine Pharmacokinetics, Rotational Sleep Schedule & Red Phone Sentinel Protocol

A team that attempts to stay awake for 36 continuous hours without structured sleep will suffer severe cognitive degradation, memory lapses, and catastrophic 05:00 AM git merge errors.

```
+-----------------------------------------------------------------------------------------------+
|                       THE HARDENED ROTATIONAL SLEEP & DESK SENTINEL SYSTEM                    |
+-----------------------------------------------------------------------------------------------+
|                                                                                               |
|  * The 90-Minute Circadian Ultradian Cycle:                                                   |
|    - Human sleep cycles last exactly ~90 minutes (NREM Stage 1-3 -> REM sleep).              |
|    - Waking up in the middle of deep Stage 3 sleep (e.g. after 45 minutes) causes severe       |
|      sleep inertia, grogginess, and mental fog. Sleeping for 90 or 150 minutes ensures you    |
|      wake up at the end of a REM cycle, alert and cognitively sharp.                          |
|                                                                                               |
|  * The Anti-Collision Schedule (Zero Overlap with Evaluation Round 2):                         |
|                                                                                               |
|    - 22:30 - 01:00 AM (Slot 1 - 2.5h): Pair A sleeps (Frontend Lead + Co-Presenter/Domain).   |
|      [4 Active at Desk: Team Leader, Backend Lead, ML Lead, Integration/DevOps Lead].         |
|                                                                                               |
|    - 01:00 - 04:00 AM : ALL-HANDS BATTLE STATIONS (EVALUATION ROUND 2 WINDOW).               |
|      *ALL 6 TEAM MEMBERS AWAKE & AT THE DESK*. Zero members in hostel/sleeping rooms.         |
|      (TL coordinates, Backend Lead runs queries, ML Lead defends inference latency).          |
|                                                                                               |
|    - 04:15 - 06:45 AM (Slot 2 - 2.5h): Pair B sleeps (Backend Lead + Integration/DevOps Lead).|
|      [4 Active at Desk: Team Leader, Frontend Lead, ML Lead, Co-Presenter Lead].              |
|                                                                                               |
|    - 04:30 - 06:00 AM (Slot 3 - 1.5h): Team Leader & Pitch Lead power-nap post-Round 2.       |
|                                                                                               |
|  * The 15-Minute Wake-up & Face-Wash Buffer:                                                  |
|    - NEVER step directly from a sleeping mattress to an evaluator conversation.               |
|    - Maintain a strict 15-minute wake-up buffer: splash cold water on face, use lubricating   |
|      eye drops, do a 60-second stretch, and review the current git branch status before       |
|      taking the desk.                                                                         |
|                                                                                               |
|  * The Caffeine Pharmacokinetics Protocol:                                                    |
|    - Half-life of caffeine is 5 to 6 hours. Consuming caffeine within 4 hours of a sleep shift|
|      blocks adenosine receptors, ruins sleep architecture, and triggers 05:00 AM crashes.     |
|    - CAFFEINE BAN: Strict caffeine prohibition between 20:00 and 04:00 AM for sleeping pairs.|
|    - Hydration Rule: Drink 500ml water with ORS (Oral Rehydration Salts) electrolytes every   |
|      4 hours to prevent dehydration-induced headaches and brain fog.                          |
|    - STRATEGIC MORNING PEAK: Take one cup of strong black coffee/tea at 10:30 AM on Day 2     |
|      (exactly 90 minutes before the 12:00 PM Final Evaluation Power Round) to ensure peak     |
|      synaptic firing and voice projection during the final pitch.                              |
|                                                                                               |
|  * The Desk Sentinel "Red Phone" Emergency Paging Protocol:                                   |
|    - At least 4 engineers MUST remain awake and active at the desk at all times.              |
|    - If an evaluator arrives unexpectedly while a teammate is in the rest area:               |
|      1. Sentinel 1 immediately greets the judge and initiates the introductory C4 Container   |
|         Architecture overview ("Welcome Sir, let us frame our problem and system design").    |
|      2. Sentinel 2 sends a single silent vibrating emergency alert via WhatsApp/SMS ("CODE 1").|
|      3. The resting member executes the 2-minute emergency wash-face transition and steps up  |
|         to the desk completely composed.                                                      |
+-----------------------------------------------------------------------------------------------+
```

---

## 4.5 The 06:00 AM Hard Feature Freeze & Dawn Stabilization Push

At **06:00 AM sharp on Day 2**, the Team Leader must enforce an absolute **Hard Feature Freeze**.

```
+-----------------------------------------------------------------------------------------------+
|                            06:00 AM HARD FEATURE FREEZE RULES                                 |
+-----------------------------------------------------------------------------------------------+
|  1. ZERO new feature branches or new UI routes may be created under any circumstances.        |
|  2. All short-lived micro-branches merged into `main` after a clean local smoke test.        |
|  3. Run the Database Reset & Seed Script: Wipe test junk records and seed 500+ clean,         |
|     realistic Indian demographic records (valid names, districts, phone numbers).             |
|  4. Fix all broken layout elements, visual overflow bugs, and mobile responsive glitches.    |
|  5. Ensure all local services (PostgreSQL, Redis, FastAPI, Next.js) start cleanly on a cold   |
|     machine reboot (`docker compose down && docker compose up -d`).                           |
+-----------------------------------------------------------------------------------------------+
```

---

## 4.6 The Final Evaluation Power Round & The 1080p OBS Safety Net Protocol

The Final Evaluation Round (typically between **12:00 PM and 16:00 PM on Day 2**) is the ultimate make-or-break crucible. You have exactly **5 minutes to pitch** followed by **3 to 5 minutes of intensive jury Q&A**.

### The 5-Minute Final Pitch Choreography

```
+-----------------------------------------------------------------------------------------------+
|                         THE 5-MINUTE POWER PITCH CHOREOGRAPHY                                 |
+-----------------------------------------------------------------------------------------------+
|                                                                                               |
|  MINUTE 00:00 - 01:00 : THE PROBLEM & THE 3-TIER PERSONA SETUP (Team Leader)                  |
|  - State the exact Ministry bottleneck with a hard-hitting statistic.                         |
|  - Introduce the 3 Personas: "Today we will walk you through our system through the eyes of    |
|    Ramesh (Citizen in Rural Bihar), Sunita (Field Verification Officer), and Dr. Verma        |
|    (Joint Secretary at Ministry HQ)."                                                         |
|                                                                                               |
|  MINUTE 01:00 - 03:00 : THE LIVE INTERACTIVE WORKFLOW DEMO (Lead Dev / Female Lead)          |
|  - Step 1: Citizen submits a claim on the mobile PWA in Hindi (demonstrating offline sync).   |
|  - Step 2: Field Officer receives real-time geo-fenced alert and approves with digital audit. |
|  - Step 3: Ministry Dashboard instantly updates with anomaly score from the local ML engine.  |
|                                                                                               |
|  MINUTE 03:00 - 04:00 : THE TECHNICAL FORTRESS & COMPLIANCE (System Architect)                |
|  - Show C4 Architecture diagram: Point out offline-first IndexedDB sync, local ONNX runtime,  |
|    PostGIS spatial queries, and DPDP Act 2023 Electronic Consent Artefact & Erasure engine.   |
|                                                                                               |
|  MINUTE 04:00 - 05:00 : UNIT ECONOMICS, SCALABILITY & MINISTRY ROADMAP (Presenter)           |
|  - Present itemized MeghRaj Cloud BOM (~₹12,500/mo) and 30-day sandbox pilot deployment plan. |
+-----------------------------------------------------------------------------------------------+
```

### The 1080p OBS Screen Recording Safety Net Protocol
One of the most devastating occurrences in hackathon history is when a team steps up to the jury podium, plugs in their HDMI cable, and their local server crashes or their browser hangs.

**The Mandatory Safety Net Protocol**:
1. At **10:00 AM on Day 2**, record a full, uncut, 1080p 60fps screen recording of your entire end-to-end user workflow using **OBS Studio** or QuickTime.
2. Walk through every feature, click every button, and show the database updating cleanly.
3. Keep this video file open in VLC Media Player minimized in the background.
4. **The Failover Rule**: If during the live jury demo, any network timeout or local script error occurs, the presenter smoothly transitions without flinching:
   *"While our local container finishes indexing this batch, let us show you this exact real-time execution recorded on our staging node 1 hour ago."*
   You switch to the video, narrate the workflow seamlessly, and save your team from total elimination.

---

## 4.7 Official Final 100-Point Scoring Rubric Breakdown

```
+-----------------------------------------------------------------------------------------------+
|                       OFFICIAL GRAND FINALE EVALUATION SCORING RUBRIC                         |
+-----------------------------------------------------------------------------------------------+
|  1. Innovation, Novelty & Real-World Uniqueness .................... [ 15 Points ]            |
|  2. Technical Complexity & Engineering Soundness .................... [ 25 Points ]            |
|     - Clean code, database normalization, API design, security.                               |
|  3. UI/UX, Accessibility & Multilingual Localization ............... [ 15 Points ]            |
|     - Indian Government design standards, high contrast, mobile responsiveness.              |
|  4. Scalability, Cost-Viability & Statutory DPDP Compliance ........ [ 20 Points ]            |
|     - Deployment economics, NIC compatibility, low infrastructure footprint.                  |
|  5. Live Working Prototype & R1 Mentoring Curveball Integration ..... [ 15 Points ]            |
|     - Evidence of active iteration during the 36 hours.                                       |
|  6. Team Presentation Dynamics, Cohesion & Defense in Q&A .......... [ 10 Points ]            |
|     - Active participation of all members; zero tokenism.                                     |
|                                                                                               |
|  TOTAL GRAND FINALE SCORE .......................................... [ 100 Points ]           |
+-----------------------------------------------------------------------------------------------+
```
"""