"""Feed storage manager for saving and retrieving user feeds from database."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, and_, or_, desc, func

from database import (
    db_manager, 
    UserProfile,
    UserPreferencesDB, 
    FeedItem, 
    UserInteraction,
    ReadingSession,
    InterestWeight,
    FeedCache
)
from models import PersonalNewsItem, PersonalFeedResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeedStorageManager:
    """Manager for storing and retrieving user feeds."""
    
    def __init__(self):
        """Initialize feed storage manager."""
        pass
    
    async def ensure_user_profile(self, user_id: str) -> bool:
        """
        Ensure user profile exists in database.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if profile exists or was created
        """
        try:
            async with db_manager.get_session() as session:
                # Check if user exists
                result = await session.execute(
                    select(UserProfile).where(UserProfile.user_id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    # Create new user profile
                    user = UserProfile(user_id=user_id)
                    session.add(user)
                    await session.flush()
                    logger.info(f"Created new user profile for {user_id}")
                else:
                    # Update last active
                    user.last_active_at = datetime.now()
                    await session.flush()
                
                return True
        except Exception as e:
            logger.error(f"Error ensuring user profile: {e}")
            return False
    
    async def save_feed_items(
        self,
        user_id: str,
        items: List[PersonalNewsItem]
    ) -> int:
        """
        Save feed items to database.
        
        Args:
            user_id: User identifier
            items: List of PersonalNewsItem objects
            
        Returns:
            Number of items saved
        """
        try:
            await self.ensure_user_profile(user_id)
            
            async with db_manager.get_session() as session:
                saved_count = 0
                
                for item in items:
                    # Check if item already exists
                    result = await session.execute(
                        select(FeedItem).where(
                            and_(
                                FeedItem.user_id == user_id,
                                FeedItem.article_id == item.id
                            )
                        )
                    )
                    existing_item = result.scalar_one_or_none()
                    
                    if existing_item:
                        # Update existing item (maybe relevance changed)
                        existing_item.relevance_score = item.relevance_score
                        existing_item.matched_keywords = item.matched_keywords
                        existing_item.cluster_size = item.cluster_size
                    else:
                        # Create new feed item
                        feed_item = FeedItem(
                            user_id=user_id,
                            article_id=item.id,
                            title=item.title,
                            summary=item.summary,
                            url=item.url,
                            source=item.source,
                            published_at=item.published_at,
                            relevance_score=item.relevance_score,
                            matched_keywords=item.matched_keywords or [],
                            cluster_size=item.cluster_size
                        )
                        session.add(feed_item)
                        saved_count += 1
                
                await session.flush()
                logger.info(f"Saved {saved_count} new feed items for user {user_id}")
                return saved_count
                
        except Exception as e:
            logger.error(f"Error saving feed items: {e}")
            return 0
    
    async def get_user_feed(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False,
        saved_only: bool = False,
        liked_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get user's feed from database.
        
        Args:
            user_id: User identifier
            limit: Maximum number of items
            offset: Offset for pagination
            unread_only: Only unread items
            saved_only: Only saved items
            liked_only: Only liked items
            
        Returns:
            List of feed item dictionaries
        """
        try:
            async with db_manager.get_session() as session:
                # Build query
                query = select(FeedItem).where(FeedItem.user_id == user_id)
                
                # Apply filters
                if unread_only:
                    query = query.where(FeedItem.is_read == False)
                if saved_only:
                    query = query.where(FeedItem.is_saved == True)
                if liked_only:
                    query = query.where(FeedItem.is_liked == True)
                
                # Order by relevance and recency
                query = query.order_by(
                    desc(FeedItem.relevance_score),
                    desc(FeedItem.published_at)
                ).limit(limit).offset(offset)
                
                result = await session.execute(query)
                items = result.scalars().all()
                
                return [item.to_dict() for item in items]
                
        except Exception as e:
            logger.error(f"Error getting user feed: {e}")
            return []
    
    async def mark_as_read(self, user_id: str, article_id: str) -> bool:
        """Mark article as read."""
        try:
            async with db_manager.get_session() as session:
                result = await session.execute(
                    update(FeedItem)
                    .where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.article_id == article_id
                        )
                    )
                    .values(is_read=True, read_at=datetime.now())
                )
                await session.flush()
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error marking as read: {e}")
            return False
    
    async def toggle_like(self, user_id: str, article_id: str, liked: bool) -> bool:
        """Toggle like status."""
        try:
            async with db_manager.get_session() as session:
                result = await session.execute(
                    update(FeedItem)
                    .where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.article_id == article_id
                        )
                    )
                    .values(
                        is_liked=liked,
                        liked_at=datetime.now() if liked else None,
                        is_disliked=False  # Can't be both
                    )
                )
                await session.flush()
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error toggling like: {e}")
            return False
    
    async def toggle_dislike(self, user_id: str, article_id: str, disliked: bool) -> bool:
        """Toggle dislike status."""
        try:
            async with db_manager.get_session() as session:
                result = await session.execute(
                    update(FeedItem)
                    .where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.article_id == article_id
                        )
                    )
                    .values(
                        is_disliked=disliked,
                        disliked_at=datetime.now() if disliked else None,
                        is_liked=False  # Can't be both
                    )
                )
                await session.flush()
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error toggling dislike: {e}")
            return False
    
    async def toggle_save(self, user_id: str, article_id: str, saved: bool) -> bool:
        """Toggle save status."""
        try:
            async with db_manager.get_session() as session:
                result = await session.execute(
                    update(FeedItem)
                    .where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.article_id == article_id
                        )
                    )
                    .values(
                        is_saved=saved,
                        saved_at=datetime.now() if saved else None
                    )
                )
                await session.flush()
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error toggling save: {e}")
            return False
    
    async def track_interaction(
        self,
        user_id: str,
        article_id: str,
        interaction_type: str,
        view_duration_seconds: Optional[int] = None,
        scroll_depth: Optional[float] = None,
        clicked_read_more: bool = False,
        matched_keywords: Optional[List[str]] = None,
        relevance_score: Optional[float] = None
    ) -> bool:
        """
        Track user interaction with an article.
        
        Args:
            user_id: User identifier
            article_id: Article identifier
            interaction_type: Type of interaction ('view', 'click', 'like', 'dislike', 'save')
            view_duration_seconds: Duration of view in seconds
            scroll_depth: Scroll depth (0-1)
            clicked_read_more: Whether user clicked read more
            matched_keywords: Keywords that matched
            relevance_score: Relevance score of article
            
        Returns:
            True if tracked successfully
        """
        try:
            await self.ensure_user_profile(user_id)
            
            async with db_manager.get_session() as session:
                # Get feed_item_id if exists
                result = await session.execute(
                    select(FeedItem.id).where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.article_id == article_id
                        )
                    )
                )
                feed_item = result.scalar_one_or_none()
                
                # Create interaction
                interaction = UserInteraction(
                    user_id=user_id,
                    article_id=article_id,
                    feed_item_id=feed_item,
                    interaction_type=interaction_type,
                    view_duration_seconds=view_duration_seconds,
                    scroll_depth=scroll_depth,
                    clicked_read_more=clicked_read_more,
                    matched_keywords=matched_keywords or [],
                    relevance_score=relevance_score
                )
                session.add(interaction)
                await session.flush()
                
                logger.info(f"Tracked {interaction_type} interaction for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error tracking interaction: {e}")
            return False
    
    async def get_user_stats(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get user statistics for the last N days.
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            
        Returns:
            Dictionary with statistics
        """
        try:
            since = datetime.now() - timedelta(days=days)
            
            async with db_manager.get_session() as session:
                # Count articles
                total_result = await session.execute(
                    select(func.count(FeedItem.id))
                    .where(FeedItem.user_id == user_id)
                )
                total_articles = total_result.scalar() or 0
                
                read_result = await session.execute(
                    select(func.count(FeedItem.id))
                    .where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.is_read == True,
                            FeedItem.read_at >= since
                        )
                    )
                )
                articles_read = read_result.scalar() or 0
                
                liked_result = await session.execute(
                    select(func.count(FeedItem.id))
                    .where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.is_liked == True
                        )
                    )
                )
                articles_liked = liked_result.scalar() or 0
                
                saved_result = await session.execute(
                    select(func.count(FeedItem.id))
                    .where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.is_saved == True
                        )
                    )
                )
                articles_saved = saved_result.scalar() or 0
                
                # Get interactions
                interactions_result = await session.execute(
                    select(func.count(UserInteraction.id))
                    .where(
                        and_(
                            UserInteraction.user_id == user_id,
                            UserInteraction.created_at >= since
                        )
                    )
                )
                total_interactions = interactions_result.scalar() or 0
                
                # Average view time
                avg_time_result = await session.execute(
                    select(func.avg(UserInteraction.view_duration_seconds))
                    .where(
                        and_(
                            UserInteraction.user_id == user_id,
                            UserInteraction.interaction_type == 'view',
                            UserInteraction.created_at >= since
                        )
                    )
                )
                avg_view_time = avg_time_result.scalar() or 0
                
                return {
                    "user_id": user_id,
                    "days": days,
                    "total_articles_in_feed": total_articles,
                    "articles_read": articles_read,
                    "articles_liked": articles_liked,
                    "articles_saved": articles_saved,
                    "total_interactions": total_interactions,
                    "avg_view_duration_seconds": round(avg_view_time, 1) if avg_view_time else 0
                }
                
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    async def cleanup_old_feed_items(self, user_id: str, keep_days: int = 30) -> int:
        """
        Remove old feed items (except saved ones).
        
        Args:
            user_id: User identifier
            keep_days: Days to keep
            
        Returns:
            Number of items deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            
            async with db_manager.get_session() as session:
                result = await session.execute(
                    delete(FeedItem).where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.added_to_feed_at < cutoff_date,
                            FeedItem.is_saved == False  # Don't delete saved items
                        )
                    )
                )
                await session.flush()
                deleted_count = result.rowcount
                logger.info(f"Cleaned up {deleted_count} old feed items for user {user_id}")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up feed items: {e}")
            return 0
    
    async def get_new_items_count(
        self, 
        user_id: str, 
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get count of new unread items since a specific time.
        
        Args:
            user_id: User identifier
            since: Check for items added after this time (default: last check)
            
        Returns:
            Dictionary with new items count and timestamp
        """
        try:
            async with db_manager.get_session() as session:
                # Get user's last check time if not provided
                if since is None:
                    result = await session.execute(
                        select(UserProfile.last_feed_check)
                        .where(UserProfile.user_id == user_id)
                    )
                    last_check = result.scalar_one_or_none()
                    since = last_check or datetime.now() - timedelta(hours=1)
                
                # Count new unread items
                count_result = await session.execute(
                    select(func.count(FeedItem.id))
                    .where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.is_read == False,
                            FeedItem.added_to_feed_at > since
                        )
                    )
                )
                new_count = count_result.scalar() or 0
                
                # Get latest item timestamp
                latest_result = await session.execute(
                    select(func.max(FeedItem.added_to_feed_at))
                    .where(FeedItem.user_id == user_id)
                )
                latest_timestamp = latest_result.scalar()
                
                return {
                    "new_items_count": new_count,
                    "since": since.isoformat(),
                    "latest_update": latest_timestamp.isoformat() if latest_timestamp else None,
                    "checked_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting new items count: {e}")
            return {
                "new_items_count": 0,
                "since": since.isoformat() if since else None,
                "latest_update": None,
                "checked_at": datetime.now().isoformat()
            }
    
    async def update_last_feed_check(self, user_id: str) -> bool:
        """
        Update user's last feed check timestamp.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if updated successfully
        """
        try:
            await self.ensure_user_profile(user_id)
            
            async with db_manager.get_session() as session:
                result = await session.execute(
                    update(UserProfile)
                    .where(UserProfile.user_id == user_id)
                    .values(last_feed_check=datetime.now())
                )
                await session.flush()
                return result.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating last feed check: {e}")
            return False
    
    async def get_feed_metadata(self, user_id: str) -> Dict[str, Any]:
        """
        Get feed metadata (last update, counts, etc.).
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with feed metadata
        """
        try:
            async with db_manager.get_session() as session:
                # Get total items
                total_result = await session.execute(
                    select(func.count(FeedItem.id))
                    .where(FeedItem.user_id == user_id)
                )
                total_count = total_result.scalar() or 0
                
                # Get unread count
                unread_result = await session.execute(
                    select(func.count(FeedItem.id))
                    .where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.is_read == False
                        )
                    )
                )
                unread_count = unread_result.scalar() or 0
                
                # Get latest update time
                latest_result = await session.execute(
                    select(func.max(FeedItem.added_to_feed_at))
                    .where(FeedItem.user_id == user_id)
                )
                latest_update = latest_result.scalar()
                
                # Get user's last check time
                profile_result = await session.execute(
                    select(UserProfile.last_feed_check, UserProfile.last_active_at)
                    .where(UserProfile.user_id == user_id)
                )
                profile_data = profile_result.first()
                
                return {
                    "total_items": total_count,
                    "unread_items": unread_count,
                    "latest_update": latest_update.isoformat() if latest_update else None,
                    "last_check": profile_data[0].isoformat() if profile_data and profile_data[0] else None,
                    "last_active": profile_data[1].isoformat() if profile_data and profile_data[1] else None,
                }
                
        except Exception as e:
            logger.error(f"Error getting feed metadata: {e}")
            return {
                "total_items": 0,
                "unread_items": 0,
                "latest_update": None,
                "last_check": None,
                "last_active": None
            }


# Global instance
feed_storage = FeedStorageManager()