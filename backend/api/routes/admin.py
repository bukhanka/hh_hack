"""Admin and background worker control endpoints."""

import logging
from fastapi import APIRouter, HTTPException

from background_worker import background_worker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/worker/run-job")
async def run_background_job(job_id: str):
    """
    Manually trigger a background job.
    
    Available jobs:
    - update_feeds: Update all user feeds
    - train_models: Train ML models
    - discover_interests: Discover new interests
    - cleanup_data: Clean up old data
    """
    try:
        valid_jobs = ['update_feeds', 'train_models', 'discover_interests', 'cleanup_data']
        if job_id not in valid_jobs:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid job_id. Must be one of: {', '.join(valid_jobs)}"
            )
        
        await background_worker.run_job_now(job_id)
        return {"message": f"Job {job_id} executed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running background job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/worker/status")
async def get_worker_status():
    """Get background worker status and scheduled jobs."""
    try:
        jobs_info = []
        if background_worker.is_running:
            for job in background_worker.scheduler.get_jobs():
                jobs_info.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
        
        return {
            "is_running": background_worker.is_running,
            "jobs": jobs_info,
            "total_jobs": len(jobs_info)
        }
    except Exception as e:
        logger.error(f"Error getting worker status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

