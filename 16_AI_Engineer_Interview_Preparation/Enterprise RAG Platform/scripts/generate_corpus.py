# -*- coding: utf-8 -*-
"""Generate the Meridian Cloud demo corpus.

Every document is markdown with a YAML-ish frontmatter block carrying the ABAC
attributes the policy engine reads. Keeping the corpus in one generator makes the
access-control matrix auditable at a glance - which is the whole point of the demo.

Run:  python scripts/generate_corpus.py
"""
import io
import os
import textwrap

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "corpus")

# ---------------------------------------------------------------------------
# Sensitivity ladder (must match authz.policy.SENSITIVITY_RANK)
#   public(0) < internal(1) < confidential(2) < restricted(3)
# ---------------------------------------------------------------------------

DOCS = []


def doc(doc_id, title, source, sensitivity, allowed_groups, region, body,
        need_to_know=None, valid_from=None, valid_until=None, contains_pii=False,
        product=None, owner=None):
    DOCS.append(dict(
        doc_id=doc_id, title=title, source=source, sensitivity=sensitivity,
        allowed_groups=allowed_groups, region=region, body=textwrap.dedent(body).strip(),
        need_to_know=need_to_know or [], valid_from=valid_from, valid_until=valid_until,
        contains_pii=contains_pii, product=product or "platform", owner=owner or "unassigned",
    ))


# ===========================================================================
# HELP CENTER  - public, everyone
# ===========================================================================
doc("HC-001", "Getting Started with Meridian Ingest", "helpcenter", "public",
    ["public"], "GLOBAL", product="ingest", owner="docs-team", body="""
    # Getting Started with Meridian Ingest

    Meridian Ingest is the metrics pipeline that accepts telemetry from your services and makes it
    queryable in Meridian Query within seconds.

    ## Sending your first metric

    Point your agent at the regional ingest endpoint and include your workspace write key:

        POST https://ingest.eu.meridiancloud.io/v1/metrics
        Authorization: Bearer <WORKSPACE_WRITE_KEY>

    Payloads are newline-delimited JSON. Each line must contain `name`, `value`, `timestamp`, and an
    optional `tags` object. The maximum accepted payload is 5 MB per request.

    ## Ingest tiers

    Every workspace has a sustained ingest ceiling measured in data points per minute (DPM). The
    ceiling is set by your plan. Bursts above the ceiling are buffered for up to 90 seconds before
    the pipeline begins shedding load.

    ## Common first-run problems

    - A `401` means the write key is missing or belongs to a different workspace.
    - A `413` means the payload exceeded 5 MB - split the batch.
    - A `429` means you are above your plan's DPM ceiling. See "Understanding Rate Limits".
    """)

doc("HC-002", "Understanding Error Code MRD-5031 (Ingest Backpressure)", "helpcenter", "public",
    ["public"], "GLOBAL", product="ingest", owner="docs-team", body="""
    # Error MRD-5031 - Ingest Backpressure

    `MRD-5031` is returned when the ingest pipeline has accepted your data but cannot commit it to
    the storage tier fast enough, and the write-ahead buffer for your workspace is full.

    ## What it means for your data

    Data that receives `MRD-5031` has **not** been durably stored. Your agent must retry it. Meridian
    agents version 3.2 and above retry automatically with exponential backoff and jitter. Older
    agents drop the batch silently - this is the single most common cause of gaps in customer
    dashboards.

    ## What to do

    1. Confirm your agent version is 3.2 or later.
    2. Check whether you are sustaining more than your plan's DPM ceiling.
    3. If the error persists for more than 15 minutes with normal traffic, open a support ticket and
       include your workspace ID and the exact timestamp range.

    ## Related codes

    - `MRD-5030` - transient storage timeout, safe to retry immediately.
    - `MRD-5032` - buffer full and shedding; data is being discarded at the edge.
    - `MRD-4290` - you are over your rate limit, distinct from backpressure.
    """)

