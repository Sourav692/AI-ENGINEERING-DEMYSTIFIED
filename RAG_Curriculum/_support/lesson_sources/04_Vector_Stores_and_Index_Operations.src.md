%%markdown
# Vector Stores and Index Operations

Lesson 01 called `FAISS.from_documents(chunks, embeddings)` and never touched the index again. That is fine for a demo and useless for a system that has to live: real corpora gain documents, lose documents, and correct documents, and every one of those operations has to happen without rebuilding from scratch.

This lesson treats the vector store as what it actually is — **a database** — and covers the operations that implies: insert, search, filter, update, delete, persist. It also covers the one that people assume exists and does not.

## Learning objectives

By the end of this notebook you will be able to:

1. **Perform the full CRUD cycle** against a vector store, and explain why **stable document IDs** are the prerequisite for all of it.
2. **Interpret a similarity score correctly**, knowing that "score" means different and incompatible things across backends.
3. **Filter by metadata**, and explain why pre-filtering and post-filtering give different results for the same query.
4. **Persist and reload** a store, including the collection-level identity that has to match.
5. **Use the retriever adapter** and understand exactly what it hides.
6. **Choose a backend** — in-memory, FAISS, Chroma, or a hosted service — against real requirements.

%%markdown
## Prerequisites

**Lessons**

- `01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb` — building and querying an index.
- `01_Foundations/02_Document_Loading_and_Metadata.ipynb` — metadata is what Part 4 filters on.
- `01_Foundations/03_Embeddings_and_Model_Selection.ipynb` — the model/index compatibility rule matters here.

**Packages**

`langchain-chroma`, `langchain-community` (for FAISS), `langchain-core`, `langchain-openai`, `faiss-cpu`, `pandas`.

**Services**

`OPENAI_API_KEY` for embeddings. No generation in this lesson — nothing here calls a chat model.

**Storage**

Every store is written to a temporary directory. Nothing in this notebook touches the checked-in indexes at `04_Retrieval_and_RAG/09_RAG_with_LangChain/index/` or `vs_db/`.

%%markdown
## Provenance and runtime status

Consolidated from:

| Source | Contribution |
| --- | --- |
| `04_Retrieval_and_RAG/RAG_Production_Course/05_vector_stores.ipynb` | Overall structure: Chroma basics, scored search, metadata filtering, retrievers, persistence. |
| `04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/2. Vector_Databases.ipynb` | The add / update / delete / reload cycle, which is the part most tutorials skip. |
| `04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/2.3. Othervectorstores.ipynb` | `InMemoryVectorStore` and the backend-comparison framing. |
| `04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/3. Retrievers.ipynb` | The `as_retriever` adapter and `search_kwargs` surface only. |

**Deliberately not carried:** the retrieval *strategies* in `3. Retrievers.ipynb` — MMR, score thresholds, multi-query, contextual compression, ensemble. Those change *how candidates are selected* and belong to `03_Retrieval/`, not to a lesson about the store itself. This lesson stops at the adapter boundary and names where each strategy lives.

The per-backend notebooks (`2.1. Chromadb`, `2.2. Faiss`, `2.4. Datastaxdb`, `2.5. PineconeVectorDB`) remain useful as setup references for those specific services; they are not duplicate lessons.

**Runtime status:** see `RAG_MIGRATION_MANIFEST.md`.

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
import shutil
import tempfile

import pandas as pd
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

load_dotenv(repo_root() / ".env")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

print("Ready:", embeddings.model)

