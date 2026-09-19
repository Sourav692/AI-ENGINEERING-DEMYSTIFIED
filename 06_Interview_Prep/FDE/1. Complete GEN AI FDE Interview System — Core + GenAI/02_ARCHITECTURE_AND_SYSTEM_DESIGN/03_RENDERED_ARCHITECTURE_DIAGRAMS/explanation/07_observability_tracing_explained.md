# 07. Observability and Tracing
## What the diagram shows

This diagram shows how a request ID connects to a trace collector, which records prompt logs, retrieval metrics, tool-call metrics, safety events, cost, latency SLOs, alerting, and dashboards.

The key idea is that GenAI systems need application observability plus model-specific observability.

## How to explain it in an interview

A strong spoken explanation could be:

> I would assign every user request a trace ID and propagate it through the gateway, retriever, re-ranker, LLM gateway, tool calls, and final answer. For each trace, I would capture retrieved document IDs, chunk scores, prompt version, model version, token usage, latency, safety events, tool calls, refusal reason, and user feedback. The goal is to debug why an answer was wrong, unsafe, slow, or expensive.

## Key trade-offs

- **Debug detail vs privacy:** Rich traces help debugging but may contain sensitive data.
- **Sampling vs completeness:** Full tracing is expensive; sampling can miss rare incidents.
- **Raw prompt logs vs redacted logs:** Raw logs are useful but risky. Redacted logs are safer but less complete.
- **Metric volume vs signal quality:** Too many metrics can hide the few that matter.

## Failure modes

- Missing trace propagation between services.
- Logs capture generated text but not retrieved chunk IDs.
- Safety events are not connected to the original request.
- Cost spikes are detected too late.
- Latency dashboard shows API latency but not retriever or model latency separately.
- Tool-call failures are hidden inside generic LLM errors.
- PII appears in logs.

## Security concerns

- Redact or hash sensitive fields in prompts, traces, and tool outputs.
- Restrict who can view prompt logs.
- Keep audit logs immutable for regulated workflows.
- Separate operational metrics from sensitive content logs.
- Apply retention policies for traces and conversation data.
- Alert on suspicious patterns such as repeated restricted-data requests.

## What a weak candidate misses

A weak candidate says: “Add monitoring with logs and dashboards.” That is too vague. It does not explain what GenAI-specific signals are needed.

## What a strong candidate says

A strong candidate names concrete signals: retrieval recall, top-k scores, citation support rate, prompt version, model version, token cost, tool-call success rate, refusal rate, safety event type, latency by component, and user feedback. They explain how these signals support debugging and launch decisions.

## Visual improvement suggestion

Group the diagram into:

- **Trace Spine:** Request ID and Trace Collector
- **Quality Signals:** Retrieval Metrics, Citation Metrics, Answer Feedback
- **Safety Signals:** Policy Violations, Prompt Injection, Refusals
- **Operational Signals:** Latency, Cost, Tool Errors
- **Action Layer:** Alerting, Dashboard, Incident Ticket

Add a retention and redaction box around prompt logs.
