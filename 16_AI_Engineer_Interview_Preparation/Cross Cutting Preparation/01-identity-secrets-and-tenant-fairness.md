# Identity, secrets, encryption, and fair sharing

Foundational plumbing for any multi-tenant AI platform. None of this needs a codebase — it's
architecture to defend on a whiteboard.

---

## 1. Real identity — SSO/OIDC, not a local user table

A simple system checks "who is this user" by looking them up in a local table. That's fine for a
demo. Production needs a layer in front of it: **authentication via the customer's own identity
provider (SSO/OIDC)**, with roles mapped from the customer's own groups — never invented locally.

**Why this is a different problem, not just a bigger lookup:** a local lookup answers "given a user
ID, what are their attributes." Real SSO/OIDC answers "is this token genuinely from the customer's
identity provider, still valid, and who does it actually represent" — a **verification** problem:

- **Token validation** — check the signature against the identity provider's published keys, check
  expiry, check the token was issued for your app specifically. Reject a forged or stale token before
  any permission logic runs at all.
- **Group mapping is owned by the customer, not you.** Their Okta or Azure AD groups are the source
  of truth; your platform maps them to your internal role vocabulary. That mapping is configuration
  that can silently drift — a group renamed on the customer's side orphans your mapping until someone
  notices.
- **Just-in-time provisioning.** The first time a user from a newly connected customer logs in, there's
  no local record for them yet — one has to be created from the token's claims on the spot, correctly
  scoped to their company, never created with more access than intended by default.

**Where this connects to everything else:** once the token is validated and mapped to a role, every
permission rule downstream — who can see what, who can approve what — works exactly the same as if
identity had been simple all along. The gap is entirely in front of that: verifying the claim is real,
before handing it to logic that already assumes it is.

## 2. Secrets management — the actual pattern, not just "use a vault"

Every platform that connects to a customer's other systems (CRM, ticketing, a knowledge base) needs
credentials for those systems. "Store secrets in a vault" is the right instinct but not yet an answer.
The mechanism worth having ready:

- **Reference, never the value.** A connector holds a *pointer* to a secret (a vault path or key ID),
  never the credential itself. The credential is resolved only at the moment it's used, and it's never
  logged, never written into a trace, never passed around as a plain argument between steps.
- **Envelope encryption.** The secret is encrypted with its own key; that key is itself encrypted by a
  master key held centrally. Rotating the master key then only means re-wrapping the small keys, not
  re-encrypting every secret — the standard reason "just encrypt everything with one key" doesn't
  scale operationally.
- **Rotation without downtime.** A credential can be rotated on a schedule (or immediately, on
  suspected compromise) without breaking work already in flight — the old version stays valid for a
  short grace window while new calls pick up the new one.
- **Scoped per connection, not per connector type.** A leaked credential for one customer's helpdesk
  connection should never grant access to a different customer's helpdesk, even though both use the
  same *kind* of connector. Scope the credential to the specific customer + connection, not the
  general integration.

## 3. Per-tenant encryption keys — what "per tenant" actually buys you

Beyond storing data with a customer-id tag, the stronger property: **if one tenant's encryption key
is ever compromised, the blast radius is that one tenant only — not the whole platform.**

- Every tenant gets its own data-encryption key, itself wrapped by a shared or per-tenant master key
  (the same envelope pattern as above).
- This is the encryption-side version of the same idea used for stronger tenant isolation elsewhere —
  physical or cryptographic separation, instead of one shared pile of data with a filter on top.
- **The interview tell:** if asked "what happens if someone gets raw read access to the storage
  layer," the answer with per-tenant keys is "they get one tenant's ciphertext, and only that tenant's
  key would ever decrypt it" — versus one platform-wide key, where the same breach exposes every
  customer at once.

## 4. Queue fairness — a different problem than rate limits

Rate limiting stops one tenant from exceeding *their own* allotment — a **ceiling**. There's a
separate, easy-to-miss problem: can one large tenant's burst of traffic make a *small, well-behaved*
tenant wait longer for their turn, even though the small tenant never went over any limit of their
own?

- A rate limit answers "may this request proceed at all." A fair queue answers "in what order do
  requests get served when the system is under load" — these are orthogonal, and a real platform
  needs both.
- The standard mechanism: **weighted fair queuing**, or giving every tenant their own token bucket
  feeding into a shared pool of workers, so throughput gets shared proportionally under contention —
  not simple first-come-first-served, which lets one tenant's burst monopolize everyone else's
  capacity.

---

## What to say if asked directly

*"Authorization logic — who can see what, who can approve what — assumes identity is already
established. In front of that, production needs real SSO/OIDC: validating the customer's own token,
mapping their groups into my role vocabulary rather than inventing roles locally. Underneath the
authorization logic: credentials resolved from a vault by reference and never logged, with per-tenant
encryption keys so one tenant's breach doesn't expose everyone else. And one thing worth calling out
directly: rate limiting stops a tenant from exceeding their own budget, but it doesn't guarantee
fairness between tenants competing for the same shared capacity — that's a queuing problem, not an
authorization problem, and it's easy to conflate the two."*
