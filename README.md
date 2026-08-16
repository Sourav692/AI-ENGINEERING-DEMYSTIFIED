<div align="center">

# AI Engineering — End-to-End Roadmap

*A hands-on course covering agent frameworks, protocols, and cross-cutting AI engineering competencies — organized by learning phase, one topic per phase, no duplication.*

---

## Who Is This For?

| Level                                  | Start At                                                                 |
| --------------------------------------- | -------------------------------------------------------------------------- |
| **Complete beginner**, new to LangChain/prompting | [Phase 2: LangChain Fundamentals & Prompting](#phase-2--langchain-fundamentals--prompting) |
| **Know LangChain basics**, want agent graphs | [Phase 3: LangGraph Fundamentals](#phase-3--langgraph-fundamentals)      |
| **Know the frameworks**, want retrieval  | [Phase 4: Retrieval & RAG](#phase-4--retrieval--rag)                      |
| **Built basic RAG**, want to build agents | [Phase 5: AI Agent Fundamentals](#phase-5--ai-agent-fundamentals)         |
| **Built basic agents**, want multi-agent systems | [Phase 7: Advanced Agentic Systems](#phase-7--advanced-agentic-systems) |
| **Know agents**, want agentic/advanced RAG | [Phase 8: Advanced RAG](#phase-8--advanced-rag)                          |
| **Ready for production**                 | [Phase 12: Production & Observability](#phase-12--production--observability) or [Phase 13: Projects](#phase-13--projects) |
| **Exploring other frameworks/protocols** | Phases 1, 6, 9–11                                                        |

---

## Full Course Roadmap

The course is a sequence of **phases** — each owns exactly one topic, so there's a single place to learn any given thing. Where a topic has framework-specific implementations, they sit as clearly labeled sibling tracks *inside* that phase (e.g. Phase 4 has both `RAG_with_LangGraph/` and `RAG_with_LangChain/`) — never split across two different phases.

| # | Phase | Status |
|---|---|---|
| 1 | [Theory & Foundations](#phase-1--theory--foundations) *(optional, compressible)* | ✅ Partially built |
| 2 | [LangChain Fundamentals & Prompting](#phase-2--langchain-fundamentals--prompting) | ✅ Built |
| 3 | [LangGraph Fundamentals](#phase-3--langgraph-fundamentals) | ✅ Built |
| 4 | [Retrieval & RAG](#phase-4--retrieval--rag) *(foundational)* | ✅ Built |
| 5 | [AI Agent Fundamentals](#phase-5--ai-agent-fundamentals) | ✅ Built |
| 6 | [Agent SDKs (First-Party)](#other-phases-planned) | 🚧 Planned |
| 7 | [Advanced Agentic Systems](#phase-7--advanced-agentic-systems) | ✅ Built |
| 8 | [Advanced RAG](#phase-8--advanced-rag) *(needs Phases 5 & 7 first)* | ✅ Built |
| 9 | [Agent Protocols](#phase-9--agent-protocols) *(MCP, ACP, A2A)* | ✅ Partially built |
| 10 | [Alternative Agent Frameworks](#phase-10--alternative-agent-frameworks) *(DSPy, CrewAI, PydanticAI, AutoGen)* | ✅ Partially built |
| 11 | [Claude Code & AI Coding Tools](#other-phases-planned) | 🚧 Planned |
| 12 | [Production & Observability](#phase-12--production--observability) | ✅ Partially built |
| 13 | [Projects](#phase-13--projects) | ✅ Built |

> For the complete, up-to-date notebook-by-notebook listing, see [`NOTEBOOK_INDEX.md`](NOTEBOOK_INDEX.md) — it's the source of truth for what actually exists.

**Why RAG is split across two phases, not duplicated:** Phase 4 covers *foundational* RAG (chunking, basic retrieval, embeddings theory, each framework's straightforward implementation) — nothing there requires knowing agents. Phase 8, "Advanced RAG," covers agentic/self-correcting RAG, CacheRAG, and GraphRAG — patterns that genuinely depend on understanding agents (Phase 5) and advanced agentic systems (Phase 7) first, so it's deliberately sequenced after both rather than bundled into Phase 4.

---

## Quick Start

```bash
# Clone
git clone https://github.com/Sourav692/LangGraph-Demystified.git
cd LangGraph-Demystified

# Setup
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"

# Launch
jupyter lab
```

### Environment Variables

Create a `.env` at the project root:

```env
OPENAI_API_KEY=...          # OpenAI models
GROQ_API_KEY=...            # Groq models (fast + free tier)
GOOGLE_API_KEY=...          # Streamlit apps
TAVILY_API_KEY=...          # Web search notebooks
# Databricks credentials    # Auto-selected on macOS
```

---

# Built Phases

## Phase 1 — Theory & Foundations

> *Optional internals: model landscape and the Hugging Face ecosystem. Skip or come back later if you want to start applied work sooner.*

| Track | Status | Scope |
|---|---|---|
| `Model_Landscape_and_Hugging_Face/` | ✅ Built | Hub setup, Transformers, Diffusers, audio/video, Gradio, pretrained models from the Hub |
| `Math_and_ML_Intuition/` | 🚧 Planned | Math/ML intuition for LLMs |
| `Transformer_Architecture/` | 🚧 Planned | Attention, positional encoding, transformer internals |
| `Fine_Tuning_and_RL/` | ✅ Partially built | SFT / data prep / training / eval (DeepLearning.AI); Llama 2 AutoTrain; RLHF/DPO/LoRA planned |
| `Coding_Essentials_for_Agents/` | ✅ Built | Python, files/DBs, Flask APIs, raw LLM API calls, threading/GIL, asyncio |

## Phase 2 — LangChain Fundamentals & Prompting

> *The on-ramp: LangChain's core building blocks, then how to write and assemble what the model sees.*

| Track | Status | Scope |
|---|---|---|
| `LangChain_Fundamentals/` | ✅ Built | Getting started, I/O & prompts, LCEL, chains, summarization (5 modules — true fundamentals only) |
| `Prompt_and_Context_Engineering/Prompt_Engineering/` | ✅ Built | Core & advanced prompting patterns, hands-on-by-model, multimodal, real-world applications |
| `Prompt_and_Context_Engineering/Context_Engineering/` | 🚧 Planned | Context assembly — retrieval/memory/tool-result context, context-window management |

### `LangChain_Fundamentals/`

| # | Module | Topic |
|---|---|---|
| 1 | `01_Getting_Started/` | Commercial + open-source LLMs, natively and via LangChain |
| 2 | `02_Inputs_Outputs_Prompts/` | Inputs/outputs, prompt templates, LLM vs ChatModel, output parsers |
| 3 | `03_LCEL/` | LangChain Expression Language, Runnables, chain migrations |
| 4 | `04_Chains/` | Chain basics, advanced chains, branching/routing/merging |
| 5 | `05_Summarization/` | Text summarization |

Tool-calling, agents, memory, RAG, LangSmith, advanced features, and microservices deployment each have their own dedicated phase elsewhere — see the roadmap table above.

---

## Phase 3 — LangGraph Fundamentals

> *How does LangGraph work?*

Core mechanics only — no RAG, no agent builds, no design patterns (those are Phases 4, 5, 8).

| #  | Notebook (`01_Foundations/`)          | Key Concepts                                           |
| -- | -------------------------------------- | ------------------------------------------------------ |
| 1  | `01_State_and_Graph_Basics.ipynb`    | `StateGraph`, `TypedDict`, nodes, edges, reducers  |
| 2  | `02_MessageState.ipynb`              | `MessagesState`, the pre-built state for chat graphs |
| 3  | `03_Conditional_Routing.ipynb`       | `add_conditional_edges`, routing functions           |
| 4  | `04_LLM_Powered_Chatbot.ipynb`       | Chat models, message history, streaming                |
| 5  | `05_Augmented_LLM_with_Tools.ipynb`  | `@tool`, `bind_tools()`, `ToolNode`              |
| 6  | `06_ReAct_Agent.ipynb`               | ReAct loop: Reason → Act → Observe                   |
| 7  | `07_Different_Graph_States.ipynb`    | Four ways to define graph state                        |
| 8  | `08_Pydantic_State_Validation.ipynb` | `BaseModel` vs `TypedDict`, runtime validation     |
| 9  | `09_Node_Patterns.ipynb`             | Node arguments, config, and runtime context            |
| 10 | `10_Runtime_Context.ipynb`           | Injecting external dependencies via runtime context    |
| 11 | `11_Command_Objects.ipynb`           | `Command` — combined routing + state updates        |

Plus `02_Core_Capabilities/` — routing (incl. an agentic-RAG-router example, kept here since it's also a routing-mechanics demo), human-in-the-loop, advanced state, subgraphs, async & streaming, retries. *(Memory lives in Phase 7 instead.)*

---

## Phase 4 — Retrieval & RAG

> *How do I build retrieval systems?*

Foundational RAG only — theory plus each framework's basic implementation. Nothing here requires knowing agents; agentic/advanced RAG is Phase 8.

| Track | Status | Scope |
|---|---|---|
| `Introduction_to_RAG/` | ✅ Built | RAG overview, indexing, LangChain+RAG |
| `Embeddings_and_Vector_Databases/` | ✅ Built | Embedding models, vector DB options (Chroma, FAISS, Pinecone, DataStax, others), retrievers |
| `RAG_Naive_to_Production/` | ✅ Built | Loading data → chunking → hybrid search → query enhancement → parent-doc retrieval → postprocessing → full pipelines |
| `Query_Transformation_Techniques/` | ✅ Built | Multi-query, RAG-Fusion, decomposition, HyDE, step-back prompting, routing, cross-encoder reranking |
| `Multimodal_and_Document_Intelligence/` | ✅ Built (light) | Multimodal RAG |
| `RAG_with_LangGraph/` | ✅ Built | Basic agentic RAG (2 nb) |
| `RAG_with_LangChain/` | ✅ Built | RAG essentials, comprehensive, filtered search, indexing API (4 nb) |
| `RAG_with_LlamaIndex/` | ✅ Built | Chainlit ReAct RAG chatbot over Wikipedia |

Also `shared_data/` — supporting PDFs/data referenced by several notebooks in this phase.

---

## Phase 5 — AI Agent Fundamentals

> *How do I build agents?*

All agent-building content, across both frameworks, in one phase.

| Track | Status | Scope |
|---|---|---|
| `LangChain_Tools_and_Agents/` | ✅ Built | Tool calling, tool-calling agents, OpenAI tool calling, agents, + 16 applied projects |
| `AI_Agents_with_LangGraph/` | ✅ Built | 11 real-world agent builds (research, financial, hotel reservations, software engineering, and more) |
| `Workflow_and_Agent_Patterns/` | ✅ Built | 8 pattern subfolders, ~27 notebooks — tool use, planning, reflection, router, prompt chaining, evaluator-optimizer, orchestrator-worker, advanced cognitive patterns |
| `Building_Agents_From_Scratch/` | ✅ Built | OpenAI API + `agentic_patterns` package (no LangGraph) |

Also includes `Design_Patterns_Reference.md` — a taxonomy write-up with diagrams.

---

## Phase 7 — Advanced Agentic Systems

> *Compose agents into systems.*

| Track | Status | What It Covers |
|---|---|---|
| `Memory_and_State/` | ✅ Built | `LangGraph/` (memory & threads + PostgreSQL long-term memory) + `LangChain/` (chat message memory, multi-user in-memory & SQL persistent storage) |
| `Multi_Agent_Orchestration/` | ✅ Built | Supervisor pattern + peer-to-peer/swarm multi-agent architecture |
| `Deep_Agents_and_Harness_Engineering/` | ✅ Built | `deepagents`-based multi-agent orchestration — see below |
| `Evaluation_and_Eval_Harnesses/` | ✅ Built | `RAG_Evaluation/` (metrics + DeepEval drills + RAGAS); `Agent_Evaluation/` (Arize labs + CrewAI eval); `LLM_as_Judge/` (DeepEval G-Eval intro) |

### `Deep_Agents_and_Harness_Engineering/`

Orchestrate specialized agents with skills, tool delegation, and code execution, built on the `deepagents` library:

```
Orchestrator (Claude Opus via Databricks)
├── memory-manager         Saves, recalls, and organizes long-term memories
├── senior-developer       Plans, writes, and delivers complete Python projects
├── code-reviewer          Reviews code for bugs, style, and best practices
├── research-agent         Web research via Tavily
└── Analytics agents (Databricks Genie)
    ├── aia-customer-analytics       Customer segmentation, retention, demographics
    ├── aia-distribution-channels    Agent performance, sales channels
    ├── aia-policy-underwriting      Premiums, renewals, product mix
    └── aia-claims-analytics         Claims, fraud scores, processing times
```

Three code-execution backends: `FilesystemBackend` (safe default), `LocalShellBackend` (local dev), `LangSmithSandbox` (cloud, production) — plus a JSON-backed long-term memory variant.

```bash
cd 07_Advanced_Agentic_Systems/Deep_Agents_and_Harness_Engineering
python examples/simple_coding_agent.py
python examples/long_term_memory_agent.py
```

Runs off the root environment — no separate install needed. A standalone deployable version (FastAPI + frontend, Docker) also lives under `app/`.

---

## Phase 8 — Advanced RAG

> *Agentic and advanced retrieval patterns — needs Phases 5 & 7 first.*

| Track | Status | Scope |
|---|---|---|
| `RAG_with_LangGraph_Advanced/` | ✅ Built | Self-correcting retrieval, corrective/adaptive RAG, healthcare router agentic RAG |
| `Comprehensive_RAG_Techniques/` | ✅ Built | ~35-notebook anthology — CRAG, Self-RAG, RAPTOR, GraphRAG, fusion/adaptive retrieval, and more |
| `GraphRAG/` | ✅ Built | Knowledge-graph-based retrieval — full KG+RAG course |
| `CacheRAG/` | 🚧 Planned | Caching strategies for RAG |

Also two standalone apps: `building-adaptive-rag/` and `mcp_a2a_agentic_rag/` (MCP + A2A agentic RAG).

---

## Phase 12 — Production & Observability

> *How do I ship it, and know it's working?*

| Track | Status | Scope |
|---|---|---|
| `DevOps_and_Deployment/` | 🚧 Planned | Deployment foundations |
| `LLMOps_and_AI_Infrastructure/` | ✅ Partially built | `Tracing_and_Observability/` (LangSmith built, LangFuse planned, callbacks), `Caching_and_Performance/`, `Cost_Monitoring/` |
| `Security_and_Compliance/` | 🚧 Planned | Security, compliance, private deployment |
| `Safety_and_Alignment/` | ✅ Partially built | Content moderation |

---

## Phase 13 — Projects

> *Capstones combining multiple frameworks and phases.*

| Project | Status | What It Is |
|---|---|---|
| `LangGraph_Fullstack_Capstone/` | ✅ Built | FastAPI + Angular + PostgreSQL with human-in-the-loop workflows, unit tests, Streamlit apps |
| `LangChain_Microservices_Capstone/` | ✅ Built | LangChain deployed as microservices (Docker, k8s-style manifests, frontend) |
| `RAG_Systems_Projects/` | ✅ Built | 7 applied RAG capstones — document search engine, multi-user conversational RAG, multimodal RAG, Q&A systems |
| `ShopUNow_Agentic_RAG_Capstone/` | ✅ Built | Vector DB + agentic RAG e-commerce capstone |
| `AI_Powered_Customer_Support/`, `Automated_Candidate_Interview_Evaluation_System/`, `End_to_End_Medical_Chatbot/`, `Pipecat_QuickStart/`, `Realtime_Source_Code_Analyzer/`, `Realtime_Voice_AI_Agent_with_RAG/` | ✅ Built | 6 more standalone full-stack apps |

```bash
# LangGraph capstone
cd 13_Projects/LangGraph_Fullstack_Capstone/fullstackapp && docker compose up
cd 13_Projects/LangGraph_Fullstack_Capstone/unit_tests && pytest
cd 13_Projects/LangGraph_Fullstack_Capstone/streamlit_apps/doc-entity-extractor && streamlit run app.py
```

---

## Phase 9 — Agent Protocols

> *How models reach tools and data (MCP), then how agents talk to each other (ACP, A2A).*

| Track | Status | Scope |
|---|---|---|
| `MCP/` | ✅ Built | Anthropic + Educative foundations, servers, clients, Udemy MCP Mastery apps, Databricks Apps server |
| `ACP/` | 🚧 Planned | Agent Communication Protocol |
| `A2A/` | 🚧 Planned | Agent2Agent Protocol |

## Phase 10 — Alternative Agent Frameworks

> *Frameworks to pick up after the LangGraph/LangChain core path (Phases 3 & 5).*

| Track | Status | Scope |
|---|---|---|
| `CrewAI/` | ✅ Built | Foundations (basics, 8 simple agents, comprehensive tutorial), Flows, multi-agent patterns, 9 application project sets |
| `AutoGen/` | ✅ Built | Foundations, conversable/sequential/tool/code/multimodal labs, group/swarm patterns, 8 application project sets (incl. Auto-EDA) |
| `DSPy/` | ✅ Built | Context-engineering course with DSPy (levels 1–5, kept whole) |
| `PydanticAI/`, `Orchestration_Frameworks_Overview/` | 🚧 Planned | |

---

# Other Phases (Planned)

Everything below has a scope-describing `README.md` and (for framework/protocol phases) a first level of subfolders — but **no actual notebooks or code exist yet**.

- **Phase 6 — Agent SDKs (First-Party)**: `Google_ADK/`, `OpenAI_Agents_SDK/`, `Google_AI_SDK/`
- **Phase 11 — Claude Code & AI Coding Tools**: `Claude_Code/`, `Agent_Skills/`, `Claude_API_and_Agent_SDK/`, `AI_Coding_Tool_Landscape/`

---

## Project Structure

```
AI ENGINEERING/
│
├── 01_Theory_and_Foundations/               ✅ Partially built
│   ├── Model_Landscape_and_Hugging_Face/     00_Setup/ … 06_Pretrained_Models/
│   ├── Math_and_ML_Intuition/                🚧 Planned
│   ├── Transformer_Architecture/             🚧 Planned
│   ├── Fine_Tuning_and_RL/                   01_Foundations/ + 03_Applications/ built; 02_Techniques/ planned
│   └── Coding_Essentials_for_Agents/         01 … 06 (Python through asyncio)
├── 02_LangChain_Fundamentals_and_Prompting/ ✅ Built
│   ├── LangChain_Fundamentals/               01_Getting_Started/ … 05_Summarization/
│   └── Prompt_and_Context_Engineering/
│       ├── Prompt_Engineering/                01_Core_Patterns/ … 05_Real_World_Applications/, Assignments/
│       └── Context_Engineering/               🚧 Planned
├── 03_LangGraph_Fundamentals/               ✅ Built
│   ├── 01_Foundations/
│   └── 02_Core_Capabilities/
├── 04_Retrieval_and_RAG/                    ✅ Built
│   ├── Introduction_to_RAG/
│   ├── Embeddings_and_Vector_Databases/
│   ├── RAG_Naive_to_Production/
│   ├── Query_Transformation_Techniques/
│   ├── Multimodal_and_Document_Intelligence/
│   ├── RAG_with_LangGraph/
│   ├── RAG_with_LangChain/
│   ├── RAG_with_LlamaIndex/
│   └── shared_data/
├── 05_AI_Agent_Fundamentals/                ✅ Built
│   ├── LangChain_Tools_and_Agents/            01_Tools_and_Functions/, 02_Agents/, 03_Applied_Projects/
│   ├── AI_Agents_with_LangGraph/              01 … 11 (research, financial, hotel, software-eng builds)
│   ├── Workflow_and_Agent_Patterns/
│   └── Building_Agents_From_Scratch/
├── 06_Agent_SDKs_First_Party/                🚧 Planned
├── 07_Advanced_Agentic_Systems/              ✅ Built
│   ├── Memory_and_State/                      LangGraph/, LangChain/
│   ├── Multi_Agent_Orchestration/
│   ├── Deep_Agents_and_Harness_Engineering/
│   └── Evaluation_and_Eval_Harnesses/         RAG_Evaluation/, Agent_Evaluation/, LLM_as_Judge/
├── 08_Advanced_RAG/                          ✅ Built
│   ├── RAG_with_LangGraph_Advanced/
│   ├── Comprehensive_RAG_Techniques/
│   ├── GraphRAG/
│   ├── CacheRAG/                              🚧 Planned
│   ├── building-adaptive-rag/
│   └── mcp_a2a_agentic_rag/
├── 09_Agent_Protocols/                       ✅ Partially built
│   ├── MCP/                                   01_Foundations/ … 04_Applications/, mcp_a2a_agentic_rag/
│   ├── ACP/                                   🚧 Planned
│   └── A2A/                                   🚧 Planned
├── 10_Alternative_Agent_Frameworks/          ✅ Partially built
│   ├── CrewAI/                                01_Foundations/, 02_Core_Capabilities/, 03_Multi_Agent_Patterns/, 04_Applications/
│   ├── AutoGen/                                01_Foundations/, 02_Core_Capabilities/, 03_Multi_Agent_Patterns/, 04_Applications/
│   ├── DSPy/                                   context-engineering-dspy/ (levels 1–5)
│   └── PydanticAI/, Orchestration_Frameworks_Overview/  🚧 Planned
├── 11_Claude_Code_and_AI_Coding_Tools/       🚧 Planned
├── 12_Production_and_Observability/          ✅ Partially built
│   ├── DevOps_and_Deployment/                 🚧 Planned
│   ├── LLMOps_and_AI_Infrastructure/           Tracing_and_Observability/, Caching_and_Performance/, Cost_Monitoring/
│   ├── Security_and_Compliance/               🚧 Planned
│   └── Safety_and_Alignment/
├── 13_Projects/                              ✅ Built (10 projects)
│   ├── LangGraph_Fullstack_Capstone/
│   ├── LangChain_Microservices_Capstone/
│   ├── RAG_Systems_Projects/
│   ├── ShopUNow_Agentic_RAG_Capstone/
│   └── AI_Powered_Customer_Support/, Automated_Candidate_Interview_Evaluation_System/,
│       End_to_End_Medical_Chatbot/, Pipecat_QuickStart/, Realtime_Source_Code_Analyzer/,
│       Realtime_Voice_AI_Agent_with_RAG/
├── helpers/                                  Shared LLM/embedding factory (used by built LangGraph phases)
├── docs/                                     Static HTML tutorial microsite (LangGraph mechanics chapters)
└── archive/                                  Retired notebooks
```

---

## Shared Helpers

LangGraph notebooks use a unified LLM/embedding factory (LangChain-course notebooks instantiate clients directly instead):

```python
from helpers import get_llm, get_embeddings

llm = get_llm()                # Auto-selects by platform
embeddings = get_embeddings()
```

| Platform | LLM                              | Embeddings                          |
| -------- | --------------------------------- | ------------------------------------ |
| macOS    | Databricks (`claude-opus-4-6`)  | Databricks (`gte-large-en`)        |
| Windows  | Groq (`gpt-oss-120b`)           | OpenAI (`text-embedding-3-small`)  |

Override: `get_llm(provider="openai", model="gpt-4o")`

---

## Installation Options

```bash
uv pip install -e ".[dev]"          # Core + dev tools (pytest, jupyter)
uv pip install -e ".[apps]"         # + Streamlit apps
uv pip install -e ".[fullstack]"    # + FastAPI, PostgreSQL
uv pip install -e ".[all]"          # Everything
```

---

## Contributing

Contributions welcome! Fork, branch, and submit a PR.

## License

See [LICENSE](LICENSE) for details.
