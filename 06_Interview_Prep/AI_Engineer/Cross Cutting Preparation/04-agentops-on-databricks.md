# AgentOps on Databricks — prompt versioning, rollout, and observability, with real tools named

**What this is:** the same AgentOps concepts covered generically in `enterprise_rag_platform/docs/10`
and `cross_cutting_prep/02-03` (prompt versioning, canary rollout, rollback, tracing, drift, audit),
mapped onto the actual Databricks primitives that implement each one. Use this doc specifically when
you want to say *"I've done this for real, on Databricks, in a customer engagement"* rather than
speaking purely from architecture theory.

**How to use this in the interview:** answer the system-design question in generic terms first (that's
what the other AgentOps docs are for) — then, when asked "have you actually done this," switch to this
doc's vocabulary and name the real product. That order matters: leading with vendor names first reads
as name-dropping; leading with the architecture and *then* grounding it in a real deployment reads as
someone who's actually shipped it.

---

## 1. Prompt / model versioning → MLflow Model Registry (on Unity Catalog)

The generic concept: treat every prompt as an immutable, hashed, versioned artifact, never a mutable
string in source.

**The real Databricks mechanism:** a registered model in the **Unity Catalog Model Registry** is
exactly that artifact. Every prompt/agent version becomes a new registered version under the same
model name, and it's addressed not by a raw version number but by an **alias** — `@champion`,
`@challenger`, `@prod`, `@staging` — so the application code always references *the alias*, never a
hardcoded version. Promoting a new version is re-pointing the alias, not touching the calling code at
all.

Databricks also ships **`optimize_prompts()`** — an automated prompt-optimization loop (GEPA) that
takes a registered prompt, a dataset, and a scorer, and produces a new candidate version — the closest
real-world equivalent to "automatically generate the next version to evaluate," rather than only
hand-editing prompts.

**What to say:** *"On the engagement, every prompt/agent version was a registered model version in
Unity Catalog, addressed by alias rather than a hardcoded version — promoting meant re-pointing the
alias, never redeploying calling code."*

## 2. The gate before promotion → `mlflow.genai.evaluate()` + scorers/judges

The generic concept: a new version can't be promoted unless it clears a safety gate (must hit zero)
and a quality gate (no regression vs. the current baseline), measured on a fixed test set.

**The real mechanism:** `mlflow.genai.evaluate()` runs a candidate version against a dataset with a
set of **scorers** (built-in or custom judges) and produces exactly the kind of report this whole
series treats as the release gate. Two Databricks-specific refinements worth naming:

- **MemAlign judge alignment** — a built-in workflow for calibrating a custom judge against real
  human-labeled examples collected from subject-matter experts, so the judge scoring your gate isn't
  just an off-the-shelf prompt guessing at "good" — it's been checked against actual human judgment.
  This is the concrete answer to "how do you calibrate an LLM-as-judge," which every project in this
  series flags as the step candidates skip.
- **Named runs for baseline comparison** — a candidate version's evaluation run is compared against a
  named baseline run, not an ad hoc rerun, so "did this regress vs. the current production version" is
  an actual tracked comparison, not something recomputed by eyeballing two numbers.

**What to say:** *"The quality gate ran `mlflow.genai.evaluate()` against a fixed dataset before any
promotion, and we calibrated the judge itself against real SME-labeled examples rather than trusting
an off-the-shelf grading prompt — that calibration step is exactly the part most teams skip."*

## 3. Canary / shadow rollout → Model Serving traffic routing

The generic concept: shadow first (new version runs alongside live, zero user risk), then a small-scale
release (a slice of traffic sees the new version), then promote or roll back.

**The real mechanism:** a Databricks **Model Serving endpoint** can have multiple served entities
(model versions) registered under one endpoint, with a **traffic config that routes a percentage of
requests to each** — this is the literal canary mechanism: 95% of traffic to the current version, 5%
to the candidate, watched live before shifting further. "Shadow" (watch decisions on live traffic
without ever acting on them) is achieved by logging predictions from the candidate without routing any
real traffic to it — or routing a small percentage while keeping any *destructive* action gated behind
a separate application-level approval step, the same guardrail-vs-model-output separation this whole
series argues for.

**What to say:** *"Canary rollout was a Model Serving traffic-split — a small percentage of real
requests routed to the candidate version, watched live, before shifting the rest. It's the same
pattern as an A/B test, just expressed as endpoint config instead of application code."*

## 4. Rollback → alias repoint, not a redeploy

The generic concept: rollback has to be instant and cheap — a version-pointer flip, with the previous
version kept warm and ready.

