# -*- coding: utf-8 -*-
"""Meridian Cloud - Enterprise RAG platform with attribute-based access control."""
from .config import SETTINGS, Settings
from .models import Answer, Chunk, Document, Principal, ResourceAttributes, ScoredChunk
from .identity import get_principal, list_principals

__all__ = [
    "SETTINGS", "Settings", "Answer", "Chunk", "Document", "Principal",
    "ResourceAttributes", "ScoredChunk", "get_principal", "list_principals",
]

def get_platform():
    """Lazy import so `import enterprise_rag` stays cheap and side-effect free."""
    from .graph.build import RAGPlatform
    return RAGPlatform()
