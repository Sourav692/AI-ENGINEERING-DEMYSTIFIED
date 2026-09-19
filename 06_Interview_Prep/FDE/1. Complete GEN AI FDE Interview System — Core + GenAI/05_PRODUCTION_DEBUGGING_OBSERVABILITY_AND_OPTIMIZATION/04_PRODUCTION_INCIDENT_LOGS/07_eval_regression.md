# Incident 7: Model Regression Missed by Weak Evaluation Suite

## Scenario

A sales copilot drafts account-specific outreach emails using CRM notes, product documentation, and approved messaging. The company recently upgraded the model route to improve fluency and personalization.

After the upgrade, sales leaders noticed that emails sounded polished but included unsupported claims about security certifications and customer ROI. Offline evals had passed, so the incident exposed a weakness in the evaluation suite rather than a simple model outage.

This is an important interview incident because it tests whether candidates understand eval design, launch gates, golden datasets, regression coverage, and business-specific failure modes.

## User-Visible Symptom

Sales reps saw persuasive drafts claiming “SOC 2 Type II renewal completed in June 2026” and “average 34% support cost reduction.” The SOC 2 claim was not yet approved for external use, and the ROI claim was only from an internal pilot.

## System Context

Workflow: CRM account context → approved claims retriever → prompt template → LLM gateway → policy evaluator → offline eval suite → online quality monitor. The release gate checked grammar, tone, and general groundedness on 120 examples but included only 6 examples about regulated claims.

## Production Telemetry

```text
2026-07-08T12:16:44.921Z level=warn service=online-eval-monitor
  workflow=sales_email_draft model_route=llm_premium_v3 previous_model_route=llm_standard_v2
  unsupported_claim_rate=8.7% baseline=1.2% sample_size=430
  external_claim_policy_failures=37 severity=high

2026-07-08T12:17:03.108Z level=info service=eval-runner
  eval_suite=sales_copilot_release_gate version=eval_v14
  total_cases=120 pass_rate=96.7% release_gate=pass
  regulated_claim_cases=6 regulated_claim_pass_rate=83.3%
  missing_cases=[security_cert_pending,roi_internal_only,customer_logo_permission]

2026-07-08T12:17:11.339Z level=error service=claim-verifier
  trace_id=trc_eval_4402 request_id=req_sales_91902 tenant_id=acme
  generated_claim="SOC 2 Type II renewal completed in June 2026"
  claim_status=pending_approval approved_for_external_use=false
  retrieved_claim_doc_id=doc_security_roadmap_internal visibility=internal_only
  policy_action=should_block actual_action=warn_only
```

## What Changed Recently

The model router moved sales email drafting from `llm_standard_v2` to `llm_premium_v3` on 2026-07-08 at 09:00 after an offline eval showed better fluency and personalization. The policy evaluator was also changed from block mode to warn-only mode during the experiment to reduce false positives.

## Root Cause

The eval suite over-measured writing quality and under-measured unsupported business claims. It lacked representative cases for pending security certifications, internal-only ROI numbers, and unapproved customer references. The model upgrade increased persuasive extrapolation, and warn-only policy mode allowed risky drafts through.

## Debugging Path

A strong engineer compares offline eval pass rates to online failure modes. They inspect failing drafts, retrieve the claims used, verify claim approval metadata, and segment failures by model route and policy mode. They should ask whether the eval suite reflects real sales-risk scenarios rather than generic writing quality.

They also identify the launch gate flaw: a high aggregate pass rate can hide failure on a small but critical slice.

## Fix / Mitigation

Immediate mitigation: roll back to `llm_standard_v2`, restore policy evaluator block mode for external claims, and add review banners to drafts generated during the experiment.

Long-term fix: create a claim-level eval suite with labeled approval status, add slice-based release gates, require zero critical failures for regulated claims, and monitor unsupported-claim rate online. Add negative examples where the model must refuse to use internal-only claims.

## Red-Team / Safety Risk

Unsupported sales claims can create legal exposure, customer trust damage, and compliance issues. A malicious or careless rep could intentionally prompt the assistant to exaggerate ROI or security status, then send the draft externally.

## Interview Explanation

A strong candidate should explain that evals must match the business risk. They should criticize aggregate pass rates, propose slice-based gates, and connect online monitoring to offline eval expansion.

## Weak Candidate Answer

“The model is too creative. I would make the prompt stricter and ask sales reps to review the output.”

## Strong Candidate Answer

“The failure is an eval and launch-gate problem. The suite passed at 96.7%, but it had only six regulated-claim cases and the online unsupported-claim rate jumped to 8.7%. I would roll back the model route, restore blocking for external claims, add claim-level evals for security, ROI, and customer-logo claims, and require critical slices to pass independently before release.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies eval coverage regression | Says model is “too creative” only |
| Telemetry interpretation | Reads slice pass rates, unsupported claim rate, policy action | Cites aggregate pass rate only |
| Root-cause reasoning | Connects model route, weak evals, warn-only policy | Blames prompt alone |
| Production debugging | Compares offline/online failures by slice | Manually edits one draft |
| Security/privacy awareness | Notes legal/commercial risk of unsupported claims | Treats as style issue |
| Mitigation quality | Rollback, block mode, claim-level gates | Adds generic human review only |
| Communication clarity | Explains why evals missed critical slice | Says “evals passed” defensively |