**The real mechanism:** rolling back means re-pointing the Unity Catalog alias back to the previous
registered version and updating the endpoint's served-entity config to match — both steps, done
together (repointing the alias alone doesn't move the endpoint; updating the endpoint alone leaves the
alias pointing at the old version — a real, easy-to-hit bug if only one half is done). Because the
previous version is still a registered model version, not a deleted deployment, it's available
instantly — there's no redeploy, no rebuild, just a config update.

**What to say:** *"Rollback was a config change — repoint the alias, update the endpoint's traffic
config to match, done. The previous version was never torn down, so there was nothing to rebuild."*

## 5. Observability and tracing → MLflow Tracing into Unity Catalog

The generic concept: every run traced end to end — prompt version, retrieved context, tool calls,
tokens, latency, cost — ideally in a standard span format, feeding both debugging and production
monitoring.

**The real mechanism:** **MLflow Tracing** captures exactly that per-request trace, and it can be
configured to write directly into a **Unity Catalog table** as its trace destination — which means
traces are queryable with ordinary SQL, joinable with other governed data, and covered by the same
access-control model as everything else in the lakehouse, rather than living in a separate, bespoke
logging system. This closes the exact gap the generic observability doc names: a bespoke trace format
that isn't queryable or governed the same way as everything else.

Production monitoring is the same tracing pipeline, continuously scoring live traffic against the same
scorers used for the pre-promotion gate — so "did this regress after promotion" isn't a separate system
from "did this pass before promotion," it's the same measurement running on a schedule.

**What to say:** *"Traces weren't a bespoke log format — they landed in Unity Catalog tables, so they
were queryable with SQL and governed the same way as every other table, and production monitoring was
the same evaluation scorers running continuously against live traces instead of a one-time gate."*

## 6. Drift, cost attribution, and audit → Unity Catalog system tables

The generic concept: alert on drift (refusal rate, error rate, cost per run) before it becomes a
visible incident; attribute cost per tenant/workflow/model; keep a full audit trail of who did what.

**The real mechanism — three different system tables, three different questions:**

- **`system.access.audit`** — every permission grant/revoke and access event, queryable with SQL. This
  is the literal audit trail this whole series argues every AI system needs, already built into the
  platform rather than something to construct from scratch.
- **`system.billing.usage`** — usage and cost by workspace/SKU, the raw material for per-tenant or
  per-workload cost attribution (the exact gap named in the agent-platform observability doc as
  "a report, not a missing signal").
- **Data profiling / drift detection** — Unity Catalog's data-profiling capability computes profile
  metrics over a table's history, which is the same instinct as drift alerting on model outputs,
  applied to underlying data instead of model behavior — worth naming as the platform-native version of
  "alert when the distribution of what you're seeing changes."

**What to say:** *"Audit wasn't a custom table I built — `system.access.audit` already has every
access event, queryable with plain SQL. Cost attribution came from `system.billing.usage` rolled up by
workspace and SKU. And where we needed drift detection, Unity Catalog's data-profiling capability gave
us that as a platform feature rather than something to build."*

---

## Quick mapping table

| Generic AgentOps concept | Databricks mechanism |
| --- | --- |
| Versioned prompt/config artifact | Unity Catalog Model Registry, addressed by alias |
| Automated prompt improvement | `optimize_prompts()` (GEPA) |
| Pre-promotion quality/safety gate | `mlflow.genai.evaluate()` with scorers/judges |
| Judge calibration against human labels | MemAlign judge alignment via SME labeling |
| Baseline comparison for regressions | Named evaluation runs |
| Canary / percentage rollout | Model Serving traffic-config routing across served entities |
| Shadow mode | Candidate version logged without live traffic, or gated behind an approval step |
| Rollback | Alias repoint + endpoint config update, together |
| Tracing | MLflow Tracing, written to Unity Catalog tables |
| Production monitoring | The same scorers, run continuously against live traces |
| Audit trail | `system.access.audit` |
| Cost attribution | `system.billing.usage` |
| Data drift | Unity Catalog data profiling |

---

## What to say if asked directly

*"Everything in my system-design answer generalizes across any platform — that's how I'd design it
cold. On this specific engagement, I actually built it on Databricks: prompt and agent versions were
registered models in Unity Catalog addressed by alias, promotion gated on `mlflow.genai.evaluate()`
with a judge calibrated against real SME labels, canary rollout was a Model Serving traffic split,
rollback was an alias repoint, and traces landed in Unity Catalog tables so they were queryable and
governed the same way as everything else — with audit, cost, and drift signals coming from the
platform's own system tables rather than something I had to build from scratch."*
