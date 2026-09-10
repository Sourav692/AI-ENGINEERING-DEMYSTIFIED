%%markdown
# Document Splitting and Chunking

Lesson 01 split a document with `RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=50)` and moved on, with a note that those numbers were chosen to make overlap visible rather than because they were good.

This is the lesson that takes chunking seriously, because **chunking determines the ceiling on retrieval quality.** A chunk is the unit retrieval returns: too small and the answer is truncated across chunks that arrive separately or not at all; too large and the relevant sentence is diluted by surrounding noise, both in the embedding and in the prompt. No reranker, no query rewriting, and no better model recovers information that chunking destroyed.

The good news is that most of the decision is structural, not numerical. Splitting *at the right boundaries* matters more than splitting *at the right size*.

## Learning objectives

By the end of this notebook you will be able to:

1. **Explain why chunking exists** — three distinct pressures, which sometimes conflict.
2. **Use `RecursiveCharacterTextSplitter` correctly**, including what its separator list actually does and how it degrades.
3. **Choose a splitter by document structure** — Markdown, code, HTML — and explain why structure-aware splitting beats character counting.
4. **Split on tokens rather than characters**, and know when the difference bites.
5. **See what overlap does and does not fix**, and measure the redundancy it costs.
6. **Inspect a chunking outcome** — distribution, outliers, boundary damage — instead of trusting the parameters.

%%markdown
## Prerequisites

**Lessons**

- `01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb` — where splitting sits in the pipeline.
- `01_Foundations/02_Document_Loading_and_Metadata.ipynb` — loaders produce the `Document`s this lesson splits, and load granularity already made part of this decision.
- `01_Foundations/03_Embeddings_and_Model_Selection.ipynb` — chunk length and embedding quality interact.

**Packages**

`langchain-text-splitters`, `langchain-community`, `langchain-core`, `tiktoken`, `pandas`, `pypdf`.

**Services**

None for Parts 1–5. **Splitting is a pure text operation — no API key needed.** Only the optional Part 6 comparison embeds anything.

**Input assets**

`layoutparser_paper.pdf` and `dummy.txt` from `shared_data/`, plus inline samples, all via `rag_paths.asset()`.

%%markdown
## Provenance and runtime status

Consolidated from:

| Source | Contribution |
| --- | --- |
| `04_Retrieval_and_RAG/06_RAG_Naive_to_Production/02_Splitting_and_Chunking/1. Document_Splitters_and_Chunkers.ipynb` | The comprehensive splitter catalogue — fixed, sentence, paragraph, sliding window, recursive, character, code, Markdown, token-based (tiktoken / spaCy / SentenceTransformers), and section-based. 87 cells, the largest single source in this batch. |
| `04_Retrieval_and_RAG/RAG_Production_Course/02_text_splitters.ipynb` | Clearer structure and the chunk-size / overlap comparison framing. |

**Note on the larger source:** `1. Document_Splitters_and_Chunkers.ipynb` reads `../../docs/layoutparser_paper.pdf`, one of the broken paths documented in lesson 02 — that directory does not exist, and the file is in `shared_data/`. It is unrunnable as written, like the eleven loader notebooks.

**Deliberately deferred, not dropped:**

- **Semantic chunking** gets its own lesson (`02_Semantic_Chunking.ipynb`) — it is a different algorithm with a different cost profile, not another splitter setting.
- **Choosing the numbers empirically** is `04_Choosing_Chunk_Size.ipynb`. This lesson explains what the parameters *do*; that one measures which values to use.
- **Context windows and parent-document retrieval** — the "retrieve small, return large" family — are `05_Context_and_Generation/01` and `02_Chunking_and_Indexing/06`. They are retrieval-time answers to chunking-time problems, which is why they are separate.

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

from rag_paths import asset, repo_root

print("Repository root:", repo_root())

%%code
# ============ IMPORTS ============
# stdlib -> third-party -> LangChain
import pandas as pd
import tiktoken

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import (
    CharacterTextSplitter,
    Language,
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
)

encoding = tiktoken.get_encoding("cl100k_base")

print("Imports ready. Parts 1-5 need no API key.")

