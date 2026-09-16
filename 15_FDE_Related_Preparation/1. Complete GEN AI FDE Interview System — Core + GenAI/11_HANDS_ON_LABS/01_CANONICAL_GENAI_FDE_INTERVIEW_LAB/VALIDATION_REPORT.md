# Canonical Lab Fix Report

## Validation result

- `pytest -q`: **20 passed**
- `ruff check backend tests`: **passed**
- `bandit -r backend -x backend/evals,backend/tests -q`: **passed**
- `python -m compileall -q backend tests`: **passed**

## Principal fixes

1. Resolved the `backend.rag.embeddings` module/package collision by adding a proper package API.
2. Preserved the offline retrieval baseline and renamed it accurately as lexical-vector scoring.
3. Added a deterministic provider-compatible `LexicalVectorEmbeddingProvider`.
4. Repaired incomplete RAG domain models and missing imports.
5. Implemented a functional in-memory vector store with dimension validation and cosine search.
6. Repaired the ingestion service and its chunker/vector-store contracts.
7. Removed an accidental fake provider implementation from `backend/rag/__init__.py`.
8. Restored meaningful unit tests for similarity, ingestion, deterministic vectors, retrieval mode, and vector storage.
9. Expanded pytest discovery to include `backend/tests`.
10. Corrected the CI Bandit command so test assertions under `backend/evals` and `backend/tests` do not make the security job fail.
11. Repaired Python project metadata and separated the optional sentence-transformer dependency from the offline default path.
12. Updated architecture wording to stop presenting lexical vectors as semantic embeddings.
