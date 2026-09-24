# G09 — Enterprise Coding Assistant: Deep Dive

The [Main guide](/modules/15-fde-case-studies/agents-that-act/enterprise-coding-assistant#main) is the spoken answer. This backs it with mechanisms from the unchanged [source study](/modules/15-fde-case-studies/agents-that-act/enterprise-coding-assistant#full-pack), especially §§3–13.

## 1. Context and index design

The extension gathers current function and file, cursor, open tabs, imports, repository structure, language, recent edits, and compiler errors. Each signal consumes tokens and carries a permission. Rank nearby code above distant history; a whole repository is never a prompt. Build the index incrementally on push, with symbol/file/dependency chunks so a function or class and its imports remain a coherent unit. Mirror code-host repository ACLs into chunk metadata and recheck authorization at retrieval. Deleted helpers must disappear from the index promptly enough to avoid stale suggestions.

An ordinary RAG-style vector result is not an authoritative count, ID lookup, or API-existence check. Use the symbol index to resolve names and to validate suggested API calls. Internal documentation and project conventions may be indexed under their own access rules. For cross-repository retrieval, the developer must have read access to every snippet included; a single allowed current file is not permission to see neighboring private repositories.

## 2. Cache correctness and invalidation

Cache before embedding, retrieval, and model inference. Exact matching is the safe first step; semantic matching raises hit rate but introduces false equivalence between prompts that look alike and require different code. A cache key includes tenant, permission signature, repository/content version, prompt/model route, language, and task context where relevant. A role or repository ACL change invalidates affected entries. A cached completion is still validated before display. Prompt-prefix caching saves static system and convention tokens; embedding caching saves unchanged chunk work. Neither is a substitute for tenant and repository scope.

The cache-first headline applies to repeated requests; a miss still uses the context funnel and permission-filtered index. Keep a measurable false-hit budget, not just a hit-rate goal. A cross-scope hit is a security incident even if the code happens to compile.

## 3. Task routing, LLM role, and validation

Inline completion gets the small low-latency model and a short output cap. Multi-line completion can use a medium route if it fits the SLO. Explicit explanation, tests, bug fixes, refactors, and architecture Q&A use the larger reasoning model and a slower lane. The router reads the IDE task type, not the model’s opinion. Persistent IDE connections, close-to-user inference, streaming, limited retrieved context, and supported decoding optimizations help the hot path.

The LLM proposes code; the validation service decides what the editor can show. Parse syntax and format, check symbols/APIs against the index, scan for secrets and license conflicts, apply unsafe-pattern filters, and suppress or regenerate invalid output. On the slow path, static analysis and test execution can be added where their latency is acceptable. Retrieved comments are data, not prompt instructions. If chat mode gains tools such as “run tests” or “open PR,” it becomes an acting agent and needs scoped tool authority and approval outside the completion route.

## 4. Budget arithmetic and scale

The source’s illustrative decomposition is **10 + 40 + 200 + 50 = 300 ms**: cache, context, streamed inference, validation. Because the target is **under** 300 ms at p95, that sum leaves no margin; optimize a stage or reserve headroom for network and queue tails before calling the plan an SLO. Track first token and full completion separately. Streaming reduces perceived wait, not generation time. Suppress a late completion rather than display it after the developer has typed past it.

At millions of developers, keystrokes are bursty. Keep APIs stateless, indexes sharded by repository/region, indexing asynchronous on push, and GPU inference capacity autoscaled near users. Rate limits protect shared pools; slow refactors cannot consume the completion queue. At 10×, the source expects index pressure to bind first, so measure shard lookup p95 and cache churn as well as model saturation.

## 5. Security and telemetry

Private code flows from code host to authorized index, from index to a permission-scoped prompt, and from model to the same developer’s editor. Mask secrets before prompt assembly and scan output again. Encrypt in transit and at rest, support private deployment where required, and obtain explicit consent before using enterprise code for training. Nothing enters a third-party system without the customer’s contract and deployment decision.

Telemetry records task type, stage latencies, cache result, token counts, model/prompt versions, validation verdict, and accept/partial/reject. Store hashes or references rather than raw code or suggestion text. This is enough to diagnose a retrieval miss, template regression, route change, or model drift without turning observability into a second code repository.

## 6. Evaluation, failures, and rollout

Prompt unit checks run on template changes, golden cases on build changes, nightly regression against prior output, and controlled A/B experiments on prompts, retrieval, or models. Slice acceptance by language/task/repository. Check hallucinated APIs against the symbol index, planted secrets and unsafe patterns, license conflict, and the same query from developers with different repo permissions. A zero-leak gate is separate from acceptance and latency.

Acceptance alone does not prove productivity. Compare adopters with a matched control on time-to-merge, review rework, and defects; decide effect size and sample before interpreting the result. A deleted completion consumed latency and money even if offline fluency scores improved.

On backend failure, show no suggestion; on index failure, use authorized local context or safe cache; on stale ACL, refuse affected retrieval; on validator failure, suppress output; on slow-path model failure, queue with status. Roll out one repository and three permission-different developers first, then silent mode, a live pilot team, and incremental repositories. Expand only while p95, acceptance, and safety gates hold.

## 7. Cost pivot

Measure input tokens, output tokens, first-token p95, cache hit rate, and cost per thousand completions. Input tokens rise when retrieved snippets and history loosen; trim, compress, dedupe, and cache static prompt prefixes. Output tokens rise when completions run long; cap length and offer expansion on demand. Keep the strong model for explicit tasks. A global model downgrade or one large model for every path is a poor response to a measured context problem.
