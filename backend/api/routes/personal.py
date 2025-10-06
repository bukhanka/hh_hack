"""Personal news aggregator endpoints - preferences and sources management."""

import logging
from fastapi import APIRouter, HTTPException

from models import PersonalFeedResponse, UserPreferences
from modes.personal.news_aggregator import PersonalNewsAggregator
from modes.personal.user_preferences import preferences_manager
from modes.personal.feed_storage import feed_storage
from api.schemas import PersonalScanRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/personal", tags=["personal"])

# Initialize Personal News Aggregator
personal_aggregator = PersonalNewsAggregator()

# Cache for personal feed results
personal_feed_cache = {}


@router.post("/scan", response_model=PersonalFeedResponse)
async def scan_personal_news(request: PersonalScanRequest):
    """
    Scan and aggregate personalized news feed.
    
    Args:
        request: Personal scan parameters
        
    Returns:
        PersonalFeedResponse with filtered and summarized news
    """
    try:
        logger.info(f"Processing personal feed request: user={request.user_id}")
        
        result = await personal_aggregator.process_news(
            user_id=request.user_id,
            time_window_hours=request.time_window_hours,
            custom_sources=request.custom_sources
        )
        
        # Save feed items to database
        if result.items:
            saved_count = await feed_storage.save_feed_items(request.user_id, result.items)
            logger.info(f"Saved {saved_count} new items to database for user {request.user_id}")
        
        # Cache result
        personal_feed_cache[request.user_id] = result
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing personal news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences/{user_id}", response_model=UserPreferences)
async def get_user_preferences(user_id: str):
    """
    Get user preferences.
    
    Args:
        user_id: User identifier
        
    Returns:
        UserPreferences object
    """
    try:
        prefs = await preferences_manager.get_or_create_default_async(user_id)
        return prefs
    except Exception as e:
        logger.error(f"Error fetching preferences: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preferences")
async def save_user_preferences(preferences: UserPreferences):
    """
    Save user preferences.
    
    Args:
        preferences: UserPreferences object
        
    Returns:
        Success message
    """
    try:
        success = await preferences_manager.save_preferences_async(preferences)
        if success:
            return {"message": "Preferences saved successfully", "user_id": preferences.user_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to save preferences")
    except Exception as e:
        logger.error(f"Error saving preferences: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/popular")
async def get_popular_sources():
    """
    Get popular RSS sources by category.
    
    Returns:
        Dictionary of categories and their sources
    """
    try:
        return preferences_manager.get_popular_sources()
    except Exception as e:
        logger.error(f"Error fetching popular sources: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sources/add")
async def add_source(user_id: str, source_url: str):
    """
    Add RSS source to user preferences.
    
    Args:
        user_id: User identifier
        source_url: RSS feed URL
        
    Returns:
        Success message
    """
    try:
        success = await preferences_manager.add_source_async(user_id, source_url)
        if success:
            return {"message": "Source added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add source")
    except Exception as e:
        logger.error(f"Error adding source: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sources/remove")
async def remove_source(user_id: str, source_url: str):
    """
    Remove RSS source from user preferences.
    
    Args:
        user_id: User identifier
        source_url: RSS feed URL
        
    Returns:
        Success message
    """
    try:
        success = await preferences_manager.remove_source_async(user_id, source_url)
        if success:
            return {"message": "Source removed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to remove source")
    except Exception as e:
        logger.error(f"Error removing source: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keywords/add")
async def add_keyword(user_id: str, keyword: str):
    """
    Add keyword filter to user preferences.
    
    Args:
        user_id: User identifier
        keyword: Keyword to add
        
    Returns:
        Success message
    """
    try:
        success = await preferences_manager.add_keyword_async(user_id, keyword)
        if success:
            return {"message": "Keyword added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add keyword")
    except Exception as e:
        logger.error(f"Error adding keyword: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/keywords/remove")
async def remove_keyword(user_id: str, keyword: str):
    """
    Remove keyword filter from user preferences.
    
    Args:
        user_id: User identifier
        keyword: Keyword to remove
        
    Returns:
        Success message
    """
    try:
        success = await preferences_manager.remove_keyword_async(user_id, keyword)
        if success:
            return {"message": "Keyword removed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to remove keyword")
    except Exception as e:
        logger.error(f"Error removing keyword: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str, days: int = 7):
    """
    Get user statistics.
    
    Returns reading statistics for the specified time period.
    """
    try:
        stats = await feed_storage.get_user_stats(user_id, days=days)
        return stats
    except Exception as e:
        logger.error(f"Error getting user stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feed/new-count")
async def get_new_items_count(user_id: str):
    """
    Get count of new unread items since last check.
    
    Returns count of new items and metadata.
    """
    try:
        result = await feed_storage.get_new_items_count(user_id)
        return result
    except Exception as e:
        logger.error(f"Error getting new items count: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feed/metadata")
async def get_feed_metadata(user_id: str):
    """
    Get feed metadata (counts, last update time, etc.).
    
    Returns comprehensive feed metadata.
    """
    try:
        metadata = await feed_storage.get_feed_metadata(user_id)
        return metadata
    except Exception as e:
        logger.error(f"Error getting feed metadata: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feed/refresh")
async def refresh_feed(user_id: str):
    """
    Perform incremental feed refresh (only new items).
    
    Faster than full scan as it only fetches recent news.
    """
    try:
        from modes.personal.smart_updater import smart_updater
        
        logger.info(f"Incremental refresh requested for user {user_id}")
        
        # Perform incremental update
        new_items_count = await smart_updater.incremental_update(user_id, time_window_hours=6)
        
        # Update last check timestamp
        await feed_storage.update_last_feed_check(user_id)
        
        # Get updated feed
        items = await feed_storage.get_user_feed(user_id, limit=20)
        
        return {
            "message": "Feed refreshed successfully",
            "new_items_added": new_items_count,
            "total_items": len(items),
            "items": items[:10] if items else []  # Return first 10 new items
        }
    except Exception as e:
        logger.error(f"Error refreshing feed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feed/mark-checked")
async def mark_feed_checked(user_id: str):
    """
    Mark feed as checked (updates last_feed_check timestamp).
    
    Used when user views their feed.
    """
    try:
        success = await feed_storage.update_last_feed_check(user_id)
        if success:
            return {"message": "Feed marked as checked", "checked_at": "now"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update check time")
    except Exception as e:
        logger.error(f"Error marking feed as checked: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

