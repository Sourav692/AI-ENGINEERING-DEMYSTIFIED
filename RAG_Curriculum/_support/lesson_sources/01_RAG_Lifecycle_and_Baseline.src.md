%%markdown attach=four_components
# RAG Lifecycle and Baseline

Retrieval-Augmented Generation (RAG) gives a language model access to knowledge it was never trained on. Instead of asking the model what it remembers, you retrieve relevant passages from your own corpus and hand them to the model as context. Answers become grounded in documents you control, can be updated without retraining, and can be traced back to a source.

This lesson builds the complete pipeline once, end to end, at baseline depth — the version everything else in this curriculum modifies. Every later lesson changes exactly one stage of what you build here.

## Learning objectives

By the end of this notebook you will be able to:

1. **Describe the four components of RAG** — indexing, retrieval, augmentation, generation — and explain why indexing happens once while the other three happen per query.
2. **Implement retrieval without a framework**, using TF-IDF vectors and nearest-neighbour search, so you can see that "retrieval" is ordinary vector similarity before any library hides it.
3. **Build the indexing phase**: load documents, split them into chunks, embed the chunks, and store them in a vector index.
4. **Build the retrieval and generation phase**: retrieve by similarity, inspect the evidence and its scores, assemble a prompt, and generate a grounded answer.
5. **Harden the baseline** with source attribution, an out-of-scope fallback, and validated structured output.
6. **Diagnose where this baseline fails**, and name the lesson in this curriculum that fixes each failure.

![RAG four components](attachment:four_components)

%%markdown
## Prerequisites

**Knowledge**

- Basic Python: functions, classes, list comprehensions.
- Familiarity with calling an LLM through LangChain, and with LCEL's `|` composition operator. See `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/`.
- No prior RAG knowledge is assumed. This is the entry point.

**Packages**

`langchain`, `langchain-core`, `langchain-classic`, `langchain-openai`, `langchain-community`, `langchain-text-splitters`, `faiss-cpu`, `scikit-learn`, `tiktoken`, `numpy`, `pandas`, `pydantic`, `python-dotenv`, `pypdf`, plus this repository's own `helpers` package (installed with `uv pip install -e . --no-deps`).

All of these are in the repository's pinned environment; see the root `requirements.txt`.

> **LangChain version matters here.** This lesson is written for **LangChain 1.x** (verified against `langchain` 1.4.0 / `langchain-core` 1.6.1 / `langchain-classic` 1.0.8). LangChain 1.0 moved every legacy chain out of the `langchain` package, so imports copied from older RAG tutorials fail outright rather than warning. Part 4 has the migration table.

**Services and credentials**

Two keys, in a `.env` file at the repository root:

| Variable | Used for | From |
| --- | --- | --- |
| `EXPERIENTIALLABS_API_KEY` | **Generation.** All chat completions, via `helpers.get_experientiallabs_llm()` (`gpt-5.6-luna`). | Part 4 onward |
| `OPENAI_API_KEY` | **Embeddings only** (`text-embedding-3-small`). | Part 3 onward |

Generation and embedding come from different providers here, which is normal and worth noticing: they are independent choices. The one thing you may *not* mix is the embedding model between indexing and querying — see Part 2.

Part 2 runs fully offline with no key and no network access.

**Input assets**

- `bella_vista.txt` — the small restaurant FAQ corpus used throughout.
- `Transformer.pdf` — used once to show PDF loading.

Neither path is hardcoded. Both are resolved by `rag_paths.asset()`, introduced in Part 0.

**Cost**

Running Parts 3–7 end to end issues roughly 20 embedding calls (`text-embedding-3-small`) and 14 chat completions (`gpt-5.6-luna`). Actual measured token usage from a full run is recorded in the runtime-status table below. Part 2 is free.

%%markdown
## Provenance and runtime status

This lesson is the consolidated canonical source for the RAG lifecycle concept. It was merged from the notebooks below, all of which were **retired on 2026-09-10** to `RAG_Curriculum/_archive/source_notebooks_preserved_by_migration_manifest/`, where each sits at its original relative path. Nothing was deleted; see that folder's `ARCHIVE_MANIFEST.md` to restore any of them.

