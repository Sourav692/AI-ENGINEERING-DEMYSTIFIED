# 0.x → 1.x rewrite map

The canonical narrative lives in
`02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/LangChain_v0_vs_v1_Differences.md`.
This file is the **operational** companion: for each thing the scanner flags, what to actually write.

Repo pins: `langchain>=1.2.7`, `langchain-core>=1.2.7`, `langgraph==1.2.11` (see `requirements.txt`).
`langchain-classic` is **not** currently in `pyproject.toml` — adding it is a decision, see §0.

---

## 0. The decision that shapes every plan: classic vs rewrite

For every legacy chain/retriever/memory hit, there are exactly two exits:

| Exit | When | Cost |
| --- | --- | --- |
| **Repoint** to `langchain_classic.*` | The notebook's *lesson is the legacy construct itself* (e.g. a module literally titled "Chains", teaching `LLMChain` as a historical concept) | one-line import change + a new dependency across all three dep files (see below) |
| **Rewrite** to the 1.x idiom | The notebook's lesson is the *task* (summarize, retrieve, converse) and the chain was just the vehicle | real work, but the notebook stops teaching a deprecated API |

Default to **rewrite** for anything a learner is meant to copy into their own project, and
**repoint** only where the legacy API is the subject. Always surface this choice per-notebook in the
plan rather than deciding silently — for a teaching repo it's an editorial call, not a mechanical one.

Adding `langchain-classic` touches three files: `pyproject.toml` (floors / source of truth),
`requirements.txt` (resolver-verified pins), `requirements.lock.txt` (transitive lock, regenerated
with `uv pip compile requirements.txt --python-version 3.12 -o requirements.lock.txt`). Note the
repo's exclusion list in `requirements.txt`'s header — some packages deliberately cannot share this
environment. Flag the addition as a prereq task if any Wave-1 file needs it.

---

## 1. Imports

| 0.x | 1.x |
| --- | --- |
| `from langchain.chains import X` | `from langchain_classic.chains import X` (or rewrite) |
| `from langchain.retrievers import X` | `from langchain_classic.retrievers import X` |
| `from langchain.indexes import index, SQLRecordManager` | `from langchain_classic.indexes import ...` |
| `from langchain import hub` | `from langchain_classic import hub` (or inline the prompt) |
| `from langchain.memory import X` | no equivalent — see §4 |
| `from langchain.schema import HumanMessage` | `from langchain_core.messages import HumanMessage` |
| `from langchain.schema import Document` | `from langchain_core.documents import Document` |
| `from langchain.schema.output_parser import StrOutputParser` | `from langchain_core.output_parsers import StrOutputParser` |
| `from langchain.text_splitter import X` | `from langchain_text_splitters import X` |
| `from langchain.document_loaders import X` | `from langchain_community.document_loaders import X` |
| `from langchain.vectorstores import Chroma` | `from langchain_chroma import Chroma` |
| `from langchain.embeddings import OpenAIEmbeddings` | `from langchain_openai import OpenAIEmbeddings` |
| `from langchain.chat_models import ChatOpenAI` | `from langchain_openai import ChatOpenAI` |
| `from langchain.globals import set_debug` | `from langchain_core.globals import set_debug` |
| `from langchain.evaluation import X` | `from langchain_classic.evaluation import X` |

New 1.x convenience re-exports worth teaching:
`langchain.agents`, `langchain.messages`, `langchain.tools`, `langchain.chat_models.init_chat_model`,
`langchain.embeddings`.

**Repo-specific:** LangGraph-phase notebooks must route model creation through
`from helpers import get_llm, get_embeddings` — if a flagged notebook lives under Phase 3/5/7/8 and
constructs `ChatOpenAI`/`ChatGroq` directly, note it but **do not "fix" it** in
`LangChain_Fundamentals/` or `RAG_Demystified`-sourced content, where direct instantiation is the
documented, accepted convention (see `CLAUDE.md`).

---

## 2. Agents

```python
# BEFORE (AgentExecutor era)
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a research assistant."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
executor.invoke({"input": "Who won the 2024 Turing Award?"})
```

```python
# AFTER (1.x)
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a research assistant.",
)
result = agent.invoke({"messages": [{"role": "user", "content": "Who won the 2024 Turing Award?"}]})
print(result["messages"][-1].text)
```

Fallout checklist when converting:

- `prompt=` → `system_prompt=` (and the `agent_scratchpad` placeholder disappears entirely).
- Output shape changes: `{"output": str}` → `{"messages": [...]}`. Every downstream
  `result["output"]` must become `result["messages"][-1].text`.
- `verbose=True` has no equivalent — use `.stream(..., stream_mode="values")` or LangSmith tracing.
- `return_intermediate_steps=True` → read tool calls off the message list.
- Custom state: TypedDict extending `AgentState` only.
- Pre-bound `model.bind_tools(tools)` → pass `model` and `tools=` separately.
- Stream/node filters on `"agent"` → `"model"`.
- `pre_model_hook` / `post_model_hook` → middleware.
- `handle_parsing_errors` → `wrap_model_call` middleware, or just drop it (tool calling is native now).

---

## 3. Middleware (replaces hooks, callbacks-for-control, and hand-rolled graphs)

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    SummarizationMiddleware, HumanInTheLoopMiddleware, PIIRedactionMiddleware,
    before_model, after_model,
)

@before_model
def inject_context(state, runtime):
    return {"messages": [{"role": "system", "content": f"User tier: {runtime.context.tier}"}]}

