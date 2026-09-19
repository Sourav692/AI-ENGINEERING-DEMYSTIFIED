# 10. Text-to-SQL Safety
## What the diagram shows

This diagram shows a safe text-to-SQL workflow. A user question is parsed semantically, guarded against unsafe schema access, converted into SQL, checked by a SQL policy checker, executed only against a read-only database replica, sampled for results, explained to the user, and logged for audit.

The main point is that text-to-SQL must be treated as a controlled analytics system, not as free-form database access.

## How to explain it in an interview

A strong spoken explanation could be:

> I would never let the model directly query production databases. The system should expose a curated semantic layer and schema guard. The SQL generator creates a query only for allowed tables and columns. A policy checker blocks writes, joins across restricted datasets, excessive scans, PII access, or tenant violations. Queries run against a read-only replica with limits, timeouts, and audit logging. The explanation generator should describe the result and warn about limitations.

## Key trade-offs

- **Natural language flexibility vs governance:** Users want broad questions; the system must restrict unsafe queries.
- **Raw schema access vs semantic layer:** Raw schemas are powerful but risky. Semantic layers are safer but require maintenance.
- **Accuracy vs latency:** Query validation, sampling, and explanation improve trust but increase response time.
- **Read-only replica freshness vs safety:** Replicas protect production but may lag behind live data.

## Failure modes

- Model generates SQL using restricted columns.
- Query accidentally scans huge tables and causes cost or performance problems.
- Tenant filter is missing in generated SQL.
- SQL policy checker misses unsafe joins.
- Explanation overstates certainty or hides sampling limits.
- Read replica lag produces stale answers.
- Audit log stores sensitive query results.

## Security concerns

- Use read-only credentials.
- Enforce row-level and tenant-level security outside the model.
- Block DDL, DML, exports, and unrestricted SELECTs.
- Mask or aggregate sensitive fields.
- Add query limits, timeouts, and cost guards.
- Log query intent, generated SQL, policy decision, execution metadata, and user identity.

## What a weak candidate misses

A weak candidate says: “Convert the question to SQL and run it.” That is dangerous. It ignores production database safety, tenant filters, schema restrictions, cost limits, and audit requirements.

## What a strong candidate says

A strong candidate explains semantic parsing, schema guards, SQL policy checks, read-only replicas, row-level security, query budgets, result sampling, explanation limits, and audit logging.

## Visual improvement suggestion

Group the diagram into:

- **Question Understanding:** User Question, Semantic Parser
- **Governance:** Schema Guard, SQL Policy Checker
- **Execution:** Read-Only Replica, Limits, Timeouts
- **Response:** Result Sampler, Explanation Generator
- **Audit:** Query Log, Policy Decision, User/Tenant Context

Add a red boundary before database execution: **“Only validated read-only SQL may pass.”**
