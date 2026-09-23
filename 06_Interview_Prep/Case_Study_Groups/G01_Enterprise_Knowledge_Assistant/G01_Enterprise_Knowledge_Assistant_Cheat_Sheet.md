# G01 — Enterprise Knowledge Assistant: Cheat Sheet

## Problem

**Enterprise RAG where different users must get different correct answers.**

Primary constraint:

> **Permission fidelity.**

## Core architecture

**Identity → Authorization → Pre-filter → Hybrid Retrieval → Rerank → Evidence → LLM → Verify → Answer/Abstain/Escalate**

Security loop:

**Source events → ACL + Version + Tombstone → Index → Reconciliation**

**LLM/agent role:** LLM gateway generates from authorized evidence; optional multi-hop planning never decides access. This is a RAG assistant, not an autonomous write agent.

## Five rules

1. Permission first, retrieval second, generation third.
2. Unauthorized content never enters the LLM context.
3. Authorization is deterministic, not LLM-based.
4. Fail closed on security.
5. **Leak count = 0** is a release gate.

## Pre-filter vs post-check

**Pre-filter:** search only authorized documents; improves recall, latency and top-k utilization.

**Post-check:** final authoritative boundary; catches revocation, stale ACLs, embargoes and policy changes.

> **Pre-filter for efficiency. Post-check for correctness.**

## Retrieval

**Dense** → semantic meaning

**BM25** → exact IDs/error codes/policy names

**RRF** → combine ranks

**Reranker** → improve ordering

Correct order:

**Authorize → Retrieve → Fuse → Rerank → Evidence → Generate**

## Freshness

Missed deletion?

**Tombstone + reconciliation + revalidation**

Remember:

> Authorization correctness ≠ freshness correctness.

## RAG quality

Measure:

- Recall@k
- groundedness
- citation correctness
- citation completeness
- abstention
- freshness

## Security tests

- cross-tenant access
- revoked access
- deleted docs
- private Slack/DMs
- stale ACLs
- prompt injection
- cache leakage
- citation leakage
- trace leakage

Retrieved content = **data, not instructions**.

## Scale numbers

| Number | Meaning |
|---|---|
| 100k users | ACL cardinality |
| 50M chunks | Refresh/deletion problem |
| 20 QPS | Average |
| 100 QPS | Peak serving |
| <3 s | Chat target |
| <8 s | Relaxed interactive |
| ~100 ms | Generation leaves hot path |

## Cost / latency

**Measure → Route → Bound → Compress → Selective rerank → Cache safely**

Cache key:

**tenant + permission signature + index version + query**

Never simply:

**query → answer**

## Failure playbook

**Stale index** → freshness alert + reconciliation

**Missed deletion** → tombstone + revalidation

**Prompt injection** → retrieved text is data + tool gateway

**Vector drift** → versioned index + offline eval + staged cutover

**Slow reranker** → smaller pool / cheaper model / selective rerank

**LLM unavailable** → safe retrieval-only result or abstain

**Auth unavailable** → fail closed

## Databricks

> **Governed source ≠ automatically governed search index.**

Verify identity propagation, revocation, index restrictions and deletion/ACL SLO.

Bring a **persona × document visibility matrix**.

## Project story

> “I built an enterprise AI search system where the hardest part wasn't finding the right answer. It was making sure the same question produced the right answer for the right person.”

Five beats:

**Problem → Permission-first design → Two checkpoints → Production lessons → Honest limitation**

## Interview triggers

| Trigger | Answer |
|---|---|
| Why not post-filter? | Wastes top-k + hurts recall |
| Why two checks? | Fast pre-filter + authoritative post-check |
| ACL changes? | Query-time enforcement |
| Deletion missed? | Tombstone + reconciliation |
| Why hybrid? | Semantic + exact match |
| Rerank when? | After authorization |
| Hallucination? | Evidence + citation + abstain |
| Prompt injection? | Data ≠ instructions |
| Scale? | Peak QPS + refresh |
| No leaks? | Fail closed + leak suite |
| 100 ms? | Remove generation from hot path |
| Cost? | Route + bound + selective rerank + cache |
| Databricks? | Verify governance at index boundary |

## One sentence

> **Permission first. Retrieve only what the user can see. Rerank that pool. Generate only from verified evidence. If uncertain, abstain rather than leak or hallucinate.**