%%code
# ============ A SMALL CORPUS WITH DELIBERATE METADATA ============
# Metadata here is not decoration - Part 4 filters on every one of these fields.
# Note the flat types: str / int / bool only. Chroma rejects lists and dicts.
docs = [
    Document(page_content="Employees may work remotely up to three days per week.",
             metadata={"dept": "HR", "year": 2026, "public": True, "doc": "remote-policy"}),
    Document(page_content="Expense reports must be submitted within 30 days of travel.",
             metadata={"dept": "Finance", "year": 2026, "public": True, "doc": "expense-policy"}),
    Document(page_content="The 2024 expense policy required submission within 14 days.",
             metadata={"dept": "Finance", "year": 2024, "public": False, "doc": "expense-policy-old"}),
    Document(page_content="Production deploys require two approvals and a rollback plan.",
             metadata={"dept": "Engineering", "year": 2026, "public": False, "doc": "deploy-runbook"}),
    Document(page_content="All laptops must have full-disk encryption enabled.",
             metadata={"dept": "Engineering", "year": 2026, "public": True, "doc": "security-baseline"}),
    Document(page_content="Parental leave is 16 weeks at full pay for all employees.",
             metadata={"dept": "HR", "year": 2026, "public": True, "doc": "leave-policy"}),
]

# STABLE IDS. This is the single most important decision in this notebook -
# see Part 5. Derive them from something durable about the document, never
# from list position or a random UUID generated at ingest time.
ids = [d.metadata["doc"] for d in docs]

print(pd.DataFrame([{**d.metadata, "id": i} for d, i in zip(docs, ids)]).to_string(index=False))

%%markdown
---

## Part 1 — What a vector store actually does

Strip away the API and a vector store does four things:

| Operation | What it does |
| --- | --- |
| **Add** | Embed text, store the vector alongside its text and metadata under an ID |
| **Search** | Embed a query, return the nearest stored vectors by some distance metric |
| **Filter** | Restrict the search to entries whose metadata matches an exact predicate |
| **Delete** | Remove entries by ID |

Notice what is *not* on that list: **update**. Almost no vector store has a true update — Part 5 covers what happens instead, and why it bites.

Notice also that a vector store holds **three things per entry**: the vector, the original text, and the metadata. It is not just an index of numbers; it is the system of record for your retrieved content.

%%code
# ============ ADD: BUILD AN INDEX WITH EXPLICIT IDS ============
persist_dir = tempfile.mkdtemp(prefix="rag_lesson04_")

store = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    ids=ids,                          # explicit and stable - not auto-generated
    collection_name="handbook",       # collections are namespaces within a store
    persist_directory=persist_dir,
)

print(f"collection : {store._collection.name}")
print(f"entries    : {store._collection.count()}")
print(f"on disk at : {persist_dir}")

%%code
# ============ INSPECT: WHAT IS ACTUALLY STORED ============
# .get() retrieves by ID without any similarity search - the plain database
# read. Useful for verification and for debugging "is that document even in
# the index?", which is the first question when retrieval misbehaves.
raw = store.get(ids=["remote-policy", "deploy-runbook"])

for i, (doc_id, text, meta) in enumerate(zip(raw["ids"], raw["documents"], raw["metadatas"])):
    print(f"[{doc_id}]")
    print(f"  text    : {text}")
    print(f"  metadata: {meta}")

print(f"\nKeys returned by .get(): {sorted(k for k, v in raw.items() if v is not None)}")
print("Note `embeddings` is omitted by default - ask for it with include=['embeddings'].")

%%markdown
---

## Part 2 — Search, and what the score means

The critical thing about similarity scores: **there is no shared convention.** The same query against the same documents produces numbers that mean opposite things depending on the backend.

%%code
# ============ SEARCH: WITH AND WITHOUT SCORES ============
query = "how many days can I work from home"

print("similarity_search (no scores):")
for d in store.similarity_search(query, k=3):
    print(f"  - {d.page_content[:60]}...")

print("\nsimilarity_search_with_score:")
for d, score in store.similarity_search_with_score(query, k=3):
    print(f"  {score:.4f}  {d.page_content[:56]}...")

%%code
# ============ THE SAME QUERY, A DIFFERENT BACKEND ============
# Build an equivalent FAISS index and compare the numbers directly.
faiss_store = FAISS.from_documents(docs, embeddings, ids=ids)

