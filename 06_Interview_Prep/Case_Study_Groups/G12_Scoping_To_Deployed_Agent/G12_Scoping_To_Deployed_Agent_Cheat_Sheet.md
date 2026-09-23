# G12 — Scoping to Deployed Agent: Cheat Sheet

[Main](G12_Scoping_To_Deployed_Agent_Main.md) · [Deep Dive](G12_Scoping_To_Deployed_Agent_Deep_Dive.md) · [Unchanged source](G12_Scoping_To_Deployed_Agent.md)

## Ask first

Success metric and baseline? Sponsor and SME? Data sources and credentials? Reuse versus bespoke? Failed-gate policy? Human approval and rollback?

## Seven gated stages

`Intake → security → data access → golden set → baseline eval → shadow + rollback → limited production → sponsor go/no-go / handover`

Days 1–2 / 3–4 / 5–7 / 8–9 / 10–11 / 12–13 / 14. Right signer, evidence and prior gate required. Pending access escalates on day 3.

## Agent runtime

`Zendesk → PII redaction → LLM classification → KB + read-only CRM → LLM grounded draft → escalation/grounding checks → human approval/send → telemetry`

The delivery gates are deterministic; the model cannot approve itself.

## Demo facts and caveat

Northwind: five of six components reused; 4m12s first response; 63% zero-edit sends; eval .83 versus .75 baseline; rollback <2 min; 17 gate tests. These are scripted/demo results; week-four retention is unobserved. Real provisioning, eval wiring and versioned rollback remain gaps in the source.

## Close

“I start the clock only when outcome, SME and sources are real. Each phase has evidence and an owner. I shadow, prove rollback, then limit production and let the sponsor make an informed go/no-go decision.”
