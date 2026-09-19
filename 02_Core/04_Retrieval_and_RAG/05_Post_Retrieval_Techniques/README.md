# Post-Retrieval Techniques

**Status:** ✅ Built.

Split out of [`Query_Transformation_Techniques/`](../Query_Transformation_Techniques/) —
`CrossEncoder_Reranking.ipynb` got merged in alongside the query-rewriting/decomposition/routing
notebooks originally, but it doesn't transform the query at all; it runs *after* retrieval, on
documents a first-pass search already returned. See
[`../Indexing_Techniques/`](../Indexing_Techniques/) for the two indexing-stage notebooks that
were originally grouped with this one.

## What This Folder Covers

A first-pass retrieval (plain vector similarity search) is cheap but approximate — it's good
at finding documents that are *plausibly* relevant, not necessarily ranking them by how
relevant they truly are. **Post-retrieval techniques take that already-retrieved candidate set
and refine it further before it reaches generation**, without touching the query or the index:

- **`CrossEncoder_Reranking.ipynb`** — re-scores the initial retrieved documents with a more
  expensive but more accurate cross-encoder model (which jointly encodes the query *and* each
  document together, rather than comparing separately-computed embeddings), so only the
  genuinely most-relevant documents make it into the LLM's context.

## Which RAG Stage Is This?

**Post-retrieval / refinement** — strictly after an initial retrieval step returns candidates,
and before those candidates reach generation:

| Notebook | Stage | Why |
|---|---|---|
| `CrossEncoder_Reranking.ipynb` | Post-retrieval | Doesn't transform the query (retrieval-stage) or change what's indexed (indexing-stage) — it re-scores documents a prior retrieval step already returned. Some taxonomies fold this into "retrieval" broadly; it's called out separately here because the mechanism (reranking retrieved candidates) is distinct from either transforming a query or building an index. |

## Notebooks

| Notebook | Topic |
|---|---|
| `CrossEncoder_Reranking.ipynb` | Cross-encoder reranking of retrieved documents |
