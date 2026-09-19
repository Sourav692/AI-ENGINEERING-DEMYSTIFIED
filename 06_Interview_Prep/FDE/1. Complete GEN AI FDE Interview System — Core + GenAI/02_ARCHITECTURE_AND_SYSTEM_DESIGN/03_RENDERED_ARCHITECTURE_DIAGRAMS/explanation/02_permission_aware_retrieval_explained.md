# 02. Permission-Aware Retrieval
## What the diagram shows

This diagram shows how retrieval should respect user permissions before context reaches the LLM. The user JWT is resolved into tenant and access-control claims. In parallel, the query embedding retrieves candidate chunks. The permission filter intersects candidate chunks with ACL claims, then a re-ranker orders safe chunks. Only the safe context is sent to the LLM. Audit logs capture what was retrieved, filtered, denied, and used.

The core idea is simple: the LLM should never receive content the user is not allowed to see.

## How to explain it in an interview

A strong spoken explanation could be:

> I would not treat vector search as a separate trusted system. Every chunk must carry metadata such as tenant ID, document ID, classification, owner, group ACLs, region, and expiry status. The user token is converted into normalized permission claims. Retrieval can produce candidates, but before ranking and generation we must filter by tenant and ACL. I would log both allowed and denied retrieval decisions so that security and support teams can investigate permission bugs.

## Key trade-offs

- **Pre-filtering vs post-filtering:** Pre-filtering is safer and cheaper but may reduce recall if metadata is incomplete. Post-filtering is flexible but dangerous if unsafe chunks reach the LLM.
- **Chunk-level ACL vs document-level ACL:** Chunk-level ACL is more precise but harder to maintain.
- **Strict permission filtering vs user satisfaction:** Users may get “I do not have access” responses even when similar unrestricted content exists.
- **Re-ranking before vs after filtering:** Re-ranking after filtering is safer because restricted chunks are never used for ranking context.

## Failure modes

- Chunk metadata is missing or stale after document permission changes.
- User JWT contains group claims that are too broad.
- Candidate retrieval crosses tenant boundaries.
- Re-ranker sees restricted chunks before the permission filter.
- Cached answers are reused for users with different permissions.
- Audit log records only final answer, not filtered chunks.
- Permission updates are not propagated to the vector index quickly enough.

## Security concerns

- Enforce tenant filter at the database query level, not only in application code.
- Store ACL metadata with every chunk and keep it synchronized with source systems.
- Avoid caching retrieved context across users unless cache keys include tenant and ACL scope.
- Log denied retrieval attempts without exposing restricted text.
- Add tests for cross-tenant leakage, stale permissions, and privilege downgrade scenarios.

## What a weak candidate misses

A weak candidate says: “We will check permissions before showing the answer.” This is too late. If restricted content entered the prompt, the system already leaked data internally and may leak it in the response.

## What a strong candidate says

A strong candidate explains that permission filtering must happen before context construction. They mention tenant-aware metadata filters, ACL synchronization, cache isolation, audit trails, and regression tests that prove restricted documents are never included in prompts.

## Visual improvement suggestion

Show two lanes:

- **Identity/Control Lane:** JWT → Tenant Resolver → ACL Claims → Permission Decision
- **Retrieval/Data Lane:** Query Embedding → Candidate Chunks → Metadata Filter → Re-ranker → Safe Context

Add a clear red boundary: **“No restricted chunk may cross this boundary into the LLM prompt.”**
