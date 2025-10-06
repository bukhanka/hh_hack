"""Configuration management for the financial news radar system."""

import os
from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = ConfigDict(extra='ignore', env_file=".env")
    
    # API Keys
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    alpha_vantage_key: str = os.getenv("ALPHA_VANTAGE_KEY", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Database settings
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://radar_user:radar_password_2024@localhost:5432/finhack"
    )
    
    # Application parameters
    news_window_hours: int = int(os.getenv("NEWS_WINDOW_HOURS", "24"))
    top_k_stories: int = int(os.getenv("TOP_K_STORIES", "10"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
    hotness_threshold: float = float(os.getenv("HOTNESS_THRESHOLD", "0.6"))
    
    # Model settings
    gemini_model: str = "gemini-2.0-flash"
    embedding_model: str = "models/text-embedding-004"
    temperature: float = 0.3
    
    # GPT Researcher LLM settings
    fast_llm: str = os.getenv("FAST_LLM", "google_genai:gemini-2.0-flash")
    smart_llm: str = os.getenv("SMART_LLM", "google_genai:gemini-2.5-flash")
    strategic_llm: str = os.getenv("STRATEGIC_LLM", "google_genai:gemini-2.5-pro")
    embedding: str = os.getenv("EMBEDDING", "google_genai:models/text-embedding-004")
    
    # News sources RSS feeds
    rss_feeds: List[str] = [
        "https://www.ft.com/rss/companies",
        "https://seekingalpha.com/feed.xml",
        "https://www.investing.com/rss/news.rss",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://www.marketwatch.com/rss/topstories",
    ]
    
    # Cache settings
    cache_ttl_seconds: int = 3600
    enable_cache: bool = True
    
    # Deduplication
    min_cluster_size: int = 2
    
    # Parallelization settings
    max_concurrent_embeddings: int = int(os.getenv("MAX_CONCURRENT_EMBEDDINGS", "10"))
    max_concurrent_summaries: int = int(os.getenv("MAX_CONCURRENT_SUMMARIES", "5"))
    
    # Deep research settings
    enable_tavily_search: bool = os.getenv("ENABLE_TAVILY_SEARCH", "true").lower() == "true"
    enable_deep_research: bool = os.getenv("ENABLE_DEEP_RESEARCH", "true").lower() == "true"
    deep_research_threshold: float = float(os.getenv("DEEP_RESEARCH_THRESHOLD", "0.7"))
    tavily_max_results: int = int(os.getenv("TAVILY_MAX_RESULTS", "5"))


settings = Settings()

