%%markdown
# Embeddings and Model Selection

Lesson 01 used an embedding model as a black box: text went in, 1536 numbers came out, similar things scored high. That was enough to build a pipeline. It is not enough to make the decisions this stage actually demands.

The embedding model is the **single least reversible choice in a RAG system**. Changing it invalidates every vector you have stored, which means re-embedding the entire corpus — the one operation that scales with corpus size and costs real money. Chunk sizes can be retuned, prompts rewritten, retrievers swapped. The embedding model is the thing you are married to.

This lesson is about making that choice deliberately, and about the three operational concerns that follow from it: dimensions, caching, and the compatibility rule you cannot break.

## Learning objectives

By the end of this notebook you will be able to:

1. **Use the right method for the job** — `embed_query` vs `embed_documents` — and explain why the API separates them.
2. **Read a vector**: dimensions, magnitude, and whether your model returns normalized output — and what that implies for your choice of similarity metric.
3. **Trade dimensions against cost** using the `dimensions` parameter, and *measure* the quality you give up rather than guessing.
4. **Cache embeddings** so re-running a pipeline does not re-pay for text you have already embedded.
5. **Compare candidate models empirically** on a small labelled retrieval set, instead of choosing by leaderboard.
6. **State and defend the compatibility rule** — the same model must embed documents and queries — and recognise the failure it produces when broken.

%%markdown
## Prerequisites

**Lessons**

- `01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb` — cosine similarity and the role of embeddings in the pipeline.
- `01_Foundations/02_Document_Loading_and_Metadata.ipynb` — for the distinction between content (embedded) and metadata (not).

**Packages**

`langchain-openai`, `langchain-core`, `langchain-classic`, `numpy`, `pandas`.

`CacheBackedEmbeddings` and `LocalFileStore` live in `langchain_classic` on LangChain 1.x, not in `langchain` — Part 4 explains.

Part 7 (local models) additionally needs `langchain-huggingface`, `sentence-transformers` and `torch` — this repository's `hf` extra, a multi-gigabyte download. **That section is off by default and is not required.**

**Services**

`OPENAI_API_KEY` for `text-embedding-3-small` and `text-embedding-3-large`.

**Cost**

Embedding models are cheap — this notebook embeds roughly 60 short strings across several models. Measured token usage is reported by the notebook itself in Part 6.

%%markdown
## Provenance and runtime status

Consolidated from:

| Source | Contribution |
| --- | --- |
| `04_Retrieval_and_RAG/RAG_Production_Course/04_embeddings_deep.ipynb` | The `embed_query` / `embed_documents` distinction, batching, and the caching section. |
| `04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/1. Embedding_Models.ipynb` | Dimension discussion, the HuggingFace alternative, and the "build a small search engine" framing that Part 6 generalizes into a measured comparison. |
| `04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/4. Embedding_Basics_Alt.ipynb` | Conceptual introduction and cosine-similarity interpretation (largely already covered in lesson 01, so used sparingly here). |
| `04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/5. Openaiembeddings_Alt.ipynb` | Batch processing and model-comparison table. |
| `04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/6. Compare_Embedding_Models.ipynb` | The idea of evaluating candidate models against each other — reworked, since the original depends on Databricks Vector Search and MLflow and cannot run locally. |

**Deliberately not carried:** the Databricks-specific vector-search plumbing from `6. Compare_Embedding_Models.ipynb` (that belongs to `10_Production_RAG/03_Governed_Databricks_RAG.ipynb`), and the general "what is an embedding" introduction, which lesson 01 already covers.

**Runtime status:** see `RAG_MIGRATION_MANIFEST.md` for the authoritative validation record.

%%markdown
---

## Part 0 — Setup

%%code
# ============ BOOTSTRAP: DEPTH-INDEPENDENT PATHS ============
import pathlib
import sys

