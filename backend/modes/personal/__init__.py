"""Personal News Aggregator mode - personalized news feed with summaries."""

from .news_aggregator import PersonalNewsAggregator
from .summary_generator import SummaryGenerator
from .user_preferences import UserPreferences, UserPreferencesManager

__all__ = ['PersonalNewsAggregator', 'SummaryGenerator', 'UserPreferences', 'UserPreferencesManager']
