# -*- coding: utf-8 -*-
"""Shared scenario setup for both demo scripts - the Cascade Robotics workflows,
built directly as WorkflowSpec objects (standing in for what a visual builder
would emit as JSON, per §3.3 - "never raw code")."""
from agent_platform.guardrails import GuardrailPolicy
from agent_platform.models import Channel, Step, Trigger, WorkflowSpec, WorkflowStatus
from agent_platform.workflows import WorkflowStore

TENANT = "cascade_robotics"


def build_store() -> WorkflowStore:
    store = WorkflowStore()

    store.publish(WorkflowSpec(
        workflow_id="wf_ticket_triage", tenant_id=TENANT, name="Ticket Triage + Refund",
        version=1, status=WorkflowStatus.DRAFT,
        triggers=[Trigger(channel=Channel.WEBHOOK, event_type="ticket.created", priority=10)],
        steps=[
            Step(name="draft", tool="draft_reply",
                args_template={"ticket_id": "{ticket_id}", "body": "Thanks - we're on it."}),
            Step(name="refund", tool="issue_refund",
                args_template={"order_id": "{order_id}", "amount_usd": "{refund_amount_usd}"}),
        ],
        max_steps=10, max_cost_usd=100.0,
    ))

    store.publish(WorkflowSpec(
        workflow_id="wf_legacy_ticket_tagger", tenant_id=TENANT,
        name="Legacy Auto-Tagger (lower priority, same trigger)",
        version=1, status=WorkflowStatus.LIVE,
        triggers=[Trigger(channel=Channel.WEBHOOK, event_type="ticket.created", priority=1)],
        steps=[Step(name="tag", tool="tag_ticket", args_template={"ticket_id": "{ticket_id}", "tag": "auto-triaged"})],
    ))

    store.publish(WorkflowSpec(
        workflow_id="wf_runaway", tenant_id=TENANT, name="Misconfigured self-triggering workflow",
        version=1, status=WorkflowStatus.LIVE,
        triggers=[Trigger(channel=Channel.WEBHOOK, event_type="ticket.updated", priority=10)],
        steps=[Step(name=f"tag_{i}", tool="tag_ticket",
                    args_template={"ticket_id": "{ticket_id}", "tag": f"pass-{i}"}) for i in range(30)],
        max_steps=5,
    ))

    return store


def default_policy() -> GuardrailPolicy:
    return GuardrailPolicy(tenant_id=TENANT, spend_cap_usd=50.0, max_steps=10,
                           allowed_destructive_tools_autonomous=["tag_ticket"])
