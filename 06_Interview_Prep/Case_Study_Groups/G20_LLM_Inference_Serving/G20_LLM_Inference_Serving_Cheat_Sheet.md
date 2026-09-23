# G20 — LLM Inference Serving: Cheat Sheet

[Main](G20_LLM_Inference_Serving_Main.md) · [Deep Dive](G20_LLM_Inference_Serving_Deep_Dive.md) · [Unchanged source](G20_LLM_Inference_Serving.md)

## Ask first

Input/output tokens p50/p95? Interactive or batch? TTFT or TPOT target? Variable output? Peak, tenants, priorities? Mid-stream failover contract?

## Whiteboard path

`Gateway tokenize + ID → token-weighted bounded admission → router by free KV → replica continuous batch → LLM prefill/decode + paged KV → demux by ID → stream`  
Health evicts sick GPUs; disconnect cancels and frees KV.

## Assumed anchor arithmetic

`1000/20000 + 250/2500 = 0.15` replica-seconds. `1000 rps × 0.15 / 0.70 ≈ 214` replicas. ~7,000 in-flight streams ÷ 64 slots ≈ 110 slot-limited replicas; compute binds. Source rates are illustrative, not benchmarks.

## Five rules

- Prefill → TTFT; decode → TPOT and total time.
- Static generative batches wait for the longest output; continuous batches release finished sequences.
- KV memory, not request count, decides GPU placement; source example ≈128KiB KV/token.
- Unstreamed failed requests retry under budget; streamed ones need explicit continuation/partial-error semantics.
- Refuse early with bounded queues; optimize **goodput**, not raw throughput.

## Variants

#75: one GPU, 100-or-timeout batch, request-ID futures. #77: 100K rps needs request-shape pricing and independent cells. #79: critique static batches, unbounded FIFO and round-robin first. #74: split queue/prefill from decode/post-process latency.

**60-second close:** “Tokenize and admit before GPU work, route by free KV, schedule continuously, stream by request ID, cancel abandoned work and handle GPU failure with a bounded, honest retry policy.”
