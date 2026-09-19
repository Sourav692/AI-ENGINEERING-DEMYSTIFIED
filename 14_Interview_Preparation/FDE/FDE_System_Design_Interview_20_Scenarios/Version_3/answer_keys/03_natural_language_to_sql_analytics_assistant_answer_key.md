# Natural-Language-to-SQL Analytics Assistant - Answer Key

This answer key is designed for interview preparation. It shows what a strong GenAI FDE candidate should ask, design, evaluate, secure, and communicate before moving from demo to production.

## Strong discovery questions
- Who owns each metric definition, how often do definitions change, and who approves a change?
- Is there already a semantic layer or metrics catalog, or must this system build one from scratch?
- Which SQL dialects and warehouses are in scope, since dialect breadth changes generation and validation?
- What is the tolerance for latency versus cost, and can queries run synchronously or must they be async and cached?
- Is row-level and column-level security already enforced by the warehouse, or would the assistant have to reimplement it?
- What should happen when the assistant is unsure: ask a clarifying question, refuse, or escalate to an analyst?
- Which ten metrics matter most, and what does "revenue" actually mean — booked, recognized, or collected?
- What audit evidence must exist so someone can reconstruct why a given number was produced?

## Strong functional requirements
- Support the core workflow: take a natural-language question, resolve it against a governed metric, generate dialect-specific SQL, validate it, execute read-only, and return the answer with its SQL and lineage.
- Consult the semantic metric registry before touching physical tables, so the answer anchors on an approved definition.
- Retrieve only the tables, joins, and freshness context needed, never exposing the whole warehouse schema.
- Detect ambiguity and ask a clarifying question rather than silently choosing one of several plausible metrics.
- Parse candidate SQL into an AST and enforce policy against the tree, not against raw text.
- Return the result together with the exact SQL, metric lineage, and caveats such as snapshot staleness.

## Strong non-functional requirements
- Correctness: a fast, confidently wrong answer is the worst possible outcome, so trade latency for safety every time.
- Latency: keep the user-facing path synchronous; anything that only improves future answers moves to background queues.
- Security: a read-only identity that can reach only approved datasets, with warehouse-native row and column policies reused rather than reimplemented.
- Compliance: append-only query runs recording actor, SQL hash, policy decision, bytes scanned, and the schema and metric versions used.
- Reliability: fail closed on policy evaluation, planner timeouts, and suspicious scan volume; degrade on formatting or explanation failures.
- Cost: enforce scan budgets, row limits, timeouts, and bounded date windows, because an unbounded query is a reliability problem, not just a bill.

## Architecture explanation
- The user question reaches the query API, which authenticates the caller and resolves entitlements before any planning begins.
- The semantic metric registry is consulted first, so "revenue last week" anchors on the governed definition rather than whatever table looks relevant.
- The schema retriever pulls only the tables, joins, and freshness needed, backed by a cache with TTLs and version stamps so the system can explain what it used.
- If the question maps to multiple metrics or grains, the ambiguity check stops and asks, because valid SQL against the wrong definition is still a failure.
- The SQL generator produces dialect-specific SQL from the narrowed context only, never freewheeling across the full catalog.
- The candidate SQL is parsed into an AST and inspected by the policy validator, which rejects writes, unbounded cross joins, unauthorized tables, and budget violations.
- Approved queries get a cost estimate, timeout, and row limit, then run through a read-only execution gateway holding the narrowest possible credentials.
- The result summarizer returns rows, the exact SQL, lineage, and caveats; entitlement and policy are re-checked at execution, not only at planning.

## Data model / integration assumptions
- Metric(id, name, definition, dimensions, owner, version); SchemaAsset(id, engine, object, columns, sensitivity); QueryRun(id, actor, sql_hash, policy_decision, bytes_scanned, result_ref).
- Assume Metric versions are retained long enough to reconstruct why last quarter's dashboard produced a different number than today's.
- Assume QueryRun is write-once and append-only, since query history is the first place incident review and adoption analysis start.
- Assume every artifact that influences behavior is versioned — metric definitions, schema snapshots, policy bundles, generated plans — or the system works in the happy path and fails at rollout.
- Assume idempotency keys on question submission and feedback, and optimistic concurrency on metric edits, so one team cannot silently overwrite another team's definition.

## Red-team risks
- valid SQL answering the wrong business question, stale schema, join fan-out inflating totals, runaway scans, summary contradicting the table
- Semantic substitution, where the assistant quietly uses login activity for "active customers" when the approved definition requires paid activity.
- Schema drift, where a renamed table or shifted join key makes a previously good template produce something that still looks reasonable.
- Join explosions that multiply rows and inflate totals while remaining syntactically valid and passing every SQL check.
- Excessive scans that exhaust warehouse concurrency, slow other tenants, and drive an unexpected bill before anyone notices.
- Summary drift, where the table is right but the prose misstates the trend — dangerous because executives read the prose, not the rows.

