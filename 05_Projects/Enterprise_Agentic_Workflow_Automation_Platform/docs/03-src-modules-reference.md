# Source Modules Reference — `src/agent_platform`

**What this is:** every module and function, 2-3 lines each — same purpose as the equivalent doc in
the other two projects.

**Overview:** no LLM calls anywhere — the "agent reasoning" loop is a fixed, deterministic step
sequence (the honest gap is named in `docs/04`), so the whole test suite runs in well under a
second. `models.py` defines the domain (`Decision` is the same shape used across all three
projects); `channels.py` normalises input; `routing.py` matches and de-conflicts; `tools.py`
validates arguments; `workflows.py` versions and promotes; `guardrails.py` is the per-step decision
engine; `orchestrator.py` is the durable execution loop everything else plugs into;
`observability.py` renders and persists what the orchestrator already logged.

---

## models.py

- **`Channel`** (enum): the five named channels.
- **`Event`**: the canonical, channel-agnostic event — `channel`, `event_type`, `tenant_id`, `target_entity_id`, `payload`, `raw_ref`.
- **`WorkflowStatus`** (enum) / **`STATUS_ORDER`**: the five staged-rollout statuses, in order.
- **`ToolDefinition`**: `name`, `schema` (param → type), `required`, `destructive`, `scopes`.
- **`Trigger`**: `channel`, `event_type`, `priority` — what a workflow fires on, and how it ranks in a conflict.
- **`Step`**: `name`, `tool`, `args_template` — a declarative step; `{field}` values are resolved from the event at execution time.
- **`WorkflowSpec`**: `workflow_id`, `version`, `status`, `triggers`, `steps`, `max_steps`, `max_cost_usd`.
- **`Decision`**: `allowed`, `rule`, `reason` — the same shape used by every decision point in this project and the other two in the series.
- **`RunStep`**: one executed step's record — args, idempotency key, whether its side effect actually applied.
- **`RunState`** (enum): `RUNNING` / `PAUSED_FOR_APPROVAL` / `COMPLETED` / `HALTED_BUDGET` / `CRASHED`.
- **`Run`**: one execution — `next_step_index` (the checkpoint), `completed_steps`, `total_cost_usd`, `events`.
- **`Run.log(event_kind, **fields)`**: appends one event; reserved keys are set last so a caller-supplied field can't clobber them (a real bug in the delivery-framework project fixed the same way, replicated here proactively).
- **`Principal`**: `user_id`, `display_name`, `role` (`author` / `approver` / `admin`).

## identity.py

- **`get_principal(user_id)`** / **`list_principals()`**: role lookup, including `u_author_wrong_hat` — a negative control proving an author cannot approve their own work regardless of how the request is framed.

## channels.py

- **`from_webhook(payload)`**: a Zendesk-shaped payload → `Event`.
- **`from_slack(payload)`**: a Slack event payload → `Event`; also classifies `urgent_message` vs. plain `message` from the raw flag.
- **`from_email(payload)`**: an email payload → `Event`.

## routing.py

- **`matching_workflows(event, workflows)`**: every workflow whose tenant, status (not `DRAFT`), and trigger match the event.
- **`route(event, workflows)`** / **`selected_workflow(event, workflows)`**: pick the single highest-priority match, or explain why none ran (`no_trigger_match`, `entity_locked`).
- **`acquire_lock(target_entity_id, run_id)`** / **`release_lock(target_entity_id)`**: the exclusivity lock — a target entity can have at most one active run, independent of priority.

## tools.py

- **`REGISTRY`**: four typed tools — `draft_reply`, `issue_refund`, `close_ticket`, `tag_ticket` — two destructive, two not.
- **`get_tool(name)`**: lookup, raises on an unknown tool.
- **`validate_args(tool, args)`**: checks every required field is present and every field's type matches the tool's declared schema — denies before any execution is attempted.

## workflows.py

- **`WorkflowStore`**: in-memory version history per `workflow_id`; `publish()`, `latest()`, `get_version()`, `all_live()` (every workflow's current latest version for a tenant, used by routing).
- **`promote(store, workflow_id, to_status, signer)`**: advances exactly one rollout stage — denies `wrong_role` (author/approver-only, never self-promotion by the author who isn't also an approver/admin) and `cannot_skip_stage`.

## guardrails.py

- **`GuardrailPolicy`**: per-tenant `spend_cap_usd`, `max_steps`, `allowed_destructive_tools_autonomous`.
- **`authorize_step(workflow, run, step, tool, step_cost_usd, policy, approval=None)`**: the per-step decision engine, five ordered rules — step-budget, spend-cap (using the *tighter* of the workflow's own cap and the tenant policy's), non-destructive pass-through, shadow-mode block, below-`LIVE` block, then either an autonomous allow-list match or a role-checked human approval.

## orchestrator.py

- **`run_workflow(run_id, workflow, event, policy, approval=None, crash_after_step=None)`**: acquires the entity lock, then executes from step 0.
- **`resume(run, workflow, policy, approval=None, crash_after_step=None)`**: continues a `CRASHED`/`PAUSED` run from its checkpoint — never from step 0.
- **`_continue(...)`**: the actual loop — resolve args; if a destructive step's idempotency key was already applied, record a zero-cost, zero-authorization no-op replay and move straight to the next step; otherwise validate, authorize, apply the tool's effect, checkpoint, repeat.
- **`_apply_side_effect(idempotency_key, tool_name, args)`**: returns `True` only the first time a given key is seen; every subsequent call with the same key is a no-op, proven by `external_call_count()` not incrementing.
- **`_step_cost(tool_name, args)`**: what counts against the spend cap — for `issue_refund` this is the *actual dollar amount* (`args["amount_usd"]`), not a nominal per-call fee; every other tool uses a small fixed operational cost. Conflating these two was a real bug caught while building this project — a refund of any size was passing an intentionally tiny cap because the cap check was only ever looking at a hardcoded $0.00.

**A second, subtler bug this project hit and fixed:** the first version of `_continue()` let an idempotent replay skip the *side effect* but still ran it through `authorize_step()` and still added `_step_cost()` to `run.total_cost_usd` again. A legitimately-approved run whose already-completed refund step was retried (a redelivered event, a rewound checkpoint) could be pushed into `spend_cap_exceeded` on the retry — even though no money moved a second time in the real world, because nothing about the outside world had actually changed. The fix moves the idempotency check *before* authorization: a replay of an already-applied key is recorded as a free, pre-authorized no-op and never re-enters `authorize_step()` or the cost accumulator at all. The lesson worth stating in an interview: **idempotency has to cover every side effect of a step, not just its most obvious one** — cost accounting is a side effect too, and forgetting that made a correct-looking idempotency guarantee false under retry.
- **`external_call_count(tool_name)`**: how many times a tool's side effect actually applied, for idempotency assertions.

## observability.py

- **`render_run(run)`**: a human-readable, chronological render of every step's authorize/execute/reject event, plus crash and lock-denial markers.
- **`write(run, settings=SETTINGS)`**: persists a run's state, cost, and full event list as JSON under `runs/`.

## config.py

- **`Settings`**: `data_dir`, `runs_dir`, `default_spend_cap_usd`, `default_max_steps`.

---

## See also

- `01-theory.md` — the concepts
- `02-architecture-end-to-end.md` — the pipeline, diagrammed
- `04-system-design-coverage-map.md` — checked against the prep doc
