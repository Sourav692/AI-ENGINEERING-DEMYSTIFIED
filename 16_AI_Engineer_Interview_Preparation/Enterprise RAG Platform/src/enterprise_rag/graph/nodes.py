# -*- coding: utf-8 -*-
"""LangGraph nodes. Each is a pure-ish function: state in, state delta out.

The pipeline, in order:

    authorize -> plan -> retrieve -> enforce -> grade --(sufficient)--> generate -> verify -> END
                                                     \\--(insufficient)--> refuse -> END

`authorize` runs FIRST and `enforce` runs BEFORE anything reaches the model. That
ordering is the security property of the whole system, so it is expressed in the
graph topology rather than left to a code convention someone can forget.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, List

from ..authz import enforcement
from ..authz.policy import compile_prefilter, explain_prefilter, merge_filters
from ..config import SETTINGS
from ..llm.client import LLMUnavailable
from ..models import Answer, Citation, ScoredChunk
from ..retrieval import expansion
from ..retrieval.rerank import LLMReranker
from ..retrieval.strategies import RetrievalContext, get_strategy
from .prompts import (GROUNDEDNESS_SYSTEM, PARTIAL_COVERAGE_NOTE, PROMPT_VERSION,
                      REFUSAL_TEMPLATE, SUFFICIENCY_SYSTEM, SYNTHESIS_SYSTEM,
                      SYNTHESIS_USER)
from .state import RAGState

CITATION_RE = re.compile(r"\[([A-Z]{2}-[A-Za-z0-9\-]+)\]")

# Response cache: identical (question, ACL filter, exact context, coverage note)
# -> reuse the drafted answer instead of paying for synthesis again. Keyed on the
# CONTEXT actually assembled, not just the question, so a different retrieval
# draw (e.g. multi-query variance) never serves a stale answer for stale
# reasoning - only a genuinely identical situation is served from cache.
# Unbounded/process-lifetime, same tradeoff as the embedding cache in
# llm/client.py; see docs/07 for the production caveat (needs a real cache
# store, TTL, and invalidation on an ACL change, none of which a local demo
# needs to prove).
_RESPONSE_CACHE: Dict[str, str] = {}


def clear_response_cache():
    """Testing/demo hook."""
    _RESPONSE_CACHE.clear()


def _response_cache_key(question: str, where: Any, context: List[ScoredChunk],
                        coverage_note: str) -> str:
    chunk_ids = sorted(sc.chunk.chunk_id for sc in context)
    where_json = json.dumps(where or {}, sort_keys=True)
    raw = f"{question}||{where_json}||{','.join(chunk_ids)}||{coverage_note}"
    return hashlib.sha256(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# 1. authorize
# ---------------------------------------------------------------------------
def authorize(state: RAGState) -> Dict[str, Any]:
    """Compile the principal's ABAC policy into a vector-store pre-filter.

    Nothing is retrieved before this runs. The filter is an optimisation; the
    authoritative check happens again in `enforce`.
    """
    trace, principal = state["trace"], state["principal"]
    trace.start("authorize")

    ctx = {"as_of": state.get("as_of")}
    where = compile_prefilter(principal, ctx)
    # Optional, caller-supplied, non-ACL narrowing (source/doc type/recency) -
    # ANDed on afterward so it can only ever restrict further, never loosen.
    where = merge_filters(where, state.get("content_filters"))
    explained = explain_prefilter(principal)

    trace.prefilter = where
    trace.prefilter_explained = explained
    trace.tenant_id = principal.tenant_id
    trace.user_id = principal.user_id
    trace.role = principal.role
    trace.prompt_version = PROMPT_VERSION
    trace.end("authorize", clauses=len(where.get("$and", [where])))

    return {"where": where, "prefilter_explained": explained}


# ---------------------------------------------------------------------------
# 2. plan
# ---------------------------------------------------------------------------
def plan(state: RAGState) -> Dict[str, Any]:
    """Decide whether the question is multi-hop and needs decomposing.

    Cheap heuristics first, model second - a question with no conjunction almost
    never needs splitting, and skipping the call saves latency on the common path.
    """
    trace, llm = state["trace"], state["llm"]
    question = state["question"]
    trace.start("plan")

    notes: List[str] = []
    subquestions: List[str] = []

    looks_multi_hop = bool(re.search(r"\band\b|\balso\b|\bas well as\b|;", question, re.I))
    if looks_multi_hop and state.get("strategy", "enterprise") == "enterprise":
        subquestions = expansion.decompose(llm, question, history=state.get("conversation_history"))
        notes.append(f"decomposition -> {len(subquestions)} sub-questions"
                     if subquestions else "decomposition considered, not needed")
    else:
        notes.append("single-hop heuristic, decomposition skipped")

    trace.subquestions = subquestions
    trace.end("plan", subquestions=len(subquestions))
    return {"subquestions": subquestions, "plan_notes": notes}


# ---------------------------------------------------------------------------
# 3. retrieve
# ---------------------------------------------------------------------------
def retrieve(state: RAGState) -> Dict[str, Any]:
    """Run the selected strategy. Every store call carries the ACL pre-filter."""
    trace, llm = state["trace"], state["llm"]
    strategy_name = state.get("strategy", "enterprise")
    trace.start("retrieve", strategy=strategy_name)

    rctx = RetrievalContext(
        principal=state["principal"],
        where=state["where"],
        llm=llm,
        settings=SETTINGS,
        subquestions=state.get("subquestions") or [],
        history=state.get("conversation_history") or [],
    )

    degraded, degraded_reason = False, None
    try:
        candidates = get_strategy(strategy_name)(state["question"], rctx)
    except LLMUnavailable as e:
        # Query expansion needs the model; plain dense search does not. Degrade
        # rather than fail - the user gets a worse answer, not an error page.
        rctx.notes.append(f"strategy degraded to dense: {e}")
        candidates = get_strategy("dense")(state["question"], rctx)
        degraded, degraded_reason = True, "query expansion unavailable; used plain vector search"

    trace.strategy = strategy_name
    trace.generated_queries = rctx.generated_queries
    trace.hyde_passage = (rctx.hyde_passage or "")[:400] or None
    trace.end("retrieve", candidates=len(candidates), notes=rctx.notes)

    return {"candidates": candidates,
            "generated_queries": rctx.generated_queries,
            "hyde_passage": rctx.hyde_passage,
            "plan_notes": (state.get("plan_notes") or []) + rctx.notes,
            "degraded": degraded, "degraded_reason": degraded_reason}


# ---------------------------------------------------------------------------
# 4. enforce  (authoritative ACL re-check + obligations + rerank)
# ---------------------------------------------------------------------------
def enforce(state: RAGState) -> Dict[str, Any]:
    """Re-evaluate the full policy on every candidate, then rerank the survivors.

    Order matters: enforce BEFORE rerank, so the reranker only ever sees material
    this principal is allowed to read, and the top-k is the best of *their* pool.
    """
    trace, llm = state["trace"], state["llm"]
    principal = state["principal"]
    trace.start("enforce")

    ctx = {"as_of": state.get("as_of")}
    report = enforcement.enforce(principal, state.get("candidates") or [], ctx,
                                 came_from_prefilter=True)

    trace.denied = [{"doc_id": sc.chunk.doc_id, "rule": d.rule, "reason": d.reason}
                    for sc, d in report.denied]
    trace.redacted_count = report.redacted_count
    trace.audit_events = report.audit_events
    trace.security_events = report.filter_disagreements
    trace.end("enforce", **{"allowed": len(report.allowed), "denied": len(report.denied),
                            "redacted": report.redacted_count})

    # --- rerank -----------------------------------------------------------
    trace.start("rerank")
    reranker = LLMReranker(llm)
    context = reranker.rerank(state["question"], report.allowed, SETTINGS.rerank_k)

    trace.candidates = [{
        "chunk_id": sc.chunk.chunk_id,
        "doc_id": sc.chunk.doc_id,
        "source": sc.chunk.attrs.source,
        "sensitivity": sc.chunk.attrs.sensitivity,
        "retrieved_by": sc.retrieved_by,
        "fused": round(sc.fused_score or 0.0, 5),
        "rerank": sc.rerank_score,
        "redacted": sc.redacted,
    } for sc in context]
    trace.context_chunk_ids = [sc.chunk.chunk_id for sc in context]
    trace.end("rerank", kept=len(context))

    return {"context": context,
            "denied_doc_ids": report.denied_doc_ids,
            "redacted_count": report.redacted_count,
            "security_events": report.filter_disagreements}


# ---------------------------------------------------------------------------
# 5. grade  (context sufficiency guardrail)
# ---------------------------------------------------------------------------
def grade(state: RAGState) -> Dict[str, Any]:
    """Decide whether to answer at all.

    A confident wrong answer is the most expensive failure mode in enterprise
    support, so the bar to proceed is explicit and the refusal path is a
    first-class outcome rather than an error.
    """
    trace, llm = state["trace"], state["llm"]
    context = state.get("context") or []
    trace.start("grade")

    if not context:
        trace.end("grade", verdict="no_context")
        return {"sufficient": False,
                "insufficiency_reason": "No material you have access to matched this question."}

    best = max((sc.rerank_score or 0.0) for sc in context)
    if best < SETTINGS.min_rerank_score:
        trace.end("grade", verdict="weak_context", best_score=best)
        return {"sufficient": False,
                "insufficiency_reason": "The closest material does not actually answer the question."}

    passages = "\n\n".join(f"[{sc.chunk.doc_id}] {sc.chunk.text[:600]}" for sc in context)
    try:
        result = llm.chat_json(
            SUFFICIENCY_SYSTEM,
            f"Question: {state['question']}\n\nPassages:\n{passages}",
            purpose="grade")
    except LLMUnavailable:
        # If the grader is unavailable, trust the reranker's score and proceed.
        trace.end("grade", verdict="grader_unavailable", best_score=best)
        return {"sufficient": True}

    verdict = str(result.get("verdict", "sufficient")).lower()
    missing = result.get("missing") or "The available material does not cover this."

    # "partial" still answers. Refusing a multi-part question because one part is
    # unanswerable is the most common over-refusal in enterprise RAG, and it is
    # especially wrong here: which part a user can answer depends on their role,
    # so a role-appropriate partial answer is the correct product behaviour.
    if verdict == "insufficient":
        trace.end("grade", verdict="insufficient", best_score=best)
        return {"sufficient": False, "insufficiency_reason": missing}

    partial = verdict == "partial"
    trace.end("grade", verdict=verdict, best_score=best)
    return {"sufficient": True,
            "partial_coverage": partial,
            "insufficiency_reason": missing if partial else None}


def route_after_grade(state: RAGState) -> str:
    return "generate" if state.get("sufficient") else "refuse"


# ---------------------------------------------------------------------------
# 6. generate
# ---------------------------------------------------------------------------
def _format_context(context: List[ScoredChunk]) -> str:
    parts, total = [], 0
    for sc in context:
        recency = sc.chunk.attrs.source_updated_at or "unknown"
        block = (f"--- [{sc.chunk.doc_id}] {sc.chunk.title}"
                 f"{' - ' + sc.chunk.section if sc.chunk.section else ''}"
                 f" (source: {sc.chunk.attrs.source}, sensitivity: {sc.chunk.attrs.sensitivity}, "
                 f"authority: {sc.chunk.attrs.authority_rank}, updated: {recency})\n"
                 f"{sc.chunk.text}")
        if total + len(block) > SETTINGS.max_context_chars:
            break
        parts.append(block)
        total += len(block)
    return "\n\n".join(parts)


def generate(state: RAGState) -> Dict[str, Any]:
    trace, llm = state["trace"], state["llm"]
    context = state["context"]
    trace.start("generate")

    # Halt-and-escalate, not loop: if the upstream fan-out (plan/retrieve/rerank)
    # already burned through the run's cost budget, refuse rather than spend more
    # on the single most expensive call (synthesis). The measurement already
    # existed on every run via `usage`/`RunTrace`; this is the missing enforcement
    # branch on top of it.
    usage = state["usage"]
    if usage.cost_usd >= SETTINGS.max_cost_per_run_usd:
        trace.end("generate", error="cost_ceiling_exceeded", cost_so_far=usage.cost_usd)
        return {"sufficient": False,
                "insufficiency_reason": "This request exceeded its cost budget before an answer "
                                        "could be generated.",
                "degraded": True,
                "degraded_reason": f"cost ceiling (${SETTINGS.max_cost_per_run_usd:.2f}) exceeded "
                                   f"before generation (spent ${usage.cost_usd:.4f})"}

    coverage_note = ""
    if state.get("partial_coverage"):
        coverage_note = PARTIAL_COVERAGE_NOTE.format(
            missing=state.get("insufficiency_reason") or "part of the question")

    cache_key = _response_cache_key(state["question"], state.get("where"), context, coverage_note)
    cached_draft = _RESPONSE_CACHE.get(cache_key)
    if cached_draft is not None:
        trace.end("generate", chars=len(cached_draft), cache_hit=True)
        return {"draft": cached_draft}

    try:
        draft = llm.chat(
            SYNTHESIS_SYSTEM,
            SYNTHESIS_USER.format(question=state["question"],
                                  context=_format_context(context),
                                  coverage_note=coverage_note),
            purpose="synthesis", model=SETTINGS.synthesis_model, max_tokens=800)
    except LLMUnavailable as e:
        trace.end("generate", error=str(e))
        return {"sufficient": False,
                "insufficiency_reason": "The answering model is currently unavailable.",
                "degraded": True, "degraded_reason": str(e)}

    _RESPONSE_CACHE[cache_key] = draft
    trace.end("generate", chars=len(draft), cache_hit=False)
    return {"draft": draft}


# ---------------------------------------------------------------------------
# 7. verify  (citation validity + groundedness)
# ---------------------------------------------------------------------------
def verify(state: RAGState) -> Dict[str, Any]:
    """Two checks on the way out.

    1. **Citation validity + ACL.** Every cited document must exist, must have been
       in the retrieved context, and must still be readable by this principal. A
       citation is itself a disclosure - it says "this document exists and is
       relevant to your question".
    2. **Groundedness.** Does the answer's content actually follow from the
       passages? This is the online quality signal, recorded on every run.
    """
    trace = state["trace"]
    llm = state["llm"]
    principal = state["principal"]
    draft = state.get("draft") or ""
    context = state.get("context") or []
    trace.start("verify")

    cited = list(dict.fromkeys(CITATION_RE.findall(draft)))
    context_doc_ids = {sc.chunk.doc_id for sc in context}

    # Drop anything not actually in the context (hallucinated citation) ...
    in_context = [d for d in cited if d in context_doc_ids]
    hallucinated = [d for d in cited if d not in context_doc_ids]
    # ... then re-check the survivors against the live policy.
    ctx = {"as_of": state.get("as_of")}
    valid = enforcement.verify_citations(principal, in_context, ctx)

    text = draft
    for bad in hallucinated + [d for d in in_context if d not in valid]:
        text = text.replace(f"[{bad}]", "")
    text = re.sub(r"\s{2,}", " ", text).strip()

    groundedness = None
    try:
        passages = "\n\n".join(f"[{sc.chunk.doc_id}] {sc.chunk.text[:600]}" for sc in context)
        g = llm.chat_json(GROUNDEDNESS_SYSTEM,
                          f"Answer:\n{text}\n\nPassages:\n{passages}",
                          purpose="groundedness")
        groundedness = float(g.get("groundedness")) if g.get("groundedness") is not None else None
    except (LLMUnavailable, TypeError, ValueError):
        groundedness = None

    by_doc = {sc.chunk.doc_id: sc for sc in context}
    citations = [Citation(doc_id=d,
                          title=by_doc[d].chunk.title,
                          section=by_doc[d].chunk.section,
                          source=by_doc[d].chunk.attrs.source,
                          sensitivity=by_doc[d].chunk.attrs.sensitivity)
                 for d in valid if d in by_doc]

    answer = Answer(text=text, citations=citations, refused=False,
                    strategy=state.get("strategy", "enterprise"),
                    degraded=bool(state.get("degraded")),
                    degraded_reason=state.get("degraded_reason"))

    trace.answer_preview = text[:400]
    trace.citations = [c.doc_id for c in citations]
    trace.groundedness = groundedness
    trace.end("verify", cited=len(cited), valid=len(valid), hallucinated=len(hallucinated),
              groundedness=groundedness)

    return {"answer": answer, "groundedness": groundedness}


# ---------------------------------------------------------------------------
# 8. refuse
# ---------------------------------------------------------------------------
def refuse(state: RAGState) -> Dict[str, Any]:
    """The clean no-answer path.

    Note what it does NOT do: it never says "there is a restricted document you
    cannot see". Acknowledging the existence of withheld material is itself a
    disclosure. The user is told the assistant cannot answer and is routed to a
    human, which is also the escalation signal the eval harness tracks.
    """
    trace = state["trace"]
    trace.start("refuse")

    reason = state.get("insufficiency_reason") or "The available material does not cover this."
    principal = state["principal"]
    next_step = ("Escalate to Tier 3 with the workspace ID and a timestamp range."
                 if principal.role.lower().startswith("tier 1")
                 else "Ask the document owner for access, or escalate to the responsible team.")

    answer = Answer(
        text=REFUSAL_TEMPLATE.format(reason=reason, next_step=next_step),
        citations=[], refused=True, refusal_reason=reason, escalate_to_human=True,
        strategy=state.get("strategy", "enterprise"),
        degraded=bool(state.get("degraded")), degraded_reason=state.get("degraded_reason"))

    trace.refused = True
    trace.refusal_reason = reason
    trace.answer_preview = answer.text[:400]
    trace.end("refuse")
    return {"answer": answer}
