"""User Learning Engine - ML-based learning from user interactions."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import select, and_, func, desc
from collections import defaultdict

from database import (
    db_manager,
    UserInteraction,
    FeedItem,
    InterestWeight,
    UserProfile
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserLearningEngine:
    """
    Learning engine that adapts to user behavior.
    
    Analyzes user interactions and updates keyword weights automatically.
    """
    
    def __init__(self):
        """Initialize learning engine."""
        pass
    
    def calculate_article_engagement(
        self,
        view_duration_seconds: Optional[int] = None,
        scroll_depth: Optional[float] = None,
        clicked_read_more: bool = False,
        is_liked: bool = False,
        is_disliked: bool = False,
        is_saved: bool = False
    ) -> float:
        """
        Calculate engagement score for an article.
        
        Factors:
        - View duration: 0-10s = 0.1, 10-30s = 0.5, 30s+ = 1.0
        - Scroll depth: proportional (0-1)
        - Click read more: +0.3
        - Like: +0.5
        - Save: +0.4
        - Dislike: -1.0 (complete rejection)
        
        Args:
            view_duration_seconds: Duration of view
            scroll_depth: Scroll depth (0-1)
            clicked_read_more: Whether user clicked read more
            is_liked: Whether article was liked
            is_disliked: Whether article was disliked
            is_saved: Whether article was saved
            
        Returns:
            Engagement score (0-1, or negative for dislike)
        """
        if is_disliked:
            return -1.0
        
        score = 0.0
        
        # View duration
        if view_duration_seconds is not None:
            if view_duration_seconds < 10:
                score += 0.1
            elif view_duration_seconds < 30:
                score += 0.5
            else:
                score += 1.0
        
        # Scroll depth
        if scroll_depth is not None:
            score += scroll_depth * 0.3
        
        # Explicit actions
        if clicked_read_more:
            score += 0.3
        if is_liked:
            score += 0.5
        if is_saved:
            score += 0.4
        
        return min(1.0, score)
    
    async def update_keyword_weights(self, user_id: str, days_back: int = 30) -> Dict[str, float]:
        """
        Update keyword weights based on user interaction history.
        
        Logic:
        - If user frequently engages with articles containing keyword X → increase weight
        - If user ignores articles with keyword Y → decrease weight
        - Automatically add new keywords from highly engaged articles
        
        Args:
            user_id: User identifier
            days_back: Number of days to analyze
            
        Returns:
            Dictionary of keyword weights
        """
        try:
            since = datetime.now() - timedelta(days=days_back)
            
            async with db_manager.get_session() as session:
                # Get all interactions with matched keywords
                result = await session.execute(
                    select(UserInteraction, FeedItem)
                    .join(
                        FeedItem,
                        and_(
                            FeedItem.user_id == UserInteraction.user_id,
                            FeedItem.article_id == UserInteraction.article_id
                        ),
                        isouter=True
                    )
                    .where(
                        and_(
                            UserInteraction.user_id == user_id,
                            UserInteraction.created_at >= since
                        )
                    )
                )
                interactions = result.all()
                
                # Analyze keyword engagement
                keyword_stats = defaultdict(lambda: {'total': 0, 'engagement_sum': 0.0, 'count': 0})
                
                for interaction, feed_item in interactions:
                    # Calculate engagement for this interaction
                    engagement = self.calculate_article_engagement(
                        view_duration_seconds=interaction.view_duration_seconds,
                        scroll_depth=interaction.scroll_depth,
                        clicked_read_more=interaction.clicked_read_more,
                        is_liked=feed_item.is_liked if feed_item else False,
                        is_disliked=feed_item.is_disliked if feed_item else False,
                        is_saved=feed_item.is_saved if feed_item else False
                    )
                    
                    # Extract keywords
                    keywords = []
                    if interaction.matched_keywords:
                        keywords = interaction.matched_keywords
                    elif feed_item and feed_item.matched_keywords:
                        keywords = feed_item.matched_keywords
                    
                    # Update stats for each keyword
                    for keyword in keywords:
                        keyword_stats[keyword]['total'] += 1
                        keyword_stats[keyword]['engagement_sum'] += engagement
                        keyword_stats[keyword]['count'] += 1
                
                # Calculate weights (average engagement)
                keyword_weights = {}
                for keyword, stats in keyword_stats.items():
                    if stats['count'] > 0:
                        avg_engagement = stats['engagement_sum'] / stats['count']
                        # Normalize to 0-1 range, with boost for high engagement
                        weight = max(0.0, min(1.0, (avg_engagement + 0.5) / 1.5))
                        keyword_weights[keyword] = weight
                
                # Save to database
                for keyword, weight in keyword_weights.items():
                    # Check if weight exists
                    weight_result = await session.execute(
                        select(InterestWeight).where(
                            and_(
                                InterestWeight.user_id == user_id,
                                InterestWeight.keyword == keyword
                            )
                        )
                    )
                    existing_weight = weight_result.scalar_one_or_none()
                    
                    if existing_weight:
                        # Update existing weight (exponential moving average)
                        new_weight = 0.7 * existing_weight.weight + 0.3 * weight
                        existing_weight.weight = new_weight
                        existing_weight.engagement_count = keyword_stats[keyword]['count']
                        existing_weight.last_seen_at = datetime.now()
                        existing_weight.updated_at = datetime.now()
                    else:
                        # Create new weight
                        new_weight_entry = InterestWeight(
                            user_id=user_id,
                            keyword=keyword,
                            weight=weight,
                            engagement_count=keyword_stats[keyword]['count']
                        )
                        session.add(new_weight_entry)
                
                await session.flush()
                
                logger.info(
                    f"Updated {len(keyword_weights)} keyword weights for user {user_id}"
                )
                return keyword_weights
                
        except Exception as e:
            logger.error(f"Error updating keyword weights: {e}", exc_info=True)
            return {}
    
    async def get_keyword_weights(self, user_id: str) -> Dict[str, float]:
        """
        Get current keyword weights for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of keyword weights
        """
        try:
            async with db_manager.get_session() as session:
                result = await session.execute(
                    select(InterestWeight)
                    .where(InterestWeight.user_id == user_id)
                    .order_by(desc(InterestWeight.weight))
                )
                weights = result.scalars().all()
                
                return {w.keyword: w.weight for w in weights}
                
        except Exception as e:
            logger.error(f"Error getting keyword weights: {e}")
            return {}
    
    async def discover_new_interests(
        self,
        user_id: str,
        min_engagement_threshold: float = 0.7,
        limit: int = 10
    ) -> List[str]:
        """
        Discover new potential interests based on high-engagement articles.
        
        Finds keywords from articles user engaged with heavily.
        
        Args:
            user_id: User identifier
            min_engagement_threshold: Minimum engagement score to consider
            limit: Maximum number of new interests to discover
            
        Returns:
            List of suggested keywords
        """
        try:
            async with db_manager.get_session() as session:
                # Get highly engaged articles
                result = await session.execute(
                    select(FeedItem)
                    .where(
                        and_(
                            FeedItem.user_id == user_id,
                            FeedItem.is_liked == True
                        )
                    )
                    .order_by(desc(FeedItem.relevance_score))
                    .limit(50)
                )
                liked_items = result.scalars().all()
                
                # Extract keywords
                keyword_frequency = defaultdict(int)
                
                for item in liked_items:
                    if item.matched_keywords:
                        for keyword in item.matched_keywords:
                            keyword_frequency[keyword] += 1
                
                # Get current keyword weights
                current_weights = await self.get_keyword_weights(user_id)
                
                # Find new keywords (not in current weights)
                new_keywords = []
                for keyword, freq in sorted(
                    keyword_frequency.items(),
                    key=lambda x: x[1],
                    reverse=True
                ):
                    if keyword not in current_weights and freq >= 2:
                        new_keywords.append(keyword)
                        if len(new_keywords) >= limit:
                            break
                
                logger.info(
                    f"Discovered {len(new_keywords)} new interests for user {user_id}"
                )
                return new_keywords
                
        except Exception as e:
            logger.error(f"Error discovering new interests: {e}")
            return []
    
    async def predict_relevance(
        self,
        user_id: str,
        article_keywords: List[str]
    ) -> float:
        """
        Predict relevance of an article based on learned preferences.
        
        Args:
            user_id: User identifier
            article_keywords: Keywords in the article
            
        Returns:
            Predicted relevance score (0-1)
        """
        try:
            if not article_keywords:
                return 0.5  # Neutral score
            
            # Get keyword weights
            weights = await self.get_keyword_weights(user_id)
            
            if not weights:
                return 0.5  # No learned preferences yet
            
            # Calculate weighted score
            total_weight = 0.0
            matched_count = 0
            
            for keyword in article_keywords:
                if keyword in weights:
                    total_weight += weights[keyword]
                    matched_count += 1
            
            if matched_count == 0:
                return 0.5  # No matching keywords
            
            # Average weight, with boost for multiple matches
            base_score = total_weight / matched_count
            match_boost = min(0.2, matched_count * 0.05)
            
            return min(1.0, base_score + match_boost)
            
        except Exception as e:
            logger.error(f"Error predicting relevance: {e}")
            return 0.5
    
    async def get_learning_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get insights about what the system has learned.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with learning insights
        """
        try:
            weights = await self.get_keyword_weights(user_id)
            
            # Sort by weight
            sorted_weights = sorted(
                weights.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Categorize
            strong_interests = [(k, v) for k, v in sorted_weights if v > 0.7]
            moderate_interests = [(k, v) for k, v in sorted_weights if 0.4 < v <= 0.7]
            weak_interests = [(k, v) for k, v in sorted_weights if v <= 0.4]
            
            return {
                "total_learned_keywords": len(weights),
                "strong_interests": strong_interests[:10],
                "moderate_interests": moderate_interests[:10],
                "weak_interests": weak_interests[:10],
                "learning_status": "active" if len(weights) > 5 else "learning"
            }
            
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return {}


# Global instance
learning_engine = UserLearningEngine()

