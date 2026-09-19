# Indexing Techniques

**Status:** ✅ Built.

Split out of [`Query_Transformation_Techniques/`](../Query_Transformation_Techniques/) — these
2 notebooks got merged in alongside the query-rewriting/decomposition/routing notebooks
originally, but they don't transform the *query* at all. They change how the index itself is
built. See
[`Query_Transformation_Techniques/README.md`](../Query_Transformation_Techniques/README.md#which-rag-stage-is-this)
for the full stage breakdown this split came from, and
[`../Post_Retrieval_Techniques/`](../Post_Retrieval_Techniques/) for the third notebook that
was originally grouped with these two (reranking — a different stage again: after retrieval,
not before it).

## What This Folder Covers

Both notebooks here change **what gets embedded and stored at indexing time**, so that a
later, ordinary similarity search retrieves better context — without any query-side logic
changing at all:

- **`Multi_Representation_Indexing.ipynb`** — embed a compact summary of each document (for a
  precise similarity match against short queries), while storing/returning the full original
  document as what actually gets passed to generation.
- **`Parent_Document_Retrieval.ipynb`** — embed small, specific chunks (for precise retrieval),
  but return the larger parent chunk/document they came from (for full context).

Both follow the same underlying idea: **decouple what you search against from what you feed
to the LLM.** A small, focused unit is best for finding a match; a larger unit is best for
having enough context to actually answer with.

## Which RAG Stage Is This?

**Indexing stage** — both techniques are decided and built *before* any query exists:

| Notebook | Stage | Why |
|---|---|---|
| `Multi_Representation_Indexing.ipynb` | Indexing | Decides what representation of a document gets embedded — a build-time decision. |
| `Parent_Document_Retrieval.ipynb` | Indexing (with a retrieval-time payoff) | The chunk/parent split is set up at indexing time; retrieval then benefits from it automatically — no query-side logic changes. |

## Notebooks

| Notebook | Topic |
|---|---|
| `Multi_Representation_Indexing.ipynb` | Multi-representation indexing (summary embedded, full doc returned) |
| `Parent_Document_Retrieval.ipynb` | Parent-document retrieval (small chunks embedded, parent doc returned) |
