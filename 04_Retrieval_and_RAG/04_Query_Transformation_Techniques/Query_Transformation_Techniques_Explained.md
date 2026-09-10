# Query Transformation Techniques

This folder holds eight techniques that all attack the same
weak point in a RAG pipeline: **the raw user query is often a bad search query.** It may be
ambiguous, too broad or too narrow, worded very differently from how the answer appears in the
source documents, or actually bundle several sub-questions into one sentence. Query
transformation techniques rewrite, expand, decompose, or route the query **before** — or
instead of — searching with it verbatim, so the retriever pulls back more relevant, more
complete context.

Unlike the indexing techniques (`../03_Indexing_Techniques/`), which change *what gets built
into the index* at index time, everything here operates at **query time**, on the *same* index
a naive pipeline would use.

## The Three Families

| Family | What it does | Notebooks |
|---|---|---|
| **Rewriting / expansion** | Turn one query into a better one, or several | `Multi_Query`, `RAG_Fusion`, `Step_Back_Prompting`, `HyDE` |
| **Decomposition** | Split one complex question into simpler sub-questions, answer each, then combine | `Decomposition` |
| **Routing** | Send the query to the *right* retriever/index/prompt instead of always using the same one | `Routing_LLM_Classifier`, `Semantic_Routing`, `Self_Querying_Retrieval` |

## Technique-by-Technique

### Multi-Query
Ask an LLM to rewrite the user's question into several **differently-phrased versions** of the
same question, run similarity search for each, and take the union of retrieved documents.
Different phrasings surface different relevant chunks that a single query wording would miss.
- **Use when:** queries are short/ambiguous and your corpus uses varied terminology for the
  same concept.

### RAG-Fusion
Like Multi-Query — generate several query variations — but instead of a plain union, combine
the *ranked* result lists from each query using **Reciprocal Rank Fusion (RRF)**, so documents
that rank well across multiple query variations bubble to the top.
- **Use when:** you want Multi-Query's recall benefit but also want a principled way to
  re-rank/merge multiple retrieval passes rather than a flat union.

### Decomposition
Break one complex, multi-part question into **simpler sub-questions**, retrieve and answer each
sub-question independently, then merge the sub-answers into a final answer to the original
question.
- **Use when:** users ask compound or multi-hop questions ("compare X and Y and explain why Z
  follows") that no single retrieval pass can satisfy.

### Step-Back Prompting
Prompt the LLM to first ask a more **general/abstract "step-back" question**, retrieve context
for that broader question, and use it alongside the original query's context to answer — the
idea being that grounding in the broader concept improves reasoning on the specific question.
- **Use when:** questions require background/principle-level context the specific phrasing
  alone wouldn't retrieve (e.g. "why does X happen" needing the underlying general mechanism).

### HyDE (Hypothetical Document Embeddings)
Instead of embedding the user's question, ask an LLM to **generate a hypothetical answer
document** to that question, and embed *that* for similarity search. A well-formed hypothetical
answer is closer in embedding space to real answer documents than a short question is.
- **Use when:** the query is short and question-shaped but the source documents are long,
  answer-shaped prose — the vocabulary/style gap between "question" and "answer" hurts naive
  retrieval.

### Self-Querying Retrieval
Have an LLM parse the user's natural-language query into a **structured filter + semantic
query** (e.g. "cheap sci-fi movies from the 90s" → genre=sci-fi, price<X, year in 1990s +
semantic search on the remaining text), then apply both the metadata filter and the vector
search together.
- **Use when:** your documents have rich, filterable metadata (dates, categories, prices, tags)
  and users phrase filter conditions in natural language rather than a form/facet UI.

### Routing (LLM Classifier)
Use an LLM as a **classifier** that reads the query and picks which prompt/chain/retriever to
route it to (e.g. "physics question" vs. "math question" → different expert prompts).
- **Use when:** you have several distinct domains/data sources/prompt strategies and need an
  LLM's judgment to disambiguate which one a query belongs to.

### Semantic Routing
Same routing goal, but decided by **embedding similarity** instead of an LLM call: embed the
query and each candidate route's description, and pick the route whose embedding is closest.
- **Use when:** you want routing decisions that are cheaper/faster than an LLM classification
  call, and your routes are well-separated in embedding space.

## Which RAG Stage Is This?

**Retrieval stage** — every technique here transforms the *query*, before or as part of the
similarity search, using an index that's already built. (That baseline index is built in
`RAG_Curriculum/01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb`, which isn't itself query transformation —
see the folder's `README.md` for the full stage breakdown.)

## Quick Decision Guide

| Symptom | Try |
|---|---|
| Query is short/ambiguous, corpus uses varied wording | Multi-Query or RAG-Fusion |
| Above, but you want principled re-ranking across variations | RAG-Fusion |
| Question is really several questions bundled together | Decomposition |
| Question needs broader/background context to reason about | Step-Back Prompting |
| Query is question-shaped, documents are answer-shaped prose | HyDE |
| Query mixes a semantic ask with filterable attributes | Self-Querying Retrieval |
| Multiple distinct domains/sources need disambiguation, LLM judgment OK | Routing (LLM Classifier) |
| Same, but need it cheap/fast without an LLM call | Semantic Routing |

## See Also
- [`README.md`](README.md) — where this folder sits in the RAG pipeline and its merge history.
- [`../03_Indexing_Techniques/`](../03_Indexing_Techniques/) — the sibling folder for
  *indexing*-stage techniques (multi-representation indexing, parent-document retrieval),
  including its own written comparison doc.
- [`../05_Post_Retrieval_Techniques/`](../05_Post_Retrieval_Techniques/) — cross-encoder
  reranking, the post-retrieval-stage counterpart to these query-time techniques.
