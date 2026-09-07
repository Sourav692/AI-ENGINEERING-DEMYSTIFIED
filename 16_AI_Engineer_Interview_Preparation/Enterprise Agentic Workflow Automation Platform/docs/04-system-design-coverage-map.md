# System Design Coverage Map — what this project proves vs. what's cheat-sheet only

**What this is:** every pointer named in `../../DevRev-SystemDesign-Prep.docx` §3 ("Problem Type A —
AI Agent Platform"), plus relevant bits of §6/§7, checked against what `agent_platform` actually
implements — same method as the other two projects' coverage maps.

**Why this matters for the interview:** for a ✅ item you can say *"I built this — let me show you"*
and point at a running demo (`python scripts/run_workflow_demo.py`,
`python scripts/demo_guardrail_failure.py`). For a ❌ item you are speaking from the prep doc, not
the code.

**Legend:** ✅ covered and runnable · 🟡 partial (the concept exists, scaled down or simplified) · ❌ not built

**The "To close this gap" column** on every ❌/🟡 row tells you what it would actually take —
**Code — low/moderate/large**, or **Verbal only** with a **"What to say"** column carrying the
ready-to-speak answer.

---

## §3.1 — The Question Behind the Question

| Pointer | Status | Where |
|---|---|---|
| The hard part is safe, predictable configuration by a non-technical user, not running an agent | 🟡 | The *safety* mechanisms (guardrails, staged rollout) are real; the *non-technical authoring surface* is not — see §3.3 below |
| The same workflow fires from multiple channels, different context each time | ✅ | `channels.py` — event shape is identical downstream regardless of source |
| Testing a workflow before enabling it | ✅ | `SHADOW` status — destructive steps are refused unconditionally |
| Stopping a bad workflow mid-flight | ✅ | Step/spend budget halts a run rather than looping; the entity lock stops a second run compounding the damage |

---

## §3.2 — Reference Architecture

| Pointer | Status | Where | To close this gap |
|---|---|---|---|
| Channel adapters → canonical Event schema | ✅ | `channels.py` | — |
| Trigger and routing layer | ✅ | `routing.py` | — |
| Workflow definition store, versioned, declarative | ✅ | `workflows.py::WorkflowStore` | — |
| ...authored through a visual builder, never raw code | 🟡 | Specs are real `WorkflowSpec` dataclasses (declarative data, not code the orchestrator executes as code) — but there's no builder UI; they're constructed directly in Python here, standing in for what a builder would emit | **Code — large, and mostly a UI project.** The data model already *is* what a builder would serialize to; building an actual visual/form-based editor is a frontend effort disproportionate to this demo's scope. |
| Orchestration engine: durable, checkpointed, resumable | ✅ | `orchestrator.py` — demoed with a simulated crash mid-run | — |
| ...with automatic retries | ❌ | `resume()` exists and is correct, but nothing calls it automatically on failure — every resume in this project is an explicit call | **Code — low.** A thin retry wrapper around `run_workflow()`/`resume()` with backoff would close this; the hard part (idempotent, checkpointed resumption) is already done — this is scheduling, not correctness. |
| Agent runtime: plan → select tool → call → observe → iterate, hard step cap | 🟡 | The loop shape is real and the step cap is enforced; the "planner" is a fixed step list, not an LLM choosing the next tool dynamically | **Code — moderate.** Swap the fixed step list for a call to a real LLM (or a rule engine) that selects the next tool from the registry given the run's observed state so far — the same "reasoning loop, deterministic guardrails around it" architecture, just with a real planner instead of a scripted one. |
| Tool registry: typed, scoped, destructive flag | ✅ | `tools.py::REGISTRY` | — |
| Connector layer: authenticated integrations, secrets vault | ❌ | Not built — no credential storage of any kind exists | **Code — moderate**, mostly plumbing: a `Connector` model with a reference to a secret (never the secret itself) held in a vault abstraction, resolved only at call time. The genuinely hard part — a real secrets manager — is infrastructure, not application code; see the verbal-only scale section below. |
| Policy/guardrail service: approval gates | ✅ | `guardrails.py::authorize_step()` | — |
| ...spend caps | ✅ | Same function — the tighter of workflow and tenant policy | — |
| ...PII redaction | ❌ | Not built | **Code — low.** `enterprise_rag_platform`'s `authz/enforcement.py::redact_pii()` already exists and is directly reusable — this would be a guardrail obligation applied to a step's *output* (e.g. a drafted reply) before it's shown to a human for approval, the same "obligation attached to an allow" pattern as the RAG project. |
| Run store and trace log | ✅ | `observability.py` | — |

---

## §3.3 — The Non-Technical User Problem

| Pointer | Status | Where | To close this gap |
|---|---|---|---|
| Templates, not a blank canvas | ❌ | No template library or clone-and-edit mechanism exists | **Code — low.** A small library of pre-built `WorkflowSpec`s (parallel to `delivery_framework_platform`'s accelerator library) that a new workflow starts from via a `clone()` function, tracked the same way accelerator reuse is tracked there. |
| Natural-language authoring compiling to a reviewable spec | ❌ | Not built — needs a real LLM | **Verbal, mostly**, one tractable code slice. | *"This needs a genuine LLM call — generate a candidate `WorkflowSpec` from a natural-language description, then show the user the generated spec for confirmation before it's ever published. The 'confirmation before publish' half is nearly free to add on top of what exists — `workflows.py::promote()` already gates every status change behind a human decision, so an NL-generated spec would just enter at `DRAFT` and go through the exact same gate as a hand-written one. The generation half is the real LLM-integration work, deliberately not built here, the same choice the other two projects made about not calling a real model where determinism mattered more for testing."* |
| Dry-run/simulation mode, all writes mocked | ✅ | `SHADOW` status | — |
| Plain-language run history | ❌ | The trace is structured (`observability.py::render_run()`), not natural language | **Code — low.** A template or small LLM call that turns `render_run()`'s structured events into a sentence-per-step summary — genuinely low effort since all the underlying data is already captured faithfully. |
| Staged rollout: draft → test → shadow → live (approved) → autonomous | ✅ | `workflows.py::promote()` | — |

---

## §3.5 — Likely Follow-Ups

| Follow-up | Status | Where | To close this gap |
|---|---|---|---|
| Orchestrator restarts mid-run — what happens? | ✅ Directly demoed | `orchestrator.resume()`, checkpoint = `next_step_index` | — |
| Two workflows conflict on the same event | ✅ Directly demoed | `routing.py` — priority + entity lock | — |
| Safely adding a custom tool | 🟡 | Schema validation (`tools.py::validate_args()`) and scoping (`ToolDefinition.scopes`) exist | **Code — moderate.** Sandboxed execution and a review-before-publish workflow for a *new* tool definition don't exist — the closest existing pattern to reuse is `workflows.py::promote()`'s role-gated staged approval, applied to tools instead of workflows. |
| Versioning a live workflow | ✅ | `WorkflowStore` keeps every version; a `Run` pins to the version it started on | — |
| ...with gradual migration | ❌ | No traffic-split mechanism between two versions of the same workflow | **Code — moderate.** A `traffic_split: Dict[int, float]` (version → percentage) on `WorkflowSpec`, consulted by `routing.py::selected_workflow()` to choose which version's steps to run — the same shape as `delivery_framework_platform`'s documented-but-unbuilt canary-rollout gap. |

---

## The scale gap — concurrency and volume

| Pointer | Status | Where | To close this gap | What to say |
|---|---|---|---|---|
| Locks, idempotency keys, and version stores work across many processes and high event volume | ❌ | `routing._LOCKS`, `orchestrator._SIDE_EFFECTS`, and `WorkflowStore` are all plain in-process dicts — correct for one process, not for a real deployment | **Verbal, mostly**, with one tractable slice. | *"The entity lock and idempotency-key mechanisms are correct in shape but wrong in storage — a real deployment needs a distributed lock (Redis, or a database row with a unique constraint) and a durable idempotency-key store, not an in-memory dict that resets on restart and isn't shared across workers. The mechanism doesn't change, only where it's persisted — which is exactly why I built the logic against a thin key-value interface conceptually, even though this demo's implementation is in-memory. The tractable code slice is swapping the dict for a real store behind the same two functions, `acquire_lock`/`release_lock`; the infrastructure underneath (an actual Redis instance, actual database) is what I can't stand up for a local demo."* |

---

## Punch list — code-change gaps, sorted by effort

**Low effort**
- Template library + `clone()` — reuses the delivery framework's accelerator-library pattern
- Automatic retry-with-backoff wrapper around `resume()` — the hard part (idempotent resumption) is already done
- PII redaction on step outputs — directly reuses `enterprise_rag_platform`'s `redact_pii()`
- Plain-language run summary generated from `render_run()`'s structured events

**Moderate effort**
- A `Connector` model + secrets-vault abstraction (credentials never inline, resolved only at call time)
- Real LLM-driven tool selection replacing the fixed step-list "planner"
- Sandboxed custom-tool review pipeline, reusing `promote()`'s role-gated pattern
- Gradual/canary migration between two live versions of the same workflow

**Large / likely out of scope for this demo**
- An actual visual workflow builder (a genuine frontend project)
- A real secrets manager and distributed lock/idempotency store (infrastructure, not application code)

---

## The one-paragraph interview framing

This project gives a *provably enforced* answer to §3.4's actual ask — deterministic control flow
around probabilistic reasoning — not a description of it. Idempotency, durability, budget
enforcement, and role-gated staged rollout are all real and tested, including the negative cases
(wrong role, skipped stage, double-applied side effect, runaway step count). It does **not**
demonstrate the two things that would make this genuinely usable by a non-technical user — a real
authoring surface (visual or natural-language) and connector credentials against a real system —
because both are either a frontend project or an LLM-integration project in their own right, the
same honest boundary the other two projects in this series draw around what a local demo can and
can't prove.

---

## See also

- `../../DevRev-SystemDesign-Prep.docx` — the source prep document this map is checked against
- `01-theory.md` — the concepts, and why the shape mirrors the other two projects on purpose
- `02-architecture-end-to-end.md` — the pipeline, diagrammed end to end
- `03-src-modules-reference.md` — every function in `src/agent_platform`
- `../INTERVIEW_SCRIPT.md` — the whiteboard script
- `../../enterprise_rag_platform/docs/07-system-design-coverage-map.md` — the equivalent map for Problem Type B
- `../../delivery_framework_platform/docs/04-system-design-coverage-map.md` — the equivalent map for Problem Type C
