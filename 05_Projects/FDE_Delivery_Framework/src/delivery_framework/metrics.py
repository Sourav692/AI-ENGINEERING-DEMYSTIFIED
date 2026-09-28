# -*- coding: utf-8 -*-
"""The four metrics named in §5.4, plus accelerator reuse as a repeatability
signal. Mirrors evaluation/harness.py's role in the RAG project: the artefact
that turns a claim ("this delivery process works") into a number."""
from __future__ import annotations

from typing import Optional

from .models import Engagement, GateStatus, Stage


def time_to_first_value(engagement: Engagement) -> Optional[int]:
    """Day the first artefact was produced. None if nothing has shipped yet."""
    if not engagement.artifacts:
        return None
    return min(a.produced_on_day for a in engagement.artifacts)


def eval_score_at_handover(engagement: Engagement) -> Optional[float]:
    """The eval score recorded at the EVALUATE stage - the number carried into
    the go/no-go decision."""
    return engagement.eval_scores.get(Stage.EVALUATE.label)


def override_rate(engagement: Engagement) -> Optional[float]:
    """Fraction of human-approval checkpoints where the human overrode the
    agent. High and falling over time is the signal that trust is being earned;
    high and flat means the agent isn't ready for less supervision."""
    if engagement.human_approvals_total == 0:
        return None
    return engagement.human_approval_overrides / engagement.human_approvals_total


def week4_retention(engagement: Engagement) -> Optional[float]:
    """Not knowable until week 4 has actually happened - deliberately None until
    someone records it, rather than a fake 0.0 that looks like a real measurement."""
    return engagement.retention_week4


def accelerator_reuse_rate(engagement: Engagement) -> Optional[float]:
    """Fraction of accelerator pulls that were reused from the library rather
    than custom-built. The actual measure of "productised process," not "heroics
    and bespoke code per customer" (§5.1)."""
    if not engagement.pulls:
        return None
    return sum(1 for p in engagement.pulls if p.reused) / len(engagement.pulls)


def gates_passed_ratio(engagement: Engagement) -> float:
    from .gates import GATE_DEFINITIONS
    passed = sum(1 for defn in GATE_DEFINITIONS
                if engagement.gates.get(defn.name)
                and engagement.gates[defn.name].status == GateStatus.PASSED)
    return passed / len(GATE_DEFINITIONS)


def summary(engagement: Engagement) -> dict:
    return {
        "customer": engagement.customer_name,
        "stage": engagement.current_stage.label,
        "day": engagement.day,
        "deployed": engagement.deployed,
        "gates_passed": gates_passed_ratio(engagement),
        "time_to_first_value_days": time_to_first_value(engagement),
        "eval_score_at_handover": eval_score_at_handover(engagement),
        "human_approval_override_rate": override_rate(engagement),
        "week4_retention": week4_retention(engagement),
        "accelerator_reuse_rate": accelerator_reuse_rate(engagement),
        "open_escalations": sum(1 for e in engagement.escalations if not e.resolved),
    }
