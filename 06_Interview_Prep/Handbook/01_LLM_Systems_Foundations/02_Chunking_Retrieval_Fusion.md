# Chunking, Retrieval and Fusion

> **Level** 🟢 Foundations · **Module** 01 · **Doc** 2 of 5 · **Time** ~30 min
> **Prerequisites:** [What RAG Actually Is](01_What_RAG_Actually_Is.md)
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/01-theory.md` §4–6

## Why this matters

The first box of RAG — *find relevant documents* — hides four decisions, and each has a failure mode that no amount of prompt engineering will fix downstream:

1. How you split documents decides whether a retrieved passage still *means* anything.
2. Which search method you use decides whether you can find `MRD-5031` *and* "why is my data not showing up".
3. How you merge results from several searches decides whether agreement between them counts.
4. Whether you rerank decides whether the six passages the model sees are the six *best*, or the six *nearest*.

This document takes them in order. Every technique here is implemented in Module 04's project.

## Chunking — why you cannot just index whole documents

Models have a context limit, and retrieval works better on focused passages. So documents get split into **chunks**.

The naive approach is to cut every 1,000 characters. Here is what that does to a contract:

```
  BAD (fixed size, cut mid-table)          GOOD (split on headings)
  ┌────────────────────────────┐           ┌────────────────────────────┐
  │ ...sole remedy. Credits    │           │ ## Service credits         │
  │ below 99.9% but above      │           │ Below 99.9%, above 99.5%:  │
  │ 99.5%:                     │           │   10% credit               │
  └────────────────────────────┘           │ Below 99.5%, above 99.0%:  │
  ┌────────────────────────────┐           │   25% credit               │
  │ 10% credit. Below 99.5%... │           │ Below 99.0%: 50% credit    │
  └────────────────────────────┘           └────────────────────────────┘
   "10% credit" — of what? when?            One chunk, complete meaning.
```

Four rules matter far more than the chunk size you pick:

1. **Split on structure** (headings, sections) before falling back to size.
2. **Overlap** a little, so a fact split across a boundary survives on one side.
3. **Prefix each chunk with its document title and section.** Cheap, and it puts the subject *inside* the text being searched — a chunk that says "10% credit" retrieves badly; one that says "Vertex Financial MSA › Service credits › 10% credit" retrieves well.
4. **Every chunk inherits its parent's permissions.** This one is not optional. A chunk is the unit of retrieval, so it is the unit of access control.

Module 06 extends this with chunking strategy by document type and parent-child ("small-to-big") chunking at scale.

## How retrieval actually finds things

### Dense (vector) search — "find things that *mean* the same"

An **embedding** turns text into a list of numbers (a vector) positioned so that similar *meanings* land near each other. Search = embed the question, find the nearest chunks.

```
            "how do I fix ingestion stalling?"
                      *
                     /  near
      "MRD-5031 backpressure guide"  *
                                        *  "compaction queue runbook"

                                                    *  "parental leave policy"  (far)
```

It is brilliant at paraphrase. It is **bad at exact identifiers**, because `MRD-5031`, `MRD-5030` and `MRD-4290` all *look* alike, so they embed to nearly the same place.

### Lexical (BM25) search — "find things that *say* the same"

Classic keyword scoring. A rare word appearing in a document is strong evidence. `MRD-5031` is rare, so BM25 nails it instantly. But BM25 has no idea that "data not showing up" and "commit lag" describe the same problem.

### The point

```
   Question: "What is MRD-5031?"        Question: "why is my data not showing up?"

   dense  ->  MRD-5030 guide  (wrong)   dense  ->  backpressure guide   (right)
   BM25   ->  MRD-5031 guide  (right)   BM25   ->  nothing              (no shared words)
```

Neither wins alone. Enterprise corpora are full of error codes, SKUs, ticket IDs and workspace IDs, *and* users ask questions in plain language. **You need both.** That is called **hybrid search**, and it raises the next question: how do you merge two result lists whose scores mean different things?

## Combining and improving results

### Reciprocal Rank Fusion — merging lists whose scores are not comparable

Dense search says "0.82 similarity". BM25 says "14.3". Those numbers live on different scales and cannot be added. RRF ignores the scores and uses only the **ranks**:

```
  score(doc) = sum over each list of   1 / (k + rank_in_that_list)      (k ≈ 60)
