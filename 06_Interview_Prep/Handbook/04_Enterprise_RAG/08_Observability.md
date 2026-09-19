# Observability

> **Level** 🟡 Building Production Systems · **Module** 04 · **Doc** 8 of 10 · **Time** ~20 min
> **Prerequisites:** [The Query Graph](05_The_Query_Graph.md); Module 03 doc 4
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/01-theory.md` §10; `docs/05-src-modules-reference.md` (`observability/trace.py`, `llm/client.py` → `Usage`)
> **Lab:** `project/notebooks/02-hands-on-parts/part11-observability-and-takeaways.ipynb`; any file in `project/runs/` after a query

## Why this matters

Module 03 gave you per-tool-call telemetry. This is the level above it: one complete, replayable record of every request. In an access-controlled system that record is not only a debugging aid — it is the artefact that answers *"prove this user never saw that document"*, and it is the input the evaluation harness scores. If a run is not traced, it did not happen.

## Three audiences, one artefact

- **The engineer** debugging a bad answer — which strategy ran, what was retrieved, what the reranker scored, what the grader said.
- **The auditor** asking "did this user ever see that document?" — the principal, the compiled filter, every allowed and denied chunk, every citation.
- **The finance team** asking "which tenant is burning the budget?" — tokens and cost per stage, per run, per tenant.

Designing one record that serves all three is cheaper than three systems, and it means the auditor and the engineer are looking at the same facts.

## What a `RunTrace` holds

| Section | Fields |
|---|---|
| Identity | `run_id`, principal, tenant, timestamp, `PROMPT_VERSION` |
| Authorisation | the compiled Layer 1 filter and its human-readable explanation |
| Planning | sub-questions, generated multi-queries, HyDE passage |
| Retrieval | which strategy; candidate chunk ids with provenance (`retrieved_by`) |
| Enforcement | allowed, denied (with the rule), redacted, audit events, **security events** (Layer 1/2 disagreements) |
| Generation | grade verdict and coverage note, cached-or-not, the draft |
| Verification | dropped citations, surviving citations, groundedness score |
| Steps | every named step with start, end, duration in ms |
| Cost | prompt/completion/embedding tokens, call count, USD — total and **by purpose** |
| Outcome | answer or refusal, `degraded` flag |

`RunTrace.start(name)` / `end(name)` bracket each step; `finish(usage)` copies token and cost totals from the `Usage` accumulator; `write()` saves one JSON file per run to `runs/`; `timeline()` renders an ASCII bar chart of step durations — the first thing to look at when a run is slow.

## Cost attribution by purpose

The LLM client's `Usage` object tallies tokens not only in total but **by purpose** — `rewrite`, `hyde`, `rerank`, `grade`, `synthesis`, `groundedness`, `embed`. That breakdown is what turns "this run cost 2 cents" into "60% of it was the reranker", which is the number you need to decide whether to swap the LLM reranker for a cross-encoder. It also feeds the per-run cost ceiling in `generate`.

## Prompt version on every run

`PROMPT_VERSION` is stamped onto each trace. When answer quality shifts, the first question is "did the prompt change?", and the trace answers it without a deploy log. Module 08 develops this into full prompt versioning with rollout and rollback.

## What the trace makes possible

- **Replay.** The evaluation harness replays golden questions and scores the traces; a trace has everything needed to re-derive every metric.
- **Security signal.** `filter_disagreements` on a trace means Layer 2 denied something Layer 1 should have caught — a stale index or a broken filter. That field is an alert, not a log line.
- **Degradation visibility.** The `degraded` flag and the step that set it tell you the answer was produced under a provider outage — which is different from a bad answer.

## From here to production

The demo writes JSON files. Production emits the same structure as spans in a standard format, one trace per request nested under one per conversation, with `tenant`, `principal`, `prompt_version` and `run_id` as attributes on every span. Module 06 explains why the *standard* matters more than the vendor: a customer who already runs an observability stack can ingest your traces without a bespoke integration, and per-tenant dashboards become a customer-facing surface rather than an internal log.

## In the code

| Concept | Where |
|---|---|
| Trace record | `observability/trace.py` → `RunTrace` — `start`, `end`, `finish`, `write`, `timeline` |
| Token/cost accounting by purpose | `llm/client.py` → `Usage.add`, `Usage.merge` |
| Prompt version | `graph/prompts.py` → `PROMPT_VERSION` |
| Security events | `authz/enforcement.py` → `EnforcementReport`, `filter_disagreements` |
| Where traces land | `project/runs/run_<id>.json` |

## Interview lens

> *"Every run is a replayable record: who asked, what the policy decided, what was retrieved and denied and why, what the model saw, what it produced, how long each stage took and what it cost — by purpose. Three audiences, one artefact: the engineer, the auditor, and finance."*

## Checkpoint

- Name the three audiences and one question each would ask of a trace.
- Why is cost tallied by purpose rather than only in total?
- What does a non-empty `filter_disagreements` field mean, and what should happen?
- How does the evaluation harness depend on the trace?

**Next →** [Module Reference](09_Module_Reference.md)
