<div align="center">

---

## Who Is This For?

| Level                                       | Start At                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------------ |
| **Complete beginner** to LangGraph    | [Chapter 1: Foundations](#chapter-1-foundations)                          |
| **Know Python + LLMs**, new to agents | [Chapter 3: RAG](#chapter-3-rag) or [Chapter 4: Agents](#chapter-4-agents) |
| **Built basic agents**, want patterns | [Chapter 5: Agentic Design Patterns](#chapter-5-agentic-design-patterns)  |
| **Ready for production**              | [Chapter 6: Production](#chapter-6-production)                            |
| **Want multi-agent systems**          | [Chapter 7: Deep Agents](#chapter-7-deep-agents)                          |

---

## Learning Roadmap

```
Ch 1                Ch 2                Ch 3          Ch 4           Ch 5                Ch 6          Ch 7
FOUNDATIONS         CORE CAPABILITIES   RAG           AGENTS         DESIGN PATTERNS     PRODUCTION    DEEP AGENTS

State & Graphs  ──► Memory          ──► Basic RAG ──► Research  ──► Tool Use        ──► Full-Stack ──► Multi-Agent
Routing             Routing             Databricks    Business      Planning            Testing         Orchestration
LLM + Tools         Human-in-Loop       Advanced      Intelligence  Reflection          Streamlit       Code Execution
ReAct Agent         Subgraphs           RAG-as-Tool                 Agent Patterns      Apps
Pydantic            Async/Streaming                                 Long-Term Memory

 Beginner           Beginner+           Intermediate  Intermediate  Advanced            Advanced      Expert
 (11 notebooks)     (12 notebooks)      (4 notebooks) (2 notebooks) (6 notebooks)       (apps+tests)  (multi-agent)
```

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
GOOGLE_API_KEY=...          # Streamlit apps (Chapter 6)
TAVILY_API_KEY=...          # Web search (Chapters 4-5)
# Databricks credentials    # Auto-selected on macOS
```

---

## Learning Path

> For the complete, up-to-date notebook listing, see [`NOTEBOOK_INDEX.md`](NOTEBOOK_INDEX.md).

### Chapter 1: Foundations

> *How does LangGraph work?*

Master the building blocks — state, graphs, routing, tools, and the ReAct pattern.

| #  | Notebook                               | Key Concepts                                           |
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

---

### Chapter 2: Core Capabilities

> *What can LangGraph do?*

Platform features you'll use across all agents — memory, human-in-the-loop, subgraphs, async.

| Section                     | Notebooks | What You'll Learn                                               |
| --------------------------- | --------- | --------------------------------------------------------------- |
| **Memory**            | 3         | `MemorySaver`, `SqliteSaver`, agent memory types, threads   |
| **Routing**           | 1         | Sentiment-aware routing, category-based KB                      |
| **Human-in-the-Loop** | 4         | `interrupt()`/resume, state modification, dynamic breakpoints |
| **Advanced State**    | 1         | Complex state management patterns                               |
| **Subgraphs**         | 1         | Graph composition, modular workflows                            |
| **Async & Streaming** | 1         | Async operations, streaming output                              |
| **Retries**           | 1         | Fault-tolerant nodes with`RetryPolicy`                        |

---

### Chapter 3: RAG

> *How do I build retrieval systems?*

From basic PDF Q&A to RAG as a composable tool inside larger agents.

| # | Notebook                                   | What You'll Build                             |
| - | ------------------------------------------ | --------------------------------------------- |
| 1 | `01_Simple_Agentic_RAG.ipynb`            | PDF → Chroma → LLM question-answering       |
| 2 | `02_Simple_Agentic_RAG_Databricks.ipynb` | Same agent on Databricks Vector Search        |
| 3 | `03_Advanced_RAG_Agent.ipynb`            | Advanced retrieval with grading and rewriting |
| 4 | `04_RAG_as_Tool_in_Agents.ipynb`         | RAG as a composable tool                      |

---

### Chapter 4: Agents

> *How do I build real agents?*

Build complete agents that solve real-world problems.

| # | Notebook                                    | What You'll Build                                  |
| - | ------------------------------------------- | -------------------------------------------------- |
| 1 | `01_Research_Assistant_Chatbot.ipynb`     | Web-search research assistant with Tavily          |
| 2 | `02_Competitive_Intelligence_Agent.ipynb` | Business intelligence agent with structured output |

---

### Chapter 5: Agentic Design Patterns

> *What are the design patterns?*

The architectural patterns that make agents truly powerful.

| Pattern                    | Notebooks         | What You'll Learn                               |
| -------------------------- | ----------------- | ----------------------------------------------- |
| **Tool Use**         | 2                 | Advanced tool strategies, tool calling vs ReAct |
| **Planning**         | 2                 | Parallel execution, map-reduce with`Send` API |
| **Reflection**       | *(coming soon)* | Agent self-evaluation and iterative improvement |
| **Agent Patterns**   | 1                 | Reusable production agent templates             |
| **Long-Term Memory** | 1                 | Persistent memory with PostgreSQL               |

---

### Chapter 6: Production

> *How do I ship it?*

| Component                | What It Is                                                      |
| ------------------------ | --------------------------------------------------------------- |
| **Full-Stack App** | FastAPI + Angular + PostgreSQL with human-in-the-loop workflows |
| **Unit Tests**     | pytest examples for LangGraph nodes                             |
| **Streamlit Apps** | Document entity extraction + knowledge graph builder            |

```bash
# Full-stack app
cd 06_Production/fullstackapp && docker compose up

# Unit tests
cd 06_Production/unit_tests && pytest

# Streamlit
cd 06_Production/streamlit_apps/doc-entity-extractor && streamlit run app.py
```

---

### Chapter 7: Deep Agents

> *How do I build multi-agent systems?*

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

Each agent's behavior is defined by a `SKILL.md` under `07_Deep_Agents/skills/`. Three code-execution backends are available — `FilesystemBackend` (safe default, no execution), `LocalShellBackend` (local dev), `LangSmithSandbox` (cloud, production) — plus a long-term memory variant backed by JSON (upgradeable to PostgreSQL). See `07_Deep_Agents/README.md` for details.

```bash
cd 07_Deep_Agents
python examples/simple_coding_agent.py          # default: FilesystemBackend
python examples/long_term_memory_agent.py        # cross-thread persistent memory
```

This chapter runs off the root environment (`uv pip install -e ".[dev]"`) — no separate install needed. A standalone deployable version (FastAPI + frontend, Docker) also lives under `07_Deep_Agents/app/`.

---

## Project Structure

```
LangGraph-Demystified/
│
├── 01_Foundations/                  Ch 1: State, graphs, tools, ReAct
├── 02_Core_Capabilities/           Ch 2: Memory, HITL, subgraphs, async
│   ├── 01_Memory/
│   ├── 02_Routing/
│   ├── 03_Human_in_the_Loop/
│   ├── 04_Advanced_State/
│   ├── 05_Subgraphs/
│   ├── 06_Async_and_Streaming/
│   └── 07_Retries/
├── 03_RAG/                         Ch 3: Basic → advanced → RAG-as-tool
├── 04_Agents/                      Ch 4: Research + business agents
├── 05_Agentic_Design_Patterns/     Ch 5: Tool use, planning, agent patterns
│   ├── 01_Tool_Use/
│   ├── 02_Planning/
│   ├── 04_Agent_Patterns/          (03_Reflection/ not yet implemented)
│   └── 05_Long_Term_Memory/
├── 06_Production/                  Ch 6: Full-stack, testing, Streamlit
│   ├── fullstackapp/
│   ├── unit_tests/
│   └── streamlit_apps/
├── 07_Deep_Agents/                 Ch 7: Multi-agent orchestration (deepagents)
│   ├── app/                        Standalone deployable version (FastAPI + frontend)
│   ├── docs/
│   ├── examples/
│   └── skills/
├── helpers/                        Shared LLM/embedding factory
├── docs/                           Static HTML tutorial microsite
└── archive/                        Retired notebooks
```

---

## Shared Helpers

All notebooks use a unified LLM/embedding factory:

```python
from helpers import get_llm, get_embeddings

llm = get_llm()                # Auto-selects by platform
embeddings = get_embeddings()
```

| Platform | LLM                              | Embeddings                          |
| -------- | -------------------------------- | ----------------------------------- |
| macOS    | Databricks (`claude-opus-4-6`) | Databricks (`gte-large-en`)       |
| Windows  | Groq (`gpt-oss-120b`)          | OpenAI (`text-embedding-3-small`) |

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
