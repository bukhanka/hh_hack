"""Smart Feed Updater - Incremental feed updates and smart caching."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, desc, func

from database import (
    db_manager,
    FeedItem,
    FeedCache,
    UserProfile,
    UserPreferencesDB
)
from models import PersonalNewsItem, PersonalFeedResponse, UserPreferences
from modes.personal.news_aggregator import PersonalNewsAggregator
from modes.personal.feed_storage import feed_storage
from modes.personal.user_preferences import preferences_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartFeedUpdater:
    """
    Smart updater for user feeds.
    
    Performs incremental updates and manages caching.
    """
    
    def __init__(self):
        """Initialize smart updater."""
        self.aggregator = PersonalNewsAggregator()
    
    async def should_update_feed(
        self,
        user_id: str,
        update_frequency_minutes: Optional[int] = None
    ) -> bool:
        """
        Check if feed should be updated.
        
        Args:
            user_id: User identifier
            update_frequency_minutes: Custom update frequency
            
        Returns:
            True if update is needed
        """
        try:
            async with db_manager.get_session() as session:
                # Get user preferences for update frequency
                if update_frequency_minutes is None:
                    prefs_result = await session.execute(
                        select(UserPreferencesDB).where(
                            UserPreferencesDB.user_id == user_id
                        )
                    )
                    prefs = prefs_result.scalar_one_or_none()
                    update_frequency_minutes = prefs.update_frequency_minutes if prefs else 60
                
                # Check last feed item timestamp
                result = await session.execute(
                    select(func.max(FeedItem.added_to_feed_at))
                    .where(FeedItem.user_id == user_id)
                )
                last_update = result.scalar()
                
                if last_update is None:
                    # No feed items yet, needs update
                    return True
                
                # Check if enough time has passed
                time_since_update = datetime.now() - last_update
                return time_since_update.total_seconds() / 60 >= update_frequency_minutes
                
        except Exception as e:
            logger.error(f"Error checking update status: {e}")
            return True  # Update on error to be safe
    
    async def incremental_update(
        self,
        user_id: str,
        time_window_hours: int = 6
    ) -> int:
        """
        Perform incremental feed update (only new articles).
        
        This is much faster than full re-scan as it only processes recent news.
        
        Args:
            user_id: User identifier
            time_window_hours: How far back to look for new articles
            
        Returns:
            Number of new items added
        """
        try:
            logger.info(f"Starting incremental update for user {user_id}")
            
            # Get latest article timestamp from user's feed
            async with db_manager.get_session() as session:
                result = await session.execute(
                    select(func.max(FeedItem.published_at))
                    .where(FeedItem.user_id == user_id)
                )
                latest_timestamp = result.scalar()
            
            if latest_timestamp:
                # Only look for articles newer than what we have
                hours_since_last = (datetime.now() - latest_timestamp).total_seconds() / 3600
                time_window_hours = min(time_window_hours, max(1, int(hours_since_last) + 1))
                logger.info(f"Latest article from {latest_timestamp}, scanning {time_window_hours}h")
            
            # Run aggregator with short time window
            result = await self.aggregator.process_news(
                user_id=user_id,
                time_window_hours=time_window_hours
            )
            
            # Save new items
            if result.items:
                saved_count = await feed_storage.save_feed_items(user_id, result.items)
                logger.info(f"Incremental update: added {saved_count} new items for user {user_id}")
                return saved_count
            else:
                logger.info(f"Incremental update: no new items for user {user_id}")
                return 0
                
        except Exception as e:
            logger.error(f"Error in incremental update: {e}", exc_info=True)
            return 0
    
    async def smart_cache_get(
        self,
        user_id: str,
        force_refresh: bool = False
    ) -> Optional[PersonalFeedResponse]:
        """
        Get feed from cache or update if needed.
        
        Args:
            user_id: User identifier
            force_refresh: Force cache refresh
            
        Returns:
            PersonalFeedResponse from cache or None
        """
        try:
            if force_refresh:
                return None
            
            async with db_manager.get_session() as session:
                # Check cache
                result = await session.execute(
                    select(FeedCache)
                    .where(
                        and_(
                            FeedCache.user_id == user_id,
                            FeedCache.expires_at > datetime.now()
                        )
                    )
                    .order_by(desc(FeedCache.cached_at))
                    .limit(1)
                )
                cache_entry = result.scalar_one_or_none()
                
                if cache_entry and cache_entry.feed_data:
                    logger.info(f"Cache hit for user {user_id}")
                    # Convert cached data to PersonalFeedResponse
                    feed_data = cache_entry.feed_data
                    
                    # Reconstruct PersonalNewsItem objects
                    from models import PersonalNewsItem
                    items = []
                    for item_data in feed_data.get('items', []):
                        item = PersonalNewsItem(**item_data)
                        items.append(item)
                    
                    return PersonalFeedResponse(
                        items=items,
                        total_articles_processed=feed_data.get('total_articles_processed', 0),
                        filtered_count=feed_data.get('filtered_count', 0),
                        time_window_hours=feed_data.get('time_window_hours', 24),
                        generated_at=datetime.fromisoformat(feed_data.get('generated_at')),
                        processing_time_seconds=feed_data.get('processing_time_seconds', 0),
                        user_id=user_id
                    )
                else:
                    logger.info(f"Cache miss for user {user_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None
    
    async def smart_cache_set(
        self,
        user_id: str,
        feed_response: PersonalFeedResponse,
        ttl_minutes: int = 30
    ) -> bool:
        """
        Save feed to cache.
        
        Args:
            user_id: User identifier
            feed_response: Feed to cache
            ttl_minutes: Time to live in minutes
            
        Returns:
            True if cached successfully
        """
        try:
            async with db_manager.get_session() as session:
                # Serialize feed response
                feed_data = {
                    'items': [item.model_dump() for item in feed_response.items],
                    'total_articles_processed': feed_response.total_articles_processed,
                    'filtered_count': feed_response.filtered_count,
                    'time_window_hours': feed_response.time_window_hours,
                    'generated_at': feed_response.generated_at.isoformat(),
                    'processing_time_seconds': feed_response.processing_time_seconds
                }
                
                # Delete old cache entries for this user
                from sqlalchemy import delete
                await session.execute(
                    delete(FeedCache).where(FeedCache.user_id == user_id)
                )
                
                # Create new cache entry
                cache_entry = FeedCache(
                    user_id=user_id,
                    cached_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=ttl_minutes),
                    feed_data=feed_data,
                    articles_count=len(feed_response.items)
                )
                session.add(cache_entry)
                await session.flush()
                
                logger.info(f"Cached feed for user {user_id} (TTL: {ttl_minutes}m)")
                return True
                
        except Exception as e:
            logger.error(f"Error caching feed: {e}")
            return False
    
    async def get_or_update_feed(
        self,
        user_id: str,
        force_refresh: bool = False,
        use_cache: bool = True
    ) -> PersonalFeedResponse:
        """
        Get feed from cache or generate new one.
        
        Main entry point for getting user feed.
        
        Args:
            user_id: User identifier
            force_refresh: Force refresh (ignore cache)
            use_cache: Whether to use caching
            
        Returns:
            PersonalFeedResponse
        """
        try:
            # Try cache first
            if use_cache and not force_refresh:
                cached_feed = await self.smart_cache_get(user_id)
                if cached_feed:
                    return cached_feed
            
            # Check if incremental update is sufficient
            should_update = await self.should_update_feed(user_id)
            
            if should_update or force_refresh:
                # Check if we can do incremental update
                async with db_manager.get_session() as session:
                    count_result = await session.execute(
                        select(func.count(FeedItem.id)).where(FeedItem.user_id == user_id)
                    )
                    item_count = count_result.scalar() or 0
                
                if item_count > 0 and not force_refresh:
                    # Incremental update
                    logger.info(f"Performing incremental update for user {user_id}")
                    await self.incremental_update(user_id, time_window_hours=6)
                else:
                    # Full refresh
                    logger.info(f"Performing full refresh for user {user_id}")
                    result = await self.aggregator.process_news(user_id=user_id)
                    
                    # Save items
                    if result.items:
                        await feed_storage.save_feed_items(user_id, result.items)
                    
                    # Cache the result
                    if use_cache:
                        await self.smart_cache_set(user_id, result)
                    
                    return result
            
            # Get feed from database
            items = await feed_storage.get_user_feed(user_id, limit=50)
            
            # Convert to PersonalNewsItem objects
            from models import PersonalNewsItem
            news_items = []
            for item_data in items:
                news_item = PersonalNewsItem(
                    id=item_data['article_id'],
                    title=item_data['title'],
                    summary=item_data['summary'],
                    url=item_data['url'],
                    source=item_data['source'],
                    published_at=datetime.fromisoformat(item_data['published_at']),
                    relevance_score=item_data['relevance_score'],
                    matched_keywords=item_data['matched_keywords'],
                    cluster_size=item_data['cluster_size']
                )
                news_items.append(news_item)
            
            response = PersonalFeedResponse(
                items=news_items,
                total_articles_processed=len(news_items),
                filtered_count=0,
                time_window_hours=24,
                generated_at=datetime.now(),
                processing_time_seconds=0.0,
                user_id=user_id
            )
            
            # Cache the result
            if use_cache:
                await self.smart_cache_set(user_id, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting/updating feed: {e}", exc_info=True)
            # Return empty feed on error
            return PersonalFeedResponse(
                items=[],
                total_articles_processed=0,
                filtered_count=0,
                time_window_hours=24,
                generated_at=datetime.now(),
                processing_time_seconds=0.0,
                user_id=user_id
            )
    
    async def cleanup_old_cache(self, days: int = 7) -> int:
        """
        Clean up expired cache entries.
        
        Args:
            days: Delete cache older than this many days
            
        Returns:
            Number of entries deleted
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)
            
            async with db_manager.get_session() as session:
                from sqlalchemy import delete
                result = await session.execute(
                    delete(FeedCache).where(FeedCache.expires_at < cutoff)
                )
                await session.flush()
                deleted = result.rowcount
                logger.info(f"Cleaned up {deleted} expired cache entries")
                return deleted
                
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0


# Global instance
smart_updater = SmartFeedUpdater()

