"""Learning engine and smart feed endpoints."""

import logging
from fastapi import APIRouter, HTTPException, Query

from modes.personal.learning_engine import learning_engine
from modes.personal.smart_updater import smart_updater

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/personal", tags=["learning"])


@router.get("/feed/smart")
async def get_smart_feed(
    user_id: str,
    force_refresh: bool = False,
    use_cache: bool = True
):
    """
    Get user's smart feed (with caching and auto-updates).
    
    This is the recommended endpoint for getting user feeds.
    Uses smart caching and incremental updates.
    """
    try:
        result = await smart_updater.get_or_update_feed(
            user_id=user_id,
            force_refresh=force_refresh,
            use_cache=use_cache
        )
        return result
    except Exception as e:
        logger.error(f"Error getting smart feed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning/update-weights")
async def update_user_weights(user_id: str, days_back: int = Query(30, ge=1, le=90)):
    """
    Manually trigger keyword weight update for a user.
    
    Normally happens automatically via background worker.
    """
    try:
        weights = await learning_engine.update_keyword_weights(user_id, days_back)
        return {
            "message": f"Updated {len(weights)} keyword weights",
            "weights": weights
        }
    except Exception as e:
        logger.error(f"Error updating weights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/weights/{user_id}")
async def get_user_weights(user_id: str):
    """Get current keyword weights for user."""
    try:
        weights = await learning_engine.get_keyword_weights(user_id)
        return {"user_id": user_id, "weights": weights}
    except Exception as e:
        logger.error(f"Error getting weights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/insights/{user_id}")
async def get_learning_insights(user_id: str):
    """
    Get insights about what the system has learned about user preferences.
    
    Shows strong/moderate/weak interests.
    """
    try:
        insights = await learning_engine.get_learning_insights(user_id)
        return insights
    except Exception as e:
        logger.error(f"Error getting learning insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning/discover/{user_id}")
async def discover_user_interests(
    user_id: str,
    min_engagement: float = Query(0.7, ge=0.0, le=1.0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Discover new potential interests for user.
    
    Returns suggested keywords based on high-engagement articles.
    """
    try:
        new_interests = await learning_engine.discover_new_interests(
            user_id,
            min_engagement_threshold=min_engagement,
            limit=limit
        )
        return {
            "user_id": user_id,
            "suggested_keywords": new_interests,
            "count": len(new_interests)
        }
    except Exception as e:
        logger.error(f"Error discovering interests: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