chroma_hits = store.similarity_search_with_score(query, k=3)
faiss_hits = faiss_store.similarity_search_with_score(query, k=3)

print(f"{'rank':>4}  {'Chroma':>10}  {'FAISS':>10}   document")
for i, ((cd, cs), (fd, fs)) in enumerate(zip(chroma_hits, faiss_hits), start=1):
    print(f"{i:>4}  {cs:>10.4f}  {fs:>10.4f}   {cd.page_content[:44]}...")

print("\nSame ranking, different numbers - and BOTH are distances here:")
print("lower is closer. Neither is a 0-1 'similarity' despite the method name.")
print("A threshold tuned on one backend is meaningless on the other.")

%%markdown
This is a genuine trap. `similarity_search_with_score` returns a **distance** for both Chroma and FAISS — lower is better — while `similarity_search_with_relevance_scores` returns a normalized 0–1 score where **higher** is better. Other backends return cosine similarity directly.

Three rules that follow:

1. **Never hardcode a score threshold** without checking what your backend returns. A `score > 0.8` filter can silently reject everything, or accept everything.
2. **Never compare scores across backends**, or across embedding models.
3. **Use scores for *ranking* and *relative* comparison**, which is always safe, rather than as an absolute measure of relevance.

To sanity-check a threshold, run known-good and known-irrelevant queries and look at the actual numbers, as lesson 01's Part 6 diagnostic did.

%%markdown
---

## Part 3 — Metadata filtering

Filtering is the operation that makes a vector store usable in a real application: multi-tenancy, recency, permissions, and department scoping are all metadata predicates.

Chroma uses a MongoDB-style operator syntax.

%%code
# ============ FILTER: EXACT MATCH AND OPERATORS ============
q = "what is the expense submission deadline"

print("Unfiltered - both the current AND the superseded 2024 policy:")
for d in store.similarity_search(q, k=3):
    print(f"  [{d.metadata['year']}] {d.page_content[:60]}...")

print("\nFiltered to the current year only:")
for d in store.similarity_search(q, k=3, filter={"year": 2026}):
    print(f"  [{d.metadata['year']}] {d.page_content[:60]}...")

print("\nOperators - $eq $ne $gt $gte $lt $lte $in $nin, plus $and / $or:")
for d in store.similarity_search(q, k=3, filter={"year": {"$gte": 2025}}):
    print(f"  [{d.metadata['year']}] {d.page_content[:60]}...")

%%code
# ============ FILTER: COMBINING PREDICATES ============
# $and / $or take a LIST of single-key conditions. A dict with two keys is
# an implicit AND in some backends and an error in others - be explicit.
results = store.similarity_search(
    "company policy",
    k=5,
    filter={"$and": [{"dept": {"$eq": "Engineering"}}, {"public": {"$eq": True}}]},
)
print("Engineering AND public:")
for d in results:
    print(f"  {d.metadata['dept']:<12} public={d.metadata['public']}  {d.page_content[:44]}...")

print("\nHR OR Finance:")
for d in store.similarity_search(
    "company policy", k=5, filter={"$or": [{"dept": "HR"}, {"dept": "Finance"}]}
):
    print(f"  {d.metadata['dept']:<12} {d.page_content[:44]}...")

%%markdown
### Pre-filter vs post-filter — and why `k` lies

There are two ways to combine a filter with a search, and they give different answers:

- **Pre-filtering** — restrict the candidate set, *then* find the nearest `k` within it. You always get `k` results if `k` documents match the filter.
- **Post-filtering** — find the nearest `k` overall, *then* discard those failing the filter. You often get fewer than `k`, sometimes zero.

Chroma and most modern stores pre-filter. But a **highly selective filter over a large index is expensive** either way, and some backends silently fall back to post-filtering behaviour under load or with certain index types.

The observable symptom of post-filtering is asking for `k=10` and receiving 3. That is not a bug to work around by raising `k` — it means your filter is being applied after retrieval, and documents that match your filter were never candidates.

