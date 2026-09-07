# -*- coding: utf-8 -*-
"""The state machine. This is `graph/build.py` + `graph/nodes.py`'s counterpart in
the RAG project: the thing that encodes ordering as structure, not convention.

The security property in the RAG project is "authorize runs first, enforce runs
before the model sees anything, encoded in the graph's edges." The equivalent
property here is "a stage cannot be entered while any gate blocking it is still
pending, encoded in advance_stage(), not left to whoever is running the
engagement to remember."
"""
from __future__ import annotations

from typing import Optional

from .config import SETTINGS
from .gates import blocking_gates
from .models import Artifact, Decision, Engagement, Escalation, Stage, STAGE_ORDER


def advance_stage(engagement: Engagement, to_day: Optional[int] = None) -> Decision:
    """Try to move the engagement into the next stage in order.

    Blocked if: any gate required before the next stage hasn't passed, or the
    caller tries to skip a stage. Both are hard denies - there is no override.
    """
    current_idx = engagement.current_stage.order
    if current_idx == len(STAGE_ORDER) - 1:
        decision = Decision(False, "already_final_stage",
                            "engagement is already at the final stage")
        engagement.log("advance_attempt", **_decision_fields(decision))
        return decision

    next_stage = STAGE_ORDER[current_idx + 1]
    blockers = blocking_gates(engagement, next_stage)
    if blockers:
        decision = Decision(False, "gate_blocked",
                            f"cannot enter '{next_stage.label}' - pending gate(s): "
                            f"{[g.name for g in blockers]}")
        engagement.log("advance_attempt", target_stage=next_stage.label,
                       **_decision_fields(decision))
        return decision

    engagement.current_stage = next_stage
    if to_day is not None:
        engagement.day = to_day
    decision = Decision(True, "advanced", f"entered '{next_stage.label}'")
    engagement.log("advance_attempt", target_stage=next_stage.label,
                   **_decision_fields(decision))
    return decision


def mark_deployed(engagement: Engagement) -> Decision:
    """The terminal transition - only legal from GO_NO_GO, and only once the
    success_metrics_met gate has passed."""
    if engagement.current_stage != Stage.GO_NO_GO:
        decision = Decision(False, "not_at_go_no_go",
                            "engagement must reach the GO_NO_GO stage first")
    else:
        blockers = blocking_gates(engagement, Stage.GO_NO_GO)
        if blockers:
            decision = Decision(False, "gate_blocked",
                                f"go/no-go gate(s) still pending: {[g.name for g in blockers]}")
        else:
            engagement.deployed = True
            decision = Decision(True, "deployed", "success metrics met - engagement deployed")
    engagement.log("deploy_attempt", **_decision_fields(decision))
    return decision


def record_artifact(engagement: Engagement, name: str, owner: str) -> Artifact:
    a = Artifact(name=name, stage=engagement.current_stage,
                produced_on_day=engagement.day, owner=owner)
    engagement.artifacts.append(a)
    engagement.log("artifact_produced", name=name, owner=owner)
    return a


def record_human_approval(engagement: Engagement, overridden: bool):
    engagement.human_approvals_total += 1
    if overridden:
        engagement.human_approval_overrides += 1
    engagement.log("human_approval", overridden=overridden)


def record_eval_score(engagement: Engagement, score: float):
    engagement.eval_scores[engagement.current_stage.label] = score
    engagement.log("eval_score", score=score)


def check_escalation_triggers(engagement: Engagement, settings=SETTINGS):
    """Run the named risk mitigations (§5.4) as automatic checks, not something a
    human has to remember to notice.

    Currently: data access delayed past day `data_access_escalation_day` without
    the gate passing escalates automatically, per "start day 1, escalate day 3."
    """
    gate = engagement.gates.get("data_access_granted")
    already_escalated = any(e.reason.startswith("data_access_delayed")
                            for e in engagement.escalations)
    if (engagement.day >= settings.data_access_escalation_day
            and (gate is None or gate.status.value != "passed")
            and not already_escalated):
        escalate(engagement, f"data_access_delayed: not granted by day "
                             f"{settings.data_access_escalation_day}")


def escalate(engagement: Engagement, reason: str) -> Escalation:
    e = Escalation(reason=reason, raised_on_day=engagement.day)
    engagement.escalations.append(e)
    engagement.log("escalation_raised", reason=reason)
    return e


def resolve_escalation(engagement: Engagement, reason_prefix: str):
    for e in engagement.escalations:
        if e.reason.startswith(reason_prefix) and not e.resolved:
            e.resolved = True
            e.resolved_on_day = engagement.day
            engagement.log("escalation_resolved", reason=e.reason)


def _decision_fields(d: Decision) -> dict:
    return {"allowed": d.allowed, "rule": d.rule, "reason": d.reason}
