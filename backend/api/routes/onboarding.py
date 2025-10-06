"""Onboarding flow endpoints."""

import logging
from fastapi import APIRouter, HTTPException

from models import UserPreferences
from modes.personal.user_preferences import preferences_manager
from modes.personal.feed_storage import feed_storage
from database import db_manager, OnboardingPreset
from api.schemas import OnboardingCompleteRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


@router.get("/presets")
async def get_onboarding_presets():
    """
    Get onboarding presets for quick setup.
    
    Returns predefined category/source/keyword combinations.
    """
    try:
        async with db_manager.get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(OnboardingPreset)
                .where(OnboardingPreset.is_active == True)
                .order_by(OnboardingPreset.sort_order)
            )
            presets = result.scalars().all()
            return [preset.to_dict() for preset in presets]
    except Exception as e:
        logger.error(f"Error getting onboarding presets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete")
async def complete_onboarding(request: OnboardingCompleteRequest):
    """
    Complete user onboarding and set up preferences.
    
    This endpoint is called when user finishes the onboarding flow.
    """
    try:
        # Create user preferences
        prefs = UserPreferences(
            user_id=request.user_id,
            sources=request.sources,
            keywords=request.keywords,
            categories=request.categories,
            update_frequency_minutes=60,
            max_articles_per_feed=20,
            language="ru"
        )
        
        # Save preferences
        await preferences_manager.save_preferences_async(prefs)
        
        # Mark onboarding as completed
        await feed_storage.ensure_user_profile(request.user_id)
        async with db_manager.get_session() as session:
            from sqlalchemy import update
            from database import UserProfile
            await session.execute(
                update(UserProfile)
                .where(UserProfile.user_id == request.user_id)
                .values(onboarding_completed=True)
            )
            await session.flush()
        
        logger.info(f"Onboarding completed for user {request.user_id}")
        return {"message": "Onboarding completed successfully", "user_id": request.user_id}
    except Exception as e:
        logger.error(f"Error completing onboarding: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{user_id}")
async def get_onboarding_status(user_id: str):
    """Check if user has completed onboarding."""
    try:
        async with db_manager.get_session() as session:
            from sqlalchemy import select
            from database import UserProfile
            result = await session.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                return {
                    "user_id": user_id,
                    "onboarding_completed": user.onboarding_completed,
                    "has_profile": True
                }
            else:
                return {
                    "user_id": user_id,
                    "onboarding_completed": False,
                    "has_profile": False
                }
    except Exception as e:
        logger.error(f"Error getting onboarding status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

