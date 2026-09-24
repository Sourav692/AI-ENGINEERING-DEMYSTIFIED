# G05 — Sales Copilot: Cheat Sheet

Use the [Main guide](/modules/15-fde-case-studies/agents-that-act/sales-copilot#main) to practice speaking and the [Deep Dive](/modules/15-fde-case-studies/agents-that-act/sales-copilot#deep-dive) for mechanisms. The [source](/modules/15-fde-case-studies/agents-that-act/sales-copilot#full-pack) is the full reference.

## One sentence

**Build the brief before the meeting as the rep, recheck access when serving it, cite every fact, block unapproved external claims, and preview every CRM write.**

## Five outputs by risk

**Account summary + opportunity risks:** read-only. **Discovery questions + email drafts:** draft-only. **CRM update suggestion:** preview and approval before write-back.

## Ask first

Workflow and decision? Who uses/reviews? Which tasks read/draft/write? Which sources and permissions? Approved claims and prices? Refusal cases? 30-day pilot metric? Audit proof?

## Three lanes

**Precompute:** sources → ACL/territory mirror → structured store + hybrid index → snapshot as rep → permission-keyed cache.

**Ask:** SSO/role/territory → route → authorized evidence → fresh post-check → cited answer/draft → claim verifier.

**Write:** proposed exact fields → preview → human approval → allowlisted idempotent gateway → CRM receipt.

**LLM/agent role:** The copilot LLM summarizes and drafts; a bounded agent handles ambiguous steps. Common CRM lookups are deterministic, and the model cannot approve claims or writes.

## Rules

1. Snapshot is a materialized view, not an authorization decision; recheck after territory change.
2. CRM owner, role hierarchy, territory, sharing rules, and field masks all matter.
3. Structured counts and ID lookups use reviewed CRM operations, not vector similarity.
4. Opportunity risk comes from fetched fields and interactions, not model memory.
5. External claims require approved playbook/policy evidence; verifier **blocks**.
6. Permission uncertainty and approval failures close the path.

## Source targets

Interactive **3–8 s**. Example gates: ≥90% grounded claims, ≥95% citations, ≥80% task completion, ≥95% high-risk escalation, **zero permission violations and zero critical unsupported external claims**.

## Failure card

CRM down → authorized stale snapshot labeled, no writes. Territory changed → invalidate and reauthorize. Missing fact → say so. Price/certification unapproved → block draft. Injected email/transcript → data, never instructions.

## Rollout

One connector + territory matrix → offline golden set → shadow → read-only pilot → approved drafts/writes. Gate critical claim slices independently; measure rep adoption and prep-time reduction too.

## Latency answer

30–45 s prep comes from agent steps and serial tools. Precompute, deterministic route, permission-scoped cache, parallel safe reads, bounded graph. Measure step count, tool time, cache hit, p95, cost/workflow.

## Regression card

Aggregate **96.7%/120** concealed regulated claims **83.3%/6**. Online unsupported claims **8.7% vs 1.2%** after model upgrade and warn-only verifier. Roll back route, restore block, add claim-level critical gates.

## Interview close

“The system is useful only when the rep trusts both the account facts and the boundary around them: authorized evidence, approved claims, and approved writes.”