| Contributing source | What it contributed |
| --- | --- |
| `04_Retrieval_and_RAG/09_RAG_with_LangChain/7.1_RAG_Comprehensive.ipynb` | Primary structure: loaders, splitting, embeddings and cosine similarity, FAISS, retriever configuration, modern vs legacy retrieval chains. |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/1_rag_overview.ipynb` | Four-component framing, the indexing/query-time phase split, the "what this validates" checkpoints, token counting with `cl100k_base`, and the three diagrams. |
| `04_Retrieval_and_RAG/RAG_Production_Course/06_rag_pipeline.ipynb` | Source attribution, out-of-scope fallback, structured output with Pydantic, and the `DocumentQA` exercise. |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/Basics of RAG.ipynb` | The framework-free TF-IDF + nearest-neighbour baseline in Part 2. |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/Naive_RAG.ipynb` | The indexing → retrieval → augmentation → generation stage names, and scored retrieval via `similarity_search_with_score`. |
| `04_Retrieval_and_RAG/09_RAG_with_LangChain/7.0_RAG_Essentials.ipynb` | `return_source_documents` and the multi-document summarization variant. |

**Runtime status.**

**All 27 code cells were executed end to end, in order, in a fresh namespace on September 10, 2026 — 27/27 passed.** Measured cost of that run: 13 chat completions totalling 2,664 input and 370 output tokens, plus ~20 embedding calls. Wall time 52 seconds.

| Section | Status |
| --- | --- |
| Part 0 (path resolution) | **Verified.** Resolves both input assets from the repository root and from a nested notebook directory. |
| Part 2 (TF-IDF baseline) | **Verified**, offline. No API key or network required. The paraphrase query returns cosine distance 1.0000 — fully orthogonal — which is the point being made. |
| Parts 3–7 | **Verified by execution.** Cosine similarity behaves as taught (identical 1.0000, paraphrase 0.6341, unrelated 0.0016); 9 chunks produce 9 vectors and survive a disk round trip; the fallback correctly refuses both out-of-scope questions; structured output returns a validated `RAGResponse`. |
| LangChain 1.x imports | **Verified.** The import check caught four LangChain 0.x imports inherited from the source notebooks (`langchain.chains.*`, `langchain.prompts`) that raise `ModuleNotFoundError` on this repository's LangChain 1.4 environment. They are corrected here, and the migration is taught in Part 4. |
| Legacy `RetrievalQA` cell | Deliberately deprecated, but **does execute** (returns an answer and 4 source documents). Kept as a contrast, tagged `legacy-contrast`, and not part of the main path. |

One environment note from that run: `pypdf` is declared in `pyproject.toml` and pinned in `requirements.txt`, but was missing from the virtual environment these notebooks actually run on, so the PDF cell in Part 3 failed with `ImportError: pypdf package not found` until it was installed. If you hit that, install the pinned version rather than an arbitrary one.

%%markdown
---

## Part 0 — Setup

### Depth-independent asset resolution

Notebooks in this repository have historically referenced their inputs with paths like `./bella_vista.txt` or `../../data/Transformer.pdf`. Those break the moment a notebook moves or the kernel starts in a different directory — a known, recorded problem in this repo.

`rag_paths` fixes it: it walks upward to find the repository root, then searches a known list of asset roots by filename. If an asset is genuinely missing it raises, listing every root it searched, rather than silently falling back to a different file that happens to share a name.

%%code
# ============ BOOTSTRAP: DEPTH-INDEPENDENT PATHS ============
# Walk up from wherever this kernel started until we find the repo root,
# then put the curriculum's shared helpers on sys.path.
import pathlib
import sys

_p = pathlib.Path.cwd()
while not (_p / "RAG_Curriculum").is_dir() and _p != _p.parent:
    _p = _p.parent
sys.path.insert(0, str(_p / "RAG_Curriculum" / "_support" / "helpers"))

from rag_paths import asset, repo_root

print("Repository root :", repo_root())
print("Corpus          :", asset("bella_vista.txt"))
print("PDF sample      :", asset("Transformer.pdf"))

%%code
# ============ IMPORTS AND ENVIRONMENT ============
# stdlib -> third-party -> LangChain
import tempfile
from typing import List

import numpy as np
import tiktoken
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

# Every LLM call in this lesson goes through the repository's shared factory
# rather than instantiating a chat model directly, so the provider and model
# are configured in one place. get_experientiallabs_llm returns a ChatOpenAI
# pointed at the Experiential Labs OpenAI-compatible endpoint.
from helpers import get_experientiallabs_llm
# langchain_community is being sunset in favour of standalone integration
# packages, but no standalone FAISS or PyPDF package exists yet, and this
# repository pins langchain-community==0.4.2. The DeprecationWarning it emits
# on import is expected here; there is nothing to migrate to today.
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load OPENAI_API_KEY from the .env at the repository root. We pass the path
# explicitly via repo_root() rather than using find_dotenv(), which infers the
# location by walking caller stack frames and is unreliable outside a normal
# interactive kernel.
load_dotenv(repo_root() / ".env")

print("Imports ready.")

%%markdown attach=pipeline_walkthrough
---

## Part 1 — What RAG is, and why the baseline is shaped this way

An LLM answering from its weights alone has three problems you cannot fix by prompting harder:

- **It hallucinates.** When the model does not know, it produces fluent, confident, wrong text.
- **It is frozen.** Its knowledge ends at its training cutoff, and your documents were never in it.
- **It cannot cite.** There is no source to point at, so nothing can be audited.

RAG addresses all three by retrieving relevant passages first and putting them in the prompt. The model's job shifts from *recall* to *reading comprehension over supplied evidence* — a task it is far more reliable at.

![A high-level walkthrough of a basic RAG pipeline](attachment:pipeline_walkthrough)

%%markdown attach=rag_from_scratch
### The four components, and the two phases

A RAG system has four components:

| Component | What it does |
| --- | --- |
| **Indexing** | Turn a corpus into something searchable: load, split, embed, store. |
| **Retrieval** | Given a question, find the passages most likely to contain the answer. |
| **Augmentation** | Assemble those passages into a prompt alongside the question. |
| **Generation** | Have the LLM answer *from that context*, not from memory. |

The crucial structural fact is that these split across **two phases that run at different times**:

**Indexing phase — runs once, ahead of time, offline.**

1. Load raw documents
2. Split them into chunks
3. Embed each chunk
4. Store the vectors in an index

**Query phase — runs per user question, online, on the latency budget.**

5. Embed the question
6. Retrieve the nearest chunks
7. Assemble them into a prompt
8. Generate the answer

This separation is what makes RAG practical. Embedding a million documents is slow and costs money, but you pay it once. A query only embeds one short string and does one nearest-neighbour lookup. It is also what makes RAG debuggable: when an answer is wrong you can ask *which* of the two phases failed — did retrieval surface the wrong passages, or did the model mishandle correct ones? That question is answerable, and Part 6 shows you how to answer it.

![RAG from scratch overview](attachment:rag_from_scratch)

*Diagram credit: adapted from [LangChain's rag-from-scratch](https://github.com/langchain-ai/rag-from-scratch/blob/main/rag_from_scratch_1_to_4.ipynb).*

%%markdown
---

## Part 2 — Retrieval without a framework

Before any library hides it, build retrieval by hand. The mechanism is smaller than it looks: **turn text into vectors, then find the nearest vector to the query.** That is the whole idea. Vector databases add scale and filtering, and embedding models add semantics, but neither changes the shape.

We will use TF-IDF — a purely lexical, non-neural vectorizer — and scikit-learn's nearest-neighbour index. This entire part runs offline with no API key.

%%code
# ============ STEP 1: VECTORIZE A TINY CORPUS (TF-IDF) ============
# TF-IDF scores each word by how often it appears in a document, damped by how
# common it is across all documents. No neural network, no API call - each
# document becomes a sparse vector over the vocabulary.
import pandas as pd

documents = [
    "This is the Fundamentals of RAG course",
    "Educative is an AI-powered online learning platform",
    "There are several Generative AI courses available on Educative",
    "I am writing this using my keyboard",
]

vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(documents)

# Show the vectors as a readable table: rows are documents, columns vocabulary.
tfidf_df = pd.DataFrame(
    tfidf_matrix.toarray(),
    columns=vectorizer.get_feature_names_out(),
    index=[f"Doc {i + 1}" for i in range(len(documents))],
)

print(f"Vocabulary size : {len(vectorizer.get_feature_names_out())}")
print(f"Matrix shape    : {tfidf_matrix.shape}  (documents x vocabulary)\n")
tfidf_df.round(3)

%%code
# ============ STEP 2: BUILD THE INDEX ============
# NearestNeighbors over cosine distance IS a vector database, conceptually:
# it stores the document vectors and answers "which stored vector is closest?"
index = NearestNeighbors(n_neighbors=1, metric="cosine").fit(tfidf_matrix)

print("Index built over", tfidf_matrix.shape[0], "document vectors.")

%%code
# ============ STEP 3: QUERY THE INDEX ============
# Retrieval in three lines: embed the query into the SAME space, find the
# nearest stored vector, return the document it came from.
def query_index(query: str, k: int = 1):
    """Return the k nearest documents to `query`, with their cosine distances."""
    query_vec = vectorizer.transform([query])          # same vector space as the corpus
    distances, indices = index.kneighbors(query_vec, n_neighbors=k)

    print(f"Query: {query!r}")
    for rank, (dist, doc_i) in enumerate(zip(distances[0], indices[0]), start=1):
        print(f"  {rank}. distance={dist:.4f}  ->  {documents[doc_i]!r}")
    return [documents[i] for i in indices[0]]


_ = query_index("What course is this?", k=2)

%%markdown
**What this validates**

- The query was projected into the same vector space as the corpus. This is non-negotiable: *the query and the documents must be vectorized by the same model*. Mixing vectorizers silently produces meaningless distances, and it is one of the most common RAG bugs.
- The nearest document was returned by numerical distance, not by keyword matching rules.
- Retrieval returned a *ranked list with scores*, not a single answer. Everything downstream consumes that list.

%%code
# ============ THE LIMIT OF LEXICAL MATCHING ============
# TF-IDF can only match words it has literally seen. Ask the same question
# using different words and it has nothing to work with.
print("Query that shares words with the corpus:")
_ = query_index("Educative learning platform")

print("\nSemantically identical question, different vocabulary:")
_ = query_index("Where can I study machine intelligence on the web?")

print("\nVocabulary the index actually knows:")
print(sorted(vectorizer.get_feature_names_out()))

%%markdown
The second query means almost exactly the same thing as the first, and TF-IDF cannot see it. "study", "machine intelligence" and "web" are not in the vocabulary at all, so those terms contribute nothing; the match is effectively arbitrary.

This is the gap **embeddings** close. An embedding model maps text into a dense space where *meaning* determines position, so "AI-powered online learning platform" and "study machine intelligence on the web" land near each other despite sharing no words. Everything from Part 3 onward swaps TF-IDF for a learned embedding model — but the mechanism you just built does not change at all.

> Lexical matching is not obsolete, though. BM25 (a stronger relative of TF-IDF) beats embeddings on exact identifiers, product codes and rare proper nouns. Combining both is **hybrid search** — `03_Retrieval/03_Hybrid_Search.ipynb`.

%%markdown
---

## Part 3 — The indexing phase

Now build the real thing. Four steps, run once: **load → split → embed → store.**

### Step 1: Load

A loader's job is to turn some external format into LangChain `Document` objects, each with two fields:

- `page_content` — the text
- `metadata` — where it came from (source path, page number, anything you add)

Metadata is not decoration. It is what makes filtering and citation possible later, and it is far easier to attach at load time than to reconstruct afterwards.

%%code
# ============ LOAD: TEXT FILE ============
# Path comes from the resolver, so this cell works no matter where the
# kernel was started or where this notebook is moved to.
loader = TextLoader(str(asset("bella_vista.txt")), encoding="utf-8")
docs = loader.load()

print(f"Documents loaded : {len(docs)}")
print(f"Characters       : {len(docs[0].page_content)}")
print(f"Metadata         : {docs[0].metadata}\n")
print(docs[0].page_content[:300], "...")

%%markdown
Note that the **entire file arrived as a single `Document`**. Loaders do not split; that is the next step's job. A one-document corpus is useless for retrieval, because retrieving "the document" returns everything.

LangChain ships loaders for most formats — PDF, CSV, JSON, Markdown, HTML, Word, directories, URLs, YouTube transcripts, and many more. They all return the same `Document` shape, which is the point.

%%code
# ============ LOAD: OTHER SOURCES ============
# 1. A PDF. PyPDFLoader returns one Document PER PAGE, and records the page
#    number in metadata - useful later for citations.
pdf_docs = PyPDFLoader(str(asset("Transformer.pdf"))).load()
print(f"PDF pages loaded : {len(pdf_docs)}")
print(f"Page 1 metadata  : {pdf_docs[0].metadata}")
print(f"Page 1 preview   : {pdf_docs[0].page_content[:150].strip()!r}\n")

# 2. Constructed by hand. Useful when your data comes from a database or API
#    rather than a file - you are never obliged to write it to disk first.
manual = Document(
    page_content="Bella Vista does not currently offer a delivery service.",
    metadata={"source": "manual_entry", "author": "ops-team", "verified": True},
)
print("Manual document  :", manual)

%%markdown
> **Dedicated lesson:** the full catalogue of loaders, metadata contracts and provenance is `01_Foundations/02_Document_Loading_and_Metadata.ipynb`.

### Step 2: Split into chunks

Chunking is the step people skip and then regret. It exists to solve several constraints at once:

- **Context limits.** You cannot put a 400-page PDF into a prompt.
- **Retrieval precision.** Retrieving a whole document buries the relevant sentence in noise; retrieving a focused passage does not.
- **Semantic coherence.** A chunk should ideally be about one thing, so its embedding means one thing.

Two parameters govern it:

- **`chunk_size`** — the maximum size of a chunk.
- **`chunk_overlap`** — how much text is repeated between consecutive chunks, so a sentence spanning a boundary is not cut in half in both chunks.

`RecursiveCharacterTextSplitter` is the sensible default. It tries separators in order — paragraphs, then lines, then words, then characters — and only falls back to a cruder split when a chunk is still too large. That keeps semantically related text together where it can.

%%code
# ============ SPLIT: CHUNK THE CORPUS ============
splitter = RecursiveCharacterTextSplitter(
    chunk_size=250,      # small, so the overlap is visible in the output below
    chunk_overlap=50,    # ~20% of chunk_size is a common starting point
    # Default separators, tried in order: ["\n\n", "\n", " ", ""]
)
chunks = splitter.split_documents(docs)

print(f"1 document -> {len(chunks)} chunks\n")
for i, chunk in enumerate(chunks[:3]):
    print(f"--- Chunk {i} ({len(chunk.page_content)} chars) ---")
    print(chunk.page_content)
    print(f"metadata: {chunk.metadata}\n")

%%code
# ============ INSPECT: SEE THE OVERLAP ============
# The tail of one chunk should reappear at the head of the next. This is what
# stops a fact that straddles a boundary from being lost by both chunks.
for i in range(min(3, len(chunks) - 1)):
    tail = chunks[i].page_content[-50:]
    head = chunks[i + 1].page_content[:50]
    print(f"Chunk {i} ends   : ...{tail!r}")
    print(f"Chunk {i+1} starts: {head!r}...")
    print(f"  overlapping?   {tail.strip()[-20:] in chunks[i + 1].page_content}\n")

%%markdown
**Character counts are the wrong unit.** Models and embedding APIs are billed and limited in *tokens*, not characters, and the ratio varies with the text — English prose runs roughly 4 characters per token, but code, URLs and non-English text are far denser.

`cl100k_base` is the tokenizer vocabulary used by GPT-3.5-Turbo, GPT-4 and the OpenAI embedding models. Measuring your chunks in its tokens tells you what you will actually pay and what will actually fit.

%%code
# ============ MEASURE: CHUNK SIZE IN TOKENS ============
encoding = tiktoken.get_encoding("cl100k_base")

print(f"{'chunk':>6} {'chars':>7} {'tokens':>8} {'chars/token':>13}")
for i, chunk in enumerate(chunks):
    n_chars = len(chunk.page_content)
    n_tokens = len(encoding.encode(chunk.page_content))
    print(f"{i:>6} {n_chars:>7} {n_tokens:>8} {n_chars / n_tokens:>13.2f}")

total_tokens = sum(len(encoding.encode(c.page_content)) for c in chunks)
print(f"\nWhole corpus: {total_tokens} tokens across {len(chunks)} chunks.")
print("This is what you pay to embed once, and roughly what a top-k=4 retrieval")
print("will add to every single prompt at query time.")

%%markdown
> **Dedicated lessons:** splitter types and strategies in `02_Chunking_and_Indexing/01_Document_Splitting_and_Chunking.ipynb`; picking the size empirically in `02_Chunking_and_Indexing/04_Choosing_Chunk_Size.ipynb`; embedding-boundary chunking in `02_Chunking_and_Indexing/02_Semantic_Chunking.ipynb`.

### Step 3: Embed

An embedding model maps text to a dense vector — for `text-embedding-3-small`, 1536 floating-point numbers — positioned so that **semantically similar texts land close together**. That is the property that makes meaning-based search possible.

The rule from Part 2 applies with full force here: **the model that embeds your documents must be the model that embeds your queries.** Different models produce incompatible spaces, and nothing will warn you — you will just get quietly terrible results.

%%code
# ============ EMBED: TEXT TO VECTOR ============
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vec = embeddings.embed_query("The solar system consists of the Sun and the objects that orbit it")

print(f"Dimensions       : {len(vec)}")
print(f"Type per element : {type(vec[0]).__name__}")
print(f"First 8 values   : {[round(v, 4) for v in vec[:8]]}")

%%code
# ============ COSINE SIMILARITY ============
# Cosine similarity measures the ANGLE between two vectors, ignoring their
# magnitude:   cos(t) = (A . B) / (||A|| * ||B||)
#
#    1.0  identical direction
#    0.0  orthogonal / unrelated
#   -1.0  opposite
#
# For text embeddings in practice you will see roughly 0.1 to 1.0.
def cosine_similarity(a, b) -> float:
    """Cosine similarity between two embedding vectors."""
    a, b = np.asarray(a), np.asarray(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

%%code
# ============ COMPARE: DOES THE SPACE BEHAVE? ============
texts = {
    "original": "The solar system consists of the Sun and the objects that orbit it",
    "identical": "The solar system consists of the Sun and the objects that orbit it",
    "paraphrase": "Planets, asteroids, and comets are part of our solar system.",
    "unrelated": "I love baking chocolate chip cookies on weekends.",
}
vectors = {name: embeddings.embed_query(text) for name, text in texts.items()}

print(f"{'comparison':<28} {'similarity':>10}")
for name in ("identical", "paraphrase", "unrelated"):
    score = cosine_similarity(vectors["original"], vectors[name])
    print(f"original vs {name:<16} {score:>10.4f}")

print("\nThis is the property Part 2's TF-IDF lacked: the paraphrase shares almost")
print("no vocabulary with the original, yet scores far above the unrelated text.")

%%markdown
> **Dedicated lesson:** model choice, dimensions, normalization, batching and caching in `01_Foundations/03_Embeddings_and_Model_Selection.ipynb`.

### Step 4: Store

A vector store holds the embeddings and answers nearest-neighbour queries over them quickly. We use **FAISS** — Meta's similarity-search library. It runs locally, needs no server, and persists to disk, which makes it ideal for learning.

We write to a **temporary directory**. Several notebooks in this repository persist indexes into checked-in folders such as `vs_db/` and `index/`; rebuilding those as a side effect of running a lesson would overwrite work you may still need.

%%code
# ============ STORE: BUILD THE FAISS INDEX ============
# from_documents() embeds every chunk and indexes the vectors in one call.
vectorstore = FAISS.from_documents(chunks, embeddings)

# Persist to a throwaway directory - never into a checked-in index folder.
persist_dir = tempfile.mkdtemp(prefix="rag_lesson01_")
vectorstore.save_local(persist_dir)

print(f"Indexed {vectorstore.index.ntotal} vectors of dimension {vectorstore.index.d}")
print(f"Saved to {persist_dir}")

%%code
# ============ VALIDATE THE INDEXING PHASE ============
# One chunk = one embedding = one vector entry. If these disagree, something
# was silently dropped and every downstream result is suspect.
assert vectorstore.index.ntotal == len(chunks), (
    f"{len(chunks)} chunks produced {vectorstore.index.ntotal} vectors"
)
print(f"OK: {len(chunks)} chunks -> {vectorstore.index.ntotal} vectors")

# Reload from disk with the SAME embedding model. allow_dangerous_deserialization
# is required because the metadata sidecar is a pickle - only ever load indexes
# you built or otherwise trust.
reloaded = FAISS.load_local(
    persist_dir,
    embeddings,
    allow_dangerous_deserialization=True,
)
assert reloaded.index.ntotal == vectorstore.index.ntotal
print(f"OK: round-tripped {reloaded.index.ntotal} vectors through disk")

%%markdown
> **Dedicated lesson:** collections, upserts, deletes, filters and the trade-offs between Chroma, FAISS, PostgreSQL/pgvector and Pinecone in `01_Foundations/04_Vector_Stores_and_Index_Operations.ipynb`.

The indexing phase is now complete. Everything above runs **once**. Everything below runs **per question**.

%%markdown
---

## Part 4 — The retrieval and generation phase

### Step 5: Retrieve

A **retriever** is a thin interface over the vector store with a single method, `invoke(query)`. The indirection is worth it: swapping FAISS for Chroma, or a plain similarity search for a hybrid or reranked one, becomes a one-line change that the rest of the chain never sees.

%%code
# ============ RETRIEVE: FIND RELEVANT CHUNKS ============
retriever = vectorstore.as_retriever()   # defaults: similarity search, k=4

question = "What are the opening hours on Sunday?"
retrieved = retriever.invoke(question)

print(f"Question: {question!r}")
print(f"Retrieved {len(retrieved)} chunks\n")
for i, doc in enumerate(retrieved, start=1):
    print(f"--- Result {i} (source: {doc.metadata.get('source', '?')}) ---")
    print(doc.page_content.strip()[:200])
    print()

%%code
# ============ INSPECT: THE SCORES BEHIND THE RANKING ============
# as_retriever() hides the distances. Go to the vector store directly when you
# need to see WHY something ranked where it did - this is your primary
# debugging tool when retrieval misbehaves.
scored = vectorstore.similarity_search_with_score(question, k=4)

print(f"{'rank':>4} {'distance':>10}  chunk preview")
for rank, (doc, distance) in enumerate(scored, start=1):
    preview = doc.page_content.strip().replace("\n", " ")[:70]
    print(f"{rank:>4} {distance:>10.4f}  {preview}...")

print("\nFAISS returns L2 DISTANCE here, not similarity: lower is closer.")
print("A large gap between rank 1 and rank 2 means the top hit is clearly best;")
print("a flat distribution means the retriever is guessing.")

%%code
# ============ CONFIGURE: k AND METADATA FILTERS ============
# Retrieval parameters belong in search_kwargs when the retriever is built,
# not passed ad hoc to invoke() - not every vector store honours them there.
narrow = vectorstore.as_retriever(
    search_kwargs={
        "k": 2,                                          # fewer, more precise results
        "filter": {"source": str(asset("bella_vista.txt"))},  # metadata predicate
    }
)
results = narrow.invoke(question)

print(f"k=2 with a source filter -> {len(results)} chunks")
for doc in results:
    print(f"  - {doc.page_content.strip()[:80]}...")

%%markdown
`k` is a real trade-off, not a tuning knob to max out. Too small and the answer may simply not be in the context. Too large and you pay for more tokens, add latency, and dilute the signal — models attend worse to relevant text buried among irrelevant text.

> **Dedicated lessons:** dense vs sparse retrieval in `03_Retrieval/01_Dense_and_Sparse_Retrieval.ipynb`; metadata predicates and self-querying in `03_Retrieval/02_Metadata_Filtering_and_Self_Query.ipynb`; reranking a wide candidate set down to a precise few in `03_Retrieval/05_Reranking_and_Contextual_Compression.ipynb`.

### Step 6: Augment

Augmentation is the least glamorous component and a common source of bugs. Retrieval hands you a *list of `Document` objects*; a prompt needs *a string*. How you flatten that list — the separator, the ordering, whether you label each passage with its source — is a real design decision that affects both answer quality and whether citation is possible at all.

%%code
# ============ AUGMENT: DOCUMENTS TO CONTEXT STRING ============
def format_docs(docs) -> str:
    """Flatten retrieved documents into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


prompt = ChatPromptTemplate.from_template(
    """Answer the question using only the context below.
If the context does not contain the answer, say you don't know.

Context:
{context}

Question: {question}

Answer:"""
)

# Look at exactly what the model will receive. Whenever a RAG answer is wrong,
# print this first - very often the evidence simply was not in the prompt.
assembled = prompt.format(context=format_docs(retrieved), question=question)
print(assembled)

%%markdown
### Step 7: Generate

Now compose the whole query phase into one runnable with LCEL. Read the chain top to bottom:

- `{"context": retriever | format_docs, "question": RunnablePassthrough()}` — run the question through the retriever and flatten the results into `context`, while passing the original question straight through as `question`.
- `| prompt` — fill both slots in the template.
- `| llm` — generate.
- `| StrOutputParser()` — unwrap the message into a plain string.

%%code
# ============ GENERATE: THE COMPLETE RAG CHAIN ============
# temperature=0.2 keeps the model close to the retrieved evidence rather than
# improvising - the opposite of what you would want for creative writing.
llm = get_experientiallabs_llm(temperature=0.2)
print("LLM:", llm.model_name)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

for q in [
    "What are the opening hours on Sunday?",
    "Do you have vegan options?",
    "Can I book the restaurant for a corporate event?",
]:
    print(f"Q: {q}")
    print(f"A: {rag_chain.invoke(q)}\n")

%%markdown
That is a complete RAG system. Load, split, embed, store, retrieve, augment, generate — every component in this curriculum is a modification of one of those seven lines.

#### Prebuilt chains, and the LangChain 1.x split

LangChain also ships prebuilt chains that wire retrieval and prompt-stuffing together for you. Before reaching for one, you need to know where they live now.

**LangChain 1.x moved every legacy chain out of the `langchain` package.** This repository runs LangChain 1.4, where `langchain` exposes only `agents`, `chat_models`, `embeddings`, `mcp`, `messages`, `rate_limiters` and `tools`. The chain abstractions were split into a separate `langchain_classic` package:

| Old import (LangChain 0.x) | LangChain 1.x |
| --- | --- |
| `from langchain.chains.retrieval import create_retrieval_chain` | `from langchain_classic.chains.retrieval import ...` |
| `from langchain.chains.combine_documents import create_stuff_documents_chain` | `from langchain_classic.chains.combine_documents import ...` |
| `from langchain.chains import RetrievalQA` | `from langchain_classic.chains import RetrievalQA` |
| `from langchain.prompts import PromptTemplate` | `from langchain_core.prompts import PromptTemplate` |

The old imports do not warn — they raise `ModuleNotFoundError: No module named 'langchain.chains'`. If you are following a tutorial written before this split, that error is what you will hit, and this table is the fix.

The package name is the signal: **`langchain_classic` is where the pre-1.x abstractions were retired to.** The LCEL chain you built above is the current idiom and is not in it. `create_retrieval_chain` is still genuinely useful — it returns the retrieved documents alongside the answer, which you want, because an answer you cannot trace is an answer you cannot audit — but recognise that using it means opting into the classic layer.

Note also that its input key is `input`, not `question`.

%%code
# ============ GENERATE: create_retrieval_chain (langchain_classic) ============
# In LangChain 1.x these live in langchain_classic, NOT langchain.chains.
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain

qa_prompt = ChatPromptTemplate.from_template(
    """You are an assistant for the Bella Vista restaurant.
Answer using only the context below; if it isn't there, say so politely.

Context:
{context}

Question: {input}

Answer:"""
)

combine_docs_chain = create_stuff_documents_chain(llm, qa_prompt)
retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

result = retrieval_chain.invoke({"input": "Is Bella Vista suitable for children?"})

print("Answer:", result["answer"], "\n")
print(f"Grounded in {len(result['context'])} retrieved chunks:")
for doc in result["context"]:
    print(f"  - {doc.page_content.strip()[:70]}...")

%%markdown
#### Legacy contrast: `RetrievalQA`

`RetrievalQA` was the original LangChain RAG chain. It appears throughout older tutorials and in several superseded notebooks in this repository. It is **deprecated** — recognise it, do not write it.

The cell below is kept as a historical contrast, tagged `legacy-contrast`. It is not part of the main path and will emit deprecation warnings.

%%code tags=legacy-contrast
# ============ LEGACY (DEPRECATED): RetrievalQA ============
# Shown for recognition only. Use the LCEL chain or create_retrieval_chain above.
#
# Differences that trip people up when reading old code:
#   - input key is "query", not "question" or "input"
#   - answer comes back under "result"
#   - retrieved documents require return_source_documents=True
#   - the prompt is injected via chain_type_kwargs, not composed
#
# On LangChain 1.x both of these imports moved (see the table above):
#   langchain.chains  -> langchain_classic.chains
#   langchain.prompts -> langchain_core.prompts
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

legacy_prompt = PromptTemplate(
    template="Context:\n{context}\n\nQuestion: {question}\n\nAnswer:",
    input_variables=["context", "question"],
)

legacy_qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",               # stuff every retrieved doc into one prompt
    retriever=retriever,
    chain_type_kwargs={"prompt": legacy_prompt},
    return_source_documents=True,     # otherwise you get no provenance at all
)

legacy_result = legacy_qa.invoke({"query": "What cuisine is served?"})
print("Answer :", legacy_result["result"])
print("Sources:", len(legacy_result["source_documents"]), "documents")

%%markdown
---

## Part 5 — Making the baseline trustworthy

The chain in Part 4 answers questions. It is not yet something you would put in front of a user, because it will answer questions it has no business answering, and it gives you nothing to verify. Three additions fix most of that.

### 5.1 — Carry sources through to the answer

Attaching `source` metadata at load time was the setup; this is the payoff. Label each passage in the context and the model can tell you which ones it used.

%%code
# ============ TRUSTWORTHINESS: SOURCE ATTRIBUTION ============
def format_docs_with_sources(docs) -> str:
    """Number each passage and prefix it with its source, so it can be cited."""
    return "\n\n".join(
        f"[{i}] (source: {doc.metadata.get('source', 'unknown')})\n{doc.page_content}"
        for i, doc in enumerate(docs, start=1)
    )


sourced_prompt = ChatPromptTemplate.from_template(
    """Answer the question using only the context below.
Cite the passage numbers you used, like [1] or [2].

Context:
{context}

Question: {question}

Answer with citations:"""
)

sourced_chain = (
    {"context": retriever | format_docs_with_sources, "question": RunnablePassthrough()}
    | sourced_prompt
    | llm
    | StrOutputParser()
)

print(sourced_chain.invoke("What kind of food does the restaurant serve?"))

%%markdown
This is citation at its most basic: the model is *asked* to cite and usually complies. It is not *verified* citation — nothing here checks that passage [1] actually supports the sentence attached to it. Real attribution needs span-level checking, covered in `05_Context_and_Generation/06_Citations_and_Source_Grounded_Answers.ipynb`.

### 5.2 — Refuse out-of-scope questions

The characteristic RAG failure is confident nonsense about something the corpus never mentioned. Retrieval always returns *something* — its `k` nearest neighbours exist whether or not they are relevant — and a model handed irrelevant context will often answer anyway.

%%code
# ============ TRUSTWORTHINESS: OUT-OF-SCOPE FALLBACK ============
fallback_prompt = ChatPromptTemplate.from_template(
    """Answer the question based ONLY on the context below.
If the answer is not in the context, reply with exactly:
"I don't have information about that in my knowledge base."
Do not use any other knowledge.

Context:
{context}

Question: {question}

Answer:"""
)

fallback_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | fallback_prompt
    | llm
    | StrOutputParser()
)

for q in [
    "What are the opening hours?",              # in the corpus
    "What is the head chef's salary?",          # not in the corpus
    "How do I get a table at the French Laundry?",  # not even the right restaurant
]:
    print(f"Q: {q}")
    print(f"A: {fallback_chain.invoke(q)}\n")

%%markdown
Notice what this fix actually is: **a prompt instruction**. It usually works and it is nearly free, but it is a request, not a guarantee — the model can still ignore it. A stronger version checks retrieval confidence *before* generating and short-circuits when the top score is too weak, and a stronger version still grades the retrieved documents for relevance and re-retrieves when they fail. That is Corrective RAG, in `07_Agentic_RAG/03_Corrective_RAG_CRAG.ipynb`.

### 5.3 — Return structured output

Free-form text is fine for a human reader and awkward for anything else. `with_structured_output` binds a Pydantic model to the LLM and returns a validated object.

%%code
# ============ TRUSTWORTHINESS: STRUCTURED OUTPUT ============
class RAGResponse(BaseModel):
    """A validated, machine-consumable RAG answer."""

    answer: str = Field(description="The answer to the question")
    confidence: str = Field(description="One of: high, medium, low")
    sources_used: List[str] = Field(description="Sources the answer relies on")
    follow_up: str = Field(description="A suggested follow-up question")


structured_llm = llm.with_structured_output(RAGResponse)

structured_chain = (
    {"context": retriever | format_docs_with_sources, "question": RunnablePassthrough()}
    | ChatPromptTemplate.from_template(
        "Context:\n{context}\n\nQuestion: {question}\n\nGive a structured response."
    )
    | structured_llm
)

response = structured_chain.invoke("Do I need to make a reservation?")

print(f"Answer      : {response.answer}")
print(f"Confidence  : {response.confidence}")
print(f"Sources     : {response.sources_used}")
print(f"Follow-up   : {response.follow_up}")
print(f"\nType returned: {type(response).__name__} - a validated object, not a string.")

%%markdown
One caution: `confidence` is the **model's self-report**, and language models are poorly calibrated about their own reliability. It is useful for surfacing hedging to a user; it is not a measurement. Actual measurement is what `06_Evaluation/` is for.

%%markdown
---

## Part 6 — Where this baseline fails

Knowing how to diagnose a bad answer matters more than any single technique. When a RAG system answers wrongly, there are only two possible culprits, and one question separates them:

> **Was the correct passage in the retrieved context?**

Answer it by printing the retrieved chunks — the `similarity_search_with_score` cell in Part 4 is exactly this tool.

- **No** → **retrieval failed.** Generation never had a chance. Fixing the prompt will not help.
- **Yes** → **generation failed.** The evidence was there and the model mishandled it.

Never tune the prompt before answering that question. Most fruitless RAG debugging is prompt-tuning a retrieval problem.

### The specific failure modes of this baseline

| Failure | What you observe | Where it is fixed |
| --- | --- | --- |
| Question phrased unlike the documents | Correct passage never retrieved | `04_Query_Transformation_and_Routing/01_Query_Rewriting_and_Expansion.ipynb`, `.../06_HyDE_Hypothetical_Document_Embeddings.ipynb` |
| Question needs several facts from different places | Partial answer; one fact retrieved, others missed | `04_Query_Transformation_and_Routing/04_Query_Decomposition.ipynb` |
| Exact IDs, codes or rare names not matched | Semantically close but factually wrong chunks | `03_Retrieval/03_Hybrid_Search.ipynb` |
| Top-k full of near-duplicate chunks | Repetitive context, low coverage | `03_Retrieval/04_MMR_and_Diversity_Retrieval.ipynb` |
| Right chunk retrieved but ranked below the cutoff | Answer appears at k=10 but not k=4 | `03_Retrieval/05_Reranking_and_Contextual_Compression.ipynb` |
| Chunk too small to hold the whole answer | Truncated or partial facts | `02_Chunking_and_Indexing/06_Parent_Document_Retrieval.ipynb` |
| Answer needs the corpus summarized, not searched | Retrieval of any k cannot answer it | `08_Advanced_Architectures/01_Hierarchical_Retrieval_and_RAPTOR.ipynb` |
| Retrieval returns irrelevant chunks and the model answers anyway | Confident, unsupported answer | `07_Agentic_RAG/03_Corrective_RAG_CRAG.ipynb` |
| Follow-up questions lose their referent ("what about Sundays?") | Retrieval on a pronoun returns nothing useful | `05_Context_and_Generation/07_Conversational_and_Multi_User_RAG.ipynb` |
| No idea whether any change helped | Vibes-based iteration | `06_Evaluation/` |

### Tradeoffs this baseline made

- **Chunk size 250 / overlap 50** was chosen so overlap is visible in a teaching corpus, not because it is good. Real values are found empirically.
- **`k=4`** trades precision against recall, and against tokens and latency on every request.
- **FAISS in memory** does not survive a restart, does not scale past one machine, and has no access control.
- **Similarity search with no filtering** means every user can retrieve every document — unacceptable in any multi-tenant system. See `10_Production_RAG/01_Enterprise_Access_Control_and_ACL_Retrieval.ipynb`.
- **No evaluation.** Nothing here measures whether the system is any good.

No latency or accuracy numbers are quoted anywhere in this lesson, because none were measured.

%%markdown
---

## Part 7 — Exercise

Package the whole pipeline into a reusable component. `DocumentQA` should index any text document once at construction and answer arbitrary questions against it.

The skeleton below is complete enough to run. Three `TODO`s extend it.

%%code
# ============ EXERCISE: A REUSABLE DOCUMENT Q&A COMPONENT ============
class DocumentQA:
    """Index a text document once, then answer questions about it."""

    def __init__(self, document: str, source_name: str = "document", k: int = 3):
        chunks = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50
        ).split_documents(
            [Document(page_content=document, metadata={"source": source_name})]
        )

        self.vectorstore = FAISS.from_documents(
            chunks, OpenAIEmbeddings(model="text-embedding-3-small")
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        self.llm = get_experientiallabs_llm(temperature=0.2)

        self.chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | ChatPromptTemplate.from_template(
                "Answer from the context only; say you don't know if it isn't there.\n\n"
                "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
            )
            | self.llm
            | StrOutputParser()
        )

    def ask(self, question: str) -> str:
        return self.chain.invoke(question)

    # TODO 1: add `ask_with_evidence(question)` returning both the answer and the
    #         retrieved chunks with their scores, so callers can verify grounding.
    #         Hint: self.vectorstore.similarity_search_with_score
    #
    # TODO 2: refuse to answer when the best retrieval score is too weak, instead
    #         of relying on the prompt. Pick the threshold by trying questions you
    #         KNOW are out of scope and observing the scores - do not guess it.
    #
    # TODO 3: add `add_document(text, source_name)` so the store grows after
    #         construction. Hint: self.vectorstore.add_documents
    #         Then ask yourself: how would you REMOVE a document again?
    #         That question is what 02_Chunking_and_Indexing/05 is about.


sample = """
Python was created by Guido van Rossum and first released in 1991.
It emphasizes code readability and uses significant indentation.
Python 3.12 was released in October 2023 with improved error messages.
The language is named after Monty Python, not the snake.
"""

qa = DocumentQA(sample, source_name="python_facts.txt")
for q in ["Who created Python?", "Why is it called Python?", "What is Python's market share?"]:
    print(f"Q: {q}")
    print(f"A: {qa.ask(q)}\n")

%%markdown
---

## Summary

You built a complete RAG pipeline and saw its shape at every level.

**The four components, across two phases**

| Phase | Steps | Runs |
| --- | --- | --- |
| Indexing | load → split → embed → store | Once, offline |
| Query | retrieve → augment → generate | Per question, online |

**What each step contributed**

- **Load** — external formats become `Document` objects. Metadata attached here is what makes filtering and citation possible later.
- **Split** — chunks must be small enough to be precise and large enough to be complete. Measure them in tokens.
- **Embed** — meaning becomes geometry. The same model must embed documents and queries.
- **Store** — the index answers nearest-neighbour queries. Validate that chunk count equals vector count.
- **Retrieve** — returns a *ranked list with scores*. Those scores are your main debugging instrument.
- **Augment** — a list of documents becomes one context string. How you format it determines whether citation is possible.
- **Generate** — the model reads the supplied evidence instead of recalling from weights.

**The three things that make it trustworthy**: source attribution, an out-of-scope fallback, and structured output. All three are prompt-level and therefore best-effort; stronger guarantees come later.

**The diagnostic that matters most**: when an answer is wrong, print the retrieved chunks and ask whether the correct passage was there. Retrieval failure and generation failure need completely different fixes, and you cannot tell them apart by reading the answer.

### Next lesson

`01_Foundations/02_Document_Loading_and_Metadata.ipynb` — the full loader catalogue and the metadata contracts that everything downstream depends on.

If you would rather follow a failure you hit here, use the table in Part 6 to jump straight to the lesson that fixes it.

%%markdown
---

### Migration record

This notebook is the canonical lesson for concept `RAG-F-01` (RAG lifecycle and baseline pipeline), produced by the basic-RAG pilot batch in `RAG_MIGRATION_MANIFEST.md`.

All six of its source notebooks were retired on 2026-09-10, after this lesson passed full execution validation. They were **moved, not deleted** — preserved byte-for-byte with verified checksums at their original relative paths under `RAG_Curriculum/_archive/`. A seventh, `Naive_RAG_Alt.ipynb`, went with them.

Their input assets did **not** move: `bella_vista.txt` is still in `04_Retrieval_and_RAG/09_RAG_with_LangChain/` and `Transformer.pdf` in `04_Retrieval_and_RAG/shared_data/`. This notebook reads both from there via `rag_paths.asset()`, which is why those files must stay put.

See `RAG_MIGRATION_MANIFEST.md` for each source's disposition, the donor-cell traceability table, and the full dependency mapping.
