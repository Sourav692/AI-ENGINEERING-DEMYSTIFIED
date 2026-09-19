# Source Modules Reference — `src/delivery_framework`

**What this is:** every module and function in the package, 2-3 lines each — same purpose as
`enterprise_rag_platform/docs/05-src-modules-reference.md`.

**Overview:** the package has no LLM calls anywhere — every gate decision is deterministic, so the
whole test suite runs in well under a second. `models.py` defines the domain; `identity.py` and
`gates.py` are the ABAC-shaped authority layer; `pipeline.py` is the intake refusal gate;
`engine.py` is the state machine; `accelerators.py` and `metrics.py` are the reuse/measurement
layer; `observability.py` renders and persists the event log that every other module writes to via
`Engagement.log()`.

---

## models.py

The domain model. `Decision` is deliberately the same shape as `authz.policy.Decision` in the RAG
project.

- **`Stage`** (enum): the seven ordered pipeline stages, each carrying a day-range and label. `.order` gives its position in `STAGE_ORDER`.
- **`GateStatus`** (enum): `PENDING` / `PASSED` / `FAILED`.
- **`Decision`**: `allowed`, `rule`, `reason` — the outcome of one gate sign-off or stage-advance attempt. `.denied` is the negation of `.allowed`.
- **`Gate`**: a named, blocking condition — `required_before` (a `Stage`), `allowed_roles`, current `status`, and (once passed) `evidence`/`signed_by`/`signed_on_day`.
- **`Artifact`**: something a stage produced — `name`, `stage`, `produced_on_day`, `owner`.
- **`AcceleratorAsset`**: one entry in the reusable library — `name`, `kind`, `description`.
- **`Pull`**: a record of one stage either reusing an accelerator asset or building custom — `reused` is the field the reuse-rate metric reads.
- **`Escalation`**: `reason`, `raised_on_day`, `resolved`, `resolved_on_day`.
- **`Principal`**: `user_id`, `display_name`, `role` — who is attempting a sign-off.
- **`Engagement`**: the one mutable object per customer — current stage/day, all gates/artifacts/pulls/escalations/events, deployed flag, human-approval counters, eval scores, retention.
- **`Engagement.log(event_kind, **fields)`**: appends one event to `events`. Reserved keys (`day`, `stage`, `kind`) are set *last* in the dict build so a caller-supplied field of the same name can never silently clobber them — a real bug this project hit once (`accelerators.py`'s own `kind` field colliding with the event's `kind`), fixed by reordering the dict construction.

## identity.py

Four roles, resolved by lookup — never assumed from context, same instinct as the RAG project's
`identity.py`.

- **`get_principal(user_id)`**: returns the `Principal` for a known `user_id`; raises `KeyError` otherwise.
- **`list_principals()`**: all five seeded principals, including `u_fda_wrong_hat` — a negative control with the right person and the wrong role, used to prove role-checking isn't decorative.

## gates.py

The six gate definitions and the sign-off decision engine — same design rules as
`authz/policy.py::decide()`: deny overrides, ordered explicit rules, no override path for "I say
so."

- **`GATE_DEFINITIONS`**: the six `Gate` objects (five hard gates from §5.4 plus the terminal `success_metrics_met` go/no-go gate), each with its blocking stage and allowed roles.
- **`gates_for_stage(stage)`**: every gate definition that blocks entry to `stage`.
- **`sign_off(engagement, gate_name, signer, evidence)`**: the authoritative decision function. Three ordered deny rules — wrong role, missing evidence, an earlier-stage gate still pending — then an allow that sets `PASSED` with the signer/evidence/day recorded. Every attempt, allowed or denied, is logged.
- **`_earlier_unpassed_gates(engagement, before_stage)`**: internal — every gate required before an earlier stage than `before_stage` that hasn't passed yet, used to enforce sign-off ordering.
- **`blocking_gates(engagement, target_stage)`**: every gate required before `target_stage` that hasn't passed — what `engine.py::advance_stage()` checks before allowing a transition.

## pipeline.py

The intake refusal gate — the delivery framework's equivalent of the RAG project's loader refusing
a document with no usable ACL.

