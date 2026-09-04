# -*- coding: utf-8 -*-
"""Policy and guardrail service (§3.2): approval gates, spend caps, step caps.

The rule this file exists to enforce (§3.4): "confirmation gates on destructive
actions, configurable per tenant and per tool" - and the corollary that matters
more: autonomous status does not mean unlimited. A destructive step over the
policy's spend cap needs a human's approval even on a fully autonomous
workflow. Autonomy raises the ceiling; it does not remove it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .config import SETTINGS
from .models import Decision, Principal, Run, Step, ToolDefinition, WorkflowSpec, WorkflowStatus


@dataclass
class GuardrailPolicy:
    tenant_id: str
    spend_cap_usd: float = SETTINGS.default_spend_cap_usd
    max_steps: int = SETTINGS.default_max_steps
    allowed_destructive_tools_autonomous: List[str] = field(default_factory=list)


def authorize_step(workflow: WorkflowSpec, run: Run, step: Step, tool: ToolDefinition,
                   step_cost_usd: float, policy: GuardrailPolicy,
                   approval: Optional[Principal] = None) -> Decision:
    """Decide whether this step may actually execute. Every reason is named,
    same shape as authz.policy.decide() and gates.py::sign_off()."""

    # Rule 1: budget - a run that has run away halts and escalates, it doesn't loop.
    # The effective cap is the TIGHTER of the tenant-wide policy and the workflow's
    # own declared budget - a workflow author can tighten the default, never loosen it.
    effective_max_steps = min(policy.max_steps, workflow.max_steps)
    effective_spend_cap = min(policy.spend_cap_usd, workflow.max_cost_usd)
    if len(run.completed_steps) >= effective_max_steps:
        return Decision(False, "step_budget_exceeded",
                        f"run already used {len(run.completed_steps)} of {effective_max_steps} steps")
    if run.total_cost_usd + step_cost_usd > effective_spend_cap:
        return Decision(False, "spend_cap_exceeded",
                        f"${run.total_cost_usd + step_cost_usd:.2f} would exceed the "
                        f"${effective_spend_cap:.2f} cap")

    # Non-destructive steps need nothing further.
    if not tool.destructive:
        return Decision(True, "non_destructive", "no confirmation gate on a non-destructive step")

    # Rule 2: shadow mode never actually acts, regardless of anything else.
    if workflow.status == WorkflowStatus.SHADOW:
        return Decision(False, "shadow_mode", "destructive steps are mocked, not executed, in shadow mode")

    # Rule 3: below LIVE, a destructive step cannot run at all - drafts/testing
    # never touch real systems.
    if workflow.status in (WorkflowStatus.DRAFT, WorkflowStatus.TESTING):
        return Decision(False, "not_live", f"workflow is {workflow.status.name}; destructive steps are disabled")

    # Rule 4: autonomous status only removes the approval requirement for tools
    # the policy has explicitly allow-listed. Everything else still needs a human.
    if workflow.status == WorkflowStatus.AUTONOMOUS and tool.name in policy.allowed_destructive_tools_autonomous:
        return Decision(True, "autonomous_allowlisted",
                        f"'{tool.name}' is allow-listed for autonomous execution on this tenant")

    # Rule 5: everything else destructive needs a real, present human approval.
    if approval is None:
        return Decision(False, "needs_human_approval",
                        f"'{tool.name}' is destructive and not allow-listed for autonomous use")
    if approval.role not in ("approver", "admin"):
        return Decision(False, "wrong_role", f"'{approval.role}' may not approve a destructive step")

    return Decision(True, "human_approved", f"approved by {approval.display_name}")
