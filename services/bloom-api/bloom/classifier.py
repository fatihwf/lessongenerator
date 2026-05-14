"""
Bloom taxonomy classifier.

Classifies learning outcome text into the revised Bloom taxonomy levels:
Remembering, Understanding, Applying, Analyzing, Evaluating, Creating.

MVP uses keyword matching + LLM refinement when available.
"""
from __future__ import annotations
import re
from typing import List, Optional, Tuple

BLOOM_LEVELS = [
    "remembering",
    "understanding",
    "applying",
    "analyzing",
    "evaluating",
    "creating",
]

BLOOM_KEYWORDS: dict[str, List[str]] = {
    "remembering": [
        "tanımla", "listele", "hatırla", "isimlendır", "belirle", "etiketle",
        "ifade et", "tekrar et", "tanı", "say", "göster", "seç", "kopyala",
        "define", "list", "recall", "name", "identify", "label", "state",
        "match", "recognize", "repeat", "cite", "duplicate", "memorize",
        "record", "relate", "reproduce", "tabulate", "underline",
    ],
    "understanding": [
        "açıkla", "özetle", "sınıflandır", "karşılaştır", "yorumla",
        "çevir", "betimle", "tartış", "anlat", "genişlet", "örnekle",
        "explain", "describe", "summarize", "classify", "compare",
        "interpret", "translate", "outline", "discuss", "distinguish",
        "estimate", "exemplify", "generalize", "paraphrase", "predict",
        "restate", "review", "infer",
    ],
    "applying": [
        "uygula", "göster", "kullan", "çöz", "hesapla", "yürüt", "gerçekleştir",
        "apply", "demonstrate", "use", "solve", "calculate", "practice",
        "illustrate", "implement", "execute", "carry out", "construct",
        "compute", "develop", "experiment", "modify", "operate", "produce",
    ],
    "analyzing": [
        "analiz et", "incele", "düzenle", "parçalara ayır", "karşılaştır",
        "birleştir", "ayırt et", "sorgula", "test et",
        "analyze", "differentiate", "examine", "organize", "break down",
        "distinguish", "inspect", "integrate", "separate", "categorize",
        "compare", "contrast", "deconstruct", "diagram", "test", "question",
    ],
    "evaluating": [
        "değerlendir", "yargıla", "gerekçelendir", "değer biç", "eleştir",
        "savun", "tartış", "tartmak", "ölçmek",
        "evaluate", "judge", "justify", "assess", "criticize",
        "defend", "argue", "recommend", "critique", "appraise",
        "debate", "decide", "prioritize", "rate", "support", "value",
    ],
    "creating": [
        "oluştur", "tasarla", "geliştir", "planla", "üret", "formüle et",
        "yaz", "inşa et", "dene", "yeni bir şey yap",
        "create", "design", "compose", "plan", "construct",
        "develop", "formulate", "generate", "produce", "build",
        "assemble", "devise", "hypothesize", "invent", "make", "originate",
    ],
}


def classify_bloom(text: str, context: Optional[str] = None) -> dict:
    """
    Classify text into a Bloom taxonomy level using keyword matching.

    Args:
        text: The learning outcome or text to classify.
        context: Optional additional context.

    Returns:
        Dict with primary_bloom_level, secondary_levels, confidence, reasoning, keywords_matched.
    """
    text_lower = text.lower()

    level_scores: dict[str, float] = {level: 0.0 for level in BLOOM_LEVELS}
    all_matched: dict[str, List[str]] = {level: [] for level in BLOOM_LEVELS}

    for level, keywords in BLOOM_KEYWORDS.items():
        for kw in keywords:
            pattern = r"\b" + re.escape(kw) + r"\b"
            matches = re.findall(pattern, text_lower)
            if matches:
                level_scores[level] += len(matches)
                all_matched[level].extend(matches)

    total = sum(level_scores.values())

    if total == 0:
        primary = "understanding"
        confidence = 0.4
        reasoning = "No Bloom-specific keywords found. Defaulting to 'understanding' level."
        return {
            "primary_bloom_level": primary,
            "secondary_levels": [],
            "confidence": confidence,
            "reasoning": reasoning,
            "keywords_matched": [],
        }

    sorted_levels = sorted(level_scores.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_levels[0][0]
    primary_score = sorted_levels[0][1]
    confidence = min(primary_score / total + 0.3, 0.95)

    secondary = [lvl for lvl, score in sorted_levels[1:3] if score > 0]
    matched_kws = all_matched[primary]

    reasoning = _build_reasoning(primary, matched_kws, text)

    return {
        "primary_bloom_level": primary,
        "secondary_levels": secondary,
        "confidence": round(confidence, 2),
        "reasoning": reasoning,
        "keywords_matched": matched_kws[:10],
    }


def _build_reasoning(level: str, keywords: List[str], text: str) -> str:
    """Build a human-readable reasoning string for the classification."""
    level_descriptions = {
        "remembering": "retrieving, recognizing, and recalling relevant knowledge from memory",
        "understanding": "constructing meaning from instructional messages including oral, written, and graphic communication",
        "applying": "carrying out or using a procedure in a given situation",
        "analyzing": "breaking material into its constituent parts and detecting how the parts relate to one another",
        "evaluating": "making judgments based on criteria and standards",
        "creating": "putting elements together to form a coherent or functional whole",
    }

    kw_str = ", ".join(f'"{k}"' for k in keywords[:3]) if keywords else "contextual signals"
    desc = level_descriptions.get(level, level)
    return (
        f"Classified as '{level}' because the outcome involves {desc}. "
        f"Key indicator terms found: {kw_str}."
    )


def get_bloom_prompt_strategy(bloom_level: str) -> str:
    """
    Return the generation strategy description for a given Bloom level.

    Args:
        bloom_level: One of the six Bloom taxonomy levels.

    Returns:
        A string describing the pedagogical strategy for that level.
    """
    strategies = {
        "remembering": (
            "Focus on short definitions, fundamental facts, and listing. "
            "Use clear, concise language. Provide memory aids and repetition cues."
        ),
        "understanding": (
            "Focus on explanations, cause-and-effect relationships, and paraphrasing. "
            "Use analogies and relatable examples to build meaning."
        ),
        "applying": (
            "Focus on step-by-step procedures, worked examples, and problem-solving scenarios. "
            "Provide concrete situations where students apply the concept."
        ),
        "analyzing": (
            "Focus on comparisons, breakdowns of components, and identifying relationships. "
            "Use diagrams, contrast tables, and 'why does this work?' questions."
        ),
        "evaluating": (
            "Focus on justification, argument construction, and critical assessment. "
            "Present multiple perspectives and ask students to defend positions."
        ),
        "creating": (
            "Focus on open-ended projects, design challenges, and novel production tasks. "
            "Give students latitude to synthesize and generate new ideas."
        ),
    }
    return strategies.get(bloom_level.lower(), strategies["understanding"])
