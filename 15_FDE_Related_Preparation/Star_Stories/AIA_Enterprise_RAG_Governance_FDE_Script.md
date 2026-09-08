# The RAG Governance Layer at AIA Group — Full FDE Script
### Discovery → Requirements & Scoping → STAR → Technical Build → Governance & Security → Deployment
### This is the "master" script: pull segments into either the 15–20 min deep-dive format or the open-ended conversational format, depending on the room.

> **What changed from the standalone version:** the earlier "Meridian Assist" write-up was a generalized solo build. This version places the exact same governance engineering **inside the real AIA Group engagement** — as the piece of that multi-agent system that made governed, natural-language answers over policy documents actually safe to ship. Every technical detail below is re-expressed in AIA's real stack (Unity Catalog, Databricks Vector Search, Genie, MLflow) rather than the generic Chroma/OpenAI version, so it's consistent with the rest of the AIA story if a director cross-references them.

---

## 0. One-sentence anchor (use this to open, in any format)

*"At AIA, the multi-agent system I built had a component that answered natural-language questions over policy and claims documents — and the hardest part of that one component wasn't the AI, it was that an actuary, a claims manager, and an external auditor asking the exact same question, across different markets, needed three different correct answers. I want to walk you through how I scoped that requirement before writing any code, and how I made the boundary provably safe rather than just prompted-to-be-safe."*

---

## 1. AIA's Actual Problem Statement (business framing, zoomed to this piece)

*"You'll remember the headline AIA story: business users — actuaries, claims managers, analysts — needed self-serve natural-language answers over governed data, and the old path was a 2-to-10-day BI queue. One of the four specialist agents in the system I built, the Multi-Tool agent, answered questions by combining generated SQL with retrieval over policy documents — things like policy wordings, claims files, underwriting notes.*

*That's exactly where the access problem got hard. AIA operates across multiple markets — Hong Kong, and others across the region — each with its own regulator and its own data-residency obligations. Policy and claims documents routinely contain health disclosures and other sensitive personal data. And internally, an actuary doing portfolio-level pricing work has a completely different, and much narrower, legitimate need to see a specific customer's claim file than the claims manager actually handling that claim does. So the real requirement wasn't 'let people ask questions about documents' — it was 'let people ask questions about documents, and make it structurally impossible for the answer to cross a role, market, or regulatory boundary it shouldn't.'"*

---

## 2. Requirements Gathering & Scoping — before a line of code (this is the new, critical section)

> **Why this section matters for an FDE conversation:** a Director isn't just judging whether you can build something — they're judging whether you know how to *find out what to build* at a real enterprise client, where the real requirement is rarely stated cleanly by anyone in the room. This section is where you prove that instinct.

**2.1 — Stakeholder discovery, not a requirements doc handed to me**
*"I didn't start from a spec. I sat with the actual users first — a sample of actuaries, claims managers, and business analysts — and asked what they actually needed to see, not what they assumed the system should restrict. That distinction matters: users are good at describing their own job, and bad at predicting edge cases in an access policy. The edge cases came from a separate conversation."*

**2.2 — A dedicated session with compliance, legal, and IT security**
*"Separately, I sat down with AIA's compliance and security stakeholders specifically to map two things: which document types carried which sensitivity classification (policy wording versus claims file versus underwriting medical notes are not equally sensitive), and which regulatory constraints were non-negotiable per market — data residency rules, consent requirements around health information, and internal segregation rules between functions like underwriting and claims. Those became my 'must never happen' list before I designed anything — they're the seeds of what later became a hard release gate, not a best-effort setting."*

**2.3 — Building the actual access matrix**
*"I ran this out as a role-by-document-type-by-market matrix: for each of the user roles, which document sensitivity tiers, in which markets, could they legitimately see — and under what conditions (e.g., only for cases assigned to them, only within a consent window, only within their own market unless explicitly cross-market authorized). That matrix is what later became the policy engine's actual rule set — I didn't invent the rules technically first and retrofit a justification; the rules came from this discovery process."*

