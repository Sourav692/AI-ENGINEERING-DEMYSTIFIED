# G13 — Evaluation and Release Gating: Cheat Sheet

[Main](G13_Evaluation_And_Release_Gating_Main.md) · [Deep Dive](G13_Evaluation_And_Release_Gating_Deep_Dive.md) · [Unchanged source](G13_Evaluation_And_Release_Gating.md)

## Ask first

Critical apps and slices? Release window? Labels/rubric owner? Sensitive traces? Block versus hold thresholds? Override authority?

## Whiteboard path

`Release request → pinned artifact + baseline → versioned suites → sandbox runners → deterministic checks + calibrated LLM grader → validated results → policy delta → pass / block / hold → online feedback`

LLM graders score; deterministic policy and authorized humans decide.

## Numbers

30 apps × 20 candidates/day × 5K cases = **3M executions/day**. At 2–5 calls: **6–15M calls/day**; six-hour peak ≈ **278–694 calls/s**. Tier suites and quota the shared worker pool.

## Gate rules

- Pin model, prompt, retrieval, tool, policy, dataset and rubric versions.
- Compare candidate to current production baseline across quality, safety, p95 latency and cost.
- Safety floor and critical slices pass independently of the aggregate.
- Missing evidence **blocks**; thin or disputed evidence **holds**.
- Calibrate the versioned LLM grader against humans before making it a hard gate.

## Incident to cite

Sales copilot: aggregate 96.7% pass on 120 cases; just six regulated-claim cases at 83.3%; unsupported claims 8.7% online versus 1.2% baseline; claim policy changed to warn-only. Roll back route, restore blocking, add claim-level critical-slice coverage.

## Cost close

Sample easy cases for smoke, use cheap judge then strong-judge/human escalation, run full critical suites at release, and cache only unchanged pairs. Do not thin the highest-risk slice.

**60-second close:** “I build a decision record around pinned evidence. The runner executes the application in a sandbox, calibrated graders and deterministic checks score it, and policy compares four independent dimensions with critical-slice gates. The platform holds or blocks when evidence is untrustworthy, then learns from production escapes.”
