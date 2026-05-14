"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── Curriculum ─────────────────────────────────────────────────────────────

class CurriculumItemInput(BaseModel):
    subject: str
    grade: str
    unit: str
    outcome_text: str
    bloom_level: Optional[str] = None


class CurriculumItemOut(BaseModel):
    id: int
    subject: str
    grade: str
    unit: str
    outcome_text: str
    bloom_level: str
    secondary_bloom_levels: List[str] = []
    bloom_confidence: Optional[float] = None
    created_at: str

    class Config:
        from_attributes = True


# ── Profiles ───────────────────────────────────────────────────────────────

class LearnerProfileInput(BaseModel):
    name: str
    grade: str
    proficiency_level: str
    reading_level: Optional[str] = None
    preferred_style: Optional[str] = None
    weak_topics: List[str] = []
    strong_topics: List[str] = []


class LearnerProfileUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    proficiency_level: Optional[str] = None
    reading_level: Optional[str] = None
    preferred_style: Optional[str] = None
    weak_topics: Optional[List[str]] = None
    strong_topics: Optional[List[str]] = None


class LearnerProfileOut(BaseModel):
    id: int
    name: str
    grade: str
    proficiency_level: str
    reading_level: Optional[str] = None
    preferred_style: Optional[str] = None
    weak_topics: List[str] = []
    strong_topics: List[str] = []
    created_at: str

    class Config:
        from_attributes = True


# ── Bloom ──────────────────────────────────────────────────────────────────

class BloomClassifyInput(BaseModel):
    text: str
    context: Optional[str] = None


class BloomAnnotationOut(BaseModel):
    primary_bloom_level: str
    secondary_levels: List[str] = []
    confidence: float
    reasoning: str
    keywords_matched: List[str] = []


# ── Knowledge Chunks ───────────────────────────────────────────────────────

class KnowledgeChunkInput(BaseModel):
    content: str
    source_type: str
    subject: str
    grade: Optional[str] = None
    unit: Optional[str] = None
    bloom_levels: List[str] = []
    source_name: Optional[str] = None


class KnowledgeChunkOut(BaseModel):
    id: int
    content: str
    source_type: str
    subject: str
    grade: Optional[str] = None
    unit: Optional[str] = None
    bloom_levels: List[str] = []
    source_name: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class RetrieveInput(BaseModel):
    query: str
    bloom_level: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[str] = None
    top_k: int = 5


class RetrievedChunkOut(BaseModel):
    chunk_id: int
    content: str
    score: float
    source_type: str
    bloom_levels: List[str] = []


# ── Lessons ────────────────────────────────────────────────────────────────

class LessonGenerateInput(BaseModel):
    outcome_id: int
    profile_id: int
    target_bloom_level: Optional[str] = None
    force_regenerate: bool = False


class LessonSections(BaseModel):
    introduction: str = ""
    explanation: str = ""
    examples: List[str] = []
    practice: List[str] = []
    misconceptions: List[str] = []
    summary: str = ""
    assessment: List[str] = []


class LessonSummaryOut(BaseModel):
    id: int
    lesson_title: str
    unit: str
    grade: str
    subject: str
    bloom_level: str
    profile_id: int
    cache_status: str
    created_at: str

    class Config:
        from_attributes = True


class RetrievalTraceOut(BaseModel):
    chunk_id: int
    content: str
    score: float
    bloom_match: bool
    source_type: str


class GeneratedLessonOut(BaseModel):
    id: int
    lesson_title: str
    unit: str
    grade: str
    subject: str
    bloom_level: str
    bloom_map: List[str] = []
    profile_id: int
    personalization_summary: Dict[str, Any] = {}
    sections: Dict[str, Any] = {}
    sources_used: List[str] = []
    generation_info: Optional[Dict[str, Any]] = None
    cache_status: str
    created_at: str

    class Config:
        from_attributes = True


class LessonStatsOut(BaseModel):
    total_lessons: int
    by_bloom_level: Dict[str, int]
    by_grade: Dict[str, int]
    cache_hit_rate: float
    avg_sources_used: float


# ── Feedback ───────────────────────────────────────────────────────────────

class FeedbackInput(BaseModel):
    lesson_id: int
    rating: int
    comment: Optional[str] = None
    bloom_accuracy: Optional[int] = None
    personalization_accuracy: Optional[int] = None


class FeedbackRecordOut(BaseModel):
    id: int
    lesson_id: int
    rating: int
    comment: Optional[str] = None
    bloom_accuracy: Optional[int] = None
    personalization_accuracy: Optional[int] = None
    created_at: str

    class Config:
        from_attributes = True
