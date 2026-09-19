# System Design Coverage Map — what this project proves vs. what's cheat-sheet only

**What this is:** every pointer named in `../../DevRev-SystemDesign-Prep.docx` §5 ("Problem Type C —
Scoping Doc to Deployed Agent in Under 2 Weeks"), plus the parts of §7 (Agent CI/CD) and §9
(prep-order framing) that bear directly on it, checked against what `delivery_framework_platform`
actually implements — same method as `enterprise_rag_platform/docs/07-system-design-coverage-map.md`.

**Why this matters for the interview:** for a ✅ item you can say *"I built this — let me show you"*
and point at a running demo (`python scripts/run_engagement_demo.py`,
`python scripts/demo_gate_failure.py`). For a ❌ item you are speaking from the prep doc, not the
code.

**Legend:** ✅ covered and runnable · 🟡 partial (the concept exists, scaled down or simplified) · ❌ not built

**The "To close this gap" column** on every ❌/🟡 row tells you what it would actually take:
- **Code — low/moderate/large** effort: a real codebase change, roughly sized
- **Verbal only**: infeasible or out of scope to genuinely demo locally (real infra, real scale) —
  answer from the prep doc, and say so if asked whether it's built. Where this applies, the row also
  carries a **"What to say"** column with the answer worded ready to speak.

---

## §5.1 — Why This Problem Is Here

| Pointer | Status | Where |
|---|---|---|
| Answer it as a system with inputs, stages, artefacts, gates, metrics — draw as a pipeline | ✅ | The whole package; `docs/02-architecture-end-to-end.md` §2 is the diagram to draw |
| Productised delivery process backed by reusable assets, not heroics/bespoke code per customer | ✅ | `accelerators.py` + `metrics.py::accelerator_reuse_rate()` turns this claim into a number |

---

## §5.2 — The Two-Week Pipeline

| Pointer | Status | Where |
|---|---|---|
| Seven stages, correct order, correct day ranges | ✅ | `models.py::Stage`, `STAGE_ORDER` |
| Order is enforced, not just documented | ✅ | `engine.py::advance_stage()` — only ever moves to the immediate next stage; there is no "skip a stage" code path |

This is the strongest section — every named stage is not just listed but **structurally
unskippable**, the same property the RAG project has for its ACL pre-filter.

---

## §5.3 — What Makes It Repeatable

| Pointer | Status | Where | To close this gap |
|---|---|---|---|
| Reusable accelerator library (connectors, prompt templates, eval harness, guardrail policies, dashboard templates) | ✅ | `accelerators.py::LIBRARY` — all five kinds represented | — |
| Standard scoping questionnaire that fails fast | ✅ | `pipeline.py::intake()` — refuses unmeasurable metrics, no SME, or no data sources before day 1 starts | — |
| Infrastructure as code + environment templates, so a new deployment is a parameterised config, not a project | ❌ | Not built — no config-templating or provisioning of any kind exists | **Code — moderate.** A `deployment_config.py` that renders a per-customer settings bundle from one base template plus customer-specific parameters (tenant name, data sources, model routing) would make "new customer = config, not a project" an actual artefact instead of a claim. It would not provision *real* infrastructure — that part stays verbal (see the punch list). |
| Pre-built eval harness so the golden set is the only new artefact per engagement | 🟡 | `golden_set_harness` is a named entry in the accelerator library and gets "pulled" in the demo — but nothing here actually *runs* an eval; the score (`0.83`) is a hardcoded demo value | **Code — moderate.** The real harness already exists one project over — `enterprise_rag_platform/src/enterprise_rag/evaluation/harness.py`. Wiring the Evaluate stage to actually import and call `run_eval()` against a real golden set (even a 3-case one) would make `eval_baseline_met`'s evidence a computed number instead of an asserted one. |
| Definition of done includes observability and a runbook | ✅ | `observability.py` + `rollback_runbook.md`/`handover_runbook.md` artifacts in the demo | — |

---

## §5.4 — Gates, Risks, and Metrics

| Pointer | Status | Where |
|---|---|---|
| Hard gates: security review, data access, golden set, eval baseline, rollback tested | ✅ | `gates.py::GATE_DEFINITIONS` |
| Data access delays — mitigation: start day 1, escalate day 3 | ✅ Directly demoed | `engine.py::check_escalation_triggers()`, `scripts/demo_gate_failure.py` step 6 |
| Unmeasurable success criteria — mitigation: refuse to start | ✅ Directly demoed | `pipeline.py::intake()`, `scripts/demo_gate_failure.py` step 1 |
| No customer SME — mitigation: contractual prerequisite | ✅ | `pipeline.py::intake()` |
| Time-to-first-value, eval score at handover, override rate, week-4 retention | ✅ | `metrics.py` — all four |
| "Some engagements should not be two weeks — knowing which to reject is part of the framework" | ✅ | Intake refusal is unconditional; nothing forces every request to be accepted |

| Pointer | Status | Where | To close this gap |
|---|---|---|---|
| Scope creep — mitigation: change-control on the signed scope | ❌ | Not built — `success_metrics`/`data_sources` are set once at intake and there's no governed path to change them mid-engagement | **Code — low.** A `request_scope_change(engagement, changes, signer)` requiring `signer.role == "sponsor"`, logged either way — this is almost exactly `gates.py::sign_off()`'s shape reused for a different decision, so it's cheap given the pattern already exists. |

---

## Related — §7 Agent CI/CD (rollback and rollout, applied to this pipeline)

| Pointer | Status | Where | To close this gap |
|---|---|---|---|
| Rollback must be a config change, not a redeploy — a version pointer flip | 🟡 | `rollback_tested` is a real, enforced gate — but it's an *attestation* ("evidence says rollback was tested"), not an implementation of rollback itself | **Code — moderate.** A small `deployment_version.py` with `deploy(version)`/`rollback_to(version)` and an immutable version history would let the gate's evidence point at an actual rollback call that ran, rather than a text string asserting it happened. |
| Canary / progressive rollout to a percentage of traffic | ❌ | `LIMITED_PROD` is a stage name, not a number — no traffic-percentage concept exists | **Code — low.** Add a `traffic_percentage` field to `Engagement` and a `set_traffic()` function only callable inside `LIMITED_PROD`, so "limited" becomes a measurable quantity. |

---

## The scale gap — running more than one engagement at once

| Pointer | Status | Where | To close this gap | What to say |
|---|---|---|---|---|
| A real FDA runs several customer engagements in parallel, with finite capacity | ❌ | This package models exactly one `Engagement` at a time — no portfolio view, no per-person capacity tracking | **Verbal, mostly**, with one tractable code slice. | *"The stage/gate model doesn't change with portfolio size — it's the same state machine per engagement. What's missing is a registry layer: which engagements are active, whose desk they're on, and a capacity signal (how many engagements one FDA can carry without every gate becoming a bottleneck). That's a genuinely different problem — resource scheduling, not delivery-process design — and I'd want real engagement-duration data before designing it, not guess at a number. The tractable piece I could add here is just a dict-of-Engagements registry with a `week4_retention`/`gates_passed_ratio` roll-up across all of them — a one-file addition — but a real capacity model needs production data this local demo can't produce, the same way the RAG project's '10M chunks' cost story can't be proven on a 22-document corpus."* |

---

## Punch list — code-change gaps, sorted by effort

**Low effort**
- `request_scope_change()` — change-control on scope creep, reusing the `sign_off()` pattern
- `traffic_percentage` on `Engagement` — makes "limited production" a number

**Moderate effort**
- `deployment_config.py` — parameterised per-customer config templating (proves "config, not a project")
- Wire the Evaluate stage to `enterprise_rag_platform`'s real `evaluation.harness.run_eval()` instead of a hardcoded score
- `deployment_version.py` — an actual rollback mechanism behind the `rollback_tested` gate's evidence

**Large / likely out of scope for this demo**
- Multi-engagement portfolio view + FDA capacity modeling — needs real engagement-duration data, not a local demo
- Real infrastructure provisioning (actual customer environment connection, actual IaC execution)

---

## The one-paragraph interview framing

This project gives a *provably enforced* answer to the part of Problem Type C most candidates only
describe: the pipeline's gates actually block, the wrong role genuinely cannot sign off a gate, and
a request with no measurable success metric is refused before day 1 rather than quietly defaulted
into a doomed two-week clock. It does **not** demonstrate real infrastructure provisioning, a
running eval harness (the golden-set score is asserted, not computed, in the demo), or
multi-engagement portfolio scale — for those, the honest answer is to speak from
`DevRev-SystemDesign-Prep.docx` §5/§7 directly. Per the prep doc's own prioritization (§9, item 7),
this problem type is lower-likelihood as a full question than the agent-platform or RAG rounds — but
it doubles as the most direct evidence of "founder's-mentality" and process thinking, which is
exactly what §10's checklist asks you to ground with a concrete delivery story.

---

## See also

- `../../DevRev-SystemDesign-Prep.docx` — the source prep document this map is checked against
- `01-theory.md` — the concepts, and why the shape mirrors the RAG project on purpose
- `02-architecture-end-to-end.md` — the pipeline, diagrammed end to end
- `03-src-modules-reference.md` — every function in `src/delivery_framework`
- `../INTERVIEW_SCRIPT.md` — the whiteboard script
- `../../enterprise_rag_platform/docs/07-system-design-coverage-map.md` — the equivalent map for Problem Type B
