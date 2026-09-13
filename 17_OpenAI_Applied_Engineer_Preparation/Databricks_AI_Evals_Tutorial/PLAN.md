# Databricks AI Evals Tutorial — Build Plan

**Status: COMPLETE — all 11 phases (0-10) built.** Phase 9 was added after Phase 8 and the capstone renumbered to 10; see "Scope revision" below. Phases 0-5 and 9-10 run locally against SQLite; Phases 6-8 require a Databricks workspace. Phases 6-8 require a Databricks workspace; 0-5 run locally against SQLite. This file is the persistent reference for the phased build;
tick items off as each phase lands. See [Known Discrepancies](../../NOTEBOOK_INDEX.md) for
how this repo tracks build history for other tracks — this file plays the same role for
this one.

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
| 0 | Eval Strategy Worksheet | `00_eval_strategy_worksheet.ipynb` | Worked answers to Journey-0 strategy questions (what to evaluate, success criteria, user scenarios) for the agent built in Phase 1 | Anti-pattern #1 in the guide is skipping this — eval-driven development as a mindset, not a tool | ✅ Built |
| 1 | Minimal Agent + Tracing | `01_minimal_agent_and_tracing.ipynb` + `agent.py` | Tiny LangGraph customer-support agent (fixed retrieval step + 1 LLM-chosen lookup tool), `mlflow.langchain.autolog()` combined with explicit `@mlflow.trace(span_type=...)`, traces verified to carry AGENT/RETRIEVER/CHAT_MODEL/TOOL spans + a scorer-readiness preflight | Foundation — nothing is evaluable without traces | ✅ Built |
| 2 | Offline Eval Fundamentals | `02_offline_eval_fundamentals.ipynb` + `eval_dataset.py` | 12-record eval dataset (+2 edge cases) with `expected_facts` vs per-row `guidelines`; all 6 built-in scorers wired up; smoke test; quality gates turned into a ship/no-ship decision; per-row failure analysis and category slicing | Metric-based evals + LLM-as-judge basics; "collect diverse datasets"; the "biased dataset" anti-pattern | ✅ Built |
| 3 | Custom Scorers & Judges | `03_custom_scorers_and_judges.ipynb` + `scorers.py` | Cost hierarchy of scorers; deterministic trace-based `tool_call_correctness` (penalising unexpected calls, not just missing ones) fills the gate Phase 2 left unmeasured; deterministic-vs-judge on the same rule; numeric scorer w/ aggregations; class-based configurable scorer; categorical + `{{ trace }}` `make_judge`; low-level judges API for iterating on wording; production-serialization constraints | Architecture-specific eval: tool-selection accuracy, single-agent trajectory | ✅ Built |
| 4 | Eval Datasets from Production Traces | `04_eval_datasets_from_traces.ipynb` + `traffic.py` | Skewed traffic simulator; random vs novelty-targeted sampling (threshold, not top-k); trace tagging; managed dataset via OSS `create_dataset(name=)` with the UC form noted; `log_expectation` with `AssessmentSource` provenance; `merge_records` dedup-by-input-hash semantics; discovery of an entirely untested behaviour (abstention on out-of-scope questions) and the scorer it motivated | "Collect diverse datasets reflecting real-world/production traffic"; the "biased dataset" anti-pattern | ✅ Built |
| 5 | Prompt Versioning & Regression Detection | `05_prompt_versioning_and_regression.ipynb` + `promotion.py` | Prompt Registry as the regression-detection mechanism: v1 registered and aliased `@production`, a plausible-but-worse v2 registered and rejected by the gate, a targeted v3 fix promoted, then a rollback drill. Two-condition promotion gate (absolute thresholds + no regression) with per-metric-type tolerance: zero for deterministic scorers, 0.02 for judged ones | Continuous eval / catching regressions before ship; direct answer to interview Case #8 ("offline benchmark improved but quality declined") | ✅ Built |
| 6 | Online Evaluation — Production Monitoring | `06_online_eval_production_monitoring.ipynb` + `monitoring.py` | Scorer-eligibility rule (anything reading `expectations` is offline-only — incl. `tool_call_correctness`); UC schema linking into a *separate* production experiment; `register()`+`start()` with per-scorer sampling; sampling economics *and* statistical resolution (Wilson intervals — a 5% sample resolves ±4.5pts, so a 2-pt drop is noise); SQL over the Delta trace tables; scorer lifecycle management; the online-discovers/offline-prevents loop | The literal "online eval" ask — Databricks' actual differentiator | ✅ Built |
| 7 | Human-in-the-Loop Judge Alignment (MemAlign) | `07_judge_alignment_memalign.ipynb` + `alignment.py` | Agreement measurement (exact / Cohen's kappa / quadratic weighted kappa) as the *correct* metric instead of mean score; Likert `make_judge`; labeling session + label schema sharing one variable with the judge name; MemAlign with explicit `embedding_model`; before/after report showing mean score DOWN while every agreement measure rises | Closes the "human evaluation / calibrate with human feedback" gap | ✅ Built |
| 8 | Automated Improvement Loop (GEPA) | `08_automated_improvement_gepa.ipynb` | Optimisation dataset (`expectations` required on every row, describing behaviour not gold text); registry-reloading `predict_fn`; GEPA with aligned judge as reward + `aggregation` normaliser; candidate registered but gated through Phase 5's full scorer set — a superset of the optimisation objective, which is what catches the overfitting | Closes the "eval insight drives improvement" gap | ✅ Built |
| 9 | Multi-Turn and Tool-Selection Evaluation | `09_multiturn_and_tool_selection.ipynb` + `conversation.py` | `p ** n` arithmetic showing turn-level metrics overstate conversation quality; second read-only tool making tool *selection* measurable; an ungated write action gated only by the prompt, verified by an approval-gate scorer; context-retention scoring; which scorers belong at which level | Multi-turn context recall + approval gating — interview Cases #2 and #6 | ✅ Built |
| 10 | Capstone: Edge-Case Eval Design + OpenAI Cross-Reference | `10_capstone_edge_cases_and_crossref.ipynb` + `edge_cases.py` | Adversarial suite designed as **5 attack classes x 3 variants** rather than a flat string list; 7 non-adversarial edge cases (ambiguous tool responses, multiple intents, format variability, minimal context, non-English, prompt conflict); a deterministic scorer for the polite-tool-failure hallucination mode; a coverage map against the guide's edge-case list stating N/A items *with reasons*; full cross-reference to the OpenAI guide and the interview cases; an explicit list of what the track does NOT cover | Closes the "edge-case eval design" gap; ties the whole track back to both source docs | ✅ Built |

Plus a top-level `README.md` (learning path, prerequisites, how to run) — ✅ built alongside Phase 0.

## Notebook conventions

Follows this repo's standard (`CLAUDE.md` → Notebook Conventions): `# Title` first
markdown cell, `##`/`###` section hierarchy, `# ============ SECTION NAME ============`
banner comments in code cells, imports grouped stdlib → third-party → local, final cell
is a summary markdown with key takeaways. Outputs ship cleared (nbstripout via
pre-commit) — same "runs fresh" convention as the rest of the repo.

## Known issue found during the Phase 1 build (not fixed — out of scope)

`helpers.get_llm()` is **broken on macOS**. `PLATFORM_DEFAULTS["darwin"]` routes to
`get_databricks_llm()`, which returns `client.responses.create(...)` — an already-executed
OpenAI *Responses* API call object, not a chat-model instance. It also ignores its own
`model_name` argument and hardcodes both the workspace URL and `system.ai.gemma-3-12b`.
`CLAUDE.md` documents the intended behaviour (`ChatDatabricks` with
`databricks-gpt-oss-120b`), so the code and the docs disagree.

This track therefore does **not** use the `helpers` factory — `agent.py` names its models
explicitly in a `MODELS` dict, which is the right call for evaluation anyway (the model
under test has to be pinned and visible, or Phase 5's before/after comparison is
meaningless). Flagged here because it affects other LangGraph notebooks in this repo that
*do* call `get_llm()` on macOS.

## Findings from the Phase 10 build

- **A flat list of adversarial examples is a weak test.** It cannot tell you which class of
  attack is unprotected. The suite is built as classes x variants, and a simulated agent in
  `test_edge_cases.py` scores 80% overall while one class sits at 0% — the aggregate hides
  it, the class view does not.
- **Edge-case rows must assert boundaries, not gold answers.** For an ambiguous input,
  several behaviours are acceptable; asserting one fails a good agent. No adversarial or
  edge-case row uses `expected_facts`, enforced by test.
- **Tools that fail politely are a hallucination trap.** Both read tools return
  `{"found": False}` rather than raising, which is easy for a model to skate past. Added
  `no_fabrication_after_failed_lookup`, a deterministic scorer reading the TOOL span output.
  Nothing in Phases 1-9 tested this path.
- **State N/A items with reasons.** "Single agent, no handoffs" shows the item was
  considered; silence is indistinguishable from having missed it.

## Phase 0 resync (done alongside Phase 9)

Phase 0 is the track's single source of truth for scope and thresholds, so it was audited
after Phase 9 rather than left to drift. Six things were stale; one was substantive:

- **Three Phase 9 scorers had no gate entry** — `tool_selection_correctness`,
  `approval_before_write`, `context_retained`. An agent opening a ticket nobody asked for
  would have been measured and shipped. Added `tool_selection`, `approval_gate` (threshold
  1.00 — a write nobody requested is a trust breach, not a quality miss) and
  `context_retention`. **This is the second time a phase added scorers and forgot the
  gate**, which is now called out explicitly in Phase 0's own output.
- Phase 0's `QUALITY_GATES` was already two gates behind `eval_dataset.py` from Phase 5.
  Both copies now agree on all 11 gates, verified by test.
- The new gates resolve only on conversation runs and report as "not measured" on
  single-turn ones — the correct behaviour, and a new lesson: **gates have a scope, exactly
  as scorers do.**
- `AGENT_SPEC` tools/purpose/formats, the Step 1 table (which still claimed "no
  write-capable tools"), and the note asserting `multi_turn` was empty were all corrected;
  the last two had become self-contradictory with cells directly beside them.

## Scope revision (Phase 9, made after Phase 8)

Two of Phase 0's four non-goals were revised, and the revision is recorded in Phase 0's own
notebook rather than quietly edited in. The distinction that drove it:

> A non-goal that limits the **agent** is discipline. A non-goal that silently limits what
> you can **measure** is a blind spot.

- *"no multi-turn memory"* meant "agent took a write action without asking" could not be
  expressed at all — consent happens between turns — and neither could context retention.
- *"no write actions"* plus a single tool meant tool-*selection* accuracy was unmeasurable:
  with one tool, "called a tool" and "called the right tool" are the same question.

Added additively (Phases 1-8 run unchanged): `check_network_status` (read-only, second
tool), `open_ticket` (write, gated only by the prompt), `history=` on `answer`, and
`converse()`. The remaining non-goals — authentication, autonomous escalation routing —
still stand, because they constrain the agent without hiding an eval concept.

Two bugs my own tests caught during this build, both semantic rather than syntactic:

- **Approval gate used `t <= consent_turn`.** Consent arrives in the *user's message* at the
  start of a turn and the write happens in the agent's response within that same turn, so
  `<=` failed the agent for behaving correctly. Fixed to strictly-before.
- **`customer_id` was applied only to turn 1.** That dropped customer identity from turn 2
  onward, so every conversation would have failed context-retention for a plumbing reason
  rather than a model one — measuring the harness instead of the agent. Identity is now
  session-scoped.

## Findings from the Phase 7-8 build

- **Agreement, not average score, is the measure of a judge.** Mean score measures
  generosity; a judge rating everything 5/5 scores wonderfully and is useless.
- **Plain Cohen's kappa cannot distinguish "systematically one point generous" from
  "uncorrelated".** Verified in `test_alignment.py`: two judges with *identical* exact
  agreement (0.00) and *identical* plain kappa (-0.250) score +0.71 and -0.82 under
  quadratic weighted kappa. Use the weighted form on ordinal scales.
- **The label schema name must equal the judge name**, or `align()` finds no score pairs,
  learns nothing, and returns silently. `alignment.format_alignment_report` names this as the
  likely cause whenever agreement fails to improve.
- **GEPA's reward signal is the judge, so Phase 7 gates Phase 8.** Optimising against an
  unaligned judge tunes the agent toward a standard nobody holds — efficiently.
- **A higher optimisation score is not permission to ship.** It is by definition the metric
  the optimiser was pointed at. Phase 8 therefore runs the candidate through Phase 5's full
  gate, whose scorer set is a strict superset of the optimisation objective.

## Findings from the Phase 6 build

- **Linking a UC schema hides that experiment's pre-existing MLflow-stored traces.** Phase 6
  therefore links a *separate* `/Shared/telcoassist-production` experiment rather than
  `telcoassist-evals`, which holds everything from Phases 1-5.
- **A scorer that reads `expectations` cannot run online at all.** Production traffic has no
  ground truth, so `tool_call_correctness` — one of the most useful scorers in the track —
  would return `skip` on every live trace while appearing healthy. Eligibility is mechanical:
  reference-free scorers transfer, expectation-reading ones don't.
- **Sample rate must be chosen from the regression size you need to detect.** At 2,000
  traces/day a 5% sample resolves only ±4.5 percentage points, so a 2-point drop is
  indistinguishable from noise; detecting it needs ~30% sampling. Small regressions are far
  cheaper to catch offline (Phase 5), where coverage is 100% and the comparison is paired.

## Findings from the Phase 4 build

- **Evaluation Datasets also require a SQL-backed store** — same constraint as the Prompt
  Registry, independently confirmed. Two features now depend on the SQLite switch.
- **`merge_records` needs `search_traces(..., return_type="list")`.** The default DataFrame
  return does not work, and the argument is easy to miss.
- **The mined traffic exposed a behaviour the curated set never tested at all**: what the
  agent does when the knowledge base cannot answer the question (family plans, service
  pauses, 5G tiers, student discounts are all absent from `agent.KNOWLEDGE_BASE`). That
  produced a new `abstains_when_unsupported` scorer, which is the concrete argument for
  this phase existing.

## Corrections made during the Phase 5 build

- **The Prompt Registry requires a database-backed tracking store.** `file:./mlruns` does
  not support registry features. Phases 1-3 were retrofitted from `file:./mlruns` to
  `sqlite:///mlflow.db` so traces and prompts share one store and the track doesn't switch
  stores midway.
- **Two blocking gates were missing.** Phases 2-3 added `protects_other_accounts`,
  `no_account_leakage`, and `escalates_restricted_actions` scorers, none of which were
  listed in `QUALITY_GATES` — so an account-leakage regression would have been reported as
  "noted, not blocking" and shipped. Added `account_protection` and `escalation` gates.
  Adding a scorer does not add a gate.
- **`resolve_gate_metrics` ignored candidate priority.** It iterated over the metrics dict
  rather than the candidate list, so which metric backed a gate depended on dict ordering
  rather than the documented preference (deterministic scorer over judged one). Fixed to
  iterate candidates in order.

## Build order note

Phases 0-5 will be built and left runnable against a local/dev MLflow tracking URI first.
Phases 6-8 need real Databricks workspace details (SQL warehouse ID, UC catalog/schema)
plugged in before they can actually execute — they'll be written complete and correct
against the API, but flagged inline as needing those values filled in, matching how other
Databricks-backed notebooks in this repo (e.g. `03_Customer_Support_Router_RAG_Databricks_Alt.ipynb`)
already handle this.
