"""Bloom taxonomy classification endpoint."""
from fastapi import APIRouter

from bloom.classifier import classify_bloom
from schemas import BloomAnnotationOut, BloomClassifyInput

router = APIRouter(prefix="/bloom", tags=["bloom"])


@router.post("/classify", response_model=BloomAnnotationOut)
def classify_bloom_endpoint(payload: BloomClassifyInput):
    """Classify text into a Bloom taxonomy level."""
    result = classify_bloom(payload.text, payload.context)
    return BloomAnnotationOut(**result)
