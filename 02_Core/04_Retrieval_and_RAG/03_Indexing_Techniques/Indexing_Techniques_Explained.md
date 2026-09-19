# Indexing Techniques: Multi-Representation Indexing vs. Parent Document Retrieval

This folder has two notebooks that solve the **same underlying problem** in **different ways**:
plain RAG embeds and searches the exact same chunk it later feeds to the LLM, and that's a bad
compromise. A chunk small enough to embed precisely rarely has enough context to answer with; a
chunk large enough to carry context rarely embeds precisely enough to be found.

Both techniques fix this by **decoupling what you search against from what you return** — but
they split the two representations along different axes.

## The Core Idea, Side by Side

| | **Multi-Representation Indexing** | **Parent Document Retrieval** |
|---|---|---|
| Notebook | `Multi_Representation_Indexing.ipynb` | `Parent_Document_Retrieval.ipynb` |
| What's embedded (searched) | An **LLM-generated summary** of the document | A **small child chunk** (plain text split, no LLM) |
| What's returned (fed to LLM) | The **full original document** | The **larger parent chunk** (or whole document) the child came from |
| How the two are linked | Shared `doc_id` in the summary's metadata | Shared `parent_id` in each child chunk's metadata |
| Vectorstore | `Chroma`, embedding *summaries* | `Chroma`, embedding *child chunks* |
| Docstore | `InMemoryByteStore` (raw bytes/full docs) | `InMemoryStore` (parent chunk objects) |
| Retriever | `MultiVectorRetriever` | `ParentDocumentRetriever` |
| Cost to build the index | Higher — one LLM call per document to summarize | Lower — pure text splitting, no LLM calls |
| Representation semantics | *Compressed meaning* (summary) | *Same text, different granularity* (chunk vs. parent) |

## How Each One Actually Works

### Multi-Representation Indexing
1. Split source documents into chunks.
2. Ask an LLM to **summarize** each chunk.
3. Embed the **summaries** into the vectorstore; store the **full chunk text** in the
   docstore — both tagged with the same `doc_id`.
4. At query time: similarity search runs over summary embeddings (short, semantically dense,
   easy to match against a short query) → the matched summary's `doc_id` is used to fetch and
   return the **full original chunk** from the docstore.

### Parent Document Retrieval
1. Split source documents into **parent** chunks (large, or the whole document if no
   `parent_splitter` is given).
2. Split each parent further into **child** chunks (small).
3. Embed the **child chunks** into the vectorstore, each tagged with its parent's `parent_id`;
   store the **parent chunks** in the docstore.
4. At query time: similarity search runs over child-chunk embeddings (small, specific, easy to
   match precisely) → the matched child's `parent_id` is used to fetch and return the **larger
   parent chunk** from the docstore.

## Key Difference: Why Retrieval Precision Differs

- Multi-Representation Indexing trades an **LLM call per document** for a **semantically
  compressed, meaning-focused** search key — a summary can match a query even when the query
  uses different words than the source text, because the LLM already distilled *what the text
  means*.
- Parent Document Retrieval trades **no LLM cost** for **finer-grained, literal** search
  precision — a small child chunk matches a query more sharply when the query's wording is
  close to the source text, because it's a direct (unsummarized) fragment.

In short: **Multi-Representation** compresses *meaning*; **Parent Document Retrieval**
compresses *scope* (how much text one embedding covers).

## When to Use Which

### Reach for Multi-Representation Indexing when:
- Your documents are long, dense, or narratively structured (reports, articles, transcripts)
  where a short summary still captures the gist.
- Queries are phrased very differently from the source text (paraphrased, conversational, or
  keyword-sparse questions) — summary embeddings generalize better than raw-text embeddings.
- You can afford one LLM call per document at index time (and documents don't change often, so
  that cost is paid once).
- You want the retriever to hand back a *complete* unit of context (e.g. a whole document or
  section) rather than an arbitrary chunk boundary.

**Typical use cases:** long-form knowledge bases, internal wikis, research papers, meeting
transcripts, customer support articles — anywhere "what is this document broadly about" is a
good proxy for "is this the document the user needs."

### Reach for Parent Document Retrieval when:
- You want retrieval precision on **specific facts, numbers, or exact phrases** that a summary
  would blur or drop.
- You can't afford (or don't want) an LLM call per document just to build the index — this is
  pure text splitting, so it's cheap and fast to (re)build.
- Documents are frequently updated and you need to re-index often — no summarization latency.
- You still want the LLM to see enough surrounding context to answer well, not just the
  matched sentence/paragraph in isolation.

**Typical use cases:** technical documentation, API references, legal/contract text, code
documentation, FAQs with precise answers — anywhere the exact wording matters and re-indexing
speed/cost matters.

### Can you combine them?
Yes — nothing stops you from summarizing parent chunks *and* further splitting them into child
chunks; they attack orthogonal axes (meaning-compression vs. granularity). Most teams start
with whichever one directly fixes their current retrieval failure mode (missed paraphrased
queries → try Multi-Representation; missed precise facts buried in long context → try Parent
Document Retrieval) rather than combining both up front.

## See Also
- [`README.md`](README.md) — where this folder sits in the RAG pipeline (indexing stage) and
  why it was split out from `Query_Transformation_Techniques/`.
- [`Multi_Representation_Indexing.ipynb`](Multi_Representation_Indexing.ipynb) — runnable
  implementation with an in-notebook diagram.
- [`Parent_Document_Retrieval.ipynb`](Parent_Document_Retrieval.ipynb) — runnable
  implementation with an in-notebook diagram.