agent = create_agent(model, tools, middleware=[inject_context, SummarizationMiddleware(...)])
```

Map old → new:

| 0.x mechanism | 1.x middleware hook |
| --- | --- |
| `pre_model_hook` (trim/summarize history) | `before_model` / `SummarizationMiddleware` |
| `post_model_hook` (guardrail on output) | `after_model` |
| retry/fallback wrapper around the LLM call | `wrap_model_call` |
| tool approval / confirmation prompt | `HumanInTheLoopMiddleware` |
| manual PII scrubbing before send | `PIIRedactionMiddleware` |
| `AgentExecutor(max_iterations=N)` | middleware that ends the loop, or agent-level limits |

---

## 4. Memory

```python
# BEFORE
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

memory = ConversationBufferMemory()
chain = ConversationChain(llm=llm, memory=memory)
chain.predict(input="Hi, I'm Sourav")
chain.predict(input="What's my name?")
```

```python
# AFTER
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(model=llm, tools=[], checkpointer=InMemorySaver())
cfg = {"configurable": {"thread_id": "demo-1"}}
agent.invoke({"messages": [{"role": "user", "content": "Hi, I'm Sourav"}]}, cfg)
agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, cfg)
```

| 0.x memory class | 1.x replacement |
| --- | --- |
| `ConversationBufferMemory` | checkpointer + `thread_id` (full history is the default) |
| `ConversationBufferWindowMemory(k=N)` | `before_model` middleware trimming to last N, or `trim_messages` |
| `ConversationSummaryMemory` / `...SummaryBufferMemory` | `SummarizationMiddleware(max_tokens_before_summary=...)` |
| `VectorStoreRetrieverMemory` | LangGraph `Store` (semantic long-term memory) |
| `ConversationEntityMemory` / `ConversationKGMemory` | `Store` + an extraction step; no drop-in |
| `CombinedMemory` | compose multiple middleware |

Persistent variants: `PostgresSaver` / `SqliteSaver` instead of `InMemorySaver`.
Worked examples already in-repo: `07_Advanced_Agentic_Systems/Memory_and_State/`.

---

## 5. Chains → LCEL

```python
# BEFORE
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
chain.run(topic="quantum computing")

# AFTER
from langchain_core.output_parsers import StrOutputParser
chain = prompt | llm | StrOutputParser()
chain.invoke({"topic": "quantum computing"})
```

```python
# BEFORE
from langchain.chains import RetrievalQA
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
qa.run(query)

# AFTER (LCEL)
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)
rag.invoke(query)
```

```python
# AFTER (agentic — preferred for Phase 8 material)
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def search_docs(query: str) -> str:
    """Search the knowledge base."""
    return "\n\n".join(d.page_content for d in retriever.invoke(query))

agent = create_agent(llm, [search_docs], system_prompt="Answer using search_docs.")
```

| Legacy chain | Rewrite |
| --- | --- |
| `LLMChain` | `prompt \| llm \| StrOutputParser()` |
| `SimpleSequentialChain` / `SequentialChain` | pipe runnables, or `RunnableParallel` for fan-out |
| `ConversationChain` | `create_agent` + checkpointer |
| `RetrievalQA` / `ConversationalRetrievalChain` | LCEL retrieval chain, or retriever-as-tool agent |
| `load_summarize_chain("stuff")` | `prompt \| llm` over joined docs |
| `load_summarize_chain("map_reduce")` | LangGraph map-reduce with `Send` (Phase 5 orchestrator-worker) |
| `create_extraction_chain` / `create_tagging_chain` | `llm.with_structured_output(Schema)` |
| `LLMRouterChain` / `MultiPromptChain` | LangGraph conditional edge, or `create_agent` tool choice |
| `LLMMathChain` / `APIChain` / `SQLDatabaseChain` | a `@tool` the agent calls |

`.run()` / `.predict()` / `.apply()` all become `.invoke()` / `.batch()` / `.stream()`.

---

## 6. Messages and content blocks

```python
# BEFORE — provider-specific digging
text = resp.content if isinstance(resp.content, str) else resp.content[0]["text"]
reasoning = resp.additional_kwargs.get("reasoning_content")

# AFTER — provider-agnostic
text = resp.text                        # property, not resp.text()
for block in resp.content_blocks:
    if block["type"] == "reasoning":
        print(block["reasoning"])
    elif block["type"] == "citation":
        print(block)
```

Also: `AIMessage(..., example=True)` → drop the kwarg; `FunctionMessage`/`function_call` →
`ToolMessage`/`tool_calls`; chat model `.invoke()` now returns `AIMessage` (not `BaseMessage`),
so `isinstance` checks can tighten.

---

## 7. What NOT to flag as work

These are unchanged on 1.x — if a plan proposes touching them, it's wrong:

- LCEL itself: `|`, `Runnable`, `RunnableParallel`, `RunnablePassthrough`, `RunnableLambda`,
  `.batch()`, `.stream()`, `.astream()`, `.with_retry()`, `.with_fallbacks()`.
- `ChatPromptTemplate`, `PromptTemplate`, `FewShotPromptTemplate`, `MessagesPlaceholder`.
- `StrOutputParser`, `JsonOutputParser`, `PydanticOutputParser`, `with_structured_output`.
- Partner package classes: `ChatOpenAI`, `ChatGroq`, `ChatAnthropic`, `OpenAIEmbeddings`, …
- Text splitters, document loaders, vector stores (in their post-0.2 homes).
- `@tool` decorator and `StructuredTool`.
- Everything in Phase 3 `03_LangGraph_Fundamentals/` that builds `StateGraph` by hand —
  LangGraph 1.x kept its API; only the *prebuilt* `create_react_agent` shortcut is superseded.
