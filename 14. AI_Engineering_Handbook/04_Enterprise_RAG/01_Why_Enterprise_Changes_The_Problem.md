# Why Enterprise Changes the Problem

> **Level** 🟡 Building Production Systems · **Module** 04 · **Doc** 1 of 10 · **Time** ~35 min
> **Prerequisites:** Module 01 docs 1–2
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/README.md` (business case), `docs/01-theory.md` §2, §7 (the three patterns, "groups overlap")
> **Lab:** `project/notebooks/02-hands-on-parts/part01-corpus-and-permissions.ipynb`

## Why this matters

Module 01 gave you the two-box picture of RAG and warned that the enterprise version has a problem: *which* documents the first box may find depends on who is asking. This module builds the whole system around that problem. Before the mechanics, you need to feel the problem concretely enough that every later design decision seems inevitable — because in the source project, it was.

## The case study: Meridian Assist

**Meridian Cloud** is a B2B SaaS observability company. Support engineers, account managers and security staff all need answers from the same knowledge base: help-centre docs, engineering runbooks, support tickets, incident post-mortems, customer contracts, pricing policy and security advisories. Twenty-two documents in the demo corpus; six source types; four sensitivity levels.

They cannot all see the same things.

> *"Why did Vertex Financial lose data in March, and do they get service credits?"*

| Who asks | What they should get |
|---|---|
| Tier-1 support agent | Platform-side backlog; credits are an account-manager conversation |
| Tier-3 engineer | The engineering root cause; the account is credit-eligible |
| Account manager | The contractual credit tiers — but not the engineering root cause |
| External contractor | Nothing — blocked by data residency and the external-source rule |
| Anyone in another tenant | Nothing at all, regardless of their groups or clearance |

Getting that right — **provably**, not by prompting the model nicely — is what the project is about. Draw this table early in any design conversation; it *is* the requirement, and everything after it is justified by it.

## Three patterns for access control, and why two of them are wrong

Every enterprise RAG design has to answer one question: *where does the permission check happen relative to retrieval?* There are three answers.

### (a) Post-filter — retrieve everything, then drop what they cannot see

Tempting, because it is the smallest change to a demo. Wrong, for two independent reasons.

```
  top 6 retrieved:   [contract] [postmortem] [contract] [helpdoc] [postmortem] [helpdoc]
  after filtering:                                      [helpdoc]              [helpdoc]
                     ^^^^ the user's top-6 became a top-2, and the good stuff was crowded out
```

You asked the vector store for top-6. After ACL filtering, two help-docs remain. The contracts and post-mortems were relevant but not allowed, so they occupied slots and then disappeared.

**Quality failure.** The model never sees the best *allowed* answers if they sat below forbidden hits. You did not retrieve six allowed chunks; you retrieved six overall and threw most away. Recall collapses for exactly the users with the most restricted views.

**Security failure — the existence oracle.** Even after dropping content, the *shape* of the result leaks. "0 results" vs "2 results", or a slower query, hints that matching classified documents exist. An attacker probes: *do I get fewer hits for this secret topic?* The filter hid the text and revealed the existence.

### (b) Partitioned indexes — one index per tenant or per group

Physically split the data: `index_meridian`, `index_acme`, `index_engineering`. A query is routed only to the index(es) the user belongs to. Other tenants' chunks are *not in the candidate set at all*.

**Why isolation is strongest:** a bug in a `where` clause cannot leak another tenant, because those vectors are not on the index being searched. The blast radius of a mis-filter or a stolen key is one partition.

**Why it is expensive:** one collection per tenant to build, warm, back up and monitor. Small tenants waste capacity; cross-tenant features need extra plumbing.

**Why groups make it awkward:** a document allowed to *engineering* **and** *support-tier3* has no single home. Put it in both indexes → duplicate embeddings that drift on update. Put it in one union index → you are back to filtering inside a mixed set. Fan the query out across every group index → merge N result lists with inconsistent scores.

Tenants almost never overlap. Groups overlap constantly. So: **partition by tenant, not by group.**

### (c) Pre-filter — push the permission check *into* the search ✅

```
   search(query_vector, where = { tenant = X AND sensitivity <= Y AND groups overlap Z })
