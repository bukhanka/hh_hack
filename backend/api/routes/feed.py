"""Feed management endpoints - interactions, likes, reads, saves."""

import logging
from fastapi import APIRouter, HTTPException, Query

from modes.personal.feed_storage import feed_storage
from api.schemas import InteractionRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/personal", tags=["feed"])


@router.post("/interactions/track")
async def track_interaction(request: InteractionRequest):
    """
    Track user interaction with an article.
    
    This endpoint records user behavior for learning preferences.
    """
    try:
        success = await feed_storage.track_interaction(
            user_id=request.user_id,
            article_id=request.article_id,
            interaction_type=request.interaction_type,
            view_duration_seconds=request.view_duration_seconds,
            scroll_depth=request.scroll_depth,
            clicked_read_more=request.clicked_read_more,
            matched_keywords=request.matched_keywords,
            relevance_score=request.relevance_score
        )
        
        if success:
            return {"message": "Interaction tracked successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to track interaction")
    except Exception as e:
        logger.error(f"Error tracking interaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feed/mark-read")
async def mark_article_read(user_id: str, article_id: str):
    """Mark article as read."""
    try:
        success = await feed_storage.mark_as_read(user_id, article_id)
        if success:
            # Also track interaction
            await feed_storage.track_interaction(user_id, article_id, 'view')
            return {"message": "Article marked as read"}
        else:
            raise HTTPException(status_code=404, detail="Article not found")
    except Exception as e:
        logger.error(f"Error marking as read: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feed/toggle-like")
async def toggle_like(user_id: str, article_id: str, liked: bool):
    """Toggle like status of an article."""
    try:
        success = await feed_storage.toggle_like(user_id, article_id, liked)
        if success:
            # Track interaction
            await feed_storage.track_interaction(
                user_id, 
                article_id, 
                'like' if liked else 'unlike'
            )
            return {"message": f"Article {'liked' if liked else 'unliked'}"}
        else:
            raise HTTPException(status_code=404, detail="Article not found")
    except Exception as e:
        logger.error(f"Error toggling like: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feed/toggle-dislike")
async def toggle_dislike(user_id: str, article_id: str, disliked: bool):
    """Toggle dislike status of an article."""
    try:
        success = await feed_storage.toggle_dislike(user_id, article_id, disliked)
        if success:
            # Track interaction
            await feed_storage.track_interaction(
                user_id, 
                article_id, 
                'dislike' if disliked else 'undislike'
            )
            return {"message": f"Article {'disliked' if disliked else 'undisliked'}"}
        else:
            raise HTTPException(status_code=404, detail="Article not found")
    except Exception as e:
        logger.error(f"Error toggling dislike: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feed/toggle-save")
async def toggle_save(user_id: str, article_id: str, saved: bool):
    """Toggle save status of an article."""
    try:
        success = await feed_storage.toggle_save(user_id, article_id, saved)
        if success:
            # Track interaction
            await feed_storage.track_interaction(
                user_id, 
                article_id, 
                'save' if saved else 'unsave'
            )
            return {"message": f"Article {'saved' if saved else 'unsaved'}"}
        else:
            raise HTTPException(status_code=404, detail="Article not found")
    except Exception as e:
        logger.error(f"Error toggling save: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feed/get")
async def get_user_feed(
    user_id: str,
    limit: int = Query(20, ge=5, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = False,
    saved_only: bool = False,
    liked_only: bool = False
):
    """
    Get user's feed from database (persisted feed).
    
    This returns previously saved feed items.
    """
    try:
        items = await feed_storage.get_user_feed(
            user_id=user_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
            saved_only=saved_only,
            liked_only=liked_only
        )
        return {"items": items, "count": len(items)}
    except Exception as e:
        logger.error(f"Error getting user feed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

