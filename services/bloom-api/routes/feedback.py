"""Feedback endpoints."""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import FeedbackRecord, GeneratedLesson
from schemas import FeedbackInput, FeedbackRecordOut

router = APIRouter(prefix="/feedback", tags=["feedback"])


def _to_out(f: FeedbackRecord) -> FeedbackRecordOut:
    return FeedbackRecordOut(
        id=f.id,
        lesson_id=f.lesson_id,
        rating=f.rating,
        comment=f.comment,
        bloom_accuracy=f.bloom_accuracy,
        personalization_accuracy=f.personalization_accuracy,
        created_at=f.created_at.isoformat(),
    )


@router.get("", response_model=List[FeedbackRecordOut])
def list_feedback(db: Session = Depends(get_db)):
    """List all feedback records."""
    return [_to_out(f) for f in db.query(FeedbackRecord).order_by(FeedbackRecord.id.desc()).all()]


@router.post("", response_model=FeedbackRecordOut, status_code=201)
def submit_feedback(payload: FeedbackInput, db: Session = Depends(get_db)):
    """Submit feedback on a generated lesson."""
    lesson = db.query(GeneratedLesson).filter(GeneratedLesson.id == payload.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    fb = FeedbackRecord(
        lesson_id=payload.lesson_id,
        rating=payload.rating,
        comment=payload.comment,
        bloom_accuracy=payload.bloom_accuracy,
        personalization_accuracy=payload.personalization_accuracy,
        created_at=datetime.utcnow(),
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return _to_out(fb)
