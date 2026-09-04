# Structured data, query routing, and connecting many sources at scale

A real enterprise RAG deployment is never pure document search. It's document search **plus**
structured records — tickets, accounts, orders — and a real interviewer will expect both. None of this
needs a codebase — it's architecture to describe on a whiteboard.

---

## 1. Why plain search fails on structured questions

> *"How many high-priority tickets did this customer file last week?"*

Embed that question and search a document index, and you get **the most similar-sounding tickets** —
not a count. Semantic search answers "which things are like this," never "how many," "which is most
recent," or "sum this field." Those are aggregate/filter operations, and no amount of better search
quality fixes that — it's a category mismatch, not a search-quality problem.

| Question shape | Right tool | Why plain search fails here |
| --- | --- | --- |
| "Why did this customer's system break in March?" | Semantic search over documents/postmortems | — |
| "How many high-priority tickets did they file last week?" | A structured query (count/filter) | Search returns *similar* records, not a count |
| "What's the status of ticket #4821?" | Direct lookup by ID | Treating an ID like ordinary text is wasteful and imprecise |
| "Summarize the pattern across all high-priority billing tickets this quarter" | **Both** — filter first, then summarize the filtered set | A filter alone can't summarize prose; search alone can't reliably scope to "this quarter's high-priority billing tickets" |

## 2. A router in front of retrieval

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

**The router is the new piece.** Two honest ways to build one:

1. **Rule-based first pass** — cheap and deterministic: a question containing "how many," "count,"
   "list all," or an ID pattern routes structured. Fast and free, but brittle on phrasing it hasn't
   seen before.
2. **A small model as intent classifier** — a cheap, fast model call that outputs one of
   {structured, semantic, hybrid} plus any extracted filters (customer, date range, priority). More
   robust to varied phrasing, at the cost of one extra small model call per question — the same
   "route by difficulty" idea used elsewhere (cheap model for easy decisions, expensive model only for
   the final answer).

**The structured path itself is a choice between two mechanisms:**
- **Generating a query from natural language**, run against a small, fixed, well-documented view of
  the data — fast, but generating a correct query reliably is its own hard problem: the model can
  invent fields that don't exist, so the query needs to be validated (or its result sanity-checked)
  before it's trusted.
- **Calling a small set of fixed, well-defined operations** against the record system directly (get
  tickets by status, get ticket by ID) — safer than an open query language, because the surface of
  what can happen is a fixed, reviewed set of operations, not an open-ended language the model could
  misuse. This is usually the better default in an enterprise setting, where "the model generated a
  query that touched every row" is a real incident, not a hypothetical.

## 3. Permission checks don't get to skip the structured path

It's tempting to think access control only applies to document search. It doesn't — it's a **data
access** concern, and structured queries need the exact same discipline as document chunks:

- **Row-level permission checks on the structured side** — the same rule chain (which company, what
  clearance level, which region, which specific compartment of information) has to gate structured
  results too, not just retrieved document passages. A count query still needs the tenant/company
  scope forced in before it runs, never trusted to a filter added after the fact.
- **The same two-layer discipline still applies.** Push whatever the structured store can express
  (company, region, clearance level) into the query itself; re-verify anything it can't express
  (a narrower compartment of access, a permission that just changed) before the result reaches the
  model or the user.
- **A structured leak is still a leak.** A count that includes records the user isn't allowed to see,
  or a lookup that returns a restricted record's details, is exactly as serious an incident as a
  forbidden document surfacing in search results — the same zero-tolerance bar applies.

## 4. Connecting many live sources at scale

Proving the *pattern* for a second data source (a differently-shaped source feeding the same common
pipeline, into its own tenant) generalizes cleanly in principle — but "generalizes" does a lot of work
once the real requirement is dozens of live external systems instead of two files.

| At small scale (proving the pattern) | At real scale (dozens of live sources) |
| --- | --- |
| One custom mapping function per source, all landing in the same common schema | A **connector registry** — config-driven, not a bespoke function hand-written per source |
| One combined sync run | Independent schedules per source; one source's outage can't block the others |
| Simple content-comparison to skip unchanged records | Same idea, but per-source **change tokens** where the source API supports them — content comparison is the fallback when it doesn't |
| A place to record rejected/failed records | Same idea, plus **connector health** as its own signal — is a credential expired, is a source rate-limiting us, did the source's structure change and break the mapping |
| One tenant, one demo run | **Backfill vs. incremental** as an explicit mode per source — a newly connected source needs a bounded, resumable initial load, not "run the regular sync loop and hope" |

**Concrete things worth being ready to say:**

- *"Each source maps its own native shape into one common internal schema — a wiki page and a support
  ticket both end up looking the same downstream, so the rest of the pipeline never has to know which
  source something came from."*
- *"One source failing is quarantined to that source — one system rate-limiting us shouldn't stall
  ingestion from every other connected source."*
- *"Permission data usually comes either from the same connector as the content, or from a separate
  entitlements feed — whatever system actually owns access decisions in production, like an admin
  console or an HR system — and that split should be modeled explicitly rather than assumed to always
  travel with the content."*

---

## What to say if asked directly

*"Document search proves permission-checked retrieval end to end. The real gap is a router in front
of it that recognizes when a question needs structured data — counts, filters, a specific record by
ID — instead of semantic search, and dispatches to a fixed set of operations or a carefully
constrained query instead. The same permission discipline that applies to document chunks — check
what the store can express, re-verify what it can't — has to extend to that structured path too,
because a leaked row is exactly as much of an incident as a leaked document."*
