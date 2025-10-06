"""Tavily Search API integration for collecting financial news."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from tavily import TavilyClient

from config import settings
from models import NewsArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TavilyNewsCollector:
    """Collects financial news using Tavily Search API."""
    
    def __init__(self):
        """Initialize Tavily client."""
        if not settings.tavily_api_key:
            logger.warning("Tavily API key not configured")
            self.client = None
        else:
            self.client = TavilyClient(api_key=settings.tavily_api_key)
    
    async def collect_news(
        self,
        query: str = "financial markets breaking news",
        time_window_hours: int = 24,
        max_results: Optional[int] = None
    ) -> List[NewsArticle]:
        """
        Collect news using Tavily Search API.
        
        Args:
            query: Search query
            time_window_hours: Time window for news
            max_results: Maximum number of results
            
        Returns:
            List of NewsArticle objects
        """
        if not self.client:
            logger.warning("Tavily client not initialized, skipping Tavily collection")
            return []
        
        max_results = max_results or settings.tavily_max_results
        
        try:
            logger.info(f"Collecting news from Tavily: query='{query}', max_results={max_results}")
            
            # Calculate days parameter
            days = max(1, time_window_hours // 24)
            
            # Search with Tavily
            response = self.client.search(
                query=query,
                topic="finance",  # Use finance topic for financial news
                search_depth="advanced",  # Advanced search for better content
                max_results=max_results,
                days=days,  # Time filter
                include_raw_content=True,  # Get full content
                include_answer=False  # We don't need the AI answer
            )
            
            articles = []
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            
            for result in response.get("results", []):
                try:
                    # Parse published date if available
                    published_at = datetime.now()
                    if "published_date" in result:
                        try:
                            published_at = datetime.fromisoformat(result["published_date"])
                        except:
                            pass
                    
                    # Skip if too old
                    if published_at < cutoff_time:
                        continue
                    
                    # Extract domain as source
                    url = result.get("url", "")
                    source = url.split("//")[-1].split("/")[0] if url else "tavily"
                    
                    # Create article
                    article = NewsArticle(
                        id=f"tavily_{hash(url)}",
                        title=result.get("title", ""),
                        content=result.get("content", "") or result.get("raw_content", "")[:1000],
                        url=url,
                        source=source,
                        published_at=published_at,
                        raw_data=result
                    )
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Failed to parse Tavily result: {e}")
                    continue
            
            logger.info(f"Collected {len(articles)} articles from Tavily")
            return articles
            
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []
    
    async def search_for_context(
        self,
        query: str,
        max_results: int = 3
    ) -> List[dict]:
        """
        Search for additional context on a specific topic.
        
        Args:
            query: Specific search query
            max_results: Number of results
            
        Returns:
            List of search results with context
        """
        if not self.client:
            return []
        
        try:
            response = self.client.search(
                query=query,
                topic="finance",
                search_depth="advanced",
                max_results=max_results,
                include_raw_content=True,
                include_answer=True  # Get AI summary
            )
            
            return response.get("results", [])
            
        except Exception as e:
            logger.error(f"Tavily context search failed: {e}")
            return []


async def main():
    """Test Tavily collector."""
    collector = TavilyNewsCollector()
    
    print("Testing Tavily News Collector")
    print("=" * 80)
    
    # Test general news collection
    articles = await collector.collect_news(
        query="stock market news",
        time_window_hours=24,
        max_results=5
    )
    
    print(f"\nCollected {len(articles)} articles:")
    for article in articles:
        print(f"\n- {article.title}")
        print(f"  Source: {article.source}")
        print(f"  URL: {article.url}")
        print(f"  Content: {article.content[:100]}...")
    
    # Test context search
    print("\n" + "=" * 80)
    print("Testing context search...")
    
    context = await collector.search_for_context(
        query="Tesla stock price movement reasons",
        max_results=3
    )
    
    print(f"\nFound {len(context)} context results")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

