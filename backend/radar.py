"""Main RADAR module that orchestrates the entire pipeline."""

import asyncio
import logging
import time
from datetime import datetime
from typing import List, Optional

from config import settings
from models import NewsArticle, NewsStory, RadarResponse
from news_collector import NewsCollector
from deduplication import NewsDeduplicator
from hotness_analyzer import HotnessAnalyzer
from draft_generator import DraftGenerator
from tavily_collector import TavilyNewsCollector
from deep_researcher import DeepNewsResearcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialNewsRadar:
    """Main RADAR system for hot news detection."""
    
    def __init__(self):
        """Initialize all components."""
        self.collector = None  # Will be initialized in async context
        self.tavily_collector = TavilyNewsCollector()
        self.deduplicator = NewsDeduplicator()
        self.analyzer = HotnessAnalyzer()
        self.generator = DraftGenerator()
        self.researcher = DeepNewsResearcher()
    
    async def _process_cluster(
        self,
        cluster_id: str,
        cluster_articles: List[NewsArticle],
        hotness_threshold: float
    ) -> Optional[NewsStory]:
        """
        Process a single cluster of articles.
        
        Args:
            cluster_id: Cluster identifier
            cluster_articles: Articles in the cluster
            hotness_threshold: Minimum hotness score
            
        Returns:
            NewsStory or None if processing failed or below threshold
        """
        try:
            # Get representative articles (max 3 for analysis)
            representative_articles = cluster_articles[:3]
            
            # Analyze hotness with structured output
            analysis = self.analyzer.analyze_hotness(representative_articles)
            
            if not analysis:
                logger.warning(f"Skipping cluster {cluster_id}: analysis failed")
                return None
            
            # Extract components from structured output
            hotness_score = analysis.hotness
            entities = analysis.entities
            timeline = analysis.timeline
            headline = analysis.headline
            why_now = analysis.why_now
            
            # Skip if below threshold
            if hotness_score.overall < hotness_threshold:
                logger.debug(
                    f"Skipping cluster {cluster_id}: "
                    f"hotness {hotness_score.overall:.2f} < {hotness_threshold}"
                )
                return None
            
            # Step 4: Generate draft (only for high-hotness stories OR if deep research disabled)
            should_generate_draft = (
                not settings.enable_deep_research or 
                hotness_score.overall >= settings.deep_research_threshold
            )
            
            draft = None
            has_deep_research = False
            research_summary = None
            
            if should_generate_draft:
                logger.info(f"Generating draft for cluster {cluster_id} (hotness={hotness_score.overall:.2f})...")
                draft = self.generator.generate_draft(
                    headline=headline,
                    articles=cluster_articles[:5],
                    entities=entities,
                    timeline=timeline,
                    why_now=why_now,
                    hotness_reasoning=hotness_score.reasoning
                )
                
                if not draft:
                    logger.warning(f"Failed to generate draft for cluster {cluster_id}")
                    draft = f"# {headline}\n\n{why_now}\n\nНе удалось сгенерировать полный черновик."
            else:
                # For lower-hotness stories, create a simple summary instead of full draft
                logger.info(f"Skipping full draft for cluster {cluster_id} (hotness below deep research threshold)")
                draft = f"# {headline}\n\n**Почему это важно сейчас**: {why_now}\n\n**Ключевые сущности**: {', '.join(e.name for e in entities[:5])}\n\n_Полный черновик не создан - оценка горячести ниже порога для детального анализа._"
            
            # Collect source URLs
            source_urls = [article.url for article in cluster_articles[:5]]
            
            # Create story
            story = NewsStory(
                id=cluster_id,
                headline=headline,
                hotness=hotness_score.overall,
                hotness_details=hotness_score,
                why_now=why_now,
                entities=entities,
                sources=source_urls,
                timeline=timeline,
                draft=draft,
                dedup_group=cluster_id,
                article_count=len(cluster_articles),
                has_deep_research=has_deep_research,
                research_summary=research_summary
            )
            
            # Step 5: Apply deep research for top stories
            if (settings.enable_deep_research and 
                hotness_score.overall >= settings.deep_research_threshold):
                logger.info(f"Conducting deep research for: {headline[:50]}...")
                try:
                    story = await self.researcher.enrich_story(story)
                    story.has_deep_research = True
                    story.research_summary = "Глубокое исследование выполнено с помощью GPT Researcher"
                except Exception as e:
                    logger.error(f"Deep research failed for {cluster_id}: {e}")
            
            logger.info(
                f"Processed story: {headline[:50]}... "
                f"(hotness={hotness_score.overall:.2f})"
            )
            
            return story
            
        except Exception as e:
            logger.error(f"Failed to process cluster {cluster_id}: {e}", exc_info=True)
            return None
    
    async def process_news(
        self,
        time_window_hours: Optional[int] = None,
        top_k: Optional[int] = None,
        hotness_threshold: Optional[float] = None,
        custom_feeds: Optional[List[str]] = None
    ) -> RadarResponse:
        """
        Process news and return hot stories.
        
        Args:
            time_window_hours: Hours to look back (default from settings)
            top_k: Number of top stories to return (default from settings)
            hotness_threshold: Minimum hotness score (default from settings)
            custom_feeds: Optional custom RSS feeds
            
        Returns:
            RadarResponse with processed stories
        """
        start_time = time.time()
        
        time_window_hours = time_window_hours or settings.news_window_hours
        top_k = top_k or settings.top_k_stories
        hotness_threshold = hotness_threshold or settings.hotness_threshold
        
        logger.info(f"Starting RADAR processing: window={time_window_hours}h, top_k={top_k}")
        
        # Step 1: Collect news from RSS feeds
        logger.info("Step 1: Collecting news from RSS feeds...")
        async with NewsCollector() as collector:
            rss_articles = await collector.collect_news(
                time_window_hours=time_window_hours,
                custom_feeds=custom_feeds
            )
        
        logger.info(f"Collected {len(rss_articles)} articles from RSS")
        
        # Step 1b: Collect additional news from Tavily (if enabled)
        tavily_articles = []
        if settings.enable_tavily_search:
            logger.info("Step 1b: Collecting news from Tavily Search...")
            tavily_articles = await self.tavily_collector.collect_news(
                query="financial markets breaking news stock market",
                time_window_hours=time_window_hours,
                max_results=settings.tavily_max_results
            )
            logger.info(f"Collected {len(tavily_articles)} articles from Tavily")
        
        # Combine articles from both sources
        articles = rss_articles + tavily_articles
        
        if not articles:
            logger.warning("No articles collected")
            return RadarResponse(
                stories=[],
                total_articles_processed=0,
                time_window_hours=time_window_hours,
                processing_time_seconds=time.time() - start_time
            )
        
        logger.info(f"Total collected: {len(articles)} articles (RSS: {len(rss_articles)}, Tavily: {len(tavily_articles)})")
        
        # Step 2: Deduplicate and cluster
        logger.info("Step 2: Deduplicating and clustering...")
        clusters = self.deduplicator.cluster_articles(articles)
        logger.info(f"Created {len(clusters)} clusters")
        
        # Step 3: Analyze hotness for each cluster (PARALLEL PROCESSING)
        logger.info(f"Step 3: Analyzing hotness for {len(clusters)} clusters in parallel...")
        
        # Create tasks for parallel processing
        tasks = [
            self._process_cluster(cluster_id, cluster_articles, hotness_threshold)
            for cluster_id, cluster_articles in clusters.items()
        ]
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None and exceptions
        stories = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Cluster processing raised exception: {result}")
            elif result is not None:
                stories.append(result)
        
        logger.info(f"Processed {len(stories)} stories out of {len(clusters)} clusters")
        
        # Sort by hotness and take top K
        stories.sort(key=lambda s: s.hotness, reverse=True)
        top_stories = stories[:top_k]
        
        processing_time = time.time() - start_time
        
        logger.info(
            f"RADAR processing complete: "
            f"{len(top_stories)} stories in {processing_time:.1f}s"
        )
        
        return RadarResponse(
            stories=top_stories,
            total_articles_processed=len(articles),
            time_window_hours=time_window_hours,
            processing_time_seconds=processing_time
        )


async def main():
    """Test the complete RADAR system."""
    radar = FinancialNewsRadar()
    
    print("=" * 80)
    print("Financial News RADAR - Hot News Detection System")
    print("=" * 80)
    print()
    
    response = await radar.process_news(
        time_window_hours=24,
        top_k=5,
        hotness_threshold=0.5
    )
    
    print(f"\nProcessed {response.total_articles_processed} articles in {response.processing_time_seconds:.1f}s")
    print(f"Found {len(response.stories)} hot stories\n")
    
    for i, story in enumerate(response.stories, 1):
        print("=" * 80)
        print(f"STORY #{i}: {story.headline}")
        print("=" * 80)
        print(f"Hotness: {story.hotness:.2f}")
        print(f"Articles in cluster: {story.article_count}")
        print(f"\nWhy Now: {story.why_now}")
        print(f"\nEntities: {', '.join(e.name for e in story.entities)}")
        print(f"\nSources ({len(story.sources)}):")
        for url in story.sources[:3]:
            print(f"  - {url}")
        print(f"\n{'-'*80}")
        print("DRAFT:")
        print(f"{'-'*80}")
        print(story.draft)
        print()


if __name__ == "__main__":
    asyncio.run(main())

