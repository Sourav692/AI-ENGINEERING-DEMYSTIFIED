# 03. Ingestion Pipeline
## What the diagram shows

This diagram shows the document ingestion path for a production RAG system. Source systems feed connectors. Documents pass through PII scanning, parsing, chunking, metadata enrichment, embedding generation, keyword indexing, lineage storage, quality checks, and finally vector indexing.

The key point is that retrieval quality is determined long before the user asks a question. Bad ingestion produces bad answers.

## How to explain it in an interview

A strong spoken explanation could be:

> I would design ingestion as an auditable pipeline, not a one-time script. Each document receives a source ID, version, checksum, tenant ID, ACL metadata, classification label, parser status, chunk IDs, embedding version, and lineage record. Quality checks catch empty chunks, corrupted PDFs, excessive PII, duplicated content, and failed embeddings. The vector index should be rebuilt or incrementally updated when documents, permissions, or embedding models change.

## Key trade-offs

- **Batch vs streaming ingestion:** Batch is simpler; streaming gives fresher answers but adds operational complexity.
- **Chunk size:** Smaller chunks improve precision but may lose context. Larger chunks preserve context but increase prompt cost and reduce retrieval precision.
- **Embedding-only vs hybrid retrieval:** Embeddings capture semantic similarity; keyword indexes help with exact names, IDs, policy numbers, and error codes.
- **PII removal vs answer completeness:** Aggressive redaction improves privacy but can remove useful business context.
- **Incremental updates vs full reindexing:** Incremental updates are cheaper but require strong lineage and consistency checks.

## Failure modes

- Connectors silently fail and documents become stale.
- PDF parser drops tables, headers, or footnotes.
- Chunker splits policy clauses in the wrong place.
- PII scanner misses sensitive data or over-redacts useful content.
- Metadata enricher attaches the wrong tenant or ACL.
- Embedding worker uses an old model version while the query side uses a new one.
- Quality checks pass empty or duplicate chunks.
- Vector index contains deleted documents.

## Security concerns

- Do not ingest documents without verified source permissions.
- Preserve source ACLs and classification labels during chunking.
- Encrypt document content, embeddings, and lineage data where required.
- Keep a deletion pipeline for right-to-be-forgotten or document removal requests.
- Avoid putting raw secrets, tokens, or credentials into embeddings.
- Maintain audit records for ingestion time, parser version, embedding model, and source document version.

## What a weak candidate misses

A weak candidate focuses only on “load documents, create embeddings, store in vector DB.” They miss parsing quality, metadata, ACL propagation, freshness, deletion, re-indexing, and data lineage.

## What a strong candidate says

A strong candidate explains ingestion as a governed data pipeline. They discuss document versions, chunk lineage, ACL metadata, parser failures, quality gates, hybrid indexes, embedding versioning, and operational recovery when ingestion breaks.

## Visual improvement suggestion

Convert the diagram into three grouped layers:

- **Source Layer:** SaaS apps, file stores, databases, tickets, wikis
- **Processing Layer:** Connectors, PII Scanner, Parser, Chunker, Metadata Enricher, Quality Checks
- **Index Layer:** Vector Index, Keyword Index, Lineage Store, Dead-Letter Queue

Add feedback arrows from quality checks to a **reprocess queue**.
