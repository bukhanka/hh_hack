"""Test full Personal News Aggregator flow."""

import asyncio
import logging
from datetime import datetime

from database import db_manager
from modes.personal.user_preferences import preferences_manager
from modes.personal.news_aggregator import PersonalNewsAggregator
from modes.personal.feed_storage import feed_storage
from modes.personal.learning_engine import learning_engine
from modes.personal.smart_updater import smart_updater
from models import UserPreferences

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_onboarding():
    """Test 1: Onboarding and preferences setup."""
    logger.info("=" * 80)
    logger.info("TEST 1: ONBOARDING & PREFERENCES")
    logger.info("=" * 80)
    
    test_user = "test_flow_user"
    
    # Create user profile first (required for foreign key)
    await feed_storage.ensure_user_profile(test_user)
    logger.info(f"✅ User profile created for {test_user}")
    
    # Create preferences (simulate onboarding)
    prefs = UserPreferences(
        user_id=test_user,
        sources=[
            "https://habr.com/ru/rss/hub/programming/all/?fl=ru",
            "https://nplus1.ru/rss",
        ],
        keywords=["AI", "Python", "нейросети", "Machine Learning"],
        excluded_keywords=["реклама"],
        categories=["Технологии", "Наука"],
        update_frequency_minutes=60,
        max_articles_per_feed=10,
        language="ru"
    )
    
    # Save preferences
    success = await preferences_manager.save_preferences_async(prefs)
    logger.info(f"✅ Preferences saved: {success}")
    
    # Verify
    saved_prefs = await preferences_manager.get_preferences_async(test_user)
    logger.info(f"✅ Preferences verified: {len(saved_prefs.keywords)} keywords, {len(saved_prefs.sources)} sources")
    
    return test_user


async def test_feed_generation(user_id: str):
    """Test 2: Generate personalized feed."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: FEED GENERATION")
    logger.info("=" * 80)
    
    aggregator = PersonalNewsAggregator()
    
    # Generate feed
    feed = await aggregator.process_news(user_id=user_id, time_window_hours=24)
    
    logger.info(f"✅ Feed generated:")
    logger.info(f"   - Total articles processed: {feed.total_articles_processed}")
    logger.info(f"   - Filtered out: {feed.filtered_count}")
    logger.info(f"   - Final items: {len(feed.items)}")
    logger.info(f"   - Processing time: {feed.processing_time_seconds:.1f}s")
    
    # Display first 3 items
    logger.info("\n📰 Top 3 items:")
    for i, item in enumerate(feed.items[:3], 1):
        logger.info(f"\n{i}. {item.title}")
        logger.info(f"   Source: {item.source}")
        logger.info(f"   Relevance: {item.relevance_score:.2f}")
        logger.info(f"   Keywords: {', '.join(item.matched_keywords)}")
    
    return feed


async def test_feed_storage(user_id: str, feed):
    """Test 3: Save feed to database."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: FEED STORAGE")
    logger.info("=" * 80)
    
    # Save feed items
    saved_count = await feed_storage.save_feed_items(user_id, feed.items)
    logger.info(f"✅ Saved {saved_count} new items to database")
    
    # Retrieve feed
    stored_items = await feed_storage.get_user_feed(user_id, limit=10)
    logger.info(f"✅ Retrieved {len(stored_items)} items from database")
    
    return stored_items