_p = pathlib.Path.cwd()
while not (_p / "RAG_Curriculum").is_dir() and _p != _p.parent:
    _p = _p.parent
sys.path.insert(0, str(_p / "RAG_Curriculum" / "_support" / "helpers"))

from rag_paths import repo_root

%%code
# ============ IMPORTS AND ENVIRONMENT ============
import time

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings

load_dotenv(repo_root() / ".env")

# Model used throughout unless a cell says otherwise.
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
print("Ready:", embeddings.model)

%%markdown
---

## Part 1 — Two methods, and why they are separate

Every LangChain embedding object exposes two methods:

| Method | Input | Returns | Used at |
| --- | --- | --- | --- |
| `embed_documents(texts)` | a list of strings | a list of vectors | **Index time** — once, over the corpus |
| `embed_query(text)` | one string | one vector | **Query time** — on every request |

They look redundant. They are not, for two reasons.

**Batching.** `embed_documents` sends many texts in one HTTP request. Calling `embed_query` in a loop sends one request per text, and the round-trip dominates — the difference on a real corpus is minutes versus hours.

**Asymmetry.** Some embedding models are *asymmetric*: they are trained so that short questions and long passages land near each other, and they apply different internal prefixes to each. For those models the two methods genuinely produce different vectors for the same input. OpenAI's models are symmetric, so the outputs match — but code written against the abstraction stays correct when you swap in a model that is not.

%%code
# ============ BATCH VS SINGLE: THE COST OF THE LOOP ============
corpus = [
    "The mitochondrion is the powerhouse of the cell.",
    "Python's GIL prevents true parallel execution of bytecode in threads.",
    "The Treaty of Westphalia was signed in 1648.",
    "Sourdough fermentation relies on wild yeast and lactic acid bacteria.",
    "TCP guarantees ordered, reliable delivery; UDP does not.",
    "The Baroque period in music runs roughly from 1600 to 1750.",
]

t0 = time.perf_counter()
batched = embeddings.embed_documents(corpus)          # ONE request
t_batch = time.perf_counter() - t0

t0 = time.perf_counter()
looped = [embeddings.embed_query(t) for t in corpus]  # SIX requests
t_loop = time.perf_counter() - t0

print(f"embed_documents (1 request) : {t_batch:.2f}s")
print(f"embed_query x{len(corpus)} ({len(corpus)} requests) : {t_loop:.2f}s")
print(f"speedup: {t_loop / t_batch:.1f}x on just {len(corpus)} texts\n")
# Are the two paths equivalent? Compare - but do not expect bit-identical
# floats, since a batched request and a single request take different code
# paths through the server.
delta = np.abs(np.array(batched[0]) - np.array(looped[0])).max()
print(f"max per-component difference : {delta:.2e}")
print(f"cosine between the two       : {float(np.dot(batched[0], looped[0])):.8f}")
print()
print("Semantically identical (cosine ~1.0), but NOT bit-identical. That tiny")
print("float difference is numerical noise, not asymmetry - OpenAI's models are")
print("symmetric. For an asymmetric model the cosine here would be visibly < 1.")

%%markdown
---

## Part 2 — Reading a vector

Two properties of the returned vector determine which similarity metric is correct for your store: its **dimensionality** and its **magnitude**.

%%code
# ============ ANATOMY OF AN EMBEDDING ============
v = np.array(embeddings.embed_query("How do I reset my password?"))

print(f"dimensions : {v.shape[0]}")
print(f"dtype      : {v.dtype}")
print(f"L2 norm    : {np.linalg.norm(v):.6f}")
print(f"min / max  : {v.min():.4f} / {v.max():.4f}")
print(f"mean       : {v.mean():.6f}")
print(f"first 8    : {np.round(v[:8], 4)}")

%%markdown
**That L2 norm is the important line.** It is `1.0` to within float error — you will see something like `0.99976`, because the API returns rounded floats. OpenAI returns **unit-normalized** vectors: every component squared sums to one.

