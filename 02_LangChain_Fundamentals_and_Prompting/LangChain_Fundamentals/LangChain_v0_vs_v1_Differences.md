# LangChain 0.x vs LangChain 1.x — What Actually Changed

> Researched from the official LangChain docs and release blog (checked September 2026).
> This repo pins `langchain>=1.2.7` / `langchain-core>=1.2.7` in `pyproject.toml` — i.e. **the 1.x line**.
> Many notebooks in this track were written against 0.x idioms; use the mapping tables below when updating them.

---

## 1. The one-sentence summary

LangChain 0.x was a **large toolbox of chains, memory classes, retrievers and agent executors**.
LangChain 1.0 (October 2025) rewrote the top-level package around **one high-level agent abstraction (`create_agent`) running on LangGraph**, moved everything legacy into a separate `langchain-classic` package, and standardized model outputs behind provider-agnostic **content blocks**.

1.0 was also the first release with a **stability commitment**: no breaking changes until 2.0. The 1.x line has since moved fast on additive features (`langchain-core` was at 1.5.x as of August 2026).

---

## 2. Package layout

### Old (0.x)

```
langchain                 # chains, agents, memory, retrievers, indexing, hub — everything
langchain-core            # base abstractions
langchain-community       # 3rd-party integrations
langchain-openai / ...    # per-provider partner packages
langgraph                 # separate graph runtime, optional
```

### New (1.x)

```
langchain                 # narrow: agents + convenience re-exports
  ├── langchain.agents        -> create_agent, middleware
  ├── langchain.messages      -> HumanMessage, AIMessage, content blocks
  ├── langchain.tools         -> @tool, ToolNode
  ├── langchain.chat_models   -> init_chat_model
  └── langchain.embeddings
langchain-classic         # ALL legacy: chains, retrievers, indexing API, hub, cache-backed embeddings
langchain-core            # base abstractions (unchanged role)
langgraph                 # now the runtime *underneath* langchain agents
```

**Practical rule:** if an import broke on upgrade, it almost certainly moved to `langchain-classic`.

```bash
uv pip install langchain-classic
```

```python
# 0.x
from langchain.chains import LLMChain, RetrievalQA
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain import hub

# 1.x
from langchain_classic.chains import LLMChain, RetrievalQA
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langchain_classic import hub
```

---

## 3. Agents — the biggest change

All 0.x agent constructors (`initialize_agent`, `AgentExecutor`, `create_react_agent`, `create_tool_calling_agent`, `create_openai_functions_agent`, …) are superseded by a **single** entry point.

```python
# 0.x — AgentExecutor era
from langchain.agents import AgentExecutor, create_tool_calling_agent
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
executor.invoke({"input": "..."})

# 0.x — LangGraph prebuilt era
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(model, tools, prompt="You are helpful")

# 1.x
from langchain.agents import create_agent
agent = create_agent(model, tools, system_prompt="You are helpful")
agent.invoke({"messages": [{"role": "user", "content": "..."}]})
```

### Parameter / behaviour deltas when moving off `create_react_agent`

| 0.x                                           | 1.x                                                | Note                           |
| --------------------------------------------- | -------------------------------------------------- | ------------------------------ |
| `prompt=`                                   | `system_prompt=`                                 | renamed                        |
| `pre_model_hook` / `post_model_hook`      | middleware`before_model` / `after_model`       | see §4                        |
| state as Pydantic model or dataclass          | **TypedDict only**, extending `AgentState` | hard breaking change           |
| pass a model already`.bind_tools(...)`-ed   | not supported — pass model +`tools` separately  |                                |
| stream node name`"agent"`                   | node name`"model"`                               | breaks existing stream filters |
| `config["configurable"]` for runtime values | `context=` parameter                             |                                |

---

## 4. Middleware — new in 1.x

The 0.x way to customize an agent loop was to subclass `AgentExecutor`, wrap callbacks, or hand-roll a LangGraph graph. 1.x introduces **composable middleware** hooks around the agent loop:

`before_agent` → `before_model` → `wrap_model_call` → `wrap_tool_call` → `after_model` → `after_agent`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    SummarizationMiddleware,
    PIIRedactionMiddleware,
)

agent = create_agent(
    model="openai:gpt-4o",
    tools=tools,
    system_prompt="...",
    middleware=[
        SummarizationMiddleware(max_tokens_before_summary=4000),
        PIIRedactionMiddleware(),
        HumanInTheLoopMiddleware(interrupt_on={"send_email": True}),
    ],
)
```

This is where **context engineering** now lives: trimming/summarizing history, injecting retrieved context, gating tool calls, redacting data — all as reusable, ordered layers instead of bespoke graph code.

---

## 5. Memory

| 0.x                                                                                             | 1.x                                                                                                          |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `ConversationBufferMemory`, `ConversationSummaryMemory`, `ConversationBufferWindowMemory` | LangGraph**checkpointers** (`InMemorySaver`, `PostgresSaver`) + `thread_id` for short-term state |
| summary-buffer memory                                                                           | `SummarizationMiddleware`                                                                                  |
| `ConversationChain`                                                                           | `create_agent` + checkpointer                                                                              |
| ad-hoc long-term stores                                                                         | LangGraph`Store` / `BaseStore`                                                                           |

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(model, tools, checkpointer=InMemorySaver())
agent.invoke(
    {"messages": [...]},
    config={"configurable": {"thread_id": "user-1"}},
)
```

