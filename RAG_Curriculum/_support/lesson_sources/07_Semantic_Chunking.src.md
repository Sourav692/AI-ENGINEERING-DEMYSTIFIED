%%markdown
# Semantic Chunking

Every splitter in the previous lesson decides where to cut by counting — characters, tokens, or occurrences of a separator. None of them read the text. A `RecursiveCharacterTextSplitter` will happily cut between a claim and its supporting evidence because that is where character 1000 fell, and it will just as happily glue two unrelated topics together because they happened to fit.

Semantic chunking asks a different question: **where does the meaning change?** It embeds the sentences, measures how much consecutive sentences differ, and cuts where the difference spikes.

It is a genuinely better idea, and it is not free. This lesson covers how it works, builds it from scratch so the mechanism is visible, uses the library version, and — most importantly — establishes when the extra cost is and is not worth paying.

## Learning objectives

By the end of this notebook you will be able to:

1. **Explain the algorithm**: sentence-split, embed, measure consecutive distance, threshold, group.
2. **Implement it from scratch** in about fifteen lines, so `SemanticChunker` stops being a black box.
3. **Use `SemanticChunker`** and choose between its four breakpoint threshold types.
4. **See the boundaries it finds** that a character splitter misses — on text with a deliberate topic shift.
5. **Account for its costs**: an embedding pass over every sentence at index time, unbounded chunk sizes, and sensitivity to sentence segmentation.
6. **Decide when to use it**, which is not always.

%%markdown
## Prerequisites

**Lessons**

- `02_Chunking_and_Indexing/01_Document_Splitting_and_Chunking.ipynb` — the splitters this improves on, and the tension it addresses.
- `01_Foundations/03_Embeddings_and_Model_Selection.ipynb` — cosine similarity and normalization; this lesson computes distances directly.

**Packages**

`langchain-experimental` (for `SemanticChunker`), `langchain-openai`, `langchain-text-splitters`, `numpy`, `pandas`.

`SemanticChunker` lives in `langchain_experimental`, not `langchain`. The name is a real signal: the API has changed before and may change again.

**Services**

`OPENAI_API_KEY`. Unlike the previous lesson, **semantic chunking requires embeddings at chunk time** — that is the central cost, and Part 5 measures it.

**Input assets**

`langchain_intro.txt`, resolved via `rag_paths.asset()`. It is a short file with a deliberate topic shift, which is exactly what this lesson needs to demonstrate.

%%markdown
## Provenance and runtime status

Consolidated from:

