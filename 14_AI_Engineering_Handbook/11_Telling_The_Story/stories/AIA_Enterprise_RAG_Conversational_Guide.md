> **Level** 🔴 Telling the Story · **Module** 11 · **stories/** · **Format:** open-ended conversational guide
> **Source material:** `4. FDE_Related_Preparation/Star_Stories/AIA_Enterprise_RAG_Conversational_Guide.md` — kept as a worked example of the format described in [Deep-Dive and Conversational Formats](../01_Deep_Dive_And_Conversational_Formats.md). It is one engineer's own engagement narrative; use it as a template for the shape, not a script to repeat.

---

# The RAG Governance Layer at AIA Group — Open-Ended Conversational Guide

### For: MongoDB Director · Format: fluid discussion, not a fixed slot · Frames the ABAC/governance work as the access-control layer inside AIA's real Multi-Tool agent

> **How this differs from the deep-dive version:** that one is a script you move through top to bottom. This is a **toolkit** — self-contained "story beats" (30–60 seconds each) deployed in whatever order the conversation goes, plus bridges and a topic-organized "go deeper" menu. New in this version relative to the original standalone guide: a discovery/scoping beat, since that's the FDE-differentiating material.

> **Honesty note to hold internally:** this specific sub-component's depth (document-governance inside the Multi-Tool agent) is a well-reasoned extension of the real AIA engagement, not something already spelled out verbatim in the headline story. Own it as "the layer I'd go deep on if asked," delivered with full confidence.

---

## The one-sentence cold open

If asked "tell me about something you built" with zero other context:

*"At AIA, one of the agents I built answered questions over policy and claims documents — and the hardest part wasn't finding the right answer, it was that the same question needed a different correct answer depending on who was asking, across roles and markets. I wanted to prove that boundary never breaks, not just hope it doesn't."*

Then wait. Let their next question tell you which beat to go to.

---

## Core story beats (deploy independently, any order)

### Beat 0 — AIA's real problem, zoomed in

*"You know the headline AIA story — actuaries, claims managers, analysts needed self-serve natural-language answers over governed data instead of a 2-to-10-day BI queue. One of the four agents in that system, the Multi-Tool agent, handled the retrieval half — policy wordings, claims files, underwriting notes. That's exactly where access control got hard: multiple markets, each with its own regulator and data-residency rules, documents carrying health disclosures, and an actuary needing something completely different from what the claims manager actually handling that case needs."*

**Bridge to the next beat:** *"So before I designed anything, I had to actually go find out what each role legitimately needed — that's usually the part people skip."*

### Beat A — Discovery and scoping, before any code

*"I didn't start from a spec. I sat with vv, claims managers, and analysts directly to understand real usage patterns, and separately with compliance, legal, and security to map document sensitivity and regulatory non-negotiables per market — those two conversations surface different things, and you need both. That became a role-by-document-type-by-market access matrix, which is what the policy engine's rules actually came from. And I deliberately scoped the first build to two business units in one market, so I could prove the model was airtight before expanding it — access-control mistakes compound fast if you scale before validating."*

**Why this beat matters in open conversation:** it's the material a purely technical candidate hasn't prepared, and it directly answers "how do you approach a new engagement" without being asked that exact question.

### Beat B — The two-layer defense (business-first)

*"I built it with two checkpoints. A fast one at the door that gets you into the right neighborhood of documents for your role and market. And a slower, careful one right before you're actually handed anything — because your permissions might have changed in the gap between those two moments: a case reassignment, a revoked grant, a consent window closing."*

**Bridge to technical:** *"In system terms, that's a metadata pre-filter compiled into the Databricks Vector Search query, and a live re-check against Unity Catalog's current grants right before the agent generates an answer."*

### Beat C — The trust story: bugs my own testing caught

*"Three mistakes I want to tell you about, because how you respond to your own testing catching you is more informative than a clean story. My harness once flagged a false leak — a claims manager shown a case outside their assignment — but they'd actually just been reassigned it; my test data was stale, not the system. I found one policy rule that no test was actually exercising because a stricter rule kept masking it. And I pulled the model's judgment completely out of the leak/no-leak decision, because a security call can't be probabilistic — that's hard rules only."*

**Why this beat works in open conversation:** it naturally invites "how did you catch that" — good, let the conversation do your work.

### Beat D — The platform-reality insight (your strongest MongoDB bridge)

*"Building this inside AIA's actual Databricks environment, I found something that generalizes beyond that platform: a Vector Search index is a derived copy of your governed data — it doesn't automatically inherit Unity Catalog's row-level rules. If someone's access is revoked at the source, that doesn't reach the index on its own; you have to re-verify, live, at query time."*

**Bridge to MongoDB directly, if the moment allows:** *"That's true of any architecture where a vector index sits next to, but separate from, your governed operational data — which is exactly the shape of the problem for anyone building AI features on top of Atlas."* (Only if it feels natural.)

### Beat E — Honest limitations (deploy proactively)

*"I'll flag this myself: the MVP is scoped to two business units, one market — I haven't proven this at AIA's full document estate or market footprint, and I'd expect the retrieval-strategy choice to need re-evaluating at that scale. What holds regardless of scale is the zero-leak gate and the discovery process behind the policy rules."*

---

## Bridges — moving between business and technical mid-sentence

- *"...which, in plain terms, means..."*
- *"...think of it like [analogy] — technically that's called [term], but the idea is..."*
- *"I can go as deep as you'd like on the how — where should I take this?"*
- *"The business reason I did that is X; the engineering reason is Y."*

---

## The "go deeper" menu — organized by what they might ask about

### If they ask about **how you approached the engagement / discovery**

- Direct stakeholder interviews (actuaries, claims managers, analysts) for real usage patterns.
- A separate dedicated session with compliance, legal, and security for regulatory non-negotiables and document sensitivity classification.
- Synthesized into a role × document-type × market access matrix — the actual source of the policy rules, not a retrofit.
- Deliberately narrow MVP scope (two business units, one market) to prove the model before expanding.
- Success bar (zero leaks, explainability, latency) agreed with the business sponsor and compliance *before* the build started.

### If they ask about **architecture / how it's built**

- Pipeline: classify → resolve governed attributes → retrieve (constrained) → re-verify (live) → generate → log via MLflow.
- Seven-rule deny-by-default policy: business unit, market, clearance tier, timing/consent window, need-to-know case assignment, external-contractor flag, default deny. Deny always overrides allow.
- Fast layer = metadata filter compiled into Databricks Vector Search; slow layer = live Unity Catalog grant re-check right before generation.

### If they ask about **why you chose your retrieval approach**

- Benchmarked several strategies against the same governed test set instead of picking one on instinct.
- Honest result at this scoped MVP's scale: the simpler approach was the right production choice; the fancier one cost more without earning its keep yet — expected to flip once the document estate scales past the MVP boundary.

### If they ask about **testing philosophy / how you validate AI systems**

- Security correctness decided by hard rules only, never the AI's judgment.
- Zero-leak eval harness gates releases — one leak on the governed test set and it doesn't ship.
- A standalone check keeps security documentation in sync with running policy code, so what compliance/regulators were told can't silently drift from what's deployed.

### If they ask about **deployment / running this at AIA's actual scale**

- The platform-reality lesson from Beat D: verify governance independently on the platform you're on, never assume it travels automatically from the source system.
- What would need to change at full scale: a larger, tiered evaluation corpus, and re-running the retrieval-strategy comparison once the document estate is representative.

### If they ask about **what you'd do differently / next steps**

- Bring compliance into the *very first* round of discovery conversations rather than a separate follow-up pass.
- Re-run the retrieval-strategy benchmark at a realistic AIA-scale document count before trusting the current result beyond the MVP boundary.
- Design a scaling plan for the access-matrix maintenance process itself as more business units and markets get added.

---

## Reading the room — quick cues

| Signal                                      | What it means                                   | What to do                                                        |
| ------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------- |
| Nodding, staying quiet                      | They're tracking, want the story to keep moving | Continue at current depth                                         |
| "How exactly did you gather that?"          | Green light to go deeper on discovery/scoping   | Move into Beat A's specifics                                      |
| "How exactly does the access control work?" | Green light on the technical layer              | Move from Beat B's plain-English framing into the technical layer |
| Redirecting to a different angle            | They want a different lens                      | Drop what you're doing, follow their thread                       |
| Silence after a technical sentence          | Went too deep too fast                          | Re-anchor in plain English immediately                            |
| Checking the time / wrapping-up language    | Time to close                                   | Go straight to a closing line, skip the menu                      |

---

## Closing lines (pick based on how the conversation actually ended)

**If it ended on the discovery/scoping thread:**
*"That's really the part of this job I care about proving — the build only worked because the discovery before it was rigorous. Anyone can build an access-control system to a spec; the harder skill is figuring out what the spec should actually be."*

**If it ended on the security/trust thread:**
*"That's the throughline for me — an FDE's job is turning a technical guarantee into something a customer's security team can sign off on, and that's exactly the muscle this project built."*

**If it ended on the platform/deployment thread:**
*"That's the instinct I'd bring to any customer's stack — don't assume a guarantee travels between systems until you've verified it yourself, on their specific platform."*

**If it ended on limitations/what's next:**
*"I'd rather tell you exactly where the edges of what I've proven are than let you find them later — that's more useful than a system that claims to have no edges at all."*

**Generic fallback, any ending:**
*"Happy to go deeper on any piece of this — the discovery process, the policy engine, the testing setup, or the platform work — whichever's most useful to you."*
