"""Request and response schemas for API endpoints."""

from typing import Optional, List
from pydantic import BaseModel


class ProcessRequest(BaseModel):
    """Request model for processing news."""
    time_window_hours: Optional[int] = 24
    top_k: Optional[int] = 10
    hotness_threshold: Optional[float] = 0.5
    custom_feeds: Optional[List[str]] = None


class PersonalScanRequest(BaseModel):
    """Request model for personal news scan."""
    user_id: str = "default"
    time_window_hours: Optional[int] = 24
    custom_sources: Optional[List[str]] = None


class InteractionRequest(BaseModel):
    """Request model for tracking user interactions."""
    user_id: str
    article_id: str
    interaction_type: str  # 'view', 'click', 'like', 'dislike', 'save'
    view_duration_seconds: Optional[int] = None
    scroll_depth: Optional[float] = None
    clicked_read_more: bool = False
    matched_keywords: Optional[List[str]] = None
    relevance_score: Optional[float] = None


class OnboardingCompleteRequest(BaseModel):
    """Request for completing onboarding."""
    user_id: str
    preset_key: Optional[str] = None
    categories: List[str]
    keywords: List[str]
    sources: List[str]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    google_api_configured: bool

