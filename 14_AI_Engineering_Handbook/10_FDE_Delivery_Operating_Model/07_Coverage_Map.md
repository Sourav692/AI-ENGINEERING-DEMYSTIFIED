# Coverage Map — What This Project Proves vs What Is Cheat-Sheet Only

> **Level** 🔴 The FDE Role · **Module** 10 · **Doc** 7 of 7 · **Time** ~20 min
> **Prerequisites:** docs 3–4 of this module
> **Source material:** `4. FDE_Related_Preparation/Delivery Framework from Scoping to Delivery/docs/04-system-design-coverage-map.md`; `README.md` ("What this deliberately does not do")
> **Note:** the original checks the project against §5 and §7 of a company-specific prep guide. Section labels are kept for traceability.

## Why this matters

The third and last coverage map in the handbook, and the one where the honest boundary is easiest to blur — because a delivery process is mostly *not* code, and it is tempting to let a demo of the state machine imply the whole engagement was demonstrated. It was not. This map says exactly what was.

**Legend:** ✅ covered and runnable · 🟡 partial · ❌ not built.

## Why the problem is here (§5.1)

| Pointer | Status | Where |
|---|---|---|
| Answer it as a system — inputs, stages, artefacts, gates, metrics — drawn as a pipeline | ✅ | The whole package; doc 3's state machine is the diagram |
| A productised process backed by reusable assets, not heroics | ✅ | `accelerators.py` + `accelerator_reuse_rate()` — the claim as a number |

## The two-week pipeline (§5.2)

| Pointer | Status | Where |
|---|---|---|
| Seven stages, correct order, correct day ranges | ✅ | `models.py::Stage`, `STAGE_ORDER` |
| Order enforced, not just documented | ✅ | `advance_stage()` only ever moves to the immediate next stage; no skip path exists |

The strongest section: every stage is structurally unskippable — the same property Module 04 has for its pre-filter.

## What makes it repeatable (§5.3)

| Pointer | Status | Where / to close |
|---|---|---|
| Reusable accelerator library — five kinds | ✅ | `LIBRARY` |
| A scoping questionnaire that fails fast | ✅ | `intake()` |
| Infrastructure as code and environment templates, so a new deployment is config, not a project | ❌ | **Code — moderate.** A per-customer settings bundle rendered from one base template. Would not provision real infrastructure — that stays verbal |
| A pre-built eval harness so the golden set is the only new artefact per engagement | 🟡 | `golden_set_harness` is a named library entry that gets pulled — but nothing *runs* an eval; the 0.83 is a hardcoded demo value. **Code — moderate.** The real harness exists in Module 04's project; wiring the Evaluate stage to call `run_eval()` against even a three-case golden set would make the gate's evidence a computed number |
| Definition of done includes observability and a runbook | ✅ | `observability.py`; `rollback_runbook.md` and `handover_runbook.md` artefacts in the demo |

## Gates, risks and metrics (§5.4)

| Pointer | Status | Where |
|---|---|---|
| Hard gates: security review, data access, golden set, eval baseline, rollback tested | ✅ | `GATE_DEFINITIONS` |
| Data-access delay → start day 1, escalate day 3 | ✅ Demoed | `check_escalation_triggers()` |
| Unmeasurable success criteria → refuse to start | ✅ Demoed | `intake()` |
| No customer SME → contractual prerequisite | ✅ | `intake()` |
| Time-to-first-value, eval score at handover, override rate, week-4 retention | ✅ | `metrics.py` — all four |
| "Some engagements should not be two weeks" | ✅ | Intake refusal is unconditional |
| Scope creep → change-control on signed scope | ❌ | **Code — low.** `request_scope_change(engagement, changes, signer)` requiring the sponsor role — `sign_off()`'s shape reused for a different decision |

## Agent CI/CD applied to the pipeline (§7)

| Pointer | Status | Where / to close |
|---|---|---|
| Rollback as a version-pointer flip, not a redeploy | 🟡 | `rollback_tested` is a real, enforced gate — but an *attestation* that rollback was tested, not an implementation of rollback. **Code — moderate.** A `deploy(version)` / `rollback_to(version)` with an immutable history would let the evidence point at a rollback that actually ran |
| Canary / progressive rollout | ❌ | `LIMITED_PROD` is a stage name, not a number. **Code — low.** A `traffic_percentage` settable only inside `LIMITED_PROD` |

## The scale gap — many engagements at once

| Pointer | Status | What to say |
|---|---|---|
| A real FDA runs several engagements in parallel with finite capacity | ❌ One `Engagement` at a time | *"The stage/gate model doesn't change with portfolio size — it's the same state machine per engagement. What's missing is a registry layer: which engagements are active, whose desk they're on, and a capacity signal — how many one FDA can carry before every gate becomes a bottleneck. That's a genuinely different problem — resource scheduling, not delivery-process design — and I'd want real engagement-duration data before designing it. The tractable slice is a dict-of-engagements registry with a retention and gates-passed roll-up; a real capacity model needs production data a local demo can't produce, the same way the RAG project's 10M-chunk cost story can't be proven on 22 documents."* And underneath it, doc 4's point: it is also a tenancy decision about the process's own data |

## Punch list, by effort

**Low:** `request_scope_change()`; `traffic_percentage` on `Engagement`.

**Moderate:** per-customer config templating; wire Evaluate to Module 04's real `run_eval()`; an actual rollback mechanism behind the gate's evidence.

**Large / out of scope:** a multi-engagement portfolio and capacity model (needs real data); real infrastructure provisioning.

## What this deliberately does not do

- **No real infrastructure provisioning.** "Configure, do not code" is modelled as pulling named assets from a registry, not standing up connectors against a real customer environment.
- **The eval harness is referenced, not run.**
- **One engagement at a time.**
- **No change-control mechanism yet.**
- **Rollback is an attestation, not a mechanism.**

## The one-paragraph framing

This project gives a *provably enforced* answer to the part of the delivery-framework question most candidates only describe: the gates actually block, the wrong role genuinely cannot sign, and a request with no measurable metric is refused before day 1 rather than defaulted into a doomed two-week clock. It does **not** demonstrate real provisioning, a running eval harness, or portfolio scale — for those, the honest answer is to speak from the operating-model knowledge in this module and Module 08, and say so. This problem type is lower-likelihood as a full design question than the RAG or agent-platform rounds — but it is the most direct evidence of process thinking and founder's mentality, which is exactly what a delivery story in Module 11 has to be grounded in.

## Checkpoint

- Which three properties are proven by negative tests?
- What is the difference between `rollback_tested` as an attestation and as a mechanism?
- Deliver the scale-gap answer without notes, including the tenancy point.
- Which Module 04 artefact would close the biggest 🟡, and how?

**Next →** [Module 11 · Telling the Story](../11_Telling_The_Story/README.md)
