# G13 — Evaluation and Release Gating: Main Interview Guide

**Release process** is: you want to change a prompt or model on a live app. A dashboard is not a decision. **Pass, block, or hold** is.

**G13 covers one slice:** a shared gate for ~30 apps vs a pinned production baseline. Not auto-tuning.

End to end, as the refund-bot prompt change:

1. **Someone files a release** with frozen artifacts (prompt, model, retrieval, policy).
2. **A versioned suite and rubric run** in a sandbox — not on live customers.
3. **Deterministic checks plus a calibrated LLM grader** score quality, safety, latency, cost.
4. **Policy compares to the pinned live version.** Groundedness −2% might auto-block or wait for a human — they already said which.
5. **Hold goes to the risk owner**, not a random engineer override.
6. **A prod miss becomes a golden-set case** before the next ship.

That’s it: **pin candidate → eval vs baseline → pass/block/hold → learn.** Shipping on vibes stays out.

> **Source:** [G13_Evaluation_And_Release_Gating.md](G13_Evaluation_And_Release_Gating.md). The [Deep Dive](G13_Evaluation_And_Release_Gating_Deep_Dive.md) expands the gate, graders and incident; the [Cheat Sheet](G13_Evaluation_And_Release_Gating_Cheat_Sheet.md) is for rehearsal.

## The case in one sentence

Build a shared platform for 30 AI applications that makes a controlled **pass, block or hold** release decision against a pinned production baseline, with evidence for quality, safety, latency and cost. A dashboard alone does not own that decision.

## Questions to ask the interviewer

| Question to ask | What it's really asking | What you then decide |
| --- | --- | --- |
| Which applications are critical, and what counts as a release? | Is changing a prompt on the refund bot a “release” that must pass the suite? | Suite tiers and per-app policies. |
| Who owns labels, rubrics, review and override authority? | Can an engineer override a safety fail, or only the risk owner? | Trusted evidence and who may decide. |
| What is the release window and acceptable evaluation spend? | Do we have 20 minutes and $200 per candidate, or overnight and unlimited? | Workers and suite schedule. |
| Which traces contain PII, secrets or proprietary prompts? | Can eval logs contain a customer SSN from a test ticket? | Redaction, retention, and tenant access. |
| Which regressions must block automatically versus hold for review? | If groundedness drops 2%, is that an automatic block or a meeting? | Thresholds and confidence bands. |
| How are post-release failures fed back into tests? | When prod invents a policy, does that case join the golden set before the next ship? | How the suite stays current. |

## Requirements and scale

**Functional:** pin candidate prompt/model/retrieval/tool/policy artifacts; select versioned suites and rubrics; run deterministic and model-based checks; compare candidate with pinned baseline; gate critical slices and four outcome dimensions; route uncertain/disputed cases to humans; record decisions, owners and overrides; sample production failures into a reviewed test pipeline.

**Non-functional:** p95 release evaluation within roughly 20 minutes, reproducibility, tenant isolation, sandboxed runners, trustworthy grader calibration, bounded cost and fail-closed behavior when evidence is missing. Do not assume one universal rubric across applications. The first version does not automate tuning or broadly share tenant datasets.

At 30 apps × 20 candidates/day × 5,000 cases, the full naive volume is **3 million case executions/day**. At 2–5 model/evaluator calls each, that is **6–15 million calls/day**. A six-hour release window raises the required rate to roughly 278–694 calls/s, versus 69–174/s spread across a day. At 2.5 calls/s/worker, that is about 112–278 workers before headroom in the six-hour window. Tier suites and use a shared elastic pool with tenant quotas.

## Architecture

The LLM grader provides one calibrated score, while deterministic checks, policy code and human authority control the release. Candidate applications and evaluation inputs run in a sandbox; the decision plane reads only validated completed results.

```mermaid
flowchart LR
  A[Release request] --> R[Immutable artifact registry]
  D[Versioned dataset + rubric store] --> S[Scheduler / tenant quotas]
  R --> S
  S --> X[Sandboxed app runner]
  X --> T[Deterministic checks]
  X --> J[Versioned LLM grader]
  T --> W[Validated result store]
  J --> W
  W --> P[Policy engine: delta vs pinned baseline]
  P -->|pass| O[Release with decision record]
  P -->|block| B[Stop / remediate]
  P -->|hold| H[Human review / more evidence]
  N[Redacted online sampling] --> D
```

### Step-by-step architecture

1. A release request pins the full candidate artifact bundle and the current production baseline, including model, prompt, retrieval, tool and policy versions.
2. The scheduler chooses versioned suites and app-specific rubrics, applies tenant quotas, and sends cases to sandboxed runners with timeouts and limited egress/secrets.
3. Runners execute the whole application workflow; deterministic checks score schemas, policy rules and measurable outcomes, while a versioned LLM grader evaluates rubric dimensions that require judgment.
4. Validated results are written immutably with run, case, grader and rubric hashes; incomplete runs cannot masquerade as complete evidence.
5. The policy engine computes candidate-minus-baseline deltas for quality, safety, p95 latency and cost, checks critical slices independently, and issues pass, block or hold.
6. Humans review disputed or statistically thin cases and record overrides with reasons. Production signals are redacted and labelled before joining future suites.

## Gate logic and the failure to remember

**Quality** uses task-specific outcomes and a confidence-aware lower bound on candidate delta. **Safety** has an independent floor: better average quality cannot compensate for a safety regression. **Latency** and **cost** have agreed envelopes. Missing evidence blocks; thin evidence holds. A critical slice must pass on its own. For nondeterministic outputs, use repeated trials and outcome equivalence rather than exact text match.

The source's sales-copilot incident shows why: the release suite passed **96.7% of 120 cases**, but only **six** covered regulated claims, with an **83.3%** pass on that slice. Production unsupported claims reached **8.7% versus 1.2% baseline** after a model route change and a policy evaluator changed from block to warn-only. Roll back the route, restore blocking, review affected drafts, and add claim-level cases for security status, ROI and customer-logo permission. Version the policy mode so it cannot bypass the gate.

## Grader trust, cost and rollout

An LLM grader can reward verbosity over correctness. Version its model and rubric, calibrate it against humans using concise-correct and verbose-wrong examples, inspect disagreements, and keep it advisory until it earns trust. Use hidden holdouts, incident cases and critical-slice minimum coverage to prevent benchmark overfit. Online feedback discovers new failure modes; redaction and labelling make them usable offline.

To control cost, run smoke samples on ordinary changes, broader regression at release, and deep audits for high-risk changes. Route easy cases to a cheaper judge, escalate disagreements to a strong judge/human, and cache only unchanged artifact–case–grader pairs. Do not sample away critical slices. Measure cost per release, decision time, grader agreement, escape rate, flaky-case rate and override rate.

Roll out on one critical app with an advisory recommendation; calibrate graders against human labels; add latency and cost gates; then expand through a shared schema with app-specific rubrics. A grader timeout or unavailable evidence store blocks release. A delayed dashboard can degrade if the durable decision record remains intact. Roll back on a bad canary, unchecked severe incident or untrustworthy scoring.

## Two-minute interview answer

“I would build a release decision system, not just an evaluation dashboard. I pin the candidate and production baseline, run versioned cases in an isolated worker pool, score deterministic checks and calibrated LLM rubrics, and store immutable evidence. A policy engine compares quality, safety, latency and cost separately, with critical slices passing independently. Missing results block, thin samples hold, and humans handle disputes and overrides. I would start advisory on one critical app, validate the grader against humans, then harden the gate and expand. Post-release incidents become labelled regression cases, and the gate's own cost and escape rate are measured.”
