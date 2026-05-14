"""Lesson generation and retrieval endpoints."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from cag.cache import context_cache
from database import get_db
from generation.generator import generate_lesson_content
from logger import logger
from models import CurriculumItem, GeneratedLesson, LearnerProfile
from rag.retriever import retrieve_chunks
from schemas import (
    GeneratedLessonOut,
    LessonGenerateInput,
    LessonStatsOut,
    LessonSummaryOut,
    RetrievalTraceOut,
)

router = APIRouter(prefix="/lessons", tags=["lessons"])


def _to_summary(l: GeneratedLesson) -> LessonSummaryOut:
    return LessonSummaryOut(
        id=l.id,
        lesson_title=l.lesson_title,
        unit=l.unit,
        grade=l.grade,
        subject=l.subject,
        bloom_level=l.bloom_level,
        profile_id=l.profile_id,
        cache_status=l.cache_status,
        created_at=l.created_at.isoformat(),
    )


def _to_full(l: GeneratedLesson) -> GeneratedLessonOut:
    return GeneratedLessonOut(
        id=l.id,
        lesson_title=l.lesson_title,
        unit=l.unit,
        grade=l.grade,
        subject=l.subject,
        bloom_level=l.bloom_level,
        bloom_map=l.bloom_map or [],
        profile_id=l.profile_id,
        personalization_summary=l.personalization_summary or {},
        sections=l.sections or {},
        sources_used=l.sources_used or [],
        generation_info=l.generation_info,
        cache_status=l.cache_status,
        created_at=l.created_at.isoformat(),
    )


@router.get("/stats", response_model=LessonStatsOut)
def get_lesson_stats(db: Session = Depends(get_db)):
    """Get lesson generation statistics."""
    lessons = db.query(GeneratedLesson).all()
    total = len(lessons)

    by_bloom: dict = {}
    by_grade: dict = {}
    cache_hits = 0
    total_sources = 0

    for l in lessons:
        by_bloom[l.bloom_level] = by_bloom.get(l.bloom_level, 0) + 1
        by_grade[l.grade] = by_grade.get(l.grade, 0) + 1
        if l.cache_status == "hit":
            cache_hits += 1
        total_sources += len(l.sources_used or [])

    return LessonStatsOut(
        total_lessons=total,
        by_bloom_level=by_bloom,
        by_grade=by_grade,
        cache_hit_rate=round(cache_hits / total, 2) if total else 0.0,
        avg_sources_used=round(total_sources / total, 1) if total else 0.0,
    )


@router.get("", response_model=List[LessonSummaryOut])
def list_lessons(
    profile_id: Optional[int] = Query(None),
    grade: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List generated lessons with optional filters."""
    q = db.query(GeneratedLesson)
    if profile_id:
        q = q.filter(GeneratedLesson.profile_id == profile_id)
    if grade:
        q = q.filter(GeneratedLesson.grade == grade)
    if subject:
        q = q.filter(GeneratedLesson.subject.ilike(f"%{subject}%"))
    return [_to_summary(l) for l in q.order_by(GeneratedLesson.id.desc()).all()]


