"""
LLM-based lesson generator.

Combines CAG teaching context + RAG retrieved chunks + learner profile
to produce a structured, Bloom-aligned lesson via an OpenAI-compatible API.
Marks any claim not grounded in RAG sources explicitly.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional

import httpx

from bloom.classifier import get_bloom_prompt_strategy
from config import settings
from logger import logger


SECTION_KEYS = [
    "introduction",
    "explanation",
    "examples",
    "practice",
    "misconceptions",
    "summary",
    "assessment",
]


def _build_system_prompt(bloom_level: str) -> str:
    """Build the system prompt based on Bloom taxonomy level."""
    strategy = get_bloom_prompt_strategy(bloom_level)
    return (
        "You are an expert curriculum designer and pedagogical specialist. "
        "You generate structured, high-quality lesson content aligned to the "
        "revised Bloom's taxonomy. \n\n"
        "IMPORTANT: You MUST generate all content in TURKISH language. "
        "All explanations, examples, and questions must be in Turkish.\n\n"
        f"For this lesson, the Bloom level is '{bloom_level}'. "
        f"Strategy: {strategy}\n\n"
        "IMPORTANT RULES:\n"
        "- Do NOT fabricate facts. If you state something not in the provided sources, "
        "prefix it with [INFERRED].\n"
        "- Keep the language complexity appropriate for the learner's level.\n"
        "- Return ONLY valid JSON in the exact schema requested. No markdown, no code blocks.\n"
        "- Do not exceed the Bloom level in your explanations."
    )


def _build_user_prompt(
    outcome: Any,
    profile: Any,
    rag_chunks: List[Dict],
    bloom_level: str,
    teaching_context: Optional[Dict],
) -> str:
    """
    Build the user-facing prompt combining all inputs.

    Args:
        outcome: CurriculumItem ORM object.
        profile: LearnerProfile ORM object.
        rag_chunks: Retrieved knowledge chunks.
        bloom_level: Target Bloom level.
        teaching_context: Optional cached teaching context.

    Returns:
        Formatted prompt string.
    """
    sources_text = "\n\n".join(
        f"[Source {i+1} | {c['source_type']}]:\n{c['content']}"
        for i, c in enumerate(rag_chunks[:5])
    ) if rag_chunks else "No external sources available. Generate from pedagogical knowledge only; mark inferences with [INFERRED]."

    profile_summary = (
        f"Grade: {profile.grade}, "
        f"Proficiency: {profile.proficiency_level}, "
        f"Reading Level: {profile.reading_level or 'standard'}, "
        f"Preferred Style: {profile.preferred_style or 'mixed'}, "
        f"Weak Topics: {', '.join(profile.weak_topics) if profile.weak_topics else 'none'}, "
        f"Strong Topics: {', '.join(profile.strong_topics) if profile.strong_topics else 'none'}"
    )

    ctx_note = ""
    if teaching_context:
        ctx_note = f"\n\nTeaching context hints:\n{json.dumps(teaching_context, ensure_ascii=False)}"

    return f"""Generate a complete lesson for the following curriculum outcome.

OUTCOME:
Subject: {outcome.subject}
Grade: {outcome.grade}
Unit: {outcome.unit}
Outcome: {outcome.outcome_text}
Target Bloom Level: {bloom_level}

LEARNER PROFILE:
{profile_summary}
{ctx_note}

KNOWLEDGE SOURCES:
{sources_text}