doc("HC-003", "Understanding Rate Limits and the DPM Ceiling", "helpcenter", "public",
    ["public"], "GLOBAL", product="ingest", owner="docs-team", body="""
    # Rate Limits and the DPM Ceiling

    Every Meridian workspace is provisioned with a sustained data-points-per-minute (DPM) ceiling.

    ## How the ceiling is enforced

    The edge applies a token bucket per workspace. The bucket refills at your DPM ceiling and holds
    120 seconds of burst capacity. When the bucket empties, requests receive `MRD-4290` with a
    `Retry-After` header.

    ## Plan ceilings

    - Starter: 50,000 DPM
    - Growth: 500,000 DPM
    - Enterprise: negotiated, typically 2,000,000 DPM and above

    ## Raising your ceiling

    Temporary increases for a launch or migration can be requested through support with 48 hours of
    notice. Permanent increases are a commercial change and go through your account manager.
    """)

doc("HC-004", "Query Timeouts in Meridian Query", "helpcenter", "public",
    ["public"], "GLOBAL", product="query", owner="docs-team", body="""
    # Query Timeouts

    Meridian Query enforces a wall-clock timeout on every query. The default is 30 seconds for
    interactive queries and 300 seconds for scheduled queries.

    A query that exceeds the timeout returns `MRD-4080`. This is not a bug - it means the query
    scanned more data than the timeout allows.

    ## Making queries faster

    - Narrow the time range first; it is the cheapest filter.
    - Filter on indexed tags before unindexed ones.
    - Avoid high-cardinality `group by` on raw series; pre-aggregate with a recording rule instead.
    - Recording rules materialise a rollup on a schedule and query in near-constant time.
    """)

# ===========================================================================
# RUNBOOKS - internal, engineering + tier3 support
# ===========================================================================
doc("RB-101", "Runbook: Ingest Backpressure (MRD-5031) Triage", "runbook", "internal",
    ["engineering", "support-tier3", "sre"], "GLOBAL", product="ingest", owner="ingest-team", body="""
    # Runbook - Ingest Backpressure (MRD-5031)

    **Severity guide:** single workspace = SEV3. More than 5% of workspaces in a region = SEV1.

    ## Step 1 - Confirm the blast radius

    Open the `ingest-commit-lag` dashboard, filtered by region. If `commit_lag_p99` is above 45
    seconds for the region as a whole, this is a platform incident, not a customer problem.

    ## Step 2 - Identify the bottleneck

    In 90% of historical cases the bottleneck is the storage-tier compaction queue, not the ingest
    workers. Check `compaction_queue_depth`. Above 40,000 segments means compaction has fallen
    behind and the write-ahead buffer will fill within roughly 20 minutes.

    ## Step 3 - Mitigate

    1. Raise the compaction worker pool: `meridianctl scale compaction --region eu --replicas 24`.
    2. If lag continues to climb, enable shed-to-cold: `meridianctl feature enable shed_to_cold
       --region eu`. This preserves durability at the cost of a 5-10 minute query delay on new data.
    3. Never scale the ingest workers first. It increases the commit rate against an already
       saturated storage tier and makes the incident worse. This mistake extended the 14 March
       incident by roughly 40 minutes.

    ## Step 4 - Customer communication

    Any workspace with sustained `MRD-5031` for over 10 minutes must get a status page entry.
    Enterprise accounts with an SLA get a direct notification from their account manager - do not
    send this yourself, route it through the AM.
    """)

doc("RB-102", "Runbook: Compaction Queue Saturation", "runbook", "internal",
    ["engineering", "support-tier3", "sre"], "GLOBAL", product="storage", owner="storage-team", body="""
    # Runbook - Compaction Queue Saturation

    The compaction queue merges small ingest segments into larger, queryable blocks. When it falls
    behind, both ingest (backpressure) and query (slow scans over many small segments) degrade.

    ## Leading indicators

    - `compaction_queue_depth` climbing steadily for more than 15 minutes
    - `segment_count_per_workspace` above 200,000 for any single workspace
    - Query p95 latency rising while query volume is flat

    ## Root causes seen in production

    1. A single workspace sending very high-cardinality tags, producing thousands of tiny segments.
       Identify with the `top-cardinality-workspaces` query. This was the trigger on 14 March 2026.
    2. A compaction worker deploy that failed a rolling restart and silently ran at half capacity.
    3. Cold-storage throttling from the object store during regional peak.

    ## Mitigation

    Scale compaction replicas first. If a single workspace is the cause, apply a temporary
    cardinality cap: `meridianctl workspace limit-cardinality <workspace_id> --max-series 500000`.
    This is customer-visible and requires account manager sign-off for Enterprise accounts.
    """)

