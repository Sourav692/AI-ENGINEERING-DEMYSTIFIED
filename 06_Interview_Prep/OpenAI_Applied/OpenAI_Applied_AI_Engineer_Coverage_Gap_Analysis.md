# OpenAI Applied AI Engineer — Decomp Round: Coverage & Gap Analysis

Prepared against the two resources OpenAI HR sent ahead of the Decomposition round:

- [Building Agents](https://developers.openai.com/tracks/building-agents) — OpenAI's own agent-building learning track
- [Evaluation Best Practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices?api-mode=responses) — OpenAI's eval-design guide

The Decomp round is discussion-based: clarify requirements, decompose an ambiguous agentic-system problem, discuss design choices and tradeoffs, and explain how you'd assess/improve the solution in practice. No coding. This doc maps every topic in the two resources to where — if anywhere — this repo already has hands-on coverage, then names what's genuinely missing.

---

## 1. "Building Agents" track — topic-by-topic coverage

**Moved to [`OPENAI_BUILDING_AGENTS_COVERAGE.md`](../../OPENAI_BUILDING_AGENTS_COVERAGE.md) at
the repo root (2026-09-19).** The table that used to sit here had drifted: it recorded the
OpenAI Agents SDK track as "🚧 Planned, empty" when it has a 23-cell foundations notebook, said
computer use had "no coverage anywhere" when
`02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/06_BrowserAgent_Computer_Use_Applied.ipynb`
exists, and cited 12 paths that the restructure had invalidated.

Rather than keep two mappings of the same track in sync, the root file is now the single
source and every path in it is verified against disk. Summary of what it found: **11 covered,
8 partial, 4 real gaps** — the repo teaches the concepts thoroughly through LangChain/LangGraph
and is thin on OpenAI's own surface (Responses API, the Agents SDK past foundations, and the
five hosted tools).

The four gaps worth closing for this round: the Responses API, reasoning-model selection as a
design lever, hosted-vs-client-side tool execution, and real computer use.

---

## 2. "Evaluation Best Practices" guide — topic-by-topic coverage

> **⚠ Read the statuses below as describing the sibling repo, not this one.** Evaluation was
> removed from this repo on 2026-09-19 — 147 files, verified by content hash as duplicated,
> none unique — and lives in **`Agent_Evaluation_Demystified`**. Every `Evaluation_and_Eval_Harnesses/`,
> `RAG_Evaluation/`, `Agent_Evaluation/` and `LLM_as_Judge/` path below resolves *there*. For this
> repo, evaluation is a blanket gap by design; see the root `CLAUDE.md`. The mapping is kept
> because the material still exists and is still what you would revise from.

| Topic | Coverage (in `Agent_Evaluation_Demystified` unless noted) | Status |
|---|---|---|
| Eval types: industry benchmarks, standard scores, custom app-specific tests | `03_Advanced/07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/Tutorial_RAG_Agent_Tool_Evaluation/` (Modules 0-5, evaluation landscape → capstone) | ✅ Strong *(moved 2026-09-19 to the sibling repo `Agent_Evaluation_Demystified`; not in this repo)* |
| Eval-driven development methodology / continuous eval | Implicit across `Evaluation_and_Eval_Harnesses/`, but no notebook frames it as a development *process* the way the guide does | 🟡 Partial *(moved 2026-09-19 to the sibling repo `Agent_Evaluation_Demystified`; not in this repo)* |
| 5-step eval workflow (objective → dataset → metrics → run/compare → continuous) | Closest match: `RAG_Evaluation/4. End_to_End_RAG_System_Evaluation.ipynb`; process framing itself is closer to `06_Interview_Prep/FDE/.../ch12_validation_and_measurement.md` than to a hands-on notebook | 🟡 Partial |
| Single-turn / workflow eval (instruction following, functional correctness) | `RAG_Evaluation/2.Generator_Evaluation_Metrics.ipynb` | ✅ Strong |
| Single-agent eval (tool selection accuracy, argument extraction) | `Agent_Evaluation/DeepLearningAI_Arize/Lab 3 - Adding Router & Skill Evaluations/L7.ipynb` | ✅ Strong |
| Multi-agent eval (handoff accuracy, per-agent specialization) | `Agent_Evaluation/DeepLearningAI_Arize/Lab 4 - Adding Trajectory Evaluations/L9.ipynb`; `Tutorial_RAG_Agent_Tool_Evaluation/` Module 4 (agent trajectory eval) | ✅ Strong *(moved 2026-09-19 to the sibling repo `Agent_Evaluation_Demystified`; not in this repo)* |
| Metric-based evals (exact match, ROUGE/BLEU, function-call accuracy) | `RAG_Evaluation/1.Retriever_Evaluation_Metrics.ipynb`, `DeepEval_Metrics/` (contextual precision/recall/relevancy) | ✅ Strong |
| Human evaluation (blinded comparison, consensus voting) | No dedicated hands-on notebook — theory only, in `ch12_validation_and_measurement.md` | ❌ Gap |
| LLM-as-a-judge (pairwise, single-answer, reference-guided) | `RAG_Evaluation/3.Custom_LLM_as_a_Judge _(G-Eval).ipynb`; `LLM_as_Judge/DeepEval_GEval/test_firstdeepeval.py` | ✅ Strong |
| Edge-case eval design (multilingual, format variety, circular handoffs, jailbreak resistance in eval sets) | Not built as eval-set design content — jailbreak coverage exists only as *production* guardrails (`Safety_and_Alignment/`), not as an adversarial eval-dataset practice | ❌ Gap |
| Using eval insight to drive a reinforcement fine-tuning flywheel | `01_Theory_and_Foundations/Fine_Tuning_and_RL/02_Techniques/` (RLHF/DPO/LoRA) — 🚧 Planned, empty | ❌ Gap |

