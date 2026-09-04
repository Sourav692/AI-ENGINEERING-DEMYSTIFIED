# -*- coding: utf-8 -*-
"""The LangGraph state object.

One typed dict flows through every node. Keeping it flat and explicit means the
trace can be reconstructed from the state alone, and any node can be tested in
isolation by handing it a dict.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from ..llm.client import LLMClient, Usage
from ..models import Answer, Principal, ScoredChunk
from ..observability.trace import RunTrace


class RAGState(TypedDict, total=False):
    # --- request ----------------------------------------------------------
    question: str
    principal: Principal
    strategy: str
    as_of: Optional[str]                 # lets tests pin "today" for embargo rules
    content_filters: Optional[Dict[str, Any]]  # optional, non-ACL: source/doc type/recency
    conversation_history: List[Dict[str, str]]  # prior {"question","answer"} turns, if any

    # --- infrastructure handles ------------------------------------------
    llm: LLMClient
    usage: Usage
    trace: RunTrace

    # --- authorisation ----------------------------------------------------
    where: Dict[str, Any]
    prefilter_explained: str

    # --- planning ---------------------------------------------------------
    subquestions: List[str]
    generated_queries: List[str]
    hyde_passage: Optional[str]
    plan_notes: List[str]

    # --- retrieval --------------------------------------------------------
    candidates: List[ScoredChunk]
    context: List[ScoredChunk]

    # --- enforcement ------------------------------------------------------
    denied_doc_ids: List[str]
    redacted_count: int
    security_events: List[Dict[str, Any]]

    # --- generation -------------------------------------------------------
    draft: str
    answer: Answer
    sufficient: bool
    partial_coverage: bool
    insufficiency_reason: Optional[str]
    groundedness: Optional[float]
    degraded: bool
    degraded_reason: Optional[str]
