"""
CAG (Cache-Augmented Generation) module.

The cache stores teaching contexts — not raw LLM outputs — keyed by a
composite signature of grade, unit, outcome, Bloom level, learner profile
signature, and content type. This allows similar profiles to reuse
pedagogical context while still personalizing the final output.

MVP: In-memory TTL cache. Future: Redis.
"""
from __future__ import annotations
import hashlib
import json
import time
from typing import Any, Dict, Optional

from logger import logger


class TeachingContextCache:
    """
    In-memory teaching context cache with TTL support.

    Cache key encodes: grade + unit + outcome_id + bloom_level +
    profile_signature + difficulty.
    """

    def __init__(self, ttl_seconds: int = 3600):
        self._store: Dict[str, Dict] = {}
        self._ttl = ttl_seconds

    def _build_key(
        self,
        grade: str,
        unit: str,
        outcome_id: int,
        bloom_level: str,
        profile_signature: str,
        difficulty: str = "standard",
    ) -> str:
        """
        Build a deterministic cache key from teaching context parameters.

        Args:
            grade: Student grade level.
            unit: Curriculum unit.
            outcome_id: Curriculum item ID.
            bloom_level: Target Bloom level.
            profile_signature: Hash of the learner profile.
            difficulty: Difficulty modifier.

        Returns:
            SHA-256 hex digest of the combined key.
        """
        raw = f"{grade}|{unit}|{outcome_id}|{bloom_level}|{profile_signature}|{difficulty}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _profile_signature(self, profile: Any) -> str:
        """
        Generate a compact signature for a learner profile.

        Only includes fields that materially affect pedagogy.
        """
        sig_data = {
            "grade": getattr(profile, "grade", ""),
            "proficiency": getattr(profile, "proficiency_level", ""),
            "style": getattr(profile, "preferred_style", "") or "",
            "weak": sorted(getattr(profile, "weak_topics", []) or []),
        }
        return hashlib.md5(json.dumps(sig_data, sort_keys=True).encode()).hexdigest()[:8]

    def get(
        self,
        grade: str,
        unit: str,
        outcome_id: int,
        bloom_level: str,
        profile: Any,
    ) -> Optional[Dict]:
        """
        Look up a teaching context in cache.

        Args:
            grade: Student grade.
            unit: Curriculum unit.
            outcome_id: Curriculum item ID.
            bloom_level: Bloom level.
            profile: LearnerProfile ORM object.

        Returns:
            Cached context dict, or None on cache miss.
        """
        sig = self._profile_signature(profile)
        key = self._build_key(grade, unit, outcome_id, bloom_level, sig)
        entry = self._store.get(key)

        if entry is None:
            logger.info("cag.cache.miss", key=key[:16])
            return None

        if time.time() > entry["expires_at"]:
            del self._store[key]
            logger.info("cag.cache.expired", key=key[:16])
            return None

        logger.info("cag.cache.hit", key=key[:16])
        return entry["context"]

    def set(
        self,
        grade: str,
        unit: str,
        outcome_id: int,
        bloom_level: str,
        profile: Any,
        context: Dict,
    ) -> str:
        """
        Store a teaching context in cache.

        Args:
            grade: Student grade.
            unit: Curriculum unit.
            outcome_id: Curriculum item ID.
            bloom_level: Bloom level.
            profile: LearnerProfile ORM object.
            context: The teaching context dict to cache.

        Returns:
            The cache key used.
        """
        sig = self._profile_signature(profile)
        key = self._build_key(grade, unit, outcome_id, bloom_level, sig)
        self._store[key] = {
            "context": context,
            "expires_at": time.time() + self._ttl,
        }
        logger.info("cag.cache.set", key=key[:16], ttl=self._ttl)
        return key

    def invalidate(self, key: str) -> None:
        """Remove a specific cache entry."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._store.clear()

    def size(self) -> int:
        """Return number of active (non-expired) cache entries."""
        now = time.time()
        return sum(1 for v in self._store.values() if v["expires_at"] > now)


context_cache = TeachingContextCache()
