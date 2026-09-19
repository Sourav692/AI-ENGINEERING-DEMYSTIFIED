# -*- coding: utf-8 -*-
"""The orchestration engine (§3.2): durable, step-by-step execution with
checkpointing, retries, and resumability after a crash - and the agent runtime's
plan/select-tool/observe loop (§3.2), deliberately deterministic here rather
than calling a real LLM, the same choice `delivery_framework_platform` made to
keep every test fast, free, and exactly reproducible. The loop shape (plan one
step, validate its args, check the guardrail, execute, observe, continue) is
real; the "planner" is a fixed step list instead of a model choosing one
dynamically - the honest gap is named in docs/04.

Two properties this file exists to prove:
  1. DURABILITY - a crash mid-run does not restart the run. `run.next_step_index`
     is the checkpoint; resume() reads it, it never re-reads index 0.
  2. IDEMPOTENCY - retrying a destructive step never applies its side effect
     twice, even though the step itself is attempted twice.
"""
from __future__ import annotations

from typing import Dict, Optional

from . import routing, tools
from .guardrails import GuardrailPolicy, authorize_step
from .models import Event, Principal, Run, RunState, RunStep, Step, WorkflowSpec

# Simulates the external systems every destructive tool actually calls.
# Keyed by idempotency_key so a retried step can never double-apply.
_SIDE_EFFECTS: Dict[str, Dict] = {}
_EXTERNAL_CALL_COUNT: Dict[str, int] = {}  # tool_name -> real calls made, for the demo to prove no double-call


def _resolve_args(step: Step, event: Event) -> Dict:
    out = {}
    for k, v in step.args_template.items():
        if isinstance(v, str) and v.startswith("{") and v.endswith("}"):
            field = v[1:-1]
            out[k] = event.payload.get(field, event.target_entity_id if field == "target_entity_id" else None)
        else:
            out[k] = v
    return out


def _apply_side_effect(idempotency_key: str, tool_name: str, args: Dict) -> bool:
    """Returns True if this call actually applied the effect (first time),
    False if it was a no-op replay of an already-applied idempotency key."""
    if idempotency_key in _SIDE_EFFECTS:
        return False
    _SIDE_EFFECTS[idempotency_key] = {"tool": tool_name, "args": dict(args)}
    _EXTERNAL_CALL_COUNT[tool_name] = _EXTERNAL_CALL_COUNT.get(tool_name, 0) + 1
    return True


def external_call_count(tool_name: str) -> int:
    """How many times a destructive tool's side effect actually applied (not
    counting no-op idempotent replays) - what the idempotency demo checks."""
    return _EXTERNAL_CALL_COUNT.get(tool_name, 0)


_OPERATIONAL_COST = {"draft_reply": 0.02, "issue_refund": 0.0, "close_ticket": 0.0, "tag_ticket": 0.01}


def _step_cost(tool_name: str, args: Dict) -> float:
    """What counts against the spend cap. For a financial tool this is the real
    dollar amount the action would move (a $500 refund must cost $500 against
    the cap, not a nominal per-call fee) - conflating "cost to run this step"
    with "dollars this step spends on the customer's behalf" was a real bug
    caught while building this: a refund of any size passed a $5 cap because
    the cap was only ever checking a hardcoded $0.00 operational fee. For every
    other tool this is a small nominal cost, standing in for the LLM/API call
    cost of executing that step."""
    if tool_name == "issue_refund":
        return float(args.get("amount_usd", 0.0))
    return _OPERATIONAL_COST.get(tool_name, 0.05)


def run_workflow(run_id: str, workflow: WorkflowSpec, event: Event, policy: GuardrailPolicy,
                 approval: Optional[Principal] = None, crash_after_step: Optional[int] = None) -> Run:
    """Execute (or continue) a run from its current checkpoint. If
    `crash_after_step` matches the index of a step that just completed, the
    function returns immediately with state=CRASHED - simulating a process
    restart - without touching any step after it."""
    run = Run(run_id=run_id, workflow_id=workflow.workflow_id, workflow_version=workflow.version, event=event)
    if not routing.acquire_lock(event.target_entity_id, run_id):
        run.state = RunState.HALTED_BUDGET
        run.log("lock_denied", target=event.target_entity_id)
        return run
    result = _continue(run, workflow, policy, approval, crash_after_step)
    if result.state != RunState.RUNNING:
        routing.release_lock(event.target_entity_id)
    return result


