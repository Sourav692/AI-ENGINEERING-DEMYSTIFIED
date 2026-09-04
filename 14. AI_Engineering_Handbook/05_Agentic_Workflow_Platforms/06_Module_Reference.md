# Module Reference — `src/agent_platform`

> **Level** 🟡 Building Production Systems · **Module** 05 · **Doc** 6 of 7 · **Time** reference — use as needed
> **Prerequisites:** docs 1–5 of this module
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise Agentic Workflow Automation Platform/docs/03-src-modules-reference.md`; `docs/02-architecture-end-to-end.md` §4
> **Code:** `project/src/agent_platform/`

## The package in one paragraph

No LLM calls anywhere — the "agent reasoning" loop is a fixed, deterministic step sequence, so the whole test suite runs in well under a second. `models.py` defines the domain (`Decision` is the same shape used across all three source projects); `channels.py` normalises input; `routing.py` matches and de-conflicts; `tools.py` validates arguments; `workflows.py` versions and promotes; `guardrails.py` is the per-step decision engine; `orchestrator.py` is the durable execution loop everything plugs into; `observability.py` renders and persists what the orchestrator already logged.

## `models.py` — the domain

| Symbol | Purpose |
|---|---|
| `Channel` | Enum of the five channels |
| `Event` | The canonical event: `channel`, `event_type`, `tenant_id`, `target_entity_id`, `payload`, `raw_ref` |
| `WorkflowStatus`, `STATUS_ORDER` | The five rollout stages, in order |
| `ToolDefinition` | `name`, `schema` (param → type), `required`, `destructive`, `scopes` |
| `Trigger` | `channel`, `event_type`, `priority` |
| `Step` | `name`, `tool`, `args_template` — `{field}` values resolved from the event at execution |
| `WorkflowSpec` | `workflow_id`, `version`, `status`, `triggers`, `steps`, `max_steps`, `max_cost_usd` |
| `Decision` | `allowed`, `rule`, `reason` — every decision point returns this |
| `RunStep` | One executed step: args, idempotency key, whether the side effect actually applied |
| `RunState` | `RUNNING` / `PAUSED_FOR_APPROVAL` / `COMPLETED` / `HALTED_BUDGET` / `CRASHED` |
| `Run` | `next_step_index` (the checkpoint), `completed_steps`, `total_cost_usd`, `events`. `Run.log(event_kind, **fields)` appends an event with reserved keys set last so a caller-supplied field cannot clobber them |
| `Principal` | `user_id`, `display_name`, `role` (`author` / `approver` / `admin`) |

## `identity.py`

| Symbol | Purpose |
|---|---|
| `get_principal(user_id)`, `list_principals()` | Role lookup. Includes `u_author_wrong_hat` — a negative control proving an author cannot approve their own work however the request is framed |

## `channels.py` — Layer 1

| Symbol | Purpose |
|---|---|
| `from_webhook(payload)` | Zendesk-shaped payload → `Event` |
| `from_slack(payload)` | Slack event → `Event`; classifies `urgent_message` vs `message` from the raw flag |
| `from_email(payload)` | Email → `Event` |

## `routing.py`

| Symbol | Purpose |
|---|---|
| `matching_workflows(event, workflows)` | Every workflow whose tenant, status (not `DRAFT`) and trigger match |
| `route(event, workflows)`, `selected_workflow(...)` | The single highest-priority match, or a named reason (`no_trigger_match`, `entity_locked`) |
| `acquire_lock(target_entity_id, run_id)`, `release_lock(target_entity_id)` | The exclusivity lock — at most one active run per target, independent of priority |

## `tools.py`

| Symbol | Purpose |
|---|---|
| `REGISTRY` | Four typed tools — `draft_reply`, `issue_refund`, `close_ticket`, `tag_ticket` — two destructive, two not |
| `get_tool(name)` | Lookup; raises on unknown |
| `validate_args(tool, args)` | Every required field present, every type matches — denies before any execution |

## `workflows.py`

| Symbol | Purpose |
|---|---|
| `WorkflowStore` | In-memory version history per `workflow_id`: `publish()`, `latest()`, `get_version()`, `all_live()` |
| `promote(store, workflow_id, to_status, signer)` | Advances exactly one stage; denies `wrong_role` and `cannot_skip_stage` |

## `guardrails.py` — Layer 3

| Symbol | Purpose |
|---|---|
| `GuardrailPolicy` | Per-tenant `spend_cap_usd`, `max_steps`, `allowed_destructive_tools_autonomous` |
| `authorize_step(workflow, run, step, tool, step_cost_usd, policy, approval=None)` | The five ordered rules — step budget, spend cap (tighter of workflow and tenant), non-destructive pass-through, shadow block, below-`LIVE` block — then autonomous allow-list match or role-checked human approval |

## `orchestrator.py` — Layer 2

| Symbol | Purpose |
|---|---|
| `run_workflow(run_id, workflow, event, policy, approval=None, crash_after_step=None)` | Acquires the entity lock; executes from step 0 |
| `resume(run, workflow, policy, approval=None, crash_after_step=None)` | Continues a `CRASHED`/`PAUSED` run from its checkpoint — never from 0 |
| `_continue(...)` | The one loop: resolve args; if the step's idempotency key was already applied, record a zero-cost, zero-authorisation no-op and move on; otherwise validate, authorise, apply, checkpoint, repeat |
| `_apply_side_effect(idempotency_key, tool_name, args)` | `True` only the first time a key is seen |
| `_step_cost(tool_name, args)` | `issue_refund` → the actual `amount_usd`; every other tool → a small fixed operational cost |
| `external_call_count(tool_name)` | How many times a tool's side effect actually applied — for idempotency assertions |

Two bugs fixed here, both worth telling: the spend cap originally checked a hardcoded $0.00 instead of the refund amount; and an idempotent replay originally skipped the side effect but still re-entered authorisation and cost accounting, so a retried, already-approved refund could trip the cap. The replay check now runs before both.

## `observability.py`

| Symbol | Purpose |
|---|---|
| `render_run(run)` | Chronological human-readable render of every authorise/execute/reject event, plus crash and lock-denial markers |
| `write(run, settings)` | Persists state, cost and the full event list as JSON under `runs/` |

## `config.py`

| Symbol | Purpose |
|---|---|
| `Settings`, `SETTINGS` | `data_dir`, `runs_dir`, `default_spend_cap_usd`, `default_max_steps` |

## Scripts and tests

| Path | Purpose |
|---|---|
| `scripts/run_workflow_demo.py` | The happy path: staged rollout, routing conflict, approval, idempotent retry, crash and resume |
| `scripts/demo_guardrail_failure.py` | The negative-control demo — seven denials |
| `scripts/_scenario.py` | The Cascade Robotics scenario (`data/case_study.json`) |
| `tests/test_platform.py` | 21 deterministic tests, no API calls |

**Next →** [Coverage Map](07_Coverage_Map.md)