---

## 3. Net gaps (the ones worth actually closing before the interview)

Everything below is a repeat theme, not five separate ones: **the repo has almost no first-party OpenAI agent-primitive coverage.** All the orchestration/guardrail/handoff/tracing depth here is real, but it's expressed in LangGraph/CrewAI/AutoGen vocabulary, not OpenAI's own.

1. **Responses API** — never used anywhere; the repo is LangChain/LangGraph-native. The **Agents SDK** is
   no longer a blank: `03_Advanced/06_Agent_SDKs_First_Party/OpenAI_Agents_SDK/01_Foundations/01_Agents_Handoffs_Guardrails.ipynb`
   is a 23-cell build covering Agent, tools, handoffs and input guardrails. `02_Core_Capabilities/`,
   `03_Multi_Agent_Patterns/` and `04_Applications/` are still scope READMEs. *(Corrected 2026-09-19 —
   this line previously said the folder was empty.)*
2. **Computer Use** — partial, not zero. `02_Core/05_AI_Agent_Fundamentals/5. Agent Pattern/01_Tool_Use/06_BrowserAgent_Computer_Use_Applied.ipynb`
   builds a ReAct loop over a deterministic mock browser exposed as tools. What is missing is the
   screenshot/vision loop against a real GUI. *(Corrected 2026-09-19 — this line previously said
   there was no analogue anywhere.)*
3. **Code Interpreter / Image Generation as hosted agent tools** — model-level coverage exists (Phase 1), tool-calling-pattern coverage doesn't.
4. **Human evaluation practice** (blinded review, consensus voting) and **adversarial/edge-case eval-set design** — the repo's eval strength is metrics and LLM-as-judge, not eval-set construction discipline.
5. **RLHF/DPO/LoRA** and the eval → fine-tuning flywheel — explicitly planned, not built.

## 4. What actually moves the needle for this specific round

This is a decomposition/discussion interview, not a build check — so the fix isn't "go build 5 more notebooks," it's:

- **Vocabulary mapping** (cheap, ~15-30 min): skim the Agents SDK and Responses API docs and mentally re-tag what you already know — supervisor pattern → `Handoff`, moderation chain → `Guardrail`, LangGraph checkpointing → `Session`. The architectural judgment already transfers; only the OpenAI-specific nouns are missing.
- **Rehearse the decomposition format out loud**, not silently: `06_Interview_Prep/FDE/Cracking_Agentic_AI_System_Design_Interviews/ch28_system_design_interview.md` already has the 45-minute script, two worked designs, and a levelling rubric for exactly this interview shape — that's higher-leverage prep time than closing any single content gap above.
- If there's time left, skim the OpenAI eval guide's **edge-case list** (multilingual, circular handoffs, ambiguous tool responses) once more right before the interview — it's the one area where the guide's framing genuinely differs from how this repo teaches evaluation.
