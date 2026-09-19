# The RAG Governance Layer at AIA Group — 15–20 Minute Deep-Dive
### For: MongoDB Director conversation · Frames the Enterprise RAG / ABAC governance work as the access-control layer inside AIA's real Multi-Tool agent · Goal: demonstrate FDE-grade discovery + translation

> **How to use this document:** same speakable-script format as the standalone version — read the segment headers and bold cues, don't memorize verbatim. New in this version: a dedicated **Requirements Gathering & Scoping** segment, since that's the part of the FDE job a purely technical narrative skips.

> **The one meta-rule for the whole thing:** every technical term gets translated in the *same breath* it's introduced. And every AIA-specific technical detail below is expressed in AIA's real stack (Unity Catalog, Databricks Vector Search, MLflow) — not the generic version — so it stays consistent if a director cross-references anything else you've said about AIA.

> **One honesty note to hold internally, not necessarily to say aloud:** the depth of this specific sub-component (document-governance inside the Multi-Tool agent) is a plausible, well-reasoned extension of the real AIA engagement — own it as "here's the layer I'd go deep on if asked," not as something already sitting verbatim in the headline story.

---

## Timing budget

| Segment | Time | Cumulative |
|---|---|---|
| 1. The Hook | 0:30 | 0:30 |
| 2. AIA's Problem Statement | 1:00 | 1:30 |
| 3. Requirements Gathering & Scoping | 3:00 | 4:30 |
| 4. STAR Narrative | 3:30 | 8:00 |
| 5. Technical Development | 2:30 | 10:30 |
| 6. Governance & Security | 3:00 | 13:30 |
| 7. Deployment & Platform Reality | 1:30 | 15:00 |
| 8. Honest Limitations | 0:45 | 15:45 |
| 9. Close → FDE Role | 0:45 | 16:30 |
| Q&A buffer | 3:30 | 20:00 |

---

## 1. The Hook (0:30)

> **Coaching note:** zero jargon. Say it, then pause.

*"At AIA, one of the agents in the multi-agent system I built answered questions by combining generated SQL with retrieval over policy and claims documents. The hardest part of that piece wasn't the AI — it was that an actuary, a claims manager, and an external auditor asking the exact same question, in different markets, needed three different correct answers. I want to walk you through how I scoped that requirement before writing any code, and how I made the boundary provably safe rather than just prompted to be safe."*

---

## 2. AIA's Problem Statement (1:00)

*"Quick reminder of the headline AIA story: actuaries, claims managers, and analysts needed self-serve natural-language answers over governed data, and the old path was a 2-to-10-day BI queue. The Multi-Tool agent I built handled the retrieval half of that — policy wordings, claims files, underwriting notes.*

*That's exactly where access got hard. AIA operates across multiple markets, each with its own regulator and data-residency obligations. Policy and claims documents routinely carry health disclosures and other sensitive personal data. And internally, an actuary doing portfolio-level pricing has a completely different, much narrower legitimate need to see a specific customer's claim than the claims manager actually handling that claim. So the real requirement wasn't 'let people ask questions about documents' — it was 'let people ask, and make it structurally impossible for the answer to cross a role, market, or regulatory boundary it shouldn't.'"*

---

## 3. Requirements Gathering & Scoping (3:00)

> **Coaching note:** this is the segment a purely technical candidate hasn't prepared. Slow down here — it's doing the most differentiation work in the whole script.

**Stakeholder discovery, not a spec handed to me (0:45)**
*"I didn't start from a written spec. I sat with actual users first — a sample of actuaries, claims managers, and analysts — and asked what they actually needed to see, not what they assumed the system should restrict. Users describe their own job well; they're bad at predicting edge cases in an access policy. Those edge cases came from a separate conversation."*

**A dedicated session with compliance, legal, and security (0:45)**
*"Separately, I sat with AIA's compliance and security stakeholders specifically to map two things: which document types carried which sensitivity classification — policy wording versus a claims file versus underwriting medical notes aren't equally sensitive — and which regulatory constraints were non-negotiable per market: data residency, consent requirements around health information, internal segregation between functions like underwriting and claims. That became my 'must never happen' list before I designed anything."*

