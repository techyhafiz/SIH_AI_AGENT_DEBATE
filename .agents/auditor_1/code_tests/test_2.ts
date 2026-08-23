+---------------------------------------------------------------------------------------------------+
|                                 THE 5-CATEGORY JURY Q&A MATRIX                                    |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
| CATEGORY 1: SCALABILITY & CONCURRENCY                                                             |
| - Jury Question: "How will your system handle 2 million concurrent users during peak deadline?"   |
| - Defense Script: "Sir, our backend is stateless and horizontally scalable behind an Nginx load   |
|   balancer. By utilizing Redis for session caching and offloading heavy batch writes to an async  |
|   BullMQ/Celery worker queue, PostgreSQL connection pools remain unblocked under high load."      |
|                                                                                                   |
| CATEGORY 2: SECURITY, PRIVACY & DPDP ACT 2023                                                     |
| - Jury Question: "Are you storing citizen Aadhaar numbers? How is citizen privacy protected?"     |
| - Defense Script: "We strictly adhere to UIDAI circulars and the DPDP Act 2023. We NEVER store raw|
|   12-digit Aadhaar numbers. The client immediately computes a salted SHA-256 hash and retains only|
|   the masked last 4 digits (`XXXX-XXXX-1234`) alongside an ephemeral JWT token."                 |
|                                                                                                   |
| CATEGORY 3: LEGACY GOVERNMENT SYSTEMS & NIC INTEGRATION                                           |
| - Jury Question: "How does this integrate with existing legacy NIC databases (e.g., ServicePlus)?"|
| - Defense Script: "Our API gateway is built on open REST/JSON and Beckn Protocol specifications,  |
|   supporting standard NIC e-Gov OAuth2 connectors and XML/SOAP adapter middleware."               |
|                                                                                                   |
| CATEGORY 4: RURAL ADOPTION & DIGITAL LITERACY                                                     |
| - Jury Question: "How does an illiterate farmer with a feature phone use this?"                   |
| - Defense Script: "We provide two dedicated channels: First, a voice-driven interface in 12 Indic |
|   languages via Bhashini. Second, an automated SMS/IVRS gateway where a citizen simply dials a     |
|   toll-free number or sends an SMS code, requiring zero smartphone ownership."                    |
|                                                                                                   |
| CATEGORY 5: DEPLOYMENT COST & BUDGET ROI                                                          |
| - Jury Question: "What is the capital expenditure (CapEx) to deploy this statewide?"              |
| - Defense Script: "Because our architecture uses open-source components (PostgreSQL, FastAPI,     |
|   Linux containers) and localized edge inference, there are zero proprietary SaaS recurring fees. |
|   It deploys directly onto existing State Data Centre (SDC) virtual machines."                    |
+---------------------------------------------------------------------------------------------------+
