# G05 — Sales Copilot: Deep Dive

Use the [Main guide](G05_Sales_Copilot_Main.md) for the spoken answer. This is the technical backup; the unchanged [source case](G05_Sales_Copilot.md) keeps the full synthesis, interview script, and references.

**Model and agent roles:** Deterministic routes handle common snapshots, CRM counts, and exact lookups; a bounded agent path handles ambiguous multi-step asks. The LLM copilot summarizes and drafts from authorized evidence, while the claim verifier and approval gateway control external claims and CRM writes.

## 1. Source and permission map

| Source | Authority and freshness | Permission detail and failure |
|---|---|---|
| Salesforce/HubSpot CRM | Accounts, opportunities, contacts, activities; minutes via change events and reconciliation | Owner, role hierarchy, territory, sharing rules, field-level security. Wrong scope leaks peer pipeline or stale stage. |
| Gong/Zoom calls | Participant statements; hours after a call | Participant/manager access and regional recording consent; PII and injection in transcripts. |
| Email/calendar | Threads, invites; near real time | Mailbox owner or explicit delegation; never read another rep’s mailbox. |
| Product docs | Approved feature descriptions; updated by product marketing | Some partner-only; superseded features and roadmap claims are dangerous. |
| Pricing/discount policy | Deal-desk rules, versioned | Regional variants and thresholds; no out-of-policy promise. |
| Support history | Account tickets/escalations | Account/tenant scope; severity can be mis-summarized. |
| Warehouse | Usage, ROI pilots, renewals; often daily | Row-level account/role scope; internal ROI is not an approved external claim. |

Each record needs stable ID, owner, updated time, and ACL metadata; exclude unmapped sources. User feedback is not ground truth until SME approval. The source notes that its detailed CRM permission model and structured router are additions to the pack based on cross-cutting references, not claims made by the purchased worksheet alone.

## 2. Identity and CRM sharing mirror

Validate the customer IdP token’s signature, audience, and expiry, then map customer groups into local roles. Alert on group-mapping drift; provision a new user only to their own tenant with minimal rights. The CRM mirror carries `owner_id`, `territory_ids`, role visibility, sharing rules, and field masks for sensitive amount/stage data. Compile tenant, territory, and role into the retrieval pre-filter. Recheck live attributes and field masks after retrieval and before generation or serving a snapshot. A count or aggregate containing forbidden rows violates the same zero-leak gate as a document excerpt.

Connector credentials are vault references, resolved at use time, never written into model prompts or traces. Scope each connection to one customer and use per-tenant encryption boundaries where required. Embeddings and snapshots are derived state, not authorization authority.

## 3. Snapshot as a materialized view

Calendar trigger or on-demand job builds summary, open opportunities/stage/next step, recent calls and emails, support escalations, segment objections, and approved claims. Run the job **as the rep**, key cache on account plus permission signature, and stamp source/index/policy versions. A manager and rep on the same account may get different snapshots. On role or territory change, invalidate affected snapshots. At serve time, reauthorize with current attributes; if the CRM is down, show a permitted last snapshot with staleness labeling or refuse. Precompute improves p95 but cannot preserve access after revocation by itself.

At 10× accounts, shard jobs by territory and make connector schedules independent so one rate-limited source does not block others. Interactive load should scale with snapshot hit rate rather than live CRM fan-out.

## 4. Structured versus semantic routing

| Question | Route |
|---|---|
| “Summarize the last three calls” | Semantic/hybrid retrieval on authorized transcripts. |
| “How many open opportunities missed close date?” | Fixed structured CRM query over authorized rows. |
| “Status of opportunity ID 0065g00000?” | Direct exact-ID lookup. |
| “Objections across late-stage deals this quarter?” | Structured filter first, then summarize matching prose. |

Use reviewed operations such as get account by ID, opportunities by stage, interactions since a date. Free-form natural-language query generation can invent fields or scan too broadly. Opportunity risk logic uses fetched stage age, moved close date, competitor mention, unanswered emails, open escalations, and playbook objections; each risk carries a source. Missing fields or stale transcripts become explicit gaps.

## 5. Claim and write boundaries

`Playbook.approved_claims` is the source for outbound claims. Pricing uses the current deal-desk policy. The claim verifier blocks an external draft if a claim has no approved entry or correct citation; “warn” is insufficient for pending certifications, internal ROI, or unapproved customer references. Discovery questions and personalization may use the rep’s account interactions and approved playbook, never model stereotypes.