OUTPUT FORMAT (return ONLY this JSON, no extra text):
{{
  "lesson_title": "string",
  "bloom_map": ["list", "of", "bloom", "verbs", "used"],
  "personalization_summary": {{
    "adapted_for": "string describing adaptation",
    "style_notes": "string",
    "scaffolding": "string"
  }},
  "sections": {{
    "introduction": "string (1-2 paragraphs)",
    "explanation": "string (2-4 paragraphs, Bloom-level aligned)",
    "examples": ["example 1", "example 2", "example 3"],
    "practice": ["practice question 1", "practice question 2", "practice question 3"],
    "misconceptions": ["common misconception and clarification 1", "misconception 2"],
    "summary": "string (key takeaways, 1 paragraph)",
    "assessment": ["assessment question 1", "assessment question 2", "assessment question 3"]
  }},
  "sources_used": ["Source 1 description", "Source 2 description"]
}}"""


async def generate_lesson_content(
    outcome: Any,
    profile: Any,
    rag_chunks: List[Dict],
    bloom_level: str,
    teaching_context: Optional[Dict] = None,
) -> Dict:
    """
    Generate structured lesson content via LLM.

    Args:
        outcome: CurriculumItem ORM object.
        profile: LearnerProfile ORM object.
        rag_chunks: Retrieved and ranked knowledge chunks.
        bloom_level: Target Bloom taxonomy level.
        teaching_context: Optional cached teaching context from CAG.

    Returns:
        Dict with lesson_title, bloom_map, personalization_summary, sections, sources_used.

    Raises:
        RuntimeError: If LLM call fails and fallback generation also fails.
    """
    system_prompt = _build_system_prompt(bloom_level)
    user_prompt = _build_user_prompt(outcome, profile, rag_chunks, bloom_level, teaching_context)

    logger.info(
        "generation.llm.call",
        outcome_id=outcome.id,
        profile_id=profile.id,
        bloom_level=bloom_level,
        model=settings.openai_model,
    )

    if not settings.openai_api_key or settings.openai_api_key.strip() == "":
        logger.error("generation.llm.error", error="API key is missing or empty", outcome_id=outcome.id)
        return _fallback_lesson(outcome, profile, bloom_level, rag_chunks, "API anahtarı bulunamadı (.env dosyasını kontrol edin)")

    try:
        api_key = settings.openai_api_key.strip()
        
        # 'Bearer ' prefix'inin tekrarlanmasını veya yanlış oluşmasını engelle
        if api_key.startswith("Bearer "):
            auth_value = api_key
        else:
            auth_value = f"Bearer {api_key}"

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.openai_base_url}/chat/completions",
                headers={
                    "Authorization": auth_value,
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/OpenRouterTeam/openrouter-runner",
                    "X-Title": "Bloom Lesson Generator",
                },
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3000,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            data = response.json()
            raw_content = data["choices"][0]["message"]["content"]
            lesson_data = json.loads(raw_content)
            lesson_data["generation_info"] = {
                "source": "LLM",
                "model": settings.openai_model,
                "timestamp": logger.info("generation.llm.success", outcome_id=outcome.id) or ""
            }
            logger.info("generation.llm.success", outcome_id=outcome.id)
            return lesson_data

    except Exception as exc:
        error_msg = str(exc)
        if isinstance(exc, httpx.HTTPStatusError):
            try:
                error_msg += f" | Body: {exc.response.text}"
            except:
                pass
        logger.error("generation.llm.error", error=error_msg, outcome_id=outcome.id)
        return _fallback_lesson(outcome, profile, bloom_level, rag_chunks, error_msg)


def _fallback_lesson(
    outcome: Any,
    profile: Any,
    bloom_level: str,
    rag_chunks: List[Dict],
    error_msg: Optional[str] = None,
) -> Dict:
    """
    Generate a minimal fallback lesson without LLM when the API call fails.

    This ensures the system always returns a usable response.
    """
    strategy = get_bloom_prompt_strategy(bloom_level)
    sources = [c["content"][:120] + "..." for c in rag_chunks[:2]]

    return {
        "lesson_title": f"{outcome.subject}: {outcome.unit} ({bloom_level.capitalize()} Level)",
        "bloom_map": [bloom_level, "recall", "apply"],
        "personalization_summary": {
            "adapted_for": f"Grade {profile.grade}, {profile.proficiency_level} proficiency",
            "style_notes": profile.preferred_style or "Mixed modality",
            "scaffolding": "Standard scaffolding applied",
        },
        "sections": {
            "introduction": (
                f"[INFERRED] This lesson addresses the outcome: {outcome.outcome_text}. "
                f"It is designed for Grade {profile.grade} students at {profile.proficiency_level} proficiency."
            ),
            "explanation": (
                f"[INFERRED] {strategy} "
                f"The core concept relates to: {outcome.outcome_text}"
            ),
            "examples": [
                f"[INFERRED] Example 1 related to {outcome.unit}",
                f"[INFERRED] Example 2 applying the concept",
                f"[INFERRED] Example 3 in a real-world context",
            ],
            "practice": [
                f"Practice: Demonstrate understanding of {outcome.outcome_text}",
                f"Practice: Apply the concept to a new situation",
                f"Practice: Reflect on what you learned",
            ],
            "misconceptions": [
                f"[INFERRED] A common misconception about this topic and its clarification",
            ],
            "summary": (
                f"[INFERRED] Key takeaways from this lesson on {outcome.unit}: "
                f"{outcome.outcome_text}"
            ),
            "assessment": [
                f"Assessment question 1: Explain {outcome.outcome_text} in your own words.",
                f"Assessment question 2: Give an example from your experience.",
                f"Assessment question 3: How would you apply this knowledge?",
            ],
        },
        "sources_used": sources if sources else ["[INFERRED] Generated from pedagogical knowledge"],
        "generation_info": {
            "source": "FALLBACK",
            "model": "rule-based-engine",
            "note": "AI servisi şu an kullanılamıyor (API anahtarı sorunu veya servis kesintisi). Kural tabanlı motor ile içerik üretildi.",
            "error_detail": _clean_error_msg(error_msg)
        }
    }


def _clean_error_msg(msg: Optional[str]) -> str:
    """Teknik hata mesajlarını kullanıcı dostu hale getirir."""
    if not msg:
        return "Bilinmeyen hata"
    
    if "Bearer" in msg or "Illegal header" in msg:
        return "API Anahtarı geçersiz veya hatalı formatlanmış (Bearer sorunu). Lütfen .env dosyasını kontrol edin."
    if "401" in msg:
        return "API yetkilendirme hatası (401). Anahtarın geçerli olduğundan emin olun."
    if "429" in msg:
        return "API kota sınırı aşıldı veya çok fazla istek gönderildi (429)."
    
    return msg

