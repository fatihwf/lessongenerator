"""Learner profile endpoints."""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import LearnerProfile
from schemas import LearnerProfileInput, LearnerProfileOut, LearnerProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _to_out(p: LearnerProfile) -> LearnerProfileOut:
    return LearnerProfileOut(
        id=p.id,
        name=p.name,
        grade=p.grade,
        proficiency_level=p.proficiency_level,
        reading_level=p.reading_level,
        preferred_style=p.preferred_style,
        weak_topics=p.weak_topics or [],
        strong_topics=p.strong_topics or [],
        created_at=p.created_at.isoformat(),
    )


@router.get("", response_model=List[LearnerProfileOut])
def list_profiles(db: Session = Depends(get_db)):
    """List all learner profiles."""
    return [_to_out(p) for p in db.query(LearnerProfile).order_by(LearnerProfile.id.desc()).all()]


@router.post("", response_model=LearnerProfileOut, status_code=201)
def create_profile(payload: LearnerProfileInput, db: Session = Depends(get_db)):
    """Create a new learner profile."""
    profile = LearnerProfile(
        name=payload.name,
        grade=payload.grade,
        proficiency_level=payload.proficiency_level,
        reading_level=payload.reading_level,
        preferred_style=payload.preferred_style,
        weak_topics=payload.weak_topics or [],
        strong_topics=payload.strong_topics or [],
        created_at=datetime.utcnow(),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _to_out(profile)


@router.get("/{id}", response_model=LearnerProfileOut)
def get_profile(id: int, db: Session = Depends(get_db)):
    """Get a learner profile by ID."""
    p = db.query(LearnerProfile).filter(LearnerProfile.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _to_out(p)


@router.patch("/{id}", response_model=LearnerProfileOut)
def update_profile(id: int, payload: LearnerProfileUpdate, db: Session = Depends(get_db)):
    """Update a learner profile."""
    p = db.query(LearnerProfile).filter(LearnerProfile.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(p, field, value)
    db.commit()
    db.refresh(p)
    return _to_out(p)