**Turning that into an access matrix, and scoping the MVP narrow (0:45)**
*"I ran that out as a role-by-document-type-by-market matrix, and that matrix — not a technical guess — became the policy engine's actual rule set. And I deliberately scoped the first version to two business units, one market, rather than the whole document estate, specifically so I could prove the governance model was airtight on a bounded problem before expanding it. Boiling the ocean on access control is how you ship something that looks done and isn't."*

**Agreeing the success bar up front, then a feasibility spike (0:45)**
*"Before building, I agreed the bar explicitly with the business sponsor and compliance: zero cross-boundary leaks, full explainability, a defined latency target. That's what let 'zero leaks' later become an actual release gate instead of a number I generated after the fact and then defended. Only after that did I run a short technical spike — two retrieval approaches against a handful of de-identified real documents — to confirm viability on AIA's existing Databricks environment before committing real build time."*

---

## 4. STAR Narrative (3:30)

### Situation (0:30)
*"Within the larger multi-agent build, the Multi-Tool agent's document-retrieval piece was the one place a wrong answer meant a compliance incident, not just an unhelpful one — and the discovery work above confirmed that wasn't hypothetical: the role/market/sensitivity matrix alone had dozens of legitimate, simultaneous access patterns to get right."*

### Task (0:20)
*"I owned making that governance boundary a tested, provable property of the system — not something resting on the model refusing nicely when asked about a document it shouldn't return."*

### Action — plain English first (1:20)
*"I built it so permission-checking happens before retrieval ever runs — not a rule someone has to remember, but wired into the pipeline so it's structurally impossible to skip. Think of two checkpoints: a fast one that narrows the search to the right neighborhood of documents for that person's role and market, and a slower, careful one right before the answer is generated, checked against their access as it stands right now — because a case reassignment, a revoked grant, or a consent window closing can happen after the first check ran. The rules default to 'no': if nothing explicitly grants access, you don't see it."*

### Action — the technical layer (0:40)
> **Coaching note:** deliver only on a "how exactly" signal; otherwise skip straight to Result.

*"Technically: the fast layer is a metadata filter compiled directly into the Databricks Vector Search query — business unit, market, document sensitivity tier, case assignment, all governed as Unity Catalog columns. The slow layer re-checks the requester's live Unity Catalog grants immediately before the agent returns an answer. The policy is seven deny-by-default rules, with any single 'deny' overriding every 'allow.'"*

### Result (0:20)
*"Zero cross-boundary leaks on the governed golden test set, enforced as a release gate — not reported after the fact — with full traceability so every answer shows its source document."*

---

## 5. Technical Development (2:30)

**Retrieval strategy, chosen on evidence (1:00)**
*"I benchmarked several retrieval approaches — plain similarity search up through decomposition-and-reranking — against the same governed test set instead of assuming the fancier one was automatically right. At this scoped MVP's document volume, the simpler approach was the correct production choice; the elaborate one cost more and didn't earn its keep yet. I'd expect that to flip once the document estate scales past the MVP boundary — which is exactly why the scoping mattered."*

**Pipeline shape (1:00)**
*"Within the Multi-Tool agent: classify the request → resolve the requester's governed attributes → retrieve under that constraint → re-verify live permissions → generate the grounded answer → log the full trace via MLflow for auditability. One job per step — the same design instinct as the Supervisor pattern in the rest of the AIA system."*

---

## 6. Governance & Security (3:00)

> **Coaching note:** weight this heaviest — this is where "I built a RAG feature" becomes "I understand enterprise trust."

**The release gate (0:40)**
*"Zero leaks is a gate compliance and I agreed to before the build started — a build that produces even one cross-boundary leak on the governed test set does not ship."*

**The trust story — three real mistakes my testing caught (1:40)**
*"The harness once flagged a false leak — it thought a claims manager had been shown a case outside their assignment, but they'd actually just been reassigned that case; my test data was stale, not the system. I fixed the data and added a check that keeps a stale expectation from ever masquerading as a real leak again — a false alarm erodes trust in the gate faster than a missed one. Separately, I found one rule — the market-residency rule — that no test case was actually exercising, because a stricter rule kept firing first and masking it; I built a dedicated test whose only path to failing was that exact rule. And I kept the model's own judgment completely out of the leak/no-leak decision — that's hard rules only, never the AI, because a security decision can't be probabilistic."*