This has a concrete consequence. For unit vectors, cosine similarity and dot product are *the same number*, and Euclidean distance is a monotonic function of it. So for OpenAI embeddings the three metrics rank identically, and you can pick whichever your vector store computes fastest — usually dot product.

For a model that does **not** normalize, they diverge: dot product then rewards long documents simply for having larger vectors, which is a real and easily-missed retrieval bug. Check the norm before choosing a metric.

%%code
# ============ WHEN THE METRICS AGREE, AND WHEN THEY DO NOT ============
a = np.array(embeddings.embed_query("How do I reset my password?"))
b = np.array(embeddings.embed_query("I forgot my login credentials."))

cos = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
dot = float(a @ b)
euc = float(np.linalg.norm(a - b))

print("Normalized vectors (what OpenAI returns):")
print(f"  cosine     : {cos:.6f}")
print(f"  dot        : {dot:.6f}   <- identical to cosine")
print(f"  euclidean  : {euc:.6f}   <- sqrt(2 - 2*cosine) = "
      f"{np.sqrt(2 - 2 * cos):.6f}")

# Simulate an UN-normalized model by scaling one vector, as a long document
# would be under a model that encodes length into magnitude.
b_long = b * 3.0
print("\nAfter scaling one vector 3x (an un-normalized model):")
print(f"  cosine     : {float(a @ b_long / (np.linalg.norm(a) * np.linalg.norm(b_long))):.6f}   <- unchanged")
print(f"  dot        : {float(a @ b_long):.6f}   <- inflated 3x purely by magnitude")
print("\nCosine measures direction only. Dot product does not. With an")
print("un-normalized model, dot-product search quietly favours long documents.")

%%markdown
---

## Part 3 — Dimensions, and paying for them

Dimensions are not free. Every dimension costs storage in your vector index, memory when it is loaded, and time in every similarity computation — on **every query, forever**. A 3072-dimension index is twice the size and roughly twice the search cost of a 1536-dimension one.

OpenAI's `text-embedding-3-*` models are trained with **Matryoshka representation learning**: information is front-loaded, so the vector can be truncated and re-normalized while remaining useful. The `dimensions` parameter does this server-side.

The question is never "are shorter vectors worse?" — they are. It is **"how much worse, on my data, for the cost I save?"** That is measurable, so measure it.

%%code
# ============ MEASURE THE COST OF TRUNCATION ============
# A small labelled retrieval set: each query has exactly one correct document.
docs = [
    "To reset your password, visit the account settings page and click 'Forgot password'.",
    "Our refund policy allows returns within 30 days of purchase with a receipt.",
    "Standard shipping takes 5-7 business days; express shipping arrives next day.",
    "The premium tier includes unlimited storage and priority customer support.",
    "You can cancel your subscription at any time from the billing dashboard.",
    "Gift cards are non-refundable and expire two years after the purchase date.",
]
queries = [
    ("I can't log in, forgot my credentials", 0),
    ("how long do I have to return something", 1),
    ("when will my order arrive", 2),
    ("what do I get if I upgrade", 3),
    ("how do I stop being billed", 4),
    ("do gift cards expire", 5),
]


def recall_at_1(dims=None, model="text-embedding-3-small"):
    """Return (recall@1, margin, dimensions) for one embedding configuration.

    `margin` is the mean gap between the correct document's similarity and the
    best WRONG document's similarity. Recall@1 is a step function that saturates
    at 1.0 on an easy corpus; margin is continuous and keeps degrading, so it
    reveals damage long before recall does.
    """
    kw = {"model": model}
    if dims:
        kw["dimensions"] = dims
    emb = OpenAIEmbeddings(**kw)

    D = np.array(emb.embed_documents(docs))                     # index
    Q = np.array(emb.embed_documents([q for q, _ in queries]))  # queries, batched
    sims = Q @ D.T          # unit vectors, so dot product IS cosine

    hits, margins = 0, []
    for row, (_, gold) in zip(sims, queries):
        hits += int(row.argmax() == gold)
        margins.append(row[gold] - np.max(np.delete(row, gold)))
    return hits / len(queries), float(np.mean(margins)), D.shape[1]