```

```
  dense list        BM25 list          RRF result
  1. A              1. C               1. B   <- 2nd in BOTH lists
  2. B              2. B               2. A
  3. D              3. E               3. C
```

A document ranked 2nd by *both* retrievers beats one ranked 1st by only one. That "agreement across independent retrievers" is exactly the signal you want, and RRF gets it without any score normalisation.

### Multi-Query — the user's wording is only one guess

The user says *"data not showing up"*. The runbook says *"commit lag"*. No overlap. So ask the model to rewrite the question several ways, search with all of them, and RRF the results.

```
   "why is my data not showing up?"
            |
            +--> "ingest pipeline dropping metrics"     -> search -+
            +--> "MRD-5031 backpressure"                -> search -+--> RRF --> better results
            +--> "gaps in dashboards after ingestion"   -> search -+
            +--> (original question)                    -> search -+
```

**Multi-Query + RRF is what people market as "RAG-Fusion".** Same thing; know both names.

### HyDE — search with a fake answer instead of the question

Questions and answers are written differently. *"Why did ingest stall?"* looks nothing like *"the compaction queue saturated at 08:47"*.

HyDE's trick: ask the model to **make up** a plausible answer, then embed *that* and search with it. A fake answer looks much more like a real answer than a question does.

```
   question ──> LLM ──> hypothetical answer ──> embed ──> search
                        (invented, never
                         shown to the user)
```

Yes, it hallucinates on purpose. That is fine — the hallucination is only ever used as a *search probe* and is discarded. Anchor it by searching with the original question too.

### Decomposition — multi-hop questions

*"Why did they lose data **and** what does their contract promise?"* — no single chunk answers that. Split it, retrieve for each part, synthesise once. This is the `plan` step in the query pipeline from the previous document.

### Reranking — the biggest single quality win

Retrieval is optimised to be **fast over millions of documents**, so it is approximate. Reranking is **slow and accurate over 20 candidates**. Do both:

```
   1,000,000 chunks
        |  retrieve (fast, approximate, high recall)
        v
       ~20 candidates
        |  rerank (slow, accurate, high precision)
        v
        6 chunks -> the model
```

Why it works: dense search embeds the question and the document *separately* and never compares them directly. A reranker (a cross-encoder) looks at the question and the document **together** and answers one question: *does this passage actually answer this?* That is a fundamentally stronger judgement, affordable only because it runs on twenty items rather than a million.

## Putting the techniques in one place

| Technique | Fixes | Cost |
|---|---|---|
| Structure-aware chunking with title prefix | passages that lose meaning; chunks with no subject | none at query time |
| Hybrid search (dense + BM25) | identifiers vs paraphrase | two searches instead of one |
| RRF | merging incomparable score scales | negligible |
| Multi-Query | vocabulary mismatch between user and corpus | one LLM call + N searches |
| HyDE | question/answer style mismatch | one LLM call + one search |
| Decomposition | multi-hop questions | one LLM call + N searches |
| Reranking | approximate top-k ordering | one cross-encoder pass over ~20 items |

None of these are exclusive. Module 04's project runs them as six swappable strategies behind one interface, and its evaluation harness is how you decide which combination is worth its latency for a given corpus.

## Interview lens

The question is usually "how would you improve retrieval quality?" and the weak answer is "use a better embedding model". The strong answer names the *failure* first — identifiers, vocabulary mismatch, approximate ranking — and the technique that targets it. The line that carries it:

> *"Hybrid search because enterprise corpora mix identifiers and prose; RRF because the scores aren't comparable; rerank because retrieval is approximate by design and twenty candidates are cheap to judge properly."*

## Checkpoint

- Why is "split every 1,000 characters" wrong, and what are the four rules that matter more than size?
- Give one query that dense search gets right and BM25 gets wrong, and one the other way round.
- Explain RRF without using the word "score". Why does a document ranked 2nd twice beat one ranked 1st once?
- What is the difference between Multi-Query and HyDE? When would you use each?
- Why can a reranker make a judgement that dense retrieval cannot?

**Next →** [What an Agent Actually Is](03_What_An_Agent_Actually_Is.md)
