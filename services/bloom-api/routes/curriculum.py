"""Curriculum outcomes endpoints."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from bloom.classifier import classify_bloom
from database import get_db
from logger import logger
from models import CurriculumItem
from schemas import CurriculumItemInput, CurriculumItemOut

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


def _to_out(item: CurriculumItem) -> CurriculumItemOut:
    return CurriculumItemOut(
        id=item.id,
        subject=item.subject,
        grade=item.grade,
        unit=item.unit,
        outcome_text=item.outcome_text,
        bloom_level=item.bloom_level,
        secondary_bloom_levels=item.secondary_bloom_levels or [],
        bloom_confidence=item.bloom_confidence,
        created_at=item.created_at.isoformat(),
    )


@router.get("/outcomes", response_model=List[CurriculumItemOut])
def list_outcomes(
    subject: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    unit: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List all curriculum outcomes with optional filters."""
    q = db.query(CurriculumItem)
    if subject:
        q = q.filter(CurriculumItem.subject.ilike(f"%{subject}%"))
    if grade:
        q = q.filter(CurriculumItem.grade == grade)
    if unit:
        q = q.filter(CurriculumItem.unit.ilike(f"%{unit}%"))
    return [_to_out(i) for i in q.order_by(CurriculumItem.id.desc()).all()]


@router.post("/outcomes", response_model=CurriculumItemOut, status_code=201)
def create_outcome(payload: CurriculumItemInput, db: Session = Depends(get_db)):
    """Create a curriculum outcome and auto-classify its Bloom level."""
    bloom_level = payload.bloom_level
    secondary = []
    confidence = None

    if not bloom_level:
        result = classify_bloom(payload.outcome_text)
        bloom_level = result["primary_bloom_level"]
        secondary = result["secondary_levels"]
        confidence = result["confidence"]
        logger.info("curriculum.bloom_auto_classified", level=bloom_level, confidence=confidence)

    item = CurriculumItem(
        subject=payload.subject,
        grade=payload.grade,
        unit=payload.unit,
        outcome_text=payload.outcome_text,
        bloom_level=bloom_level,
        secondary_bloom_levels=secondary,
        bloom_confidence=confidence,
        created_at=datetime.utcnow(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_out(item)


@router.get("/outcomes/{id}", response_model=CurriculumItemOut)
def get_outcome(id: int, db: Session = Depends(get_db)):
    """Get a single curriculum outcome by ID."""
    item = db.query(CurriculumItem).filter(CurriculumItem.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Outcome not found")
    return _to_out(item)