rows = []
for dims in (None, 512, 256, 128, 64, 32):
    score, margin, actual = recall_at_1(dims)
    rows.append({"dimensions": actual, "recall@1": score,
                 "margin": round(margin, 4),
                 "index_size": f"{actual / 1536:.0%}"})

print(pd.DataFrame(rows).to_string(index=False))
print("\nrecall@1 stays perfect - six well-separated documents are easy.")
print("`margin` is the honest signal: watch the correct answer's lead over the")
print("best wrong answer shrink as dimensions fall. On a large corpus full of")
print("near-duplicates, that shrinking margin is exactly where recall breaks.")

%%markdown
Two cautions about that table.

**Six queries is not an evaluation.** It is a demonstration of the method. A real decision needs hundreds of labelled queries drawn from actual user traffic, and `recall@1` is the crudest possible metric — as the table shows, it saturates immediately and then tells you nothing, which is why `margin` is there. Proper retrieval measurement is `06_Evaluation/01_Deterministic_Retrieval_Metrics.ipynb`.

**Small corpora flatter every model.** With six well-separated documents almost anything scores perfectly. Truncation damage shows up when you have hundreds of thousands of chunks and near-duplicates that need to be told apart — exactly the case a toy corpus cannot reproduce.

%%markdown
---

## Part 4 — Caching: the cost you pay twice

Re-running a notebook re-embeds everything. Re-ingesting a corpus after changing an unrelated setting re-embeds everything. This is the quiet, recurring cost of RAG development, and it is almost entirely avoidable.

`CacheBackedEmbeddings` wraps any embedding model with a key-value store. Text already seen returns from the store; only new text hits the API.

%%code
# ============ CACHE-BACKED EMBEDDINGS ============
import tempfile

# LangChain 1.x: the caching wrapper moved out of `langchain` into
# `langchain_classic` along with the other pre-1.x abstractions.
#   0.x: from langchain.embeddings import CacheBackedEmbeddings
#   1.x: from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_core.stores import InMemoryByteStore

store = InMemoryByteStore()          # LocalFileStore(path) to persist across sessions
cached = CacheBackedEmbeddings.from_bytes_store(
    embeddings,
    store,
    namespace=embeddings.model,      # CRITICAL - see the note below
)

t0 = time.perf_counter()
cached.embed_documents(corpus)
cold = time.perf_counter() - t0

t0 = time.perf_counter()
cached.embed_documents(corpus)       # identical input, second time
warm = time.perf_counter() - t0

print(f"cold (API call)  : {cold:.3f}s")
print(f"warm (from cache): {warm:.4f}s")
print(f"speedup          : {cold / max(warm, 1e-9):.0f}x, and the warm run cost nothing")
print(f"\ncache entries    : {len(list(store.yield_keys()))}")

%%markdown
**`namespace` is not optional.** The cache key is derived from the text. Without a namespace, switching from `text-embedding-3-small` to `-large` returns the *small* model's cached vectors for text it has seen — silently, with no error, producing an index that mixes two incompatible vector spaces.

Always set `namespace` to something that identifies the model *and* its configuration, including `dimensions` if you set it.

Use `LocalFileStore` rather than `InMemoryByteStore` for anything beyond a single session:

```python
from langchain_classic.storage import LocalFileStore   # 0.x: langchain.storage
store = LocalFileStore("./.embedding_cache/")
```

Note the import path again. `langchain.storage` does not exist on LangChain 1.x either — like `langchain.chains` and `langchain.prompts` in lesson 01, it moved to `langchain_classic`. Any 0.x-era tutorial you follow will need the same substitution, and it fails with `ModuleNotFoundError` rather than a deprecation warning.

