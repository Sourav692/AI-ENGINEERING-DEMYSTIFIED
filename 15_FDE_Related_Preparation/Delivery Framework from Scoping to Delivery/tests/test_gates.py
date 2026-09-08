# -*- coding: utf-8 -*-
"""Gate-enforcement tests - the properties that must hold on every engagement,
mirroring test_pipeline.py's role in the RAG project. No LLM involved anywhere
in this project, so these are all fast and deterministic.
"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest

from delivery_framework import accelerators, engine, gates, metrics
from delivery_framework.identity import get_principal
from delivery_framework.models import GateStatus, Stage
from delivery_framework.pipeline import ScopingRefused, intake

FDA = get_principal("u_fda_sourav")
SEC = get_principal("u_sec_priya")
SME = get_principal("u_sme_northwind")
SPONSOR = get_principal("u_sponsor_northwind")
WRONG_HAT = get_principal("u_fda_wrong_hat")


def fresh_engagement():
    return intake(customer_name="Test Co", success_metrics=["ticket latency < 5m"],
                 data_sources=["zendesk_connector"], customer_sme="u_sme_test")


def test_intake_refuses_unmeasurable_metrics():
    with pytest.raises(ScopingRefused):
        intake(customer_name="Vague Corp", success_metrics=[],
              data_sources=["zendesk_connector"], customer_sme="u_sme_test")


def test_intake_refuses_missing_sme():
    with pytest.raises(ScopingRefused):
        intake(customer_name="No SME Corp", success_metrics=["x"],
              data_sources=["zendesk_connector"], customer_sme=None)


def test_intake_refuses_no_data_sources():
    with pytest.raises(ScopingRefused):
        intake(customer_name="No Data Corp", success_metrics=["x"],
              data_sources=[], customer_sme="u_sme_test")


def test_intake_accepts_a_well_formed_request():
    eng = fresh_engagement()
    assert eng.current_stage == Stage.SCOPING
    assert eng.day == 1


def test_wrong_role_cannot_sign_a_gate():
    eng = fresh_engagement()
    d = gates.sign_off(eng, "security_review_passed", WRONG_HAT, "trust me")
    assert d.denied
    assert d.rule == "wrong_role"


def test_missing_evidence_is_denied():
    eng = fresh_engagement()
    d = gates.sign_off(eng, "security_review_passed", SEC, "")
    assert d.denied
    assert d.rule == "no_evidence"


def test_correct_role_and_evidence_passes():
    eng = fresh_engagement()
    d = gates.sign_off(eng, "security_review_passed", SEC, "SEC-142 report")
    assert d.allowed
    assert eng.gates["security_review_passed"].status == GateStatus.PASSED
    assert eng.gates["security_review_passed"].signed_by == SEC.user_id


def test_gate_for_a_later_stage_cannot_be_signed_out_of_order():
    eng = fresh_engagement()
    # data_access_granted blocks CONFIGURE; security_review_passed (blocks
    # DATA_READINESS, which comes first) has not been signed yet.
    d = gates.sign_off(eng, "data_access_granted", SME, "tokens verified")
    assert d.denied
    assert d.rule == "prior_gate_incomplete"


def test_stage_cannot_advance_while_its_gate_is_pending():
    eng = fresh_engagement()
    d = engine.advance_stage(eng)
    assert d.denied
    assert d.rule == "gate_blocked"
    assert eng.current_stage == Stage.SCOPING


def test_stage_advances_once_its_gate_passes():
    eng = fresh_engagement()
    gates.sign_off(eng, "security_review_passed", SEC, "SEC-142 report")
    d = engine.advance_stage(eng)
    assert d.allowed
    assert eng.current_stage == Stage.DATA_READINESS


def test_advance_is_always_exactly_one_stage_no_skipping():
    """There is no API that jumps to an arbitrary stage - advance_stage() only
    ever moves to STAGE_ORDER[current+1], so 'skip a stage' is not a code path
    that exists to call, the same way retrieval has no code path that skips the
    ACL filter in the RAG project."""
    eng = fresh_engagement()
    gates.sign_off(eng, "security_review_passed", SEC, "SEC-142 report")
    engine.advance_stage(eng)
    assert eng.current_stage == Stage.DATA_READINESS
    assert eng.current_stage != Stage.CONFIGURE


def test_deploy_blocked_before_go_no_go_stage():
    eng = fresh_engagement()
    d = engine.mark_deployed(eng)
    assert d.denied
    assert d.rule == "not_at_go_no_go"


def test_escalation_fires_at_day_3_if_data_access_still_pending():
    eng = fresh_engagement()
    eng.day = 3
    engine.check_escalation_triggers(eng)
    assert any(e.reason.startswith("data_access_delayed") for e in eng.escalations)


def test_escalation_does_not_fire_before_day_3():
    eng = fresh_engagement()
    eng.day = 2
    engine.check_escalation_triggers(eng)
    assert eng.escalations == []


def test_escalation_does_not_fire_if_gate_already_passed():
    eng = fresh_engagement()
    gates.sign_off(eng, "security_review_passed", SEC, "SEC-142 report")
    engine.advance_stage(eng)
    gates.sign_off(eng, "data_access_granted", SME, "tokens verified")
    eng.day = 3
    engine.check_escalation_triggers(eng)
    assert eng.escalations == []


def test_accelerator_reuse_rate():
    eng = fresh_engagement()
    accelerators.pull_or_build(eng, "connector", "zendesk_connector")     # in library
    accelerators.pull_or_build(eng, "connector", "totally_custom_thing")  # not in library
    assert metrics.accelerator_reuse_rate(eng) == 0.5


def test_metrics_summary_is_none_before_anything_happens():
    eng = fresh_engagement()
    s = metrics.summary(eng)
    assert s["time_to_first_value_days"] is None
    assert s["eval_score_at_handover"] is None
    assert s["human_approval_override_rate"] is None