%%code
# ============ HELPER: INSPECT A CHUNKING OUTCOME ============
# Every experiment below reports the same statistics, so results are
# comparable. Looking at the DISTRIBUTION rather than the parameters is the
# habit this lesson is trying to build.
def profile(chunks, label, show=0):
    """Summarize a list of chunks: count, size distribution, token cost."""
    texts = [c.page_content if isinstance(c, Document) else c for c in chunks]
    chars = [len(t) for t in texts]
    toks = [len(encoding.encode(t)) for t in texts]
    s = pd.Series(chars)
    print(f"{label}")
    print(f"  chunks {len(texts):>4} | chars min/med/max {s.min():>5}/{int(s.median()):>5}/{s.max():>6}"
          f" | tokens total {sum(toks):>6} med {int(pd.Series(toks).median()):>4}")
    for t in texts[:show]:
        print(f"    | {t[:88].strip()!r}")
    return {"label": label, "chunks": len(texts), "median_chars": int(s.median()),
            "max_chars": s.max(), "total_tokens": sum(toks)}

%%markdown
---

## Part 1 — Why chunking exists

Three separate pressures, and it matters that they are separate because they do not always point the same way.

**1. Context limits.** A prompt has a token budget. Retrieving `k=4` chunks of 8,000 tokens each does not fit. This is the constraint everyone knows, and the least interesting.

**2. Retrieval precision.** An embedding is one vector for the whole chunk — a single point representing everything in it. A chunk covering five topics has a vector that is the *average* of five topics, and sits near none of them. Smaller, focused chunks produce vectors that mean one thing.

**3. Signal-to-noise at generation time.** Even with a huge context window, models attend worse to relevant text buried in irrelevant text. Padding the prompt with surrounding paragraphs measurably degrades answers.

Pressures 2 and 3 push toward smaller chunks. But there is a fourth consideration pushing back:

**4. Answer completeness.** A chunk must contain enough to answer on its own. Split a two-sentence definition across two chunks and retrieval returns half an answer — with nothing indicating the other half exists.

**That tension is the whole problem.** Small enough to be precise, large enough to be complete. Which is why later lessons introduce techniques that decouple the two — retrieve on small chunks, return large ones.

%%code
# ============ THE TENSION, MADE CONCRETE ============
policy = (
    "Employees are eligible for the annual training stipend after completing "
    "six months of continuous service. The stipend is $2,000 per calendar year "
    "and covers conference fees, course tuition, and technical books. "
    "Unused stipend does not roll over into the following year."
)

for size in (60, 120, 400):
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=size, chunk_overlap=0
    ).split_text(policy)
    print(f"chunk_size={size} -> {len(chunks)} chunks")
    for c in chunks:
        print(f"   | {c}")
    print()

print("Ask: 'How much is the training stipend and does it roll over?'")
print("At size=60 the amount and the roll-over rule are in DIFFERENT chunks.")
print("Retrieving one gives you half the answer, with no sign the other exists.")

%%markdown
---

## Part 2 — `RecursiveCharacterTextSplitter`

The default, and worth understanding rather than copying. Its behaviour comes entirely from one parameter people rarely look at: `separators`.

```python
separators = ["\n\n", "\n", " ", ""]   # the default
```

The algorithm is: try to split on the first separator. If a resulting piece is still larger than `chunk_size`, recurse into it with the *next* separator. Keep going until pieces fit, or until the separator list is exhausted.

So it splits on **paragraphs** first, falls back to **lines**, then **words**, and only as a last resort cuts mid-word. That ordering is why it is the default — it respects natural boundaries when it can and degrades gracefully when it cannot.

%%code
# ============ WATCHING THE RECURSION DEGRADE ============
structured = (
    "First paragraph about retrieval. It has two sentences.\n\n"
    "Second paragraph about chunking.\n"
    "This line is part of the same paragraph.\n\n"
    "Thirdparagraphwithnospacesatallwhichcannotbesplitonwhitespace"
)

for size in (200, 60, 20):
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=size, chunk_overlap=0
    ).split_text(structured)
    print(f"chunk_size={size}:")
    for c in chunks:
        print(f"   {len(c):>3} chars | {c!r}")
    print()

