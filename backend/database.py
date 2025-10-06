"""Database models and connection for storing radar results."""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy.pool import NullPool

from config import settings

Base = declarative_base()


class RadarRun(Base):
    """Represents a single radar processing run."""
    
    __tablename__ = "radar_runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)
    time_window_hours = Column(Integer, nullable=False)
    total_articles_processed = Column(Integer, nullable=False)
    processing_time_seconds = Column(Float, nullable=False)
    hotness_threshold = Column(Float, nullable=False)
    top_k = Column(Integer, nullable=False)
    
    # Relationships
    stories = relationship("StoryDB", back_populates="radar_run", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "time_window_hours": self.time_window_hours,
            "total_articles_processed": self.total_articles_processed,
            "processing_time_seconds": self.processing_time_seconds,
            "hotness_threshold": self.hotness_threshold,
            "top_k": self.top_k,
            "story_count": len(self.stories) if self.stories else 0
        }


class StoryDB(Base):
    """Represents a news story from radar processing."""
    
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    radar_run_id = Column(Integer, ForeignKey("radar_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Story data
    story_id = Column(String(100), nullable=False)  # cluster_0001, etc.
    headline = Column(Text, nullable=False)
    hotness = Column(Float, nullable=False, index=True)
    why_now = Column(Text, nullable=False)
    draft = Column(Text, nullable=False)
    dedup_group = Column(String(100), nullable=False)
    article_count = Column(Integer, default=1)
    
    # Complex fields stored as JSON
    hotness_details = Column(JSON, nullable=False)
    entities = Column(JSON, nullable=False)
    sources = Column(JSON, nullable=False)
    timeline = Column(JSON, nullable=False)
    
    # Deep research fields
    has_deep_research = Column(Boolean, default=False)
    research_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    radar_run = relationship("RadarRun", back_populates="stories")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary matching NewsStory model."""
        return {
            "id": self.story_id,
            "headline": self.headline,
            "hotness": self.hotness,
            "hotness_details": self.hotness_details,
            "why_now": self.why_now,
            "entities": self.entities,
            "sources": self.sources,
            "timeline": self.timeline,
            "draft": self.draft,
            "dedup_group": self.dedup_group,
            "article_count": self.article_count,
            "has_deep_research": self.has_deep_research,
            "research_summary": self.research_summary,
            "created_at": self.created_at.isoformat()
        }


class DatabaseManager:
    """Manager for database operations."""
    
    def __init__(self):
        """Initialize database manager."""
        self.database_url = settings.database_url
        self.engine = None
        self.session_maker = None
    
    def init_sync(self):
        """Initialize synchronous engine."""
        if not self.engine:
            # Synchronous engine for initialization
            sync_url = self.database_url.replace("postgresql+asyncpg://", "postgresql://")
            self.engine = create_engine(sync_url, echo=False)
            Base.metadata.create_all(self.engine)
    
    async def init_async(self):
        """Initialize async engine and session maker."""
        if not self.session_maker:
            engine = create_async_engine(
                self.database_url,
                echo=False,
                poolclass=NullPool
            )
            
            # Create tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self.session_maker = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
    
    @asynccontextmanager
    async def get_session(self):
        """Get async database session."""
        if not self.session_maker:
            await self.init_async()
        
        session = self.session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def save_radar_result(
        self,
        stories: List[Dict[str, Any]],
        total_articles_processed: int,
        time_window_hours: int,
        processing_time_seconds: float,
        hotness_threshold: float,
        top_k: int
    ) -> int:
        """
        Save radar processing result to database.
        
        Args:
            stories: List of story dictionaries
            total_articles_processed: Total articles processed
            time_window_hours: Time window used
            processing_time_seconds: Processing time
            hotness_threshold: Hotness threshold used
            top_k: Top K parameter used
            
        Returns:
            ID of the created radar run
        """
        async with self.get_session() as session:
            # Create radar run
            radar_run = RadarRun(
                time_window_hours=time_window_hours,
                total_articles_processed=total_articles_processed,
                processing_time_seconds=processing_time_seconds,
                hotness_threshold=hotness_threshold,
                top_k=top_k
            )
            session.add(radar_run)
            await session.flush()  # Get the ID
            
            # Create stories
            for story_data in stories:
                story = StoryDB(
                    radar_run_id=radar_run.id,
                    story_id=story_data.get("id", ""),
                    headline=story_data.get("headline", ""),
                    hotness=story_data.get("hotness", 0.0),
                    why_now=story_data.get("why_now", ""),
                    draft=story_data.get("draft", ""),
                    dedup_group=story_data.get("dedup_group", ""),
                    article_count=story_data.get("article_count", 1),
                    hotness_details=story_data.get("hotness_details", {}),
                    entities=story_data.get("entities", []),
                    sources=story_data.get("sources", []),
                    timeline=story_data.get("timeline", []),
                    has_deep_research=story_data.get("has_deep_research", False),
                    research_summary=story_data.get("research_summary", None)
                )
                session.add(story)
            
            await session.commit()
            return radar_run.id
    
    async def get_radar_history(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get radar processing history.
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of radar run dictionaries with story counts
        """
        from sqlalchemy import select, desc, func
        
        async with self.get_session() as session:
            # Query radar runs with story count
            query = (
                select(
                    RadarRun,
                    func.count(StoryDB.id).label("story_count")
                )
                .outerjoin(StoryDB)
                .group_by(RadarRun.id)
                .order_by(desc(RadarRun.created_at))
                .limit(limit)
                .offset(offset)
            )
            
            result = await session.execute(query)
            rows = result.all()
            
            return [
                {
                    **row[0].to_dict(),
                    "story_count": row[1]
                }
                for row in rows
            ]
    
    async def get_radar_run_details(
        self,
        run_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific radar run.
        
        Args:
            run_id: Radar run ID
            
        Returns:
            Dictionary with run details and stories, or None if not found
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        async with self.get_session() as session:
            query = (
                select(RadarRun)
                .options(selectinload(RadarRun.stories))
                .where(RadarRun.id == run_id)
            )
            
            result = await session.execute(query)
            radar_run = result.scalar_one_or_none()
            
            if not radar_run:
                return None
            
            return {
                **radar_run.to_dict(),
                "stories": [story.to_dict() for story in radar_run.stories]
            }
    
    async def delete_old_runs(self, keep_last_n: int = 100):
        """
        Delete old radar runs, keeping only the last N runs.
        
        Args:
            keep_last_n: Number of recent runs to keep
        """
        from sqlalchemy import select, delete
        
        async with self.get_session() as session:
            # Get IDs of runs to keep
            query = (
                select(RadarRun.id)
                .order_by(RadarRun.created_at.desc())
                .limit(keep_last_n)
            )
            result = await session.execute(query)
            ids_to_keep = [row[0] for row in result.all()]
            
            if ids_to_keep:
                # Delete old runs
                delete_query = delete(RadarRun).where(RadarRun.id.notin_(ids_to_keep))
                await session.execute(delete_query)
                await session.commit()


# =============================================================================
# Personal News Aggregator Models
# =============================================================================

class UserProfile(Base):
    """User profile information."""
    
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255))
    display_name = Column(String(100))
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    last_active_at = Column(DateTime, default=datetime.now, nullable=False, index=True)
    last_feed_check = Column(DateTime, nullable=True, index=True)
    
    # Relationships
    preferences = relationship("UserPreferencesDB", back_populates="user", uselist=False, cascade="all, delete-orphan")
    feed_items = relationship("FeedItem", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("ReadingSession", back_populates="user", cascade="all, delete-orphan")
    interest_weights = relationship("InterestWeight", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "display_name": self.display_name,
            "onboarding_completed": self.onboarding_completed,
            "created_at": self.created_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat()
        }


class UserPreferencesDB(Base):
    """User preferences stored in database."""
    
    __tablename__ = "user_preferences_db"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    sources = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    excluded_keywords = Column(JSON, default=list)
    categories = Column(JSON, default=list)
    update_frequency_minutes = Column(Integer, default=60)
    max_articles_per_feed = Column(Integer, default=20)
    language = Column(String(10), default="ru")
    auto_refresh_enabled = Column(Boolean, default=True)
    compact_view = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    user = relationship("UserProfile", back_populates="preferences")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "sources": self.sources or [],
            "keywords": self.keywords or [],
            "excluded_keywords": self.excluded_keywords or [],
            "categories": self.categories or [],
            "update_frequency_minutes": self.update_frequency_minutes,
            "max_articles_per_feed": self.max_articles_per_feed,
            "language": self.language,
            "auto_refresh_enabled": self.auto_refresh_enabled,
            "compact_view": self.compact_view,
            "updated_at": self.updated_at.isoformat()
        }


class FeedItem(Base):
    """Saved article in user's feed."""
    
    __tablename__ = "feed_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(String(200), nullable=False)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    source = Column(String(255), nullable=False)
    published_at = Column(DateTime, nullable=False, index=True)
    added_to_feed_at = Column(DateTime, default=datetime.now, nullable=False)
    relevance_score = Column(Float, default=0.5)
    matched_keywords = Column(JSON, default=list)
    cluster_size = Column(Integer, default=1)
    is_read = Column(Boolean, default=False, index=True)
    is_saved = Column(Boolean, default=False, index=True)
    is_liked = Column(Boolean, default=False, index=True)
    is_disliked = Column(Boolean, default=False)
    read_at = Column(DateTime)
    saved_at = Column(DateTime)
    liked_at = Column(DateTime)
    disliked_at = Column(DateTime)
    
    # Relationships
    user = relationship("UserProfile", back_populates="feed_items")
    interactions = relationship("UserInteraction", back_populates="feed_item", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "article_id": self.article_id,
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "source": self.source,
            "published_at": self.published_at.isoformat(),
            "added_to_feed_at": self.added_to_feed_at.isoformat(),
            "relevance_score": self.relevance_score,
            "matched_keywords": self.matched_keywords or [],
            "cluster_size": self.cluster_size,
            "is_read": self.is_read,
            "is_saved": self.is_saved,
            "is_liked": self.is_liked,
            "is_disliked": self.is_disliked,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "saved_at": self.saved_at.isoformat() if self.saved_at else None,
            "liked_at": self.liked_at.isoformat() if self.liked_at else None
        }


class UserInteraction(Base):
    """Behavioral tracking of user interactions."""
    
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(String(200), nullable=False, index=True)
    feed_item_id = Column(Integer, ForeignKey("feed_items.id", ondelete="CASCADE"))
    
    # Interaction type: 'view', 'click', 'like', 'dislike', 'save', 'share'
    interaction_type = Column(String(50), nullable=False, index=True)
    
    # Metrics
    view_duration_seconds = Column(Integer)
    scroll_depth = Column(Float)
    clicked_read_more = Column(Boolean, default=False)
    
    # Context
    matched_keywords = Column(JSON)
    relevance_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)
    
    # Relationships
    user = relationship("UserProfile", back_populates="interactions")
    feed_item = relationship("FeedItem", back_populates="interactions")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "article_id": self.article_id,
            "interaction_type": self.interaction_type,
            "view_duration_seconds": self.view_duration_seconds,
            "scroll_depth": self.scroll_depth,
            "clicked_read_more": self.clicked_read_more,
            "matched_keywords": self.matched_keywords,
            "relevance_score": self.relevance_score,
            "created_at": self.created_at.isoformat()
        }


