# OpenAI "Building Agents" Track — Repo Coverage

Maps every topic in OpenAI's [Building Agents track](https://developers.openai.com/tracks/building-agents)
to where this repo teaches it, and names what is genuinely missing.

**Checked against disk 2026-09-19.** Every path below was verified to exist.

**The headline:** the repo covers the *concepts* well and the *OpenAI-specific surface* poorly.
Agent loops, tool calling, routing, handoffs, memory, guardrails, structured output and
RAG are all taught in depth — through LangChain/LangGraph. What is thin is OpenAI's own
primitives: the Responses API, the Agents SDK beyond one foundations notebook, and the
five server-side hosted tools.

| | Count |
|---|---|
| ✅ Covered | 11 |
| 🟡 Partial — concept taught, OpenAI's implementation not | 8 |
| ❌ Gap | 4 |

---

## 1. Core Concepts

| Track topic | Repo coverage | Status |
|---|---|---|
| Reasoning vs. non-reasoning model choice; reasoning-effort levers | No notebook frames this as a design decision. `helpers/get_llm()` abstracts provider choice away, which is the opposite emphasis. `reasoning_effort` appears nowhere | ❌ Gap |
| **Responses API** (OpenAI's stateful core API) | Named in three places, used in none. The repo is LangChain/LangGraph-native and calls chat-completions style APIs | ❌ Gap |
| **Agents SDK** (OpenAI's own) | `03_Advanced/06_Agent_SDKs_First_Party/OpenAI_Agents_SDK/01_Foundations/01_Agents_Handoffs_Guardrails.ipynb` — 23 cells covering Agent, tools, handoffs and input guardrails, with an explicit LangGraph comparison. The track's other three folders are scope READMEs | 🟡 Partial |
| Augmenting agents with tools | `02_Core/03_LangGraph_Fundamentals/01_Foundations/` (`05_Augmented_LLM_with_Tools.ipynb`), `02_Core/05_AI_Agent_Fundamentals/2. LangChain_Tools_and_Agents/01_Tools_and_Functions/` | ✅ Covered |

## 2. Tools

| Track topic | Repo coverage | Status |
|---|---|---|
| Function calling mechanics | `02_Core/05_AI_Agent_Fundamentals/2. LangChain_Tools_and_Agents/01_Tools_and_Functions/`, plus `5. Agent Pattern/01_Tool_Use/02_Tool_Calling_vs_ReAct.ipynb` | ✅ Covered |
| Function calling **vs. hosted built-ins** — the architectural split | Not framed anywhere. The repo always executes tools client-side; "the model calls a tool that runs on OpenAI's infrastructure" is a different failure/latency/cost model and is never contrasted | ❌ Gap |
| Web search | Tavily throughout, e.g. `02_Core/05_AI_Agent_Fundamentals/3. AI_Agents_with_LangGraph/01_Research_Assistant_Chatbot.ipynb`. Same concept, client-side provider | 🟡 Partial |
| File search (managed RAG) | `02_Core/04_Retrieval_and_RAG/` and `03_Advanced/08_Advanced_RAG/` — chunking, embeddings, vector stores, retrieval, reranking. Far deeper than the track. What is absent is the *managed* vector store where you hand OpenAI the files | ✅ Covered |
| Code interpreter | `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/05_SWE_Agent_Applied.ipynb` and `3. AI_Agents_with_LangGraph/05_Reflective_Code_Generation_Agent/` teach code-writing agents; the hosted-sandbox-as-a-tool pattern is not shown | 🟡 Partial |
| Computer use | `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/06_BrowserAgent_Computer_Use_Applied.ipynb` — a 20-cell build over a deterministic mock browser exposed as tools, driven by a ReAct loop. Teaches the pattern; no screenshot/vision loop against a real GUI | 🟡 Partial |
| Image generation as a mid-conversation tool call | `01_Foundations/00_Theory_and_Foundations/Model_Landscape_and_Hugging_Face/02_Diffusers/` covers image-generation *models*. An agent deciding to generate an image as a tool call is not shown | 🟡 Partial |
| MCP | `03_Advanced/09_Agent_Protocols/MCP/` — foundations, building servers, building clients, applications, plus `04_Applications/mcp_a2a_agentic_rag/`. Deeper than the track | ✅ Covered |

## 3. Orchestration

| Track topic | Repo coverage | Status |
|---|---|---|
| Agent loop management | `02_Core/03_LangGraph_Fundamentals/` (whole phase) | ✅ Covered |
| Handoffs | `03_Advanced/07_Advanced_Agentic_Systems/Multi_Agent_Orchestration/Production_Course_Multi_Agent/03_agent_handoffs.ipynb`, plus the OpenAI-SDK version in the foundations notebook above | ✅ Covered |
| Guardrails | `03_Advanced/12_Production_and_Observability/Safety_and_Alignment/01_Moderating_Chains.ipynb`, `Production_Course_Ops/03_security_patterns.ipynb` | ✅ Covered |
| Sessions / automatic history | `03_Advanced/07_Advanced_Agentic_Systems/Memory_and_State/` (22 notebooks) and LangGraph checkpointing. OpenAI's `Session` object and `conversation_id` sharing specifically are not used | 🟡 Partial |
| Tracing | `03_Advanced/12_Production_and_Observability/LLMOps_and_AI_Infrastructure/Tracing_and_Observability/LangSmith/01_LangSmith_Basics.ipynb`. LangSmith, not OpenAI's built-in tracing dashboard | 🟡 Partial |
| Multi-agent collaboration: routing, agent-as-tool, parallelization | `03_Advanced/07_Advanced_Agentic_Systems/Multi_Agent_Orchestration/` (supervisor, swarm), `02_Core/03_LangGraph_Fundamentals/02_Core_Capabilities/02_Routing/`, CrewAI + AutoGen in `03_Advanced/10_Alternative_Agent_Frameworks/` | ✅ Covered |

## 4. Example Use Cases

| Track topic | Repo coverage | Status |
|---|---|---|
| Support agent with human-in-the-loop | `02_Core/03_LangGraph_Fundamentals/02_Core_Capabilities/03_Human_in_the_Loop/` | ✅ Covered |
| Customer-service agent network | `03_Advanced/08_Advanced_RAG/Agentic_RAG/1. Build_a_Healthcare_Customer_Support_Router_Agentic_RAG_System.ipynb`, `05_Projects/AI_Powered_Customer_Support/` | ✅ Covered |
| Frontend testing agent (computer use) | Nearest is the mock-browser notebook above. No real browser automation, no vision loop, no test-assertion framing | ❌ Gap |
| Optimizing for speed / reliability / cost as an upfront choice | `03_Advanced/12_Production_and_Observability/LLMOps_and_AI_Infrastructure/` and `06_Interview_Prep/Study_Guides/Cost_Latency_Optimization/` (playbook, cram sheets, drill decks) cover this well — as operations, and the Study_Guides material does frame it as design levers | ✅ Covered |

## 5. Best Practices

| Track topic | Repo coverage | Status |
|---|---|---|
| Input guardrails, jailbreak prevention | `03_Advanced/12_Production_and_Observability/Safety_and_Alignment/`, `Production_Course_Ops/03_security_patterns.ipynb` | ✅ Covered |
| Structured outputs | `02_Core/01_LangChain_Fundamentals/07_LangChain_1x_Agents_and_Middleware/7.4_Structured_Output.ipynb`, `02_Core/03_LangGraph_Fundamentals/01_Foundations/08_Pydantic_State_Validation.ipynb` | ✅ Covered |
| Output guardrails | Covered as moderation; a separate output-validation stage before display is thinner | 🟡 Partial |
| Production monitoring | `03_Advanced/12_Production_and_Observability/` (whole phase) | ✅ Covered |

---

## The four real gaps

1. **Responses API** — never used. Everything routes through LangChain abstractions, so the
   stateful-by-default request model is not experienced anywhere.
2. **Reasoning-model selection as a design decision** — `helpers/get_llm()` deliberately hides
   provider and model choice, which is useful for teaching but means the "which model, and how
   much reasoning effort" tradeoff is never posed.
3. **Hosted tools vs. client-side tools** — the repo executes every tool locally. The
   architectural consequences of server-side execution are not discussed.
4. **Real computer use / frontend testing** — the mock-browser notebook teaches the loop shape
   but stops before screenshots, vision and a live GUI.

The natural home for the first three is
`03_Advanced/06_Agent_SDKs_First_Party/OpenAI_Agents_SDK/`, whose `02_Core_Capabilities/`,
`03_Multi_Agent_Patterns/` and `04_Applications/` folders are scope READMEs today. The fourth
extends `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/`.

## Related

`06_Interview_Prep/OpenAI_Applied/OpenAI_Applied_AI_Engineer_Coverage_Gap_Analysis.md` analyses
this same track alongside OpenAI's Evaluation Best Practices guide, scoped to interview prep.
Its section 1 now points here rather than restating the mapping — it had drifted, claiming the
Agents SDK track was empty and that computer use had no coverage, both of which were out of date.