print("size=200: splits on blank lines - paragraphs stay whole.")
print("size=60 : falls back to single newlines within the long paragraph.")
print("size=20 : the no-space run has no separator left, so it is cut mid-word.")

%%markdown
Two things that surprise people:

**`chunk_size` is a ceiling, not a target.** A paragraph of 30 characters becomes a 30-character chunk. The splitter never pads or merges to reach the target — which is why real chunk sizes are usually well under the configured maximum and why looking at the *distribution* is more informative than the setting.

**Separators are removed by default.** `keep_separator=True` preserves them, which matters when the separator carries meaning — a Markdown heading marker, for instance.

%%code
# ============ CharacterTextSplitter: THE NON-RECURSIVE ONE ============
# Splits on ONE separator, and does not recurse. If a piece is still too big,
# it stays too big - the splitter emits it oversized and warns.
char_chunks = CharacterTextSplitter(
    separator="\n\n", chunk_size=50, chunk_overlap=0
).split_text(structured)

print("CharacterTextSplitter(separator='\\n\\n', chunk_size=50):")
for c in char_chunks:
    flag = "  <-- OVER the limit" if len(c) > 50 else ""
    print(f"   {len(c):>3} chars{flag} | {c[:60]!r}")

print("\nIt splits only on blank lines. Anything between them is emitted whole,")
print("however large. Recursive splitting exists precisely to fix this.")
print("Use CharacterTextSplitter only when you KNOW the separator bounds size.")

%%markdown
---

## Part 3 — Structure-aware splitting

Here is the most valuable idea in this lesson: **if a document has structure, split on the structure, not on a character count.**

A Markdown document has headings. Source code has functions. HTML has sections. These are semantic boundaries the author already placed — vastly better split points than "every 1000 characters".

%%code
# ============ MARKDOWN: SPLIT ON HEADINGS, KEEP THE HIERARCHY ============
markdown_doc = """# Retrieval Augmented Generation

RAG grounds model output in retrieved documents.

## Indexing

Indexing runs once, ahead of time.

### Chunking

Chunks are the unit retrieval returns. Size trades precision against completeness.

### Embedding

Each chunk becomes a vector. The model must match at query time.

## Retrieval

Retrieval runs per query and returns a ranked list.

### Filtering

Metadata filters narrow candidates before similarity search.
"""

header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")]
)
md_chunks = header_splitter.split_text(markdown_doc)

for c in md_chunks:
    trail = " > ".join(c.metadata.get(k, "") for k in ("h1", "h2", "h3") if c.metadata.get(k))
    print(f"[{trail}]")
    print(f"   {c.page_content.strip()[:70]!r}\n")

%%markdown
Look at the metadata: **the heading hierarchy was captured, not discarded.** The chunk containing "Chunks are the unit retrieval returns" knows it lives under *Retrieval Augmented Generation → Indexing → Chunking*.

That is worth a great deal. A chunk reading "Chunks are the unit retrieval returns" is ambiguous on its own; the same chunk labelled with its section path is not. And because that context is in metadata, you can either filter on it or prepend it to the text before embedding — which is exactly the technique `05_Context_and_Generation/02_Contextual_Chunk_Headers_and_Retrieval.ipynb` develops.

%%code
# ============ COMBINING: STRUCTURE FIRST, THEN SIZE ============
# Header splitting alone does not bound chunk size - a long section stays long.
# The standard pattern is to split structurally, THEN size-split the results,
# which preserves the header metadata on every resulting piece.
sized = RecursiveCharacterTextSplitter(chunk_size=80, chunk_overlap=0).split_documents(md_chunks)

print(f"{len(md_chunks)} header sections -> {len(sized)} size-bounded chunks\n")
for c in sized[:4]:
    trail = " > ".join(c.metadata.get(k, "") for k in ("h1", "h2", "h3") if c.metadata.get(k))
    print(f"  [{trail}] {c.page_content.strip()[:56]!r}")

print("\nEvery piece kept its heading metadata through the second split.")
print("This two-stage pattern - structure, then size - is the general recipe.")