doc("RB-103", "Runbook: Emergency Rate Limit Override", "runbook", "internal",
    ["engineering", "support-tier3", "sre"], "GLOBAL", product="ingest", owner="ingest-team", body="""
    # Runbook - Emergency Rate Limit Override

    Used when a customer's legitimate traffic spike is being rejected with `MRD-4290` and waiting for
    the standard 48-hour commercial process is not acceptable.

    ## Authorisation required

    A temporary override above 2x the contracted ceiling requires approval from an on-call engineering
    manager. Overrides above 5x additionally require the account owner, because the cost is absorbed
    by Meridian, not billed.

    ## Applying the override

        meridianctl workspace set-dpm <workspace_id> --dpm <value> --expires-in 24h --reason "<ticket>"

    Overrides always carry an expiry. An override without an expiry has caused two separate billing
    disputes and is now blocked by policy in the CLI.

    ## After the incident

    File a follow-up with the account manager within one business day so the ceiling change can be
    made permanent or the customer can be moved to a higher plan.
    """)

doc("RB-104", "Runbook: Query Timeout Escalation (MRD-4080)", "runbook", "internal",
    ["engineering", "support-tier3", "sre"], "GLOBAL", product="query", owner="query-team", body="""
    # Runbook - Query Timeout Escalation (MRD-4080)

    ## Distinguish the two causes

    `MRD-4080` is customer-caused when the query scans a wide time range at high cardinality. It is
    platform-caused when segment counts are inflated because compaction is behind - in that case the
    same query succeeded yesterday and fails today with unchanged parameters.

    Check `segment_count_per_workspace` before telling a customer to optimise their query. Telling a
    customer to rewrite a query during a platform incident is a recurring complaint in escalation
    reviews.

    ## Escalation path

    Tier 1 handles query-optimisation advice using the public documentation. Anything where the same
    query regressed without a customer-side change goes straight to Tier 3 with the workspace ID,
    query hash, and a 24-hour window of `segment_count_per_workspace`.
    """)

# ===========================================================================
# ZENDESK TICKETS - internal, support (tier1 + tier3)
# ===========================================================================
doc("TK-4471", "Ticket 4471 - Vertex Financial: ingestion gaps on 14 March", "ticket", "internal",
    ["support-tier1", "support-tier3", "engineering"], "EU", product="ingest",
    owner="support", contains_pii=True, body="""
    # Ticket 4471 - Vertex Financial (Enterprise, EU)

    **Reporter:** Priya Raman, Platform Lead, Vertex Financial (priya.raman@vertexfinancial.example)
    **Opened:** 2026-03-14 09:412 UTC   **Priority:** P1   **Workspace:** ws_vtx_eu_001

    ## Customer description

    "We have gaps in our trading-latency dashboards between roughly 08:50 and 10:30 UTC today. Our
    agents logged thousands of MRD-5031 responses. We are running agent 3.1.4. This dashboard feeds
    our regulatory reporting and we need to know whether the data is recoverable."

    ## Tier 1 notes

    Confirmed sustained MRD-5031 across the window. Workspace was within its contracted 2,000,000 DPM
    ceiling the whole time, so this is not a rate-limit issue. Customer agent version 3.1.4 predates
    automatic retry, so the batches were dropped client-side and are not recoverable from our side.

    Escalated to Tier 3 at 11:05 UTC. Customer explicitly asked about SLA credits - routed that
    question to their account manager rather than answering it directly.

    ## Resolution

    Root cause was a platform-side compaction backlog in EU (see the incident post-mortem). Customer
    was advised to upgrade to agent 3.2+ to make future backpressure survivable. Credit discussion
    handled commercially.
    """)

