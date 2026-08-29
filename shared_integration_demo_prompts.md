# Shared Prompts — Integration, Testing, Docs & Pitch

Use these together, once each member's individual pieces (from their own prompt file) are working.

---

### Prompt 1 — End-to-end integration test script

```
Write a Python script (using requests + pytest) that simulates the full
pipeline for a demo:
1. POSTs a synthetic rainfall spike to the ML feature pipeline for
   segment_id "DEMO_001".
2. Calls the ML /predict endpoint and asserts hazard_probability rises
   above 0.70.
3. Triggers Member B's dynamic-cost update job.
4. Calls /route-safe between two demo points and asserts the returned
   route does NOT include segment "DEMO_001".
5. Submits a crowdsource "clear" report for DEMO_001 via /sync/up and
   asserts a follow-up /predict or override reduces its effective cost.

This becomes your live demo script too — narrate each assert as a step
in front of the judges.
```

---

### Prompt 2 — README generator

```
Write a project README.md with these sections: Problem Statement (2-3
sentences), Architecture diagram (ASCII, based on our 5-tier design:
Presentation / API Gateway / Ingestion / ML+Routing / Persistence),
Tech Stack table, Setup Instructions (assume Docker Compose with
services: postgres+postgis, fastapi-backend, ml-service, frontend), How
to Run the Demo, and Team & Roles. Keep it under 500 words excluding
the diagram and setup commands — judges skim READMEs.
```

---

### Prompt 3 — Docker Compose for one-command demo setup

```
Write a docker-compose.yml with services: postgres (postgis/postgis
image, with a volume and init SQL for our schema), ml-service (FastAPI,
exposes /predict), backend (FastAPI, exposes /route-safe and
/sync/*), and frontend (Next.js). Include healthchecks and correct
service dependency ordering (backend waits for postgres to be healthy).
Add comments on how to swap in OSRM as an additional service if we
choose that path over pgRouting.
```

---

### Prompt 4 — Architecture diagram description for slides

```
Turn our 5-tier architecture (Presentation / API Gateway / Ingestion /
ML+Routing / Persistence, with Kafka-style event flow from weather+IoT
sources through feature engineering to hazard scoring to edge-cost
mutation to routing) into a clean, presentation-ready diagram
description I can hand to a designer or draw myself in draw.io/Mermaid.
Output as Mermaid flowchart syntax so I can render it directly.
```

---

### Prompt 5 — Pitch deck outline

```
Write a 10-slide SIH pitch deck outline for SIH26002 covering: Problem
(with a concrete NER stat), Existing Gap, Our Solution (one sentence),
Architecture (diagram slide), ML Model (feature list + PR-AUC/Recall
metric slide), Offline-First Field App (why it matters for NER
specifically), Tech Stack (emphasize zero-GPU / low-cost deployability),
Demo screenshot slide, Impact (SDMA/NDRF, cold-chain, NHIDCL/BRO,
commercial fleets — one line each), and Team & Next Steps. For each
slide give a 1-sentence speaker note, not full paragraphs.
```

---

### Prompt 6 — Judge Q&A prep

```
Based on our architecture (XGBoost hazard model, PostGIS/pgRouting or
OSRM, offline-first Flutter field app, no GPU anywhere), generate the
10 toughest questions a SIH panel of judges might ask about this
project — covering data availability, model accuracy/false negatives,
scalability, offline sync reliability, and real-world deployment with
GSI/NDMA — and draft a 2-3 sentence answer for each.
```
