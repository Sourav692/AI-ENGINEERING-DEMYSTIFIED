# -*- coding: utf-8 -*-
"""Thin OpenAI wrapper: chat, structured JSON, and embeddings.

Everything the platform does with a model goes through here so that retries,
timeouts, token accounting and cost attribution live in exactly one place - which
is what you want when the interviewer asks "who pays for a runaway agent?".
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI
from openai import APIError, APITimeoutError, RateLimitError

from ..config import SETTINGS

# Published prices (USD per 1M tokens) for cost attribution. Keeping them here
# rather than in a spreadsheet is what makes per-tenant cost reporting possible.
PRICING = {
    "gpt-4o-mini":            {"in": 0.150, "out": 0.600},
    "gpt-4o":                 {"in": 2.500, "out": 10.000},
    "text-embedding-3-small": {"in": 0.020, "out": 0.0},
}


@dataclass
class Usage:
    """Running token and cost totals for a single request."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    embedding_tokens: int = 0
    calls: int = 0
    cost_usd: float = 0.0
    by_purpose: Dict[str, int] = field(default_factory=dict)

    def add(self, model: str, prompt: int, completion: int, purpose: str, embedding: bool = False):
        self.calls += 1
        if embedding:
            self.embedding_tokens += prompt
        else:
            self.prompt_tokens += prompt
            self.completion_tokens += completion
        p = PRICING.get(model, {"in": 0.0, "out": 0.0})
        self.cost_usd += (prompt / 1e6) * p["in"] + (completion / 1e6) * p["out"]
        self.by_purpose[purpose] = self.by_purpose.get(purpose, 0) + prompt + completion

    def merge(self, other: "Usage"):
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.embedding_tokens += other.embedding_tokens
        self.calls += other.calls
        self.cost_usd += other.cost_usd
        for k, v in other.by_purpose.items():
            self.by_purpose[k] = self.by_purpose.get(k, 0) + v


# Embedding cache: identical (model, text) never gets re-embedded. Shared across
# every LLMClient instance/request in this process (unlike Usage, which is
# per-request) - a repeated question, or the same chunk text seen by two
# different retrieval strategies in the same demo session, only ever pays once.
# Unbounded/process-lifetime; a production version needs an LRU cap and a real
# cache store shared across workers, not an in-process dict - see docs/07.
_EMBED_CACHE: Dict[Tuple[str, str], List[float]] = {}


def clear_embed_cache():
    """Testing/demo hook."""
    _EMBED_CACHE.clear()


class LLMUnavailable(RuntimeError):
    """Raised when the model provider cannot serve the request after retries.

    Callers catch this and degrade gracefully rather than failing the whole run.
    """


class _CircuitBreaker:
    """Process-wide, not per-LLMClient - it represents "is the provider
    currently down", which is a fact about the outside world, not about any
    one caller. After `failure_threshold` consecutive genuine-outage
    exhaustions (not our own 4xx bugs - see `_with_retries`), the breaker
    trips OPEN and every call fails immediately with no network attempt for
    `cooldown_s`, instead of every request separately re-discovering the same
    outage through a full retry loop. After cooldown, one trial call is
    allowed (half-open); success closes the breaker, failure reopens it."""

    def __init__(self):
        self.consecutive_failures = 0
        self.opened_at: Optional[float] = None

    def is_open(self, settings) -> bool:
        if self.opened_at is None:
            return False
        if time.time() - self.opened_at >= settings.circuit_breaker_cooldown_s:
            return False   # cooldown elapsed - allow a half-open trial call
        return True

    def record_success(self):
        self.consecutive_failures = 0
        self.opened_at = None

    def record_failure(self, settings):
        self.consecutive_failures += 1
        if self.consecutive_failures >= settings.circuit_breaker_failure_threshold:
            self.opened_at = time.time()


_BREAKER = _CircuitBreaker()


def circuit_breaker_state() -> Dict[str, Any]:
    return {"consecutive_failures": _BREAKER.consecutive_failures,
            "open": _BREAKER.opened_at is not None}