| Source | Contribution |
| --- | --- |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/semantic_chunking.ipynb` | `SemanticChunker` usage and the breakpoint-threshold types. |
| `04_Retrieval_and_RAG/06_RAG_Naive_to_Production/02_Splitting_and_Chunking/2. Semantichunking.ipynb` | The from-scratch implementation, and `langchain_intro.txt` — a corpus built specifically to have a topic shift. |

**A defect in the second source:** it is written entirely against LangChain 0.x — `langchain.chat_models`, `langchain.document_loaders`, `langchain.vectorstores`, `langchain.schema`, `langchain.prompts`. All of those raise `ModuleNotFoundError` on this repository's LangChain 1.4. It also depends on `sentence_transformers`, which is not installed here (the `hf` extra). It cannot run as written.

**Added here, present in neither source:** the cost measurement in Part 5, the comparison against a character splitter on the same text, and the guidance on when *not* to use semantic chunking. Both sources demonstrate the technique working and stop there.

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

%%code
# ============ IMPORTS AND ENVIRONMENT ============
import re
import time

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(repo_root() / ".env")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

print("Ready:", embeddings.model)

%%code
# ============ THE CORPUS ============
# Deliberately constructed: it talks about LangChain, then abruptly switches
# to Paris and France. A character splitter has no way to notice that.
text = asset("langchain_intro.txt").read_text(encoding="utf-8").strip()

print(f"{len(text)} characters\n")
for i, line in enumerate(text.splitlines()):
    print(f"  {i}: {line}")

%%markdown
---

## Part 1 — What a character splitter does with this

Before introducing the new technique, establish the baseline honestly: what does the previous lesson's default do here, and is it actually wrong?

%%code
# ============ BASELINE: RECURSIVE CHARACTER SPLITTING ============
baseline = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=0).split_text(text)

print(f"RecursiveCharacterTextSplitter(150) -> {len(baseline)} chunks\n")
for i, c in enumerate(baseline):
    print(f"--- chunk {i} ({len(c)} chars) ---")
    print(c)
    print()

%%markdown
Look at whether any chunk mixes the LangChain material with the Paris material. At this size the split may land near the topic boundary by luck — the paragraph break is there, and `RecursiveCharacterTextSplitter` splits on `\n` before falling back to words.

**That is worth stating plainly: on well-structured text, character splitting often gets the boundary right for free**, because authors already mark topic changes with paragraph breaks. Semantic chunking earns its cost on text where that structure is *absent or misleading* — transcripts, OCR output, scraped pages, or long unbroken prose.

Watch what happens when the structural cue is removed.

%%code
# ============ THE HARD CASE: STRUCTURE REMOVED ============
# Collapse the newlines. Now there is no paragraph break to split on - the
# text is one continuous run, and the topic shift is invisible to any
# character-counting splitter.
flat = " ".join(line.strip() for line in text.splitlines() if line.strip())
print(f"{len(flat)} characters, no line breaks:\n")
print(flat)

flat_chunks = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=0).split_text(flat)
print(f"\n-> {len(flat_chunks)} chunks\n")
for i, c in enumerate(flat_chunks):
    print(f"--- chunk {i} ---")
    print(c)
    print()

%%markdown
Now inspect the chunks: one of them contains the tail of the LangChain material *and* both France sentences. The cut landed where the character count expired, which is mid-topic.

That chunk's embedding is a blend of two unrelated subjects, so it sits between them rather than squarely on either. Part 4 measures exactly how much that costs — it is a smaller effect than you might expect on a five-sentence corpus, and a decisive one at scale.

This is the failure semantic chunking exists to fix.

%%markdown
---

## Part 2 — The algorithm, from scratch

Five steps. Implementing it takes about fifteen lines, and doing so makes every parameter of the library version obvious.

1. **Split into sentences** — the atomic units that will be grouped.
2. **Embed each sentence.**
3. **Measure the distance between consecutive sentences** — `1 - cosine similarity`.
4. **Pick a threshold.** Distances above it are topic boundaries.
5. **Group** the sentences between boundaries into chunks.

%%code
# ============ STEP 1: SENTENCES ============
# A regex is crude - it mishandles "Dr.", "e.g.", decimals - but it makes the
# dependency visible. Everything downstream inherits these boundaries.
sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", flat) if s.strip()]

print(f"{len(sentences)} sentences:")
for i, s in enumerate(sentences):
    print(f"  {i}: {s}")

%%code
# ============ STEPS 2-3: EMBED, THEN MEASURE CONSECUTIVE DISTANCE ============
vecs = np.array(embeddings.embed_documents(sentences))   # one batched call

# Unit vectors (lesson 03), so dot product is cosine similarity.
distances = [1.0 - float(vecs[i] @ vecs[i + 1]) for i in range(len(vecs) - 1)]

print(f"{'gap':>5}  {'distance':>9}   between")
for i, d in enumerate(distances):
    print(f"{i:>2}-{i+1:<2} {d:>9.4f}   {sentences[i][:34]!r} | {sentences[i+1][:34]!r}")

print(f"\nmean {np.mean(distances):.4f}   max {np.max(distances):.4f} "
      f"at gap {int(np.argmax(distances))}-{int(np.argmax(distances)) + 1}")

%%markdown
The distance series is the whole signal. Consecutive sentences on the same topic sit close together; the sentence that changes subject shows a spike.

Note that this measures **local** change only — sentence *i* against sentence *i+1*. It has no notion of a chunk drifting gradually off-topic over five sentences, none of which differs much from its neighbour. Gradual drift is invisible to this method.

%%code
# ============ STEPS 4-5: THRESHOLD AND GROUP ============
# Percentile thresholding: treat the top X% of distances as boundaries.
# Absolute thresholds do not transfer between texts or embedding models;
# a percentile adapts to the distribution at hand.
def semantic_chunks(sentences, distances, percentile=90):
    if not distances:
        return sentences
    cutoff = np.percentile(distances, percentile)
    breaks = [i for i, d in enumerate(distances) if d > cutoff]

    chunks, start = [], 0
    for b in breaks:
        chunks.append(" ".join(sentences[start:b + 1]))
        start = b + 1
    chunks.append(" ".join(sentences[start:]))
    return [c for c in chunks if c.strip()], cutoff, breaks


chunks, cutoff, breaks = semantic_chunks(sentences, distances, percentile=90)

print(f"cutoff (90th percentile) = {cutoff:.4f}")
print(f"boundaries after sentences: {breaks}\n")
for i, c in enumerate(chunks):
    print(f"--- chunk {i} ({len(c)} chars) ---")
    print(c)
    print()

%%markdown
Compare that against the flat-text character chunks from Part 1. The boundary should now fall exactly where the subject changes — because that is what was measured, rather than where a character count expired.

%%markdown
---

## Part 3 — `SemanticChunker`

The library version does the same five steps with more care: a better sentence splitter, a configurable buffer that compares small *groups* of sentences rather than single ones, and four threshold strategies.

%%code
# ============ SemanticChunker: THE LIBRARY IMPLEMENTATION ============
chunker = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=90,
)

t0 = time.perf_counter()
lib_chunks = chunker.split_text(flat)
elapsed = time.perf_counter() - t0

print(f"SemanticChunker -> {len(lib_chunks)} chunks in {elapsed:.2f}s\n")
for i, c in enumerate(lib_chunks):
    print(f"--- chunk {i} ({len(c)} chars) ---")
    print(c)
    print()

%%markdown
### The four threshold types

| `breakpoint_threshold_type` | Splits when a distance is… | `breakpoint_threshold_amount` | Behaviour |
| --- | --- | --- | --- |
| `"percentile"` (default) | above the Nth percentile | 95 | Predictable chunk *count*; always finds boundaries even in uniform text |
| `"standard_deviation"` | more than N σ above the mean | 3 | Finds genuine outliers; may find none at all |
| `"interquartile"` | beyond N × IQR | 1.5 | Robust to a few extreme values |
| `"gradient"` | at a peak in the *rate of change* | 95 | For text where topics shift gradually rather than abruptly |

The distinction that matters: **`percentile` always splits** — the 95th percentile of any distribution exists, even if the text never changes topic. `standard_deviation` and `interquartile` can legitimately return one chunk for a document that is genuinely about one thing.

%%code
# ============ COMPARING THRESHOLD TYPES ============
rows = []
for ttype, amount in [
    ("percentile", 90),
    ("percentile", 95),
    ("standard_deviation", 1.0),
    ("standard_deviation", 3.0),
    ("interquartile", 1.5),
]:
    out = SemanticChunker(
        embeddings,
        breakpoint_threshold_type=ttype,
        breakpoint_threshold_amount=amount,
    ).split_text(flat)
    sizes = [len(c) for c in out]
    rows.append({"type": ttype, "amount": amount, "chunks": len(out),
                 "min_chars": min(sizes), "max_chars": max(sizes)})

print(pd.DataFrame(rows).to_string(index=False))
print("\nNote `standard_deviation` at 3.0: on a short text with few sentences,")
print("no distance is 3 sigma above the mean, so it returns ONE chunk.")
print("That is correct behaviour, not a failure - but it means chunk sizes")
print("are unbounded, which Part 5 returns to.")

%%markdown
---

## Part 4 — Verifying the boundary is real

A chunking method that produces boundaries is easy. Producing boundaries that *help retrieval* is the claim, and it is checkable: chunks about one topic should be close to that topic's query and far from the other's.

%%code
# ============ DO THE CHUNKS SEPARATE CLEANLY? ============
queries = {
    "framework query": "What is LangChain used for?",
    "geography query": "Where is the Eiffel Tower?",
}
q_vecs = {k: np.array(embeddings.embed_query(v)) for k, v in queries.items()}


def separation(chunk_list, label):
    """Similarity of each chunk to each query, and the MARGIN between them.

    Margin is the signal: a topically clean chunk is much closer to one query
    than the other. A mixed chunk sits between them and serves neither well.
    """
    c_vecs = np.array(embeddings.embed_documents(chunk_list))
    print(f"{label}")
    print(f"  {'chunk':>5} {'framework':>10} {'geography':>10} {'margin':>8}")
    margins = []
    for i, cv in enumerate(c_vecs):
        a = float(cv @ q_vecs["framework query"])
        b = float(cv @ q_vecs["geography query"])
        margins.append(abs(a - b))
        print(f"  {i:>5} {a:>10.4f} {b:>10.4f} {abs(a - b):>8.4f}")
    print(f"  mean margin: {np.mean(margins):.4f}")
    print()
    return float(np.mean(margins))


m_char = separation(flat_chunks, "Character splitter on flat text:")
m_sem = separation(lib_chunks, "SemanticChunker on the same text:")
print(f"Semantic chunking sharpened the mean margin "
      f"{m_char:.4f} -> {m_sem:.4f} ({m_sem / m_char:.2f}x)")

%%markdown
**Read the `margin` column, not the verdicts.** Both methods put each chunk nearer one query than the other — the character splitter is not catastrophically wrong here. The difference is *how decisively*.

The character splitter's second chunk contains the tail of the LangChain material *and* both France sentences. Its vector is a blend, so it lands between the two queries: still closer to geography, but with a smaller margin. Semantic chunking cuts exactly at the topic change, so each chunk is about one thing and the margin roughly doubles.

That margin is what determines whether the right chunk beats a competitor in a large index. On a five-sentence corpus a blended chunk still wins its query; among a hundred thousand chunks it does not. This is the same reasoning as the `margin` metric in `01_Foundations/03` — a binary hit/miss verdict saturates and stops discriminating, while the margin keeps telling you something.

Measure this on your own corpus before adopting the technique, rather than taking it on faith.

%%markdown
---

## Part 5 — The cost

Semantic chunking embeds every sentence in your corpus **before** you embed the chunks. That is an extra full pass over all your text at index time.

%%code
# ============ MEASURING THE OVERHEAD ============
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")
corpus_tokens = len(enc.encode(flat))

t0 = time.perf_counter()
RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=0).split_text(flat)
t_char = time.perf_counter() - t0

t0 = time.perf_counter()
SemanticChunker(embeddings, breakpoint_threshold_type="percentile",
                breakpoint_threshold_amount=90).split_text(flat)
t_sem = time.perf_counter() - t0

print(f"{'method':<26} {'seconds':>9}  {'embeds text?':>13}")
print(f"{'RecursiveCharacter':<26} {t_char:>9.4f}  {'no':>13}")
print(f"{'SemanticChunker':<26} {t_sem:>9.4f}  {'yes':>13}")
print(f"\nratio: {t_sem / max(t_char, 1e-9):,.0f}x slower on {corpus_tokens} tokens")
print()
print("Character splitting is pure string manipulation - microseconds, free.")
print("Semantic chunking is network-bound: one embedding pass over every")
print("sentence, then the usual pass over the resulting chunks.")

%%markdown
Extrapolate honestly. On a 10-million-token corpus semantic chunking means embedding roughly 10 million tokens *twice* — once by sentence to find boundaries, once by chunk to index. It roughly doubles index-time embedding cost and adds substantial wall time.

Two further costs that are easy to miss:

**Chunk sizes are unbounded.** Nothing in the algorithm caps a chunk. A long stretch on one topic becomes one enormous chunk, which may exceed your embedding model's input limit (silently truncated by some providers) or blow your prompt budget at retrieval time. The mitigation is a second size-bounded split afterwards — the two-stage pattern from the previous lesson.

**It inherits its sentence splitter's mistakes.** Bad sentence segmentation means bad candidate boundaries, and no threshold tuning recovers from that. Abbreviations, decimals, bullet lists and transcripts without punctuation all degrade it.

%%code
# ============ BOUNDING THE OUTPUT ============
# The safe pattern: semantic boundaries first, then a size ceiling.
semantic = SemanticChunker(embeddings, breakpoint_threshold_type="percentile",
                           breakpoint_threshold_amount=90).split_text(flat)
bounded = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base", chunk_size=60, chunk_overlap=0
).split_text("\n\n".join(semantic))

print(f"semantic only     : {len(semantic)} chunks, "
      f"max {max(len(c) for c in semantic)} chars")
print(f"semantic + bounded: {len(bounded)} chunks, "
      f"max {max(len(c) for c in bounded)} chars")
print("\nTopic boundaries are respected first; the size split only intervenes")
print("where a topic ran longer than the ceiling.")

%%markdown
---

## Part 6 — When to use it

**Use semantic chunking when:**

- The text lacks reliable structure — transcripts, OCR, scraped pages, unbroken prose.
- Topics shift *within* documents in ways paragraph breaks do not mark.
- Retrieval quality matters more than index cost, and the corpus is small enough that a doubled embedding pass is affordable.
- You have measured it, on your corpus, and it helps.

**Do not use it when:**

- The document already has structure. Markdown headings, code syntax and HTML sections are *author-supplied* boundaries — better signal than inferred ones, and free. Reach for the previous lesson's structure-aware splitters first.
- The corpus is very large. Doubling index-time embedding cost is a real budget line.
- Content is uniform — API reference pages, product records, log entries. If every entry is about one thing, there is no topic shift to find.
- You have not measured it. It is intuitively appealing, which makes it easy to adopt on faith. Part 4 shows how to check.

**The honest summary:** semantic chunking is the right tool for a specific problem — unstructured text with internal topic shifts — and is often outperformed on structured documents by a `MarkdownHeaderTextSplitter` that costs nothing. Try structure first.

%%markdown
---

## Limitations and tradeoffs

**One 292-character file.** Everything measured here is a demonstration of method, not a result. The separation numbers in Part 4 come from a corpus built to have exactly one obvious topic shift.

**Only local change is detected.** Sentence *i* against *i+1*. A chunk that drifts gradually across five sentences never triggers a boundary. `gradient` thresholding helps somewhat; nothing solves it fully.

**`langchain_experimental` is experimental.** The package name is the warning. Pin the version if you depend on this in production.

**Threshold values do not transfer.** A percentile tuned on legal contracts will misbehave on chat transcripts. It is a per-corpus parameter, and the percentile types will always find *something* to split on.

**It is orthogonal to the completeness problem.** Semantic chunking places boundaries better; it does not solve "the chunk is too small to contain the whole answer". That is still parent-document retrieval (`06`) or context windows.

%%markdown
---

## Exercise

Build a `SemanticChunkingReport` that decides whether semantic chunking is worth it for a given text, rather than assuming.

%%code
# ============ EXERCISE: IS IT WORTH IT HERE? ============
class SemanticChunkingReport:
    """Compare semantic against character chunking on one text, with evidence."""

    def __init__(self, embeddings, target_chars=150):
        self.embeddings = embeddings
        self.target_chars = target_chars

    def analyse(self, text: str, percentile: int = 90) -> dict:
        char_chunks = RecursiveCharacterTextSplitter(
            chunk_size=self.target_chars, chunk_overlap=0
        ).split_text(text)
        sem_chunks = SemanticChunker(
            self.embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=percentile,
        ).split_text(text)

        # How separable are the distances? A text with a real topic shift has
        # a high max-to-median ratio; uniform text does not.
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        v = np.array(self.embeddings.embed_documents(sents))
        d = [1.0 - float(v[i] @ v[i + 1]) for i in range(len(v) - 1)] or [0.0]

        return {
            "sentences": len(sents),
            "char_chunks": len(char_chunks),
            "semantic_chunks": len(sem_chunks),
            "semantic_max_chars": max(len(c) for c in sem_chunks),
            "distance_median": round(float(np.median(d)), 4),
            "distance_max": round(float(np.max(d)), 4),
            "peak_ratio": round(float(np.max(d) / max(np.median(d), 1e-9)), 2),
            "verdict": ("worth trying - distances have a clear peak"
                        if np.max(d) / max(np.median(d), 1e-9) > 1.5
                        else "probably not - distances are uniform"),
        }

    # TODO 1: `peak_ratio > 1.5` is a guess. Replace it with the Part 4
    #         separation test: does semantic chunking actually produce chunks
    #         that favour one query over another more sharply than character
    #         chunking does? That needs labelled queries - where do they come from?
    #
    # TODO 2: add the cost side. Count the tokens embedded for boundary
    #         detection vs for indexing. At what corpus size does the extra
    #         pass stop being affordable for you?
    #
    # TODO 3: run it on structured text (a Markdown document with headings).
    #         Does the peak ratio still recommend semantic chunking? Should it,
    #         when MarkdownHeaderTextSplitter would do the job for free?


report = SemanticChunkingReport(embeddings)
print("Flat text (structure removed, real topic shift):")
for k, v in report.analyse(flat).items():
    print(f"  {k:<20} {v}")

%%markdown
---

## Summary

**The algorithm:** split into sentences → embed each → measure distance between consecutive sentences → threshold → group. About fifteen lines from scratch, and worth writing once so the library version is not a black box.

**What it fixes:** boundaries that land mid-idea, and chunks that fuse unrelated topics into an averaged vector that serves neither. Visible on text where structural cues are absent.

**`SemanticChunker`** takes four threshold types. `percentile` always finds boundaries; `standard_deviation` and `interquartile` can correctly decide a document has none. Thresholds are per-corpus and do not transfer.

**The costs are real:** an extra embedding pass over every sentence at index time (roughly doubling embedding cost), unbounded chunk sizes, and total dependence on sentence-segmentation quality.

**Bound the output** with a size split afterwards — semantic boundaries first, size ceiling second.

**Try structure first.** Author-supplied boundaries — headings, code syntax, HTML sections — are better signal than inferred ones and cost nothing. Semantic chunking earns its cost on unstructured text with internal topic shifts, and should be measured rather than assumed.

### Next lesson

`02_Chunking_and_Indexing/03_Proposition_Chunking.ipynb` — taking the idea further: instead of finding boundaries in the text, rewrite it into standalone atomic facts.

%%markdown
---

### Migration record

Canonical lesson for concept `RAG-CI-02` (semantic chunking), Chunking & Indexing batch.

`2. Semantichunking.ipynb` is written entirely against LangChain 0.x (`langchain.chat_models`, `langchain.document_loaders`, `langchain.vectorstores`, `langchain.schema`, `langchain.prompts`) and additionally requires `sentence_transformers`, which is not installed in this environment. It cannot run as written; its from-scratch approach and its purpose-built `langchain_intro.txt` corpus are carried here on the current stack. See `RAG_MIGRATION_MANIFEST.md`.
