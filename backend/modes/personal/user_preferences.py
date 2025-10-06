"""User preferences management for personal news aggregator."""

import logging
from typing import Optional, List
from datetime import datetime

from models import UserPreferences
from database import db_manager, UserPreferencesDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserPreferencesManager:
    """Manages user preferences for personal news aggregator."""
    
    def __init__(self):
        """Initialize preferences manager."""
        # In-memory cache for performance
        self._cache = {}
    
    def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """
        Get user preferences from database.
        
        Args:
            user_id: User identifier
            
        Returns:
            UserPreferences or None if not found
        """
        # Check cache first
        if user_id in self._cache:
            return self._cache[user_id]
        
        # Load from database
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in async context, can't use asyncio.run
                return None
            else:
                prefs = asyncio.run(self._get_preferences_async(user_id))
                if prefs:
                    self._cache[user_id] = prefs
                return prefs
        except Exception as e:
            logger.error(f"Failed to get preferences from DB: {e}")
            return None
    
    async def _get_preferences_async(self, user_id: str) -> Optional[UserPreferences]:
        """Async helper to get preferences from DB."""
        async with db_manager.get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UserPreferencesDB).where(UserPreferencesDB.user_id == user_id)
            )
            db_prefs = result.scalar_one_or_none()
            
            if db_prefs:
                return UserPreferences(
                    user_id=db_prefs.user_id,
                    sources=db_prefs.sources or [],
                    keywords=db_prefs.keywords or [],
                    excluded_keywords=db_prefs.excluded_keywords or [],
                    categories=db_prefs.categories or [],
                    update_frequency_minutes=db_prefs.update_frequency_minutes,
                    max_articles_per_feed=db_prefs.max_articles_per_feed,
                    language=db_prefs.language,
                    created_at=db_prefs.created_at,
                    updated_at=db_prefs.updated_at
                )
            return None
    
    def save_preferences(self, preferences: UserPreferences) -> bool:
        """
        Save user preferences to database.
        
        Args:
            preferences: UserPreferences object
            
        Returns:
            True if saved successfully
        """
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in async context, can't use asyncio.run
                return False
            else:
                asyncio.run(self._save_preferences_async(preferences))
                # Update cache
                self._cache[preferences.user_id] = preferences
                logger.info(f"Saved preferences for user {preferences.user_id}: keywords={preferences.keywords}")
                return True
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}", exc_info=True)
            return False
    
    async def _save_preferences_async(self, preferences: UserPreferences):
        """Async helper to save preferences to DB."""
        from sqlalchemy import select
        from sqlalchemy.dialects.postgresql import insert
        
        async with db_manager.get_session() as session:
            preferences.updated_at = datetime.now()
            
            # Upsert (insert or update)
            stmt = insert(UserPreferencesDB).values(
                user_id=preferences.user_id,
                sources=preferences.sources,
                keywords=preferences.keywords,
                excluded_keywords=preferences.excluded_keywords,
                categories=preferences.categories,
                update_frequency_minutes=preferences.update_frequency_minutes,
                max_articles_per_feed=preferences.max_articles_per_feed,
                language=preferences.language,
                created_at=preferences.created_at,
                updated_at=preferences.updated_at
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=['user_id'],
                set_=dict(
                    sources=preferences.sources,
                    keywords=preferences.keywords,
                    excluded_keywords=preferences.excluded_keywords,
                    categories=preferences.categories,
                    update_frequency_minutes=preferences.update_frequency_minutes,
                    max_articles_per_feed=preferences.max_articles_per_feed,
                    language=preferences.language,
                    updated_at=preferences.updated_at
                )
            )
            await session.execute(stmt)
            await session.flush()
    
    async def get_preferences_async(self, user_id: str) -> Optional[UserPreferences]:
        """
        Get user preferences from database (async version).
        
        Args:
            user_id: User identifier
            
        Returns:
            UserPreferences or None if not found
        """
        # Check cache first
        if user_id in self._cache:
            return self._cache[user_id]
        
        # Load from database
        prefs = await self._get_preferences_async(user_id)
        if prefs:
            self._cache[user_id] = prefs
        return prefs
    
    async def save_preferences_async(self, preferences: UserPreferences) -> bool:
        """
        Save user preferences to database (async version).
        
        Args:
            preferences: UserPreferences object
            
        Returns:
            True if saved successfully
        """
        try:
            await self._save_preferences_async(preferences)
            # Update cache
            self._cache[preferences.user_id] = preferences
            logger.info(f"Saved preferences for user {preferences.user_id}: keywords={preferences.keywords}")
            return True
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}", exc_info=True)
            return False
    
    async def get_or_create_default_async(self, user_id: str) -> UserPreferences:
        """
        Get user preferences or create default ones (async version).
        
        Args:
            user_id: User identifier
            
        Returns:
            UserPreferences object
        """
        prefs = await self.get_preferences_async(user_id)
        if prefs:
            return prefs
        
        # Create default preferences
        default_prefs = UserPreferences(
            user_id=user_id,
            sources=self._get_default_sources(),
            keywords=[],
            excluded_keywords=["реклама", "спам", "казино", "азартн", "ставк"],
            categories=[
                "технологии", "технология", "it", "программирование", "разработка", "софт",
                "наука", "исследован", "учен", "научн",
                "бизнес", "экономика", "финанс", "рынок", "компани"
            ],
            update_frequency_minutes=60,
            max_articles_per_feed=20,
            language="ru"
        )
        
        await self.save_preferences_async(default_prefs)
        return default_prefs
    
    def get_or_create_default(self, user_id: str) -> UserPreferences:
        """
        Get user preferences or create default ones (sync version - deprecated).
        
        Args:
            user_id: User identifier
            
        Returns:
            UserPreferences object
        """
        prefs = self.get_preferences(user_id)
        if prefs:
            return prefs
        
        # Create default preferences
        default_prefs = UserPreferences(
            user_id=user_id,
            sources=self._get_default_sources(),
            keywords=[],
            excluded_keywords=["реклама", "спам", "казино", "азартн", "ставк"],
            categories=[
                "технологии", "технология", "it", "программирование", "разработка", "софт",
                "наука", "исследован", "учен", "научн",
                "бизнес", "экономика", "финанс", "рынок", "компани"
            ],
            update_frequency_minutes=60,
            max_articles_per_feed=20,
            language="ru"
        )
        
        self.save_preferences(default_prefs)
        return default_prefs
    
    def _get_default_sources(self) -> List[str]:
        """Get default RSS sources."""
        return [
            # Технологии
            "https://habr.com/ru/rss/hub/programming/all/?fl=ru",
            "https://www.cnews.ru/inc/rss/news.xml",
            
            # Наука
            "https://nplus1.ru/rss",
            "https://www.popmech.ru/feed/",
            
            # Бизнес
            "https://www.rbc.ru/v10/rss/news/news.rss",
            "https://www.vedomosti.ru/rss/news",
            
            # Общие новости
            "https://lenta.ru/rss",
            "https://tass.ru/rss/v2.xml",
        ]
    
    async def add_source_async(self, user_id: str, source_url: str) -> bool:
        """Add RSS source to user preferences (async version)."""
        prefs = await self.get_or_create_default_async(user_id)
        
        if source_url not in prefs.sources:
            prefs.sources.append(source_url)
            return await self.save_preferences_async(prefs)
        
        return True
    
    async def remove_source_async(self, user_id: str, source_url: str) -> bool:
        """Remove RSS source from user preferences (async version)."""
        prefs = await self.get_or_create_default_async(user_id)
        
        if source_url in prefs.sources:
            prefs.sources.remove(source_url)
            return await self.save_preferences_async(prefs)
        
        return True
    
    async def add_keyword_async(self, user_id: str, keyword: str) -> bool:
        """Add keyword filter (async version)."""
        prefs = await self.get_or_create_default_async(user_id)
        
        if keyword not in prefs.keywords:
            prefs.keywords.append(keyword.lower())
            return await self.save_preferences_async(prefs)
        
        return True
    
    async def remove_keyword_async(self, user_id: str, keyword: str) -> bool:
        """Remove keyword filter (async version)."""
        prefs = await self.get_or_create_default_async(user_id)
        
        if keyword.lower() in prefs.keywords:
            prefs.keywords.remove(keyword.lower())
            return await self.save_preferences_async(prefs)
        
        return True
    
    def add_source(self, user_id: str, source_url: str) -> bool:
        """
        Add RSS source to user preferences.
        
        Args:
            user_id: User identifier
            source_url: RSS feed URL
            
        Returns:
            True if added successfully
        """
        prefs = self.get_or_create_default(user_id)
        
        if source_url not in prefs.sources:
            prefs.sources.append(source_url)
            return self.save_preferences(prefs)
        
        return True
    
    def remove_source(self, user_id: str, source_url: str) -> bool:
        """
        Remove RSS source from user preferences.
        
        Args:
            user_id: User identifier
            source_url: RSS feed URL
            
        Returns:
            True if removed successfully
        """
        prefs = self.get_or_create_default(user_id)
        
        if source_url in prefs.sources:
            prefs.sources.remove(source_url)
            return self.save_preferences(prefs)
        
        return True
    
    def add_keyword(self, user_id: str, keyword: str) -> bool:
        """Add keyword filter."""
        prefs = self.get_or_create_default(user_id)
        
        if keyword not in prefs.keywords:
            prefs.keywords.append(keyword.lower())
            return self.save_preferences(prefs)
        
        return True
    
    def remove_keyword(self, user_id: str, keyword: str) -> bool:
        """Remove keyword filter."""
        prefs = self.get_or_create_default(user_id)
        
        if keyword.lower() in prefs.keywords:
            prefs.keywords.remove(keyword.lower())
            return self.save_preferences(prefs)
        
        return True
    
    @staticmethod
    def get_popular_sources() -> dict:
        """
        Get popular RSS sources by category.
        
        Returns:
            Dictionary of categories and their sources
        """
        return {
            "Технологии": [
                {"name": "Habr", "url": "https://habr.com/ru/rss/hub/programming/all/?fl=ru"},
                {"name": "CNews", "url": "https://www.cnews.ru/inc/rss/news.xml"},
                {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
                {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
            ],
            "Наука": [
                {"name": "N+1", "url": "https://nplus1.ru/rss"},
                {"name": "PopMech", "url": "https://www.popmech.ru/feed/"},
                {"name": "Элементы", "url": "https://elementy.ru/rss/news"},
            ],
            "Бизнес": [
                {"name": "РБК", "url": "https://www.rbc.ru/v10/rss/news/news.rss"},
                {"name": "Ведомости", "url": "https://www.vedomosti.ru/rss/news"},
                {"name": "Коммерсант", "url": "https://www.kommersant.ru/RSS/news.xml"},
            ],
            "Общие новости": [
                {"name": "Lenta.ru", "url": "https://lenta.ru/rss"},
                {"name": "TASS", "url": "https://tass.ru/rss/v2.xml"},
                {"name": "РИА Новости", "url": "https://ria.ru/export/rss2/archive/index.xml"},
            ],
            "Спорт": [
                {"name": "Чемпионат", "url": "https://www.championat.com/rss/news.xml"},
                {"name": "Sports.ru", "url": "https://www.sports.ru/rss/"},
            ],
        }


# Global instance
preferences_manager = UserPreferencesManager()
