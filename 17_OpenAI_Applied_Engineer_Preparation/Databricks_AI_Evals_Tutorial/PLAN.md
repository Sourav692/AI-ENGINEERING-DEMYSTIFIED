# Databricks AI Evals Tutorial — Build Plan

**Status:** Plan approved-pending — no notebooks built yet. This file is the persistent
reference for the phased build; tick items off as each phase lands. See
[Known Discrepancies](../../NOTEBOOK_INDEX.md) for how this repo tracks build history for
other tracks — this file plays the same role for this one.

## Why this track exists

Built in preparation for the OpenAI Applied AI Engineer Decomp round (see
`../OpenAI_Applied_AI_Engineer_Coverage_Gap_Analysis.md`). That analysis found the repo's
evaluation content strong on metrics and LLM-as-judge but with two specific gaps:
**human-eval calibration** (blinded review, consensus voting) and the **eval → improvement
flywheel** (using eval insight to drive systematic improvement). This track closes both,
using Databricks' MLflow 3 GenAI evaluation stack as the concrete implementation.

## Design philosophy

The agent is a means to an end, not the subject. One tiny LangGraph customer-support
agent (one retriever tool over a handful of toy docs + one deterministic lookup tool) gets
built once in Phase 1 and is never touched again except to deliberately break it for the
regression-detection phase. Every phase after that is entirely about evaluation — offline
metrics, custom scorers, judges, eval datasets, regression detection, and — the part most
eval tutorials skip — **online/production evaluation** via Unity Catalog trace ingestion
and continuous monitoring of live traffic.

Grounded against the `databricks-mlflow-evaluation` skill's `CRITICAL-interfaces.md` and
`GOTCHAS.md` (MLflow 3 GenAI API surface: `mlflow.genai.evaluate()`, built-in scorers,
judges, UC trace ingestion, production monitoring, MemAlign judge alignment, GEPA prompt
optimization) — not written from memory.

**Prompt versioning is explicit, not incidental.** MLflow's Prompt Registry
(`mlflow.genai.register_prompt`, `load_prompt`, `set_prompt_alias`) is introduced as its
own concept in Phase 5 as the mechanism behind regression detection — a prompt change is a
new registered version, evaluated before its alias (e.g. `@production`) moves — and then
reused, not re-taught, when Phase 8's GEPA loop registers and promotes its winning
candidate the same way.

## Prerequisites (needed before Phases 6–8 can actually run)

- A Databricks workspace + CLI profile (`databricks auth profiles`)
- A SQL warehouse ID (for UC trace ingestion / `MLFLOW_TRACING_SQL_WAREHOUSE_ID`)
- A Unity Catalog catalog + schema you can create tables in (`USE_CATALOG`, `USE_SCHEMA`,
  plus explicit `MODIFY`+`SELECT` grants on the `mlflow_experiment_trace_*` tables —
  `ALL_PRIVILEGES` is explicitly NOT sufficient, see GOTCHAS)
- `mlflow[databricks]>=3.9.0` (3.1.0 is enough for Phases 2-5; trace ingestion needs 3.9.0+)
- Someone to act as the domain-expert labeler in Phase 7 (can be the user)

Phases 0-5 need none of the above — they run against a local/dev MLflow tracking URI.

## Format policy — notebook-agnostic by default

The deliverable format per phase is **not mandated to be `.ipynb`**. Default to whatever
format best teaches that phase's concept — a notebook, a plain markdown walkthrough, or a
`.py` script — and only reach for a `.py` file when there's an actual technical
requirement to do so, not as a default engineering habit. Concretely, that requirement
shows up in a few places this track will actually hit:

- **The Phase 1 agent itself** should live in an importable `.py` module (e.g.
  `agent.py`), not be defined inline in a notebook cell. This isn't a style choice — the
  GOTCHAS "Using Model Serving Endpoints for Development" pattern specifically calls for
  `from plan_execute_agent import AGENT` so `predict_fn` can import and call the agent
  directly across every later phase's evaluation notebook. An inline notebook-only
  definition can't be re-imported that way.
- **Custom scorers reused across phases 3-9** (e.g. a tool-trajectory judge, a
  guidelines set) belong in a shared module (e.g. `scorers.py`), since GOTCHAS also
  requires production-monitoring scorers to use inline imports for serialization —
  easier to get right once in a module than repeated inline in nine notebooks.
- Anything that's genuinely one-phase, one-shot, and benefits from prose-plus-code
  narration (strategy worksheets, eval-result walkthroughs, the capstone cross-reference)
  stays a notebook — that's most of this track.

So expect a small `agent.py` / `scorers.py` (or similar) alongside the phase
notebooks once building starts, not a rule that everything must be a notebook.

## Phase table