%%markdown
---

## Part 5 — Choosing a model

Leaderboards like MTEB are a starting point for a shortlist, not an answer. They measure average performance across benchmark datasets that are not your data, with queries that are not your users' queries.

Score your shortlist on your own labelled set. The infrastructure for that is the `recall_at_1` function from Part 3 — the same function, pointed at different models.

%%code
# ============ COMPARE CANDIDATE MODELS ON THE SAME TASK ============
candidates = [
    ("text-embedding-3-small", None),
    ("text-embedding-3-small", 256),   # same model, cheaper index
    ("text-embedding-3-large", None),
    ("text-embedding-3-large", 1536),  # large model truncated to small's size
]

rows = []
for model, dims in candidates:
    t0 = time.perf_counter()
    score, margin, actual = recall_at_1(dims=dims, model=model)
    elapsed = time.perf_counter() - t0
    rows.append({
        "model": model.replace("text-embedding-", ""),
        "dims": actual,
        "recall@1": score,
        "margin": round(margin, 4),
        "seconds": round(elapsed, 2),
    })

df = pd.DataFrame(rows)
print(df.to_string(index=False))
print("\nCompare on `margin`, not `recall@1` - recall is saturated here. The")
print("interesting row is `3-large` truncated to 1536: a stronger model at")
print("the same index cost as the small one. That trade is invisible on a")
print("leaderboard and only shows up when you measure the axes YOU care about.")

%%markdown
### The axes that actually decide it

| Axis | Why it matters | How to find out |
| --- | --- | --- |
| **Retrieval quality on your data** | The only quality that counts | Labelled set + `recall@k` / nDCG |
| **Dimensions** | Storage, memory and per-query search cost, forever | Model spec; tune with `dimensions` |
| **Cost per token** | Scales with corpus size at index time, with traffic at query time | Provider pricing |
| **Latency** | Query-time embedding is on the user's critical path | Measure it, as above |
| **Max input length** | Longer limits allow larger chunks | Model spec |
| **Multilingual** | A monolingual model fails silently on other languages | Test on your actual languages |
| **Self-hostable** | Data residency, air-gapped deployment, no per-call cost | See Part 6 |
| **Stability** | A provider deprecating a model forces a full re-index | Provider policy |

That last row is underrated. A hosted model can be deprecated or silently updated; both force you to re-embed everything. Self-hosting trades that risk for operational burden.

%%markdown
---

## Part 6 — Local models *(optional — requires the `hf` extra)*

Running the embedding model yourself removes per-call cost and keeps data on your machine — decisive when documents cannot leave your network. You pay in operational complexity, and in a multi-gigabyte dependency tree.

This section is **off by default**. It needs `langchain-huggingface`, `sentence-transformers` and `torch` (this repository's `hf` extra), plus a model download on first run.

%%code
# ============ LOCAL EMBEDDINGS (OPTIONAL) ============
RUN_LOCAL_MODEL = False   # set True after: uv pip install -e ".[hf]"

if RUN_LOCAL_MODEL:
    from langchain_huggingface import HuggingFaceEmbeddings

    local = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",   # 384 dims, ~80MB
        encode_kwargs={"normalize_embeddings": True},          # NOT the default - see below
    )
    v_local = np.array(local.embed_query("How do I reset my password?"))
    print(f"dimensions: {v_local.shape[0]}")
    print(f"L2 norm   : {np.linalg.norm(v_local):.6f}")
else:
    print("Local model disabled. Set RUN_LOCAL_MODEL = True after installing the hf extra.")
    print()
    print("Two things to know before you do:")
    print("  1. sentence-transformers does NOT normalize by default. Pass")
    print("     encode_kwargs={'normalize_embeddings': True}, or use cosine")
    print("     rather than dot product - otherwise long documents win unfairly.")
    print("  2. all-MiniLM-L6-v2 is 384 dimensions vs OpenAI's 1536. Smaller,")
    print("     faster, free, and measurably weaker. Score it on your own set")
    print("     with the recall_at_1 function above before deciding.")

