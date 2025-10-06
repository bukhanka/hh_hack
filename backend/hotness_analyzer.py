"""Hotness analysis module using Gemini for intelligent scoring."""

import logging
from typing import List, Optional

from google import genai

from config import settings
from models import NewsArticle, HotnessAnalysis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HotnessAnalyzer:
    """Analyzes news hotness using Gemini LLM."""
    
    def __init__(self):
        """Initialize the analyzer with Gemini."""
        if not settings.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is not set. Please set it in your .env file or environment variables."
            )
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model_name = settings.gemini_model
    
    def _create_hotness_prompt(self, articles: List[NewsArticle]) -> str:
        """Create prompt for hotness analysis."""
        
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"""
Article {i}:
Title: {article.title}
Source: {article.source}
Published: {article.published_at.isoformat()}
Content: {article.content[:1000]}
URL: {article.url}

"""
        
        prompt = f"""Ты финансовый аналитик, специализирующийся на выявлении "горячих" новостей, которые могут повлиять на финансовые рынки.

Проанализируй следующие новостные статьи и предоставь структурированную оценку их "горячести" - насколько значимы и актуальны эти новости для финансовых рынков.

{articles_text}

Оцени горячесть по следующим измерениям (каждое 0-1):
1. **Unexpectedness (Неожиданность)**: Насколько это неожиданно относительно рыночного консенсуса?
2. **Materiality (Материальность)**: Потенциальное влияние на цену/волатильность/ликвидность
3. **Velocity (Скорость)**: Скорость распространения информации (репосты, обновления, подтверждения)
4. **Breadth (Широта)**: Количество затронутых активов (прямые и spillover эффекты)
5. **Credibility (Достоверность)**: Репутация источника и уровень подтверждений

Также предоставь:
- **Overall hotness**: Взвешенная комбинация всех измерений (0-1)
- **Reasoning**: Детальное объяснение оценки НА РУССКОМ ЯЗЫКЕ
- **Headline**: Краткий заголовок НА РУССКОМ ЯЗЫКЕ
- **Why Now**: 1-2 предложения на русском, объясняющие почему это важно ИМЕННО СЕЙЧАС
- **Entities**: Компании, тикеры, сектора, страны (с типом и релевантностью 0-1)
- **Timeline**: Ключевые события с временными метками (типы: first_mention, confirmation, update, correction), описания НА РУССКОМ

Будь точным и аналитичным. Для малозначимых новостей ставь низкие оценки. Для действительно рыночных новостей - высокие.

ВАЖНО: Все текстовые поля (reasoning, headline, why_now, timeline descriptions) должны быть НА РУССКОМ ЯЗЫКЕ.
"""
        return prompt
    
    def analyze_hotness(
        self,
        articles: List[NewsArticle]
    ) -> Optional[HotnessAnalysis]:
        """
        Analyze hotness of news cluster using structured output.
        
        Args:
            articles: List of articles in the cluster (already deduplicated)
            
        Returns:
            HotnessAnalysis object or None if failed
        """
        if not articles:
            return None
        
        try:
            prompt = self._create_hotness_prompt(articles)
            
            logger.info(f"Analyzing hotness for cluster of {len(articles)} articles...")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": settings.temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                    "response_schema": HotnessAnalysis,
                }
            )
            
            # With structured output, response is automatically parsed
            analysis = response.parsed
            
            if analysis:
                logger.info(
                    f"Hotness analysis complete: "
                    f"overall={analysis.hotness.overall:.2f}"
                )
                return analysis
            else:
                logger.error("Failed to parse structured output")
                logger.debug(f"Response text: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to analyze hotness: {e}", exc_info=True)
            return None


if __name__ == "__main__":
    # Test hotness analyzer
    import asyncio
    from news_collector import NewsCollector
    from deduplication import NewsDeduplicator
    
    async def test():
        # Collect news
        async with NewsCollector() as collector:
            articles = await collector.collect_news(time_window_hours=24)
        
        # Deduplicate
        deduplicator = NewsDeduplicator()
        clusters = deduplicator.cluster_articles(articles)
        
        # Analyze hotness for top clusters
        analyzer = HotnessAnalyzer()
        
        for cluster_id, cluster_articles in list(clusters.items())[:3]:
            print(f"\n{'='*80}")
            print(f"Cluster: {cluster_id} ({len(cluster_articles)} articles)")
            print(f"{'='*80}")
            
            # Take representative or first few articles
            articles_to_analyze = cluster_articles[:3]
            
            analysis = analyzer.analyze_hotness(articles_to_analyze)
            
            if analysis:
                print(f"\nHeadline: {analysis.headline}")
                print(f"Why Now: {analysis.why_now}")
                
                hotness = analysis.hotness
                print(f"\nHotness Score: {hotness.overall:.2f}")
                print(f"  - Unexpectedness: {hotness.unexpectedness:.2f}")
                print(f"  - Materiality: {hotness.materiality:.2f}")
                print(f"  - Velocity: {hotness.velocity:.2f}")
                print(f"  - Breadth: {hotness.breadth:.2f}")
                print(f"  - Credibility: {hotness.credibility:.2f}")
                print(f"\nReasoning: {hotness.reasoning}")
                
                print(f"\nEntities: {', '.join(e.name for e in analysis.entities)}")
            else:
                print("Analysis failed")
    
    asyncio.run(test())

