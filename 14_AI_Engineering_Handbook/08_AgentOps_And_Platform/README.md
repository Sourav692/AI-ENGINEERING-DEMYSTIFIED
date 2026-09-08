# Module 08 · AgentOps and Platform

> **Level** 🟠 Scale, Security, Operations · **Docs** 6 · **Time** ~3 h
> **Prerequisites:** Modules 04, 05, 06, 07
> **Lab:** `../04_Enterprise_RAG/project/notebooks/04-databricks-enterprise-rag.ipynb` and `project/databricks/validate_*.py` (need a Databricks workspace); `../07_Multi_Agent_Systems/reference_code/` (Terraform, CI workflow, PyRIT dashboard — read)

The "after it works once" module. How do you change a prompt safely, and what does that look like with real tools named? What changes when the platform gives you governance for free — and the one place it deliberately does not? How does one system serve four channels, and what does "escalate to a human" actually do? How do you keep proving the guardrails hold? And what does all of it run on?

## Reading order

| # | Doc | What you get | Time |
|---|---|---|---|
| 1 | [Prompt Versioning, Rollout and Rollback](01_Prompt_Versioning_Rollout_Rollback.md) | Prompts as deployable artefacts; the two gates; shadow → canary → promote; rollback as a pointer flip; A/B with the safety gate held at zero | 20 min |
| 2 | [AgentOps on Databricks](02_AgentOps_On_Databricks.md) | Every concept from doc 1 mapped to a Databricks primitive: UC Model Registry aliases, `mlflow.genai.evaluate()`, MemAlign, Model Serving traffic config, MLflow Tracing to UC tables, system tables | 25 min |
| 3 | [Enterprise RAG on Databricks](03_Enterprise_RAG_On_Databricks.md) | Module 04 rebuilt on the Lakehouse; the two facts that force a physical split; row filters and masks as the policy; OBO; managed hybrid and rerank; `no_leak` as a SQL assertion; what was verified live | 60 min |
| 4 | [Multi-Channel Delivery and Human Escalation](04_Multi_Channel_And_HITL_Escalation.md) | One pipeline, a thin adapter that changes only latency budget and format; the five things escalation must do | 20 min |
| 5 | [Red Teaming](05_Red_Teaming.md) | Six architectural attacks and why each fails; PyRIT's four attack families weekly through the real path; a red-team programme | 20 min |
| 6 | [Infrastructure and CI/CD](06_Infra_And_CICD.md) | Terraform, GitHub Actions, auto-rollback, secrets at startup; the Databricks equivalent with DABs; the assembled pipeline | 20 min |

## How to read docs 2 and 3

Answer any design question generically first — that is Modules 04–07. Docs 2 and 3 are what you switch to when asked *"have you actually done this?"* Leading with vendor names reads as name-dropping; leading with the architecture and then grounding it reads as someone who has shipped it.

## Checkpoint

You are ready for Level 4 when you can:

- Describe the full prompt-change pipeline from edit to nightly monitoring, naming the gate at each step.
- Map versioning, gating, canary, rollback, tracing and audit to their Databricks mechanisms.
- State the two Vector Search facts and draw the forced two-object design.
- Say what a channel adapter may and may not change, and list the five obligations of escalation.
- Name the six architectural attacks and the four adversarial families, and say why the red team must use the real path.

**Next →** [Module 09 · AI System Design Casebook](../09_AI_System_Design_Casebook/README.md)
