"""Background worker for automated feed updates and maintenance tasks."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_

from database import db_manager, UserProfile, UserPreferencesDB
from modes.personal.smart_updater import smart_updater
from modes.personal.learning_engine import learning_engine
from modes.personal.feed_storage import feed_storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackgroundWorker:
    """
    Background worker for automated tasks.
    
    Handles:
    - Automatic feed updates for active users
    - ML model retraining
    - Data cleanup
    - Cache maintenance
    """
    
    def __init__(self):
        """Initialize background worker."""
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def get_active_users(self, hours: int = 24) -> List[str]:
        """
        Get list of active users (active in last N hours).
        
        Args:
            hours: Hours to look back
            
        Returns:
            List of user IDs
        """
        try:
            since = datetime.now() - timedelta(hours=hours)
            
            async with db_manager.get_session() as session:
                result = await session.execute(
                    select(UserProfile.user_id)
                    .where(UserProfile.last_active_at >= since)
                    .order_by(UserProfile.last_active_at.desc())
                )
                users = result.scalars().all()
                return list(users)
                
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    async def update_user_feed(self, user_id: str) -> bool:
        """
        Update feed for a single user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if updated successfully
        """
        try:
            # Check if user has auto-refresh enabled
            async with db_manager.get_session() as session:
                result = await session.execute(
                    select(UserPreferencesDB.auto_refresh_enabled)
                    .where(UserPreferencesDB.user_id == user_id)
                )
                auto_refresh = result.scalar_one_or_none()
                
                if auto_refresh is False:
                    logger.debug(f"Auto-refresh disabled for user {user_id}")
                    return False
            
            # Perform incremental update
            new_items = await smart_updater.incremental_update(user_id)
            
            if new_items > 0:
                logger.info(f"Updated feed for user {user_id}: {new_items} new items")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating feed for user {user_id}: {e}")
            return False
    
    async def update_all_feeds(self):
        """
        Update feeds for all active users.
        
        Runs every 15 minutes.
        """
        try:
            logger.info("Starting feed update job for all active users...")
            
            # Get active users from last 24 hours
            active_users = await self.get_active_users(hours=24)
            
            if not active_users:
                logger.info("No active users to update")
                return
            
            logger.info(f"Found {len(active_users)} active users")
            
            # Update feeds concurrently (but with limit to avoid overwhelming the system)
            tasks = []
            for user_id in active_users:
                tasks.append(self.update_user_feed(user_id))
                
                # Process in batches of 5
                if len(tasks) >= 5:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    tasks = []
            
            # Process remaining
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info("Feed update job completed")
            
        except Exception as e:
            logger.error(f"Error in update_all_feeds job: {e}", exc_info=True)
    
    async def train_user_models(self):
        """
        Retrain ML models for all active users.
        
        Runs every hour.
        """
        try:
            logger.info("Starting ML model training job...")
            
            # Get users active in last 7 days (they need model updates)
            active_users = await self.get_active_users(hours=24 * 7)
            
            if not active_users:
                logger.info("No users to train")
                return
            
            logger.info(f"Training models for {len(active_users)} users")
            
            updated_count = 0
            for user_id in active_users:
                try:
                    # Update keyword weights based on interactions
                    weights = await learning_engine.update_keyword_weights(user_id, days_back=30)
                    
                    if weights:
                        updated_count += 1
                        logger.info(f"Updated model for user {user_id}: {len(weights)} keywords")
                    
                except Exception as e:
                    logger.error(f"Error training model for user {user_id}: {e}")
            
            logger.info(f"ML training job completed: {updated_count}/{len(active_users)} users updated")
            
        except Exception as e:
            logger.error(f"Error in train_user_models job: {e}", exc_info=True)
    
    async def cleanup_old_data(self):
        """
        Clean up old data (old feed items, expired cache, etc.).
        
        Runs daily at 3 AM.
        """
        try:
            logger.info("Starting data cleanup job...")
            
            # Get all users
            async with db_manager.get_session() as session:
                result = await session.execute(select(UserProfile.user_id))
                all_users = result.scalars().all()
            
            total_deleted = 0
            
            # Clean up old feed items for each user
            for user_id in all_users:
                try:
                    deleted = await feed_storage.cleanup_old_feed_items(user_id, keep_days=30)
                    total_deleted += deleted
                except Exception as e:
                    logger.error(f"Error cleaning up feed for user {user_id}: {e}")
            
            logger.info(f"Cleaned up {total_deleted} old feed items")
            
            # Clean up expired cache
            cache_deleted = await smart_updater.cleanup_old_cache(days=7)
            logger.info(f"Cleaned up {cache_deleted} expired cache entries")
            
            logger.info("Data cleanup job completed")
            
        except Exception as e:
            logger.error(f"Error in cleanup_old_data job: {e}", exc_info=True)
    
    async def discover_new_interests(self):
        """
        Discover new interests for active users.
        
        Runs every 6 hours.
        """
        try:
            logger.info("Starting interest discovery job...")
            
            # Get active users
            active_users = await self.get_active_users(hours=24 * 7)
            
            if not active_users:
                logger.info("No users for interest discovery")
                return
            
            logger.info(f"Discovering interests for {len(active_users)} users")
            
            discovered_count = 0
            for user_id in active_users:
                try:
                    # Discover new interests
                    new_interests = await learning_engine.discover_new_interests(
                        user_id,
                        min_engagement_threshold=0.7,
                        limit=5
                    )
                    
                    if new_interests:
                        discovered_count += 1
                        logger.info(
                            f"Discovered {len(new_interests)} new interests for user {user_id}: "
                            f"{', '.join(new_interests)}"
                        )
                    
                except Exception as e:
                    logger.error(f"Error discovering interests for user {user_id}: {e}")
            
            logger.info(
                f"Interest discovery job completed: "
                f"discovered interests for {discovered_count}/{len(active_users)} users"
            )
            
        except Exception as e:
            logger.error(f"Error in discover_new_interests job: {e}", exc_info=True)
    
    def start(self):
        """Start the background worker."""
        if self.is_running:
            logger.warning("Background worker is already running")
            return
        
        logger.info("Starting background worker...")
        
        # Schedule jobs
        
        # 1. Update feeds every 15 minutes
        self.scheduler.add_job(
            self.update_all_feeds,
            trigger=IntervalTrigger(minutes=15),
            id='update_feeds',
            name='Update user feeds',
            replace_existing=True
        )
        
        # 2. Train ML models every hour
        self.scheduler.add_job(
            self.train_user_models,
            trigger=IntervalTrigger(hours=1),
            id='train_models',
            name='Train ML models',
            replace_existing=True
        )
        
        # 3. Discover new interests every 6 hours
        self.scheduler.add_job(
            self.discover_new_interests,
            trigger=IntervalTrigger(hours=6),
            id='discover_interests',
            name='Discover new interests',
            replace_existing=True
        )
        
        # 4. Clean up old data daily at 3 AM
        self.scheduler.add_job(
            self.cleanup_old_data,
            trigger=CronTrigger(hour=3, minute=0),
            id='cleanup_data',
            name='Clean up old data',
            replace_existing=True
        )
        
        # Start scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info("Background worker started successfully")
        logger.info("Scheduled jobs:")
        for job in self.scheduler.get_jobs():
            logger.info(f"  - {job.name}: {job.trigger}")
    
    def stop(self):
        """Stop the background worker."""
        if not self.is_running:
            logger.warning("Background worker is not running")
            return
        
        logger.info("Stopping background worker...")
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("Background worker stopped")
    
    async def run_job_now(self, job_id: str):
        """
        Run a specific job immediately.
        
        Args:
            job_id: Job ID to run
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                logger.info(f"Running job {job_id} ({job.name}) now...")
                await job.func()
                logger.info(f"Job {job_id} completed")
            else:
                logger.error(f"Job {job_id} not found")
        except Exception as e:
            logger.error(f"Error running job {job_id}: {e}", exc_info=True)


# Global instance
background_worker = BackgroundWorker()


async def main():
    """Test the background worker."""
    # Initialize database
    await db_manager.init_async()
    
    # Start worker
    background_worker.start()
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        background_worker.stop()


if __name__ == "__main__":
    asyncio.run(main())

