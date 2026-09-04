# -*- coding: utf-8 -*-
"""Reciprocal Rank Fusion - the glue that makes hybrid search and RAG-Fusion work.

RRF combines several ranked lists without needing their scores to be comparable.
That is the whole trick: a cosine similarity of 0.82 and a BM25 score of 14.3 mean
nothing to each other, but "3rd place" and "1st place" always do.

    score(d) = sum over lists L of  1 / (k + rank_L(d))

`k` (60 by convention) damps the influence of the very top ranks so a document that
appears respectably in *several* lists beats one that tops a single list. That
"agreement across retrievers" property is exactly what you want in enterprise
search, where a document matching both the meaning and the literal error code is
almost always the right one.
"""
from __future__ import annotations

from typing import Dict, List

from ..config import SETTINGS
from ..models import ScoredChunk


def reciprocal_rank_fusion(ranked_lists: List[List[ScoredChunk]],
                           k: int = None,
                           top_n: int = None) -> List[ScoredChunk]:
    """Fuse ranked lists into one. Returns the surviving ScoredChunks, best first.

    Note: this annotates the input ScoredChunk objects in place (`fused_score`,
    `score`, `retrieved_by`) so that retrieval provenance survives into the trace.
    Do not feed the same list into two fusion calls and compare the results.
    """
    k = k if k is not None else SETTINGS.rrf_smoothing
    top_n = top_n if top_n is not None else SETTINGS.fusion_k

    scores: Dict[str, float] = {}
    best: Dict[str, ScoredChunk] = {}
    provenance: Dict[str, List[str]] = {}

    for ranked in ranked_lists:
        for rank, sc in enumerate(ranked):
            cid = sc.chunk.chunk_id
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
            provenance.setdefault(cid, [])
            for tag in sc.retrieved_by:
                if tag not in provenance[cid]:
                    provenance[cid].append(tag)
            # Keep the instance that ranked best; its per-retriever ranks are the
            # ones worth showing in a trace.
            if cid not in best or rank < (best[cid].dense_rank or 10**6):
                best[cid] = sc

    fused: List[ScoredChunk] = []
    for cid, s in scores.items():
        sc = best[cid]
        sc.fused_score = s
        sc.score = s
        sc.retrieved_by = provenance[cid]
        fused.append(sc)

    fused.sort(key=lambda x: x.fused_score, reverse=True)
    return fused[:top_n]