@router.post("", response_model=GeneratedLessonOut, status_code=201)
async def generate_lesson(payload: LessonGenerateInput, db: Session = Depends(get_db)):
    """
    Generate a personalized, Bloom-aligned lesson.

    Flow:
    1. Validate outcome and profile exist.
    2. Determine target Bloom level.
    3. Check CAG cache for a teaching context.
    4. Run RAG retrieval filtered by Bloom level and subject.
    5. Call LLM with combined context.
    6. Persist and return result.
    """
    outcome = db.query(CurriculumItem).filter(CurriculumItem.id == payload.outcome_id).first()
    if not outcome:
        raise HTTPException(status_code=404, detail="Curriculum outcome not found")

    profile = db.query(LearnerProfile).filter(LearnerProfile.id == payload.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    bloom_level = payload.target_bloom_level or outcome.bloom_level

    if not payload.force_regenerate:
        existing = (
            db.query(GeneratedLesson)
            .filter(
                GeneratedLesson.outcome_id == payload.outcome_id,
                GeneratedLesson.profile_id == payload.profile_id,
                GeneratedLesson.bloom_level == bloom_level,
            )
            .order_by(GeneratedLesson.id.desc())
            .first()
        )
        if existing:
            logger.info("lessons.cache.db_hit", lesson_id=existing.id)
            existing.cache_status = "hit"
            return _to_full(existing)

    teaching_context = context_cache.get(
        grade=outcome.grade,
        unit=outcome.unit,
        outcome_id=outcome.id,
        bloom_level=bloom_level,
        profile=profile,
    )
    cache_status = "hit" if teaching_context else "miss"

    rag_results = retrieve_chunks(
        db=db,
        query=f"{outcome.outcome_text} {outcome.unit}",
        bloom_level=bloom_level,
        subject=outcome.subject,
        grade=outcome.grade,
        top_k=5,
    )

    logger.info(
        "lessons.generate.start",
        outcome_id=outcome.id,
        profile_id=profile.id,
        bloom_level=bloom_level,
        rag_chunks=len(rag_results),
    )

    lesson_data = await generate_lesson_content(
        outcome=outcome,
        profile=profile,
        rag_chunks=rag_results,
        bloom_level=bloom_level,
        teaching_context=teaching_context,
    )

    if not teaching_context:
        new_context = {
            "outcome": outcome.outcome_text,
            "bloom_level": bloom_level,
            "grade": outcome.grade,
            "strategy": lesson_data.get("personalization_summary", {}),
        }
        context_cache.set(
            grade=outcome.grade,
            unit=outcome.unit,
            outcome_id=outcome.id,
            bloom_level=bloom_level,
            profile=profile,
            context=new_context,
        )

    retrieval_trace = [
        {
            "chunk_id": r["chunk_id"],
            "content": r["content"][:200],
            "score": r["score"],
            "bloom_match": r["bloom_match"],
            "source_type": r["source_type"],
        }
        for r in rag_results
    ]

    sections_data = lesson_data.get("sections", {})

    lesson = GeneratedLesson(
        lesson_title=lesson_data.get("lesson_title", f"{outcome.subject}: {outcome.unit}"),
        unit=outcome.unit,
        grade=outcome.grade,
        subject=outcome.subject,
        bloom_level=bloom_level,
        bloom_map=lesson_data.get("bloom_map", [bloom_level]),
        outcome_id=outcome.id,
        profile_id=profile.id,
        personalization_summary=lesson_data.get("personalization_summary", {}),
        sections=sections_data,
        sources_used=lesson_data.get("sources_used", []),
        retrieval_trace=retrieval_trace,
        generation_info=lesson_data.get("generation_info"),
        cache_status=cache_status,
        created_at=datetime.utcnow(),
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    logger.info("lessons.generate.done", lesson_id=lesson.id, cache_status=cache_status)
    return _to_full(lesson)


@router.get("/{id}", response_model=GeneratedLessonOut)
def get_lesson(id: int, db: Session = Depends(get_db)):
    """Get a generated lesson by ID."""
    lesson = db.query(GeneratedLesson).filter(GeneratedLesson.id == id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return _to_full(lesson)


@router.get("/{id}/trace", response_model=List[RetrievalTraceOut])
def get_lesson_trace(id: int, db: Session = Depends(get_db)):
    """Get retrieval trace for a lesson."""
    lesson = db.query(GeneratedLesson).filter(GeneratedLesson.id == id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return [
        RetrievalTraceOut(
            chunk_id=t["chunk_id"],
            content=t["content"],
            score=t["score"],
            bloom_match=t["bloom_match"],
            source_type=t["source_type"],
        )
        for t in (lesson.retrieval_trace or [])
    ]
