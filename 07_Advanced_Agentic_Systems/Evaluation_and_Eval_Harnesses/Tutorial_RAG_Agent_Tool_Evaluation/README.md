# RAG, Agent & Tool Evaluation — Tutorial

**Status:** ✅ Built — all modules (0 through 5) complete. See `../TUTORIAL_PLAN.md` for the full build plan, source mapping, and build-time notes.

A single, ordered learning path through everything this repo has for evaluating RAG systems, tool-calling agents, and multi-turn conversational agents — pulled together from the notebooks and scripts previously scattered across `RAG_Evaluation/`, `Agent_Evaluation/`, `multi-turn eval and tool evaluations/`, and `04_Agent_RAG_Eval/`. Nothing was deleted from those folders; this tutorial is additive and, where a module references material with real relative-path or live-service dependencies (Module 4's Arize labs, Module 5's CrewAI app), links to it in place rather than copying it.

**Target environment:** `deepeval==4.1.8` (repo root `.venv`). If you run an original source notebook directly instead of this tutorial's version, check that notebook's own folder for a different pin first.

**📖 [`TUTORIAL.md`](TUTORIAL.md)** — the theory-only companion to everything below: taxonomy, reference-based vs. referenceless, LLM-as-judge failure modes, every metric's definition and when to reach for it, and a master quick-reference table — with no code, no API calls, and no environment needed. Read it standalone (to study or prep for an interview) or alongside the notebooks as a concept lookup.

## Table of contents

| # | Notebook | Covers | Status |
|---|---|---|---|
| 0 | [`00_Evaluation_Landscape.ipynb`](00_Evaluation_Landscape.ipynb) | Taxonomy of RAG/agent evaluation, reference-based vs. referenceless, LLM-as-judge and its failure modes, the DeepEval/RAGAS/MLflow/Arize tooling landscape, and a question → module/metric lookup table | ✅ Built |
| 1.1 | [`01_Retrieval_Metrics_Deterministic.ipynb`](01_Retrieval_Metrics_Deterministic.ipynb) | Precision@K, Recall@K, MRR, nDCG — no API calls | ✅ Built (executed) |
| 1.2 | [`02_Retrieval_Metrics_LLM_Judged.ipynb`](02_Retrieval_Metrics_LLM_Judged.ipynb) | Contextual Precision/Recall/Relevancy — condensed from the 3 `DeepEval_Metrics/` drill notebooks, hand-constructed test cases (no live-pipeline dependency) | ✅ Built (not executed — needs `OPENAI_API_KEY`) |
| 1.3 | [`03_Generator_Metrics_Referenceless.ipynb`](03_Generator_Metrics_Referenceless.ipynb) | Faithfulness, Answer Relevancy, Hallucination (DeepEval + RAGAS) | ✅ Built (not executed — needs `OPENAI_API_KEY`) |
| 1.4 | [`04_Generator_Metrics_Reference_Based.ipynb`](04_Generator_Metrics_Reference_Based.ipynb) | Answer Correctness (custom `GEval`, both `criteria`- and `evaluation_steps`-based), Answer Semantic Similarity | ✅ Built (not executed — needs `OPENAI_API_KEY`) |
| 1.5 | [`05_RAG_Eval_Inside_the_Pipeline.ipynb`](05_RAG_Eval_Inside_the_Pipeline.ipynb) | Evaluation wired in as LangGraph nodes — mocked (executed) then real (needs `OPENAI_API_KEY`) | ✅ Built |
| 1.6 | [`06_RAGAS_in_Practice.ipynb`](06_RAGAS_in_Practice.ipynb) | RAGAS quickstart + multi-metric example + the pytest/Excel/live-backend CI pattern | ✅ Built (not executed — needs `OPENAI_API_KEY`) |
| 1.7 | [`07_RAG_Capstone_Build_and_Evaluate.ipynb`](07_RAG_Capstone_Build_and_Evaluate.ipynb) | Build a real RAG system (Chroma + the phase's shared dataset), synthesize a golden dataset, run the full metric suite end-to-end | ✅ Built (not executed — needs `OPENAI_API_KEY`; data-loading path verified) |
| 2.1 | [`08_MultiTurn_Conversational_Evaluation.ipynb`](08_MultiTurn_Conversational_Evaluation.ipynb) | `ConversationalGEval`, `TurnRelevancyMetric`, `KnowledgeRetentionMetric`, conversation simulation | ✅ Built (not executed — needs `OPENAI_API_KEY`) |
| 2.2 | [`09_Tool_Use_Evaluation.ipynb`](09_Tool_Use_Evaluation.ipynb) | `ToolCorrectnessMetric`, `ArgumentCorrectnessMetric`, `ToolUseMetric` | ✅ Built (not executed — needs `OPENAI_API_KEY`) |
| 2.3 | [`10_Task_Completion_Evaluation.ipynb`](10_Task_Completion_Evaluation.ipynb) | `TaskCompletionMetric`, custom `GEval` rubrics, outcome verification | ✅ Built (not executed — needs `OPENAI_API_KEY`) |
| 2.4 | [`11_Same_Evals_with_MLflow.ipynb`](11_Same_Evals_with_MLflow.ipynb) | Modules 2.1–2.2's questions, reimplemented via `mlflow.genai.evaluate()` (`Guidelines`, `make_judge`, `@scorer` over `Trace`/`SpanType.TOOL`) | ✅ Built (not executed — needs `OPENAI_API_KEY`; local SQLite MLflow store) |
| 3 | [`12_Agent_Trajectory_Evaluation.ipynb`](12_Agent_Trajectory_Evaluation.ipynb) | Simple mocked trajectory scoring, then the full 9-metric trace-level suite (mocked, executed) on a realistic refund-agent scenario + Databricks mapping table, then a real tool-calling agent (needs `OPENAI_API_KEY`) | ✅ Built (Parts A–B executed; Part C needs `OPENAI_API_KEY`) |
| 4 | [`13_Production_Grade_Agent_Eval_Overview.ipynb`](13_Production_Grade_Agent_Eval_Overview.ipynb) + links to the 5 Arize labs (left in place at `../Agent_Evaluation/DeepLearningAI_Arize/`) | Live tracing + offline experiments (Arize Phoenix); concept map from each lab back to Modules 1–3's vocabulary | ✅ Built (bridge notebook; labs need their own env — see notebook's Prerequisites) |
| 5 | [`14_Capstone_CrewAI_Travel_Planner_Eval.ipynb`](14_Capstone_CrewAI_Travel_Planner_Eval.ipynb) | `TaskCompletionMetric` (Module 2.3) batch-scored against a real running 3-agent CrewAI app, left in place at `../Agent_Evaluation/CrewAI_Travel_Planner/` | ✅ Built (walkthrough; app is a separate live process — see notebook's Standing up the app) |

**If you only have an hour:** Module 0 → 1.2 → 2.2 → 3.

## Related, but out of scope for this tutorial

- `07_Advanced_Agentic_Systems/Evaluation_and_Eval_Harnesses/red_teaming/` and `12_Production_and_Observability/Safety_and_Alignment/02_Red_Teaming_Agents_and_RAG.ipynb` — adversarial/safety testing (`deepteam`) answers "can this be made to misbehave?", a different question from the quality evaluation covered here.
