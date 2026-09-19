# Observability

## Logs

Use structured logs with request IDs. Logs should explain system behavior without storing sensitive content.

Example safe log:

```json
{"event":"ask_completed","request_id":"req-123","user_id":"u-manager-1","intent":"sales_account_summary","elapsed_ms":42.3}
```

## Metrics

Track:

- Request count
- Average latency
- Max latency
- Retrieval fallback count
- Invalid prompt count
- LLM timeout count
- Safety flag count

## Traces

Production traces should show:

```text
API -> auth -> planner -> retriever -> reranker -> LLM -> redaction -> guardrails -> audit
```

Use OpenTelemetry when moving beyond the local lab.

## Audit events

Audit events should capture decisions:

- User ID
- Role
- Intent
- Source IDs
- Safety flags
- Refusal reason
- Timestamp

They should not store full prompts or raw customer data.

## Token usage

Add model usage tracking:

- Prompt tokens
- Completion tokens
- Total tokens
- Estimated cost
- Cost by tenant/customer/use case

## Cost monitoring

Monitor cost by workflow. FDEs should be able to explain why a design uses a small model, reranker, cache, or retrieval filter.

## Latency monitoring

Measure:

- Authentication latency
- Retrieval latency
- Reranking latency
- LLM latency
- Redaction latency
- Total response time

## Error analysis

Classify errors into operational categories:

- Retrieval unavailable
- LLM timeout
- Invalid prompt version
- Permission denied
- No context found
- PII blocked
- Evaluation regression
