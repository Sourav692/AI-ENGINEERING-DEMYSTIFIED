# Query Transformation Techniques

**Status:** ✅ Built.

Merged from `RAG_Demystified`'s "Advanced RAG" module — despite the source's naming, this is query-transformation/retrieval technique content that doesn't require knowing agents, so it lives here in the foundational RAG phase rather than Phase 8.

## What Do We Mean by "Query Transformation"?

A naive RAG pipeline takes the user's raw question, embeds it, and runs a similarity search
against the vector store as-is. That works poorly whenever the question is ambiguous, too
broad/narrow, phrased differently from how the answer is worded in the source documents, or
actually bundles several sub-questions together.

**Query transformation techniques rewrite, expand, decompose, or route the query *before* (or
instead of) searching with it verbatim** — the goal is always the same: get the retriever to
pull back more relevant, more complete context than a single raw-query search would.

- **Rewriting / expansion** — turn one query into a better one, or several: `Multi_Query`,
  `RAG_Fusion`, `Step_Back_Prompting`, `HyDE`.
- **Decomposition** — split one complex question into simpler sub-questions answered (and
  retrieved) independently, then combined: `Decomposition`.
- **Routing** — send the query to the *right* retriever/index/data source instead of always
  querying the same one: `Routing_LLM_Classifier`, `Semantic_Routing`, `Self_Querying_Retrieval`.

## Which RAG Stage Is This?

**Retrieval stage** — every technique in this folder operates on the *query*, before or as
part of the similarity search that fetches context for generation:

| Stage | What happens | Where it shows up here |
|---|---|---|
| **Indexing** (build-time, before any query exists) | Chunk documents, embed them, write them to a vector store | `Naive_RAG.ipynb` / `Naive_RAG_Alt.ipynb` set up the baseline index everything else in this folder compares against — this is indexing, not query transformation, but it's the starting point the rest builds on. |
| **Retrieval** (query-time, before generation) | Transform the incoming query, then search the index with the transformed version(s) | `Multi_Query`, `RAG_Fusion`, `Decomposition`, `Step_Back_Prompting`, `HyDE`, `Self_Querying_Retrieval`, `Routing_LLM_Classifier`, `Semantic_Routing` — all of them operate on the **query**, before or as part of the similarity search. |
| **Generation** (LLM synthesizes the answer) | Not this folder's concern | Query transformation's whole job is to hand generation better context — it doesn't touch generation itself. |

> **Note:** Two indexing-stage techniques (`Multi_Representation_Indexing`,
> `Parent_Document_Retrieval`) and one post-retrieval refinement technique
> (`CrossEncoder_Reranking`) used to live in this folder despite not actually transforming the
> query. They've been split out to
> [`../Indexing_Techniques/`](../Indexing_Techniques/) and
> [`../Post_Retrieval_Techniques/`](../Post_Retrieval_Techniques/) respectively, each with its
> own stage breakdown for exactly why it doesn't belong here.

## Notebooks

| Notebook | Topic |
|---|---|
| `Naive_RAG.ipynb` / `Naive_RAG_Alt.ipynb` | Baseline naive RAG (two variants from the source repo) |
| `Multi_Query.ipynb` | Multi-query retrieval |
| `RAG_Fusion.ipynb` | RAG-Fusion |
| `Decomposition.ipynb` | Query decomposition |
| `Step_Back_Prompting.ipynb` | Step-back prompting |
| `HyDE.ipynb` | Hypothetical Document Embeddings |
| `Self_Querying_Retrieval.ipynb` | Self-querying retrieval |
| `Routing_LLM_Classifier.ipynb`, `Semantic_Routing.ipynb` | Query routing |

See also: [`../Indexing_Techniques/`](../Indexing_Techniques/) for multi-representation
indexing and parent-document retrieval, and
[`../Post_Retrieval_Techniques/`](../Post_Retrieval_Techniques/) for cross-encoder reranking.