Worked versions live in `07_Advanced_Agentic_Systems/Memory_and_State/`.

---

## 6. Standard content blocks (messages)

In 0.x, message `.content` was either a string or a provider-shaped list of dicts — you wrote per-provider branching to read reasoning traces, citations or tool calls.

1.x adds a **provider-agnostic, typed `.content_blocks`** property on every message:

```python
resp = model.invoke("Explain quantum tunneling with citations")

for block in resp.content_blocks:
    if block["type"] == "reasoning":
        print("THINKING:", block["reasoning"])
    elif block["type"] == "text":
        print(block["text"])
    elif block["type"] == "citation":
        print(block)
```

Block shapes are standardized — e.g. `{"type": "text", "text": ...}`, `{"type": "image", "url": ..., "mime_type": ...}` — plus `reasoning`, `tool_call`, `citation` and `server_tool_call` types.

`.content` still exists for backwards compatibility and does **not** serialize standard blocks unless you set `LC_OUTPUT_VERSION=v1`.

---

## 7. Other breaking changes worth knowing

- **Python ≥ 3.10** required across all LangChain packages (0.x supported 3.8/3.9). This repo targets 3.12, so no action needed.
- `message.text()` (method) → `message.text` (property).
- `example` parameter removed from `AIMessage`.
- Chat model `.invoke()` return type narrowed from `BaseMessage` to **`AIMessage`**.
- `langchain-anthropic` changed its default `max_tokens`.
- The `langchain` package no longer re-exports chains / retrievers / indexing / hub at all.

---

## 8. What did *not* change

- **LCEL is intact.** `prompt | model | parser`, `Runnable`, `RunnableParallel`, `RunnablePassthrough`, `.batch()`, `.stream()`, `.astream()` all behave as before — module `03_LCEL/` in this track stays valid.
- **Prompt templates** (`ChatPromptTemplate`, `PromptTemplate`, few-shot templates) are unchanged.
- **Output parsers** and structured output (`with_structured_output`) are unchanged.
- **Partner packages** (`langchain-openai`, `langchain-groq`, `langchain-anthropic`, …) keep the same class names.
- **Document loaders, text splitters, vector stores** keep their homes (`langchain-community`, `langchain-text-splitters`, `langchain-chroma`, …).

---

## 9. Quick migration checklist

1. `uv pip install -U langchain langchain-core` (already pinned to 1.x here).
2. Run the code; every `ImportError` from `langchain.chains` / `langchain.retrievers` / `langchain.indexes` / `langchain.hub` → install `langchain-classic` and re-point the import.
3. Replace `AgentExecutor` / `initialize_agent` / `create_react_agent` with `langchain.agents.create_agent`; rename `prompt=` → `system_prompt=`.
4. Convert any Pydantic/dataclass agent state to a `TypedDict` extending `AgentState`.
5. Replace `Conversation*Memory` with a checkpointer + `thread_id`, and add `SummarizationMiddleware` where you were summarizing.
6. Replace `pre_model_hook` / `post_model_hook` with middleware.
7. Fix `.text()` → `.text`; update stream filters keyed on the `"agent"` node → `"model"`.
8. Where you branched on provider-specific `content` shapes, switch to `.content_blocks`.

---

## 10. Decision guide: `create_agent` vs raw LangGraph

| Use`langchain.create_agent`           | Use`langgraph` directly                                           |
| --------------------------------------- | ------------------------------------------------------------------- |
| Standard tool-calling / ReAct loop      | Custom control flow, cycles, branching beyond the agent loop        |
| Customization fits the middleware hooks | Multi-agent topologies (supervisor, swarm), map-reduce with`Send` |
| Fast to ship, provider-swappable        | Long-running, durable, human-in-the-loop business processes         |

They are the same runtime — `create_agent` compiles down to a LangGraph graph, so you can start there and drop a level when you outgrow it.
Phase 3 (`03_LangGraph_Fundamentals/`) and Phase 5 (`05_AI_Agent_Fundamentals/`) cover that lower level.

---

## Sources

- [What&#39;s new in LangChain v1 — LangChain Docs](https://docs.langchain.com/oss/python/releases/langchain-v1)
- [Migrate to LangChain v1 — LangChain Docs](https://docs.langchain.com/oss/python/migrate/langchain-v1)
- [LangChain and LangGraph Agent Frameworks Reach v1.0 Milestones — LangChain Blog](https://www.langchain.com/blog/langchain-langgraph-1dot0)
- [langchain-core on PyPI (version history)](https://pypi.org/project/langchain-core/)
- [langchain-ai/langchain GitHub Releases](https://github.com/langchain-ai/langchain/releases)
- [Lessons Learnt from Upgrading to LangChain 1.0 in Production — Towards Data Science](https://towardsdatascience.com/lessons-learnt-from-upgrading-to-langchain-1-0-in-production/)
- [LangChain v1 is now generally available — Microsoft Community Hub](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/langchain-v1-is-now-generally-available/4462159)
