<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 13 — Projects

**Owns:** capstone and integration builds. A top-level stage folder: projects are *applications* of many topics, not a topic.

16 projects, flat — one folder per project, no grouping parent. That flatness is an explicit decision that survived the count passing 10.

Full-stack capstones: `LangGraph_Fullstack_Capstone/` (FastAPI + Angular + Postgres + unit tests + Streamlit apps), `LangChain_Microservices_Capstone/` (Docker, k8s-style manifests, frontend).
Enterprise platforms (moved here from interview prep on 2026-09-19 — they had CODE trees and dependency manifests, so they were applications misfiled as prep): `Enterprise_Multi_Agent_AI_Research_Platform/`, `Enterprise_Agentic_Workflow_Automation_Platform/`, `Enterprise_RAG_Platform/`.
`Building_Adaptive_RAG/` arrived the same day from `03_Advanced/08_Advanced_RAG/building-adaptive-rag/` by the same test — 25 `.py` files, `src/`, `tests/`, `main.py`, `requirements.txt`, zero notebooks. It is the only project here with no notebook, which is expected: it is a CLI app.

## Conventions here

- **One venv per project.** 16 dependency manifests live here and some genuinely conflict (CrewAI's `chromadb<1.2` vs `langchain-chroma` 1.1). There is deliberately no root manifest for this phase.
- No `helpers` usage — projects instantiate their own clients, as deployable apps should.
- Every project should carry a `README.md` with Problem → Architecture → Stack → Run → Demo, plus a `.env.example`.
- `pyproject.toml`'s ruff `extend-exclude` hardcodes JS frontend paths under this phase. **Add a new entry if you add another JS app.**

## Running

```bash
cd 05_Projects/LangGraph_Fullstack_Capstone/fullstackapp && docker compose up
# backend :8000 · frontend :5555 · postgres :5433
cd 05_Projects/LangGraph_Fullstack_Capstone/unit_tests && pytest
```
