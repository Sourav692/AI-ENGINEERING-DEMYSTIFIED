# -*- coding: utf-8 -*-
"""The five hard gates (§5.4) plus the terminal go/no-go gate, and the sign-off
decision engine.

Design rule this file exists to enforce, deliberately identical to
authz.policy.decide() in the RAG project:

  1. Deny overrides. Any rule that denies wins.
  2. Rules are ordered and explicit so a reviewer can read them top to bottom.
  3. No gate can be signed off by "I say so" - wrong role or missing evidence is
     always a hard deny, regardless of how senior the signer is.

The six gates, each blocking entry to the stage named:

  security_review_passed  -> blocks DATA_READINESS   (security_reviewer)
  data_access_granted     -> blocks CONFIGURE         (customer_sme)
  golden_set_signed_off   -> blocks EVALUATE          (customer_sme)
  eval_baseline_met       -> blocks SHADOW            (fda)
  rollback_tested         -> blocks LIMITED_PROD      (fda)
  success_metrics_met     -> blocks DEPLOYED          (sponsor)   [go/no-go]
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .models import Decision, Engagement, Gate, GateStatus, Principal, Stage, STAGE_ORDER

GATE_DEFINITIONS: List[Gate] = [
    Gate("security_review_passed",
         "Security review of data access and the deployment footprint is complete.",
         Stage.DATA_READINESS, ["security_reviewer"]),
    Gate("data_access_granted",
         "Read access to the agreed data sources is live and verified.",
         Stage.CONFIGURE, ["customer_sme"]),
    Gate("golden_set_signed_off",
         "The golden evaluation set has been reviewed and approved by the customer's SME.",
         Stage.EVALUATE, ["customer_sme"]),
    Gate("eval_baseline_met",
         "The measured eval score meets the agreed baseline before real traffic sees the agent.",
         Stage.SHADOW, ["fda"]),
    Gate("rollback_tested",
         "A tested rollback path exists before the agent can act on real customer data.",
         Stage.LIMITED_PROD, ["fda"]),
    Gate("success_metrics_met",
         "The agreed success metrics were met in limited production - the go/no-go decision.",
         Stage.GO_NO_GO, ["sponsor"]),
]


def gates_for_stage(stage: Stage) -> List[Gate]:
    """Every gate that must be PASSED before `stage` may be entered."""
    return [g for g in GATE_DEFINITIONS if g.required_before == stage]


def sign_off(engagement: Engagement, gate_name: str, signer: Principal,
            evidence: str) -> Decision:
    """Attempt to sign off one gate. Authoritative - the only way a gate's status
    ever changes. Every attempt, allowed or denied, is logged on the engagement."""
    defn = next((g for g in GATE_DEFINITIONS if g.name == gate_name), None)
    if defn is None:
        decision = Decision(False, "unknown_gate", f"'{gate_name}' is not a defined gate")
        engagement.log("gate_signoff", gate=gate_name, signer=signer.user_id,
                       allowed=False, rule=decision.rule, reason=decision.reason)
        return decision

    gate = engagement.gates.setdefault(gate_name, Gate(
        defn.name, defn.description, defn.required_before, defn.allowed_roles))

    # Rule 1: wrong role - deny overrides seniority.
    if signer.role not in gate.allowed_roles:
        decision = Decision(False, "wrong_role",
                            f"'{signer.role}' may not sign off '{gate_name}'; "
                            f"requires one of {gate.allowed_roles}")
    # Rule 2: no evidence - a sign-off with no artefact behind it is not a sign-off.
    elif not evidence or not evidence.strip():
        decision = Decision(False, "no_evidence",
                            f"'{gate_name}' requires evidence, not just an approval")
    # Rule 3: stage ordering - a gate for stage N can't be signed while every gate
    # for stage N-1 (and earlier) hasn't already passed. Mirrors the pipeline's
    # own no-skipping rule at the gate level, not just the stage-advance level.
    else:
        blocking = _earlier_unpassed_gates(engagement, gate.required_before)
        if blocking:
            decision = Decision(False, "prior_gate_incomplete",
                                f"cannot sign '{gate_name}' - still pending: "
                                f"{[g.name for g in blocking]}")
        else:
            gate.status = GateStatus.PASSED
            gate.evidence = evidence
            gate.signed_by = signer.user_id
            gate.signed_on_day = engagement.day
            decision = Decision(True, "gate_signoff", f"'{gate_name}' passed by {signer.role}")

    engagement.log("gate_signoff", gate=gate_name, signer=signer.user_id,
                   allowed=decision.allowed, rule=decision.rule, reason=decision.reason)
    return decision


def _earlier_unpassed_gates(engagement: Engagement, before_stage: Stage) -> List[Gate]:
    earlier_stages = STAGE_ORDER[:before_stage.order]
    out = []
    for defn in GATE_DEFINITIONS:
        if defn.required_before in earlier_stages:
            g = engagement.gates.get(defn.name)
            if g is None or g.status != GateStatus.PASSED:
                out.append(defn)
    return out


def blocking_gates(engagement: Engagement, target_stage: Stage) -> List[Gate]:
    """Every gate required before `target_stage` that has not yet passed."""
    out = []
    for defn in gates_for_stage(target_stage):
        g = engagement.gates.get(defn.name)
        if g is None or g.status != GateStatus.PASSED:
            out.append(defn)
    return out
