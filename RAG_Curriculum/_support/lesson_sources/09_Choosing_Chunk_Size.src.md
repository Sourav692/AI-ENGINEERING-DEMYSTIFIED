%%markdown
# Choosing Chunk Size

Three lessons have now explained what chunking parameters *do*. None has told you what to set them to, and that omission was deliberate: **there is no correct answer in general, only a correct answer for your corpus, your queries, and your embedding model.**

Every RAG tutorial confidently recommends 1000/200 or 512/50. Those numbers are someone else's measurement on someone else's data, repeated until they sounded like a standard. This lesson replaces that with a procedure: build a small labelled set, sweep the parameters, plot the curve, and read it.

The procedure matters more than any number this notebook produces.

## Learning objectives

By the end of this notebook you will be able to:

1. **Explain why chunk size cannot be chosen analytically**, and what it actually depends on.
2. **Build a labelled evaluation set** small enough to be practical and honest about its limits.
3. **Sweep chunk size** and measure retrieval quality with a metric that does not saturate.
4. **Sweep overlap separately**, and see that it is a much weaker lever than size.
5. **Weigh quality against cost** — tokens per query, index size, latency — because the best-scoring configuration is rarely the one to ship.
6. **Read a sweep curve**: find the plateau, distinguish signal from noise, and know when the honest conclusion is "it doesn't matter much".

%%markdown
## Prerequisites

**Lessons**

- `02_Chunking_and_Indexing/01_Document_Splitting_and_Chunking.ipynb` — what the parameters do.
- `01_Foundations/03_Embeddings_and_Model_Selection.ipynb` — the labelled-set-and-sweep pattern this generalizes, and the `margin` metric it reuses.

**Packages**

`langchain-text-splitters`, `langchain-openai`, `numpy`, `pandas`, `tiktoken`.

**Services**

`OPENAI_API_KEY`. The sweep re-embeds the corpus once per configuration — that is the cost of measuring, and Part 6 puts a number on it.

%%markdown
## Provenance and runtime status

Based on `08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/4. choose_chunk_size.ipynb`, which establishes the right idea: sweep chunk sizes, evaluate each, compare.

**That source cannot run here.** It is built entirely on **LlamaIndex** — `llama_index.core`, `llama_index.core.evaluation`, `llama_index.llms.openai`, plus `nest_asyncio`. LlamaIndex is **not installed in this environment and is not declared in `pyproject.toml` or `requirements.txt`**. It also uses LlamaIndex's `FaithfulnessEvaluator` and `RelevancyEvaluator`, which are LLM judges — a reasonable choice, and a slow and expensive one for a parameter sweep.

The method is carried and rebuilt on this curriculum's stack, with a deterministic retrieval metric instead of LLM judges: faster, free of judge variance, and directly comparable to the sweeps in `01_Foundations/03`.

**Added here:** the cost axis (Part 5), the guidance on reading a curve including the case where the honest answer is "no difference" (Part 6), and the escape hatch when no size works (Part 7).

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
import time

import numpy as np
import pandas as pd
import tiktoken
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(repo_root() / ".env")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
enc = tiktoken.get_encoding("cl100k_base")

print("Ready:", embeddings.model)

%%markdown
---

## Part 1 — Why there is no general answer

Chunk size interacts with at least five things, and they vary per project:

| Depends on | Why |
| --- | --- |
| **Information density** | A dense reference page packs a fact per sentence; a narrative spreads one over a paragraph |
| **Query specificity** | Pinpoint lookups favour small chunks; "explain X" favours large ones |
| **Embedding model** | Different models degrade differently as input grows; input limits differ |
| **Document structure** | Structural boundaries may already dictate natural sizes |
| **`k` and the token budget** | `chunk_size × k` must fit the prompt, and larger `k` partly substitutes for larger chunks |

Because it is an interaction, it is empirical. The good news is that measuring it is cheap — much cheaper than the arguments people have about it.

