# -*- coding: utf-8 -*-
"""Central configuration. Everything tunable lives here, nothing is hard-coded downstream."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# The repo-root .env holds OPENAI_API_KEY. Walk up until we find it so the package
# works from a notebook, a script, or pytest regardless of cwd.
_here = Path(__file__).resolve()
for _parent in _here.parents:
    _candidate = _parent / ".env"
    if _candidate.exists():
        load_dotenv(_candidate, override=False)
        break

PACKAGE_ROOT = _here.parents[1]            # src/
PROJECT_ROOT = _here.parents[2]            # enterprise_rag_platform/

# The shared repo-root .env turns LangSmith tracing on globally. This project ships
# its own trace layer (observability/trace.py) and that shared key 403s here, which
# floods stderr on every call. Opt out unless someone explicitly asks for it.
if os.environ.get("ENTERPRISE_RAG_LANGSMITH", "0") != "1":
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGSMITH_TRACING"] = "false"

# Chroma reads this at import time. Keep product telemetry off even if a client is
# constructed without Settings(anonymized_telemetry=False).
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")


@dataclass
class Settings:
    """Runtime settings for the platform."""

    # --- paths -------------------------------------------------------------
    corpus_dir: Path = PROJECT_ROOT / "data" / "corpus"
    acl_manifest_file: Path = PROJECT_ROOT / "data" / "acl_manifest.json"
    identity_file: Path = PROJECT_ROOT / "data" / "identities.json"
    golden_set_file: Path = PROJECT_ROOT / "data" / "golden_set.json"
    chroma_dir: Path = PROJECT_ROOT / "data" / "chroma"
    acl_catalog_path: Path = PROJECT_ROOT / "data" / "acl_catalog.db"
    runs_dir: Path = PROJECT_ROOT / "runs"

    # --- tenancy -----------------------------------------------------------
    # One Chroma collection per tenant: defence in depth, so a bug in the metadata
    # filter still cannot cross a tenant boundary.
    collection_prefix: str = "meridian_kb"

    # --- models ------------------------------------------------------------
    embedding_model: str = "text-embedding-3-small"
    fast_model: str = "gpt-4o-mini"        # rewrites, HyDE, reranking, grading
    synthesis_model: str = "gpt-4o-mini"   # final answer
    embedding_dim: int = 1536

    # --- chunking ----------------------------------------------------------
    chunk_target_chars: int = 1100
    chunk_overlap_chars: int = 150

    # --- retrieval ---------------------------------------------------------
    # dense_k/bm25_k/fusion_k set the pre-rerank candidate pool. The prep doc's
    # reference architecture over-retrieves 50-100 before reranking; this repo's
    # 22-document demo corpus doesn't have 50 distinct relevant chunks to find,
    # so these are sized for a realistic pool without wastefully over-fetching
    # against a corpus this small - see docs/07 §4.4 for the sizing rationale.
    dense_k: int = 40                      # per-query dense candidates
    bm25_k: int = 40                       # per-query keyword candidates
    fusion_k: int = 50                     # candidates surviving fusion, pre-rerank
    rerank_k: int = 6                      # chunks actually shown to the synthesiser
    rrf_smoothing: int = 60                # the k constant in Reciprocal Rank Fusion
    multi_query_n: int = 4                 # number of generated query variants
    max_subquestions: int = 3

    # --- guardrails --------------------------------------------------------
    min_rerank_score: float = 3.0          # 0-10 scale; below this the context is too weak
    max_context_chars: int = 12000
    request_timeout_s: int = 60
    max_cost_per_run_usd: float = 0.10     # a run this expensive is almost certainly a runaway loop

    # --- rate limiting / resilience -----------------------------------------
    rate_limit_per_minute: int = 30        # per-tenant; generous enough not to trip normal demo use
    circuit_breaker_failure_threshold: int = 3   # consecutive LLMUnavailable before the breaker opens
    circuit_breaker_cooldown_s: float = 30.0     # how long the breaker stays open before a trial call

    # --- observability -----------------------------------------------------
    trace_enabled: bool = True

    api_key: str = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY", ""))

    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("sk-"))

    def collection_for(self, tenant_id: str) -> str:
        return f"{self.collection_prefix}__{tenant_id}"


SETTINGS = Settings()
