# G06 — Natural Language over Governed Data: Cheat Sheet

Use the [Main guide](G06_NL_Over_Governed_Data_Main.md) for the spoken answer, the [Deep Dive](G06_NL_Over_Governed_Data_Deep_Dive.md) for mechanisms, and the unchanged [source](G06_NL_Over_Governed_Data.md) for the full case.

## One sentence

**The metric registry defines the business answer; the LLM translates the question and explains a validated, read-only result.**

## Ask first

Who owns the first ten metrics? Semantic layer exists? Warehouse and dialect? Native row/column security? What ambiguity needs clarification? Scan and latency budgets? Analyst review threshold? Audit evidence?

## Flow

**Identity → governed metric → ambiguity gate → permitted schema → LLM SQL proposal → AST policy + scan-cost check → read-only warehouse with native security → numeric cross-check → answer with SQL, lineage and caveats.**

**Agent role:** default is a governed query workflow. Use a supervisor only for a real multi-specialist task; it routes, while policy and warehouse controls remain authoritative.

## Rules

1. Valid SQL can answer the wrong business question; semantic correctness is the release gate.
2. Ask about “revenue” when more than one approved definition fits.
3. Parse the AST; do not rely on regex or prompt rules to stop unsafe SQL.
4. Read-only credentials, execution-time entitlement check, warehouse-native row/column security, scan budget.
5. A summary that contradicts the table is rejected; return the table alone.

## Case numbers, with context

**MVP:** ten governed metrics, golden question/SQL/result cases, analyst shadowing. **Copilot example:** 3–8 s interactive. **AIA example:** clarify intent below 60%; seven metric views; eight-node supervisor; 16-asset index. **Cost signal:** bytes scanned per answer >20% above seven-day baseline. These are source examples to confirm with the customer.

## Failures and routes

| Trigger | Response |
|---|---|
| Wrong metric or grain | Block and clarify/analyst review; add golden case. |
| Schema drift or join fan-out | Stop affected query/template; refresh and validate cardinality. |
| Hidden column or policy failure | Fail closed. |
| Excessive scan | Narrow window or pre-aggregate; cancel if unsafe. |
| Summary mismatch | Table only, alert review queue. |

## Cost answer

Measure retries, tokens, and bytes scanned. Send metric definitions rather than the full schema; prefer approved operations, dry-run SQL, cap scans, and cache only within tenant/permission/version scope. Do not retry a wrong definition with a stronger model.

## Interview close

“Ten governed metrics, a clarifying gate, AST and cost checks, read-only execution, and analyst-reviewed semantic correctness before executive rollout.”