%%code
# ============ DEMONSTRATING THE k CONTRACT ============
# Only two documents have dept="HR". Ask for five.
hits = store.similarity_search("policy", k=5, filter={"dept": "HR"})
print(f"Requested k=5 with a filter matching only 2 documents -> got {len(hits)}")
for d in hits:
    print(f"  {d.metadata['doc']}")

print("\nChroma pre-filters: it returned every matching document and stopped.")
print("Under POST-filtering you might have received 0 or 1 here, because the")
print("global top-5 need not contain any HR document at all.")
print("\nAlways log how many results you got, not just what you asked for.")

%%markdown
---

## Part 4 — Update and delete, and the ID problem

Here is the operation that does not exist: **there is no in-place update of a document's text.**

Changing a document's content changes its embedding, and the embedding is the index key. So "update" is always implemented as delete-then-insert. Chroma exposes `update_document`, which does exactly that under the hood.

Everything here depends on having **stable IDs**. If your IDs are auto-generated UUIDs assigned at ingest time, you have no way to say "this is the same document as before" on the next run — so you cannot update it, cannot delete it, and re-ingestion produces duplicates.

%%code
# ============ UPDATE: DELETE-AND-REINSERT UNDER THE HOOD ============
before = store.get(ids=["remote-policy"])["documents"][0]
print(f"before: {before}")

store.update_document(
    document_id="remote-policy",
    document=Document(
        page_content="Employees may work remotely up to four days per week.",
        metadata={"dept": "HR", "year": 2026, "public": True, "doc": "remote-policy"},
    ),
)

after = store.get(ids=["remote-policy"])["documents"][0]
print(f"after : {after}")
print(f"\nentries still {store._collection.count()} - replaced in place, not appended.")

# And the change is retrievable - the vector was recomputed, not just the text.
top = store.similarity_search("how many days remote", k=1)[0]
print(f"retrieved: {top.page_content}")

%%code
# ============ THE DUPLICATE TRAP ============
# Re-adding the SAME content with a NEW id duplicates it. This is what happens
# every time a re-ingestion pipeline generates fresh UUIDs.
store.add_documents(
    [Document(page_content="Employees may work remotely up to four days per week.",
              metadata={"dept": "HR", "year": 2026, "public": True, "doc": "remote-policy"})],
    ids=["remote-policy-COPY"],
)
print(f"entries after re-adding with a new id: {store._collection.count()}")

hits = store.similarity_search("how many days remote", k=3)
print("\nRetrieval now returns the same content twice:")
for d in hits:
    print(f"  - {d.page_content[:58]}...")

print("\nThat duplicate consumes a top-k slot, so a real answer gets pushed out.")
print("Re-adding with the SAME id would have overwritten instead.")

store.delete(ids=["remote-policy-COPY"])
print(f"\nAfter delete: {store._collection.count()} entries")

%%markdown
**Derive IDs deterministically from the document, not from the run.** Good choices:

- `f"{source_path}::{page}::{chunk_index}"` — readable, and tells you where it came from
- A hash of the content, if you want re-ingestion to be a genuine no-op for unchanged text
- A stable business key (`doc_id`, `ticket_id`) when one exists

The full lifecycle — detecting which documents changed, cleaning up chunks belonging to a deleted parent, and avoiding a full re-index — is `02_Chunking_and_Indexing/05_Incremental_Indexing_and_Record_Management.ipynb`. Getting IDs right here is what makes that lesson possible.

%%markdown
---

## Part 5 — Persistence

%%code
# ============ PERSIST AND RELOAD ============
# Chroma with a persist_directory writes as it goes. Reopening requires the
# same directory, the same collection name, AND the same embedding function.
reopened = Chroma(
    persist_directory=persist_dir,
    collection_name="handbook",       # wrong name -> a new EMPTY collection, no error
    embedding_function=embeddings,    # wrong model -> meaningless search, no error
)
print(f"reopened entries: {reopened._collection.count()}")
print(f"search works    : {reopened.similarity_search('parental leave', k=1)[0].page_content}")