%%code
# ============ A CORPUS WITH KNOWN ANSWERS ============
# Each entry is a short policy section containing ONE distinctive fact. Because
# we know which section answers which question, we can score retrieval without
# hand-labelling individual chunks - the gold answer is a substring.
sections = [
    ("expenses", "Expense reports must be submitted within 30 days of the travel end date. "
                 "Reports submitted after this window require director approval. "
                 "Receipts are mandatory for any single item above 75 dollars. "
                 "Mileage is reimbursed at 0.58 dollars per mile for personal vehicles."),
    ("remote", "Employees may work remotely up to three days per week with manager approval. "
               "Fully remote arrangements require a formal agreement reviewed annually. "
               "Home office equipment is reimbursed up to 1200 dollars in the first year. "
               "Core collaboration hours are 10am to 3pm in the employee's local time zone."),
    ("leave", "Parental leave is 16 weeks at full pay for all employees regardless of tenure. "
              "Annual leave accrues at 2.5 days per month worked. "
              "Unused annual leave may be carried over up to a maximum of 10 days. "
              "Sick leave is uncapped but absences beyond 5 consecutive days need a medical note."),
    ("security", "All laptops must have full-disk encryption enabled before first use. "
                 "Passwords must be at least 14 characters and rotated every 180 days. "
                 "Multi-factor authentication is mandatory for all production systems. "
                 "Security incidents must be reported to the security team within 1 hour."),
    ("deploys", "Production deployments require two approvals and a documented rollback plan. "
                "Deployments are frozen between December 20 and January 2 each year. "
                "Any deployment causing an outage must have a written postmortem within 5 days. "
                "Canary releases must run for at least 30 minutes before full rollout."),
    ("training", "Employees are eligible for the training stipend after 6 months of service. "
                 "The stipend is 2000 dollars per calendar year. "
                 "It covers conference fees, course tuition and technical books. "
                 "Unused stipend does not roll over into the following year."),
    ("hardware", "Laptops are replaced on a 3 year cycle or earlier if hardware fails. "
                 "Employees may choose between a 14 inch and a 16 inch model. "
                 "External monitors are provided one per employee on request. "
                 "Personal use of company hardware is permitted within the acceptable use policy."),
    ("travel", "Flights over 6 hours may be booked in premium economy. "
               "Hotel spending is capped at 250 dollars per night in major cities. "
               "Travel must be booked at least 14 days in advance where practical. "
               "Airport transfers are reimbursed but rental cars require prior approval."),
]

corpus = "\n\n".join(body for _, body in sections)

# (question, a distinctive string that MUST appear in a correct chunk)
labelled = [
    ("How long do I have to submit an expense report?", "within 30 days"),
    ("What is the mileage reimbursement rate?", "0.58 dollars per mile"),
    ("How many days a week can I work from home?", "three days per week"),
    ("How much can I claim for home office equipment?", "1200 dollars"),
    ("How much parental leave is there?", "16 weeks at full pay"),
    ("How much annual leave can I carry over?", "maximum of 10 days"),
    ("How long must passwords be?", "at least 14 characters"),
    ("How quickly must security incidents be reported?", "within 1 hour"),
    ("How many approvals does a production deploy need?", "two approvals"),
    ("When is the deployment freeze?", "December 20 and January 2"),
    ("How much is the training stipend?", "2000 dollars per calendar year"),
    ("When do I become eligible for the training stipend?", "after 6 months of service"),
    ("How often are laptops replaced?", "3 year cycle"),
    ("What is the hotel spending cap?", "250 dollars per night"),
]

print(f"corpus: {len(corpus)} chars, {len(enc.encode(corpus))} tokens")
print(f"  {len(sections)} sections containing answers")
print(f"  {len(distractors)} distractor sections containing none")
print(f"labelled questions: {len(labelled)}")
print()
print("Most of this corpus is irrelevant to any given question - which is")
print("conservative next to a real corpus, and is what makes margin meaningful.")

%%markdown
**Two honest caveats about this evaluation set**, both of which apply to yours as well:

**Substring matching is a proxy.** "Does the retrieved chunk contain `within 30 days`?" is not "did the system answer correctly" — a chunk could contain the string in a misleading context. It is a *retrieval* metric, deliberately: it isolates chunking from generation, and it is deterministic, free and instant, which is what a parameter sweep needs. Judging answers is `06_Evaluation/`.