%%markdown
| | Hosted API | Self-hosted |
| --- | --- | --- |
| Cost | Per token, forever | Hardware + operations |
| Data | Leaves your network | Stays put |
| Latency | Network round trip | Local compute (GPU helps a lot) |
| Quality | Generally stronger at a given size | Improving fast; the gap is narrowing |
| Ops burden | None | Versioning, serving, scaling, GPU capacity |
| Deprecation risk | Provider can retire the model | You control it |

%%markdown
---

## Part 7 — The rule you cannot break

**The model that embeds your documents must be the model that embeds your queries.**

Lesson 01 stated this. Here is what breaking it actually looks like — because it does not raise an error. It just returns bad results, forever, and it looks like a retrieval-quality problem rather than a configuration bug.

%%code
# ============ MISMATCHED MODELS: SILENT, NOT LOUD ============
small = OpenAIEmbeddings(model="text-embedding-3-small")
large = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=1536)  # SAME dims

# Index with one model, query with the other. Dimensions match, so nothing errors.
D = np.array(small.embed_documents(docs))
Q_matched = np.array(small.embed_documents([q for q, _ in queries]))
Q_mixed = np.array(large.embed_documents([q for q, _ in queries]))

for label, Q in (("matched (small/small)", Q_matched), ("MIXED (small/large)", Q_mixed)):
    sims = Q @ D.T
    top1 = sims.argmax(axis=1)
    hits = sum(int(p == g) for p, (_, g) in zip(top1, queries))
    print(f"{label:24s} recall@1 = {hits}/{len(queries)}   "
          f"top-1 similarity avg = {sims.max(axis=1).mean():.4f}")

print("\nNo exception. No warning. Same 1536 dimensions on both sides.")
print("Just quietly meaningless similarity scores - the two models place text")
print("in unrelated coordinate systems that happen to have the same shape.")

%%markdown
Notice the average top-1 similarity in the mixed case: it collapses toward zero, because the two vector spaces are effectively unrelated. **That number is your detector.** If your best retrieval scores sit near zero on queries that obviously have answers in the corpus, suspect a model mismatch before you touch anything else.

The three ways this happens in practice:

1. **Config drift** — the indexing job and the query service read the model name from different places, and one gets updated.
2. **An unnamespaced cache** — as in Part 4.
3. **A silent provider-side model update** — pinned model *names* are not always pinned model *weights*.

The defence is to record the embedding model and its dimensions in your index metadata, and check them at query time.

%%markdown
---

## Limitations and tradeoffs

**Everything here was measured on six documents.** That is enough to demonstrate a method and nowhere near enough to choose a model. Treat the numbers as illustrations of the procedure, not as results.

**Embeddings encode semantic similarity, not truth or relevance.** "The drug is effective" and "The drug is not effective" embed close together — they are about the same topic. Retrieval will happily return the opposite of what was asked. Negation, numeric comparison, and exact identifiers are all weak points; hybrid search (`03_Retrieval/03_Hybrid_Search.ipynb`) exists largely because of them.

**Chunk length interacts with embedding quality.** A single vector for a long passage averages away its specifics. This is why chunk size is a tuning parameter, not a formatting detail — `02_Chunking_and_Indexing/04_Choosing_Chunk_Size.ipynb`.

**Domain mismatch is real.** General-purpose models underperform on specialized vocabulary — legal, clinical, or internal jargon. Fine-tuned or domain-specific embeddings can help, at the cost of another thing to maintain.

**No latency or cost numbers here are benchmarks.** They are single measurements on one machine over one network, and they vary with load.

%%markdown
---

## Exercise

Build an `EmbeddingBench` that scores several configurations on a labelled set and reports quality alongside cost, so the trade-off is visible in one table.

