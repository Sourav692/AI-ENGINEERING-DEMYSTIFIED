# Semantic Embedding Completion Checklist

- [x] Every ingested chunk receives a dense vector.
- [x] Query text is embedded with the configured provider.
- [x] Document and query vectors are normalized.
- [x] Cosine similarity validates dimensions and zero vectors.
- [x] Model artifacts are cached locally.
- [x] Computed embeddings are cached in SQLite.
- [x] Local mode needs no paid API or cloud account after model download.
- [x] Deterministic unit tests use a clearly labelled fake provider.
- [x] A real-model semantic ranking integration test is included.
- [x] Model name, dimension, normalization, and chunk hash are stored with chunks.
- [x] Optional Vertex AI dependencies are isolated.
- [x] README claims describe the actual behavior and limitations.
- [x] A small retrieval evaluation dataset is included.

## Still an extension point

The PostgreSQL/pgvector adapter remains an explicitly documented production extension. The local canonical path uses the permission-aware in-memory vector store for demonstration and testing.