**Docs that can't drift from code (0:40)**
*"I also built a standalone check that verifies the security documentation compliance signed off on still matches the running policy code — so a rule change can never silently drift from what a regulator or internal audit was told the system does."*

---

## 7. Deployment & Platform Reality (1:30)

*"A discovery specific to building this inside AIA's real Databricks environment: a Vector Search index is a derived copy of your governed data — it doesn't automatically inherit Unity Catalog's row-level rules just because the source table is governed. If access is revoked in Unity Catalog, that doesn't propagate to the vector index on its own. That's exactly why the two-layer design isn't a defensive-programming flourish — it's the direct fix for a real platform gap found while building this at AIA specifically. Anyone building governed RAG on any platform where the index is a derived artifact needs to verify this independently rather than assume it — which is, I'd argue, the actual job of a Forward Deployed Engineer: know exactly which platform guarantees hold, and which you have to re-check yourself, for this specific customer's stack."*

---

## 8. Honest Limitations (0:45)

*"The scoped MVP covers two business units and one market by design — I haven't proven this at AIA's full document estate or full market footprint yet, and I'd expect the retrieval-strategy choice specifically to need re-evaluating at that scale. What I can stand behind regardless of scale is the zero-leak gate and the discovery process behind the policy rules, because that process doesn't get invalidated by growing the dataset."*

---

## 9. Close — Tying Back to the FDE Role (0:45)

*"I wanted to walk through the discovery and scoping as carefully as the build itself, because that's the part of this job that doesn't show up in a demo: sitting with actuaries, claims managers, and compliance before writing code, translating what I heard into an access matrix, agreeing the success bar with a business sponsor up front, and only then building — and testing — to that bar. That sequence is the actual FDE job. The system working is the proof; the discovery process is what made the right system get built in the first place."*

---

## Appendix A — Anticipated Follow-Ups (crib sheet)

| If asked... | Lead with (business) | Then, if pushed (technical) |
|---|---|---|
| "Did AIA hand you a spec, or did you gather this yourself?" | "Neither, really — I went and sat with the actual users and with compliance separately, because they'd tell me different, complementary things." | Stakeholder interviews for real usage patterns; a dedicated compliance/security/legal session for regulatory non-negotiables; synthesized into a role × document-type × market access matrix. |
| "Why scope to two business units and one market first?" | "So I could prove the governance model was airtight on a bounded problem before expanding it." | Access-control mistakes compound fast if you scale before validating the model; the MVP boundary was a deliberate scoping decision, not a resource constraint. |
| "Who signed off on 'zero leaks' as the bar, and when?" | "The business sponsor and compliance, before the build started." | It was a pre-agreed release gate baked into the plan, not a number generated afterward and then defended. |
| "Why does the index need its own governance check if Unity Catalog already governs the source table?" | "Because a search index is a copy, not the original." | A Vector Search index is a derived artifact; permission changes in Unity Catalog don't automatically propagate to an already-built index — you have to re-verify live, at query time. |
| "What would you scope differently starting over?" | "Bring compliance in even earlier." | Fold the sensitivity-classification and usage-pattern discovery into the same initial round of conversations instead of two separate passes. |

## Appendix B — Delivery Notes

- **Pause after the hook** and again after Section 3 (Requirements & Scoping) — that section is doing the heaviest lifting and deserves room to land.
- **Watch for the "how exactly" signal** before the technical half of Section 4's Action, or Section 5 — otherwise a two-sentence business summary is enough.
- **Never apologize for the limitations section.** State it flatly, like a fact you're proud to know.
- **If time runs short**, compress Section 5 (Technical Development) first — Sections 3, 6, and 7 are what a director will remember and shouldn't be rushed.
- Keep every AIA-specific detail (markets, roles, regulators) consistent with anything already said about AIA earlier in the conversation.