%%code
# ============ CODE: SPLIT ON SYNTAX, NOT CHARACTERS ============
# from_language() supplies separators ordered by syntactic significance:
# for Python, class definitions before function definitions before blank lines.
python_source = '''
import numpy as np


class Retriever:
    """Nearest-neighbour retrieval over a dense index."""

    def __init__(self, index):
        self.index = index

    def search(self, query_vector, k=4):
        scores = self.index @ query_vector
        return np.argsort(-scores)[:k]


def build_index(vectors):
    """Stack embedding vectors into a matrix."""
    return np.vstack(vectors)
'''

code_chunks = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON, chunk_size=200, chunk_overlap=0
).split_text(python_source)

for c in code_chunks:
    print(f"--- {len(c)} chars ---")
    print(c.strip()[:170])
    print()

print("Functions and classes stay intact. A character splitter at the same size")
print("would cut through a method body, producing a chunk that is neither")
print("runnable nor comprehensible - and embeds as noise.")

%%code
# ============ THE SEPARATORS EACH LANGUAGE USES ============
for lang in (Language.PYTHON, Language.MARKDOWN, Language.HTML):
    seps = RecursiveCharacterTextSplitter.get_separators_for_language(lang)
    print(f"{lang.value:<10} {seps[:6]}")

print("\nOrdered most-significant first - exactly the recursion from Part 2,")
print("with separators that mean something in that language.")

%%markdown
---

## Part 4 — Tokens, not characters

`chunk_size` counts **characters** by default. Everything downstream counts **tokens**. The ratio varies with content, so a character limit gives you inconsistent token sizes — and token size is what determines cost and what fits.

%%code
# ============ THE CHARACTER-TO-TOKEN RATIO IS NOT CONSTANT ============
samples = {
    "English prose": "The quick brown fox jumps over the lazy dog near the river bank.",
    "Python code": "def f(x, y=None): return [i**2 for i in range(x) if i % 2 == 0]",
    "A URL": "https://example.com/api/v2/documents?filter=active&sort=created_at",
    "German": "Donaudampfschifffahrtsgesellschaftskapitaen ist ein langes Wort.",
    "JSON": '{"id": 4471, "status": "resolved", "tags": ["export", "timeout"]}',
}

rows = []
for name, text in samples.items():
    n_tok = len(encoding.encode(text))
    rows.append({"sample": name, "chars": len(text), "tokens": n_tok,
                 "chars/token": round(len(text) / n_tok, 2)})

print(pd.DataFrame(rows).to_string(index=False))
print("\nEnglish prose runs ~4 chars/token. Code, URLs and compound-word")
print("languages run far denser. At these ratios a chunk_size of 1000")
print("CHARACTERS is ~220 tokens of prose but ~430 tokens of code - roughly")
print("double, from the same setting.")

%%code
# ============ SPLITTING BY TOKENS ============
text = asset("dummy.txt").read_text(encoding="utf-8")

by_chars = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=0).split_text(text)
by_tokens = TokenTextSplitter(chunk_size=100, chunk_overlap=0).split_text(text)

# Same target (~100 tokens), two different ways of getting there.
c_tok = [len(encoding.encode(c)) for c in by_chars]
t_tok = [len(encoding.encode(c)) for c in by_tokens]

print(f"{'splitter':<28} {'chunks':>7} {'min':>5} {'median':>7} {'max':>5}  (tokens)")
print(f"{'chars=400 (~100 tokens)':<28} {len(by_chars):>7} {min(c_tok):>5} "
      f"{int(pd.Series(c_tok).median()):>7} {max(c_tok):>5}")
print(f"{'tokens=100':<28} {len(by_tokens):>7} {min(t_tok):>5} "
      f"{int(pd.Series(t_tok).median()):>7} {max(t_tok):>5}")

print("\nToken splitting gives a tight, predictable distribution.")
print("Character splitting varies with the text.")

%%markdown
**But `TokenTextSplitter` ignores structure.** It splits at exactly N tokens, cheerfully cutting mid-sentence — it has no separator list at all.

The best of both is `RecursiveCharacterTextSplitter.from_tiktoken_encoder()`: recursive structural splitting, with the size *measured* in tokens.

%%code
# ============ RECURSIVE SPLITTING, MEASURED IN TOKENS ============
hybrid = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=100,          # tokens, not characters
    chunk_overlap=0,
).split_text(text)