def resume(run: Run, workflow: WorkflowSpec, policy: GuardrailPolicy,
          approval: Optional[Principal] = None, crash_after_step: Optional[int] = None) -> Run:
    """Continue a CRASHED or PAUSED run from its checkpoint - never from step 0."""
    run.state = RunState.RUNNING
    result = _continue(run, workflow, policy, approval, crash_after_step)
    if result.state != RunState.RUNNING:
        routing.release_lock(run.event.target_entity_id)
    return result


def _continue(run: Run, workflow: WorkflowSpec, policy: GuardrailPolicy,
             approval: Optional[Principal], crash_after_step: Optional[int]) -> Run:
    while run.next_step_index < len(workflow.steps):
        idx = run.next_step_index
        step = workflow.steps[idx]
        tool = tools.get_tool(step.tool)
        args = _resolve_args(step, run.event)
        idempotency_key = f"{run.run_id}:{step.name}"

        # An idempotent replay of an already-applied destructive step is not
        # re-validated, re-authorized, or re-costed - it already happened once,
        # for real, and was already paid for. Re-running the budget check here
        # would double-count a cost against the cap for money that didn't
        # actually move a second time - a real bug caught while building this:
        # a legitimately-approved, already-completed refund could be pushed
        # into "spend_cap_exceeded" purely by a redelivered/retried event,
        # nothing in the outside world having changed at all.
        if tool.destructive and idempotency_key in _SIDE_EFFECTS:
            run.completed_steps.append(RunStep(
                step_name=step.name, tool=tool.name, args=args, idempotency_key=idempotency_key,
                allowed=True, rule="idempotent_replay", reason="already applied; replay is a no-op",
                side_effect_applied=False, cost_usd=0.0))
            run.log("step_executed", step=step.name, tool=tool.name,
                   side_effect_applied=False, cost_usd=0.0)
            run.next_step_index += 1
            continue

        # PLAN -> SELECT TOOL -> the "agent loop," here a fixed plan (see module docstring).
        validity = tools.validate_args(tool, args)
        if validity.denied:
            run.log("step_rejected", step=step.name, rule=validity.rule, reason=validity.reason)
            run.state = RunState.HALTED_BUDGET
            return run

        cost = _step_cost(tool.name, args)
        auth = authorize_step(workflow, run, step, tool, cost, policy, approval)
        run.log("step_authorize", step=step.name, tool=tool.name, allowed=auth.allowed,
               rule=auth.rule, reason=auth.reason)

        if auth.denied:
            if auth.rule == "needs_human_approval":
                run.state = RunState.PAUSED_FOR_APPROVAL
            else:
                run.state = RunState.HALTED_BUDGET
            return run

        # EXECUTE + OBSERVE. A replay of an already-applied key is handled above
        # and never reaches here, so this is always a genuine first application.
        if tool.destructive:
            _apply_side_effect(idempotency_key, tool.name, args)
        run.completed_steps.append(RunStep(
            step_name=step.name, tool=tool.name, args=args, idempotency_key=idempotency_key,
            allowed=True, rule=auth.rule, reason=auth.reason,
            side_effect_applied=True, cost_usd=cost))
        run.total_cost_usd += cost
        run.log("step_executed", step=step.name, tool=tool.name,
               side_effect_applied=True, cost_usd=cost)

        run.next_step_index += 1   # THE CHECKPOINT

        if crash_after_step is not None and idx == crash_after_step:
            run.state = RunState.CRASHED
            run.log("simulated_crash", after_step=step.name)
            return run

    run.state = RunState.COMPLETED
    run.log("run_completed")
    return run
