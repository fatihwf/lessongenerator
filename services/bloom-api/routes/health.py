"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
def health_check():
    """Return server health status."""
    return {"status": "ok"}
