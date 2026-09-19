# -*- coding: utf-8 -*-
"""Query transformation: Multi-Query, HyDE, and decomposition.

Three different fixes for three different failure modes. Knowing *which* to reach
for is the actual skill; running all three on every query is expensive theatre.

  Multi-Query  - the user's wording is one sample from a space of phrasings, and
                 the corpus may use any other one. Generate N rewrites, retrieve
                 for each, fuse. Fixes vocabulary mismatch.
                 (Multi-Query + RRF is what people market as "RAG-Fusion".)

  HyDE         - a question and its answer are written in different registers.
                 "Why did ingest stall?" embeds nowhere near "compaction queue
                 saturated at 08:47". So have the model *hallucinate a plausible
                 answer*, embed that, and search with it. Fixes question/answer
                 asymmetry. The hallucination is never shown to the user - it is
                 only a probe.

  Decomposition- multi-hop questions ("what happened AND what did we promise
                 them contractually?") have no single chunk that answers them.
                 Split into sub-questions, retrieve independently, synthesise once.
"""
from __future__ import annotations

import json
from typing import Dict, List, Optional

from ..config import SETTINGS
from ..llm.client import LLMClient, LLMUnavailable

HISTORY_TURNS_INCLUDED = 3   # only the most recent turns - enough to resolve "it"/"that", not a transcript dump


def _format_history(history: Optional[List[Dict[str, str]]]) -> str:
    """Render the last few conversation turns as a compact block, or "" if none.
    Multi-turn awareness is opt-in and additive - every call site here degrades
    to exactly today's single-turn behaviour when `history` is empty/None."""
    if not history:
        return ""
    recent = history[-HISTORY_TURNS_INCLUDED:]
    lines = ["Conversation so far (most recent last):"]
    for turn in recent:
        q, a = turn.get("question", ""), turn.get("answer", "")
        lines.append(f"  Q: {q}")
        if a:
            lines.append(f"  A: {a[:300]}")
    return "\n".join(lines) + "\n\n"

MULTI_QUERY_SYSTEM = """You rewrite a user's support question into alternative search queries \
for an enterprise knowledge base covering help-centre docs, engineering runbooks, support tickets, \
incident post-mortems and customer contracts.

Rules:
- Produce genuinely different phrasings and vocabulary, not synonyms of each other.
- At least one variant must use precise internal/technical vocabulary (error codes, component names).
- At least one variant must use the plain language a customer would use.
- Preserve every identifier (error codes, ticket numbers, customer names, dates) exactly.
- Never invent identifiers that are not in the original question.
- If conversation history is given, use it only to resolve pronouns/references ("it", "that
  incident") in the current question into concrete terms. Never answer or rewrite a prior turn.

Return JSON: {"queries": ["...", "..."]}"""

HYDE_SYSTEM = """You write a short, confident, factual-sounding passage that would answer the \
user's question if it appeared in an enterprise knowledge base.

This passage is used only as a search probe - it is never shown to anyone. Write it in the register \
of an internal runbook or incident report: specific, technical, declarative. Invent plausible \
specifics (component names, metrics, thresholds) so the passage reads like real documentation.

Two short paragraphs maximum. No preamble, no hedging, no "I don't know"."""

DECOMPOSE_SYSTEM = """You decide whether a support question needs to be broken into sub-questions.

Break it up ONLY if answering requires facts from genuinely different places - for example an \
engineering root cause AND a commercial contract term. Do not split a question that one document \
could answer.

Return JSON:
{"needs_decomposition": true/false, "subquestions": ["...", "..."]}
Maximum 3 sub-questions. If no decomposition is needed, return an empty list."""


def generate_multi_queries(llm: LLMClient, question: str,
                           n: int = None, settings=SETTINGS,
                           history: Optional[List[Dict[str, str]]] = None) -> List[str]:
    """Return [original] + generated variants. Always includes the original.

    `history`, if given, lets rewrites resolve references to prior turns (e.g.
    "what about that incident?" -> "the March EU ingest incident") instead of
    generating variants of a pronoun. Optional and additive - omitting it is
    exactly today's single-turn behaviour.
    """
    n = n or settings.multi_query_n
    try:
        data = llm.chat_json(
            MULTI_QUERY_SYSTEM,
            f"{_format_history(history)}Generate {n} alternative search queries for:\n\n{question}",
            purpose="multi_query",
        )
        variants = [q.strip() for q in (data.get("queries") or []) if isinstance(q, str) and q.strip()]
    except LLMUnavailable:
        variants = []                      # degrade to plain retrieval, do not fail the run
    seen, out = set(), []
    for q in [question] + variants[:n]:
        key = q.lower()
        if key not in seen:
            seen.add(key)
            out.append(q)
    return out


def generate_hyde_passage(llm: LLMClient, question: str) -> Optional[str]:
    """A hypothetical answer, used only as an embedding probe."""
    try:
        passage = llm.chat(HYDE_SYSTEM, question, purpose="hyde", max_tokens=320)
        return passage or None
    except LLMUnavailable:
        return None


def decompose(llm: LLMClient, question: str, settings=SETTINGS,
             history: Optional[List[Dict[str, str]]] = None) -> List[str]:
    """Return sub-questions, or [] when the question is single-hop."""
    try:
        data = llm.chat_json(DECOMPOSE_SYSTEM, f"{_format_history(history)}{question}",
                             purpose="decompose")
    except LLMUnavailable:
        return []
    if not data.get("needs_decomposition"):
        return []
    subs = [s.strip() for s in (data.get("subquestions") or [])
            if isinstance(s, str) and s.strip()]
    return subs[: settings.max_subquestions]