- **`ScopingRefused`**: raised when a scoping request cannot be started at all.
- **`intake(customer_name, success_metrics, data_sources, customer_sme, settings=SETTINGS)`**: validates a scoping request — refuses (raises) if success metrics are empty, no customer SME is assigned, or no data sources are named. Returns a fresh `Engagement` at `Stage.SCOPING`, day 1, only if all three hold.

## engine.py

The state machine — the counterpart to the RAG project's `graph/build.py` + `graph/nodes.py`.

- **`advance_stage(engagement, to_day=None)`**: attempts to move to `STAGE_ORDER[current+1]`. There is no code path that jumps further — "skip a stage" is not callable, the same way retrieval has no code path that skips the ACL filter. Blocked (with a named reason) if any gate required before the next stage hasn't passed.
- **`mark_deployed(engagement)`**: the terminal transition. Only legal from `Stage.GO_NO_GO`, and only once `success_metrics_met` has passed.
- **`record_artifact(engagement, name, owner)`**: appends an `Artifact` at the current stage/day and logs it.
- **`record_human_approval(engagement, overridden)`**: increments the approval/override counters that `metrics.py::override_rate()` reads.
- **`record_eval_score(engagement, score)`**: stores a score keyed by the current stage's label.
- **`check_escalation_triggers(engagement, settings=SETTINGS)`**: the automatic version of §5.4's "start day 1, escalate day 3" — raises an escalation if `data_access_granted` is still pending once `engagement.day >= settings.data_access_escalation_day`, and only once.
- **`escalate(engagement, reason)` / `resolve_escalation(engagement, reason_prefix)`**: raise/resolve an `Escalation`, logged either way.

## accelerators.py

The reusable accelerator library (§5.3) and the reuse-vs-build decision every stage makes.

- **`LIBRARY`**: ten seeded `AcceleratorAsset`s across all five kinds named in the prep guide — connectors, prompt templates, an eval harness, guardrail policies, dashboard templates.
- **`pull_or_build(engagement, kind, name)`**: looks up `(kind, name)` in `LIBRARY`; records a `Pull` with `reused=True` if found, `reused=False` (custom-built) otherwise. Always logged, whichever branch.

## metrics.py

Turns the four metrics named in §5.4 (plus accelerator reuse) from a claim into a number — the
counterpart to `evaluation/harness.py` in the RAG project.

- **`time_to_first_value(engagement)`**: earliest `produced_on_day` across all artifacts, or `None` if nothing has shipped yet.
- **`eval_score_at_handover(engagement)`**: the score recorded during the `EVALUATE` stage.
- **`override_rate(engagement)`**: overrides ÷ total human-approval checkpoints, or `None` before any have happened.
- **`week4_retention(engagement)`**: `None` until explicitly recorded — deliberately not a fake `0.0` that looks like a real measurement before week 4 has actually occurred.
- **`accelerator_reuse_rate(engagement)`**: reused pulls ÷ total pulls — the numeric answer to "productised or bespoke?"
- **`gates_passed_ratio(engagement)`**: fraction of the six gate definitions currently `PASSED`.
- **`summary(engagement)`**: a single dict of everything above, plus stage/day/deployed/open-escalation-count — what the demo script prints at the end of a run.

## observability.py

Renders and persists the event log every other module writes to via `Engagement.log()` — the
counterpart to `observability/trace.py::RunTrace`.

- **`render_timeline(engagement)`**: a human-readable, chronological render of every event — gate sign-offs (pass/deny + rule), stage-advance attempts, escalations, accelerator pulls (reused vs. custom), artifacts, eval scores, human approvals, deploy attempts.
- **`write(engagement, settings=SETTINGS)`**: persists the engagement's stage/day/deployed status and full event list as JSON under `runs/`, named after the customer and day.

## config.py

- **`Settings`**: `data_dir`, `runs_dir`, `data_access_escalation_day` (default 3, per §5.4), and the two intake-strictness flags (`require_measurable_metrics`, `require_customer_sme`).

---

## See also

- `01-theory.md` — the concepts
- `02-architecture-end-to-end.md` — the pipeline, diagrammed
- `04-system-design-coverage-map.md` — checked against the prep doc
