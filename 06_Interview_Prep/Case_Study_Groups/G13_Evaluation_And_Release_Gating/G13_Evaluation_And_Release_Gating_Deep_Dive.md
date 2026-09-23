# G13 — Evaluation and Release Gating: Deep Dive

> Read with the unchanged [source](G13_Evaluation_And_Release_Gating.md). The [Main guide](G13_Evaluation_And_Release_Gating_Main.md) gives the interview flow; the [Cheat Sheet](G13_Evaluation_And_Release_Gating_Cheat_Sheet.md) is the recall card.

## 1. Decision contract and stakeholders

An engineer asks whether a change worsened behavior; an evaluator asks what to score; a safety lead asks if it is safe; a release manager needs an auditable decision. The shared platform supplies artifact lineage, execution and evidence, while each app owns its rubric and thresholds. A pass needs a named policy, a pinned baseline and a complete validated run. Block means a known limit failed or required evidence is unavailable; hold means the evidence is too thin or disputed to decide. Every override has an authorized owner and reason.

## 2. Data model and load

Store immutable `EvalArtifact`, `EvalCase`, `EvalRun` and `EvalResult` records. Artifact hashes cover model, prompt, retrieval, tools and policy. Case and rubric versions prevent silent benchmark drift. Results include the grader version, raw trace reference, score, deterministic outcomes and tenant scope. API writes are idempotent; conditional updates protect reviews and decisions. A superseding record is safer than mutating an old result.

Thirty apps × twenty candidates/day × five thousand cases means three million executions/day and six to fifteen million model/evaluator calls at two to five calls per case. Concentration into six hours implies 278–694 calls/s. With 2.5 calls/s per worker, 112–278 workers are a rough pre-headroom range. Use suite tiers, per-tenant quotas and elastic workers. Cache immutable fixtures, but do not cache away a stochastic judgment the release needs to re-measure.

## 3. Evaluation design

Pin a production baseline and compare deltas, not only absolute scores. Quality should represent task completion and can use a bootstrapped lower confidence bound for the delta. Safety has a separate floor; p95 latency and cost each have their own limits. Apply gates per critical slice, since an average hides rare harm. Golden sets should include representative flows, known hard cases, prior incidents, policy-sensitive cases, retrieval misses, malformed tool calls and convincing-but-wrong responses.

LLM-as-judge is itself release logic. Pin its version and rubric hash, calibrate against human labels and audit disagreement, especially concise-correct versus verbose-wrong outputs. Use repeated trials and outcome equivalence for nondeterministic application behavior. Keep a hidden holdout and refresh suites when they stop distinguishing candidates. Online thumbs-down and corrections are leads for new cases, not labels by themselves.

## 4. Incident #91: aggregate success, slice failure

A sales copilot changed its model route while a claim policy changed from block to warn-only. Its 120-case offline suite passed at 96.7%, but only six cases tested regulated claims; that slice passed at 83.3%. Online unsupported claims rose to 8.7% from 1.2%, including unapproved security-certification and internal-pilot ROI claims. The failure is in release coverage and policy control, not simply “the model is creative.”

Contain by rolling back the route, restoring external-claim blocking and reviewing affected drafts. Prevent recurrence with claim-level labelled cases, minimum critical-slice size, zero critical failures for regulated claims and a policy-mode artifact that must pass the same gate. The neighboring “model got worse after upgrade” prompt is this gate run retroactively: replay a fixed set, segment failures, compare retrieval/prompt/schema, human-review the hard cases, then pin or roll back. “No evaluation strategy” is this gate built from scratch with representative data and human labels.

## 5. Trust boundary and failure policy

Candidate prompts, retrieved pages and uploaded cases may contain instructions aimed at the grader. Isolate runners with limited secrets, timeout and egress; sanitize data; pin inputs; store suspicious traces for investigation. Separate tenants and app reviewers. Redact or synthesize sensitive online cases before storage. Keep gate suites away from candidate prompts and retrieval indexes to reduce leakage.

Grader timeout and evidence-store outage block release. A sample too small to support a conclusion holds. Dashboards can lag if an already durable decision record remains available. Retry idempotent writes and move persistent dependency failures to a dead-letter/human-review path. Log policy edits, grader versions, redactions, retries and overrides.

## 6. Rollout and economics

Start with one critical app, human labels and an advisory gate. Promote well-calibrated dimensions to hard gates, then add latency and cost and expand with shared schemas plus app-specific rubrics. Track evaluation coverage, regression escape, human-grader agreement, p95 decision time, cost/run, flaky cases and override reasons. A severe escape or bad canary triggers rollback and a new incident case.

The eval bill can be a major inference bill. Run cheap smoke samples on ordinary changes, full release-relevant suites at gate time and deep audit on high-risk changes. Use a cheap judge for easy cases and a strong judge/human on failures and disagreements; cache only truly unchanged pairs. Keep all critical-slice cases in the release suite. Human review load often dominates marginal cost, so better calibration can lower spend without weakening the gate.