h_tok = [len(encoding.encode(c)) for c in hybrid]
print(f"from_tiktoken_encoder: {len(hybrid)} chunks, "
      f"tokens min/med/max {min(h_tok)}/{int(pd.Series(h_tok).median())}/{max(h_tok)}")

print("\nBoundaries (last 40 chars of each chunk) - note they land on sentence ends:")
for c in hybrid[:3]:
    print(f"   ...{c[-40:]!r}")

print("\nTokenTextSplitter for comparison - mid-sentence cuts:")
for c in by_tokens[:3]:
    print(f"   ...{c[-40:]!r}")

%%markdown
**This is the recommended default for prose:** `RecursiveCharacterTextSplitter.from_tiktoken_encoder()`. Structural boundaries, token-accurate sizes.

%%markdown
---

## Part 5 — What overlap actually does

Overlap repeats the tail of one chunk at the head of the next, so a sentence spanning a boundary survives intact somewhere. It is real insurance — and it is not free, and it does not do what people often assume.

%%code
# ============ OVERLAP: THE FIX AND THE COST ============
doc = (
    "The retention period is thirty days. After that, records are purged "
    "automatically and cannot be recovered. Customers on the enterprise plan "
    "may request an extended retention period of up to one year."
)

for ov in (0, 20, 60):
    chunks = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=ov).split_text(doc)
    total = sum(len(c) for c in chunks)
    print(f"overlap={ov:>2}: {len(chunks)} chunks, {total} chars stored "
          f"({total / len(doc):.2f}x the original)")
    for c in chunks:
        print(f"     | {c}")
    print()

print("Overlap buys boundary safety and costs storage, embedding calls, and")
print("index size - all multiplied by that ratio. 10-20% of chunk_size is the")
print("usual compromise.")

%%markdown
Two things overlap does **not** fix:

**It does not reunite distant facts.** Overlap of 50 characters helps a sentence that straddles a boundary. It does nothing for the Part 1 case where the amount and the roll-over rule are 200 characters apart — that needs a bigger chunk, or parent-document retrieval.

**It creates near-duplicate chunks.** Two chunks sharing 20% of their text embed to nearby vectors, so both can occupy top-k slots for the same query — spending two of your `k` on one region of the document. This is one of the problems MMR addresses (`03_Retrieval/04_MMR_and_Diversity_Retrieval.ipynb`).

Overlap is a hedge against boundary damage, not a solution to chunk sizing.

%%markdown
---

## Part 6 — Inspect the outcome, not the parameters

Chunking is configured with two numbers and evaluated by looking at the result. Anyone who reports "I used 1000/200" without looking at the distribution is guessing.

%%code
# ============ PROFILING A REAL DOCUMENT ============
pages = PyPDFLoader(str(asset("layoutparser_paper.pdf"))).load()
print(f"Loaded {len(pages)} pages (PyPDFLoader gives one Document per page)\n")

results = []
for name, splitter in [
    ("recursive chars=1000/200",
     RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)),
    ("recursive tokens=250/50",
     RecursiveCharacterTextSplitter.from_tiktoken_encoder(
         encoding_name="cl100k_base", chunk_size=250, chunk_overlap=50)),
    ("token-only tokens=250/50",
     TokenTextSplitter(chunk_size=250, chunk_overlap=50)),
    ("character-only \\n\\n, 1000",
     CharacterTextSplitter(separator="\n\n", chunk_size=1000, chunk_overlap=200)),
]:
    results.append(profile(splitter.split_documents(pages), name))

print()
print(pd.DataFrame(results).to_string(index=False))

%%markdown
The `max_chars` column is the diagnostic. A maximum far above `chunk_size` means the splitter ran out of separators and emitted oversized chunks — for `CharacterTextSplitter` that is routine, and those chunks may not fit your context budget or may exceed the embedding model's input limit.

%%code
# ============ FINDING THE DAMAGE ============
chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(pages)
sizes = pd.Series([len(c.page_content) for c in chunks])

print("Chunk size distribution:")
print(sizes.describe().to_string())

