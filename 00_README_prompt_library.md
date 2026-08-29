# SIH26002 Prompt Library — Index

This is a set of ready-to-use, engineered prompts (for Claude, ChatGPT, or any coding assistant) covering every phase of the project from the roadmap. Each file is scoped to one team member's track so you can work in parallel without stepping on each other.

| File | Owner | Covers |
|---|---|---|
| `member_A_ml_prompts.md` | Member A (ML/Data) | Feature engineering, XGBoost model, SHAP, model API |
| `member_B_backend_routing_prompts.md` | Member B (Backend/Routing) | PostGIS/pgRouting or OSRM, FastAPI, dynamic edge weights, sync endpoints |
| `member_C_frontend_mobile_prompts.md` | Member C (Frontend/Mobile) | Next.js dashboard, Flutter/PWA field app, offline-first sync UI |
| `shared_integration_demo_prompts.md` | All | End-to-end testing, README, architecture diagram, pitch deck, demo script |

## How to use these prompts

1. Copy a prompt as-is into your AI assistant of choice.
2. Fill in any `[bracketed placeholder]` with your actual details (district name, table names, file paths, etc.) before sending.
3. Prompts are ordered to match the roadmap phases (0 → 5) — do them in order within your file, since later prompts assume earlier outputs exist.
4. Every prompt already bakes in the "no GPU / lightweight" constraint from our architecture decision, so you don't need to repeat it yourself.
5. If a response is too generic, add: *"Be specific to the SIH26002 NER landslide/logistics use case, not a generic example."*

## General prompting tips applied throughout this library

- Each prompt states **role + context + task + constraints + output format** — the same structure the assistant is asked to follow every time, which keeps outputs consistent across all three members.
- Prompts ask for **step-by-step reasoning before code** where correctness matters (e.g., the ML training prompt), since that reliably produces better code than "just write the code."
- Prompts specify **exact file/function names** matching our architecture doc, so outputs from different prompts plug into each other without renaming.
