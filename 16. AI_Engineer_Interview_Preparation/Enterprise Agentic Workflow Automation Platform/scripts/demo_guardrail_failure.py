# -*- coding: utf-8 -*-
"""The negative-control demo: prove every guardrail actually blocks, the same
role as demo_gate_failure.py in the delivery framework and
demo_access_control.py in the RAG project.

Usage:
    python scripts/demo_guardrail_failure.py
"""
import sys

import _bootstrap  # noqa: F401
from _scenario import TENANT, build_store, default_policy

from agent_platform import channels, orchestrator, routing
from agent_platform.identity import get_principal
from agent_platform.models import WorkflowStatus
from agent_platform.tools import get_tool, validate_args
from agent_platform.workflows import promote

RULE = "=" * 100


def main():
    store = build_store()
    policy = default_policy()
    author = get_principal("u_author_dana")
    wrong_hat = get_principal("u_author_wrong_hat")
    approver = get_principal("u_approver_raj")
    admin = get_principal("u_admin_lee")

    print(RULE)
    print("1. WRONG ROLE - an author cannot promote their own workflow")
    print(RULE)
    d = promote(store, "wf_ticket_triage", WorkflowStatus.TESTING, wrong_hat)
    print(f"{'OK' if d.allowed else 'DENY'} [{d.rule}] {d.reason}")

    print(RULE)
    print("2. CANNOT SKIP A STAGE - draft straight to autonomous")
    print(RULE)
    d = promote(store, "wf_ticket_triage", WorkflowStatus.AUTONOMOUS, admin)
    print(f"{'OK' if d.allowed else 'DENY'} [{d.rule}] {d.reason}")

    print(RULE)
    print("3. MALFORMED TOOL ARGS - rejected before execution, never reaches the tool")
    print(RULE)
    tool = get_tool("issue_refund")
    d = validate_args(tool, {"order_id": "ORD-1", "amount_usd": "fifty dollars"})   # wrong type
    print(f"{'OK' if d.allowed else 'DENY'} [{d.rule}] {d.reason}")
    d = validate_args(tool, {"order_id": "ORD-1"})   # missing required field
    print(f"{'OK' if d.allowed else 'DENY'} [{d.rule}] {d.reason}")

    print(RULE)
    print("4. DESTRUCTIVE STEP BELOW LIVE - a draft-status workflow's refund never fires")
    print(RULE)
    event = channels.from_webhook({
        "type": "ticket.created", "id": "wh_1", "tenant_id": TENANT,
        "ticket_id": "TCK-1", "order_id": "ORD-1", "refund_amount_usd": 20.0,
    })
    draft_wf = store.get_version("wf_ticket_triage", 1)   # still DRAFT - never promoted in this script
    run = orchestrator.run_workflow("run_bad_001", draft_wf, event, policy)
    print(f"run state = {run.state.value}")
    for ev in run.events:
        if ev["kind"] == "step_authorize":
            print(f"  [{ev['rule']}] {ev['reason']}")

    print(RULE)
    print("5. SPEND CAP - a refund that would exceed the tenant's cap is refused, not clamped")
    print(RULE)
    promote(store, "wf_ticket_triage", WorkflowStatus.TESTING, admin)
    promote(store, "wf_ticket_triage", WorkflowStatus.SHADOW, admin)
    promote(store, "wf_ticket_triage", WorkflowStatus.LIVE, admin)
    live_wf = store.get_version("wf_ticket_triage", 1)
    big_event = channels.from_webhook({
        "type": "ticket.created", "id": "wh_2", "tenant_id": TENANT,
        "ticket_id": "TCK-2", "order_id": "ORD-2", "refund_amount_usd": 500.0,
    })
    run = orchestrator.run_workflow("run_bad_002", live_wf, big_event, policy, approval=approver)
    print(f"run state = {run.state.value}")
    for ev in run.events:
        if ev["kind"] == "step_authorize":
            print(f"  [{ev['rule']}] {ev['reason']}")

    print(RULE)
    print("6. STEP BUDGET - a misconfigured self-triggering workflow halts, it doesn't loop forever")
    print(RULE)
    runaway = store.get_version("wf_runaway", 1)
    tight_policy = default_policy()
    event3 = channels.from_webhook({
        "type": "ticket.updated", "id": "wh_3", "tenant_id": TENANT, "ticket_id": "TCK-3",
    })
    run = orchestrator.run_workflow("run_runaway_001", runaway, event3, tight_policy)
    print(f"run state = {run.state.value}  steps completed = {len(run.completed_steps)} "
         f"(workflow declared 30 steps, capped at 5)")

    print(RULE)
    print("7. ENTITY LOCK - a second workflow cannot start against a ticket that already has a run in flight")
    print(RULE)
    live_wf2 = store.get_version("wf_ticket_triage", 1)
    ticket_event = channels.from_webhook({
        "type": "ticket.created", "id": "wh_4", "tenant_id": TENANT,
        "ticket_id": "TCK-4", "order_id": "ORD-4", "refund_amount_usd": 5.0,
    })
    routing.acquire_lock(ticket_event.target_entity_id, "run_in_flight_999")   # simulate an in-flight run
    run = orchestrator.run_workflow("run_bad_003", live_wf2, ticket_event, policy)
    print(f"run state = {run.state.value}")
    for ev in run.events:
        if ev["kind"] == "lock_denied":
            print(f"  [lock_denied] target={ev['target']} already held")
    routing.release_lock(ticket_event.target_entity_id)

    return 0


if __name__ == "__main__":
    sys.exit(main())