# FAISS is explicit instead: save_local / load_local.
faiss_dir = tempfile.mkdtemp(prefix="rag_lesson04_faiss_")
faiss_store.save_local(faiss_dir)
faiss_reloaded = FAISS.load_local(faiss_dir, embeddings, allow_dangerous_deserialization=True)
print(f"\nFAISS reloaded  : {faiss_reloaded.index.ntotal} vectors")

%%markdown
Two silent failure modes in that cell, both worth internalizing:

**Wrong `collection_name`** — Chroma creates a new, empty collection rather than raising. Your searches return nothing and everything looks configured correctly.

**Wrong `embedding_function`** — no error, and searches return plausible-looking but meaningless results. This is exactly the mismatch failure from lesson 03, and it is why that lesson recommended storing the model name in your index metadata and asserting on it at startup.

`allow_dangerous_deserialization=True` on FAISS is required because the metadata sidecar is a pickle, which can execute arbitrary code on load. Only ever load indexes you built or otherwise trust.

%%code
# ============ ASSERT THE INDEX MATCHES THE MODEL ============
# The defensive pattern lesson 03 recommended. Cheap, and it converts a silent
# quality problem into a loud startup failure.
def open_store(persist_dir, collection, emb):
    s = Chroma(persist_directory=persist_dir, collection_name=collection,
               embedding_function=emb)
    if s._collection.count() == 0:
        raise RuntimeError(
            f"Collection {collection!r} in {persist_dir} is empty. "
            "Wrong collection name, or the index was never built."
        )
    stored_dim = len(s._collection.peek(1)["embeddings"][0])
    live_dim = len(emb.embed_query("dimension probe"))
    if stored_dim != live_dim:
        raise RuntimeError(
            f"Embedding mismatch: index has {stored_dim} dims, "
            f"{emb.model} produces {live_dim}."
        )
    return s


ok = open_store(persist_dir, "handbook", embeddings)
print(f"OK: opened 'handbook' with {ok._collection.count()} entries, dimensions verified")

try:
    open_store(persist_dir, "typo_in_collection_name", embeddings)
except RuntimeError as e:
    print(f"\nCaught what would otherwise be silent: {e}")

%%markdown
Note that the dimension check catches only *some* mismatches — `text-embedding-3-large` truncated to 1536 has the same dimensionality as `3-small` and would pass. Store the model **name** in your own metadata for a complete check.

%%markdown
---

## Part 6 — The retriever adapter

`as_retriever()` wraps a store in the `Retriever` interface: one method, `invoke(query)`, returning documents. Every chain in LangChain consumes that interface rather than a store directly, which is what lets you swap FAISS for Chroma, or a plain search for a reranked one, without touching the chain.

%%code
# ============ RETRIEVER: THE ADAPTER AND ITS CONFIGURATION ============
retriever = store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2, "filter": {"dept": "Finance"}},
)

print("retriever.invoke():")
for d in retriever.invoke("expense deadline"):
    print(f"  [{d.metadata['year']}] {d.page_content[:60]}...")

print(f"\nUnderlying store still accessible: {type(retriever.vectorstore).__name__}")
print("Scores are NOT exposed through this interface - go to the store directly")
print("when you need them for debugging (as Part 2 did).")

%%markdown
`search_type` selects the strategy the store applies:

| `search_type` | What it does | Taught in |
| --- | --- | --- |
| `"similarity"` | Plain nearest-neighbour (default) | this lesson |
| `"mmr"` | Maximal Marginal Relevance — trades relevance for diversity | `03_Retrieval/04_MMR_and_Diversity_Retrieval.ipynb` |
| `"similarity_score_threshold"` | Drops results below a cutoff | `03_Retrieval/01_Dense_and_Sparse_Retrieval.ipynb` |

Two things the adapter hides, both of which matter when debugging:

- **Scores.** `invoke()` returns documents only. When retrieval looks wrong, drop to `similarity_search_with_score` — that is the diagnostic from lesson 01's Part 6.
- **How many it actually returned.** As Part 3 showed, a filter can yield fewer than `k`. Log `len(results)`.

%%markdown
---

## Part 7 — Choosing a backend

%%code
# ============ THE SAME CORPUS IN THREE BACKENDS ============
mem_store = InMemoryVectorStore.from_documents(docs, embeddings)

for name, s in (("InMemory", mem_store), ("FAISS", faiss_store), ("Chroma", store)):
    hit = s.similarity_search("encryption requirement for laptops", k=1)[0]
    print(f"{name:<10} -> {hit.page_content[:58]}...")

print("\nIdentical API, identical top result. The backend is a deployment")
print("decision, not a modelling one - which is exactly what the abstraction buys.")

%%markdown
| | `InMemoryVectorStore` | FAISS | Chroma | Hosted (Pinecone, Weaviate, …) |
| --- | --- | --- | --- | --- |
| Persistence | None | File | File / server | Managed |
| Metadata filtering | Basic | **Limited** | Full | Full |
| Scale | Thousands | Millions (single machine) | Millions | Billions |
| Concurrent writers | No | No | Limited | Yes |
| Operational cost | None | None | Low | Per-usage |
| Good for | Tests, examples | Local, read-heavy, static corpora | Local development, small production | Production, multi-tenant, elastic |

Guidance rather than rules:

- **Start with Chroma** for anything you might keep. Persistence and real filtering, no server to run.
- **FAISS** when the corpus is static, read-heavy and speed matters. Its metadata filtering is weak — check that your filters are actually supported before committing.
- **`InMemoryVectorStore`** for tests and teaching. Nothing to clean up.
- **Move to a hosted store** when you need concurrent writers, horizontal scale, or managed availability — not before. That migration is a re-index, so the embedding model decision from lesson 03 travels with you.

`04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/` has per-backend setup notebooks for Chroma, FAISS, Pinecone and DataStax if you need the specifics of one.

%%markdown
---

## Limitations and tradeoffs

**Everything above ran on six documents.** Backend differences that matter — index build time, memory footprint, recall degradation from approximate search — appear at 10⁵–10⁷ vectors and are invisible here.

**Approximate search is approximate.** Production indexes (HNSW, IVF) trade recall for speed: they are not guaranteed to return the true nearest neighbours. FAISS's flat index and Chroma's defaults are exact at this scale, so nothing in this notebook exposed that trade-off. At scale it is a tuning parameter with real consequences.

**Metadata filtering is exact-match.** `"Engineering"` will not match `"engineering"`. Normalize at ingest time — this is the payoff for lesson 02's advice about deliberate metadata.

**Type restrictions are real.** Chroma accepts `str`, `int`, `float`, `bool`. Lists and nested dicts must be flattened or serialized before indexing.

**Deleting a parent document does not delete its chunks.** The store knows nothing about the relationship. Managing that is `02_Chunking_and_Indexing/05`.

**No access control here.** Every filter in this lesson is advisory: a caller who omits the filter sees everything. Enforcing tenant isolation at the retrieval layer is `10_Production_RAG/01_Enterprise_Access_Control_and_ACL_Retrieval.ipynb`.

%%markdown
---

## Exercise

Wrap a store in a `ManagedIndex` that makes the safe thing the easy thing: deterministic IDs, idempotent re-ingestion, and a startup check.

%%code
# ============ EXERCISE: AN INDEX WITH A SAFE INGESTION CONTRACT ============
import hashlib


