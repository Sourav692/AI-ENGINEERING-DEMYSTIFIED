# 06. Evaluation and Launch Gating
## What the diagram shows

This diagram shows how offline evaluations, synthetic tests, red-team tests, and regression suites feed into a launch gate. If the system passes, it goes to an online canary, then monitoring. If quality degrades, the rollback plan is activated.

The main lesson is that GenAI launch readiness requires measurable gates, not subjective demos.

## How to explain it in an interview

A strong spoken explanation could be:

> I would define launch gates before building the system. For example, groundedness must be above a threshold, citation precision must pass, unsafe answer rate must be below a limit, latency p95 must meet the SLO, and cost per successful task must be within budget. Offline evals catch regressions before release. Canary monitoring validates real traffic. Rollback must be automatic or operationally simple if quality, safety, or cost metrics degrade.

## Key trade-offs

- **Offline evals vs online reality:** Offline datasets are controlled but may not represent real users.
- **Synthetic tests vs human-labeled tests:** Synthetic tests scale quickly but may miss subtle business requirements.
- **Strict gates vs release speed:** Strong gates reduce incidents but can slow iteration.
- **Quality metrics vs cost metrics:** Better models may pass quality but fail budget.
- **Canary size:** Small canaries reduce blast radius but may not produce enough signal.

## Failure modes

- Golden dataset is too easy or outdated.
- Evals measure answer style but not factual correctness.
- Red-team tests do not cover real business abuse cases.
- Launch gate ignores latency, cost, or refusal rate.
- Canary monitoring lacks baseline comparison.
- Rollback is manual and slow.
- New model version passes offline eval but fails on real customer data.

## Security concerns

- Include prompt injection, data exfiltration, cross-tenant leakage, and unsafe tool-use tests.
- Evaluate refusal behavior for restricted data requests.
- Track whether sensitive data appears in generated answers.
- Include audit requirements in launch criteria.
- Ensure canary exposure is limited to approved users or tenants.

## What a weak candidate misses

A weak candidate says: “We will test the model and monitor it.” This lacks concrete datasets, metrics, thresholds, canary criteria, and rollback triggers.

## What a strong candidate says

A strong candidate defines measurable gates: groundedness, citation accuracy, task success, retrieval recall, unsafe output rate, latency p95, cost per task, human escalation rate, and regression failure thresholds. They explain how launch is blocked or rolled back when these thresholds fail.

## Visual improvement suggestion

Show the system as a release pipeline:

- **Offline Stage:** Golden Dataset, Synthetic Tests, Red-Team Tests, Regression Suite
- **Gate Stage:** Thresholds and Sign-Off
- **Online Stage:** Canary, Monitoring, Feedback
- **Recovery Stage:** Rollback, Disable Feature Flag, Revert Model/Prompt/Index

Add a feedback arrow from production failures back to the golden dataset.