**2.4 — Scoping the MVP boundary deliberately narrow**
*"I explicitly did not try to govern the entire document estate on day one. I scoped the first version to two business units and their claims and policy documents in a single market, specifically so I could prove the governance model was airtight on a bounded problem before expanding it. Boiling the ocean on access control is exactly how you ship something that looks done and isn't."*

**2.5 — Defining success criteria with the business sponsor up front, not after**
*"Before building, I agreed the success bar explicitly with the business sponsor and compliance: zero cross-boundary leaks, full explainability (every answer shows its source documents), and a defined latency target for the self-serve experience to actually replace the old queue. That agreement upfront is what let 'zero leaks' later become an actual release gate instead of an aspiration nobody had signed off on."*

**2.6 — A technical feasibility spike before committing the build**
*"Only after that discovery did I run a short technical spike — testing two retrieval approaches against a handful of real, de-identified documents — to confirm the approach was even viable on AIA's existing Databricks environment before committing real engineering time to the full build."*

**2.7 — Naming what was explicitly out of scope**
*"I also wrote down what this component would *not* do — no automated claims payout decisions, no underwriting recommendations, retrieval and grounded answers only — specifically so scope creep had something concrete to be checked against as the broader multi-agent system kept growing around it."*

---

## 3. STAR — the governance sub-project itself

### Situation
*"Within the larger multi-agent build, the Multi-Tool agent's RAG-over-policy-documents capability was the one place a wrong answer meant a compliance incident, not just an unhelpful one — and the discovery work above confirmed this wasn't a hypothetical: the role/market/sensitivity matrix alone had dozens of legitimate distinct access patterns to get right, simultaneously."*

### Task
*"I owned making that governance boundary a tested, provable property of the system — not something resting on the model refusing nicely when asked about a document it shouldn't return."*

### Action — plain English first
*"I built it so permission-checking happens before the retrieval step ever runs, not as a rule someone has to remember, but wired into the pipeline so it can't be skipped. Think of two checkpoints: a fast one that narrows the search to the right neighborhood of documents for that person's role and market, and a slower, careful one right before the answer is actually generated, checked against their access as it stands *right now* — because a case reassignment, a revoked grant, or a consent window closing can happen after the first check ran."*

### Action — the technical layer (Databricks-native)
*"Concretely: the fast layer is a metadata filter compiled directly into the Databricks Vector Search query — on attributes like business unit, market, document sensitivity tier, and case assignment, all governed as Unity Catalog columns. The slower, authoritative layer re-checks the requester's live Unity Catalog grants immediately before the Multi-Tool agent returns an answer. The policy itself is seven deny-by-default rules — business unit, market, clearance tier, timing/consent window, need-to-know case assignment, external/contractor flag, and a hard default-deny if nothing explicitly grants access — with any single 'deny' overriding every 'allow.'"*

### Result
*"Zero cross-boundary leaks on the governed golden test set — enforced as a release gate, not reported after the fact — with full traceability so every answer shows the source document and, implicitly, why that document was in-scope for that requester."*

---

## 4. Technical Development (on-demand depth)

**Retrieval strategy, chosen on evidence** — *"I benchmarked several retrieval approaches — plain similarity search up through a decomposition-and-reranking approach — against the same governed test set rather than assuming the more sophisticated one was automatically right. At AIA's document volume for this scoped MVP, the simpler approach was the correct production choice; the fancier one cost more and didn't earn its keep yet. That's a result I'd expect to flip once the document estate scales past the MVP boundary — which is exactly why the scoping in Section 2 mattered."*

**Pipeline shape** — *"Within the Multi-Tool agent: classify the request → resolve the requester's governed attributes → retrieve under that constraint → re-verify live permissions → generate the grounded answer → log the full trace via MLflow for auditability. Each step has one job, which is the same design instinct as the Supervisor pattern in the rest of the AIA system — specialize narrowly, don't let one component carry the whole burden."*

---

## 5. Governance & Security (weight this heaviest)

**The release gate** — *"The zero-leak number is a gate compliance and I agreed to before the build started, not a metric I generated afterward — a build that produces even one cross-boundary leak on the governed test set does not ship."*

