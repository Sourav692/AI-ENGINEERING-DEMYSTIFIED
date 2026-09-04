# Identity, Secrets, Per-Tenant Keys and Fair Sharing

> **Level** 🟠 Scale, Security, Operations · **Module** 06 · **Doc** 1 of 7 · **Time** ~25 min
> **Prerequisites:** Module 04 doc 2 (ABAC), Module 05 doc 5 (guardrails)
> **Source material:** `3. AI_Engineer_Interview_Preparation/Cross Cutting Preparation/01-identity-secrets-and-tenant-fairness.md`

## Why this matters

Every authorisation rule in Modules 04 and 05 — who may read what, who may approve what — *assumes identity is already established*. The ABAC engine takes a `Principal` and trusts it. In the demos, that principal comes from a JSON file. In production, three questions sit in front of that engine and none of them are about authorisation: is this token real, where do the credentials for the customer's systems live, and can one tenant's traffic starve another's? This document is that plumbing. None of it needs a codebase; all of it needs to be defended on a whiteboard.

## 1 · Real identity — SSO/OIDC, not a local user table

A demo checks "who is this user" by looking them up in a local table. Production needs a layer in front: **authentication via the customer's own identity provider**, with roles mapped from the customer's own groups — never invented locally.

Why this is a different problem, not a bigger lookup: a local lookup answers *given a user ID, what are their attributes*. Real SSO/OIDC answers *is this token genuinely from the customer's identity provider, still valid, and who does it actually represent* — a **verification** problem.

| Step | What it means |
|---|---|
| **Token validation** | Check the signature against the identity provider's published keys; check expiry; check the token was issued for *your* app. Reject a forged or stale token before any permission logic runs |
| **Group mapping owned by the customer** | Their Okta or Azure AD groups are the source of truth; your platform maps them to your internal role vocabulary. That mapping is configuration that can silently drift — a group renamed on the customer's side orphans your mapping until someone notices |
| **Just-in-time provisioning** | The first time a user from a newly connected customer logs in there is no local record. One has to be created from the token's claims on the spot — correctly scoped to their company, never with more access than intended by default |

Once the token is validated and mapped, every downstream rule works exactly as if identity had been simple all along. The gap is entirely in front of that: verifying the claim is real, before handing it to logic that assumes it is. Module 04's `identity.py` resolving a principal fresh per request is the shape; the IdP integration is what replaces the JSON file.

## 2 · Secrets management — the pattern, not the slogan

Every platform that connects to a customer's CRM, ticketing or knowledge base needs credentials for those systems. "Store secrets in a vault" is the right instinct but not an answer. The mechanism:

| Principle | What it means |
|---|---|
| **Reference, never the value** | A connector holds a *pointer* to a secret — a vault path or key ID — never the credential. The credential is resolved at the moment of use, and it is never logged, never written into a trace, never passed as a plain argument between steps |
| **Envelope encryption** | The secret is encrypted with its own key; that key is encrypted by a master key held centrally. Rotating the master then means re-wrapping the small keys, not re-encrypting every secret — the reason "encrypt everything with one key" does not scale operationally |
| **Rotation without downtime** | On a schedule, or immediately on suspected compromise, without breaking work in flight — the old version stays valid for a short grace window while new calls pick up the new one |
| **Scoped per connection, not per connector type** | A leaked credential for one customer's helpdesk connection must never grant access to a different customer's helpdesk, even though both use the same *kind* of connector |

Module 05's coverage map names the connector layer and vault as unbuilt. This is what the `Connector` model would reference.

## 3 · Per-tenant encryption keys — what "per tenant" actually buys

Beyond a tenant-id tag on every row, the stronger property: **if one tenant's encryption key is compromised, the blast radius is that one tenant — not the platform.**

- Every tenant gets its own data-encryption key, itself wrapped by a shared or per-tenant master key — the same envelope pattern.
- This is the cryptographic version of Module 04's per-tenant collection: physical or cryptographic separation instead of one shared pile with a filter on top.

The tell in a design conversation: *"What happens if someone gets raw read access to the storage layer?"* With per-tenant keys: "they get one tenant's ciphertext, and only that tenant's key would ever decrypt it." With one platform-wide key: the same breach exposes every customer at once.

## 4 · Queue fairness — a different problem than rate limits

Rate limiting stops one tenant from exceeding *their own* allotment — a **ceiling**. Module 04 built exactly that. There is a separate, easy-to-miss problem: can one large tenant's burst make a *small, well-behaved* tenant wait longer for their turn, even though the small tenant never exceeded any limit?

- A rate limit answers *may this request proceed at all*. A fair queue answers *in what order do requests get served under load*. Orthogonal; a real platform needs both.
- The standard mechanism: **weighted fair queuing**, or a token bucket per tenant feeding a shared worker pool, so throughput is shared proportionally under contention — not first-come-first-served, which lets one tenant's burst monopolise everyone's capacity.

## Interview lens

> *"Authorisation logic assumes identity is already established. In front of it, production needs real SSO/OIDC — validating the customer's own token, mapping their groups into my role vocabulary rather than inventing roles locally. Underneath it: credentials resolved from a vault by reference and never logged, with per-tenant encryption keys so one tenant's breach doesn't expose everyone else. And one thing worth calling out: rate limiting stops a tenant exceeding their own budget, but it doesn't guarantee fairness between tenants competing for shared capacity — that's a queuing problem, not an authorisation problem, and it's easy to conflate the two."*

## Checkpoint

- What three things does token validation check, and why must it happen before any permission logic?
- Why is group mapping "configuration that can drift", and what does drift look like?
- Explain envelope encryption and the operational problem it solves.
- Why must a credential be scoped per connection rather than per connector type?
- Distinguish a rate limit from a fair queue in one sentence each.

**Next →** [Observability Standards and Failure Patterns](02_Observability_Standards_Failure_Patterns.md)
