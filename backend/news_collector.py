"""News collection module for gathering financial news from multiple sources."""

import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from urllib.parse import urlparse

import aiohttp
import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from config import settings
from models import NewsArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsCollector:
    """Collects news from various sources."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _generate_article_id(self, url: str, title: str) -> str:
        """Generate unique article ID."""
        content = f"{url}{title}".encode('utf-8')
        return hashlib.sha256(content).hexdigest()[:16]
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None
        try:
            return date_parser.parse(date_str)
        except Exception as e:
            logger.warning(f"Failed to parse date {date_str}: {e}")
            return None
    
    async def fetch_rss_feed(self, feed_url: str) -> List[NewsArticle]:
        """Fetch and parse RSS feed."""
        articles = []
        
        try:
            # feedparser is synchronous, run in executor
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, feed_url)
            
            source_domain = urlparse(feed_url).netloc
            
            for entry in feed.entries:
                try:
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    
                    if not title or not link:
                        continue
                    
                    # Parse published date
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        from time import struct_time
                        import time
                        published_at = datetime.fromtimestamp(
                            time.mktime(entry.published_parsed)
                        )
                    elif hasattr(entry, 'published'):
                        published_at = self._parse_date(entry.published)
                    
                    if not published_at:
                        published_at = datetime.now()
                    
                    # Extract content
                    content = entry.get('summary', '')
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].get('value', content)
                    
                    # Clean HTML from content
                    soup = BeautifulSoup(content, 'html.parser')
                    content = soup.get_text(separator=' ', strip=True)
                    
                    article = NewsArticle(
                        id=self._generate_article_id(link, title),
                        title=title,
                        content=content,
                        url=link,
                        source=source_domain,
                        published_at=published_at,
                        author=entry.get('author'),
                        raw_data={'feed_url': feed_url}
                    )
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse entry from {feed_url}: {e}")
                    continue
            
            logger.info(f"Fetched {len(articles)} articles from {feed_url}")
            
        except Exception as e:
            logger.error(f"Failed to fetch RSS feed {feed_url}: {e}")
        
        return articles
    
    async def fetch_all_rss_feeds(self, feeds: List[str]) -> List[NewsArticle]:
        """Fetch all RSS feeds concurrently."""
        tasks = [self.fetch_rss_feed(feed) for feed in feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Feed fetch failed: {result}")
        
        return all_articles
    
    async def collect_news(
        self,
        time_window_hours: int = 24,
        custom_feeds: Optional[List[str]] = None
    ) -> List[NewsArticle]:
        """
        Collect news from all sources within time window.
        
        Args:
            time_window_hours: Hours to look back for news
            custom_feeds: Optional custom RSS feeds to use instead of defaults
            
        Returns:
            List of news articles
        """
        feeds = custom_feeds or settings.rss_feeds
        
        logger.info(f"Collecting news from {len(feeds)} sources...")
        all_articles = await self.fetch_all_rss_feeds(feeds)
        
        # Filter by time window
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        filtered_articles = [
            article for article in all_articles
            if article.published_at >= cutoff_time
        ]
        
        logger.info(
            f"Collected {len(filtered_articles)} articles "
            f"within {time_window_hours} hour window "
            f"(filtered from {len(all_articles)} total)"
        )
        
        return filtered_articles


async def main():
    """Test the news collector."""
    async with NewsCollector() as collector:
        articles = await collector.collect_news(time_window_hours=48)
        
        print(f"\nCollected {len(articles)} articles\n")
        
        for article in articles[:5]:
            print(f"Title: {article.title}")
            print(f"Source: {article.source}")
            print(f"Published: {article.published_at}")
            print(f"URL: {article.url}")
            print(f"Content preview: {article.content[:200]}...")
            print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main())

