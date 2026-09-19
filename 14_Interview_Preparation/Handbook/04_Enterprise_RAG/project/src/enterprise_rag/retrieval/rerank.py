# -*- coding: utf-8 -*-
"""Reranking - the single biggest quality win in enterprise RAG.

Retrieval optimises for *recall* over a huge corpus, cheaply. Reranking optimises
for *precision* over a small candidate set, expensively. Doing both is why you
over-retrieve 20-50 candidates and then show the model 5.

The reason it works: a bi-encoder embeds the query and the document separately and
can never compare them directly. A reranker sees the query and the document
*together* and can judge "does this passage actually answer this question?".

An LLM reranker is used here (no model download, and it can give a reason, which is
gold for debugging). A cross-encoder is cheaper and faster at scale; the interface
below is deliberately identical so it is a one-line swap.

An interaction worth mentioning in the interview: because reranking happens *after*
ACL enforcement, a restricted user's top-5 is the best of *their* authorised pool -
never a diluted version of someone else's. If you post-filtered instead, you would
rerank documents the user cannot see and hand them an empty context.
"""
from __future__ import annotations

import json
from typing import List, Optional, Protocol

from ..config import SETTINGS
from ..llm.client import LLMClient, LLMUnavailable
from ..models import ScoredChunk

RERANK_SYSTEM = """You score how well each passage answers the user's question, for an enterprise \
support assistant.

Scoring (0-10):
  9-10  directly and completely answers the question
  6-8   contains a key fact needed for the answer
  3-5   same topic, does not answer the question
  0-2   irrelevant

Judge only whether the passage answers THIS question. Do not reward passages for being \
well written, important, or interesting.

Return JSON: {"scores": [{"id": "<passage id>", "score": <0-10>, "why": "<8 words max>"}]}"""


class Reranker(Protocol):
    def rerank(self, question: str, candidates: List[ScoredChunk], top_k: int) -> List[ScoredChunk]:
        ...


class LLMReranker:
    """Score candidates with a cheap model in a single batched call."""

    name = "llm_reranker"

    def __init__(self, llm: LLMClient, settings=SETTINGS):
        self.llm = llm
        self.settings = settings

    def rerank(self, question: str, candidates: List[ScoredChunk],
               top_k: Optional[int] = None) -> List[ScoredChunk]:
        top_k = top_k or self.settings.rerank_k
        if not candidates:
            return []

        listing = []
        for sc in candidates:
            body = sc.chunk.text[:700].replace("\n", " ")
            listing.append(f"[{sc.chunk.chunk_id}] {body}")
        payload = f"Question: {question}\n\nPassages:\n" + "\n\n".join(listing)

        try:
            data = self.llm.chat_json(RERANK_SYSTEM, payload,
                                      purpose="rerank", max_tokens=1200)
        except LLMUnavailable:
            # Degrade to fusion order rather than failing the request. The answer is
            # worse, not absent, and the trace records that reranking was skipped.
            for sc in candidates:
                sc.rerank_score = None
            return candidates[:top_k]

        scores = {}
        for row in (data.get("scores") or []):
            try:
                scores[str(row["id"])] = float(row["score"])
            except (KeyError, TypeError, ValueError):
                continue

        for sc in candidates:
            sc.rerank_score = scores.get(sc.chunk.chunk_id, 0.0)

        ranked = sorted(candidates, key=lambda s: (s.rerank_score or 0.0), reverse=True)
        return ranked[:top_k]


class CrossEncoderReranker:
    """Optional local cross-encoder. Same interface, no API cost, needs a model download.

    Kept as a drop-in alternative so the platform is not tied to a provider for its
    most quality-critical step.
    """

    name = "cross_encoder"

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", settings=SETTINGS):
        from sentence_transformers import CrossEncoder      # lazy: heavy import
        self.model = CrossEncoder(model_name)
        self.settings = settings

    def rerank(self, question: str, candidates: List[ScoredChunk],
               top_k: Optional[int] = None) -> List[ScoredChunk]:
        top_k = top_k or self.settings.rerank_k
        if not candidates:
            return []
        pairs = [(question, sc.chunk.text[:1200]) for sc in candidates]
        scores = self.model.predict(pairs)
        for sc, s in zip(candidates, scores):
            # Map the cross-encoder logit onto the same 0-10 scale the rest of the
            # pipeline (and the sufficiency guardrail) expects.
            sc.rerank_score = float(max(0.0, min(10.0, (float(s) + 10.0) / 2.0)))
        return sorted(candidates, key=lambda s: s.rerank_score or 0.0, reverse=True)[:top_k]