**Fourteen questions is small.** Enough to see a trend, not enough to distinguish 480 from 520. Real evaluation sets come from actual user queries — that is the single highest-value thing you can build for a RAG system, and it does not require any special tooling.

%%markdown
---

## Part 2 — The evaluation function

One function: chunk the corpus with a given configuration, index it, run every question, score it.

Two metrics, deliberately:

- **`hit@k`** — did any of the top `k` chunks contain the gold string? Binary, easy to interpret, and it saturates.
- **`margin`** — how much closer is the best correct chunk than the best incorrect one? Continuous, keeps discriminating after `hit@k` reaches 1.0. Same reasoning as `01_Foundations/03`.

%%code
# ============ THE SWEEP FUNCTION ============
def evaluate(chunk_size, chunk_overlap, k=3, corpus=corpus, labelled=labelled):
    """Chunk, index, query, score. Returns quality AND cost for one config."""
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base", chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(corpus)

    t0 = time.perf_counter()
    C = np.array(embeddings.embed_documents(chunks))     # index-time cost
    index_time = time.perf_counter() - t0

    Q = np.array(embeddings.embed_documents([q for q, _ in labelled]))
    sims = Q @ C.T          # unit vectors -> dot product is cosine

    # A configuration coarse enough to put the whole corpus in one chunk
    # "retrieves" perfectly and has no competing chunk to measure a margin
    # against. That is degenerate, not good - flag it rather than score it.
    degenerate = len(chunks) < 2

    hits, margins = 0, []
    for row, (_, gold) in zip(sims, labelled):
        correct = [i for i, c in enumerate(chunks) if gold in c]
        if not correct:
            # The gold string was destroyed by this chunking - a real failure,
            # not a missing label. Count it as a miss with no margin.
            margins.append(0.0)
            continue
        topk = np.argsort(-row)[:k]
        hits += int(any(i in correct for i in topk))
        best_right = max(row[i] for i in correct)
        wrong = [row[i] for i in range(len(chunks)) if i not in correct]
        margins.append(best_right - max(wrong) if wrong else float("nan"))

    tokens = [len(enc.encode(c)) for c in chunks]
    return {
        "chunk_size": chunk_size,
        "overlap": chunk_overlap,
        "chunks": len(chunks),
        "degenerate": degenerate,
        f"hit@{k}": round(hits / len(labelled), 3),
        "margin": (float("nan") if degenerate
                   else round(float(np.nanmean(margins)), 4)),
        "median_tokens": int(np.median(tokens)),
        "tokens_per_query": int(np.median(tokens) * k),   # what k chunks cost the prompt
        "index_tokens": sum(tokens),
        "index_secs": round(index_time, 2),
    }


print(pd.DataFrame([evaluate(256, 32)]).to_string(index=False))

%%markdown
Note the `if not correct` branch. When a chunk size is small enough to **split the gold string itself**, no chunk contains it and the question becomes unanswerable by any retrieval. That is not a labelling gap — it is the most severe chunking failure there is, and the metric must record it rather than skip it.

%%markdown
---

## Part 3 — Sweeping chunk size

%%code
# ============ THE SIZE SWEEP ============
sizes = [64, 96, 128, 192, 256, 384, 512, 768]
size_rows = [evaluate(s, chunk_overlap=int(s * 0.15)) for s in sizes]

df = pd.DataFrame(size_rows)
print(df.to_string(index=False))

