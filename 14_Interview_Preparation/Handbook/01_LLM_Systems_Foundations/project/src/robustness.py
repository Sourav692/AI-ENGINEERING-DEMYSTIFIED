"""Robustness — the four things that turn a toy loop into a real agent.

1. Confirmation gate  : a destructive tool (close/delete/refund) must be approved first.
2. Memoization        : identical (tool, args) within a session is served from cache.
3. Retry              : transient failures are retried a few times before giving up.
4. Fallback           : if the primary tool fails permanently, try an alternative.

`execute_tool` composes confirmation + memoization + retry. Fallback is a separate
helper so you can compose it explicitly where it makes sense.
"""
from __future__ import annotations
import json
import time
from typing import Any, Callable, Dict, List, Optional

from .tools import Tool, TransientError
from .observability import ToolCallLogger


# =====================================================================
# Signals
# =====================================================================
class ConfirmationRequired(Exception):
    """Raised when a destructive tool is called but not (yet) confirmed.

    Note: we store the arguments on `call_args` (NOT `args`) because
    `BaseException.args` is a reserved attribute that only holds a tuple.
    """
    def __init__(self, tool: str, call_args: dict):
        super().__init__(f"'{tool}' needs confirmation for args {call_args}")
        self.tool = tool
        self.call_args = call_args


# A confirmation policy answers: "may this destructive tool run with these args?"
ConfirmPolicy = Callable[[Tool, dict], bool]


def deny_destructive(tool: Tool, args: dict) -> bool:      # the SAFE default
    return False


def always_approve(tool: Tool, args: dict) -> bool:        # for tests / trusted flows
    return True


def _args_key(tool_name: str, args: dict) -> str:
    """A stable cache key: same tool + same args -> same string."""
    return tool_name + "::" + json.dumps(args, sort_keys=True, default=str)


def is_retryable(exc: Exception) -> bool:
    return isinstance(exc, TransientError)


# =====================================================================
# The composed executor
# =====================================================================
def execute_tool(
    tool: Tool,
    args: dict,
    *,
    logger: ToolCallLogger,
    memo: Optional[Dict[str, Any]] = None,
    confirm: Optional[ConfirmPolicy] = None,
    retries: int = 3,
) -> Any:
    """Run a tool safely: confirmation gate -> cache -> retry."""
    # 1) CONFIRMATION GATE — block destructive tools unless approved.
    if tool.destructive:
        approved = confirm(tool, args) if confirm else False
        if not approved:
            logger.log(tool.name, args, status="blocked", error="needs confirmation")
            raise ConfirmationRequired(tool.name, args)

    # 2) MEMOIZATION — identical call this session? serve the cached result.
    key = _args_key(tool.name, args)
    if memo is not None and key in memo:
        logger.log(tool.name, args, status="cache_hit", result=memo[key])
        return memo[key]

    # 3) RETRY — transient errors get a few attempts (exponential-ish backoff).
    attempt = 0
    while True:
        t0 = time.perf_counter()
        try:
            result = tool(**args)
            ms = (time.perf_counter() - t0) * 1000
            logger.log(tool.name, args, status="ok", result=result, ms=ms)
            if memo is not None:
                memo[key] = result                    # remember for next time
            return result
        except Exception as exc:                       # noqa: BLE001 (we re-raise below)
            if is_retryable(exc) and attempt < retries:
                attempt += 1
                logger.log(tool.name, args, status="retry", error=str(exc))
                time.sleep(0.01 * attempt)             # tiny backoff (real code: + jitter)
                continue
            logger.log(tool.name, args, status="error", error=str(exc))
            raise


def with_fallback(
    primary: Tool, fallback: Tool, args: dict, *, adapt: Optional[Callable[[dict], dict]] = None,
    logger: ToolCallLogger, **kwargs,
) -> Any:
    """Try `primary`; on a permanent failure, run `fallback` (optionally re-mapping args)."""
    try:
        return execute_tool(primary, args, logger=logger, **kwargs)
    except ConfirmationRequired:
        raise                                          # confirmation is not an error to fall back on
    except Exception:                                  # noqa: BLE001
        fb_args = adapt(args) if adapt else args
        logger.log(primary.name, args, status="error", error=f"falling back to {fallback.name}")
        return execute_tool(fallback, fb_args, logger=logger, **kwargs)


def disambiguate(candidates: List[Tool], query: str) -> Tool:
    """When two tools could answer the same query, pick one deterministically.

    Strategy here: prefer a NON-destructive tool, then the one whose description
    shares the most words with the query. In production you'd let the LLM choose,
    or ask the user — but never silently run a destructive tool on a tie.
    """
    words = set(query.lower().split())

    def score(t: Tool) -> tuple:
        overlap = len(words & set(t.description.lower().split()))
        return (0 if t.destructive else 1, overlap)    # safe tools win ties

    return max(candidates, key=score)
