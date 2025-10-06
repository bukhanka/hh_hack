"""Summary generation module for personal news aggregator."""

import asyncio
import logging
from typing import Optional

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from config import settings
from models import NewsArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SummaryGenerator:
    """Generates concise summaries for news articles."""
    
    def __init__(self):
        """Initialize the generator with Gemini."""
        if not settings.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is not set. Please set it in your .env file."
            )
        
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 256,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
    
    def generate_summary(self, article: NewsArticle) -> Optional[str]:
        """
        Generate a concise 2-3 sentence summary of the article.
        
        Args:
            article: NewsArticle object
            
        Returns:
            Summary string or None if failed
        """
        
        # Limit content length for API call
        content = article.content[:2000] if len(article.content) > 2000 else article.content
        
        prompt = f"""Создай СТРОГО 2-3 ПРЕДЛОЖЕНИЯ о новости. НЕ БОЛЬШЕ!

Заголовок: {article.title}

Содержание:
{content}

КРИТИЧНЫЕ ТРЕБОВАНИЯ:
- МАКСИМУМ 3 ПРЕДЛОЖЕНИЯ! Если напишешь 4 - это ошибка!
- Каждое предложение должно нести конкретную информацию
- Первое предложение: ЧТО произошло
- Второе предложение: КТО/ГДЕ/КОГДА детали
- Третье предложение (если нужно): Последствия/значение
- БЕЗ вводных слов: "В статье", "Автор пишет"
- Конкретика: цифры, имена, факты
- Язык: русский

Сводка (2-3 предложения):"""
        
        try:
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            
            if summary:
                logger.debug(f"Generated summary for: {article.title[:50]}...")
                return summary
            else:
                logger.warning(f"Empty summary for: {article.title[:50]}...")
                return self._generate_fallback_summary(article)
                
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return self._generate_fallback_summary(article)
    
    def _generate_fallback_summary(self, article: NewsArticle) -> str:
        """
        Generate a simple fallback summary if AI generation fails.
        
        Args:
            article: NewsArticle object
            
        Returns:
            Fallback summary string
        """
        # Take first 2-3 sentences from content
        sentences = article.content.split('.')[:3]
        summary = '. '.join(sentences).strip()
        
        # Limit length
        if len(summary) > 300:
            summary = summary[:297] + "..."
        
        return summary or article.title
    
    async def generate_summary_async(self, article: NewsArticle) -> tuple[str, Optional[str]]:
        """
        Generate a concise 2-3 sentence summary of the article (async).
        
        Args:
            article: NewsArticle object
            
        Returns:
            Tuple of (article_id, summary) or (article_id, None) if failed
        """
        # Limit content length for API call
        content = article.content[:2000] if len(article.content) > 2000 else article.content
        
        prompt = f"""Создай СТРОГО 2-3 ПРЕДЛОЖЕНИЯ о новости. НЕ БОЛЬШЕ!

Заголовок: {article.title}

Содержание:
{content}

КРИТИЧНЫЕ ТРЕБОВАНИЯ:
- МАКСИМУМ 3 ПРЕДЛОЖЕНИЯ! Если напишешь 4 - это ошибка!
- Каждое предложение должно нести конкретную информацию
- Первое предложение: ЧТО произошло
- Второе предложение: КТО/ГДЕ/КОГДА детали
- Третье предложение (если нужно): Последствия/значение
- БЕЗ вводных слов: "В статье", "Автор пишет"
- Конкретика: цифры, имена, факты
- Язык: русский

Сводка (2-3 предложения):"""
        
        try:
            # Run in executor since genai is synchronous
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            summary = response.text.strip()
            
            if summary:
                logger.debug(f"Generated summary for: {article.title[:50]}...")
                return article.id, summary
            else:
                logger.warning(f"Empty summary for: {article.title[:50]}...")
                return article.id, self._generate_fallback_summary(article)
                
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return article.id, self._generate_fallback_summary(article)
    
    async def generate_batch_summaries_async(
        self, 
        articles: list[NewsArticle],
        max_concurrent: int = None
    ) -> dict[str, str]:
        """
        Generate summaries for multiple articles in parallel.
        
        Args:
            articles: List of NewsArticle objects
            max_concurrent: Maximum number of concurrent API calls
            
        Returns:
            Dictionary mapping article IDs to summaries
        """
        summaries = {}
        
        # Use config value if not specified
        if max_concurrent is None:
            max_concurrent = settings.max_concurrent_summaries
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(article):
            async with semaphore:
                return await self.generate_summary_async(article)
        
        # Process all articles in parallel (but limited by semaphore)
        tasks = [generate_with_semaphore(article) for article in articles]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for result in results:
            if isinstance(result, tuple):
                article_id, summary = result
                if summary:
                    summaries[article_id] = summary
            elif isinstance(result, Exception):
                logger.error(f"Summary generation failed: {result}")
        
        logger.info(f"Generated {len(summaries)} summaries out of {len(articles)} articles")
        return summaries
    
    def generate_batch_summaries(self, articles: list[NewsArticle]) -> dict[str, str]:
        """
        Generate summaries for multiple articles (sync wrapper).
        
        Args:
            articles: List of NewsArticle objects
            
        Returns:
            Dictionary mapping article IDs to summaries
        """
        # Run async version in event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, we need to use run_in_executor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(self.generate_batch_summaries_async(articles))
                    )
                    return future.result()
            else:
                return loop.run_until_complete(self.generate_batch_summaries_async(articles))
        except RuntimeError:
            # No event loop, create a new one
            return asyncio.run(self.generate_batch_summaries_async(articles))


if __name__ == "__main__":
    # Test summary generator
    import asyncio
    from datetime import datetime
    from news_collector import NewsCollector
    
    async def test():
        # Collect some news
        async with NewsCollector() as collector:
            articles = await collector.collect_news(time_window_hours=24)
        
        if not articles:
            print("No articles collected")
            return
        
        generator = SummaryGenerator()
        
        print(f"\n{'='*80}")
        print("Testing Summary Generator")
        print(f"{'='*80}\n")
        
        for article in articles[:5]:
            print(f"Original Title: {article.title}")
            print(f"Original Content Length: {len(article.content)} chars")
            print(f"Source: {article.source}")
            
            summary = generator.generate_summary(article)
            
            print(f"\nGenerated Summary:")
            print(summary)
            print(f"\n{'-'*80}\n")
    
    asyncio.run(test())