**The trust story — testing catching real mistakes** — *"During development, the harness once flagged a false leak — it thought a claims manager had been shown a case outside their assignment, but they'd actually just been reassigned that case and my test data was stale, not the system. I fixed the test data and added a check that keeps 'stale test expectation' from ever masquerading as a real leak again, because a false alarm erodes trust in the gate faster than a missed one. Separately, I found one policy rule — the market-residency rule — that no test case was actually exercising, because a stricter rule kept firing first and masking it; I built a dedicated test whose only path to failing was that exact rule, to confirm it worked standalone. And I kept the model's own judgment completely out of the leak/no-leak decision — that's decided by hard rules only, never by the AI, because a security decision can't be probabilistic."*

**Docs that can't drift from code** — *"I also built a standalone check that verifies the security documentation compliance signed off on still matches the running policy code — so a rule change can never silently drift from what a regulator or an internal audit was told the system does."*

---

## 6. Deployment & the Platform-Reality Insight (native to AIA's stack)

*"Here's a discovery specific to building this on Databricks, inside AIA's real environment: a Vector Search index is a derived copy of your governed data — it does not automatically inherit Unity Catalog's row-level access rules just because the source table is governed. If someone's access is revoked in Unity Catalog, that doesn't propagate to the vector index on its own. That's precisely why the two-layer design in Section 3 isn't a defensive-programming flourish — it's the direct fix for a real platform gap I found while building this at AIA specifically. Anyone building governed RAG on any platform where the index is a derived artifact — not just Databricks — needs to verify this independently rather than assume it. That verification instinct is, I'd argue, the actual job of a Forward Deployed Engineer: know exactly which platform guarantees hold, and which ones you have to re-check yourself, for this specific customer's stack."*

---

## 7. Honest Limitations

*"The scoped MVP covers two business units and one market by design — I haven't proven this at AIA's full document estate or full market footprint yet, and I'd expect the retrieval-strategy choice specifically to need re-evaluating at that scale. What I can stand behind regardless of scale is the zero-leak gate and the discovery process behind the policy rules — because that process, unlike a specific retrieval benchmark, doesn't get invalidated by growing the dataset."*

---

## 8. Close — tying back to the FDE role

*"I wanted to walk through the discovery and scoping as carefully as the build itself, because that's the part of this job that doesn't show up in a demo: sitting with actuaries, claims managers, and compliance before writing code, translating what I heard into an access matrix, agreeing the success bar with a business sponsor up front, and only then building — and testing — to that bar. That sequence is the actual FDE job. The system working is the proof; the discovery process is what made the right system get built in the first place."*

---

## Appendix — Anticipated Follow-Ups

| If asked... | Answer |
|---|---|
| "How did you actually gather the access requirements — did AIA hand you a spec?" | No — direct stakeholder interviews with actuaries/claims managers for real usage patterns, a separate session with compliance/legal/security for regulatory non-negotiables, synthesized into a role × document-type × market access matrix. |
| "Why scope to two business units and one market first?" | To prove the governance model was airtight on a bounded, provable problem before expanding it — access-control mistakes compound fast if you scale before validating the model. |
| "Who signed off on 'zero leaks' as the bar, and when?" | The business sponsor and compliance, before the build started — it was a pre-agreed release gate, not a number generated after the fact and then defended. |
| "Why does the index need its own governance check if Unity Catalog already governs the source table?" | Because a Vector Search index is a derived copy of the data — permission changes in Unity Catalog don't automatically propagate to an already-built index; you have to re-verify live, at query time. |
| "What would you scope differently starting over?" | Bring in compliance even earlier — during the initial stakeholder discovery, not as a follow-up session — so the sensitivity classification and the usage-pattern discovery happen in the same conversation instead of two passes. |

---

## Delivery Notes

- Lead with Section 2 (Requirements & Scoping) whenever the room is evaluating FDE-specific judgment, not just engineering skill — it's the section a purely technical candidate is least likely to have prepared.
- If time is short, Sections 4 (Technical Development) can compress to one sentence per bullet — Sections 2, 5, and 6 are the ones that differentiate this from "I built a RAG demo."
- Keep the AIA-specific details (markets, roles, regulators) consistent with whatever you've already said about AIA elsewhere in the conversation — don't introduce a market or regulator name here that contradicts an earlier answer.
