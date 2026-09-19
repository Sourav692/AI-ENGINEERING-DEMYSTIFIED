# -*- coding: utf-8 -*-
"""Guardrail/orchestration tests - the properties that must hold on every run,
same role as test_gates.py in the delivery framework and test_pipeline.py in
the RAG project. No LLM anywhere in this project, so these are fast and
deterministic.
"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

from agent_platform import channels, orchestrator, routing
from agent_platform.guardrails import GuardrailPolicy, authorize_step
from agent_platform.identity import get_principal
from agent_platform.models import Channel, Step, Trigger, WorkflowSpec, WorkflowStatus
from agent_platform.tools import get_tool, validate_args
from agent_platform.workflows import WorkflowStore, promote

TENANT = "test_tenant"
AUTHOR = get_principal("u_author_dana")
WRONG_HAT = get_principal("u_author_wrong_hat")
APPROVER = get_principal("u_approver_raj")
ADMIN = get_principal("u_admin_lee")


def make_workflow(status=WorkflowStatus.DRAFT, priority=10, event_type="ticket.created",
                  max_steps=10, max_cost_usd=1000.0, steps=None):
    return WorkflowSpec(
        workflow_id="wf_test", tenant_id=TENANT, name="Test workflow", version=1, status=status,
        triggers=[Trigger(channel=Channel.WEBHOOK, event_type=event_type, priority=priority)],
        steps=steps or [
            Step(name="draft", tool="draft_reply", args_template={"ticket_id": "{ticket_id}", "body": "hi"}),
            Step(name="refund", tool="issue_refund",
                args_template={"order_id": "{order_id}", "amount_usd": "{refund_amount_usd}"}),
        ],
        max_steps=max_steps, max_cost_usd=max_cost_usd,
    )


def make_event(ticket_id="TCK-1", order_id="ORD-1", refund_amount_usd=10.0, event_type="ticket.created"):
    return channels.from_webhook({
        "type": event_type, "id": "wh_1", "tenant_id": TENANT, "ticket_id": ticket_id,
        "order_id": order_id, "refund_amount_usd": refund_amount_usd,
    })


def default_policy(**overrides):
    base = dict(tenant_id=TENANT, spend_cap_usd=50.0, max_steps=10,
               allowed_destructive_tools_autonomous=[])
    base.update(overrides)
    return GuardrailPolicy(**base)


# ===========================================================================
# Channel adapters
# ===========================================================================
def test_webhook_adapter_produces_canonical_event():
    ev = make_event()
    assert ev.channel == Channel.WEBHOOK
    assert ev.tenant_id == TENANT
    assert ev.target_entity_id == "TCK-1"


def test_slack_adapter_marks_urgent_messages():
    ev = channels.from_slack({"team_id": TENANT, "ts": "123.45", "text": "prod is down",
                              "is_urgent": True, "channel_name": "support-escalations"})
    assert ev.event_type == "urgent_message"
    assert ev.channel == Channel.SLACK


# ===========================================================================
# Tool argument validation
# ===========================================================================
def test_missing_required_arg_is_denied():
    tool = get_tool("issue_refund")
    d = validate_args(tool, {"order_id": "ORD-1"})
    assert d.denied
    assert d.rule == "missing_required_args"


def test_wrong_type_arg_is_denied():
    tool = get_tool("issue_refund")
    d = validate_args(tool, {"order_id": "ORD-1", "amount_usd": "fifty"})
    assert d.denied
    assert d.rule == "type_mismatch"


def test_valid_args_pass():
    tool = get_tool("issue_refund")
    d = validate_args(tool, {"order_id": "ORD-1", "amount_usd": 12.5})
    assert d.allowed


# ===========================================================================
# Staged rollout / promotion
# ===========================================================================
def test_author_cannot_promote_own_workflow():
    store = WorkflowStore()
    store.publish(make_workflow())
    d = promote(store, "wf_test", WorkflowStatus.TESTING, WRONG_HAT)
    assert d.denied
    assert d.rule == "wrong_role"


def test_cannot_skip_a_rollout_stage():
    store = WorkflowStore()
    store.publish(make_workflow())
    d = promote(store, "wf_test", WorkflowStatus.AUTONOMOUS, ADMIN)
    assert d.denied
    assert d.rule == "cannot_skip_stage"


def test_promotion_advances_one_stage_at_a_time():
    store = WorkflowStore()
    store.publish(make_workflow())
    d = promote(store, "wf_test", WorkflowStatus.TESTING, ADMIN)
    assert d.allowed
    assert store.latest("wf_test").status == WorkflowStatus.TESTING


# ===========================================================================
# Routing / conflict resolution
# ===========================================================================
def test_higher_priority_workflow_wins_a_same_trigger_conflict():
    high = make_workflow(status=WorkflowStatus.LIVE, priority=10)
    high.workflow_id = "wf_high"
    low = make_workflow(status=WorkflowStatus.LIVE, priority=1)
    low.workflow_id = "wf_low"
    winner = routing.selected_workflow(make_event(), [high, low])
    assert winner.workflow_id == "wf_high"


def test_draft_workflows_never_match_real_events():
    draft = make_workflow(status=WorkflowStatus.DRAFT, priority=10)
    assert routing.matching_workflows(make_event(), [draft]) == []


def test_entity_lock_blocks_a_second_concurrent_run():
    assert routing.acquire_lock("TCK-locked", "run_a") is True
    assert routing.acquire_lock("TCK-locked", "run_b") is False
    routing.release_lock("TCK-locked")
    assert routing.acquire_lock("TCK-locked", "run_c") is True
    routing.release_lock("TCK-locked")


# ===========================================================================
# Guardrails
# ===========================================================================
def test_destructive_step_blocked_below_live():
    wf = make_workflow(status=WorkflowStatus.TESTING)
    tool = get_tool("issue_refund")
    run = orchestrator.Run(run_id="r1", workflow_id=wf.workflow_id, workflow_version=1, event=make_event())
    d = authorize_step(wf, run, wf.steps[1], tool, 0.0, default_policy())
    assert d.denied
    assert d.rule == "not_live"


def test_destructive_step_never_executes_in_shadow():
    wf = make_workflow(status=WorkflowStatus.SHADOW)
    tool = get_tool("issue_refund")
    run = orchestrator.Run(run_id="r1", workflow_id=wf.workflow_id, workflow_version=1, event=make_event())
    d = authorize_step(wf, run, wf.steps[1], tool, 0.0, default_policy())
    assert d.denied
    assert d.rule == "shadow_mode"


def test_destructive_step_on_live_needs_human_approval():
    wf = make_workflow(status=WorkflowStatus.LIVE)
    tool = get_tool("issue_refund")
    run = orchestrator.Run(run_id="r1", workflow_id=wf.workflow_id, workflow_version=1, event=make_event())
    d = authorize_step(wf, run, wf.steps[1], tool, 0.0, default_policy())
    assert d.denied
    assert d.rule == "needs_human_approval"


def test_destructive_step_on_live_passes_with_approver():
    wf = make_workflow(status=WorkflowStatus.LIVE)
    tool = get_tool("issue_refund")
    run = orchestrator.Run(run_id="r1", workflow_id=wf.workflow_id, workflow_version=1, event=make_event())
    d = authorize_step(wf, run, wf.steps[1], tool, 0.0, default_policy(), approval=APPROVER)
    assert d.allowed


def test_autonomous_still_needs_approval_unless_allowlisted():
    wf = make_workflow(status=WorkflowStatus.AUTONOMOUS)
    tool = get_tool("issue_refund")
    run = orchestrator.Run(run_id="r1", workflow_id=wf.workflow_id, workflow_version=1, event=make_event())
    d = authorize_step(wf, run, wf.steps[1], tool, 0.0, default_policy())   # not allow-listed
    assert d.denied
    assert d.rule == "needs_human_approval"

    d2 = authorize_step(wf, run, wf.steps[1], tool, 0.0,
                        default_policy(allowed_destructive_tools_autonomous=["issue_refund"]))
    assert d2.allowed
    assert d2.rule == "autonomous_allowlisted"


def test_spend_cap_is_refused_not_clamped():
    wf = make_workflow(status=WorkflowStatus.LIVE, max_cost_usd=1000)
    tool = get_tool("issue_refund")
    run = orchestrator.Run(run_id="r1", workflow_id=wf.workflow_id, workflow_version=1, event=make_event())
    d = authorize_step(wf, run, wf.steps[1], tool, 999.0, default_policy(spend_cap_usd=50.0),
                       approval=APPROVER)
    assert d.denied
    assert d.rule == "spend_cap_exceeded"


def test_step_budget_uses_the_tighter_of_workflow_and_policy():
    wf = make_workflow(status=WorkflowStatus.LIVE, max_steps=2)
    tool = get_tool("draft_reply")
    run = orchestrator.Run(run_id="r1", workflow_id=wf.workflow_id, workflow_version=1, event=make_event())
    run.completed_steps = [None, None]   # 2 already "completed"
    d = authorize_step(wf, run, wf.steps[0], tool, 0.0, default_policy(max_steps=10))
    assert d.denied
    assert d.rule == "step_budget_exceeded"


# ===========================================================================
# Idempotency and durability (through the real orchestrator)
# ===========================================================================
def test_retrying_a_destructive_step_never_double_applies():
    wf = make_workflow(status=WorkflowStatus.LIVE)
    event = make_event(ticket_id="TCK-idem")
    policy = default_policy()
    run = orchestrator.run_workflow("run_idem", wf, event, policy, approval=APPROVER)
    assert run.state.value == "completed"
    before = orchestrator.external_call_count("issue_refund")

    run.next_step_index = 1   # rewind to retry the refund step
    run = orchestrator.resume(run, wf, policy, approval=APPROVER)
    after = orchestrator.external_call_count("issue_refund")
    assert after == before   # no second real call
    assert run.completed_steps[-1].side_effect_applied is False


def test_crash_then_resume_continues_from_checkpoint_not_from_zero():
    wf = make_workflow(status=WorkflowStatus.LIVE)
    event = make_event(ticket_id="TCK-crash")
    policy = default_policy()

    run = orchestrator.run_workflow("run_crash", wf, event, policy, crash_after_step=0)
    assert run.state.value == "crashed"
    assert run.next_step_index == 1
    draft_calls_before_resume = sum(1 for e in run.events if e["kind"] == "step_executed" and e["step"] == "draft")
    assert draft_calls_before_resume == 1

    run = orchestrator.resume(run, wf, policy, approval=APPROVER)
    assert run.state.value == "completed"
    draft_calls_total = sum(1 for e in run.events if e["kind"] == "step_executed" and e["step"] == "draft")
    assert draft_calls_total == 1   # step 0 never ran a second time


def test_lock_is_released_once_a_run_finishes_or_halts():
    wf = make_workflow(status=WorkflowStatus.LIVE)
    event = make_event(ticket_id="TCK-lockrelease")
    policy = default_policy()
    orchestrator.run_workflow("run_lockrelease", wf, event, policy, approval=APPROVER)
    # If the lock were still held, a second run against the same entity would fail.
    assert routing.acquire_lock("TCK-lockrelease", "probe") is True
    routing.release_lock("TCK-lockrelease")
