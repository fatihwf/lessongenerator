"""SQLAlchemy ORM models."""
import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, JSON,
)
from sqlalchemy.orm import relationship
from database import Base


class CurriculumItem(Base):
    """A curriculum learning outcome with Bloom annotation."""

    __tablename__ = "curriculum_items"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(100), nullable=False)
    grade = Column(String(20), nullable=False)
    unit = Column(String(200), nullable=False)
    outcome_text = Column(Text, nullable=False)
    bloom_level = Column(String(50), nullable=False, default="understanding")
    secondary_bloom_levels = Column(JSON, nullable=False, default=list)
    bloom_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lessons = relationship("GeneratedLesson", back_populates="curriculum_item")


class LearnerProfile(Base):
    """Learner profile with mastery and preferences."""

    __tablename__ = "learner_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    grade = Column(String(20), nullable=False)
    proficiency_level = Column(String(50), nullable=False, default="intermediate")
    reading_level = Column(String(50), nullable=True)
    preferred_style = Column(String(100), nullable=True)
    weak_topics = Column(JSON, nullable=False, default=list)
    strong_topics = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lessons = relationship("GeneratedLesson", back_populates="learner_profile")


class KnowledgeChunk(Base):
    """A piece of knowledge for RAG retrieval."""

    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    source_type = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    grade = Column(String(20), nullable=True)
    unit = Column(String(200), nullable=True)
    bloom_levels = Column(JSON, nullable=False, default=list)
    source_name = Column(String(200), nullable=True)
    tfidf_tokens = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class GeneratedLesson(Base):
    """A generated lesson with all sections."""

    __tablename__ = "generated_lessons"

    id = Column(Integer, primary_key=True, index=True)
    lesson_title = Column(String(300), nullable=False)
    unit = Column(String(200), nullable=False)
    grade = Column(String(20), nullable=False)
    subject = Column(String(100), nullable=False)
    bloom_level = Column(String(50), nullable=False)
    bloom_map = Column(JSON, nullable=False, default=list)
    outcome_id = Column(Integer, ForeignKey("curriculum_items.id"), nullable=False)
    profile_id = Column(Integer, ForeignKey("learner_profiles.id"), nullable=False)
    personalization_summary = Column(JSON, nullable=False, default=dict)
    sections = Column(JSON, nullable=False, default=dict)
    sources_used = Column(JSON, nullable=False, default=list)
    retrieval_trace = Column(JSON, nullable=False, default=list)
    generation_info = Column(JSON, nullable=True)
    cache_status = Column(String(10), nullable=False, default="miss")
    cache_key = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    curriculum_item = relationship("CurriculumItem", back_populates="lessons")
    learner_profile = relationship("LearnerProfile", back_populates="lessons")
    feedback = relationship("FeedbackRecord", back_populates="lesson")


class FeedbackRecord(Base):
    """User feedback on a generated lesson."""

    __tablename__ = "feedback_records"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("generated_lessons.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    bloom_accuracy = Column(Integer, nullable=True)
    personalization_accuracy = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lesson = relationship("GeneratedLesson", back_populates="feedback")
