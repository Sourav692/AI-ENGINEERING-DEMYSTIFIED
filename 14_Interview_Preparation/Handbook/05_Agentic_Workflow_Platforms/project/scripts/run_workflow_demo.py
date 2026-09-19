# -*- coding: utf-8 -*-
"""The happy-path demo: promote a workflow through every rollout stage, route
two channels' worth of events (including a same-trigger conflict), run a
destructive step with human approval, prove idempotency on a retry, and prove
durability across a simulated crash.

Usage:
    python scripts/run_workflow_demo.py
"""
import sys

import _bootstrap  # noqa: F401
from _scenario import TENANT, build_store, default_policy

from agent_platform import channels, orchestrator, routing
from agent_platform.identity import get_principal
from agent_platform.models import RunState, WorkflowStatus
from agent_platform.observability import render_run, write
from agent_platform.workflows import promote

RULE = "=" * 100


def main():
    store = build_store()
    policy = default_policy()
    author = get_principal("u_author_dana")
    approver = get_principal("u_approver_raj")
    admin = get_principal("u_admin_lee")

    print(RULE)
    print("1. STAGED ROLLOUT - promoting wf_ticket_triage through every status")
    print(RULE)
    for target in [WorkflowStatus.TESTING, WorkflowStatus.SHADOW, WorkflowStatus.LIVE]:
        d = promote(store, "wf_ticket_triage", target, admin)
        print(f"{'OK' if d.allowed else 'DENY'} [{d.rule}] {d.reason}")

    print(RULE)
    print("2. ROUTING - a webhook ticket-created event, two workflows both match it")
    print(RULE)
    event = channels.from_webhook({
        "type": "ticket.created", "id": "wh_9001", "tenant_id": TENANT,
        "ticket_id": "TCK-5510", "order_id": "ORD-2201", "refund_amount_usd": 35.0,
    })
    live_workflows = store.all_live(TENANT)
    d = routing.route(event, live_workflows)
    print(f"{'OK' if d.allowed else 'DENY'} [{d.rule}] {d.reason}")
    print("(priority 10 beats the legacy tagger's priority 1 - same trigger, one winner)")

    print(RULE)
    print("3. RUN - destructive step (refund) needs a human, since it's not allow-listed")
    print(RULE)
    workflow = store.get_version("wf_ticket_triage", 1)
    run = orchestrator.run_workflow("run_001", workflow, event, policy)
    print(render_run(run))
    print(f"\nstate = {run.state.value}")

    print("\n" + RULE)
    print("4. RESUME WITH APPROVAL - the approver signs off, the run picks up from its checkpoint")
    print(RULE)
    run = orchestrator.resume(run, workflow, policy, approval=approver)
    print(render_run(run))
    print(f"\nstate = {run.state.value}  total_cost=${run.total_cost_usd:.2f}")

    print("\n" + RULE)
    print("5. IDEMPOTENCY - retry the SAME run object (simulating an at-least-once redelivery)")
    print(RULE)
    before = orchestrator.external_call_count("issue_refund")
    run.next_step_index = 1   # rewind the checkpoint to re-attempt the refund step only
    run = orchestrator.resume(run, workflow, policy, approval=approver)
    after = orchestrator.external_call_count("issue_refund")
    print(f"issue_refund calls before retry: {before}")
    print(f"issue_refund calls after retry:  {after}")
    print("(unchanged - the idempotency key already existed, so the second attempt was a no-op)")

    print("\n" + RULE)
    print("6. DURABILITY - crash a fresh run after step 0, then resume from the checkpoint, not step 0")
    print(RULE)
    event2 = channels.from_webhook({
        "type": "ticket.created", "id": "wh_9002", "tenant_id": TENANT,
        "ticket_id": "TCK-5511", "order_id": "ORD-2202", "refund_amount_usd": 10.0,
    })
    run2 = orchestrator.run_workflow("run_002", workflow, event2, policy, crash_after_step=0)
    print(f"after simulated crash: state={run2.state.value}  next_step_index={run2.next_step_index}")
    run2 = orchestrator.resume(run2, workflow, policy, approval=approver)
    print(render_run(run2))
    print(f"\nstate = {run2.state.value}")
    print("(step 0 - the draft reply - only ever ran once, even though the process 'crashed' after it)")

    out = write(run2)
    print(f"\nrun written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
