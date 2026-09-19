# 05 — Projects

**Status:** ✅ Built — 16 projects, 32 notebooks.

Capstone/integration projects combining multiple frameworks and competencies from earlier groups. A top-level group because projects are *applications* of many topics, not a topic themselves.

Flat by design: one folder per project, no grouping parent, even as the count passed ten.

**Prerequisites: varies by project** — most assume `02_Core/`, several assume `03_Advanced/`.

## Full-stack capstones

**`LangGraph_Fullstack_Capstone/`** ✅
- FastAPI + Angular + PostgreSQL
- Human-in-the-loop workflows
- Unit tests
- Streamlit apps

**`LangChain_Microservices_Capstone/`** ✅
- LangChain deployed as microservices
- Docker
- k8s-style manifests
- Frontend

## Enterprise platforms

**`Enterprise_RAG_Platform/`** ✅
- Enterprise RAG reference build with its own code tree

**`Enterprise_Multi_Agent_AI_Research_Platform/`** ✅
- Multi-agent research platform
- Includes a TensorZero reference stack

**`Enterprise_Agentic_Workflow_Automation_Platform/`** ✅
- Agentic workflow automation reference build

## Applied builds

**`RAG_Systems_Projects/`** ✅ — 7 applied RAG capstone notebooks
- Document search engine
- Multi-user conversational RAG
- Multimodal RAG
- Q&A systems

**`ShopUNow_Agentic_RAG_Capstone/`** ✅
- Vector DB + agentic RAG e-commerce capstone
- Architecture PPTX and walkthrough

**`Building_Adaptive_RAG/`** ✅ — the one project with no notebook; it is a CLI app
- Adaptive RAG (query routing → retrieve → grade → generate → self-correct) as a deployable package
- `src/{cli,models,workflow}/`, `main.py`, `tests/test_chains.py`, own `requirements.txt`

**`AI_Powered_Customer_Support/`** ✅
- Full-stack customer support agent
- Docker, tests, notebooks

**`Automated_Candidate_Interview_Evaluation_System/`** ✅
- AutoGen AgentChat mock interview
- FastAPI / WebSocket
- Groq, deployed on Render
- Architecture diagrams

**`End_to_End_Medical_Chatbot/`** ✅
- Flask + Pinecone medical RAG chatbot
- Groq LLM
- Docker / AWS CI/CD
- Databricks Apps deploy
- Architecture diagrams

**`Personalized_Holiday_Management_Agent/`** ✅
- FastAPI + AutoGen AgentChat holiday planner
- Planner + researcher team

**`Resume_Genie/`** ✅ — Streamlit + LangGraph career suite
- Scoring
- Cover letters
- ATS check
- Agentic chat

**`Realtime_Voice_AI_Agent_with_RAG/`** ✅
- Real-time voice AI agent with RAG

**`Realtime_Source_Code_Analyzer/`** ✅
- Real-time source code analyzer

**`Pipecat_QuickStart/`** ✅
- Real-time voice AI quickstart (Pipecat)

## Provenance

- Most of the standalone apps came from `AgenticAI_Projects_Demystified`
- `Personalized_Holiday_Management_Agent/` and `Resume_Genie/` came from their own GitHub repos
- The three `Enterprise_*` platforms moved here on 2026-09-19 from what was Phase 16 — they had code trees and dependency manifests, so they were applications misfiled under interview prep
- `Building_Adaptive_RAG/` moved here the same day from `03_Advanced/08_Advanced_RAG/building-adaptive-rag/` (originally from `RAG_Demystified`) by the same test — Phase 8 keeps the adaptive-RAG *topic* in `Agentic_RAG/`'s notebooks; this is its deployable form
- See also `README_Full_Stack_Projects.md` — the source repo's own overview of the earlier full-stack set

## Running a project

**One virtual environment per project** — there is deliberately no shared manifest here. Several projects have genuinely conflicting pins (CrewAI's `chromadb<1.2` against `langchain-chroma` 1.1), so a single lock would be a lie.

```bash
cd 05_Projects/<project>
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt     # or: uv pip install -e .
cp .env.example .env                   # then fill in keys
```

```bash
# the flagship capstone
cd 05_Projects/LangGraph_Fullstack_Capstone/fullstackapp && docker compose up
# backend :8000 · frontend :5555 · postgres :5433
cd 05_Projects/LangGraph_Fullstack_Capstone/unit_tests && pytest
```

Each project should carry a README with **Problem → Architecture → Stack → Run → Demo**. If one doesn't, that's a gap worth filling — these are the folders a reviewer actually opens.
