# Structured Data, Routers and Connectors

> **Level** 🟠 Scale, Security, Operations · **Module** 06 · **Doc** 5 of 7 · **Time** ~25 min
> **Prerequisites:** Module 04 docs 2–4
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/08-structured-data-and-connectors.md`

## Why this matters

A real enterprise deployment is never pure document search. It is document search **plus** structured records — tickets, accounts, orders — and the questions users ask mix the two freely. Module 04 proved permission-checked retrieval over documents. This document adds the piece in front of it that decides *which kind of question this is*, and extends the same permission discipline to the structured path, and then asks what "connectors" means once there are dozens of live sources rather than two files.

## 1 · Why plain search fails on structured questions

> *"How many high-priority tickets did this customer file last week?"*

Embed that and search a document index, and you get *the most similar-sounding tickets* — not a count. Semantic search answers "which things are like this", never "how many", "which is most recent", or "sum this field". Those are aggregate and filter operations, and no amount of better search quality fixes it. It is a category mismatch, not a search-quality problem.

| Question shape | Right tool | Why plain search fails |
|---|---|---|
| "Why did this customer's system break in March?" | Semantic search over documents and post-mortems | — |
| "How many high-priority tickets did they file last week?" | A structured query (count/filter) | Search returns *similar* records, not a count |
| "What's the status of ticket #4821?" | Direct lookup by ID | Treating an ID as ordinary text is wasteful and imprecise |
| "Summarise the pattern across all high-priority billing tickets this quarter" | **Both** — filter first, then summarise the filtered set | A filter cannot summarise prose; search cannot reliably scope to "this quarter's high-priority billing tickets" |

## 2 · A router in front of retrieval

```
                         ┌──────────────────────┐
   question  ──────────> │   INTENT ROUTER      │
                         └──────────┬───────────┘
                                    |
              ┌─────────────────────┼─────────────────────┐
              v                     v                     v
     ┌────────────────┐   ┌─────────────────┐   ┌────────────────────┐
     │  STRUCTURED     │   │  SEMANTIC        │   │  HYBRID             │
     │  (a query or     │   │  (document       │   │  filter first, then │
     │  tool call on    │   │  search)         │   │  search the         │
     │  the record      │   │                  │   │  filtered set       │
     │  system)         │   │                  │   │                     │
     └────────────────┘   └─────────────────┘   └────────────────────┘
              |                     |                     |
              └─────────────────────┴─────────────────────┘
                                    v
                       the same permission checks, every path
```

The router is the new piece. Two honest ways to build one:

1. **Rule-based first pass** — cheap and deterministic: "how many", "count", "list all", or an ID pattern routes structured. Fast and free; brittle on unseen phrasing.
2. **A small model as intent classifier** — a cheap call that outputs one of {structured, semantic, hybrid} plus extracted filters (customer, date range, priority). More robust, at the cost of one small model call per question — the same route-by-difficulty idea as everywhere else. Module 04's `plan` node already does a rule-based first pass for multi-hop; this is the same node grown one axis.

**The structured path itself is a choice between two mechanisms:**

- **Generate a query from natural language**, run against a small, fixed, well-documented view. Fast, but generating a correct query reliably is its own hard problem — the model can invent fields — so the query must be validated or its result sanity-checked before it is trusted.
- **Call a small set of fixed, well-defined operations** — get tickets by status, get ticket by ID. Safer, because the surface of what can happen is a reviewed set of operations, not an open-ended language. **Usually the better default in an enterprise**, where "the model generated a query that touched every row" is a real incident. This is Module 01's tool registry, pointed at a record system.

## 3 · Permission checks do not get to skip the structured path

Access control is a **data access** concern, not a document-search concern. Structured queries need the same discipline as chunks:

- **Row-level permission checks on the structured side.** The same rule chain — tenant, clearance, region, compartment — gates structured results too. A count query needs the tenant scope forced in *before it runs*, never trusted to a filter added after.
- **The same two-layer discipline.** Push what the structured store can express (tenant, region, clearance) into the query; re-verify what it cannot (a compartment, a permission that just changed) before the result reaches the model or user.
- **A structured leak is still a leak.** A count that includes records the user may not see, or a lookup that returns a restricted record, is exactly as serious as a forbidden document in search results. Same zero-tolerance bar; same gate.

## 4 · Connecting many live sources at scale

Module 04 proved the pattern for a second source: a differently shaped feed into the same pipeline, into its own tenant. That generalises in principle — but "generalises" does a lot of work once the requirement is dozens of live external systems.

| Proving the pattern (small scale) | Real scale (dozens of live sources) |
|---|---|
| One custom mapping function per source, all landing in one common schema | A **connector registry** — config-driven, not a bespoke function per source |
| One combined sync run | **Independent schedules per source**; one source's outage cannot block the others |
| Content-hash comparison to skip unchanged records | Same idea, plus per-source **change tokens** where the source API supports them; content comparison is the fallback |
| A place to record rejected records | Same, plus **connector health** as its own signal — expired credential, rate-limited by the source, a structure change that broke the mapping |
| One tenant, one demo run | **Backfill vs incremental** as an explicit mode per source — a newly connected source needs a bounded, resumable initial load, not "run the regular loop and hope" |

Three things to be able to say:

- *"Each source maps its native shape into one common internal schema — a wiki page and a support ticket look the same downstream, so the rest of the pipeline never knows which source something came from."*
- *"One source failing is quarantined to that source — one system rate-limiting us shouldn't stall ingestion from every other connected source."* (The bulkhead pattern from doc 2, applied to ingestion.)
- *"Permission data usually comes either from the same connector as the content or from a separate entitlements feed — whatever system actually owns access decisions — and that split should be modelled explicitly rather than assumed to travel with the content."* (Module 04's two-feed ingestion, generalised.)

## Interview lens

> *"Document search proves permission-checked retrieval end to end. The real gap is a router in front of it that recognises when a question needs structured data — counts, filters, a record by ID — and dispatches to a fixed set of operations or a carefully constrained query instead of semantic search. The same permission discipline — check what the store can express, re-verify what it can't — extends to that path, because a leaked row is exactly as much an incident as a leaked document."*

## Checkpoint

- Give one question for each of the three router outputs and say why plain search fails the structured one.
- Why is "a fixed set of operations" usually a better structured path than NL-to-query in an enterprise?
- Apply Layer 1 / Layer 2 to a count query.
- Name three things a connector registry needs that a per-source mapping function does not.
- Why is a structured leak held to the same gate as a document leak?

**Next →** [Scaling to Twenty Million Documents](06_Scaling_To_20M_Documents.md)
