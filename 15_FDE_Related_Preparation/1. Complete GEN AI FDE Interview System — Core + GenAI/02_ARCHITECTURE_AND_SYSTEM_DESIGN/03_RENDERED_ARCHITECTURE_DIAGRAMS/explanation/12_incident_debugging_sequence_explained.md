# 12. Incident Debugging Sequence
## What the diagram shows

This diagram shows a production debugging workflow for a GenAI incident. A user complaint becomes a support ticket. The team searches traces, retrieves inputs, inspects context, checks ACLs and model version, reproduces the failure, patches the issue, evaluates the fix, and releases through a canary.

The value is that it teaches candidates how to debug GenAI systems using evidence, not guesses.

## How to explain it in an interview

A strong spoken explanation could be:

> I would start with the user complaint and locate the trace ID. Then I would reconstruct the request: user identity, tenant, prompt version, model version, retrieved chunks, permission filters, tool calls, safety events, and final answer. I would check whether the failure came from retrieval, permissions, prompt construction, model behavior, tool execution, or stale data. After reproducing the issue, I would patch the smallest responsible component, run regression and red-team evals, and canary the fix before full rollout.

## Key trade-offs

- **Fast mitigation vs root-cause accuracy:** A temporary block or rollback may be needed before full diagnosis.
- **Patch prompt vs patch pipeline:** Prompt fixes are fast but fragile. Pipeline fixes are stronger but slower.
- **Manual investigation vs automated incident tooling:** Manual debugging works for rare incidents; recurring incidents need dashboards and trace search.
- **Canary rollout vs immediate full fix:** Canary reduces risk but delays full resolution.

## Failure modes

- Support ticket lacks trace ID or exact user input.
- Trace logs are incomplete or redacted too aggressively.
- Team fixes the prompt when the real issue is stale retrieval.
- ACL bug is missed because only the final answer is inspected.
- Model version changed without eval comparison.
- Patch fixes one complaint but causes regression elsewhere.
- Canary metrics do not include the original failure scenario.

## Security concerns

- Limit who can inspect sensitive prompts and retrieved chunks.
- Redact PII in support workflows.
- Audit access to incident traces.
- Check whether the incident exposed restricted or cross-tenant data.
- Add the incident case to regression and red-team tests.
- Notify affected customers if required by policy or regulation.

## What a weak candidate misses

A weak candidate says: “Check logs and fix the prompt.” That is shallow. It ignores retrieval state, ACLs, model versioning, trace reconstruction, reproduction, evals, and canary release.

## What a strong candidate says

A strong candidate follows a disciplined debugging sequence: identify trace, reconstruct inputs, isolate component, reproduce, patch, evaluate, canary, monitor, and add regression coverage. They explain multiple possible root causes rather than blaming the model immediately.

## Visual improvement suggestion

Turn the diagram into an incident swimlane:

- **Support Lane:** Complaint, Ticket, Customer Impact
- **Investigation Lane:** Trace Search, Retrieve Inputs, Inspect Context
- **Root Cause Lane:** ACL Check, Retrieval Check, Model Version Check, Tool Check
- **Fix Lane:** Patch, Eval, Canary Release
- **Learning Loop:** Add Regression Test, Update Runbook, Monitor Recurrence

Add decision diamonds for “Security incident?” and “Rollback needed?”
