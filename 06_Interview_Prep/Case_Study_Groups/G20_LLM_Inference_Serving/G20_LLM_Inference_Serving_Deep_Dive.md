# G20 — LLM Inference Serving: Deep Dive

> Read with the unchanged [source](G20_LLM_Inference_Serving.md). The [Main guide](G20_LLM_Inference_Serving_Main.md) gives the interview route; the [Cheat Sheet](G20_LLM_Inference_Serving_Cheat_Sheet.md) is the recall card. Serving-engine mechanisms and all numeric rates in the source are its own illustrative construction.

## 1. Two phases and two capacity checks

Prefill processes input tokens and drives time to first token (TTFT); decode adds output tokens one at a time and drives time per output token (TPOT) and total duration. Size with replica-seconds: under assumed rates, 1,000 input/20,000 prefill + 250 output/2,500 aggregate decode = 0.15 replica-seconds. At 1,000 rps and 70% utilization, ~214 replicas. Little's Law gives ~7,000 concurrent sequences for a seven-second stream; 64 slots/replica suggests ~110 replicas by slots, so the larger compute estimate binds. Both calculations depend on actual model, hardware, batch occupancy and token distributions.

CPU tokenization at the gateway permits token-weighted admission and estimated KV placement, and rejects huge prompts before the GPU queue. Incremental detokenization buffers incomplete characters and checks stop sequences on assembled text. Measure queue wait separately from service time or a peak overload will masquerade as a slow model.

## 2. Continuous batching and KV memory

Static batching waits for the longest generative output and wastes slots; dynamic size-or-time batches suit fixed-shape classifiers. Continuous batching schedules each decode iteration, dropping completed sequences and admitting new ones. Chunk long prefills to limit interference with existing streams, trading some new-request TTFT for better TPOT. Tune batch/concurrency limits against goodput, not raw token throughput alone.

For the source's illustrative 32 layers, eight KV heads, dimension 128, fp16 cache: `2 × 32 × 8 × 128 × 2 = 131,072 bytes`, or 128KiB per token. At 1,250 tokens that is ~160MB/sequence; 64 sequences ~10GB. At 8,000 tokens, ~1GB/sequence; context length can halve or worse the concurrency that fits. Paged KV blocks allocate as generated rather than reserving maximum length and can share identical prefix blocks. When full, preempt or swap/recompute lower-priority sequences rather than crashing the replica.

## 3. Routing, failure and backpressure

Each replica heartbeats free KV blocks, waiting/running sequences and health. The router samples two candidates and chooses the better to reduce herding on stale registry data; prefix affinity is a preference, not permission to queue on a hot replica. The replica makes a final fit check. Autoscale from queue depth and KV pressure, with reserved headroom because loading weights takes minutes.

Health has process liveness, model-loaded readiness and a one-token deep probe for hung devices. A failed replica loses its KV state. Before streaming, retry from scratch elsewhere. After streaming, re-prefill the original prompt plus emitted text if continuation semantics allow; greedy decoding can reproduce exact continuation, while sampling may diverge. Otherwise return an explicit partial error. Budget retries, use jitter and request-ID dedupe, and retain N+1 zone headroom so a failure does not trigger a retry storm.

Admission uses estimated tokens per tenant, a bounded queue and 429/Retry-After or batch deferral. A queue deeper than the SLO can tolerate only converts overload into late failures. Backpressure must propagate from replica saturation to router and gateway. Interactive work outranks offline jobs under load. On disconnect, cancel the sequence and free KV blocks at the next scheduler step.

## 4. One GPU, 100K rps and design review

One-GPU #75: assign a request ID and future, flush a batch when 100 inputs arrive or oldest wait reaches a timeout, run GPU, then resolve each future by ID. The source assumes a full batch of 100 in 200ms, giving a theoretical 500 rps; 400 rps is 80% and may queue badly in bursts. Bound the queue, e.g. two batches, and time out synchronous callers. Variable-length output still favors continuous batching.

For #77 at 100K rps with the source's assumed rates, 1,000/250-token chat needs ~21,400 replicas, 200/20 short completion ~2,570, and 500/1 scoring ~3,630 at 70%. The huge spread is the point: price request shape first. Partition the fleet into independent cells with local routers/registries, a global balancer and per-cell backpressure; reserved headroom absorbs bursts and failures.

For #79, review a junior design by ranking the top risks: static batches for variable output, unbounded global FIFO and round-robin placement. Then inspect size-only flush, weak health checks, unlimited retries, missing request IDs, no cancel and GPU-side tokenization. Explain each failure and its concrete correction rather than reading a long checklist.

## 5. Latency and economics

TTFT regression: inspect client/network, CPU tokenization, queue, long-prompt prefill and KV preemption. TPOT regression: inspect batch size, decode saturation and prefill interference. Slow after last token: detokenization, safety/schema post-process or a buffering proxy. Peak-only high p99 with flat p50 points toward queueing. Goodput is requests finished within SLO; raw throughput can rise while useful throughput falls.

For a high GPU bill, measure goodput/GPU-hour, occupancy, KV utilization and tokens generated after disconnect. Continuous batching, output caps, identical-prefix reuse, appropriate quantization and off-peak batch work are levers. Changing the model or buying GPUs before measuring occupancy may leave the bottleneck untouched.
