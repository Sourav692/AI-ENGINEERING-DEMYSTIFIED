# G18 — Consumer-Scale Chat Service: Cheat Sheet

[Main](/modules/15-fde-case-studies/platforms-and-scale/consumer-scale-chat-service#main) · [Deep Dive](/modules/15-fde-case-studies/platforms-and-scale/consumer-scale-chat-service#deep-dive) · [Unchanged source](/modules/15-fde-case-studies/platforms-and-scale/consumer-scale-chat-service#full-pack)

## Ask first

Consumer or API? DAU and turns? Tiers? History/memory? Files/tools? Serve or train models?

## Whiteboard path

`Client → regional gateway/auth/quota/input moderation → conversation store → bounded context → tier/task router → fair queue → LLM pool → output moderation → SSE stream + partial persistence`

Disconnect cancels model and tools. User scope comes from auth at every store and retrieval boundary.

## Assumed sizing, not production data

100M DAU × ten turns = 1B/day ≈ 11.6K/s average, 35K/s at 3× peak. Eight-second answers imply ~280K open streams; 100 streams/replica implies ~2,800 replicas before token-throughput/KV checks.

## Five lines to remember

- The model is stateless; the product is not.
- Store every turn, send only the summary/recent turns/relevant memory.
- Rate limit decides **whether**; fair queue decides **when**.
- Stable byte-exact prefix and warm replica save input prefill; a model cascade may lose that cache.
- Streaming improves perceived latency; cancellation saves actual GPU cost.

**60-second close:** “Admit safely, assemble bounded user-scoped context, stream from continuously batched pools, persist partial answers and cancel abandoned work. Measure first-token latency, fairness, isolation and cost per user.”
