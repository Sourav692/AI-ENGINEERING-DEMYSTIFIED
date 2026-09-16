# Incident 10: Embedding Model Change Degrades Recall Through Vector Drift

## Scenario

A technical support assistant answers questions from product engineers using runbooks, incident postmortems, API docs, and troubleshooting guides. The assistant relies on vector retrieval to find semantically similar chunks before reranking.

On 2026-07-08, after an embedding model migration, engineers reported that the assistant missed obvious runbooks and retrieved loosely related documents instead. The LLM still produced fluent answers, but they were less specific and sometimes omitted critical remediation steps.

This incident is useful because it tests whether candidates understand embedding migrations, index compatibility, recall evaluation, hybrid search, and rollback strategy.

## User-Visible Symptom

An engineer asked: “How do I recover stalled Kafka Connect sink tasks after schema registry auth rotation?” The assistant retrieved generic Kafka troubleshooting docs but missed the exact runbook `RB-KAFKA-CONNECT-042`, which had the correct recovery command sequence.

## System Context

Retrieval path: query embedding → vector DB HNSW index → metadata filters → hybrid BM25 merge → reranker → context assembler. The system migrated from `text_embed_v4` to `text_embed_v5`. Documents should be re-embedded with the same model used for query embeddings, or the system should query the matching index.

## Production Telemetry

```text
2026-07-08T09:58:42.774Z level=warn service=retrieval-eval-monitor
  eval_set=runbook_recall_canary window=30m
  recall_at_5_before=0.86 recall_at_5_after=0.54 mrr_before=0.71 mrr_after=0.39
  affected_domain=kafka_connect embedding_query_model=text_embed_v5
  document_embedding_model_mix={text_embed_v4:0.72,text_embed_v5:0.28}

2026-07-08T09:59:10.018Z level=info service=vector-retriever
  trace_id=trc_vec_3380 request_id=req_eng_14480
  query="recover stalled Kafka Connect sink tasks after schema registry auth rotation"
  query_embedding_model=text_embed_v5 index_name=runbooks_hnsw_mixed_v18
  expected_doc_id=doc_rb_kafka_connect_042 expected_chunk_id=chk_rb_042_06
  expected_chunk_rank=23 top_k=8 top_score=0.62 score_margin=0.03
  retrieved_doc_ids=[doc_kafka_generic_011,doc_schema_registry_faq_003,doc_connect_offsets_019]

2026-07-08T09:59:10.331Z level=warn service=index-migration-worker
  migration_id=emb_v5_runbooks progress=28%
  dual_index_routing=false backfill_status=in_progress
  index_compatibility_warning="query_model_v5_against_mixed_doc_embeddings"
  rollback_index=runbooks_hnsw_v4_ready
```

## What Changed Recently

The embedding migration began on 2026-07-08 at 08:30. Query embeddings were switched to `text_embed_v5` immediately, but only 28% of document chunks had been re-embedded. Dual-index routing was disabled to simplify the release. The canary monitored answer groundedness but not recall@k for critical runbooks.

## Root Cause

The system queried a mixed embedding space: new query embeddings against mostly old document embeddings. Similarity scores became less meaningful, reducing recall for specific technical runbooks. The reranker could not recover the correct answer because the exact runbook was outside the top-k candidate set.

## Debugging Path

A strong engineer compares retrieval metrics before and after the embedding migration, checks query model versus document embedding model, and inspects rank of expected chunks. They evaluate whether BM25 fallback retrieved the runbook and whether the reranker ever saw it. They also compare mixed index behavior to a clean v4 index and a fully rebuilt v5 index sample.

The key is to identify candidate-generation failure. If the right chunk is ranked 23 and top-k is 8, the LLM and reranker never receive the necessary evidence.

## Fix / Mitigation

Immediate mitigation: route queries back to the v4 index until v5 backfill is complete, enable hybrid BM25 fallback for exact runbook IDs, and increase top-k only temporarily for affected domains.

Long-term fix: perform embedding migrations with dual indexes, shadow evaluation, recall gates, and per-domain canaries. Do not switch query embeddings globally until document backfill is complete or routing is model-compatible. Add dashboards for embedding-model mix and recall@k by domain.

## Red-Team / Safety Risk

Vector drift can cause confident but incomplete technical guidance. In SRE workflows, missing a critical runbook step can prolong outages. Attackers may also exploit weak retrieval by using semantically broad phrasing to push the assistant toward generic documents.

## Interview Explanation

A strong candidate should explain that retrieval quality depends on embedding-space consistency. They should discuss recall@k, MRR, expected chunk rank, dual-index migration, and why rerankers cannot fix candidate-generation misses.

## Weak Candidate Answer

“I would increase top-k and use a better model to answer the question.”

## Strong Candidate Answer

“The telemetry shows query embeddings are v5 while 72% of document embeddings are still v4, and recall@5 dropped from 0.86 to 0.54. The expected runbook is ranked 23, so it never reaches the reranker or LLM. I would roll back to the v4 index or use dual-index routing until backfill completes, then add recall gates and shadow evals for future embedding migrations.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies embedding-space/vector drift | Calls it generic retrieval issue |
| Telemetry interpretation | Reads recall@k, MRR, model mix, expected rank | Looks only at answer quality |
| Root-cause reasoning | Connects query/document embedding mismatch | Blames LLM response |
| Production debugging | Tests v4, v5, mixed index, BM25, reranker exposure | Only increases top-k |
| Security/privacy awareness | Notes reliability risk in SRE guidance | Ignores operational impact |
| Mitigation quality | Rollback, dual index, shadow evals, recall gates | “Use better embeddings” vaguely |
| Communication clarity | Explains candidate-generation failure clearly | Gives generic RAG answer |
