# Module Reference — `src/delivery_framework`

> **Level** 🔴 The FDE Role · **Module** 10 · **Doc** 6 of 7 · **Time** reference — use as needed
> **Prerequisites:** docs 3–4 of this module
> **Source material:** `4. FDE_Related_Preparation/Delivery Framework from Scoping to Delivery/docs/03-src-modules-reference.md`; `docs/02-architecture-end-to-end.md` §4
> **Code:** `project/src/delivery_framework/`

## The package in one paragraph

No LLM calls anywhere — every gate decision is deterministic, so the whole suite runs in well under a second. `models.py` defines the domain; `identity.py` and `gates.py` are the ABAC-shaped authority layer; `pipeline.py` is the intake refusal gate; `engine.py` is the state machine; `accelerators.py` and `metrics.py` are the reuse and measurement layer; `observability.py` renders and persists the event log that every module writes to via `Engagement.log()`.

## `models.py` — the domain

| Symbol | Purpose |
|---|---|
| `Stage`, `STAGE_ORDER` | The seven ordered stages, each with a day range and label; `.order` gives position |
| `GateStatus` | `PENDING` / `PASSED` / `FAILED` |
| `Decision` | `allowed`, `rule`, `reason` — the same shape as Module 04's `authz.policy.Decision` |
| `Gate` | A named blocking condition: `required_before` (a `Stage`), `allowed_roles`, `status`, and once passed `evidence` / `signed_by` / `signed_on_day` |
| `Artifact` | Something a stage produced: `name`, `stage`, `produced_on_day`, `owner` |
| `AcceleratorAsset` | One library entry: `name`, `kind`, `description` |
| `Pull` | A record of one stage reusing an asset or building custom; `reused` is what the reuse-rate metric reads |
| `Escalation` | `reason`, `raised_on_day`, `resolved`, `resolved_on_day` |
| `Principal` | `user_id`, `display_name`, `role` (fda / security_reviewer / customer_sme / sponsor) |
| `Engagement` | The one mutable object per customer: stage, day, gates, artifacts, pulls, escalations, events, deployed flag, approval counters, eval scores, retention |
| `Engagement.log(event_kind, **fields)` | Appends an event. Reserved keys (`day`, `stage`, `kind`) are set *last* so a caller's field can never clobber them — a real bug hit when an accelerator's `kind` collided with the event's `kind` |

## `identity.py`

| Symbol | Purpose |
|---|---|
| `get_principal(user_id)`, `list_principals()` | Four roles resolved by lookup, never assumed from context. Includes `u_fda_wrong_hat` — the right person with the wrong role, proving role-checking is not decorative |

## `gates.py` — the authority layer

| Symbol | Purpose |
|---|---|
| `GATE_DEFINITIONS` | The six gates, each with its blocking stage and allowed roles |
| `gates_for_stage(stage)` | Every gate that blocks entry to `stage` |
| `sign_off(engagement, gate_name, signer, evidence)` | The decision function. Three ordered deny rules — `wrong_role`, `no_evidence`, `prior_gate_incomplete` — then an allow that records signer, evidence and day. Every attempt logged |
| `_earlier_unpassed_gates(engagement, before_stage)` | Enforces sign-off ordering |
| `blocking_gates(engagement, target_stage)` | What `advance_stage()` checks before a transition |

## `pipeline.py` — intake refusal

| Symbol | Purpose |
|---|---|
| `ScopingRefused` | Raised when a request cannot be started at all |
| `intake(customer_name, success_metrics, data_sources, customer_sme)` | Refuses on empty metrics, no SME, or no data sources; otherwise returns a fresh `Engagement` at `Stage.SCOPING`, day 1 |

## `engine.py` — the state machine

| Symbol | Purpose |
|---|---|
| `advance_stage(engagement, to_day=None)` | Moves to `STAGE_ORDER[current + 1]` only. **There is no code path that jumps further** — "skip a stage" is not callable. Blocked with a named reason if any gate before the next stage is unpassed |
| `mark_deployed(engagement)` | The terminal transition; legal only from `GO_NO_GO` with `success_metrics_met` passed |
| `record_artifact`, `record_human_approval(overridden)`, `record_eval_score` | Feed the metrics |
| `check_escalation_triggers(engagement)` | Raises an escalation if `data_access_granted` is still pending once `day >= data_access_escalation_day` (3) — once only |
| `escalate`, `resolve_escalation` | Logged either way |

## `accelerators.py` — the library

| Symbol | Purpose |
|---|---|
| `LIBRARY` | Ten seeded assets across all five kinds: connectors, prompt templates, an eval harness, guardrail policies, dashboard templates |
| `pull_or_build(engagement, kind, name)` | Looks up `(kind, name)`; records a `Pull` with `reused=True` if found, `False` if custom-built. Always logged |

## `metrics.py` — claims into numbers

| Symbol | Purpose |
|---|---|
| `time_to_first_value(engagement)` | Earliest `produced_on_day` across artifacts, or `None` |
| `eval_score_at_handover(engagement)` | The score recorded during `EVALUATE` |
| `override_rate(engagement)` | Overrides ÷ approval checkpoints, or `None` before any |
| `week4_retention(engagement)` | `None` until explicitly recorded — never a fake `0.0` |
| `accelerator_reuse_rate(engagement)` | Reused ÷ total pulls |
| `gates_passed_ratio(engagement)` | Passed ÷ six |
| `summary(engagement)` | Everything above plus stage, day, deployed, open escalations |

## `observability.py`

| Symbol | Purpose |
|---|---|
| `render_timeline(engagement)` | Chronological render of every event: sign-offs (pass/deny + rule), stage attempts, escalations, pulls, artifacts, scores, approvals, deploy attempts |
| `write(engagement)` | Persists stage, day, deployed and the full event list as JSON under `runs/`, named by customer and day |

## `config.py`

| Symbol | Purpose |
|---|---|
| `Settings`, `SETTINGS` | `data_dir`, `runs_dir`, `data_access_escalation_day` (3), `require_measurable_metrics`, `require_customer_sme` |

## Scripts and tests

| Path | Purpose |
|---|---|
| `scripts/run_engagement_demo.py` | Northwind Logistics — all 14 days, every gate in order |
| `scripts/demo_gate_failure.py` | The negative-control demo |
| `data/case_study.json` | The Northwind scenario |
| `tests/test_gates.py` | 17 deterministic tests |

**Next →** [Coverage Map](07_Coverage_Map.md)