class ReadingSession(Base):
    """Reading session for analytics."""
    
    __tablename__ = "reading_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.now, nullable=False, index=True)
    ended_at = Column(DateTime)
    articles_viewed = Column(Integer, default=0)
    articles_read = Column(Integer, default=0)
    articles_liked = Column(Integer, default=0)
    articles_saved = Column(Integer, default=0)
    total_time_seconds = Column(Integer, default=0)
    
    # Relationships
    user = relationship("UserProfile", back_populates="sessions")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "articles_viewed": self.articles_viewed,
            "articles_read": self.articles_read,
            "articles_liked": self.articles_liked,
            "articles_saved": self.articles_saved,
            "total_time_seconds": self.total_time_seconds
        }


class FeedCache(Base):
    """Cached feed data for fast access."""
    
    __tablename__ = "feed_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True)
    cached_at = Column(DateTime, default=datetime.now, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    feed_data = Column(JSON, nullable=False)
    articles_count = Column(Integer, default=0)


class InterestWeight(Base):
    """Learned keyword weights from user behavior."""
    
    __tablename__ = "interest_weights"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("user_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True)
    keyword = Column(String(200), nullable=False)
    weight = Column(Float, default=0.5)  # 0.0 to 1.0
    engagement_count = Column(Integer, default=0)
    last_seen_at = Column(DateTime, default=datetime.now, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    user = relationship("UserProfile", back_populates="interest_weights")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "keyword": self.keyword,
            "weight": self.weight,
            "engagement_count": self.engagement_count,
            "last_seen_at": self.last_seen_at.isoformat()
        }


class OnboardingPreset(Base):
    """Predefined presets for onboarding."""
    
    __tablename__ = "onboarding_presets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    preset_key = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    emoji = Column(String(10))
    description = Column(Text)
    categories = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    sources = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "preset_key": self.preset_key,
            "name": self.name,
            "emoji": self.emoji,
            "description": self.description,
            "categories": self.categories or [],
            "keywords": self.keywords or [],
            "sources": self.sources or [],
            "sort_order": self.sort_order
        }


# Global database manager instance
db_manager = DatabaseManager()