doc("TK-4488", "Ticket 4488 - Northgate Retail: query timeouts after no change", "ticket", "internal",
    ["support-tier1", "support-tier3", "engineering"], "US", product="query",
    owner="support", contains_pii=True, body="""
    # Ticket 4488 - Northgate Retail (Growth, US)

    **Reporter:** Dan Okafor, SRE (dan.okafor@northgateretail.example)
    **Opened:** 2026-03-15 16:20 UTC   **Priority:** P2   **Workspace:** ws_ngr_us_014

    ## Customer description

    "Our hourly checkout-latency query has run fine for eight months. Since yesterday it times out
    with MRD-4080 about half the time. We have not changed the query."

    ## Tier 1 notes

    Initially advised the customer to narrow the time range per the public docs. Customer pushed back
    - correctly - that nothing had changed on their side.

    Rechecked `segment_count_per_workspace`: it had risen from ~40,000 to ~310,000 over 36 hours,
    which matches the compaction backlog pattern in RB-104. This was a platform-caused timeout and
    should have gone to Tier 3 immediately.

    ## Resolution

    Resolved once compaction caught up. Logged as a coaching example: check segment counts before
    giving query-optimisation advice.
    """)

doc("TK-4502", "Ticket 4502 - Kestrel Media: 401 on ingest after key rotation", "ticket", "internal",
    ["support-tier1", "support-tier3"], "GLOBAL", product="ingest",
    owner="support", contains_pii=True, body="""
    # Ticket 4502 - Kestrel Media (Growth, GLOBAL)

    **Reporter:** Ana Silva (ana.silva@kestrelmedia.example)
    **Opened:** 2026-04-02 11:02 UTC   **Priority:** P3   **Workspace:** ws_kst_gl_009

    ## Customer description

    "All ingest started returning 401 after we rotated our workspace write key this morning."

    ## Resolution

    Straightforward: the customer rotated the key in the Meridian console but their agents were still
    configured with the old key from a Kubernetes secret that was not redeployed. Confirmed by
    matching the key prefix in the rejected requests. Customer redeployed and ingest recovered within
    four minutes. No platform involvement.

    Common enough that it belongs in the public help centre - filed a docs request.
    """)

doc("TK-4519", "Ticket 4519 - Vertex Financial: request for temporary DPM increase", "ticket", "internal",
    ["support-tier1", "support-tier3", "engineering"], "EU", product="ingest",
    owner="support", contains_pii=True, body="""
    # Ticket 4519 - Vertex Financial (Enterprise, EU)

    **Reporter:** Priya Raman (priya.raman@vertexfinancial.example)
    **Opened:** 2026-04-20 08:15 UTC   **Priority:** P2   **Workspace:** ws_vtx_eu_001

    ## Request

    Customer is onboarding two new trading venues on 2026-05-04 and expects a sustained 3x increase in
    data points per minute for approximately six hours during cutover.

    ## Handling

    3x the contracted ceiling exceeds the 2x threshold, so this needed on-call engineering manager
    approval per RB-103. Approved by M. Feldman. Override applied with a 24-hour expiry and the
    ticket number as the reason string.

    Account manager notified so the ceiling change can be reviewed commercially at renewal - the
    customer may simply need a higher contracted ceiling.
    """)

# ===========================================================================
# POST-MORTEMS - confidential, engineering + tier3 only (NOT tier1, NOT sales)
# ===========================================================================
doc("PM-2026-03-14", "Post-mortem: EU Ingest Degradation, 14 March 2026", "postmortem", "confidential",
    ["engineering", "support-tier3", "sre"], "EU", product="ingest", owner="ingest-team", body="""
    # Post-mortem - EU Ingest Degradation, 14 March 2026

    **Status:** Final   **Severity:** SEV1   **Duration:** 08:47 - 10:34 UTC (107 minutes)
    **Customer impact:** 412 EU workspaces saw sustained MRD-5031. An estimated 1.8 billion data
    points were rejected. Customers on agent versions below 3.2 lost that data permanently.

    ## Root cause

    A single workspace (ws_lmb_eu_077) deployed an instrumentation change that added a unique request
    ID as a metric tag. This raised its active series count from 90,000 to 14.2 million in under
    twenty minutes.

    The cardinality explosion produced a flood of tiny segments. The compaction queue saturated at
    roughly 08:47. Because compaction and ingest share the same storage-tier write path, backpressure
    propagated to every workspace in the EU region, not just the offending one.

    **The core design flaw: there is no per-workspace isolation on the compaction path.** One tenant
    was able to degrade the region.

    ## Contributing factors

    1. The cardinality alert threshold was set at 20 million series, well above the level at which
       compaction actually saturates. It never fired.
    2. The on-call engineer initially scaled ingest workers rather than compaction, which increased
       pressure on the storage tier and extended the incident by approximately 40 minutes.
    3. Runbook RB-101 did contain the correct guidance but was not linked from the alert.

    ## Resolution

    Compaction replicas scaled from 8 to 32 at 09:58. Shed-to-cold enabled at 10:06. Queue drained by
    10:34. A temporary cardinality cap was applied to ws_lmb_eu_077.

    ## Action items

    - **ING-2291** Per-workspace compaction quotas so one tenant cannot saturate a region. *Owner:
      ingest-team. Status: in progress.*
    - **ING-2292** Lower the cardinality alert to 2 million series with a rate-of-change trigger.
      *Status: done.*
    - **ING-2293** Link the relevant runbook directly from every SEV alert. *Status: done.*
    - **ING-2294** Publish guidance discouraging unbounded tag values. *Status: done, see HC-002.*

    ## Commercially sensitive

    Four Enterprise accounts breached their contractual monthly availability commitment as a result of
    this incident and are credit-eligible. Vertex Financial is the largest of these. Do not discuss
    credit eligibility with customers directly - this is an account-manager conversation.
    """)

