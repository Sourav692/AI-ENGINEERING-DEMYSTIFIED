# -*- coding: utf-8 -*-
"""Per-tenant rate limiting (§6 - "noisy-neighbour control: per-tenant rate
limits and token budgets").

A fixed-window counter, checked before `RAGPlatform.ask()` does ANY work -
before an LLMClient is even constructed - so a rate-limited request costs
nothing beyond a dict lookup. Same `Decision` shape as every other gate in this
codebase: a named rule, an explicit reason, no override path.

In-process only, same tradeoff as the embed/response caches - a real deployment
needs a shared store (Redis token bucket, etc.) across workers, not a
per-process dict. See docs/07 for that caveat.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from ..config import SETTINGS
from .policy import Decision

_WINDOWS: Dict[str, Deque[float]] = defaultdict(deque)


def check(tenant_id: str, settings=SETTINGS, now: float = None) -> Decision:
    """Record one request attempt for `tenant_id` and decide if it's within
    the per-minute limit. Denies (without recording) if already over."""
    now = time.time() if now is None else now
    window = _WINDOWS[tenant_id]

    cutoff = now - 60.0
    while window and window[0] < cutoff:
        window.popleft()

    if len(window) >= settings.rate_limit_per_minute:
        return Decision(False, "rate_limited",
                        f"tenant '{tenant_id}' exceeded {settings.rate_limit_per_minute} "
                        f"requests/minute")

    window.append(now)
    return Decision(True, "within_limit", "request accepted")


def reset(tenant_id: str = None):
    """Testing/demo hook. Clears one tenant's window, or every tenant's if None."""
    if tenant_id is None:
        _WINDOWS.clear()
    else:
        _WINDOWS.pop(tenant_id, None)