%%code
# ============ EXERCISE: A MODEL SELECTION HARNESS ============
class EmbeddingBench:
    """Score embedding configurations on a labelled retrieval set."""

    def __init__(self, documents: list[str], labelled: list[tuple[str, int]]):
        self.documents = documents
        self.labelled = labelled

    def score(self, model: str, dimensions: int | None = None, k: int = 1) -> dict:
        kw = {"model": model}
        if dimensions:
            kw["dimensions"] = dimensions
        emb = OpenAIEmbeddings(**kw)

        t0 = time.perf_counter()
        D = np.array(emb.embed_documents(self.documents))
        index_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        Q = np.array(emb.embed_documents([q for q, _ in self.labelled]))
        query_time = (time.perf_counter() - t0) / len(self.labelled)

        # Unit vectors -> dot product is cosine. Top-k by score.
        ranked = np.argsort(-(Q @ D.T), axis=1)[:, :k]
        hits = sum(int(gold in row) for row, (_, gold) in zip(ranked, self.labelled))

        return {
            "model": model.replace("text-embedding-", ""),
            "dims": D.shape[1],
            f"recall@{k}": round(hits / len(self.labelled), 3),
            "index_s": round(index_time, 2),
            "query_ms": round(query_time * 1000, 1),
        }

    def compare(self, configs: list[tuple[str, int | None]], k: int = 1) -> pd.DataFrame:
        return pd.DataFrame([self.score(m, d, k) for m, d in configs])

    # TODO 1: add recall@k for k > 1 and report both. A model that is weak at
    #         k=1 but strong at k=5 is a fine choice IF you rerank afterwards
    #         (see 03_Retrieval/05). Does that change your ranking?
    #
    # TODO 2: add estimated index cost. Count tokens with tiktoken, multiply by
    #         the model's per-token price. At what corpus size does the cheaper
    #         model's saving outweigh its lower recall?
    #
    # TODO 3: add a "hard negatives" section to the labelled set - documents
    #         that are topically close to a query but do NOT answer it. This is
    #         where models actually separate, and where a 6-document toy set
    #         tells you nothing.


bench = EmbeddingBench(docs, queries)
print(bench.compare([
    ("text-embedding-3-small", None),
    ("text-embedding-3-small", 256),
    ("text-embedding-3-large", 1536),
]).to_string(index=False))

%%markdown
---

## Summary

**The embedding model is the least reversible decision in a RAG system.** Changing it means re-embedding the whole corpus. Choose it with measurement, not with a leaderboard.

**Two methods.** `embed_documents` for the corpus (batched, once); `embed_query` for requests (one at a time). They differ for asymmetric models even when they agree for OpenAI's.

**Check the norm.** OpenAI returns unit vectors, so cosine, dot and Euclidean rank identically — pick the fastest. Un-normalized models make dot product favour long documents.

**Dimensions are a real cost**, paid on every query forever. `dimensions=` truncates Matryoshka-trained models; measure what quality you lose rather than assuming.

**Cache embeddings, and always set `namespace`.** An unnamespaced cache returns one model's vectors for another model's request, silently.

**One model, both sides.** Mismatched index and query models raise nothing and return noise. The tell is top-1 similarity scores collapsing toward zero. Record the model and dimensions in your index metadata and verify at query time.

### Next lesson

`01_Foundations/04_Vector_Stores_and_Index_Operations.ipynb` — where these vectors live, and how to add, update, delete and filter them.

%%markdown
---

### Migration record

Canonical lesson for concept `RAG-F-03` (embeddings and model selection), Foundations batch. See `RAG_MIGRATION_MANIFEST.md` for per-source disposition. The Databricks Vector Search comparison harness from `6. Compare_Embedding_Models.ipynb` was deliberately not carried here; it belongs with the governed-deployment lesson in `10_Production_RAG/`.