| # | Phase | Notebook | Deliverable | Maps to OpenAI eval guide | Status |
|---|---|---|---|---|---|
| 0 | Eval Strategy Worksheet | `00_eval_strategy_worksheet.ipynb` | Worked answers to Journey-0 strategy questions (what to evaluate, success criteria, user scenarios) for the agent built in Phase 1 | Anti-pattern #1 in the guide is skipping this — eval-driven development as a mindset, not a tool | ☐ Not started |
| 1 | Minimal Agent + Tracing | `01_minimal_agent_and_tracing.ipynb` | Tiny LangGraph customer-support agent (1 retriever tool + 1 deterministic lookup tool), `mlflow.langchain.autolog()` wired up on Databricks, traces verified to carry CHAT_MODEL/RETRIEVER/TOOL spans | Foundation — nothing is evaluable without traces | ☐ Not started |
| 2 | Offline Eval Fundamentals | `02_offline_eval_fundamentals.ipynb` | `mlflow.genai.evaluate()` runs with built-in scorers: `Guidelines`, `Correctness`, `Safety`, `RelevanceToQuery`, `RetrievalGroundedness` | Metric-based evals + LLM-as-judge basics | ☐ Not started |
| 3 | Custom Scorers & Judges | `03_custom_scorers_and_judges.ipynb` | Function-based + class-based custom scorers; low-level judges (`meets_guidelines`, `is_correct`, `make_judge`) incl. a trace-based tool-call/trajectory judge | Architecture-specific eval: tool-selection accuracy, single-agent trajectory | ☐ Not started |
| 4 | Eval Datasets from Production Traces | `04_eval_datasets_from_traces.ipynb` | UC-table-backed `mlflow.genai.datasets`, mining real traces into eval records, tagging traces in the UI for inclusion | "Collect diverse datasets reflecting real-world/production traffic" | ☐ Not started |
| 5 | Prompt Versioning & Regression Detection | `05_prompt_versioning_and_regression.ipynb` | MLflow Prompt Registry (`register_prompt`, `load_prompt`, `set_prompt_alias`) used as the actual mechanism for regression detection — register a baseline prompt as `@production`, register a deliberately-worsened v2, evaluate both against the same dataset, and only move the `@production` alias if the new version doesn't regress | Continuous eval / catching regressions before ship — every prompt change is a versioned, evaluated artifact, not an untracked edit | ☐ Not started |
| 6 | Online Evaluation — Production Monitoring | `06_online_eval_production_monitoring.ipynb` | UC trace ingestion setup, `register()`+`start()` scorers with sampling rates running against live traffic, querying trace tables via SQL | The literal "online eval" ask — Databricks' actual differentiator | ☐ Not started |
| 7 | Human-in-the-Loop Judge Alignment (MemAlign) | `07_judge_alignment_memalign.ipynb` | SME labeling session in the Databricks UI, aligning a custom judge to human feedback, demonstrating why an aligned score legitimately drops | Closes the "human evaluation / calibrate with human feedback" gap | ☐ Not started (optional/bonus) |
| 8 | Automated Improvement Loop (GEPA) | `08_automated_improvement_gepa.ipynb` | `optimize_prompts()` using the aligned judge as the reward signal, then registering and conditionally promoting the winning candidate through the *same* Prompt Registry mechanics taught in Phase 5 — the eval → improvement flywheel end to end | Closes the "eval insight drives improvement" gap | ☐ Not started (optional/bonus) |
| 9 | Capstone: Edge-Case Eval Design + OpenAI Cross-Reference | `09_capstone_edge_cases_and_crossref.ipynb` | Adversarial eval set (multilingual, ambiguous, circular-handoff-style, jailbreak probes) + explicit callouts back to the OpenAI eval guide's exact sections | Closes the "edge-case eval design" gap; ties the whole track back to the source doc | ☐ Not started |

Plus a top-level `README.md` (learning path, prerequisites, how to run) once Phase 0 lands.

## Notebook conventions

Follows this repo's standard (`CLAUDE.md` → Notebook Conventions): `# Title` first
markdown cell, `##`/`###` section hierarchy, `# ============ SECTION NAME ============`
banner comments in code cells, imports grouped stdlib → third-party → local, final cell
is a summary markdown with key takeaways. Outputs ship cleared (nbstripout via
pre-commit) — same "runs fresh" convention as the rest of the repo.

## Build order note

Phases 0-5 will be built and left runnable against a local/dev MLflow tracking URI first.
Phases 6-8 need real Databricks workspace details (SQL warehouse ID, UC catalog/schema)
plugged in before they can actually execute — they'll be written complete and correct
against the API, but flagged inline as needing those values filled in, matching how other
Databricks-backed notebooks in this repo (e.g. `03_Customer_Support_Router_RAG_Databricks_Alt.ipynb`)
already handle this.
