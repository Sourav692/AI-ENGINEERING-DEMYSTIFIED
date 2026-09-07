# Observability for Tool Calls

> **Level** 🟡 Building Production Systems · **Module** 03 · **Doc** 4 of 5 · **Time** ~20 min
> **Prerequisites:** [Retry, Fallback, Memoization and the Confirmation Gate](01_Retry_Fallback_Memo_Confirm.md)
> **Source material:** `1. Company_Wise_Preparation/2. DevRev/Coding_Round/agent_tool_calling_demo/src/observability.py`, `docs/DESIGN.md` §2

## Why this matters

"Why did the agent close the wrong ticket?" is a question you will be asked. If the answer is "I don't know, the model decided", you do not have an agent — you have a liability. Every tool call must leave a record: what was called, with what arguments, what came back, how long it took, and whether it was served from cache, retried, blocked or replaced by a fallback. This is the finest-grained layer of observability; Module 04 adds the run-level trace and Module 06 adds the standards that make both interoperable.

## What one record holds

```python
@dataclass
class ToolCall:
    step: int
    tool: str
    args: dict
    status: str          # ok | cache_hit | retry | error | blocked
    result: Any = None
    error: Optional[str] = None
    ms: float = 0.0      # latency in milliseconds
```

Five statuses, and each maps to a branch of `execute_tool` from the first document in this module:

| Status | Emitted when |
|---|---|
| `blocked` | The confirmation gate refused a destructive call |
| `cache_hit` | The memo served the result; no execution |
| `retry` | A transient failure; another attempt follows |
| `ok` | Executed successfully (with latency) |
| `error` | Permanent failure, or retries exhausted — also logged by `with_fallback` before it switches tools |

Because every branch logs, the trace is a complete account. Nothing the executor does is invisible.

## The trace

```python
class ToolCallLogger:
    def log(self, tool, args, status, result=None, error=None, ms=0.0): ...
    def trace(self) -> str: ...          # human-readable table, in order
    def count(self, status) -> int: ...  # for tests and assertions
```

`trace()` renders something like:

```
 #  tool             status         ms  args -> result/error
------------------------------------------------------------------------------
 1  search_tickets   retry         0.0  {'query': 'auth'} -> temporary outage (attempt 1)
 2  search_tickets   retry         0.0  {'query': 'auth'} -> temporary outage (attempt 2)
 3  search_tickets   ok            0.1  {'query': 'auth'} -> [{'id': 'TKT-1', 'subject': 'Cann…
 4  close_ticket     blocked       0.0  {'ticket_id': 'TKT-3'} -> needs confirmation
```

Four lines answer four questions: was the dependency flaky (yes, twice), did it recover (yes), did the agent try to do something destructive (yes), and was it stopped (yes). That is the debugging story, the cost story and the audit story in one artefact.

`count(status)` is what the tests use — `log.count("retry") == 2 and log.count("ok") == 1` — and it is also the shape of a metric: retries per run, cache hit rate, blocked destructive attempts per tenant.

## Why it matters, three ways

- **Debugging.** "Why did the agent close the wrong ticket?" → read the trace: which search ran, what it returned, which ID the brain chose.
- **Cost and latency.** Sum `ms`, count calls, spot the slow tool. In an LLM system, tool latency is often the hidden half of the response time.
- **Safety and audit.** A record of every destructive action *and its confirmation*. When a customer asks "who approved this refund?", the answer is in the log, not in someone's memory.

## From in-memory log to production spans

In production this becomes **structured spans** — OpenTelemetry, or a vendor trace product such as LangSmith:

```
 trace   = one conversation (conversation_id)
   └─ span  = one agent turn (query, answer, iterations)
        └─ span  = one tool call
                   tags: tool · status · tokens · cache_hit · retries · ms
```

Attach the `conversation_id` so you can pull the whole story, and the `user`/`tenant` so you can slice it. Module 06 explains why the standard format matters more than the vendor: a customer who already runs an observability stack can ingest your spans without a bespoke integration.

Per-call telemetry and the run-level trace are complementary, not redundant. The run trace tells you what happened overall — prompt version, retrieved chunks, policy decisions, cost. Per-call telemetry tells you *exactly which step* absorbed the latency, hit the cache or needed a fallback.

## In the code

| Concept | Where |
|---|---|
| Record and logger | `project/src/observability.py` → `ToolCall`, `ToolCallLogger` |
| Every branch logs | `project/src/robustness.py` → each `logger.log(...)` in `execute_tool` and `with_fallback` |
| Session-wide trace | `Session.logger` |
| Tests that assert on the trace | `test_retry_on_flaky_tool`, `test_memoization`, `test_session_memo_persists_across_turns` |

## Interview lens

> *"Every tool call is a record: tool, args, status, latency, result or error. The five statuses map one-to-one onto the executor's branches, so the trace is complete by construction. In production that's one span per call under one span per turn under one trace per conversation, in a standard format."*

## Checkpoint

- List the five statuses and the executor branch that emits each.
- What three audiences does the tool trace serve, and what does each look for?
- How do per-call telemetry and the run-level trace differ, and why keep both?
- Sketch the trace/span hierarchy for a conversation with three turns.

**Next →** [The Eight Guard Checks](05_The_Eight_Guard_Checks.md)