doc("PM-2026-01-22", "Post-mortem: Query Fleet Rolling Restart Failure, 22 January 2026", "postmortem",
    "confidential", ["engineering", "support-tier3", "sre"], "GLOBAL", product="query",
    owner="query-team", body="""
    # Post-mortem - Query Fleet Rolling Restart Failure, 22 January 2026

    **Severity:** SEV2   **Duration:** 13:10 - 15:40 UTC

    ## Root cause

    A routine deploy of the query fleet used a rolling restart with a readiness probe that returned
    healthy before the segment index had finished loading. Nodes accepted traffic while effectively
    cold, so queries were served with partial data or timed out with MRD-4080.

    Roughly 6% of interactive queries failed. No data was lost, but several customers received
    silently incomplete results, which is worse than an error and is the reason this was escalated to
    SEV2 rather than SEV3.

    ## Action items

    - **QRY-1180** Readiness probe must assert index load completion. *Status: done.*
    - **QRY-1181** Add a synthetic query canary per region that fails the deploy. *Status: done.*
    - **QRY-1182** Return an explicit partial-result marker rather than silently truncating.
      *Status: in progress.*
    """)

doc("PM-2025-11-03", "Post-mortem: Object Store Throttling, 3 November 2025", "postmortem",
    "confidential", ["engineering", "sre"], "GLOBAL", product="storage", owner="storage-team", body="""
    # Post-mortem - Object Store Throttling, 3 November 2025

    **Severity:** SEV2   **Duration:** 02:15 - 04:05 UTC

    ## Root cause

    Our cold-storage provider applied an undocumented per-prefix request cap. Our segment naming
    scheme placed all segments for a region under a single prefix, so we hit the cap during the
    nightly compaction window.

    ## Action items

    - **STO-903** Shard segment keys across 256 prefixes. *Status: done.*
    - **STO-904** Add provider-side throttle metrics to the storage dashboard. *Status: done.*
    - **STO-905** Negotiate documented rate limits into the provider contract at renewal.
      *Status: open, owned by procurement.*
    """)

# ===========================================================================
# CONTRACTS - confidential, sales + legal, region-scoped
# ===========================================================================
doc("CT-VTX-001", "Master Services Agreement - Vertex Financial", "contract", "confidential",
    ["sales", "legal", "account-management"], "EU", product="platform", owner="legal", body="""
    # Master Services Agreement - Vertex Financial Ltd

    **Effective:** 2025-07-01   **Term:** 36 months   **Region:** EU (Frankfurt)
    **Annual contract value:** EUR 1,240,000

    ## Service commitments

    - Monthly availability commitment: **99.9%** measured on successful ingest acceptance.
    - Contracted sustained ingest ceiling: **2,000,000 DPM**.
    - Support response: P1 within 30 minutes, 24x7.

    ## Service credits

    If monthly availability falls below the commitment, Vertex is entitled to service credits against
    the following month's fees:

    - Below 99.9% but at or above 99.5%: **10%** credit
    - Below 99.5% but at or above 99.0%: **25%** credit
    - Below 99.0%: **50%** credit

    Credits must be claimed by the customer in writing within 30 days of the end of the affected
    month. Credits are the sole and exclusive remedy for availability failures.

    ## Data residency

    All Vertex telemetry is processed and stored exclusively within the EU region. Meridian personnel
    outside the EU may not access raw customer telemetry without a documented, time-bound access
    grant approved by Vertex.

    ## Termination for repeated failure

    Three months of availability below 99.0% within any rolling twelve-month period entitles Vertex to
    terminate without penalty and receive a pro-rata refund of prepaid fees.
    """)