tiny = [c for c in chunks if len(c.page_content.strip()) < 100]
print(f"\nSuspiciously small chunks (<100 chars): {len(tiny)} of {len(chunks)}")
for c in tiny[:4]:
    print(f"   p{c.metadata.get('page', '?')}: {c.page_content.strip()[:70]!r}")

print("\nThese are page headers, footers, figure captions and reference")
print("fragments - orphaned by the page-per-Document load granularity. They")
print("embed as noise and occupy index space. Filtering them out before")
print("indexing is usually worth it.")

%%code
# ============ A MINIMUM-LENGTH FILTER ============
MIN_CHARS = 100
kept = [c for c in chunks if len(c.page_content.strip()) >= MIN_CHARS]

print(f"before filter: {len(chunks)} chunks, "
      f"{sum(len(encoding.encode(c.page_content)) for c in chunks):,} tokens")
print(f"after  filter: {len(kept)} chunks, "
      f"{sum(len(encoding.encode(c.page_content)) for c in kept):,} tokens")
print(f"removed {len(chunks) - len(kept)} fragments "
      f"({(len(chunks) - len(kept)) / len(chunks):.0%} of chunks)")

print("\nCaution: check what you are discarding before adopting a threshold.")
print("A short chunk can be a real answer - a definition, a table row, a date.")
print("Print the rejects, as the previous cell did, rather than trusting a number.")

%%markdown
---

## Part 7 — Choosing a splitter

| Content | Splitter | Why |
| --- | --- | --- |
| **Prose (default)** | `RecursiveCharacterTextSplitter.from_tiktoken_encoder()` | Structural boundaries, token-accurate sizing |
| **Markdown** | `MarkdownHeaderTextSplitter`, then a size split | Preserves the heading hierarchy as metadata |
| **Source code** | `RecursiveCharacterTextSplitter.from_language()` | Keeps functions and classes whole |
| **HTML** | `HTMLHeaderTextSplitter` / `HTMLSectionSplitter` | Section structure, tags stripped |
| **Fixed token budget** | `TokenTextSplitter` | Exact sizes; ignores structure |
| **One separator you trust** | `CharacterTextSplitter` | Simple; emits oversized chunks without recursion |
| **Topic-shifting prose** | `SemanticChunker` | Next lesson — boundaries from meaning, not markup |

The decision procedure, in order:

1. **Does the document have structure?** Use it. This matters more than any number.
2. **Split by tokens, not characters** — via `from_tiktoken_encoder`.
3. **Start at ~250–500 tokens with 10–20% overlap**, then measure. `04_Choosing_Chunk_Size.ipynb` measures.
4. **Profile the result.** Look at the distribution, read the outliers, filter obvious junk.
5. **If precision and completeness genuinely conflict**, stop tuning size and decouple them — parent-document retrieval (`06`) or context windows (`05_Context_and_Generation/01`).

%%markdown
---

## Limitations and tradeoffs

**No quality numbers here.** This lesson shows what each splitter *does* to text. Whether a configuration retrieves better is an empirical question requiring a labelled set — `04_Choosing_Chunk_Size.ipynb` and `06_Evaluation/`.

**Load granularity already constrained this.** `PyPDFLoader` gave one Document per page, so no chunk can span a page boundary and page headers arrive as separate fragments. Lesson 02's granularity decision is upstream of everything here.

**PDF structure is reconstructed, not read.** Section headings in a PDF are visual, not semantic — which is why `MarkdownHeaderTextSplitter` has no PDF equivalent. Recovering structure from PDFs needs layout analysis (`unstructured`, or `09_Multimodal_RAG/`).

**Tables and code blocks in prose survive badly.** A character or token splitter will cut a table in half. If your corpus is full of them, extract and handle them separately.

**Chunking interacts with the embedding model's input limit.** A chunk exceeding it is silently truncated by some providers — the tail is never embedded, and nothing tells you.

**One size rarely fits a mixed corpus.** API docs, narrative prose and meeting transcripts want different settings. Routing by document type is legitimate and underused.

%%markdown
---

## Exercise

Build a `ChunkingProfile` that applies a strategy and reports enough to judge it — because the point of this lesson is that you inspect outcomes rather than trusting parameters.

