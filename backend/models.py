"""Data models for the financial news radar system."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    """Raw news article from a source."""
    
    id: str
    title: str
    content: str
    url: str
    source: str
    published_at: datetime
    author: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class Entity(BaseModel):
    """Financial entity mentioned in news."""
    
    name: str
    type: str  # company, ticker, sector, country, person
    relevance: float = Field(ge=0.0, le=1.0)
    ticker: Optional[str] = None


class TimelineEvent(BaseModel):
    """Event in the news timeline."""
    
    timestamp: datetime
    description: str
    source_url: str
    event_type: str  # first_mention, confirmation, update, correction


class HotnessScore(BaseModel):
    """Detailed hotness scoring."""
    
    overall: float = Field(ge=0.0, le=1.0, description="Overall hotness score")
    unexpectedness: float = Field(ge=0.0, le=1.0, description="How unexpected is this news")
    materiality: float = Field(ge=0.0, le=1.0, description="Impact on price/volatility")
    velocity: float = Field(ge=0.0, le=1.0, description="Speed of spread")
    breadth: float = Field(ge=0.0, le=1.0, description="Number of affected assets")
    credibility: float = Field(ge=0.0, le=1.0, description="Source credibility")
    reasoning: str = Field(description="Explanation of the scoring")


class NewsStory(BaseModel):
    """Processed news story with analysis."""
    
    id: str
    headline: str
    hotness: float = Field(ge=0.0, le=1.0)
    hotness_details: HotnessScore
    why_now: str
    entities: List[Entity]
    sources: List[str]
    timeline: List[TimelineEvent]
    draft: str
    dedup_group: str
    created_at: datetime = Field(default_factory=datetime.now)
    article_count: int = Field(default=1, description="Number of articles in cluster")
    has_deep_research: bool = Field(default=False, description="Whether deep research was conducted")
    research_summary: Optional[str] = Field(default=None, description="Summary from deep research")
    

class HotnessAnalysis(BaseModel):
    """Complete hotness analysis output from LLM."""
    
    hotness: HotnessScore
    entities: List[Entity]
    timeline: List[TimelineEvent]
    why_now: str = Field(description="1-2 sentences explaining immediate significance")
    headline: str = Field(description="Concise headline summarizing the story")


class RadarResponse(BaseModel):
    """Response from the radar system."""
    
    stories: List[NewsStory]
    total_articles_processed: int
    time_window_hours: int
    generated_at: datetime = Field(default_factory=datetime.now)
    processing_time_seconds: float


# ============================================================================
# Personal News Aggregator Models
# ============================================================================

class PersonalNewsItem(BaseModel):
    """Single news item for personal feed."""
    
    id: str
    title: str
    summary: str = Field(description="2-3 sentence summary of the article")
    url: str
    source: str
    published_at: datetime
    author: Optional[str] = None
    image_url: Optional[str] = None
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Relevance to user preferences")
    matched_keywords: List[str] = Field(default_factory=list, description="Keywords that matched")
    cluster_size: int = Field(default=1, description="Number of duplicate articles")


class UserPreferences(BaseModel):
    """User preferences for personal news aggregator."""
    
    user_id: str
    sources: List[str] = Field(default_factory=list, description="RSS feed URLs")
    keywords: List[str] = Field(default_factory=list, description="Keywords to prioritize")
    excluded_keywords: List[str] = Field(default_factory=list, description="Keywords to filter out")
    categories: List[str] = Field(default_factory=list, description="News categories of interest")
    update_frequency_minutes: int = Field(default=60, ge=5, le=1440, description="Update frequency in minutes")
    max_articles_per_feed: int = Field(default=20, ge=5, le=100, description="Max articles to show")
    language: str = Field(default="ru", description="Preferred language")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PersonalFeedResponse(BaseModel):
    """Response from personal news aggregator."""
    
    items: List[PersonalNewsItem]
    total_articles_processed: int
    filtered_count: int = Field(description="Articles filtered by preferences")
    time_window_hours: int
    generated_at: datetime = Field(default_factory=datetime.now)
    processing_time_seconds: float
    user_id: Optional[str] = None

