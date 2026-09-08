# AgentOps on Databricks

> **Level** 🟠 Scale, Security, Operations · **Module** 08 · **Doc** 2 of 6 · **Time** ~25 min
> **Prerequisites:** [Prompt Versioning, Rollout and Rollback](01_Prompt_Versioning_Rollout_Rollback.md); Module 06 doc 2
> **Source material:** `3. AI_Engineer_Interview_Preparation/Cross Cutting Preparation/04-agentops-on-databricks.md`

## Why this matters

The previous document is platform-agnostic, which is how you should design cold. But "have you actually done this?" is a different question, and the answer to it is a real product name attached to each step. This document maps every AgentOps concept — versioning, gating, canary, rollback, tracing, drift, audit — onto the Databricks primitive that implements it.

**The order matters.** Answer the design question in generic terms first. Then, when asked whether you have done it, switch to this vocabulary. Leading with vendor names reads as name-dropping; leading with the architecture and *then* grounding it in a real deployment reads as someone who has shipped it.

## 1 · Versioning → Unity Catalog Model Registry, addressed by alias

A registered model in the **Unity Catalog Model Registry** is exactly the immutable, versioned artefact the previous document called for. Every prompt or agent version becomes a new registered version under the same model name, addressed not by a raw number but by an **alias** — `@champion`, `@challenger`, `@prod`, `@staging`. Application code references the alias, never a hardcoded version. Promoting is re-pointing the alias; the calling code is untouched.

Databricks also ships **`optimize_prompts()`** — an automated prompt-optimisation loop (GEPA) that takes a registered prompt, a dataset and a scorer and produces a new candidate version. The closest real-world equivalent to "automatically generate the next version to evaluate".

> *"Every prompt and agent version was a registered model version in Unity Catalog, addressed by alias — promoting meant re-pointing the alias, never redeploying calling code."*

## 2 · The gate → `mlflow.genai.evaluate()` with scorers and judges

`mlflow.genai.evaluate()` runs a candidate against a dataset with a set of **scorers** — built-in or custom judges — and produces the release-gate report. Two refinements worth naming:

- **MemAlign judge alignment** — a built-in workflow for calibrating a custom judge against real human-labelled examples from subject-matter experts, so the judge scoring your gate has been checked against actual human judgement rather than being an off-the-shelf prompt guessing at "good". This is the concrete answer to "how do you calibrate an LLM-as-judge" — the step Module 04 flagged as the one most teams skip, and did by hand with `calibrate_judge.py`.
- **Named runs for baseline comparison** — a candidate's evaluation run is compared against a named baseline run, so "did this regress versus production" is tracked, not recomputed by eye.

> *"The quality gate ran `mlflow.genai.evaluate()` against a fixed dataset before any promotion, and we calibrated the judge against real SME-labelled examples rather than trusting an off-the-shelf grading prompt."*

## 3 · Canary and shadow → Model Serving traffic routing

A **Model Serving endpoint** can have multiple served entities (model versions) under one endpoint, with a **traffic config that routes a percentage of requests to each**. That is the literal canary: 95% to the current version, 5% to the candidate, watched live before shifting further.

**Shadow** — watch decisions on live traffic without acting on them — is achieved by logging the candidate's predictions without routing real traffic to it, or by routing a small percentage while keeping any *destructive* action gated behind a separate application-level approval. The guardrail-vs-model-output separation from Module 05, again.

> *"Canary rollout was a Model Serving traffic split — a small percentage of real requests to the candidate, watched live, before shifting the rest. Same pattern as an A/B test, expressed as endpoint config instead of application code."*

## 4 · Rollback → alias repoint plus endpoint config, together

Rolling back means re-pointing the Unity Catalog alias to the previous registered version **and** updating the endpoint's served-entity config to match — both, together. Repointing the alias alone does not move the endpoint; updating the endpoint alone leaves the alias pointing at the old version. A real, easy-to-hit bug if only half is done. Because the previous version is still a registered version, not a deleted deployment, it is available instantly: no redeploy, no rebuild, a config update.

> *"Rollback was a config change — repoint the alias, update the endpoint's traffic config to match, done. The previous version was never torn down."*

## 5 · Tracing → MLflow Tracing into Unity Catalog tables

**MLflow Tracing** captures the per-request trace — prompt version, retrieved context, tool calls, tokens, latency, cost — and can write directly into a **Unity Catalog table**. Traces become queryable with ordinary SQL, joinable with other governed data, and covered by the same access-control model as everything else in the lakehouse. This closes the exact gap Module 06 doc 2 named: a bespoke trace format that is not queryable or governed like everything else.

Production monitoring is the same pipeline: the same scorers used for the pre-promotion gate, run continuously against live traces. "Did this regress after promotion" is not a separate system from "did this pass before promotion" — it is the same measurement on a schedule. That is Module 06's nightly run, built in.

> *"Traces landed in Unity Catalog tables, so they were queryable with SQL and governed like every other table — and production monitoring was the same evaluation scorers running continuously against live traces instead of a one-time gate."*

## 6 · Drift, cost attribution and audit → system tables

Three different system tables, three different questions:

| Table / feature | Answers |
|---|---|
| **`system.access.audit`** | Every permission grant, revoke and access event, queryable with SQL — the audit trail this handbook argues every AI system needs, already built in |
| **`system.billing.usage`** | Usage and cost by workspace and SKU — the raw material for per-tenant and per-workload cost attribution; Module 06's "a report, not a missing signal" |
| **Unity Catalog data profiling** | Profile metrics over a table's history — drift alerting applied to underlying data rather than model behaviour |

> *"Audit wasn't a table I built — `system.access.audit` already has every access event. Cost attribution came from `system.billing.usage` rolled up by workspace and SKU. Drift detection came from Unity Catalog's data profiling rather than something to build."*

## The mapping

| Generic AgentOps concept | Databricks mechanism |
|---|---|
| Versioned prompt/config artefact | Unity Catalog Model Registry, addressed by alias |
| Automated prompt improvement | `optimize_prompts()` (GEPA) |
| Pre-promotion quality and safety gate | `mlflow.genai.evaluate()` with scorers/judges |
| Judge calibration against human labels | MemAlign via SME labelling |
| Baseline comparison for regressions | Named evaluation runs |
| Canary / percentage rollout | Model Serving traffic config across served entities |
| Shadow mode | Candidate logged without live traffic, or gated behind an approval step |
| Rollback | Alias repoint + endpoint config update, together |
| Tracing | MLflow Tracing → Unity Catalog tables |
| Production monitoring | The same scorers, continuously, against live traces |
| Audit trail | `system.access.audit` |
| Cost attribution | `system.billing.usage` |
| Data drift | Unity Catalog data profiling |

## Interview lens

> *"Everything in my design answer generalises across any platform — that's how I'd design it cold. On this specific engagement I built it on Databricks: prompt and agent versions were registered models in Unity Catalog addressed by alias, promotion gated on `mlflow.genai.evaluate()` with a judge calibrated against real SME labels, canary rollout was a Model Serving traffic split, rollback was an alias repoint, and traces landed in Unity Catalog tables — with audit, cost and drift signals from the platform's own system tables rather than something I had to build."*

## Checkpoint

- Why answer generically first and name the platform second?
- What is an alias, and why does application code reference it rather than a version?
- What does MemAlign do, and which step from Module 04 does it replace?
- Describe the rollback bug that happens when only half the procedure is done.
- Map five generic concepts to their Databricks mechanism without looking.

**Next →** [Enterprise RAG on Databricks](03_Enterprise_RAG_On_Databricks.md)