class ManagedIndex:
    """A vector store wrapper with deterministic IDs and idempotent upserts."""

    def __init__(self, persist_dir: str, collection: str, embedding):
        self.embedding = embedding
        self.store = Chroma(
            persist_directory=persist_dir,
            collection_name=collection,
            embedding_function=embedding,
        )

    @staticmethod
    def make_id(doc: Document) -> str:
        """Derive a stable ID from source identity, not from ingest order."""
        key = f"{doc.metadata.get('source', '?')}::{doc.metadata.get('doc', '?')}"
        digest = hashlib.sha256(doc.page_content.encode()).hexdigest()[:8]
        return f"{key}::{digest}"

    def upsert(self, documents: list[Document]) -> dict:
        """Add documents, replacing any with the same ID. Safe to re-run."""
        ids = [self.make_id(d) for d in documents]
        existing = set(self.store.get(ids=ids)["ids"])
        self.store.add_documents(documents, ids=ids)   # same id -> overwrite
        return {
            "submitted": len(ids),
            "replaced": len(existing),
            "new": len(ids) - len(existing),
            "total": self.store._collection.count(),
        }

    def search(self, query: str, k: int = 4, **filters):
        results = self.store.similarity_search_with_score(
            query, k=k, filter=filters or None
        )
        if len(results) < k:
            print(f"  note: asked for {k}, got {len(results)} (filter is selective)")
        return results

    # TODO 1: content-hash IDs mean an EDITED document gets a NEW id, so the
    #         old version survives as a duplicate. Fix it: separate the stable
    #         identity from the content hash, and delete stale versions.
    #
    # TODO 2: store the embedding model name in a metadata field on every
    #         document, and assert it in __init__. The dimension check in
    #         Part 5 misses 3-large-truncated-to-1536; this would catch it.
    #
    # TODO 3: add `delete_source(source)` removing every chunk from one source
    #         document. Which metadata field do you need for that to work?


mi_dir = tempfile.mkdtemp(prefix="rag_lesson04_managed_")
index = ManagedIndex(mi_dir, "managed", embeddings)

print("first ingest :", index.upsert(docs))
print("second ingest:", index.upsert(docs), "  <- idempotent, nothing duplicated")
print()
for d, score in index.search("remote work policy", k=2, dept="HR"):
    print(f"  {score:.4f}  {d.page_content[:58]}...")

%%code
# ============ CLEANUP ============
# Every store in this notebook lived in a temp directory. Remove them so
# repeated runs do not accumulate indexes on disk.
for d in (persist_dir, faiss_dir, mi_dir):
    shutil.rmtree(d, ignore_errors=True)
print("Temporary indexes removed. No checked-in index was touched.")

%%markdown
---

## Summary

**A vector store is a database.** Add, search, filter, delete — and *not* update, which is always delete-then-insert because changing text changes the index key.

**Stable IDs are the foundation.** Derive them deterministically from the document. Without them you cannot update or delete, and re-ingestion silently duplicates — with duplicates consuming top-k slots that real answers needed.

**Scores are backend-specific.** Chroma and FAISS both return distances (lower is better) from `similarity_search_with_score`, while `..._with_relevance_scores` returns 0–1 (higher is better). Never hardcode a threshold without checking; never compare across backends or models.

**Filtering is exact-match on flat types**, and `k` is an upper bound — log what you actually got. Fewer results than requested means either a selective filter (fine, pre-filtering) or post-filtering (a problem).

**Reopening a store fails silently** on a wrong collection name (empty collection, no error) or a wrong embedding model (meaningless results, no error). Assert at startup.

**The retriever adapter** is what makes backends swappable, and it hides scores and result counts — drop to the store when debugging.

**Backend choice is a deployment decision**: InMemory for tests, Chroma to start, FAISS for static read-heavy corpora, hosted when you need concurrency and scale.

### Next lesson

`01_Foundations/05_Structured_Data_RAG.ipynb` — what happens when your corpus is rows and records rather than prose, and where the whole embed-and-retrieve approach starts to break down.

%%markdown
---

### Migration record

Canonical lesson for concept `RAG-F-04` (vector stores and index operations), Foundations batch. Retrieval *strategies* — MMR, thresholds, multi-query, compression, ensemble — were deliberately left to `03_Retrieval/` rather than carried here; this lesson stops at the retriever adapter boundary. See `RAG_MIGRATION_MANIFEST.md` for per-source disposition.
