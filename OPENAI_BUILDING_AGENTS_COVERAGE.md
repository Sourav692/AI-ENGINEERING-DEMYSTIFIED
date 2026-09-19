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
| ✅ Covered | 12 |
| 🟡 Partial — concept taught, OpenAI's implementation not | 9 |
| ❌ Gap | 2 |

---

## 1. Core Concepts

| Track topic | Repo coverage | Status |
|---|---|---|
| Reasoning vs. non-reasoning model choice; reasoning-effort levers | **Closed 2026-09-19.** `01_Foundations/00_Theory_and_Foundations/Reasoning_and_Model_Selection/` — `01_Reasoning_vs_NonReasoning.ipynb` (measured on identical tasks, including one where reasoning loses) and `02_Reasoning_Effort_Levers.ipynb` (effort swept, knee located, plus the case where effort is the wrong lever). Applied at `02_Core/05_AI_Agent_Fundamentals/4. Workflow_Pattern/2. Routing/notebooks/Routing_By_Model_Tier.ipynb`. `get_llm()` gained a `reasoning_effort` passthrough to make it reachable | ✅ Covered |
| **Responses API** (OpenAI's stateful core API) | **Re-checked 2026-09-20: it is used once**, in `02_Core/05_AI_Agent_Fundamentals/3. AI_Agents_with_LangGraph/10_Hotel_Reservations_Multi_Agent_System/Module_2_Core_Agents/1_Environment_Setup.ipynb` — a `client.responses.create(model=..., instructions=..., input=...)` smoke test reading `response.output_text`. It appears, it is not taught: no statefulness, no conversation chaining, no contrast with chat-completions, and the cell depends on `google.colab.userdata` so it will not run locally. `ChatOpenAI` also exposes `use_responses_api`, so the stack can reach it without new dependencies | 🟡 Partial |
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

## The two real gaps

*(Was four. Reasoning-model selection was **closed** 2026-09-19. The Responses API was
**downgraded to partial** 2026-09-20 — re-checking against disk found one real call that the
original sweep missed, because it searched for the phrase "Responses API" rather than for
`responses.create`.)*

1. **Hosted tools vs. client-side tools** — the repo executes every tool locally. The
   architectural consequences of server-side execution are not discussed.
2. **Real computer use / frontend testing** — the mock-browser notebook teaches the loop shape
   but stops before screenshots, vision and a live GUI.

Still worth building even though it is no longer a hard gap: **the Responses API as a
subject** — statefulness, `previous_response_id` chaining, and how it differs from
chat-completions. One smoke test in a Colab-only setup notebook is not coverage.

The natural home for the first is
`03_Advanced/06_Agent_SDKs_First_Party/OpenAI_Agents_SDK/`, whose `02_Core_Capabilities/`,
`03_Multi_Agent_Patterns/` and `04_Applications/` folders are scope READMEs today. The second
extends `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/`.

## Related

`06_Interview_Prep/OpenAI_Applied/OpenAI_Applied_AI_Engineer_Coverage_Gap_Analysis.md` analyses
this same track alongside OpenAI's Evaluation Best Practices guide, scoped to interview prep.
Its section 1 now points here rather than restating the mapping — it had drifted, claiming the
Agents SDK track was empty and that computer use had no coverage, both of which were out of date.
