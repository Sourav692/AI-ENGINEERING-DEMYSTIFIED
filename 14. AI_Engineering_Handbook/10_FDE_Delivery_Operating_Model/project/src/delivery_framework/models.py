# -*- coding: utf-8 -*-
"""Domain model for the 2-week scoping-doc-to-deployed-agent delivery framework.

Deliberately mirrors the shape of enterprise_rag_platform's ABAC model - a Stage
gate is decided the same way a document access request is: named rules, deny
overrides, a default deny, and an explicit reason. The parallel is intentional -
"gates are to delivery what ABAC rules are to RAG access."
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Stage(Enum):
    """The seven stages of the 14-day pipeline, in order. Order is enforced -
    see engine.py::advance_stage(). Values are (day_range, label)."""

    SCOPING = ("1-2", "Scoping and qualification")
    DATA_READINESS = ("3-4", "Data readiness")
    CONFIGURE = ("5-7", "Configure, do not code")
    EVALUATE = ("8-9", "Evaluate and iterate")
    SHADOW = ("10-11", "Shadow mode")
    LIMITED_PROD = ("12-13", "Limited production")
    GO_NO_GO = ("14", "Go/no-go and handover")

    def __init__(self, days: str, label: str):
        self.days = days
        self.label = label

    @property
    def order(self) -> int:
        return STAGE_ORDER.index(self)


STAGE_ORDER: List[Stage] = [
    Stage.SCOPING, Stage.DATA_READINESS, Stage.CONFIGURE, Stage.EVALUATE,
    Stage.SHADOW, Stage.LIMITED_PROD, Stage.GO_NO_GO,
]


class GateStatus(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


@dataclass
class Decision:
    """The outcome of one gate sign-off attempt. Same shape as authz.policy.Decision
    in the RAG project on purpose - a gate decision and an access decision are the
    same kind of thing: a named rule, deny-overrides, an explicit reason."""

    allowed: bool
    rule: str
    reason: str

    @property
    def denied(self) -> bool:
        return not self.allowed


@dataclass
class Gate:
    """A hard gate: a named, blocking condition that must PASS before the pipeline
    may enter `required_before`. Signing off requires the right role and evidence -
    "I say so" is not evidence."""

    name: str
    description: str
    required_before: Stage
    allowed_roles: List[str]
    status: GateStatus = GateStatus.PENDING
    evidence: Optional[str] = None
    signed_by: Optional[str] = None
    signed_on_day: Optional[int] = None


@dataclass
class Artifact:
    """Something produced by a stage. Existence of the right artifacts, not time
    elapsed, is what actually lets a stage be considered done."""

    name: str
    stage: Stage
    produced_on_day: int
    owner: str


@dataclass
class AcceleratorAsset:
    """One entry in the reusable accelerator library - a connector, prompt
    template, eval harness, guardrail policy, or dashboard template that a stage
    can pull instead of building from scratch."""

    name: str
    kind: str   # "connector" | "prompt_template" | "eval_harness" | "guardrail_policy" | "dashboard_template"
    description: str


@dataclass
class Pull:
    """A record of one stage either reusing an accelerator asset or building
    something custom. The ratio of reused:custom is the repeatability metric."""

    kind: str
    name: str
    reused: bool
    day: int


@dataclass
class Escalation:
    reason: str
    raised_on_day: int
    resolved: bool = False
    resolved_on_day: Optional[int] = None


@dataclass
class Principal:
    """Who is doing the asking. Mirrors enterprise_rag_platform's Principal -
    resolved fresh, never assumed from context."""

    user_id: str
    display_name: str
    role: str   # "fda" | "security_reviewer" | "customer_sme" | "sponsor"


@dataclass
class Engagement:
    """One customer delivery engagement, tracked end to end."""

    customer_name: str
    success_metrics: List[str]
    data_sources: List[str]
    customer_sme: Optional[str]

    current_stage: Stage = Stage.SCOPING
    day: int = 1
    gates: Dict[str, Gate] = field(default_factory=dict)
    artifacts: List[Artifact] = field(default_factory=list)
    pulls: List[Pull] = field(default_factory=list)
    escalations: List[Escalation] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    deployed: bool = False
    human_approval_overrides: int = 0
    human_approvals_total: int = 0
    eval_scores: Dict[str, float] = field(default_factory=dict)   # stage_label -> score
    retention_week4: Optional[float] = None

    def log(self, event_kind: str, **fields: Any):
        # Reserved keys are set LAST so a caller-supplied field of the same name
        # (e.g. an accelerator's own "kind") can never silently clobber them.
        event = {**fields, "day": self.day, "stage": self.current_stage.label,
                "kind": event_kind}
        self.events.append(event)
