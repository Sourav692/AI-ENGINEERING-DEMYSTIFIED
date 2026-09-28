# -*- coding: utf-8 -*-
"""The happy-path demo: Northwind Logistics, scoping doc to deployed agent, all
14 days, every gate signed off by the right role, in order. Run in front of an
interviewer to show the pipeline actually enforces its own gates rather than
just describing them.

Usage:
    python scripts/run_engagement_demo.py
"""
import json
import sys

import _bootstrap  # noqa: F401

from delivery_framework import accelerators, engine, gates, metrics, observability
from delivery_framework.config import SETTINGS
from delivery_framework.identity import get_principal
from delivery_framework.pipeline import intake

RULE = "=" * 100


def main():
    case = json.loads((SETTINGS.data_dir / "case_study.json").read_text(encoding="utf-8"))

    print(RULE)
    print(f"INTAKE - {case['customer_name']}")
    print(RULE)
    eng = intake(**case)
    print(f"accepted. success_metrics={eng.success_metrics}")
    print(f"data_sources={eng.data_sources}  customer_sme={eng.customer_sme}\n")

    fda = get_principal("u_fda_sourav")
    sec = get_principal("u_sec_priya")
    sme = get_principal("u_sme_northwind")
    sponsor = get_principal("u_sponsor_northwind")

    # --- Day 1-2: Scoping -------------------------------------------------
    engine.record_artifact(eng, "scoping_questionnaire.pdf", fda.user_id)
    engine.record_artifact(eng, "success_metrics_signoff.pdf", sponsor.user_id)
    accelerators.pull_or_build(eng, "connector", "zendesk_connector")
    accelerators.pull_or_build(eng, "connector", "confluence_connector")

    eng.day = 2
    print(gates.sign_off(eng, "security_review_passed", sec,
                         "SEC-2026-0142 review report, no blocking findings").reason)
    print(engine.advance_stage(eng, to_day=3).reason)

    # --- Day 3-4: Data readiness -------------------------------------------
    engine.check_escalation_triggers(eng)   # nothing to escalate yet, access is about to land
    engine.record_artifact(eng, "data_access_verification.log", sme.user_id)
    print(gates.sign_off(eng, "data_access_granted", sme,
                         "Read-only Zendesk/Confluence/Salesforce tokens verified live").reason)
    eng.day = 5
    print(engine.advance_stage(eng, to_day=5).reason)

    # --- Day 5-7: Configure, do not code ------------------------------------
    accelerators.pull_or_build(eng, "prompt_template", "support_triage_prompt")
    accelerators.pull_or_build(eng, "eval_harness", "golden_set_harness")
    accelerators.pull_or_build(eng, "guardrail_policy", "pii_redaction_policy")
    accelerators.pull_or_build(eng, "guardrail_policy", "northwind_custom_escalation_policy")  # not in library
    engine.record_artifact(eng, "golden_set_v1.json", sme.user_id)
    eng.day = 8
    print(f"\n[Day 5-7] pulled {len(eng.pulls)} accelerator assets "
          f"({metrics.accelerator_reuse_rate(eng):.0%} reused)")
    print(gates.sign_off(eng, "golden_set_signed_off", sme,
                         "golden_set_v1.json reviewed, 40 cases approved").reason)
    print(engine.advance_stage(eng, to_day=8).reason)

    # --- Day 8-9: Evaluate and iterate ---------------------------------------
    engine.record_eval_score(eng, 0.83)
    engine.record_artifact(eng, "eval_baseline_report.pdf", fda.user_id)
    print(f"\n[Day 8-9] eval baseline = {metrics.eval_score_at_handover(eng)}")
    print(gates.sign_off(eng, "eval_baseline_met", fda,
                         "eval_baseline_report.pdf - 0.83 vs 0.75 agreed baseline").reason)
    eng.day = 10
    print(engine.advance_stage(eng, to_day=10).reason)

    # --- Day 10-11: Shadow mode -----------------------------------------------
    for overridden in [True, True, False, False, False]:
        engine.record_human_approval(eng, overridden=overridden)
    engine.record_artifact(eng, "rollback_runbook.md", fda.user_id)
    print(f"\n[Day 10-11] shadow-mode override rate = {metrics.override_rate(eng):.0%}")
    print(gates.sign_off(eng, "rollback_tested", fda,
                         "rollback_runbook.md - tested in staging, verified <2min").reason)
    eng.day = 12
    print(engine.advance_stage(eng, to_day=12).reason)

    # --- Day 12-13: Limited production -----------------------------------------
    for overridden in [False, False, False, True, False, False]:
        engine.record_human_approval(eng, overridden=overridden)
    eng.day = 14
    print(f"\n[Day 12-13] cumulative override rate = {metrics.override_rate(eng):.0%}")
    print(engine.advance_stage(eng, to_day=14).reason)

    # --- Day 14: Go/no-go and handover ------------------------------------------
    engine.record_artifact(eng, "handover_runbook.md", fda.user_id)
    engine.record_artifact(eng, "dashboards_live.url", fda.user_id)
    print(f"\n[Day 14] " + gates.sign_off(eng, "success_metrics_met", sponsor,
                         "Week-2 metrics: first-response 4m12s, 63% zero-edit sends").reason)
    print(engine.advance_stage(eng).reason)   # now unblocked - enters GO_NO_GO
    print(engine.mark_deployed(eng).reason)

    print("\n" + RULE)
    print("METRICS SUMMARY")
    print(RULE)
    for k, v in metrics.summary(eng).items():
        print(f"  {k:<28} {v}")

    print("\n" + RULE)
    print("FULL TIMELINE")
    print(RULE)
    print(observability.render_timeline(eng))

    out = observability.write(eng)
    print(f"\nrun written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