```

Unauthorised chunks are **never scored, never ranked, never returned**. The user's top-6 is the best six *of what they are allowed to see*. No crowding-out, no existence oracle — the forbidden documents were never candidates.

## What the project actually does: (b) + (c) + a post-check

1. **Partition** — one Chroma collection per tenant. The blast-radius wall.
2. **Pre-filter** — the decidable part of the policy compiled into every vector search. Cheap and approximate.
3. **Post-check** — the *full* policy re-evaluated on every candidate before the model sees text. Correct, including everything the vector store's filter language cannot express.

Is step 3 not just pattern (a) again? No, and the distinction is the single most important idea in this module:

| | (a) Post-filter as the *only* ACL | This project's post-check (`enforce`) |
|---|---|---|
| When | After an **unfiltered** top-k | After a **pre-filtered** top-k |
| Job | Drop secrets that already occupied rank slots | Re-run the full policy on candidates (embargo, need-to-know, live IdP state) |
| Quality | Crowds out allowed docs → leftover 2 of 6 | Pool was already allowed; a drop is rare (stale index, time-based rule) |
| Trust | The *only* gate — skip it and you leak | The **authoritative** gate; the pre-filter is an optimisation |

Defence in depth: if the filter is wrong, the tenant partition still holds. If the index is stale, the post-check still denies — and logs the disagreement as a security signal.

## "Groups overlap" — two meanings, keep them apart

The phrase appears in the pre-filter (`groups overlap (engineering, …)`) and in "partitioning is awkward when groups overlap". They are different ideas.

**Meaning 1 — the access rule.** A document lists who may read it (`allowed_groups`); a user lists which teams they are on (`groups`). The rule passes if the intersection is non-empty — *any* shared group, not all of them.

```
   user.groups ∩ document.allowed_groups  ≠  ∅
```

| User groups | vs `allowed_groups: security, engineering` | Result |
|---|---|---|
| `{engineering}` | intersection `engineering` | pass |
| `{security, sre}` | intersection `security` | pass |
| `{support-tier1}` | empty | fail |

The vector store cannot filter on a list, so this becomes one boolean column per group (`grp__engineering: true`) and an `$or` over them. Mentioning that bridge is how you show you have built it.

**Meaning 2 — the partitioning problem.** One document tagged with *several* groups has no single group-index to live in. That is the argument against per-group partitions above.

One line: overlap for **access** = "share a group → can see it". Overlap for **partitioning** = "one doc, many groups → no single index".

## Interview lens

This document is the first eight minutes of the RAG whiteboard script in Module 09. The framing sentence:

> *"Anyone can build multi-source RAG. What makes this hard is that a Tier-1 agent, a Tier-3 engineer and an account manager must get different correct answers to the same question — so access control isn't a feature I add at the end, it decides the shape of the retrieval path."*

And the pattern choice: *"(b) and (c) together — partition by tenant and pre-filter within it — with an authoritative post-check, because the filter language is weaker than the policy language."*

## In the code

| Concept | Where |
|---|---|
| Per-tenant collection | `project/src/enterprise_rag/ingest/store.py` → `get_collection`, `SETTINGS.collection_for(tenant_id)` |
| Pre-filter compilation | `authz/policy.py` → `compile_prefilter` |
| Post-check | `authz/enforcement.py` → `enforce` |
| Group flags as boolean columns | `models.py` → `Chunk.to_metadata`, `attrs_from_metadata` |
| The personas | `project/data/identities.json` (9 personas, each exercising a different rule) |
| Notebook | `project/notebooks/02-hands-on-parts/part01-corpus-and-permissions.ipynb` |

## Checkpoint

- Draw the "top-6 became top-2" diagram and name both failures it illustrates.
- Why partition by tenant but not by group?
- Explain, in a table, how the project's post-check differs from post-filtering as the only ACL.
- State both meanings of "groups overlap" in one sentence each.
- For the Vertex Financial question, what does each of the five personas get, and why?

**Next →** [Access Control with ABAC](02_Access_Control_ABAC.md)
