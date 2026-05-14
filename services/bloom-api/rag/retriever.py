"""
RAG retriever module.

MVP implementation uses TF-IDF cosine similarity for semantic-ish retrieval
with Bloom-level and metadata filtering. No external vector DB required.
"""
from __future__ import annotations
import re
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from models import KnowledgeChunk
from logger import logger


def tokenize(text: str) -> List[str]:
    """Simple tokenizer: lowercase, alphanumeric only."""
    return re.findall(r"[a-z\u00c0-\u024f\u0370-\u03ff\u0400-\u04ff]+", text.lower())


def tfidf_score(query_tokens: List[str], doc_tokens: List[str]) -> float:
    """
    Compute a simple term-overlap score between query and document.

    Args:
        query_tokens: Tokenized query.
        doc_tokens: Tokenized document.

    Returns:
        Score in [0, 1].
    """
    if not query_tokens or not doc_tokens:
        return 0.0
    doc_set = set(doc_tokens)
    matches = sum(1 for t in query_tokens if t in doc_set)
    return matches / len(query_tokens)


def retrieve_chunks(
    db: Session,
    query: str,
    bloom_level: Optional[str] = None,
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    top_k: int = 5,
) -> List[dict]:
    """
    Retrieve the most relevant knowledge chunks for a query.

    Applies metadata filters (subject, grade, bloom_level) then ranks
    by TF-IDF cosine similarity. Returns explainable trace entries.

    Args:
        db: SQLAlchemy session.
        query: The retrieval query string.
        bloom_level: Optional Bloom level filter.
        subject: Optional subject filter.
        grade: Optional grade filter.
        top_k: Number of results to return.

    Returns:
        List of dicts with chunk_id, content, score, bloom_match, source_type, bloom_levels.
    """
    logger.info("rag.retrieve", query=query[:80], bloom_level=bloom_level, subject=subject)

    q = db.query(KnowledgeChunk)
    if subject:
        q = q.filter(KnowledgeChunk.subject.ilike(f"%{subject}%"))
    if grade:
        q = q.filter(KnowledgeChunk.grade == grade)

    chunks = q.all()

    if not chunks:
        logger.warning("rag.retrieve.empty", message="No chunks found in DB for filters")
        return []

    query_tokens = tokenize(query)
    scored: List[Tuple[float, KnowledgeChunk]] = []

    for chunk in chunks:
        doc_tokens = tokenize(chunk.content)
        score = tfidf_score(query_tokens, doc_tokens)

        bloom_boost = 0.0
        bloom_match = False
        if bloom_level and chunk.bloom_levels:
            chunk_levels = [lvl.lower() for lvl in chunk.bloom_levels]
            if bloom_level.lower() in chunk_levels:
                bloom_boost = 0.3
                bloom_match = True

        final_score = min(score + bloom_boost, 1.0)
        scored.append((final_score, bloom_match, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, bloom_match, chunk in scored[:top_k]:
        results.append({
            "chunk_id": chunk.id,
            "content": chunk.content,
            "score": round(score, 4),
            "bloom_match": bloom_match,
            "source_type": chunk.source_type,
            "bloom_levels": chunk.bloom_levels or [],
        })

    logger.info("rag.retrieve.done", returned=len(results))
    return results
