# G12 — Scoping to Deployed Agent: Deep Dive

> Read with the unchanged [source](G12_Scoping_To_Deployed_Agent.md). The [Main guide](G12_Scoping_To_Deployed_Agent_Main.md) is the interview route; the [Cheat Sheet](G12_Scoping_To_Deployed_Agent_Cheat_Sheet.md) is the recall card.

## 1. Two distinct systems

The primary system is a deterministic delivery state machine: intake, gated progress, sign-off, evidence and handover. The second is the customer support-triage agent that the process delivers. An LLM helps classify and draft support replies, but it does not adjudicate its own security review, eval baseline or production approval. The source's agent runtime diagram is a design construction; the gate demo is the part actually exercised by 17 deterministic tests.

## 2. Entry contract and stages

Intake requires a measurable target and baseline, named SME and named sources. Ask whether the two-week SLA is a target or commitment; who owns go/no-go; what is reused; what a failed gate means; and whether scaling is per team or across an organization. These answers change staffing, access and the schedule. A missing SME or data source is an intake failure, not a hidden implementation task.

The seven-stage sequence is security review, data access, configuration/golden set, baseline evaluation, shadow/rollback, limited-production success metrics and go/no-go. The source's day ranges are 1–2, 3–4, 5–7, 8–9, 10–11, 12–13 and day 14. Data access still pending on day 3 auto-escalates. Each gate records signer role and evidence, and advances only to the next stage when the previous gate is complete. A deny overrides an earlier optimistic state. Audit every attempt, including rejected sign-offs.

Free-text evidence can rubber-stamp a gate, so the production form should require structured security controls, dataset lineage, signed golden set, baseline report and rollback evidence. Separate the people who build from those who approve risk. Sponsor approval should cite actual metrics, not only a checkbox.

## 3. Accelerator reuse and agent runtime

Reusable connectors, prompt templates, eval harness, guardrails and dashboards shorten the calendar. Northwind uses five of six standard components; custom escalation logic is the exception. Record `pull_or_build` for each component so teams can see where bespoke work accumulates. Reuse must still be adapted to tenant identity and customer policy.

The proposed runtime path is Zendesk ticket → PII redaction → classification of the top three categories → Confluence KB plus Salesforce read-only retrieval → grounded LLM draft → groundedness and escalation checks → human review/send policy → telemetry. Keep source credentials scoped, secrets in a vault and customer data segregated. A retrieval miss should trigger abstention or escalation. The source does not demonstrate an autonomous action loop; avoid calling the LLM draft an independent release authority.

## 4. Outcomes and limitations

The demo reports 4m12s first response, 63% zero-edit sends, .83 evaluation score against .75 baseline, rollback under two minutes, .27 override rate, first value in one day and `deployed True` at day 14. These are scripted demonstration results. The actual week-four retention field is unavailable, so it cannot support a retention claim. The 17 tests demonstrate gate enforcement, not agent quality in live production.

The source calls out missing scope-change sponsor approval, real provisioning, eval-harness integration, versioned rollback and concurrent-engagement scaling. A production plan should add these before promising the same calendar broadly. If data access, security or golden-set agreement fails, a no-go is safer than silently compressing later stages.

## 5. Evaluation, cost and operations

Build a golden set with top ticket classes, ambiguous cases, PII, retrieval gaps, escalation triggers and policy exceptions. Test classification, grounded replies, refusal/escalation behavior, response latency and human-edit rate. Shadow mode collects evidence without broad sending. Limited production uses a defined approval policy and rollback trigger. Track cost per resolved ticket, token/step budget, human review load and post-handover retention separately from demo results.

Credentials should be scoped during the engagement and transferred or revoked at handover. A runbook should name the ongoing owner, how to inspect dashboards, how to stop sends, and which version to roll back to. Measure override reasons: a high rate can reveal weak retrieval, an overly conservative policy or poor classification.
