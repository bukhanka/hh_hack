"""Financial RADAR endpoints."""

import logging
from fastapi import APIRouter, HTTPException, Query

from models import RadarResponse
from radar import FinancialNewsRadar
from database import db_manager
from api.schemas import ProcessRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["financial"])

# Initialize RADAR system
radar = FinancialNewsRadar()

# Cache for last result (in-memory fallback)
last_result_cache = {
    "result": None,
    "timestamp": None
}


@router.post("/process", response_model=RadarResponse)
async def process_news(request: ProcessRequest):
    """
    Process news and return hot stories.
    
    Args:
        request: Processing parameters
        
    Returns:
        RadarResponse with detected hot stories
    """
    try:
        logger.info(f"Processing request: {request}")
        
        result = await radar.process_news(
            time_window_hours=request.time_window_hours,
            top_k=request.top_k,
            hotness_threshold=request.hotness_threshold,
            custom_feeds=request.custom_feeds
        )
        
        # Cache result in memory
        last_result_cache["result"] = result
        last_result_cache["timestamp"] = result.generated_at
        
        # Save to database
        try:
            stories_data = [story.model_dump() for story in result.stories]
            run_id = await db_manager.save_radar_result(
                stories=stories_data,
                total_articles_processed=result.total_articles_processed,
                time_window_hours=result.time_window_hours,
                processing_time_seconds=result.processing_time_seconds,
                hotness_threshold=request.hotness_threshold,
                top_k=request.top_k
            )
            logger.info(f"Saved radar result to database with ID: {run_id}")
        except Exception as db_error:
            logger.error(f"Failed to save to database: {db_error}", exc_info=True)
            # Continue even if DB save fails
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/last-result", response_model=RadarResponse)
async def get_last_result():
    """Get the last processed result from cache."""
    if last_result_cache["result"] is None:
        raise HTTPException(status_code=404, detail="No results available yet")
    
    return last_result_cache["result"]


@router.get("/history")
async def get_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get radar processing history.
    
    Args:
        limit: Maximum number of results (1-100)
        offset: Offset for pagination
        
    Returns:
        List of radar runs with metadata
    """
    try:
        history = await db_manager.get_radar_history(limit=limit, offset=offset)
        return {"history": history, "limit": limit, "offset": offset}
    except Exception as e:
        logger.error(f"Error fetching history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{run_id}")
async def get_run_details(run_id: int):
    """
    Get detailed information about a specific radar run.
    
    Args:
        run_id: Radar run ID
        
    Returns:
        Radar run with all stories
    """
    try:
        details = await db_manager.get_radar_run_details(run_id)
        
        if details is None:
            raise HTTPException(status_code=404, detail=f"Radar run {run_id} not found")
        
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching run details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/cleanup")
async def cleanup_old_runs(keep_last_n: int = Query(100, ge=10, le=500)):
    """
    Delete old radar runs, keeping only the last N runs.
    
    Args:
        keep_last_n: Number of recent runs to keep (10-500)
        
    Returns:
        Success message
    """
    try:
        await db_manager.delete_old_runs(keep_last_n=keep_last_n)
        return {"message": f"Cleaned up old runs, kept last {keep_last_n}"}
    except Exception as e:
        logger.error(f"Error cleaning up old runs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

