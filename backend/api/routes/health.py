"""Health check endpoints."""

import logging
from fastapi import APIRouter

from config import settings
from api.schemas import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        google_api_configured=bool(settings.google_api_key)
    )

