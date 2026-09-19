# OpenAI Applied AI Engineer — Decomp Round: Coverage & Gap Analysis

Prepared against the two resources OpenAI HR sent ahead of the Decomposition round:

- [Building Agents](https://developers.openai.com/tracks/building-agents) — OpenAI's own agent-building learning track
- [Evaluation Best Practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices?api-mode=responses) — OpenAI's eval-design guide

The Decomp round is discussion-based: clarify requirements, decompose an ambiguous agentic-system problem, discuss design choices and tradeoffs, and explain how you'd assess/improve the solution in practice. No coding. This doc maps every topic in the two resources to where — if anywhere — this repo already has hands-on coverage, then names what's genuinely missing.

---

## 1. "Building Agents" track — topic-by-topic coverage

| Module | Topic | Repo coverage | Status |
|---|---|---|---|
| 1. Core Concepts | Reasoning vs. non-reasoning model selection | No dedicated notebook framing this tradeoff explicitly | ❌ Gap |
| 1. Core Concepts | Responses API (OpenAI's own stateful core API) | Not used anywhere — repo is LangChain/LangGraph-native | ❌ Gap |
| 1. Core Concepts | Agents SDK (OpenAI's own) | `06_Agent_SDKs_First_Party/OpenAI_Agents_SDK/` — 🚧 Planned, empty | ❌ Gap |
| 1. Core Concepts | Augmenting agents with tools (function calling vs. built-ins) | `03_LangGraph_Fundamentals/01_Foundations/05_Augmented_LLM_with_Tools.ipynb`, `06_ReAct_Agent.ipynb`; `05_AI_Agent_Fundamentals/LangChain_Tools_and_Agents/01_Tools_and_Functions/` | ✅ Strong |
| 2. Tools | Function calling mechanics | Phase 3 `bind_tools` notebooks; Phase 5 `01_Tools_and_Functions/` (4 nb), `02_Agents/` | ✅ Strong |
| 2. Tools | Web Search built-in tool | Tavily-based web search used across `05_AI_Agent_Fundamentals/AI_Agents_with_LangGraph/01_Research_Assistant_Chatbot.ipynb` and others — same concept, different (non-OpenAI-hosted) provider | 🟡 Partial |
| 2. Tools | File Search (RAG) | `04_Retrieval_and_RAG/` (entire phase) + `08_Advanced_RAG/` — chunking, embedding, retrieval, reranking, context integration | ✅ Strong |
| 2. Tools | Code Interpreter (hosted sandbox tool) | `05_AI_Agent_Fundamentals/AI_Agents_with_LangGraph/05_Reflective_Code_Generation_Agent/` covers code-generating agents, but not the "hosted sandbox the model calls as a tool" pattern | 🟡 Partial |
| 2. Tools | Computer Use | No coverage anywhere in the repo | ❌ Gap |
| 2. Tools | Image Generation as an agent tool call | `01_Theory_and_Foundations/Model_Landscape_and_Hugging_Face/02_Diffusers/` covers image-gen *models*, not an agent calling image-gen mid-conversation as a tool | 🟡 Partial |
| 2. Tools | MCP (Model Context Protocol) | `09_Agent_Protocols/MCP/` (all 4 tracks: foundations, building servers, building clients, applications) + `08_Advanced_RAG/mcp_a2a_agentic_rag/` | ✅ Strong |
| 3. Orchestration | Agent / Handoff / Guardrail / Session primitives (OpenAI SDK vocabulary) | Equivalent concepts exist under different names: handoffs → `07_Advanced_Agentic_Systems/Multi_Agent_Orchestration/Production_Course_Multi_Agent/03_agent_handoffs.ipynb`; sessions/memory → `07_Advanced_Agentic_Systems/Memory_and_State/`; guardrails → `12_Production_and_Observability/Safety_and_Alignment/` | 🟡 Partial (concept yes, OpenAI's exact vocabulary no) |
| 3. Orchestration | Multi-agent collaboration (routing agent, agent-as-tool) | `07_Advanced_Agentic_Systems/Multi_Agent_Orchestration/` (supervisor + swarm), `03_LangGraph_Fundamentals/02_Core_Capabilities/02_Routing/`, CrewAI/AutoGen in `10_Alternative_Agent_Frameworks/` | ✅ Strong |
| 4. Example Use Cases | Human-in-the-loop support agent | `03_LangGraph_Fundamentals/02_Core_Capabilities/03_Human_in_the_Loop/` (4 nb: basics, interrupt/resume, state modification, dynamic breakpoints) | ✅ Strong |
| 4. Example Use Cases | Customer service agent networks | `03_LangGraph_Fundamentals/02_Core_Capabilities/02_Routing/` (router agentic RAG), `08_Advanced_RAG/RAG_with_LangGraph_Advanced/1. Build_a_Healthcare_Customer_Support_Router_Agentic_RAG_System.ipynb` | ✅ Strong |
| 4. Example Use Cases | Frontend testing agent using computer vision | No coverage — same gap as Computer Use above | ❌ Gap |
| 4. Example Use Cases | Optimization priorities (speed / reliability / cost) | `12_Production_and_Observability/LLMOps_and_AI_Infrastructure/Cost_Monitoring/01_LLM_Cost_Monitoring.ipynb`, `Caching_and_Performance/` — covered as infra, not framed as an upfront design-choice lever | 🟡 Partial |
| 5. Best Practices | User input guardrails (jailbreak prevention) | `12_Production_and_Observability/Safety_and_Alignment/01_Moderating_Chains.ipynb`; `03_Production_Course/07_error_handling.ipynb`; `Production_Course_Ops/03_security_patterns.ipynb` (prompt-injection/guardrail pedagogy) | ✅ Strong |
| 5. Best Practices | Structured outputs | `03_LangGraph_Fundamentals/01_Foundations/08_Pydantic_State_Validation.ipynb`; `05_AI_Agent_Fundamentals/AI_Agents_with_LangGraph/02_Competitive_Intelligence_Agent.ipynb`; `4. Workflow_Pattern/1. Prompt_Chaining/02_Prompt_Chaining_Structured_Output.ipynb` | ✅ Strong |
| 5. Best Practices | Production optimization (cost/latency/monitoring/deployment) | `12_Production_and_Observability/` (whole phase) + `Production_Course_Ops/01_monitoring.ipynb`, `02_cost_optimization.ipynb` | ✅ Strong |

---

## 2. "Evaluation Best Practices" guide — topic-by-topic coverage

| Topic | Repo coverage | Status |
|---|---|---|
| Eval types: industry benchmarks, standard scores, custom app-specific tests | `07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/Tutorial_RAG_Agent_Tool_Evaluation/` (Modules 0-5, evaluation landscape → capstone) | ✅ Strong |
| Eval-driven development methodology / continuous eval | Implicit across `Evaluation_and_Eval_Harnesses/`, but no notebook frames it as a development *process* the way the guide does | 🟡 Partial |
| 5-step eval workflow (objective → dataset → metrics → run/compare → continuous) | Closest match: `RAG_Evaluation/4. End_to_End_RAG_System_Evaluation.ipynb`; process framing itself is closer to `15_FDE_Related_Preparation/.../ch12_validation_and_measurement.md` than to a hands-on notebook | 🟡 Partial |
| Single-turn / workflow eval (instruction following, functional correctness) | `RAG_Evaluation/2.Generator_Evaluation_Metrics.ipynb` | ✅ Strong |
| Single-agent eval (tool selection accuracy, argument extraction) | `Agent_Evaluation/DeepLearningAI_Arize/Lab 3 - Adding Router & Skill Evaluations/L7.ipynb` | ✅ Strong |
| Multi-agent eval (handoff accuracy, per-agent specialization) | `Agent_Evaluation/DeepLearningAI_Arize/Lab 4 - Adding Trajectory Evaluations/L9.ipynb`; `Tutorial_RAG_Agent_Tool_Evaluation/` Module 4 (agent trajectory eval) | ✅ Strong |
| Metric-based evals (exact match, ROUGE/BLEU, function-call accuracy) | `RAG_Evaluation/1.Retriever_Evaluation_Metrics.ipynb`, `DeepEval_Metrics/` (contextual precision/recall/relevancy) | ✅ Strong |
| Human evaluation (blinded comparison, consensus voting) | No dedicated hands-on notebook — theory only, in `ch12_validation_and_measurement.md` | ❌ Gap |
| LLM-as-a-judge (pairwise, single-answer, reference-guided) | `RAG_Evaluation/3.Custom_LLM_as_a_Judge _(G-Eval).ipynb`; `LLM_as_Judge/DeepEval_GEval/test_firstdeepeval.py` | ✅ Strong |
| Edge-case eval design (multilingual, format variety, circular handoffs, jailbreak resistance in eval sets) | Not built as eval-set design content — jailbreak coverage exists only as *production* guardrails (`Safety_and_Alignment/`), not as an adversarial eval-dataset practice | ❌ Gap |
| Using eval insight to drive a reinforcement fine-tuning flywheel | `01_Theory_and_Foundations/Fine_Tuning_and_RL/02_Techniques/` (RLHF/DPO/LoRA) — 🚧 Planned, empty | ❌ Gap |

---

## 3. Net gaps (the ones worth actually closing before the interview)

Everything below is a repeat theme, not five separate ones: **the repo has almost no first-party OpenAI agent-primitive coverage.** All the orchestration/guardrail/handoff/tracing depth here is real, but it's expressed in LangGraph/CrewAI/AutoGen vocabulary, not OpenAI's own.

1. **Responses API** and **Agents SDK** — `06_Agent_SDKs_First_Party/OpenAI_Agents_SDK/` is a placeholder folder with no notebooks.
2. **Computer Use** — zero coverage; no analogue anywhere in the repo.
3. **Code Interpreter / Image Generation as hosted agent tools** — model-level coverage exists (Phase 1), tool-calling-pattern coverage doesn't.
4. **Human evaluation practice** (blinded review, consensus voting) and **adversarial/edge-case eval-set design** — the repo's eval strength is metrics and LLM-as-judge, not eval-set construction discipline.
5. **RLHF/DPO/LoRA** and the eval → fine-tuning flywheel — explicitly planned, not built.

## 4. What actually moves the needle for this specific round

This is a decomposition/discussion interview, not a build check — so the fix isn't "go build 5 more notebooks," it's:

- **Vocabulary mapping** (cheap, ~15-30 min): skim the Agents SDK and Responses API docs and mentally re-tag what you already know — supervisor pattern → `Handoff`, moderation chain → `Guardrail`, LangGraph checkpointing → `Session`. The architectural judgment already transfers; only the OpenAI-specific nouns are missing.
- **Rehearse the decomposition format out loud**, not silently: `15_FDE_Related_Preparation/Cracking_Agentic_AI_System_Design_Interviews/ch28_system_design_interview.md` already has the 45-minute script, two worked designs, and a levelling rubric for exactly this interview shape — that's higher-leverage prep time than closing any single content gap above.
- If there's time left, skim the OpenAI eval guide's **edge-case list** (multilingual, circular handoffs, ambiguous tool responses) once more right before the interview — it's the one area where the guide's framing genuinely differs from how this repo teaches evaluation.