`Draft.approval_status` controls write-back. A CRM update proposal lists exact field changes, receives a policy check and preview, then a human approves an idempotent tool-gateway call. Audit the approval and receipt. Mail sending, closing an opportunity, and changing amount/stage are above the day-one threshold. A later clean pilot may justify auto-approval for a low-risk field such as `last_contacted`; the first release does not assume that permission.

## 6. Failure decisions

| Failure | Decision |
|---|---|
| CRM unavailable | Labeled authorized snapshot if within allowed staleness; no writes. |
| Policy engine, ACL mapping, or approval down | Fail closed. |
| Missing evidence or stale source | List what was not checked; abstain or escalate. |
| Unapproved claim or price | Block external draft, not merely warn. |
| Transcript/email injection | Content is evidence, never tool or policy instruction. |
| Vector path unavailable | Use authorized keyword/structured path where supported and label limitation. |
| Model route down | Queue draft/long work with progress, or use approved fallback. |

Trace source IDs, retrieval/policy versions, field masks, citations, model/prompt versions, claim verdict, approval, and write receipt. Control-plane settings include connector registry, ACL mirror, approved claims, pricing policy, tool allowlist, evaluation suites, and budgets.

## 7. Evaluation and release

Use SME-approved historical account briefs and sparse-record cases, permission red-team questions from reps/managers across territories, exact citation audits, claim-level labels, and workflow replay. Example source thresholds: groundedness ≥90%, citations ≥95%, target task completion ≥80%, high-risk escalation ≥95%, zero permission violations, and zero critical failures on regulated-claim slices. Agree thresholds before release; treat the critical slices as separate gates.

Measure prep-time reduction, seller adoption, brief accuracy, citation coverage, meeting quality, conversion where attributable, p95, and cost/workflow. Online monitor unsupported-claim rate by model route, source, and claim category. User corrections enter evaluation after review; they are not direct training data.

Rollout: one CRM connector and territory matrix; historical golden set; offline no-write prototype; shadow mode; read-only pilot; draft-only workflow with approved write-back; expansion after safety and value hold. Keep model version pinning, canary, rollback, and source-owner sign-off.

## 8. Latency pivot

The source drill starts with 30–45 s account prep. The likely driver is serial tool calls and agent steps, not necessarily model inference. Trace the graph, then precompute the account snapshot, route common questions deterministically, parallelize independent read-only calls, cache permission-scoped state, cap steps/top-k/timeouts, and use the agent only for ambiguous next steps. Track agent step count, tool latency, snapshot hit rate, timeout rate, p95, and cost/workflow. A real-time in-call assistant is a distinct G16 problem with stronger precompute/stream/async split.

## 9. Model regression incident

On the source’s 2026-07-08 scenario, `llm_standard_v2` changed to `llm_premium_v3`. Persuasive drafts began claiming a pending SOC 2 renewal and a 34% support-cost reduction from an internal pilot. Online unsupported-claim rate reached **8.7% versus 1.2% baseline** (sample 430, 37 external-policy failures). The offline suite passed **96.7% of 120**, but its six regulated-claim cases passed only **83.3%** and omitted pending security, internal ROI, and customer-logo permission cases. The verifier had been weakened to warn-only.

**Detect:** compare online failures with offline slices and policy action. **Contain:** roll back model route, restore block mode, flag experiment drafts for review. **Root cause:** stronger extrapolation, weak critical-slice coverage, weakened policy gate. **Prevent:** claim-level labels, independent critical-slice release gates, negative examples that must refuse, online unsupported-claim monitoring, and no warn-only external-claim route. The failure is in evaluation and release control, not just prose style.

## 10. Interview trade-offs

| Choice | Reason | Revisit if |
|---|---|
| Precompute snapshot, reauthorize at serve | Removes source fan-out from hot path without freezing permissions. | Most meetings unscheduled; build a fast partial snapshot on open. |
| Fixed CRM operations | Bounds fields, rows, and authorization. | Validated open-ended query layer is genuinely needed. |
| Block unapproved external claims | Legal/commercial risk exceeds draft convenience. | Internal-only notes may use warnings; external drafts still block. |
| Preview and approve writes | Changes are consequential and auditable. | Proven low-risk field update earns a narrower automated route. |

The [source](G05_Sales_Copilot.md) retains the original sixty-minute script, detailed source attribution, and trace excerpt.
