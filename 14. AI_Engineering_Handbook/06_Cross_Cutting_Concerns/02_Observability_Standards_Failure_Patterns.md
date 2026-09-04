# Observability Standards and Failure Patterns

> **Level** 🟠 Scale, Security, Operations · **Module** 06 · **Doc** 2 of 7 · **Time** ~30 min
> **Prerequisites:** Module 03 doc 4, Module 04 doc 8 (the trace), Module 04 doc 5 (circuit breaker)
> **Source material:** `3. AI_Engineer_Interview_Preparation/Cross Cutting Preparation/02-observability-standards-and-failure-patterns.md`; `Enterprise Agentic Workflow Automation Platform/docs/05-security-tenancy-and-observability-gaps.md` §4

## Why this matters

Modules 03 and 04 built traces that capture the right data. This document is about what a trace is *for* once it leaves your laptop: a customer's monitoring stack has to read it, the customer has to see their own slice of it, and it has to drive alerts across many runs rather than explain one. And the second half covers four failure patterns that a circuit breaker alone does not handle — including the one a well-built staged rollout does not give you for free.

## 1 · Standard tracing, not a bespoke format

A trace that captures every step, every retrieved item, every tool call is good — but if it is a one-off format invented for this project, it only works inside this project.

Why the *standard* matters, not just the concept: the moment a customer wants their own tool — Datadog, Honeycomb, whatever they already run — to see your system's activity alongside their own request traces, a bespoke format means a bespoke integration for every customer. The fix is **OpenTelemetry-style spans**: every unit of work is a span with an ID, a parent ID (so spans form a tree), and a start and end time, decorated with your domain-specific fields — prompt version, retrieved document ids, tokens — as *attributes on the span* rather than a new schema. The data you capture does not change; only the wire format does, so it is readable by tools that already exist.

```
 trace: one request (run_id, tenant, principal, prompt_version)
   └─ span: authorize      attrs: filter_explanation
   └─ span: retrieve       attrs: strategy, candidate_ids, retrieved_by
   └─ span: enforce        attrs: allowed, denied, filter_disagreements
   └─ span: rerank         attrs: model, tokens, cost_usd
   └─ span: generate       attrs: cached, tokens, cost_usd
        └─ span: tool_call attrs: tool, status, ms   ← Module 03's per-call record
```

## 2 · Per-tenant dashboards — a customer-facing surface

Traces are usually something a developer reads after something goes wrong. In a customer-facing deployment the customer needs their own visibility: recall and accuracy trends, run success rate, escalation rate, cost — scoped to only their own data.

Conceptually, the data already exists in the trace store. A dashboard is a read-only aggregation over it, scoped by tenant the same way everything else is. The honest framing: this is a genuine frontend/BI project, reasonable to defer — but worth naming as a real requirement, because a forward-deployed engagement usually needs the *customer* to see this, not just the vendor's team.

## 3 · Traces are not enough — drift and attribution

Two questions a per-run trace alone does not answer:

**Drift alerting.** A sudden change in refusal rate, tool error rate or mean cost per run usually precedes a visible incident. A per-run budget that halts one runaway workflow is the same instinct applied to a single execution. Drift alerting applies it *across many runs over time*: compare today to a rolling baseline, page when it diverges. The scheduled evaluation run in the next document is one input; production metrics are the other.

**Cost attribution — who pays for a runaway agent?** Expect this question. You need totals by **tenant**, by **workflow**, and by **model** — not only a line item inside one run. That is aggregation over data the trace already has (Module 04's cost-by-purpose is the per-run half). The gap is a report and a bill, not a missing event.

## 4 · Multi-provider failover

A circuit breaker is good at one thing: *this provider is glitching right now, stop hammering it, try again soon.* It is not built for a longer outage — if the provider is down for twenty minutes, the breaker keeps waiting and retrying with nothing coming back.

For that you need a **backup provider**, not a pause-and-retry loop. Three pieces:

1. **Have a backup ready.** Do not build the system so it only knows one AI provider. Set it up to call a second one, or a smaller model, if the first is really down — decided in advance, not mid-outage. Module 04's `LLMClient` behind one interface is the seam.
2. **Tell the user when you have switched.** *"This answer used a backup system and may be less accurate"* — say so, rather than pretending everything is normal.
3. **Let the customer choose.** Some care more about accuracy than speed and would rather wait for the primary. This is a per-customer setting, not one rule for everyone.

## 5 · "Search index down → degrade gracefully, and say so"

A concrete instance of the same instinct. If retrieval combines dense and lexical search and one becomes unavailable, the fix is not to fail the request — fall back to whichever still works, and tell the user the answer used a narrower method than usual. When both methods already exist independently, this is a small wiring gap: the explicit fallback at the call site plus the disclosure in the response. Module 04's graph already degrades expansion to `dense`; this extends it one layer down.

## 6 · The bulkhead pattern

A distinct term from a circuit breaker, and interviewers notice if you conflate them:

| | Protects against | Mechanism |
|---|---|---|
| **Circuit breaker** | A dependency **failing repeatedly** | Temporarily stop calling it |
| **Bulkhead** | A dependency being **slow** (not failed) | Isolate its resource usage — its own small, dedicated pool of connections or threads — so a call that hangs for thirty seconds exhausts only its own pool, never the shared pool every other request across every other customer depends on |

Short version: a circuit breaker asks *is this dependency healthy?* A bulkhead asks *even if it isn't, can it only hurt itself?*

## 7 · A genuine kill switch

A staged rollout — draft → test → shadow → live → autonomous — is a **graceful, deliberate** state change: someone decides to move something forward or back a stage. That is a different mechanism from what an actual incident needs: **an emergency override that stops everything for a workflow or tenant, immediately, regardless of what is already running.**

- A kill switch does not ask "should this be demoted to a safer stage?" It asks "halt everything in this scope, right now" — including work mid-flight, not just new work.
- It must interrupt **in-flight** execution. A rollout demotion might only affect future authorisation checks, letting anything already past that check keep going. A real kill switch needs a separate path that reaches in and stops active work.
- It must be fast and simple to pull under pressure — a single flip a human can trigger, not a role-gated multi-step approval. That is the *opposite* instinct from a staged rollout, and worth stating as such if asked whether they are the same thing.

## Interview lens

> *"My tracing captures the right data, but as a custom format it wouldn't plug into a customer's monitoring stack — a standard span format fixes that by carrying the same fields as attributes. On failures: a circuit breaker handles a provider being temporarily down but has nowhere to fail over to — a real deployment needs an explicit backup provider, and it should tell the user. And the one thing a well-built staged rollout doesn't give you for free is a kill switch — rollout is a deliberate, role-gated transition; a kill switch is a fast, blunt override for the moments an approval flow is too slow to matter."*

## Checkpoint

- Why does the *format* of a trace matter more than its contents once a customer is involved?
- What two questions do per-run traces not answer, and what answers them?
- Distinguish a circuit breaker, a backup provider and a bulkhead — what does each protect against?
- Why is a kill switch the opposite instinct from a staged rollout? Name two properties it needs that rollout demotion lacks.

**Next →** [Caching, Streaming, CI/CD Rigor and Build vs Buy](03_Caching_Streaming_CICD_BuildVsBuy.md)