if df.degenerate.any():
    bad = df[df.degenerate].chunk_size.tolist()
    print(f"
degenerate (whole corpus in one chunk), excluded: {bad}")
df = df[~df.degenerate].reset_index(drop=True)

%%code
# ============ THE CURVE, AS A CHART ============
# A plot is easier to read than a table, and the shape is the point.
# Analyse only non-degenerate configurations.
best_margin = df.margin.max()
print(f"{'size':>5} {'hit@3':>6} {'margin':>7}  {'tok/query':>9}  margin")
for r in df.itertuples():
    bar = "#" * int(round(r.margin / best_margin * 34))
    print(f"{r.chunk_size:>5} {getattr(r, '_4'):>6.2f} {r.margin:>7.4f}  "
          f"{r.tokens_per_query:>9}  {bar}")

%%markdown
Read the shape, not the maximum. Three regions usually appear:

**Too small** — the gold fact gets split across chunks, or a chunk is too short to carry enough context for its embedding to mean anything. `hit@k` drops and margin collapses.

**The plateau** — a broad range where quality is essentially flat. This is normally wide, and it is the most useful finding in the whole exercise: **within the plateau, pick the cheapest option, not the highest-scoring one.** The difference between neighbouring points there is noise.

**Too large** — one chunk covers several topics, its embedding averages them, and the margin narrows. `hit@k` may stay high while margin degrades, because the right chunk still wins but less decisively.

%%code
# ============ FINDING THE PLATEAU, NOT THE PEAK ============
peak = df.loc[df.margin.idxmax()]
# "Within 3% of the best" is a judgement call - state it rather than hide it.
plateau = df[df.margin >= peak.margin * 0.97]
cheapest = plateau.loc[plateau.tokens_per_query.idxmin()]

print(f"best margin      : size={int(peak.chunk_size)}  margin={peak.margin:.4f}  "
      f"{int(peak.tokens_per_query)} tokens/query")
print(f"plateau (>=97%)  : sizes {sorted(plateau.chunk_size.astype(int).tolist())}")
print(f"cheapest in it   : size={int(cheapest.chunk_size)}  margin={cheapest.margin:.4f}  "
      f"{int(cheapest.tokens_per_query)} tokens/query")

if cheapest.chunk_size != peak.chunk_size:
    saving = 1 - cheapest.tokens_per_query / peak.tokens_per_query
    print(f"\n-> {saving:.0%} fewer prompt tokens per query for "
          f"{(peak.margin - cheapest.margin) / peak.margin:.1%} less margin.")
    print("   On every request, forever. That is usually the right trade.")
else:
    print("\n-> The best-scoring size is also the cheapest in the plateau.")

%%markdown
---

## Part 4 — Sweeping overlap

Overlap gets discussed as though it were as important as size. Hold size fixed and measure it.

%%code
# ============ THE OVERLAP SWEEP ============
fixed = int(cheapest.chunk_size)
ov_rows = [evaluate(fixed, o) for o in (0, 16, 32, 64, 96)]
ov = pd.DataFrame(ov_rows)
print(f"chunk_size fixed at {fixed}:\n")
print(ov[["overlap", "chunks", "hit@3", "margin", "index_tokens"]].to_string(index=False))

span = ov.margin.max() - ov.margin.min()
print(f"\nmargin varies by {span:.4f} across all overlaps "
      f"({span / ov.margin.mean():.1%} of the mean)")
print(f"index grows {ov.index_tokens.max() / ov.index_tokens.min():.2f}x "
      f"from zero overlap to the largest")

%%markdown
Overlap is usually the weaker lever, and it costs index size linearly. Its value is insurance against a specific failure — a fact straddling a boundary — which is intermittent rather than systematic. It shows up as occasional recovered questions, not as a shifted curve.

**10–20% of `chunk_size` remains a reasonable default**, not because it optimizes anything measurable here, but because it is cheap insurance. Spend your tuning effort on size.

%%markdown
---

## Part 5 — The cost axis

The best-scoring configuration is rarely the one to deploy, because quality is not the only axis.

%%code
# ============ WHAT EACH CONFIGURATION COSTS ============
cost = df[["chunk_size", "chunks", "margin", "median_tokens", "tokens_per_query",
           "index_tokens", "index_secs"]].copy()
cost["idx_vs_smallest"] = (cost.index_tokens / cost.index_tokens.min()).round(2)
print(cost.to_string(index=False))

print("\nThree separate costs, paid at different times:")
print("  index_tokens     - paid ONCE at ingestion, scales with corpus size")
print("  tokens_per_query - paid on EVERY request, forever (chunk_size x k)")
print("  chunks           - index storage and per-query search cost")
print("\ntokens_per_query is the one that compounds. A configuration costing")
print("twice as many prompt tokens costs twice as much on every single call.")

%%markdown
For a service handling 100,000 queries a month, the difference between 384 and 768 tokens of retrieved context per query is 38.4 million tokens a month of pure prompt overhead. If the margin difference between them is 2%, that is a straightforward decision — and it is invisible unless you put both columns in the same table.

%%markdown
---

## Part 6 — Reading the result honestly

**Three failure modes in how people read these sweeps:**

**Chasing the peak.** The highest-margin configuration on 14 questions is not reliably the best configuration. Prefer the cheapest point on the plateau.

**Over-reading small differences.** With this few questions, a margin difference of 0.01 is noise. Re-run the sweep — embeddings are deterministic but the *labelled set* is a sample, and a different sample moves the numbers.

**Not accepting "it doesn't matter".** A flat curve is a real, useful, and common finding. It means chunk size is not your bottleneck, and you should stop tuning it and go look at retrieval strategy, query transformation, or reranking.

%%code
# ============ IS THE DIFFERENCE REAL? ============
# Sensitivity check: re-score the best configurations on random halves of the
# labelled set. If the ranking flips between subsets, the difference is noise.
rng = np.random.default_rng(0)
top3 = df.nlargest(3, "margin").chunk_size.astype(int).tolist()

print(f"Re-scoring sizes {top3} on 6 random halves of the labelled set:\n")
wins = dict.fromkeys(top3, 0)
for trial in range(6):
    idx = rng.choice(len(labelled), size=len(labelled) // 2, replace=False)
    subset = [labelled[i] for i in idx]
    scores = {s: evaluate(s, int(s * 0.15), labelled=subset)["margin"] for s in top3}
    winner = max(scores, key=scores.get)
    wins[winner] += 1
    print(f"  trial {trial}: " + "  ".join(f"{s}={scores[s]:.4f}" for s in top3)
          + f"   -> {winner}")

print(f"\nwins: {wins}")
if max(wins.values()) < 5:
    print("The winner changes between subsets. These configurations are")
    print("indistinguishable at this sample size - pick on cost.")
else:
    print("One size wins consistently. That is weak evidence, not proof;")
    print("confirm on a larger labelled set before committing.")

%%markdown
---

## Part 7 — When no size works

Sometimes the sweep shows every configuration is bad, or that small chunks win on precision while large ones win on completeness and nothing does both. That is not a tuning failure — it means **the two requirements genuinely conflict for your corpus**, and no single number satisfies both.

The answer is to stop using one size for both jobs:

| Technique | Idea | Lesson |
| --- | --- | --- |
| **Parent-document retrieval** | Index small chunks for precise matching; return the larger parent for completeness | `02_Chunking_and_Indexing/06` |
| **Context windows** | Retrieve a small chunk, then expand to include its neighbours | `05_Context_and_Generation/01` |
| **Multi-representation indexing** | Index a summary, return the full document | `02_Chunking_and_Indexing/07` |

All three decouple *what you match on* from *what you return* — which is the only real way out of the tension, and the reason those lessons exist.

%%markdown
---

## Limitations and tradeoffs

**Fourteen questions, eight sections, one embedding model.** This is a demonstration of the procedure. Any number it produces is about this toy corpus.

**Substring matching is not answer correctness.** It measures whether the evidence was retrieved, which is deliberate — it isolates chunking from generation. A full evaluation needs `06_Evaluation/`.

**`k` was fixed at 3 throughout.** Chunk size and `k` interact: larger `k` partly compensates for smaller chunks. A thorough sweep is two-dimensional, and costs proportionally more.

**One splitter.** All of this used `RecursiveCharacterTextSplitter`. On structured documents the structure-aware splitters from lesson 01 may beat every size setting here, and that comparison belongs in the sweep too.

**The sweep costs money.** Each configuration re-embeds the whole corpus. On a large corpus, sweep on a representative *sample* rather than the full thing — and check that the sample's document-length distribution matches the whole.

%%markdown
---

## Exercise

Turn the sweep into a reusable harness that reports a recommendation with its reasoning, rather than a number.

%%code
# ============ EXERCISE: A CHUNK SIZE TUNER ============
class ChunkSizeTuner:
    """Sweep chunking configurations and recommend one, with justification."""

    def __init__(self, corpus: str, labelled: list[tuple[str, str]], embeddings, k: int = 3):
        self.corpus, self.labelled, self.embeddings, self.k = corpus, labelled, embeddings, k

    def sweep(self, sizes, overlap_frac=0.15) -> pd.DataFrame:
        return pd.DataFrame([
            evaluate(s, int(s * overlap_frac), k=self.k,
                     corpus=self.corpus, labelled=self.labelled)
            for s in sizes
        ])

    def recommend(self, sizes, tolerance=0.03) -> dict:
        df = self.sweep(sizes)
        df = df[~df.degenerate].reset_index(drop=True)   # never recommend a degenerate config
        peak = df.loc[df.margin.idxmax()]
        plateau = df[df.margin >= peak.margin * (1 - tolerance)]
        pick = plateau.loc[plateau.tokens_per_query.idxmin()]
        flat = (df.margin.max() - df.margin.min()) / df.margin.mean() < 0.10
        return {
            "recommended_size": int(pick.chunk_size),
            "recommended_overlap": int(pick.chunk_size * 0.15),
            "margin": float(pick.margin),
            "tokens_per_query": int(pick.tokens_per_query),
            "plateau": sorted(plateau.chunk_size.astype(int).tolist()),
            "curve_is_flat": bool(flat),
            "reasoning": ("Curve is flat - chunk size is not the bottleneck here. "
                          "Chosen on cost; go tune retrieval instead."
                          if flat else
                          "Cheapest configuration within tolerance of the best margin."),
        }

    # TODO 1: make it two-dimensional - sweep k alongside chunk_size. Does the
    #         best size change with k? (It should: larger k compensates for
    #         smaller chunks.) What does that do to tokens_per_query?
    #
    # TODO 2: add the sensitivity check from Part 6 automatically, and refuse
    #         to recommend a size whose advantage does not survive resampling.
    #
    # TODO 3: sweep the SPLITTER too, not just its parameters - compare
    #         RecursiveCharacterTextSplitter against the structure-aware
    #         splitters from lesson 01 on a structured corpus.


tuner = ChunkSizeTuner(corpus, labelled, embeddings)
rec = tuner.recommend([96, 128, 192, 256, 384, 512])
for key, value in rec.items():
    print(f"  {key:<20} {value}")

%%markdown
---

## Summary

**There is no universal chunk size.** It depends on information density, query specificity, embedding model, document structure, and `k`. Published defaults are someone else's measurement.

**The procedure, which transfers even though the numbers do not:**

1. Build a small labelled set — a question plus a string that must appear in a correct chunk. Real user queries are the best source.
2. Sweep chunk size, holding everything else fixed.
3. Score with a metric that does not saturate. `hit@k` reaches 1.0 and stops discriminating; `margin` keeps going.
4. Put cost in the same table — `tokens_per_query` is paid on every request, forever.
5. **Find the plateau and pick the cheapest point on it**, not the peak.
6. Sanity-check with resampling. If the winner changes between subsets, the difference is noise.

**Overlap is a weaker lever than size.** It is insurance against boundary damage and costs index size linearly. 10–20% is a reasonable default; spend your effort on size.

**A flat curve is a real result.** It means chunking is not your bottleneck. Stop tuning it.

**If precision and completeness genuinely conflict**, no size resolves it — decouple matching from returning, via parent-document retrieval, context windows, or multi-representation indexing.

### Next lesson

`02_Chunking_and_Indexing/05_Incremental_Indexing_and_Record_Management.ipynb` — keeping an index correct as documents change, without rebuilding it.

%%markdown
---

### Migration record

Canonical lesson for concept `RAG-CI-04` (choosing chunk size), Chunking & Indexing batch.

The source (`all_rag_techniques/4. choose_chunk_size.ipynb`) is built entirely on LlamaIndex, which is **not installed in this environment and not declared in `pyproject.toml` or `requirements.txt`** — it cannot run here. Its method (sweep sizes, evaluate each, compare) is carried and rebuilt on this curriculum's stack, substituting a deterministic retrieval metric for the original's LLM judges: faster, cheaper, free of judge variance, and directly comparable to the sweeps in `01_Foundations/03`. See `RAG_MIGRATION_MANIFEST.md`.
