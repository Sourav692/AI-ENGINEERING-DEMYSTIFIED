> **Level** 🔴 Telling the Story · **Module** 11 · **stories/** · **Format:** 15–20 minute deep-dive
> **Source material:** `4. FDE_Related_Preparation/Star_Stories/Enterprise_RAG_DeepDive_15-20min.md` — kept as a worked example of the format described in [Deep-Dive and Conversational Formats](../01_Deep_Dive_And_Conversational_Formats.md). It is one engineer's own engagement narrative; use it as a template for the shape, not a script to repeat.

---

# Enterprise RAG (Meridian Assist) — 15–20 Minute Deep-Dive
### For: MongoDB Director conversation · Audience: senior, business + technical judgment · Goal: demonstrate FDE-grade translation between the two

> **How to use this document:** it's written as a speakable script with embedded coaching notes (in blockquotes, like this one). Read it aloud a few times, then work from the segment headers and bold cues rather than memorizing verbatim — memorized scripts sound memorized. The timing adds up to ~15 minutes of talking with room for the director to interject; the last 3–5 minutes of your 15–20 minute slot should be Q&A, not more script.

> **The one meta-rule for the whole thing:** every technical term gets translated in the *same breath* it's introduced, not three sentences later. "A two-layer access control system — think a fast ID check at the door, then a second, more careful check right before you're handed anything sensitive" is one sentence, not two ideas.

---

## Timing budget

| Segment | Time | Cumulative |
|---|---|---|
| 1. The Hook | 0:30 | 0:30 |
| 2. STAR Narrative | 4:00 | 4:30 |
| 3. Technical Development | 3:30 | 8:00 |
| 4. Governance & Security | 3:30 | 11:30 |
| 5. Deployment & Platform Reality | 2:00 | 13:30 |
| 6. Honest Limitations | 0:45 | 14:15 |
| 7. Close → FDE Role | 0:45 | 15:00 |
| Q&A buffer | 5:00 | 20:00 |

---

## 1. The Hook (0:30)

> **Coaching note:** zero jargon in this segment. This is the sentence the director remembers if they remember nothing else. Say it, then pause — let it land before moving on.

*"The hard part of enterprise AI search isn't finding the right document — it's that the same question has a different correct answer depending on who's asking. I'll give you a concrete example: 'Why did a customer lose data in March, and do they get service credits?' A Tier-1 support agent should get the operational backlog. An account manager should get the contract terms and credit tiers, but not the engineering root cause. An external contractor, or anyone outside that customer's account team, should get nothing at all — not a summary, not a hint that the incident happened. Getting that right, provably, for every single question, was the entire point of the project I want to walk you through."*

---

## 2. STAR Narrative (4:00)

### Situation — plain English (0:45)

*"I built this as a fully working reference system — not a slide deck — because I wanted to be able to defend real design decisions under questioning, not just describe intentions. The scenario: an enterprise support and account-management platform where support agents, account managers, engineers, and external contractors all ask the same AI assistant questions, but each role is only allowed to see a different slice of the underlying data. That access boundary isn't a nice-to-have — it's the difference between a helpful product and a data-leak lawsuit."*

### Task — what I personally owned (0:30)

*"I owned this end to end, solo. My personal bar for 'done' wasn't 'the demo looks good' — it was 'I can prove, with a test that fails the build if it's wrong, that this system never shows someone something they're not allowed to see.' That's a meaningfully higher bar than 'the AI usually refuses correctly,' and the whole design follows from taking that bar seriously."*

### Action — Pass 1: plain English (1:15)

> **Coaching note:** this is the analogy pass. No architecture terms yet — that's Pass 2. If the director's body language says "I get it, keep going," you can compress or skip straight to Pass 2's headline sentence.

*"I designed the system so permission-checking happens before the AI ever sees a document — not as a rule a developer has to remember to follow, but built into the shape of the pipeline so it's structurally impossible to skip. Think of it like a venue with two checkpoints: a quick ID check at the door that gets you into the building at all, and then a second, more careful check right before you're handed something sensitive — because your access might have changed between when you walked in and when you asked for the sensitive thing. I also physically separated every customer's data into its own storage area, so even a bug in the permission logic can't leak one customer's information into another customer's answer. And the permission rules themselves default to 'no' — if nothing explicitly says you're allowed to see something, you don't see it, full stop."*

### Action — Pass 2: the technical layer (1:00)

> **Coaching note:** deliver this only if you sense engagement — a nod, a question, leaning in. If the room feels like "got it, what's the result," skip to Result.

*"In system terms: that's attribute-based access control, enforced in two layers. Layer one is a fast pre-filter compiled directly into the vector search query — it narrows retrieval to only documents the requester could plausibly see, based on attributes like company, clearance level, and region. Layer two is a slower, authoritative re-check immediately before the answer is generated, using the requester's live, up-to-the-second permissions — because the pre-filter can go stale between index-build time and question time: a revoked access grant, an expired embargo, a group membership change. If that second check ever catches something the first one should have caught, that's logged as a security event, not silently corrected — because it means the fast filter has drifted, and I want to know that."*

### Result — business framing first, numbers second (0:30)

*"The headline result: zero data leaks, and that's not a metric I reported after the fact — it's a hard gate my own test suite enforces before anything ships. Underneath that: 22 out of 22 on a golden test set, 68 automated tests passing, and a system that's honest about exactly where its guarantees are strong and where they'd need more validation at real scale — which I'll come back to."*

---

## 3. Technical Development (3:30)

> **Coaching note:** this is the "if they want more" branch. Lead with the one-sentence business framing for each sub-point, then go deeper only as far as the conversation wants.

**The policy engine (1:00)**
*"Business framing: the rules for 'who can see what' are written as seven plain checks — which company you belong to, your clearance level, your region, timing windows like embargoes, whether you specifically need to know this topic, whether you're an external contractor, and a default-deny if none of the above explicitly grants access. Technical layer: it's a deny-overrides policy chain — any single rule saying 'no' wins, regardless of how many rules say 'yes.' That asymmetry is deliberate: in security, one true negative should always beat any number of positives."*

**Retrieval strategy — evidence over instinct (1:00)**
*"I tried six different ways of searching the documents — from simple keyword matching up to a more elaborate approach that breaks a complex question into sub-questions and re-ranks the results — and benchmarked all six against the same test set, rather than picking one on instinct. That matters less for the specific numbers and more for the habit it demonstrates: measure before you commit to an architecture, and be willing to have the data tell you the fancier approach isn't always the right one for your actual scale."*

**The pipeline shape (1:00)**
*"Technical layer, for completeness: it's an 8-node orchestration graph — classify the request, resolve what the requester is allowed to see, retrieve under that constraint, re-verify permissions on fresh data, generate the answer, and log the whole trace for auditability. Each node has one job. That's a deliberate echo of the access-control philosophy — narrow, single-purpose components are easier to test and reason about than one component trying to do everything."*

---

## 4. Governance & Security (3:30)

> **Coaching note:** weight this the heaviest for a Director audience. This is where "I built a cool RAG system" becomes "I understand what enterprise trust actually requires."

**The release gate (1:00)**
*"The zero-leak number isn't something I measured and reported — it's a gate. If a build produces even one leak on the golden test set, it does not ship. That's the difference between a quality metric and a security control: a quality metric tells you something after the fact; a security control stops the bad outcome from reaching anyone."*

**The trust story — three bugs my own testing caught (1:30)**
*"I want to tell you about three mistakes I made, because I think how you respond to your own testing catching you is more informative than a system that never had a wrinkle. First: my system once flagged itself for 'leaking' a document to an account manager — but she was actually allowed to read it. I'd mislabeled 'not relevant to this question' as 'not allowed to see it' in my own test data. I fixed the data and added a check that keeps those two ideas from ever being conflated again, because a false security alarm is worse than no alarm — people learn to ignore alarms that cry wolf. Second: I found a permission rule that no test case was actually exercising — an earlier, stricter rule kept firing first and masking it — so I built a specific test scenario whose *only* path to being blocked was that exact rule, to confirm it actually worked on its own. Third: one test passed or failed almost at random, because I'd let the AI's own judgment decide part of a security pass/fail. I separated 'did we leak data' — decided by hard rules, never by the AI — from 'did we phrase the refusal politely,' which can reasonably be a judgment call. Security can never come down to a coin flip."*

**Documentation that can't drift (1:00)**
*"One more piece I think matters for an enterprise buyer specifically: I wrote a standalone check that verifies the security documentation matches the running policy code — so the two can never silently drift apart. If someone changes a permission rule and forgets to update the doc a customer's security team was shown, that check fails the build. Documentation that can lie to a customer is worse than no documentation."*

---

## 5. Deployment & Platform Reality (2:00)

> **Coaching note:** this is your strongest bridge to MongoDB specifically. Say the connection out loud — don't make the director draw it themselves.

*"I rebuilt the same system a second time on a different platform, Databricks, and that's where I found something I think is the most important insight in the whole project: their vector search index doesn't automatically inherit the source system's governance rules. It's a derived copy of the data, so a permission change in the source of truth doesn't travel with it automatically — you have to re-verify. I designed the same two-layer defense there for that exact reason: fast filter for speed, authoritative live check before the answer goes out, because you can't assume governance travels for free between a system of record and a derived index built on top of it.*

*I'm flagging this specifically because it's not a Databricks-only problem — it's true of any architecture where a vector index sits next to, but separate from, your operational data. That's the exact shape of an FDE's job: not just building the AI feature, but knowing which platform guarantees actually hold and which ones you have to verify yourself, for whatever stack a specific customer is running."*

---

## 6. Honest Limitations (0:45)

> **Coaching note:** say this before they ask. Offered honesty reads as confidence; extracted honesty reads as getting caught.

*"One caveat I want to be upfront about: my test corpus is 22 documents. At that size, retrieval is easy, and most of the six strategies I benchmarked score near-perfectly — the differences between them are mostly noise, not proof that the fancier strategy earns its cost. What the harness proves, regardless of corpus size, is the zero-leak number and the testing discipline behind it. At a real enterprise scale — hundreds of thousands of documents — I'd expect the retrieval-strategy comparison to become meaningfully differentiated, and that's exactly where I'd want production data before making a final call."*

---

## 7. Close — Tying Back to the FDE Role (0:45)

*"The reason I wanted to walk you through this specific project rather than a purely conversational one: an FDE's job is exactly this translation — taking a technical guarantee, like 'this system cannot leak data across an access boundary,' and turning it into a business guarantee a customer's security and compliance team can actually sign off on. That's not a skill I'm claiming abstractly — it's the muscle I built, concretely, shipping this system and then explaining it the way I just did to you."*

---

## Appendix A — Anticipated Follow-Ups (crib sheet)

| If asked... | Lead with (business) | Then, if pushed (technical) |
|---|---|---|
| "Why two layers instead of one good filter?" | "Because permissions change after the index is built — a revoked access grant shouldn't have to wait for a reindex to take effect." | Pre-filter is compiled into the vector search on index-time attributes; post-check re-evaluates live attributes right before generation, converting staleness into a logged event instead of a leak. |
| "How do you know your test suite isn't just testing itself?" | "Because it already caught me — three separate times, on real mistakes, not hypothetical ones." | Walk through the false-alarm bug, the shadowed-rule bug, and the flaky-gate bug as concrete evidence the harness disagrees with itself/reality when something's actually wrong. |
| "What breaks first at real scale — hundreds of thousands of documents?" | "The retrieval-strategy choice starts to actually matter, and one part of the storage design needs revisiting." | Name it directly: strategy differentiation reappears at scale (worth re-benchmarking), and the per-tenant-collection storage approach needs a scaling plan as tenant count grows. |
| "Why does the second platform need its own enforcement layer if the source system already governs the data?" | "Because a search index is a copy, not the original — permission changes don't travel with a copy automatically." | The index is a derived artifact of the governed table; the platform's native row-level security applies to the table, not automatically to embeddings extracted from it. |
| "What would you do differently if you rebuilt this today?" | "Instrument the corpus-size caveat from day one instead of discovering it after — and design the storage layer for tenant-count scale up front." | Larger, tiered eval corpus from the start; revisit per-tenant isolation strategy before it becomes a migration project. |

## Appendix B — Delivery Notes

- **Pause after the hook.** Don't rush into Situation. Let the one-liner land.
- **Watch for the "go deeper" signal** before launching into Segment 3 or the technical half of any Action beat — a raised eyebrow, "how exactly," leaning forward. If you don't get one, a business-level summary of Segment 3 in two sentences is enough; save the detail for Q&A.
- **Never apologize for the limitations section.** State it flatly, like a fact you're proud to know, not a confession.
- **If time runs short**, the segments to compress first are 3 (Technical Development) and the Pass-2 technical half of Segment 2's Action — the business framing and the governance/security section are the parts a Director will remember and should never be rushed.
