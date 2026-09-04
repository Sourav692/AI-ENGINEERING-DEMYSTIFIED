# -*- coding: utf-8 -*-
"""The negative-control demo: prove gates actually block, the way
demo_access_control.py proves ACL denials in the RAG project. Four ways a gate
attempt can fail, and one automatic escalation, none of which require the
engagement's day/stage to be advanced by hand to trigger.

Usage:
    python scripts/demo_gate_failure.py
"""
import json
import sys

import _bootstrap  # noqa: F401

from delivery_framework import engine, gates
from delivery_framework.config import SETTINGS
from delivery_framework.identity import get_principal
from delivery_framework.pipeline import intake, ScopingRefused

RULE = "=" * 100


def main():
    case = json.loads((SETTINGS.data_dir / "case_study.json").read_text(encoding="utf-8"))

    print(RULE)
    print("1. INTAKE REFUSAL - unmeasurable success metrics, same instinct as an unmappable ACL")
    print(RULE)
    try:
        intake(customer_name="Vague Corp", success_metrics=[],
              data_sources=["zendesk_connector"], customer_sme="u_sme_northwind")
    except ScopingRefused as e:
        print(f"REFUSED: {e}\n")

    eng = intake(**case)
    fda = get_principal("u_fda_sourav")
    sec = get_principal("u_sec_priya")
    sme = get_principal("u_sme_northwind")
    wrong_hat = get_principal("u_fda_wrong_hat")   # role="fda", not "security_reviewer"

    print(RULE)
    print("2. WRONG ROLE - the FDA cannot sign off the security gate, however senior")
    print(RULE)
    d = gates.sign_off(eng, "security_review_passed", wrong_hat, "trust me")
    print(f"{'ALLOW' if d.allowed else 'DENY'} [{d.rule}] {d.reason}\n")

    print(RULE)
    print("3. NO EVIDENCE - the right role, but 'approved' is not an artefact")
    print(RULE)
    d = gates.sign_off(eng, "security_review_passed", sec, "")
    print(f"{'ALLOW' if d.allowed else 'DENY'} [{d.rule}] {d.reason}\n")

    print(RULE)
    print("4. OUT OF ORDER - signing a later gate while an earlier one is still pending")
    print(RULE)
    d = gates.sign_off(eng, "data_access_granted", sme, "tokens verified")
    print(f"{'ALLOW' if d.allowed else 'DENY'} [{d.rule}] {d.reason}")
    print("(data_access_granted needs security_review_passed done first - it isn't yet)\n")

    print(RULE)
    print("5. STAGE ADVANCE BLOCKED - trying to enter DATA_READINESS with the gate still pending")
    print(RULE)
    d = engine.advance_stage(eng)
    print(f"{'OK' if d.allowed else 'DENY'} [{d.rule}] {d.reason}\n")

    print(RULE)
    print("6. AUTOMATIC ESCALATION - data access still not granted by day 3 (§5.4 risk mitigation)")
    print(RULE)
    eng.day = 3
    engine.check_escalation_triggers(eng)
    for e in eng.escalations:
        print(f"  ESCALATED on day {e.raised_on_day}: {e.reason}  (resolved={e.resolved})")

    print("\nNow sign off correctly and show the same gate passes:")
    d = gates.sign_off(eng, "security_review_passed", sec, "SEC-2026-0142, no blocking findings")
    print(f"{'ALLOW' if d.allowed else 'DENY'} [{d.rule}] {d.reason}")
    d = engine.advance_stage(eng, to_day=3)
    print(f"{'OK' if d.allowed else 'DENY'} [{d.rule}] {d.reason}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
