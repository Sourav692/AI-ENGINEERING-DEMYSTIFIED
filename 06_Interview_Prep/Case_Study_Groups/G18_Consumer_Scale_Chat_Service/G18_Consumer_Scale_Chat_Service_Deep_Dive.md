# G18 — Consumer-Scale Chat Service: Deep Dive

> Read with the unchanged [source](G18_Consumer_Scale_Chat_Service.md). The [Main guide](G18_Consumer_Scale_Chat_Service_Main.md) is the interview route; the [Cheat Sheet](G18_Consumer_Scale_Chat_Service_Cheat_Sheet.md) is the recall card. The source's design and sizing are constructed from one-line prompts; validate them against a real workload.

## 1. From users to streams

The source assumes 100M daily users, ten messages/user/day, 3× peak, 2,000 input and 400 output tokens per turn. That gives 1B messages/day, ~11,600/s average, ~35,000/s peak, 70M input and 14M output tokens/s at peak. At 50 output tokens/s a 400-token answer takes eight seconds; ~35,000/s × eight seconds ≈ 280,000 concurrent streams. If one replica supports 100 such streams, ~2,800 replicas is only a first sizing pass; actual prefill/decode throughput and KV memory may require more. About 2KB/message yields ~2TB of conversation text per day before indexes, replication and retention.

Prefill processes input and drives first-token latency. Decode produces one output token at a time and drives streaming duration. Long history primarily hurts first-token time; verbose answers primarily hurt total time and concurrency. Report both, not only request latency.

## 2. Durable state with bounded context

Shard conversations by authenticated `user_id`; persist sent messages and partial answers during streaming. A reconnect resumes a known message ID rather than silently generating another answer. Context assembly uses frozen system prompt, rolling summary, recent turns, user-visible/erasable memory and user-scoped retrieved file chunks. A roughly 15-turn fold is the source's illustrative memory-guide choice, not a universal threshold. Summarization costs another call and may drop a critical detail; inspectable memory and recent turns help.

Cross-chat semantic memory and episodic memory have different update rules. Stable facts overwrite by stable key; episodic records append and get pruned. Server-side auth determines user scope on every read. Deletion propagates to conversation store, memory, uploaded files and caches. Neither the model nor a tool parameter is allowed to choose a different user ID.

## 3. Streaming, cache and model routing

SSE fits one-way text streaming; a two-way voice path may need a different transport. Persist partial text, detect closed connections, cancel the inference sequence and in-flight tools, and release KV blocks. Streaming helps perceived latency but does not reduce total compute. Track tokens generated after abandon.

Prefix caching is byte-exact. Keep system text, tool order and serialized keys stable; put timestamps and volatile content after cache breakpoints. Prompt-version changes and model changes invalidate prefix reuse. Soft conversation-to-replica affinity helps reuse warm KV but yields to capacity and health. A cheap-to-medium-to-premium cascade may sacrifice enough cached input to erase the nominal model-price saving; compare cost per successful conversation and regeneration rate. A prompt change is a release and a cache-cost event.

## 4. Quotas, safety and regions

Per-user token buckets cap messages and tokens by tier; weighted fair queues keep admitted paid and free work from starving each other. Bound queues; reject or defer before latency exceeds the SLO. Distinguish gateway-policy 429 from provider/pool saturation. Tools have per-turn step and time caps. Uploads are scanned, parsed and embedded per user. Fetched pages/PDFs are untrusted data. A code sandbox has no network or credentials and is destroyed afterward.

Input moderation prevents severe requests before GPU use. Output moderation catches responses that expose earlier sensitive content and can halt a stream. Trained refusals, moderation classifiers and application policy are different controls. Evaluate false positives and negatives on labeled samples.

Independent regional serving pools and a home region for history contain failures. Asynchronous replication may leave slightly stale history on failover, and a new region has a cold KV cache. Reserved capacity and a circuit breaker bridge failures while new GPUs warm. Residency rules can limit which region is eligible; do not let failover bypass them.

## 5. Measure and gate releases

Observe time to first token by tier/region, queue versus service time, cache-read token share, output length, abandonment, regeneration, moderation outcomes, isolation failures and cost/DAU. Keep raw message text out of ordinary telemetry. Canary model, route and prompt changes and gate on quality, safety, latency and cost. The Claude-service variant asks for the same answer with a deeper dive on batching, GPU capacity registry and cold failover.