doc("CT-NGR-002", "Order Form - Northgate Retail", "contract", "confidential",
    ["sales", "legal", "account-management"], "US", product="platform", owner="legal", body="""
    # Order Form - Northgate Retail Inc

    **Effective:** 2026-01-15   **Term:** 12 months   **Region:** US (Virginia)
    **Annual contract value:** USD 186,000

    ## Plan

    Growth plan with a contracted sustained ingest ceiling of 500,000 DPM and a 99.5% monthly
    availability commitment.

    ## Service credits

    - Below 99.5% but at or above 99.0%: 5% credit
    - Below 99.0%: 15% credit

    Growth-plan credits are capped at 15% of the monthly fee in aggregate. Unlike Enterprise
    agreements, there is no termination-for-repeated-failure right on this order form.

    ## Renewal

    Auto-renews for successive 12-month terms unless either party gives 60 days notice. Uplift at
    renewal is capped at 7%.
    """)

doc("CT-KST-003", "Order Form - Kestrel Media", "contract", "confidential",
    ["sales", "legal", "account-management"], "GLOBAL", product="platform", owner="legal", body="""
    # Order Form - Kestrel Media GmbH

    **Effective:** 2026-02-01   **Term:** 12 months   **Region:** GLOBAL
    **Annual contract value:** USD 94,000

    ## Plan

    Growth plan, 500,000 DPM ceiling, 99.5% monthly availability commitment, business-hours support
    only (09:00-18:00 CET, Monday to Friday).

    ## Notable non-standard terms

    Kestrel negotiated a one-time right to a mid-term plan downgrade with 30 days notice, which is
    not offered on the standard Growth order form. Legal flagged this as a precedent risk at signing;
    do not offer it as standard in other deals.
    """)

# ===========================================================================
# PRICING - confidential, sales + legal
# ===========================================================================
doc("PR-001", "Internal Pricing and Discount Authority Matrix 2026", "pricing", "confidential",
    ["sales", "legal", "finance"], "GLOBAL", product="platform", owner="revops", body="""
    # Internal Pricing and Discount Authority - 2026

    **Internal only. Never share list-price internals or discount authority with customers.**

    ## List pricing

    - Starter: USD 900 / month, 50,000 DPM included
    - Growth: USD 6,500 / month, 500,000 DPM included
    - Enterprise: from USD 40,000 / month, negotiated ceiling
    - Overage: USD 0.85 per additional 10,000 DPM per month

    ## Discount authority

    - Account Executive: up to 10%
    - Regional Sales Director: up to 20%
    - VP Sales: up to 30%
    - Anything above 30%, or any multi-year prepay discount, requires CFO approval

    ## Floor

    Gross margin floor is 62%. Deals below the floor require finance sign-off regardless of discount
    percentage. The floor exists because Enterprise ingest ceilings above 2,000,000 DPM carry
    materially higher storage cost.

    ## Service-credit exposure

    Finance models availability credits at 0.8% of Enterprise ACV per year. The March 2026 EU incident
    alone consumed roughly 40% of the annual provision.
    """)

doc("PR-002", "Service Credit Approval Process", "pricing", "confidential",
    ["sales", "legal", "finance", "account-management"], "GLOBAL", product="platform",
    owner="revops", body="""
    # Service Credit Approval Process

    ## Who may discuss credits with a customer

    Only the named account manager or the legal team. Support engineers must route all credit
    questions to the account manager without confirming or denying eligibility. Confirming
    eligibility prematurely has twice created a contractual admission we could not walk back.

    ## Process

    1. Support or SRE confirms the availability figure for the affected month from the platform
       availability report.
    2. The account manager compares it against the contractual commitment in the customer's MSA or
       order form.
    3. Credits above USD 50,000 require VP Sales and finance approval.
    4. The credit is applied to the following month's invoice, never refunded in cash.

    ## Standing guidance

    Do not offer credits proactively. Credits are customer-claimed under nearly every Meridian
    agreement, and proactive offers have historically increased total credit spend without measurable
    retention benefit.
    """)