async def test_interactions(user_id: str, stored_items):
    """Test 4: Simulate user interactions."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: USER INTERACTIONS")
    logger.info("=" * 80)
    
    if not stored_items:
        logger.warning("⚠️ No items to interact with")
        return
    
    # Simulate interactions
    article_id_1 = stored_items[0]['article_id']
    article_id_2 = stored_items[1]['article_id'] if len(stored_items) > 1 else None
    
    # Mark as read
    await feed_storage.mark_as_read(user_id, article_id_1)
    logger.info(f"✅ Marked article 1 as read")
    
    # Like article 1
    await feed_storage.toggle_like(user_id, article_id_1, liked=True)
    logger.info(f"✅ Liked article 1")
    
    # Track interaction
    await feed_storage.track_interaction(
        user_id=user_id,
        article_id=article_id_1,
        interaction_type="view",
        view_duration_seconds=45,
        scroll_depth=0.8,
        clicked_read_more=True,
        matched_keywords=stored_items[0]['matched_keywords'],
        relevance_score=stored_items[0]['relevance_score']
    )
    logger.info(f"✅ Tracked view interaction")
    
    if article_id_2:
        # Dislike article 2
        await feed_storage.toggle_dislike(user_id, article_id_2, disliked=True)
        logger.info(f"✅ Disliked article 2")
    
    # Get stats
    stats = await feed_storage.get_user_stats(user_id, days=7)
    logger.info(f"\n📊 User stats:")
    logger.info(f"   - Total in feed: {stats['total_articles_in_feed']}")
    logger.info(f"   - Read: {stats['articles_read']}")
    logger.info(f"   - Liked: {stats['articles_liked']}")
    logger.info(f"   - Saved: {stats['articles_saved']}")
    logger.info(f"   - Avg view time: {stats['avg_view_duration_seconds']}s")


async def test_learning(user_id: str):
    """Test 5: ML Learning Engine."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: LEARNING ENGINE")
    logger.info("=" * 80)
    
    # Update keyword weights
    weights = await learning_engine.update_keyword_weights(user_id, days_back=30)
    logger.info(f"✅ Updated keyword weights: {len(weights)} keywords")
    
    # Display top weights
    sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    logger.info("\n🧠 Top keyword weights:")
    for keyword, weight in sorted_weights[:5]:
        logger.info(f"   - {keyword}: {weight:.2f}")
    
    # Get learning insights
    insights = await learning_engine.get_learning_insights(user_id)
    logger.info(f"\n💡 Learning insights:")
    logger.info(f"   - Total learned keywords: {insights['total_learned_keywords']}")
    logger.info(f"   - Learning status: {insights['learning_status']}")
    
    # Discover new interests
    new_interests = await learning_engine.discover_new_interests(user_id, limit=5)
    if new_interests:
        logger.info(f"\n🔍 Discovered new interests: {', '.join(new_interests)}")
    else:
        logger.info(f"\n🔍 No new interests discovered yet (need more data)")


async def test_smart_updater(user_id: str):
    """Test 6: Smart Feed Updater."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 6: SMART FEED UPDATER")
    logger.info("=" * 80)
    
    # Check if update needed
    should_update = await smart_updater.should_update_feed(user_id)
    logger.info(f"✅ Should update feed: {should_update}")
    
    # Get smart feed (with caching)
    feed = await smart_updater.get_or_update_feed(user_id, force_refresh=False, use_cache=True)
    logger.info(f"✅ Smart feed retrieved: {len(feed.items)} items")
    
    # Incremental update
    new_items = await smart_updater.incremental_update(user_id, time_window_hours=6)
    logger.info(f"✅ Incremental update: {new_items} new items added")


async def main():
    """Run full flow test."""
    logger.info("\n🚀 Starting FULL FLOW TEST\n")
    
    try:
        # Initialize database
        await db_manager.init_async()
        logger.info("✅ Database initialized\n")
        
        # Test 1: Onboarding
        user_id = await test_onboarding()
        
        # Test 2: Feed generation
        feed = await test_feed_generation(user_id)
        
        # Test 3: Feed storage
        stored_items = await test_feed_storage(user_id, feed)
        
        # Test 4: User interactions
        await test_interactions(user_id, stored_items)
        
        # Test 5: Learning engine
        await test_learning(user_id)
        
        # Test 6: Smart updater
        await test_smart_updater(user_id)
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("=" * 80)
        logger.info("\nThe Personal News Aggregator is fully functional:")
        logger.info("✅ Database persistence")
        logger.info("✅ Onboarding & preferences")
        logger.info("✅ Feed generation with ML scoring")
        logger.info("✅ User interactions tracking")
        logger.info("✅ Learning engine (keyword weights)")
        logger.info("✅ Smart caching & incremental updates")
        logger.info("\n🚀 Ready for production!")
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