def reset_circuit_breaker():
    """Testing/demo hook."""
    global _BREAKER
    _BREAKER = _CircuitBreaker()


class LLMClient:
    """OpenAI client with bounded retries and usage accounting."""

    def __init__(self, settings=SETTINGS, usage: Optional[Usage] = None):
        self.settings = settings
        self.usage = usage or Usage()
        if not settings.has_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not found. Expected it in the repo-root .env file."
            )
        self._client = OpenAI(api_key=settings.api_key, timeout=settings.request_timeout_s)

    # -- internals ---------------------------------------------------------
    def _with_retries(self, fn, *, attempts: int = 3, purpose: str = "unknown"):
        """Exponential backoff with full jitter on the retryable failures only."""
        if _BREAKER.is_open(self.settings):
            raise LLMUnavailable(f"{purpose}: circuit breaker open - provider considered down, "
                                 f"no call attempted; retry after cooldown")

        last: Optional[Exception] = None
        for i in range(attempts):
            try:
                result = fn()
                _BREAKER.record_success()
                return result
            except (RateLimitError, APITimeoutError) as e:
                last = e
                sleep = min(8.0, (2 ** i)) * random.random()
                time.sleep(sleep)
            except APIError as e:
                # 5xx is retryable and counts as a provider-outage signal; 4xx is a
                # bug in OUR request, so it fails fast and never trips the breaker.
                if getattr(e, "status_code", 500) < 500:
                    raise LLMUnavailable(f"{purpose}: non-retryable API error: {e}") from e
                last = e
                time.sleep(min(8.0, 2 ** i) * random.random())
        _BREAKER.record_failure(self.settings)
        raise LLMUnavailable(f"{purpose}: exhausted {attempts} attempts: {last}")

    # -- public API --------------------------------------------------------
    def chat(self, system: str, user: str, *, purpose: str,
             model: Optional[str] = None, temperature: float = 0.0,
             max_tokens: int = 900) -> str:
        model = model or self.settings.fast_model

        def _call():
            return self._client.chat.completions.create(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}],
            )

        resp = self._with_retries(_call, purpose=purpose)
        u = resp.usage
        self.usage.add(model, u.prompt_tokens, u.completion_tokens, purpose)
        return (resp.choices[0].message.content or "").strip()

    def chat_json(self, system: str, user: str, *, purpose: str,
                  model: Optional[str] = None, max_tokens: int = 900) -> Any:
        """Chat constrained to valid JSON. Falls back to `{}` rather than crashing."""
        model = model or self.settings.fast_model

        def _call():
            return self._client.chat.completions.create(
                model=model,
                temperature=0.0,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}],
            )

        resp = self._with_retries(_call, purpose=purpose)
        u = resp.usage
        self.usage.add(model, u.prompt_tokens, u.completion_tokens, purpose)
        raw = (resp.choices[0].message.content or "{}").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def embed(self, texts: List[str], *, purpose: str = "embed") -> List[List[float]]:
        if not texts:
            return []
        model = self.settings.embedding_model

        # Split into what's already cached and what genuinely needs an API call -
        # only the uncached portion is billed/counted against this request's usage.
        out: List[Optional[List[float]]] = [None] * len(texts)
        to_fetch: List[str] = []
        fetch_positions: List[int] = []
        for i, t in enumerate(texts):
            cached = _EMBED_CACHE.get((model, t))
            if cached is not None:
                out[i] = cached
            else:
                to_fetch.append(t)
                fetch_positions.append(i)

        if to_fetch:
            def _call():
                return self._client.embeddings.create(model=model, input=to_fetch)

            resp = self._with_retries(_call, purpose=purpose)
            self.usage.add(model, resp.usage.total_tokens, 0, purpose, embedding=True)
            for pos, text, d in zip(fetch_positions, to_fetch, resp.data):
                out[pos] = d.embedding
                _EMBED_CACHE[(model, text)] = d.embedding

        return out
