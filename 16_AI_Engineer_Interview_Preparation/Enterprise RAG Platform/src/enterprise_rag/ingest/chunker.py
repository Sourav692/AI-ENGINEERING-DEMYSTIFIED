# -*- coding: utf-8 -*-
"""Structure-aware chunking.

Fixed-size chunking cuts through the middle of a table of service-credit tiers and
produces a chunk that says "25% credit" with no indication of what triggers it.
Splitting on markdown headings first, then packing to a target size, keeps a
semantic unit intact and lets every chunk carry its section heading - which turns
out to matter more for retrieval quality than any embedding-model choice.
"""
from __future__ import annotations

import re
from typing import List

from ..config import SETTINGS
from ..models import Chunk, Document

HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$", re.M)


def _split_by_heading(text: str) -> List[tuple]:
    """Return [(section_title, section_text), ...] preserving document order."""
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [("", text.strip())]

    sections = []
    if matches[0].start() > 0:
        preamble = text[: matches[0].start()].strip()
        if preamble:
            sections.append(("", preamble))

    for i, m in enumerate(matches):
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            sections.append((title, body))
        elif title:
            # A heading with no body of its own still labels what follows.
            sections.append((title, title))
    return sections


def _pack(section_title: str, body: str, target: int, overlap: int) -> List[str]:
    """Split one section into <= target-sized pieces on paragraph boundaries."""
    if len(body) <= target:
        return [body]

    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    pieces, current = [], ""
    for p in paragraphs:
        if current and len(current) + len(p) + 2 > target:
            pieces.append(current)
            # Carry a tail of the previous piece so a fact split across the boundary
            # is still recoverable from at least one side.
            tail = current[-overlap:] if overlap else ""
            current = (tail + "\n\n" + p).strip()
        else:
            current = (current + "\n\n" + p).strip() if current else p
    if current:
        pieces.append(current)
    return pieces


def chunk_document(doc: Document, settings=SETTINGS) -> List[Chunk]:
    chunks: List[Chunk] = []
    ordinal = 0
    for section_title, body in _split_by_heading(doc.text):
        pieces = _pack(section_title, body,
                       settings.chunk_target_chars, settings.chunk_overlap_chars)
        for piece in pieces:
            # Prefixing the title and section is cheap and measurably improves both
            # dense and keyword retrieval: it puts the document's subject inside the
            # embedded text instead of only in the metadata.
            header = f"{doc.title}"
            if section_title:
                header += f" - {section_title}"
            text = f"{header}\n\n{piece}"

            chunks.append(Chunk(
                chunk_id=f"{doc.attrs.doc_id}#{ordinal}",
                doc_id=doc.attrs.doc_id,
                title=doc.title,
                text=text,
                section=section_title,
                ordinal=ordinal,
                attrs=doc.attrs,
            ))
            ordinal += 1
    return chunks


def chunk_corpus(docs: List[Document], settings=SETTINGS) -> List[Chunk]:
    out: List[Chunk] = []
    for d in docs:
        out.extend(chunk_document(d, settings))
    return out