%%code
# ============ EXERCISE: A CHUNKING STRATEGY WITH A REPORT ============
class ChunkingProfile:
    """Apply a chunking strategy and report what it did."""

    def __init__(self, chunk_size=250, chunk_overlap=50, min_chars=100):
        self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.min_chars = min_chars

    def run(self, documents: list[Document]) -> tuple[list[Document], dict]:
        raw = self.splitter.split_documents(documents)
        kept = [c for c in raw if len(c.page_content.strip()) >= self.min_chars]
        toks = [len(encoding.encode(c.page_content)) for c in kept]
        chars = pd.Series([len(c.page_content) for c in kept])
        original = sum(len(d.page_content) for d in documents)
        return kept, {
            "input_docs": len(documents),
            "chunks_raw": len(raw),
            "chunks_kept": len(kept),
            "dropped_as_fragments": len(raw) - len(kept),
            "median_tokens": int(pd.Series(toks).median()),
            "max_tokens": max(toks),
            "total_tokens": sum(toks),
            "redundancy": round(chars.sum() / original, 2),
        }

    # TODO 1: `redundancy` above measures storage inflation from overlap. Plot
    #         it against chunk_overlap. At what overlap does the cost stop
    #         buying you anything? (You need a retrieval metric to answer that
    #         properly - see 04_Choosing_Chunk_Size.)
    #
    # TODO 2: add boundary-quality checking: what fraction of chunks END on a
    #         sentence terminator? Compare RecursiveCharacterTextSplitter
    #         against TokenTextSplitter on the same text.
    #
    # TODO 3: make it dispatch by document type - use the Markdown header
    #         splitter for .md, from_language() for code, this for prose.
    #         Which metadata field from lesson 02 tells you the type?


profiler = ChunkingProfile(chunk_size=250, chunk_overlap=50)
kept, report = profiler.run(pages)

for k, v in report.items():
    print(f"  {k:<22} {v}")

print(f"\nSample chunk (page {kept[3].metadata.get('page')}):")
print(f"  {kept[3].page_content[:200].strip()!r}")

%%markdown
---

## Summary

**Chunking sets the ceiling on retrieval quality.** The chunk is the unit retrieval returns; information destroyed here is not recoverable downstream.

**The core tension:** small enough to be precise (a focused vector, a clean prompt), large enough to be complete (the whole answer in one chunk). When they genuinely conflict, decouple them rather than compromising — that is what parent-document retrieval is for.

**Split on structure first.** Markdown headings, code syntax, HTML sections are boundaries the author already placed. `MarkdownHeaderTextSplitter` additionally captures the heading path as metadata, which is valuable well beyond splitting.

**The two-stage recipe:** structural split, then size split. Metadata survives both.

**Measure in tokens, not characters.** The ratio varies 2× or more across content types. `RecursiveCharacterTextSplitter.from_tiktoken_encoder()` gives structural boundaries with token-accurate sizes, and is the right default for prose.

**Overlap is boundary insurance**, costing storage and creating near-duplicate chunks that compete for top-k slots. 10–20% is the usual compromise. It does not reunite facts that are far apart.

**Inspect the outcome.** Distribution, oversized chunks, tiny fragments — read them, don't trust the parameters. `chunk_size` is a ceiling, and real chunks are usually well below it.

### Next lesson

`02_Chunking_and_Indexing/02_Semantic_Chunking.ipynb` — placing boundaries where the *meaning* changes rather than where the character count runs out, and what that costs.

%%markdown
---

### Migration record

Canonical lesson for concept `RAG-CI-01` (document splitting and chunking), Chunking & Indexing batch.

Consolidates `06_RAG_Naive_to_Production/02_Splitting_and_Chunking/1. Document_Splitters_and_Chunkers.ipynb` (87 cells) and `RAG_Production_Course/02_text_splitters.ipynb`. The larger source is unrunnable as written — it reads `../../docs/layoutparser_paper.pdf`, one of the non-existent paths documented in lesson 02; the file is in `shared_data/` and is reached here via `rag_paths.asset()`.

Semantic chunking, empirical size selection, and the retrieve-small/return-large family were deliberately deferred to their own lessons rather than folded in here. See `RAG_MIGRATION_MANIFEST.md`.
