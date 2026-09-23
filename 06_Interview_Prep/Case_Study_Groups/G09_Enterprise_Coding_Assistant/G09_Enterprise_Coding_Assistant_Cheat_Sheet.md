# G09 — Enterprise Coding Assistant: Cheat Sheet

Use the [Main guide](G09_Enterprise_Coding_Assistant_Main.md) for the interview, the [Deep Dive](G09_Enterprise_Coding_Assistant_Deep_Dive.md) for mechanisms, and the unchanged [source](G09_Enterprise_Coding_Assistant.md) for the full design.

## One sentence

**A private-code completion is a context and latency product: cache early, retrieve only authorized snippets, use a small LLM, validate, then show.**

## Ask first

Real-time p95? IDEs/languages/tasks? Whole-repo context? Code-host ACL? Private/on-prem requirement? Training consent? Validation rules? Peak load? Productivity proof?

## Flow

**On push:** code host + ACL → symbol/dependency chunks → embedding/index. **On keystroke:** extension → auth → context funnel → scoped cache hit or authorized retrieval → small LLM → syntax/API/secret/license/unsafe validation → editor. **Explicit tasks:** larger reasoning model on a separate slow lane.

**Agent role:** core completion is a routed LLM assistant. Tool-using chat mode is a separate acting-agent surface, with G03-style tool and approval controls if introduced.

## Numbers

**Inline target:** p95 under **300 ms**. Source’s illustrative stage budget: **~10 ms cache + ~40 ms context + ~200 ms streamed inference + ~50 ms validation**; reserve headroom because that sums to the full limit. First-token target example: under **100 ms**. Cost metric: per thousand completions, not only per request.

## Five rules

1. Funnel repository → signals → ranked authorized snippets → prompt. Never send the repo.
2. Exact cache first; semantic cache only with conservative threshold and tenant/permission/version key.
3. Small model for completion; large model for explicit explain/test/fix/refactor.
4. Symbol-index and security validation happen before display; validator down means no suggestion.
5. Source stays out of training without consent and out of telemetry always.

## Failure card

Backend slow/down → silence. Index down → authorized local context or safe cache. ACL stale → refuse affected snippet. Cache crosses scope → incident, disable and purge. Secret output or validation failure → suppress. Large model down → visible slow-task queue; hot path protected.

## Evaluation and rollout

Acceptance per task/language/repo is the product signal; matched-control time-to-merge, rework, and defects test productivity. Zero cross-repo/secret leaks, hallucinated APIs blocked, p95 under 300 ms. One repo + three users with different access → silent mode → live team → more repos/tasks.

“Cache first, retrieve on a miss, route by task, validate before display.”
