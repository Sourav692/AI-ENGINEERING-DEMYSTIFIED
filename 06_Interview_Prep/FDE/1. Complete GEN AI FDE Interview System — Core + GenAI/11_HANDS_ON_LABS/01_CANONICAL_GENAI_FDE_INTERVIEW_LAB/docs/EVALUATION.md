# Evaluation

## Why GenAI evaluation matters

GenAI systems can regress after a data update, prompt change, model migration, or retrieval tuning change. Evaluation turns quality and safety into repeatable checks.

## Offline evaluation

Offline evaluation runs against a golden dataset before deployment. This lab checks:

- Retrieval relevance
- Permission leakage
- Citation presence
- PII redaction
- Safe failure behavior

## Online evaluation

Production systems should also monitor live behavior:

- Thumbs up/down
- Human review outcomes
- Escalation rates
- Deflection rates
- Latency and cost
- Refusal quality
- Source-click behavior

## Golden datasets

A strong golden dataset contains:

- Common happy-path questions
- Ambiguous questions
- Restricted-access attempts
- Prompt injection attempts
- PII-heavy examples
- No-context questions
- High-risk domain questions

## Human review

Human review is essential when the business cost of a wrong answer is high. Examples:

- Legal contract review
- Healthcare intake
- Financial compliance
- Security incident triage
- Customer-facing refund promises

## Regression testing

Every prompt or retrieval change should run evaluation tests. The CI pipeline should fail if restricted content leaks or PII redaction fails.

## Metrics

Retrieval metrics:

- Precision@k
- Recall@k
- Mean reciprocal rank
- Source coverage
- Permission-filter rejection count

Generation metrics:

- Groundedness
- Citation correctness
- Refusal correctness
- PII leakage rate
- Human approval rate
- Latency
- Cost per answer
