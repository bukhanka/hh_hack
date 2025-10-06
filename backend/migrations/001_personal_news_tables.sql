-- Migration 001: Personal News Aggregator Tables
-- Adds tables for user profiles, preferences, feed items, and interactions

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- User Profiles
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255),
    display_name VARCHAR(100),
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_last_active ON user_profiles(last_active_at DESC);

-- =============================================================================
-- User Preferences (DB-backed)
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_preferences_db (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    sources JSONB DEFAULT '[]',
    keywords JSONB DEFAULT '[]',
    excluded_keywords JSONB DEFAULT '[]',
    categories JSONB DEFAULT '[]',
    update_frequency_minutes INTEGER DEFAULT 60,
    max_articles_per_feed INTEGER DEFAULT 20,
    language VARCHAR(10) DEFAULT 'ru',
    auto_refresh_enabled BOOLEAN DEFAULT TRUE,
    compact_view BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_user_preferences_user_id ON user_preferences_db(user_id);

-- =============================================================================
-- Feed Items (Saved articles in user's feed)
-- =============================================================================

CREATE TABLE IF NOT EXISTS feed_items (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    article_id VARCHAR(200) NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    url TEXT NOT NULL,
    source VARCHAR(255) NOT NULL,
    published_at TIMESTAMP NOT NULL,
    added_to_feed_at TIMESTAMP DEFAULT NOW(),
    relevance_score FLOAT DEFAULT 0.5,
    matched_keywords JSONB DEFAULT '[]',
    cluster_size INTEGER DEFAULT 1,
    is_read BOOLEAN DEFAULT FALSE,
    is_saved BOOLEAN DEFAULT FALSE,
    is_liked BOOLEAN DEFAULT FALSE,
    is_disliked BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    saved_at TIMESTAMP,
    liked_at TIMESTAMP,
    disliked_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, article_id)
);

CREATE INDEX idx_feed_items_user_id ON feed_items(user_id);
CREATE INDEX idx_feed_items_published_at ON feed_items(published_at DESC);
CREATE INDEX idx_feed_items_is_read ON feed_items(user_id, is_read);
CREATE INDEX idx_feed_items_is_saved ON feed_items(user_id, is_saved);
CREATE INDEX idx_feed_items_is_liked ON feed_items(user_id, is_liked);
CREATE INDEX idx_feed_items_relevance ON feed_items(user_id, relevance_score DESC);

-- =============================================================================
-- User Interactions (Behavioral tracking)
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_interactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    article_id VARCHAR(200) NOT NULL,
    feed_item_id INTEGER,
    
    -- Interaction type
    interaction_type VARCHAR(50) NOT NULL,  -- 'view', 'click', 'like', 'dislike', 'save', 'share'
    
    -- Metrics
    view_duration_seconds INTEGER,
    scroll_depth FLOAT,
    clicked_read_more BOOLEAN DEFAULT FALSE,
    
    -- Context
    matched_keywords JSONB,
    relevance_score FLOAT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    FOREIGN KEY (feed_item_id) REFERENCES feed_items(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX idx_user_interactions_article_id ON user_interactions(article_id);
CREATE INDEX idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX idx_user_interactions_created_at ON user_interactions(created_at DESC);

-- =============================================================================
-- Reading Sessions
-- =============================================================================

CREATE TABLE IF NOT EXISTS reading_sessions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    articles_viewed INTEGER DEFAULT 0,
    articles_read INTEGER DEFAULT 0,
    articles_liked INTEGER DEFAULT 0,
    articles_saved INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_reading_sessions_user_id ON reading_sessions(user_id);
CREATE INDEX idx_reading_sessions_started_at ON reading_sessions(started_at DESC);

-- =============================================================================
-- Feed Cache (For fast access)
-- =============================================================================

CREATE TABLE IF NOT EXISTS feed_cache (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    cached_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    feed_data JSONB NOT NULL,
    articles_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_feed_cache_user_id ON feed_cache(user_id);
CREATE INDEX idx_feed_cache_expires_at ON feed_cache(expires_at);

-- =============================================================================
-- Interest Weights (Learned from user behavior)
-- =============================================================================

CREATE TABLE IF NOT EXISTS interest_weights (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    keyword VARCHAR(200) NOT NULL,
    weight FLOAT DEFAULT 0.5,  -- 0.0 to 1.0
    engagement_count INTEGER DEFAULT 0,  -- How many times user engaged with articles containing this keyword
    last_seen_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, keyword)
);

CREATE INDEX idx_interest_weights_user_id ON interest_weights(user_id);
CREATE INDEX idx_interest_weights_weight ON interest_weights(user_id, weight DESC);

-- =============================================================================
-- Onboarding Presets
-- =============================================================================

CREATE TABLE IF NOT EXISTS onboarding_presets (
    id SERIAL PRIMARY KEY,
    preset_key VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    emoji VARCHAR(10),
    description TEXT,
    categories JSONB DEFAULT '[]',
    keywords JSONB DEFAULT '[]',
    sources JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0
);

-- Insert default presets
INSERT INTO onboarding_presets (preset_key, name, emoji, description, categories, keywords, sources, sort_order) VALUES
('tech-enthusiast', 'Технофил', '💻', 'Всё о технологиях, программировании и инновациях', 
 '["Технологии", "Стартапы"]',
 '["AI", "Python", "JavaScript", "Machine Learning", "разработка"]',
 '["https://habr.com/ru/rss/hub/programming/all/?fl=ru", "https://techcrunch.com/feed/", "https://www.cnews.ru/inc/rss/news.xml"]',
 1),

('business-pro', 'Бизнес-профи', '💼', 'Бизнес, финансы, инвестиции и стартапы',
 '["Бизнес", "Финансы", "Стартапы"]',
 '["стартапы", "инвестиции", "IPO", "венчур", "M&A"]',
 '["https://www.rbc.ru/v10/rss/news/news.rss", "https://www.vedomosti.ru/rss/news", "https://www.kommersant.ru/RSS/news.xml"]',
 2),

('science-lover', 'Научный энтузиаст', '🔬', 'Наука, исследования и открытия',
 '["Наука", "Технологии"]',
 '["исследования", "открытие", "эксперимент", "учёные", "нобелевская"]',
 '["https://nplus1.ru/rss", "https://www.popmech.ru/feed/", "https://elementy.ru/rss/news"]',
 3),

('all-rounder', 'Всё понемногу', '🌍', 'Разнообразная лента: технологии, бизнес, новости',
 '["Общие новости", "Технологии", "Бизнес"]',
 '[]',
 '["https://lenta.ru/rss", "https://tass.ru/rss/v2.xml", "https://habr.com/ru/rss/hub/programming/all/?fl=ru", "https://www.rbc.ru/v10/rss/news/news.rss"]',
 4)
ON CONFLICT (preset_key) DO NOTHING;

-- =============================================================================
-- Views for analytics
-- =============================================================================

-- User engagement summary
CREATE OR REPLACE VIEW user_engagement_summary AS
SELECT 
    u.user_id,
    u.display_name,
    u.onboarding_completed,
    u.last_active_at,
    COUNT(DISTINCT fi.id) as total_articles_in_feed,
    COUNT(DISTINCT CASE WHEN fi.is_read THEN fi.id END) as articles_read,
    COUNT(DISTINCT CASE WHEN fi.is_liked THEN fi.id END) as articles_liked,
    COUNT(DISTINCT CASE WHEN fi.is_saved THEN fi.id END) as articles_saved,
    COUNT(DISTINCT ui.id) as total_interactions,
    AVG(ui.view_duration_seconds) as avg_view_duration
FROM user_profiles u
LEFT JOIN feed_items fi ON u.user_id = fi.user_id
LEFT JOIN user_interactions ui ON u.user_id = ui.user_id
GROUP BY u.user_id, u.display_name, u.onboarding_completed, u.last_active_at;

-- Top interests by user
CREATE OR REPLACE VIEW user_top_interests AS
SELECT 
    user_id,
    keyword,
    weight,
    engagement_count,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY weight DESC, engagement_count DESC) as rank
FROM interest_weights
WHERE weight > 0.3;

COMMENT ON TABLE user_profiles IS 'User profile information';
COMMENT ON TABLE user_preferences_db IS 'User preferences stored in database';
COMMENT ON TABLE feed_items IS 'Saved articles in user feed';
COMMENT ON TABLE user_interactions IS 'Behavioral tracking of user interactions';
COMMENT ON TABLE reading_sessions IS 'Reading sessions for analytics';
COMMENT ON TABLE feed_cache IS 'Cached feed data for fast access';
COMMENT ON TABLE interest_weights IS 'Learned keyword weights from user behavior';
COMMENT ON TABLE onboarding_presets IS 'Predefined presets for onboarding';
