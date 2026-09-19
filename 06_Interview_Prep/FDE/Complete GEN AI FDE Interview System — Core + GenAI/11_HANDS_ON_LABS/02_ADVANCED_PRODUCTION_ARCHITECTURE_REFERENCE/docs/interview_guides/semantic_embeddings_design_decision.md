# Semantic Embeddings Design Decision

## Decision

The canonical local RAG path uses `sentence-transformers/all-MiniLM-L6-v2` through an `EmbeddingProvider` interface. Every chunk is embedded during ingestion; every query is embedded with the same provider. Vectors are L2-normalized and compared using cosine similarity.

## Why an interface?

The ingestion and retrieval services depend on an application contract rather than a vendor SDK. This allows the local Sentence Transformers implementation and the optional Vertex AI implementation to be exchanged without rewriting business logic.

## Why the same model for documents and queries?

Vectors are comparable only when they are produced in a compatible representation space. Changing model name, preprocessing, normalization, or output dimension requires re-indexing.

## Why normalize?

Normalization makes cosine similarity stable and permits dot-product optimizations in vector engines that support normalized vectors.

## Why cache?

Model files are cached separately from computed embeddings. The SQLite result cache uses a key based on model identity, preprocessing version, and normalized text, so unchanged chunks are not recomputed.

## Deterministic testing

Unit tests inject `DeterministicFakeEmbeddingProvider`. It is a stable test double, not a semantic model. The real neural model is exercised in a separately marked integration test that asserts ranking behavior rather than exact floating-point values.

## Local versus Vertex AI

Local mode is the default because it requires no cloud account, supports privacy-preserving demonstrations, and avoids API cost. Vertex AI is an optional adapter for managed scaling, IAM integration, governance, and Google Cloud interview discussion.

## Production limitations to discuss

- model versioning and drift;
- multilingual and domain-specific quality;
- vector-dimension migrations and re-index cost;
- tenant isolation and permission filtering;
- deletion, retention, and PII handling;
- batch throughput, latency, and backpressure;
- retrieval evaluation with Recall@K, MRR, and nDCG;
- observability without placing raw queries in metric labels;
- explicit failure behavior when the model or index is unavailable.
