# Coverage Map — What This Project Proves vs What Is Cheat-Sheet Only

> **Level** 🟡 Building Production Systems · **Module** 05 · **Doc** 7 of 7 · **Time** ~20 min
> **Prerequisites:** docs 1–5 of this module
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise Agentic Workflow Automation Platform/docs/04-system-design-coverage-map.md`
> **Note:** the original checks the project against §3 of a company-specific prep guide. Section labels are kept for traceability; the topics are stated in full.

## Why this matters

Same discipline as Module 04's coverage map: for every claim, *built and runnable* or *known but not demonstrated*. This project's honest boundary is sharper than the RAG project's, because it deliberately contains no LLM — so the map is as much about what that choice bought as what it cost.

**Legend:** ✅ covered and runnable · 🟡 partial · ❌ not built.

## The question behind the question (§3.1)

| Pointer | Status | Where |
|---|---|---|
| The hard part is safe, predictable configuration by a non-technical user | 🟡 | The *safety* mechanisms are real; the *authoring surface* is not |
| The same workflow fires from multiple channels | ✅ | `channels.py` — identical downstream regardless of source |
| Testing a workflow before enabling it | ✅ | `SHADOW` — destructive steps refused unconditionally |
| Stopping a bad workflow mid-flight | ✅ | Step/spend budget halts rather than loops; the entity lock stops a second run compounding the damage |

## Reference architecture (§3.2)

| Layer | Status | Where | To close |
|---|---|---|---|
| Channel adapters → canonical event | ✅ | `channels.py` | — |
| Trigger and routing | ✅ | `routing.py` | — |
| Versioned, declarative workflow store | ✅ | `workflows.py::WorkflowStore` | — |
| …authored through a visual builder | 🟡 | The spec *is* what a builder would serialise to; there is no builder | **Code — large, mostly a UI project** |
| Durable, checkpointed, resumable orchestration | ✅ | `orchestrator.py` — demoed with a simulated crash | — |
| …with automatic retries | ❌ | `resume()` is correct but nothing calls it automatically | **Code — low.** A retry wrapper with backoff; the hard part (idempotent resumption) is done |
| Agent runtime with a hard step cap | 🟡 | Loop shape and cap are real; the planner is a fixed step list | **Code — moderate.** Swap the list for an LLM or rule engine selecting the next tool from observed state — same architecture, real planner |
| Typed, scoped tool registry with destructive flag | ✅ | `tools.py::REGISTRY` | — |
| Connector layer with secrets vault | ❌ | No credential storage exists | **Code — moderate** for a `Connector` model referencing a vault secret; the vault itself is infrastructure |
| Approval gates | ✅ | `guardrails.py::authorize_step()` | — |
| Spend caps | ✅ | Same function — tighter of workflow and tenant | — |
| PII redaction | ❌ | Not built | **Code — low.** Module 04's `redact_pii()` is directly reusable as an obligation on a step's *output* before a human sees it |
| Run store and trace | ✅ | `observability.py` | — |

## The non-technical user problem (§3.3)

| Pointer | Status | To close / what to say |
|---|---|---|
| Templates, not a blank canvas | ❌ | **Code — low.** A library of pre-built `WorkflowSpec`s with `clone()`, tracked the way Module 10's accelerator reuse is tracked |
| Natural-language authoring → reviewable spec | ❌ | **Verbal, mostly.** *"This needs a real LLM call — generate a candidate spec from a description, then show it for confirmation before it is published. The confirmation half is nearly free: `promote()` already gates every status change behind a human, so an NL-generated spec enters at `DRAFT` and goes through the same gate as a hand-written one. The generation half is the LLM-integration work, deliberately not built, for the same reason the other projects avoided a live model where determinism mattered more for testing."* |
| Dry-run mode, all writes mocked | ✅ | `SHADOW` |
| Plain-language run history | ❌ | **Code — low.** A template or small LLM call over `render_run()`'s structured events |
| Staged rollout | ✅ | `promote()` |

## Likely follow-ups (§3.5)

| Follow-up | Status | Where / to close |
|---|---|---|
| Orchestrator restarts mid-run | ✅ Demoed | `resume()`, checkpoint = `next_step_index` |
| Two workflows conflict on one event | ✅ Demoed | Priority + entity lock |
| Safely adding a custom tool | 🟡 | Schema validation and scoping exist; sandboxed execution and review-before-publish do not — reuse `promote()`'s role-gated pattern for tools |
| Versioning a live workflow | ✅ | Every version kept; a run pins to its version |
| …with gradual migration | ❌ | **Code — moderate.** A `traffic_split` on the spec, consulted by routing — the same shape as Module 10's unbuilt canary gap |

## The scale gap

| Pointer | Status | What to say |
|---|---|---|
| Locks, idempotency keys and version stores across many processes and high volume | ❌ In-process dicts | *"The entity lock and idempotency mechanisms are correct in shape but wrong in storage — a real deployment needs a distributed lock (Redis, or a database row with a unique constraint) and a durable idempotency-key store shared across workers. The mechanism doesn't change, only where it's persisted — which is why the logic sits behind `acquire_lock`/`release_lock` and one `_apply_side_effect`. The tractable slice is swapping the dict for a real store behind those functions; the infrastructure underneath is what a local demo can't stand up."* |

## Punch list, by effort

**Low:** template library + `clone()`; automatic retry wrapper around `resume()`; PII redaction on step outputs; plain-language run summary.

**Moderate:** `Connector` model + vault abstraction; a real planner replacing the fixed step list; sandboxed custom-tool review; canary migration between versions.

**Large / out of scope:** a visual builder (a frontend project); a real secrets manager and distributed lock store (infrastructure).

## The one-paragraph framing

This project gives a *provably enforced* answer to the actual ask — deterministic control flow around probabilistic reasoning — not a description of it. Idempotency, durability, budget enforcement and role-gated staged rollout are all real and tested, including the negative cases: wrong role, skipped stage, double-applied side effect, runaway step count, oversized refund, concurrent run. It does **not** demonstrate the two things that would make it usable by a non-technical user — a real authoring surface and connector credentials against a real system — because both are a frontend or LLM-integration project in their own right. That is the same honest boundary the other two projects draw around what a local demo can prove.

## Checkpoint

- Which three claims are demonstrated by *negative* tests, and why does that matter more than the happy path?
- Deliver the "what to say" for natural-language authoring and for the scale gap without notes.
- What does the no-LLM choice buy, and what does it cost? Name one row for each.
- Which Module 04 function is directly reusable here, and for what?

**Next →** [Module 06 · Cross-Cutting Concerns](../06_Cross_Cutting_Concerns/README.md)
