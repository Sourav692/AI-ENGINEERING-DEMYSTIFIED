# Prompt Versioning

Prompts are production artifacts. Treat them like code.

## Registry structure

Prompt files live in `backend/prompts/` and use the pattern:

```text
{name}.{version}.json
```

Each prompt includes:

- Prompt name
- Version
- Use case
- Input variables
- Expected output format
- Owner
- Risk level
- Change history
- System guidance

## Why version prompts

Prompt changes can affect:

- Refusal behavior
- Citation style
- Hallucination risk
- PII leakage
- Latency
- Cost
- Customer trust

## Change policy

For medium/high-risk prompts:

1. Create a new version.
2. Run unit tests.
3. Run evaluation tests.
4. Review failures.
5. Capture reason for change.
6. Roll out gradually.
7. Monitor online metrics.

## Example interview answer

"I would not edit prompts directly in production. I would create versioned prompt artifacts, tie each version to evaluation results, and roll out changes behind a config flag. If permission leakage, citation correctness, or PII tests fail, CI blocks the release."
