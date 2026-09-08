> **Level** 🔴 Telling the Story · **Module** 11 · **stories/** · **Format:** open-ended conversational guide
> **Source material:** `4. FDE_Related_Preparation/Star_Stories/Enterprise_RAG_Conversational_Guide.md` — kept as a worked example of the format described in [Deep-Dive and Conversational Formats](../01_Deep_Dive_And_Conversational_Formats.md). It is one engineer's own engagement narrative; use it as a template for the shape, not a script to repeat.

---

# Enterprise RAG (Meridian Assist) — Open-Ended Conversational Guide
### For: MongoDB Director · Format: fluid discussion, not a fixed slot · Goal: same substance as the deep-dive, delivered adaptively

> **How this document differs from the 15–20 minute deep-dive:** that one is a script you move through top to bottom. This one is a **toolkit** — a set of self-contained "story beats" (30–60 seconds each) you can deploy in whatever order the conversation actually goes, plus bridges for moving between business and technical framing, and a "go deeper" menu organized by topic rather than by time. Read this once to internalize the beats; don't try to force the conversation into a fixed order.

---

## The one-sentence cold open

If asked "tell me about something you built" with zero other context, lead with this and stop talking:

*"I built an enterprise AI search system where the hardest part wasn't finding the right answer — it was that the same question needed a different correct answer depending on who was asking, and I wanted to prove that boundary never breaks, not just hope it doesn't."*

Then wait. Let them ask the next question — that tells you which beat to go to next.

---

## Core story beats (deploy independently, any order)

Each beat is written to stand alone — you can lead with any of them depending on what the director seems to care about.

### Beat A — The business problem (relatability)
*"Think about a support platform where a Tier-1 agent, an account manager, an engineer, and an outside contractor all use the same AI assistant — but each one is allowed to see a different slice of the same customer's data. The AI has to give the account manager the contract terms without the engineering root cause, give the engineer the root cause without the contract terms, and give the contractor nothing at all. Same question, three different correct answers, and one wrong answer that's a data leak."*

**Bridge to technical:** *"That's an access-control problem before it's an AI problem — so that's where I actually spent most of my design effort."*

### Beat B — The two-layer defense (the core technical idea, business-first)
*"I built it with two checkpoints. A fast one at the door that gets you into the right neighborhood of documents. And a slower, careful one right before you're actually handed anything — because your permissions might have changed in the gap between those two moments. Most systems only build the first one and hope nothing changes in between. I assumed it would, and built for that."*

**If they ask "why does that matter / what changes":** access grants get revoked, embargoes expire, people change teams — the fast filter is built from a snapshot, and snapshots go stale.

**Bridge to technical:** *"In system terms, that's a pre-filter compiled into the vector search, and a live, attribute-based re-check right before generation."*

### Beat C — The trust story: bugs my own testing caught
*"I actually want to tell you about three mistakes, because I think that's more informative than a story where nothing went wrong. My system once accused itself of leaking a document to someone who was actually allowed to see it — I'd mislabeled my own test data. I found a security rule that no test was actually exercising because a stricter rule kept masking it. And I found one check that passed or failed almost at random because I'd let the AI's own judgment decide something security-critical — I pulled that apart so the security decision is always a hard rule, never a model's mood."*

**Why this beat works well in open conversation:** it naturally invites follow-up questions ("how did you catch that," "what did you change") — good, that's the conversation doing your work for you.

### Beat D — The platform-reality insight (your strongest MongoDB bridge)
*"I rebuilt the same system on a second platform, and found something I think generalizes beyond that platform: a search index built from your data doesn't automatically inherit your data's governance rules. It's a copy. If someone's access gets revoked in the source system, that doesn't automatically reach the index sitting downstream of it — you have to check again, live, at query time."*

**Bridge to MongoDB directly, if the moment allows:** *"That's true of any architecture where a vector index sits next to, but separate from, operational data — which is exactly the shape of the problem for anyone building AI features on top of Atlas."* (Say this only if it feels natural — don't force it if the conversation hasn't opened that door.)

### Beat E — Honest limitations (deploy proactively, don't wait to be asked)
*"I'll flag the honest caveat myself: my test set is 22 documents. At that size, almost every retrieval strategy scores well, so the differences between them are mostly noise — I wouldn't claim my benchmark proves anything about which strategy wins at real scale. What it does prove, independent of scale, is the zero-leak guarantee and the testing discipline behind it."*

---

## Bridges — moving between business and technical mid-sentence

Use these when you feel yourself about to drop a term without translating it:

- *"...which, in plain terms, means..."*
- *"...think of it like [analogy] — technically that's called [term], but the idea is..."*
- *"I can go as deep as you'd like on the how — where should I take this?"* (a direct, confident way to hand control of the depth-dial to the director)
- *"The business reason I did that is X; the engineering reason is Y."* (splitting the same decision into both framings explicitly)

---

## The "go deeper" menu — organized by what they might ask about

Rather than a timeline, here's a topic map. If the conversation turns toward any of these, here's the deeper material ready to go.

### If they ask about **architecture / how it's built**
- 8-node orchestration pipeline: classify → resolve permissions → retrieve (constrained) → re-verify (live) → generate → log.
- 7-rule deny-by-default policy: company, clearance, region, timing/embargo, need-to-know, external-contractor flag, default deny. Deny always overrides allow.
- Physical per-tenant data isolation (separate storage per customer) as a second, independent line of defense beneath the permission logic — so a bug in the logic still can't cross a tenant boundary.

### If they ask about **why you chose your retrieval approach**
- Benchmarked six strategies (keyword, similarity, hybrid, and a decomposition+reranking approach) against the same test set instead of picking one on instinct.
- The honest result at this scale: most strategies tie; the fancier approach is the most expensive and slowest by design — dense retrieval would be the right production choice for a corpus this small, and you say that plainly rather than defending the more impressive-sounding option.

### If they ask about **testing philosophy / how you validate AI systems**
- Security correctness is decided by hard rules only, never by the AI's own judgment — that's a deliberate separation, since a security decision can't be probabilistic.
- The eval harness gates releases: a build that produces even one leak does not ship.
- A standalone check keeps the security documentation in sync with the running policy code, so what a customer's security team was told can't silently drift from what's actually deployed.

### If they ask about **deployment / running this for a real customer**
- The platform-portability lesson from Beat D: verify governance independently on each platform you deploy to, never assume it travels automatically from the source system.
- What would need to change for a real customer: a larger, tiered evaluation corpus (the 22-document caveat), and a revisited storage-isolation strategy as tenant count grows past what per-tenant collections handle cleanly.

### If they ask about **what you'd do differently / next steps**
- Instrument the scale caveat from day one instead of discovering it afterward.
- Design the storage/isolation approach for tenant-count growth up front, before it becomes a migration project.
- Re-run the retrieval-strategy benchmark at a realistic document count once one exists, since the current result is only trustworthy at the scale it was measured.

---

## Reading the room — quick cues

| Signal | What it means | What to do |
|---|---|---|
| Nodding, "mm-hm," staying quiet | They're tracking, want the story to keep moving | Continue at current depth, don't over-explain |
| "How exactly does that work?" | Green light to go one layer deeper | Move from the beat's plain-English framing into its technical layer |
| Redirecting to a different angle ("what about cost," "what about the customer side") | They want a different lens than the one you're on | Drop what you're doing, follow their thread — this is a conversation, not a script to protect |
| Silence after a technical sentence | You may have gone too deep too fast | Immediately re-anchor in plain English: "the short version is..." |
| Checking the time / wrapping-up language | Time to close | Go straight to a closing line (below), skip anything mid-menu |

---

## Closing lines (pick based on how the conversation actually ended)

**If it ended on the security/trust thread:**
*"That's really the throughline for me — an FDE's job is turning a technical guarantee into something a customer's security team can sign off on, and that's exactly the muscle this project built."*

**If it ended on the platform/deployment thread:**
*"That's the instinct I'd bring to any customer's stack — don't assume a guarantee travels between systems until you've verified it yourself, on their specific platform."*

**If it ended on limitations/what's next:**
*"I'd rather tell you exactly where the edges of what I've proven are than let you find them later — I think that's the more useful signal than a system that claims to have no edges at all."*

**Generic fallback, any ending:**
*"Happy to go deeper on any piece of this — the policy engine, the testing setup, or the platform work — whichever's most useful to you."*
