# Appendix C · Interview Q&A Log

> **Reference artefact.** A running log of conceptual questions asked while preparing the Enterprise RAG project (Module 04), with full answers. Kept as written; each answer deepens a point made in Module 04 doc 2 (the two-layer split), doc 3 (the ACL catalog), or doc 5 (`merge_filters`).
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/QA.md`

---


Running log of questions asked during prep, with full detailed answers.

---

**Q: In a real enterprise system, do the docs have the check fields embedded in the doc, or do we
generally have a different table which has the info for each doc?**

A: In real enterprise systems, the ACL/sensitivity fields almost never live inside the document
itself — they live in a separate document catalog/metadata store, and the ingest pipeline resolves
them by looking up the source system's own permission model. This demo embeds them as markdown
front-matter purely to keep the corpus self-contained and readable for a demo/interview — that's a
simplification, not the production pattern.

**Why real systems separate them:**

1. **Permissions change independently of content.** A Confluence page's group ACL can change on
   Monday without the page text changing at all. If ACLs were baked into the document, every
   permission change would require re-ingesting/re-chunking/re-embedding — expensive and slow. A
   separate catalog lets you update just the ACL row.
2. **The source of truth is the source system, not the RAG pipeline.** Confluence space permissions,
   SharePoint group ACLs, Zendesk organization visibility, Salesforce sharing rules — these are
   already the authoritative permission model, owned by another team/system. The RAG platform's job
   is to *translate* that model into its own attribute schema (tenant, sensitivity, region,
   allowed_groups...), not invent it. These fields are not invented by the RAG pipeline — they are a
   translation of each source system's own permission model.
3. **Live revocation.** If someone's access is pulled, you need that reflected immediately, without
   touching the document text or vector index at all. That only works if identity/permission lookups
   are a live call to a directory or catalog, not something frozen into the doc at embed time.

**How it actually looks in production**, roughly:

| Layer                         | What it is                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Document content              | Lives wherever it always lived — Confluence, SharePoint, Zendesk, S3, etc.                                                                                                                                                                                                                                                                                                                                                                                       |
| Document metadata/ACL catalog | A separate table/service — often literally a Delta/Postgres table keyed by`doc_id` — storing `sensitivity`, `region`, `allowed_groups`, `owner`, `source_system_id`, etc. This is what `store.py`'s docstring means by *"in production this is a row in the document catalogue, not a dict"* (referring to `_DOC_ATTRS`).                                                                                                                     |
| Ingest connector              | Reads the source system's native permission model (e.g. Confluence space + page restrictions) via API, translates it into the platform's ACL schema, writes a catalog row. Refuses/quarantines anything it can't confidently map — this demo's`loader.py` does a toy version of that same refusal.                                                                                                                                                             |
| Vector store metadata         | Usually carries a**copy** of the ACL fields (denormalized onto each chunk) purely so the pre-filter can be pushed into the vector query cheaply — same pattern as this demo's Chroma metadata. But that copy is explicitly treated as a cache, not authoritative — which is exactly why a post-retrieval re-check against the live catalog/directory (Layer 2) is still required. A stale denormalized copy is the normal failure mode, not an edge case. |
| Identity                      | Resolved fresh per request from the IdP/directory (Okta, Entra ID, SCIM-synced groups) — never cached in a session, same as`identity.py` in this repo.                                                                                                                                                                                                                                                                                                         |

**Mental model for the interview:** content storage, ACL catalog, and identity directory are three
separate systems; the vector store's per-chunk metadata is a *denormalized, potentially-stale copy*
of the catalog used only for cheap pre-filtering (Layer 1), and the catalog/directory is queried
again post-retrieval for the authoritative check (Layer 2) — this is precisely the physical/logical
and Layer 1/Layer 2 split documented in `docs/04` §0, just naming where each side's data actually
lives in a real deployment.

---

**Q: So if some ACL field value is changed every day, do we have to sync the vector store metadata
from scratch every day?**

A: No — you don't need to re-embed anything, and you don't need a full nightly rebuild either. Two
things save you:

**1. Metadata updates are cheap and separate from embedding.** The vector (the expensive part — the
embedding model call) is a function of the *content*, not the ACL. If only
`sensitivity`/`allowed_groups`/`region` changed, you update just the metadata on the existing chunk
rows — Chroma (and every other vector DB) supports a metadata-only update/upsert that leaves the
vectors untouched. So "sync ACLs daily" is a cheap `UPDATE ... SET metadata` style operation, not a
re-ingest.

**2. Even if you never sync it, you don't have a security problem — only a performance one.** This is
the whole point of the Layer 1 / Layer 2 split from `docs/04`. Layer 1 (the vector store's pre-filter
metadata) is explicitly allowed to be stale — it's an optimization, not the source of truth. Layer 2
re-queries the live catalog/directory on every single request, so even a metadata copy that's a week
stale can never leak anything: a revoked user still gets denied at Layer 2 regardless of what the
cached copy in Chroma says.

What staleness actually costs you is **overshoot** — Layer 1 lets through candidates that Layer 2 then
has to reject, wasting retrieval slots/latency and (per `enforcement.py`) logging a
`filter_disagreements` / `security_event` every time that happens. So sync frequency is purely a "how
much wasted work am I willing to tolerate" dial, not a correctness requirement.

**How real systems actually handle this**, roughly, in order of sophistication:

- **Cheapest / most common**: a scheduled batch job (daily or hourly) that re-pulls ACL fields from
  the catalog/source system and does a metadata-only upsert into the vector store for changed
  `doc_id`s. Simple, and the daily-stale window is fine precisely because Layer 2 backstops it.
- **Better**: event-driven — the source system (Confluence webhook, IAM change stream, Okta
  group-change event) fires, and a small job updates just that doc's metadata immediately. Lower
  overshoot, more moving parts.
- **What you should never do**: treat the vector store's metadata as authoritative and skip the
  post-retrieval re-check to save latency — that's the one move that actually turns staleness into a
  real leak, because then nothing is querying live state at all.

**Interview line:** *"ACL sync frequency into the vector store is a latency/efficiency tuning knob,
not a security control — security lives entirely in the post-retrieval re-check against the live
catalog, which is why Layer 1 is allowed to be as stale as your ops budget tolerates."*

---

**Q: "Layer 2 re-fetches each doc's rule from the catalog and re-decides — catches everything Layer 1
structurally can't (embargo, need-to-know, obligations, live revocation)." Why can't Layer 1 do
this?**

A: Layer 1 is a filter compiled once and pushed into the vector query — a static, pre-compiled
snapshot. Each of the four fails it for a different structural reason:

1. **Embargo/expiry — needs "now".** The filter is compiled at query-build time; whether a document
   is currently published depends on the moment the query *runs*, which a static filter has no way to
   reference. Left out entirely; Layer 2 evaluates it against the real current date every request.
2. **Need-to-know — list-subset semantics.** Chroma's filter language only supports scalar
   comparisons (`$eq`, `$lte`, `$or` of those). Group membership fakes "any overlap" via one boolean
   column per group, but need-to-know needs "principal holds **every** tag on the doc" — a genuine
   subset check with no boolean-column trick available.
3. **Obligations (e.g. PII redaction) — a transformation, not a filter.** A filter can only decide
   yes/no on whether a row comes back. Redaction needs the row to come back **with its text
   rewritten** — filters can't modify content, only gate it.
4. **Live revocation — the index is a snapshot.** The vector store's metadata was written once, at
   ingest time, and stays exactly that stale until something re-upserts it. Layer 2 avoids this
   entirely by never reading that copy — it re-resolves the principal and re-fetches the document's
   attrs fresh from the ACL catalog on every request, so a revocation from a second ago is already
   visible.

**One line:** Layer 1 is a pre-compiled snapshot filter; anything needing the current moment,
all-of list logic, content rewriting, or the *latest* value of something that can change after
indexing is structurally outside what a filter compiled once and cached in an index can represent.

---

**Q: "ACL fields already live in Chroma metadata and are already used as a filter — so why does
docs/07 list 'metadata filters as first-class' as a gap?"**

A: They're two different axes answering two different questions, even though both end up as a Chroma
`where` clause on the same metadata.

- **ACL filter (already built, Layer 1).** `compile_prefilter(principal)` builds `where` entirely
  from the principal's identity, automatically, on every query — the caller has no say in it.
  Answers: *"given who's asking, what are they even allowed to see?"*
- **Content/relevance filter (the actual gap).** A user asking *"just search runbooks"* or *"only
  documents from the last 90 days"* is expressing intent about **what** to search, not **who** they
  are. There is currently no code path for a caller of `RAGPlatform.ask()` to supply that — `where`
  in `RetrievalContext` is 100% owned by `compile_prefilter()`; nothing merges in a second,
  caller-supplied clause.

Why "low effort" to close: the *data* already exists in Chroma metadata (`source` is already a
column, populated for the `external_restriction` ACL rule) — nothing needs to be added to ingestion
or storage. The fix is adding a second, optional input to `RetrievalContext`/`ask()` and merging it
with `$and` alongside the mandatory ACL filter — same mechanism, two different owners (policy engine
= unconditional; content filter = optional, caller-supplied).

**Interview line:** *"The ACL filter and a content filter are the same mechanism — a Chroma `where`
clause — but two different owners: the policy engine always contributes one, unconditionally; a
content filter would be optional and caller-supplied. They compose with `$and`."*

---
