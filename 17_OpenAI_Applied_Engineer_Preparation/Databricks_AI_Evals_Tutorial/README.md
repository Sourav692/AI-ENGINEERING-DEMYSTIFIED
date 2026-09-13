# Databricks AI Evals Tutorial

A hands-on track for understanding **AI evaluation — offline and online** — using
Databricks' MLflow 3 GenAI evaluation stack. Built to close specific gaps identified in
`../OpenAI_Applied_AI_Engineer_Coverage_Gap_Analysis.md` against OpenAI's own
[Evaluation Best Practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices?api-mode=responses)
guide.

**Status: complete — all 11 phases built.**

**This track is about evaluation, not agent-building.** A minimal customer-support agent
(`TelcoAssist`) is built once in Phase 1 and never meaningfully changed again — every
phase after that is entirely about how to evaluate it, offline and in production. See
`PLAN.md` for the full phase-by-phase breakdown, status tracker, and design rationale.

## Learning path

Work through the notebooks in order — each one assumes the state left by the previous
phase (`AGENT_SPEC`, `EVAL_DIMENSIONS`, `QUALITY_GATES`, etc. defined in Phase 0 are reused
by name throughout, not redefined):

0. `00_eval_strategy_worksheet.ipynb` — decide what "good" means *before* writing agent code
1. `01_minimal_agent_and_tracing.ipynb` — build TelcoAssist, instrument with MLflow tracing
2. `02_offline_eval_fundamentals.ipynb` — `mlflow.genai.evaluate()` with built-in scorers, quality gates as a ship decision
3. `03_custom_scorers_and_judges.ipynb` — custom scorers, trace-based tool-call judge, low-level judges API
4. `04_eval_datasets_from_traces.ipynb` — mine production traces into a managed eval dataset (sampling strategy, provenance)
5. `05_prompt_versioning_and_regression.ipynb` — MLflow Prompt Registry as the regression-detection mechanism, two-condition promotion gate
6. `06_online_eval_production_monitoring.ipynb` — UC trace ingestion, sampled continuous scoring, sampling economics and statistics
7. `07_judge_alignment_memalign.ipynb` *(bonus)* — align a judge to human feedback; measure agreement, not score
8. `08_automated_improvement_gepa.ipynb` *(bonus)* — GEPA prompt optimisation, gated by Phase 5's promotion check
9. `09_multiturn_and_tool_selection.ipynb` — conversation-level metrics, tool selection, approval gating
10. `10_capstone_edge_cases_and_crossref.ipynb` — adversarial design by attack surface, edge-case coverage map, full cross-reference

### Theory & reference (`theory/`)

Companion material that does what a sequential notebook can't — random access. It does
**not** repeat the notebooks' explanations (there are ~15,900 words of those already):

- `theory/CONCEPTS.md` — every concept defined in a line or two, grouped **by theme**, with
  a pointer to the phase that demonstrates it
- `theory/GOTCHAS.md` — 32 traps as symptom → cause → fix, led by the silent failures that
  look like success
- `theory/QUICK_REFERENCE.md` — the numbers, thresholds and decision rules, compressible to
  one sitting

### Shared modules

- `agent.py` — TelcoAssist, the agent under test (built in Phase 1, unchanged after)
- `eval_dataset.py` — the evaluation dataset, edge cases, and quality gates (built in Phase 2, reused by 3-5)
- `scorers.py` — custom scorers and judges (built in Phase 3; some get registered for production monitoring in Phase 6)
- `promotion.py` — promotion gating: thresholds + no-regression rules with per-metric-type tolerance (built in Phase 5, reused by Phase 8)
- `traffic.py` — skewed simulated production traffic (built in Phase 4, reused by Phase 6)
- `monitoring.py` — online scorer eligibility + sampling cost/statistics (built in Phase 6)
- `alignment.py` — judge/human agreement measures incl. quadratic weighted kappa (built in Phase 7)
- `conversation.py` — conversation-level metrics, context retention, approval gating (built in Phase 9)
- `edge_cases.py` — adversarial taxonomy, edge-case suite, OpenAI edge-case coverage map (built in Phase 10)

## Prerequisites

- **Phases 0-5**: `mlflow[databricks]>=3.1.0`, `langgraph`, this repo's root `.venv`, and an
  LLM endpoint (Databricks-served by default, or set `TELCOASSIST_PROVIDER=openai`).
  Tracking runs locally against `sqlite:///mlflow.db` — **not** a `file://` store, since
  Phase 5's Prompt Registry requires a database-backed backend.
- **Phases 6-8**: a Databricks workspace + CLI profile, a SQL warehouse ID, and a Unity
  Catalog catalog/schema you can create tables in (`mlflow[databricks]>=3.9.0`). See
  `PLAN.md`'s Prerequisites section for exact grants needed — `ALL_PRIVILEGES` is
  explicitly *not* sufficient for UC trace tables.
- **Phase 7** additionally needs a human willing to act as the domain-expert labeler
  (can be you).

## Relationship to the rest of `17_OpenAI_Applied_Engineer_Preparation/`

- `../OpenAI_Applied_AI_Engineer_Coverage_Gap_Analysis.{md,html}` — the gap analysis this
  track exists to close
- `../Sample_Questions/` — interview case studies; this track's agent (Case #2) and its
  entire premise (Case #11) are grounded in specific cases there, cross-referenced inline
  in Phase 0 and the capstone