# ===========================================================================
# SECURITY ADVISORIES - restricted, security group, embargoed
# ===========================================================================
doc("SA-2026-07", "Security Advisory MRD-SA-2026-07 (EMBARGOED)", "advisory", "restricted",
    ["security"], "GLOBAL", need_to_know=["vuln-response"],
    valid_from="2026-09-01", product="platform", owner="secops", body="""
    # Security Advisory MRD-SA-2026-07 - EMBARGOED UNTIL 2026-09-01

    **Severity:** High (CVSS 8.1)   **Status:** Fix in staged rollout

    ## Summary

    A workspace write key scoped to one workspace could, under a specific request-shaping condition,
    be used to write metrics into a sibling workspace within the same organisation. Read access was
    never affected. There is no evidence of exploitation in production.

    ## Affected

    Ingest edge versions 4.10.0 through 4.12.3, all regions.

    ## Mitigation

    Fixed in 4.12.4. Rollout completes 2026-08-28. Customer notification is drafted and legally
    reviewed but must not be sent before the embargo lifts on 2026-09-01.

    ## Handling

    This document is restricted to the security group with vuln-response need-to-know. Do not discuss
    with customers, support, or sales before the embargo date, including in ticket notes.
    """)

doc("SA-2026-05", "Security Advisory MRD-SA-2026-05 (Published)", "advisory", "restricted",
    ["security", "engineering"], "GLOBAL", need_to_know=["vuln-response"],
    valid_from="2026-05-15", product="query", owner="secops", body="""
    # Security Advisory MRD-SA-2026-05 - Published

    **Severity:** Medium (CVSS 5.4)   **Status:** Resolved and published

    ## Summary

    Query result caching could, for a window of up to 60 seconds after a permission change, return
    cached rows to a user whose access had just been revoked.

    ## Resolution

    Cache keys now incorporate a permissions epoch that increments on any grant change, so a
    permission change invalidates the affected cache entries immediately.

    ## Lesson carried forward

    Any cache in front of a permission-filtered read path must include a permissions version in its
    key. This is now a review checklist item for all services.
    """)

# ===========================================================================
# WRITE
# ===========================================================================
def frontmatter(d):
    lines = ["---"]
    lines.append(f"doc_id: {d['doc_id']}")
    lines.append(f"title: {d['title']}")
    lines.append(f"source: {d['source']}")
    lines.append(f"sensitivity: {d['sensitivity']}")
    lines.append(f"allowed_groups: {', '.join(d['allowed_groups'])}")
    lines.append(f"region: {d['region']}")
    lines.append(f"product: {d['product']}")
    lines.append(f"owner: {d['owner']}")
    lines.append(f"contains_pii: {str(d['contains_pii']).lower()}")
    if d["need_to_know"]:
        lines.append(f"need_to_know: {', '.join(d['need_to_know'])}")
    if d["valid_from"]:
        lines.append(f"valid_from: {d['valid_from']}")
    if d["valid_until"]:
        lines.append(f"valid_until: {d['valid_until']}")
    lines.append("---")
    return "\n".join(lines)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".md"):
            os.remove(os.path.join(OUT, f))
    for d in DOCS:
        path = os.path.join(OUT, f"{d['doc_id']}.md")
        with io.open(path, "w", encoding="utf-8") as fh:
            fh.write(frontmatter(d) + "\n\n" + d["body"] + "\n")
    print(f"wrote {len(DOCS)} documents to {OUT}")
    by_source = {}
    for d in DOCS:
        by_source.setdefault(d["source"], []).append(d["sensitivity"])
    for s, sens in sorted(by_source.items()):
        print(f"  {s:12} {len(sens):>2} docs   ({', '.join(sorted(set(sens)))})")


if __name__ == "__main__":
    main()
