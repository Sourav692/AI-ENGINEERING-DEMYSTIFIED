# -*- coding: utf-8 -*-
"""Named, swappable retrieval strategies.

Every strategy has the same signature, so the graph can pick one at runtime and the
evaluation harness can benchmark them against each other on the same golden set.
Being able to say "here is the A/B harness, here are the numbers" is the difference
between claiming a technique helps and knowing it does.

  dense        vector search only                       (the baseline)
  bm25         keyword search only                      (identifiers, error codes)
  hybrid       dense + bm25, fused with RRF
  multi_query  N LLM rewrites, dense each, fused        (= RAG-Fusion)
  hyde         hypothetical answer embedded as the probe
  enterprise   hybrid + multi-query + HyDE + rerank     (the production default)

Every strategy receives the compiled ACL pre-filter and passes it to every single
store call. There is no code path that queries without it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..config import SETTINGS
from ..ingest import store
from ..llm.client import LLMClient
from ..models import Principal, ScoredChunk
from . import expansion
from .fusion import reciprocal_rank_fusion
from .lexical import BM25Index


@dataclass
class RetrievalContext:
    """Everything a strategy needs, assembled once per request."""

    principal: Principal
    where: Dict[str, Any]
    llm: LLMClient
    settings: Any = field(default_factory=lambda: SETTINGS)
    subquestions: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    generated_queries: List[str] = field(default_factory=list)
    hyde_passage: Optional[str] = None
    history: List[Dict[str, str]] = field(default_factory=list)   # prior turns, for reference resolution


def _embed_and_search(ctx: RetrievalContext, queries: List[str], k: int) -> List[List[ScoredChunk]]:
    """Embed a batch of queries in one API call, then search once per query."""
    vectors = ctx.llm.embed(queries, purpose="embed_query")
    lists: List[List[ScoredChunk]] = []
    for q, vec in zip(queries, vectors):
        lists.append(store.dense_search(
            ctx.principal.tenant_id, vec, ctx.where, k, matched_query=q, settings=ctx.settings))
    return lists


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------
def dense_only(question: str, ctx: RetrievalContext) -> List[ScoredChunk]:
    lists = _embed_and_search(ctx, [question], ctx.settings.dense_k)
    return lists[0][: ctx.settings.fusion_k]


def bm25_only(question: str, ctx: RetrievalContext) -> List[ScoredChunk]:
    pool = store.fetch_all_allowed(ctx.principal.tenant_id, ctx.where, ctx.settings)
    ctx.notes.append(f"bm25 pool = {len(pool)} authorised chunks")
    return BM25Index(pool).search(question, ctx.settings.fusion_k)


def hybrid(question: str, ctx: RetrievalContext) -> List[ScoredChunk]:
    dense = _embed_and_search(ctx, [question], ctx.settings.dense_k)[0]
    pool = store.fetch_all_allowed(ctx.principal.tenant_id, ctx.where, ctx.settings)
    lexical = BM25Index(pool).search(question, ctx.settings.bm25_k)
    ctx.notes.append(f"hybrid: {len(dense)} dense + {len(lexical)} lexical")
    return reciprocal_rank_fusion([dense, lexical])


def multi_query(question: str, ctx: RetrievalContext) -> List[ScoredChunk]:
    """RAG-Fusion: N rewrites -> dense retrieve each -> RRF."""
    queries = expansion.generate_multi_queries(ctx.llm, question, settings=ctx.settings, history=ctx.history)
    ctx.generated_queries = queries
    ctx.notes.append(f"multi-query: {len(queries)} variants")
    lists = _embed_and_search(ctx, queries, ctx.settings.dense_k)
    return reciprocal_rank_fusion(lists)


def hyde(question: str, ctx: RetrievalContext) -> List[ScoredChunk]:
    passage = expansion.generate_hyde_passage(ctx.llm, question)
    ctx.hyde_passage = passage
    if not passage:
        ctx.notes.append("hyde: generation unavailable, fell back to dense")
        return dense_only(question, ctx)
    # Search with both the probe and the literal question: HyDE helps with phrasing
    # asymmetry but can drift off-topic, and the original query anchors it.
    lists = _embed_and_search(ctx, [passage, question], ctx.settings.dense_k)
    ctx.notes.append("hyde: hypothetical passage + original question, fused")
    return reciprocal_rank_fusion(lists)


def enterprise(question: str, ctx: RetrievalContext) -> List[ScoredChunk]:
    """The production default: every signal fused, then reranked by the caller.

    Fan-out is: original question + N rewrites + HyDE probe on the dense side, plus
    BM25 on the original question and each sub-question. All fused with RRF.
    """
    queries = expansion.generate_multi_queries(ctx.llm, question, settings=ctx.settings, history=ctx.history)
    ctx.generated_queries = queries

    probe = expansion.generate_hyde_passage(ctx.llm, question)
    ctx.hyde_passage = probe

    dense_queries = list(queries)
    if probe:
        dense_queries.append(probe)
    if ctx.subquestions:
        dense_queries.extend(ctx.subquestions)

    ranked_lists = _embed_and_search(ctx, dense_queries, ctx.settings.dense_k)

    # Lexical side: the original wording and any sub-questions. Rewrites are not
    # used lexically - paraphrases dilute the rare identifiers BM25 relies on.
    pool = store.fetch_all_allowed(ctx.principal.tenant_id, ctx.where, ctx.settings)
    bm25 = BM25Index(pool)
    for q in [question] + ctx.subquestions:
        ranked_lists.append(bm25.search(q, ctx.settings.bm25_k))

    ctx.notes.append(
        f"enterprise fan-out: {len(dense_queries)} dense queries "
        f"({len(queries)} variants{', +hyde' if probe else ''}"
        f"{f', +{len(ctx.subquestions)} sub-questions' if ctx.subquestions else ''}), "
        f"{1 + len(ctx.subquestions)} lexical queries, pool={len(pool)}")

    return reciprocal_rank_fusion(ranked_lists)


STRATEGIES: Dict[str, Callable[[str, RetrievalContext], List[ScoredChunk]]] = {
    "dense": dense_only,
    "bm25": bm25_only,
    "hybrid": hybrid,
    "multi_query": multi_query,
    "hyde": hyde,
    "enterprise": enterprise,
}


def get_strategy(name: str):
    if name not in STRATEGIES:
        raise ValueError(f"unknown strategy '{name}'; available: {', '.join(STRATEGIES)}")
    return STRATEGIES[name]