## Rollout plan
- Week 0-1: pick ten governed metrics with stable definitions, known owners, and visible business impact; document non-goals.
- Week 1-2: document metric definitions, review query templates, and confirm the assistant can explain which metric it used and why.
- Week 2-3: build golden cases pairing question, approved SQL, and expected result shape, including ambiguous paraphrases and known traps.
- Week 3-4: run the golden set on every change, comparing execution accuracy and semantic correctness, and explain every failure.
- Week 5: shadow analysts on real questions while users still see the analyst's answer as the source of truth.
- Week 6-8: release to executives only once the assistant consistently matches analyst-reviewed answers and escalation works.
- After pilot: expand domain by domain, each with a named metric owner who approves definitions and owns semantic-layer changes.

## Evaluation plan
| Metric | What it proves | Strong threshold | Dataset / method |
|---|---|---|---|
| Semantic correctness | The answer matches the governed business definition | Consistently matches analyst review on scope | Golden question/SQL/result cases |
| Execution accuracy | The generated SQL runs and returns the right shape | No unexplained regression on the golden set | Golden-set replay on every change |
| Policy violations | No query escaped the safety boundary | Zero escaped; investigate repeated blocks | Policy decisions in query-run audit |
| Bytes scanned per answer | Cost stays bounded per governed question | No 20% rise over the 7-day baseline | Warehouse query telemetry |
| User trust score | Users rely on answers rather than re-checking them | At or above the launch target, not declining | In-product rating and periodic survey |
| p95 latency and escalation volume | The workflow actually improved for analysts | Within target; escalations trending down | Request traces plus analyst ticket counts |

## Weak answer
I would let an LLM write SQL against the warehouse schema and run it. This is weak because generation is not the hard part — it ignores who owns metric definitions, allows an unapproved reading of "revenue," and has no AST validation, cost bound, or way to notice a confidently wrong answer.

## Average answer
I would use a semantic layer for metric definitions, generate SQL from it, validate the query before running it, and execute with a read-only account and row limits. I would log every query. This is better, but still incomplete because it does not say what happens when the question is ambiguous, when schema drifts, or when the prose summary disagrees with the table it supposedly describes.

## Strong answer
I would reframe this from building a text-to-SQL model to building a governed decision-support system that only speaks in terms the business already agreed to. The metric registry is consulted before any physical table, ambiguity triggers a clarifying question rather than a guess, and generated SQL is parsed into an AST and checked against policy and a scan budget before a read-only gateway ever sees it. Entitlements are re-checked at execution. I would prove it on ten governed metrics with golden cases pairing question, approved SQL, and expected result, then shadow analysts before any executive sees an answer. The key is not generating SQL, but guaranteeing that valid SQL can never quietly answer the wrong business question.

## Interviewer scorecard
| Area | 1 - Weak | 3 - Average | 5 - Strong |
|---|---|---|---|
| Problem framing | "Let an LLM write the SQL" | Names executives and analysts | Reframes as governed decision support, names semantic failure as the danger |
| Requirements | "Answer questions accurately" | Lists pipeline stages | Correctness over speed, explicit non-goals, ten-metric definition of good |
| Architecture | Chat UI plus warehouse | Semantic layer and validation | Registry first, ambiguity gate, AST policy, read-only gateway, re-check at execution |
| Data/integration | Mentions a metrics table | Names the core records | Versioned metrics and schema snapshots, append-only query runs, idempotency |
| Evaluation | "We would test the SQL" | Some test queries | Golden cases, semantic correctness, bytes scanned, trust score, escalation volume |
| Safety/security | "The model will refuse" | Read-only account and logging | Least privilege, warehouse-native policies, parse not regex, result masking |
| Rollout | Ship to executives | Pilot then expand | Ten metrics, golden set, analyst shadowing, domain-by-domain with named owners |
| Communication | Explains the model | Clear but generic | Leads with the wrong-answer risk, states trade-offs, closes with the first gate |

## Final 2-minute spoken answer
I would not start with the model. The naive pitch here is to let an LLM write the SQL, and that loses immediately, because generation is not the hard part. The hard part is that "revenue" might mean booked, recognized, or collected, and a syntactically perfect query against the wrong definition is a governance failure dressed up as a working feature. So I would reframe the problem as building a governed decision-support system that only speaks in terms the business has already agreed to. That means three things from day one: a semantic layer of governed metric definitions, a safety boundary around the warehouse that is read-only and cost-bounded, and an explicit way to say "I don't know which definition you mean" instead of guessing. Architecturally, the query API authenticates and resolves entitlements, the metric registry is consulted before any physical table, the schema retriever pulls only what is needed, ambiguity triggers a clarifying question, and the generated SQL is parsed into an AST and checked against policy and a scan budget before a read-only gateway executes it with timeouts and row limits. I would prove it on ten governed metrics with golden cases pairing question, approved SQL, and expected result, then shadow analysts before any executive sees output, then expand domain by domain with named metric owners. Success is not a fast answer; it is an answer nobody has to re-check.
