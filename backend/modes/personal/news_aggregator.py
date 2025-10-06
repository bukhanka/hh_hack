"""Personal news aggregator - personalized news feed with summaries."""

import asyncio
import logging
import time
from datetime import datetime
from typing import List, Optional, Dict

from config import settings
from models import NewsArticle, PersonalNewsItem, PersonalFeedResponse, UserPreferences
from news_collector import NewsCollector
from deduplication import NewsDeduplicator
from modes.personal.summary_generator import SummaryGenerator
from modes.personal.user_preferences import UserPreferencesManager
from modes.personal.learning_engine import learning_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonalNewsAggregator:
    """Main aggregator for personalized news feed."""
    
    def __init__(self):
        """Initialize all components."""
        self.summary_generator = SummaryGenerator()
        self.deduplicator = NewsDeduplicator()
        self.preferences_manager = UserPreferencesManager()
    
    async def _calculate_relevance_score(
        self,
        article: NewsArticle,
        preferences: UserPreferences,
        user_id: str
    ) -> tuple[float, List[str]]:
        """
        Calculate relevance score based on user preferences and ML learning.
        
        Uses learned keyword weights from user behavior for smarter predictions.
        
        Args:
            article: NewsArticle object
            preferences: User preferences
            user_id: User identifier for ML predictions
            
        Returns:
            Tuple of (relevance_score, matched_keywords)
        """
        matched_keywords = []
        matched_categories = []
        
        # Check title and content for keywords
        text_to_check = f"{article.title} {article.content}".lower()
        
        # Find matched keywords
        for keyword in preferences.keywords:
            if keyword.lower() in text_to_check:
                matched_keywords.append(keyword)
        
        # Find matched categories (if no keywords specified)
        if not preferences.keywords:
            for category in preferences.categories:
                if category.lower() in text_to_check:
                    matched_categories.append(category)
        
        # Combine matched items for scoring
        all_matches = matched_keywords + matched_categories
        
        # If we have matched items, use ML to predict relevance
        if all_matches:
            try:
                ml_score = await learning_engine.predict_relevance(user_id, all_matches)
                logger.debug(
                    f"ML predicted relevance for article '{article.title[:50]}...': "
                    f"{ml_score:.2f} (matches: {', '.join(all_matches)})"
                )
                return ml_score, all_matches
            except Exception as e:
                logger.warning(f"Failed to get ML prediction, falling back to basic scoring: {e}")
        
        # Fallback: basic scoring
        score = 0.5  # Base score
        
        # Boost score for matched keywords (higher weight)
        for keyword in matched_keywords:
            score += 0.2
        
        # Boost score for matched categories (lower weight)
        for category in matched_categories:
            score += 0.1
        
        # Cap at 1.0
        score = min(1.0, score)
        
        return score, all_matches
    
    def _should_filter_article(
        self,
        article: NewsArticle,
        preferences: UserPreferences
    ) -> bool:
        """
        Check if article should be filtered out.
        
        Args:
            article: NewsArticle object
            preferences: User preferences
            
        Returns:
            True if article should be filtered out
        """
        text_to_check = f"{article.title} {article.content}".lower()
        
        # Filter by excluded keywords (always applied)
        for excluded_keyword in preferences.excluded_keywords:
            if excluded_keyword.lower() in text_to_check:
                logger.info(f"✗ Filtering article due to excluded keyword '{excluded_keyword}': {article.title[:70]}")
                return True
        
        # If user has specified keywords, filter out articles that don't match ANY of them
        if preferences.keywords:
            has_match = False
            for keyword in preferences.keywords:
                if keyword.lower() in text_to_check:
                    has_match = True
                    break
            
            if not has_match:
                logger.info(f"✗ Filtering article (no keyword match): {article.title[:70]}")
                return True
        # If no keywords specified, but categories are, filter by categories
        elif preferences.categories:
            has_category_match = False
            for category in preferences.categories:
                if category.lower() in text_to_check:
                    has_category_match = True
                    break
            
            if not has_category_match:
                logger.info(f"✗ Filtering article (no category match): {article.title[:70]}")
                return True
        
        return False
    
    async def process_news(
        self,
        user_id: str = "default",
        time_window_hours: Optional[int] = None,
        custom_sources: Optional[List[str]] = None,
        force_preferences: Optional[UserPreferences] = None
    ) -> PersonalFeedResponse:
        """
        Process news and return personalized feed.
        
        Args:
            user_id: User identifier
            time_window_hours: Hours to look back (default from preferences)
            custom_sources: Optional custom RSS feeds (overrides user preferences)
            force_preferences: Force specific preferences (for one-time use)
            
        Returns:
            PersonalFeedResponse with filtered and summarized news
        """
        start_time = time.time()
        
        # Get user preferences
        if force_preferences:
            preferences = force_preferences
        else:
            preferences = await self.preferences_manager.get_or_create_default_async(user_id)
        
        time_window_hours = time_window_hours or 24
        
        # Determine sources
        sources = custom_sources or preferences.sources
        
        if not sources:
            logger.warning("No sources configured, using defaults")
            sources = self.preferences_manager._get_default_sources()
        
        logger.info(
            f"Processing personal feed for user {user_id}: "
            f"sources={len(sources)}, window={time_window_hours}h"
        )
        logger.info(
            f"Filters: keywords={len(preferences.keywords)}, "
            f"categories={len(preferences.categories)}, "
            f"excluded={len(preferences.excluded_keywords)}"
        )
        if preferences.keywords:
            logger.info(f"Keywords: {', '.join(preferences.keywords)}")
        if preferences.categories:
            logger.info(f"Categories: {', '.join(preferences.categories[:5])}{'...' if len(preferences.categories) > 5 else ''}")
        if preferences.excluded_keywords:
            logger.info(f"Excluded: {', '.join(preferences.excluded_keywords)}")
        
        # Step 1: Collect news from RSS feeds
        logger.info("Step 1: Collecting news from RSS feeds...")
        async with NewsCollector() as collector:
            articles = await collector.collect_news(
                time_window_hours=time_window_hours,
                custom_feeds=sources
            )
        
        logger.info(f"Collected {len(articles)} articles")
        
        if not articles:
            logger.warning("No articles collected")
            return PersonalFeedResponse(
                items=[],
                total_articles_processed=0,
                filtered_count=0,
                time_window_hours=time_window_hours,
                processing_time_seconds=time.time() - start_time,
                user_id=user_id
            )
        
        # Step 2: Deduplicate and cluster
        logger.info("Step 2: Deduplicating...")
        clusters = await self.deduplicator.cluster_articles_async(articles)
        logger.info(f"Created {len(clusters)} unique clusters")
        
        # Step 3: Filter and score articles
        logger.info("Step 3: Filtering and scoring...")
        filtered_articles = []
        filtered_count = 0
        
        for cluster_id, cluster_articles in clusters.items():
            # Take the first article from each cluster (representative)
            representative_article = cluster_articles[0]
            
            # Apply filters
            if self._should_filter_article(representative_article, preferences):
                filtered_count += 1
                continue
            
            # Calculate relevance score (with ML learning)
            relevance_score, matched_keywords = await self._calculate_relevance_score(
                representative_article,
                preferences,
                user_id
            )
            
            filtered_articles.append({
                'article': representative_article,
                'cluster_size': len(cluster_articles),
                'relevance_score': relevance_score,
                'matched_keywords': matched_keywords
            })
        
        logger.info(f"Filtered: {filtered_count}, Remaining: {len(filtered_articles)}")
        
        # Step 4: Sort by relevance and limit
        filtered_articles.sort(
            key=lambda x: (x['relevance_score'], x['article'].published_at),
            reverse=True
        )
        
        # Limit to max_articles_per_feed
        filtered_articles = filtered_articles[:preferences.max_articles_per_feed]
        
        # Step 5: Generate summaries in parallel
        logger.info(f"Step 4: Generating summaries for {len(filtered_articles)} articles...")
        
        # Generate summaries for all articles
        articles_to_summarize = [item['article'] for item in filtered_articles]
        
        # Generate summaries in parallel
        summaries = await self.summary_generator.generate_batch_summaries_async(articles_to_summarize)
        
        logger.info(f"Generated {len(summaries)} summaries")
        
        # Step 6: Create PersonalNewsItem objects
        items = []
        for item_data in filtered_articles:
            article = item_data['article']
            summary = summaries.get(article.id, article.content[:200] + "...")
            
            personal_item = PersonalNewsItem(
                id=article.id,
                title=article.title,
                summary=summary,
                url=article.url,
                source=article.source,
                published_at=article.published_at,
                author=article.author,
                relevance_score=item_data['relevance_score'],
                matched_keywords=item_data['matched_keywords'],
                cluster_size=item_data['cluster_size']
            )
            items.append(personal_item)
        
        processing_time = time.time() - start_time
        
        logger.info(
            f"Personal feed processing complete: "
            f"{len(items)} items in {processing_time:.1f}s"
        )
        
        return PersonalFeedResponse(
            items=items,
            total_articles_processed=len(articles),
            filtered_count=filtered_count,
            time_window_hours=time_window_hours,
            processing_time_seconds=processing_time,
            user_id=user_id
        )


async def main():
    """Test the personal news aggregator."""
    aggregator = PersonalNewsAggregator()
    
    print("=" * 80)
    print("Personal News Aggregator - Test Run")
    print("=" * 80)
    print()
    
    # Test with default preferences
    response = await aggregator.process_news(
        user_id="test_user",
        time_window_hours=24
    )
    
    print(f"\nProcessed {response.total_articles_processed} articles in {response.processing_time_seconds:.1f}s")
    print(f"Filtered out: {response.filtered_count}")
    print(f"Final feed: {len(response.items)} items\n")
    
    for i, item in enumerate(response.items[:5], 1):
        print("=" * 80)
        print(f"ITEM #{i}: {item.title}")
        print("=" * 80)
        print(f"Source: {item.source}")
        print(f"Published: {item.published_at}")
        print(f"Relevance Score: {item.relevance_score:.2f}")
        if item.matched_keywords:
            print(f"Matched Keywords: {', '.join(item.matched_keywords)}")
        print(f"\nSummary:\n{item.summary}")
        print(f"\nURL: {item.url}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
