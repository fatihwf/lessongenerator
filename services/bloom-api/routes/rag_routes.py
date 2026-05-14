"""RAG knowledge chunk endpoints."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from logger import logger
from models import KnowledgeChunk
from rag.retriever import retrieve_chunks
from schemas import (
    KnowledgeChunkInput,
    KnowledgeChunkOut,
    RetrievedChunkOut,
    RetrieveInput,
)

router = APIRouter(prefix="/rag", tags=["rag"])


def _to_out(c: KnowledgeChunk) -> KnowledgeChunkOut:
    return KnowledgeChunkOut(
        id=c.id,
        content=c.content,
        source_type=c.source_type,
        subject=c.subject,
        grade=c.grade,
        unit=c.unit,
        bloom_levels=c.bloom_levels or [],
        source_name=c.source_name,
        created_at=c.created_at.isoformat(),
    )


@router.get("/chunks", response_model=List[KnowledgeChunkOut])
def list_chunks(
    subject: Optional[str] = Query(None),
    bloom_level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List knowledge chunks with optional filters."""
    q = db.query(KnowledgeChunk)
    if subject:
        q = q.filter(KnowledgeChunk.subject.ilike(f"%{subject}%"))
    chunks = q.order_by(KnowledgeChunk.id.desc()).all()
    if bloom_level:
        chunks = [c for c in chunks if bloom_level.lower() in [b.lower() for b in (c.bloom_levels or [])]]
    return [_to_out(c) for c in chunks]


@router.post("/chunks", response_model=KnowledgeChunkOut, status_code=201)
def create_chunk(payload: KnowledgeChunkInput, db: Session = Depends(get_db)):
    """Add a new knowledge chunk."""
    chunk = KnowledgeChunk(
        content=payload.content,
        source_type=payload.source_type,
        subject=payload.subject,
        grade=payload.grade,
        unit=payload.unit,
        bloom_levels=payload.bloom_levels or [],
        source_name=payload.source_name,
        created_at=datetime.utcnow(),
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    logger.info("rag.chunk.created", id=chunk.id, subject=chunk.subject)
    return _to_out(chunk)


@router.post("/retrieve", response_model=List[RetrievedChunkOut])
def retrieve(payload: RetrieveInput, db: Session = Depends(get_db)):
    """Retrieve relevant knowledge chunks for a query."""
    results = retrieve_chunks(
        db=db,
        query=payload.query,
        bloom_level=payload.bloom_level,
        subject=payload.subject,
        grade=payload.grade,
        top_k=payload.top_k,
    )
    return [
        RetrievedChunkOut(
            chunk_id=r["chunk_id"],
            content=r["content"],
            score=r["score"],
            source_type=r["source_type"],
            bloom_levels=r["bloom_levels"],
        )
        for r in results
    ]
