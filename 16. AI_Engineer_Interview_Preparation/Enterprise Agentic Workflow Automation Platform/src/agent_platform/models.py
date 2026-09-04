# -*- coding: utf-8 -*-
"""Domain model for the multi-channel agent workflow platform.

Third project in the series, same `Decision` shape as the other two on purpose:
`enterprise_rag_platform.authz.policy.Decision`, `delivery_framework.models.Decision`,
and this one are all (allowed, rule, reason) - a named rule, deny overrides, an
explicit reason, no "because I said so." Access control, delivery gates, and
workflow guardrails are the same kind of problem wearing three different hats.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Channel(Enum):
    EMAIL = "email"
    CHAT = "chat"
    SLACK = "slack"
    WEB_FORM = "web_form"
    WEBHOOK = "webhook"


@dataclass
class Event:
    """The canonical, channel-agnostic event every adapter normalises into.
    Nothing downstream of channels.py ever looks at a raw channel payload again."""

    channel: Channel
    event_type: str
    tenant_id: str
    target_entity_id: str          # what this event is ABOUT - a ticket id, an order id...
    payload: Dict[str, Any]
    raw_ref: str                   # opaque pointer back to the raw source message


class WorkflowStatus(Enum):
    """Staged rollout (§3.3): draft -> testing -> shadow -> live -> autonomous.
    Order matters - see workflows.py::promote(), which enforces it the same way
    delivery_framework.engine.py enforces stage order."""

    DRAFT = 0
    TESTING = 1
    SHADOW = 2          # runs for real, all writes mocked
    LIVE = 3            # acts, but every destructive step needs human approval
    AUTONOMOUS = 4       # acts without approval, within the guardrail policy's caps


STATUS_ORDER: List[WorkflowStatus] = [
    WorkflowStatus.DRAFT, WorkflowStatus.TESTING, WorkflowStatus.SHADOW,
    WorkflowStatus.LIVE, WorkflowStatus.AUTONOMOUS,
]


@dataclass
class ToolDefinition:
    """A typed, schema-validated capability. No tool call ever takes free-text
    arguments - constrained schemas over free text (§3.4)."""

    name: str
    description: str
    schema: Dict[str, str]     # param_name -> "str" | "int" | "float" | "bool"
    required: List[str]
    destructive: bool
    scopes: List[str]


@dataclass
class Trigger:
    channel: Channel
    event_type: str
    priority: int = 0          # higher wins a same-event conflict


@dataclass
class Step:
    name: str
    tool: str
    args_template: Dict[str, str]   # values may reference event.payload via "{field}"


@dataclass
class WorkflowSpec:
    """A versioned, declarative workflow. Never raw code (§3.2) - steps are data,
    the orchestrator is what interprets them."""

    workflow_id: str
    tenant_id: str
    name: str
    version: int
    status: WorkflowStatus
    triggers: List[Trigger]
    steps: List[Step]
    max_steps: int = 10
    max_cost_usd: float = 5.0


@dataclass
class Decision:
    """Same shape everywhere in this three-project series - see module docstring."""

    allowed: bool
    rule: str
    reason: str

    @property
    def denied(self) -> bool:
        return not self.allowed


@dataclass
class RunStep:
    step_name: str
    tool: str
    args: Dict[str, Any]
    idempotency_key: str
    allowed: bool
    rule: str
    reason: str
    side_effect_applied: bool = False
    cost_usd: float = 0.0


class RunState(Enum):
    RUNNING = "running"
    PAUSED_FOR_APPROVAL = "paused_for_approval"
    COMPLETED = "completed"
    HALTED_BUDGET = "halted_budget"
    CRASHED = "crashed"


@dataclass
class Run:
    """One execution of a WorkflowSpec version against one Event."""

    run_id: str
    workflow_id: str
    workflow_version: int
    event: Event
    state: RunState = RunState.RUNNING
    next_step_index: int = 0        # the checkpoint - resume reads this, never index 0
    completed_steps: List[RunStep] = field(default_factory=list)
    total_cost_usd: float = 0.0
    events: List[Dict[str, Any]] = field(default_factory=list)

    def log(self, event_kind: str, **fields: Any):
        entry = {**fields, "kind": event_kind, "step_index": self.next_step_index}
        self.events.append(entry)


@dataclass
class Principal:
    user_id: str
    display_name: str
    role: str   # "author" | "approver" | "admin"
