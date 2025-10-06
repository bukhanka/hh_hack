"""GPT Researcher integration for deep research on hot news stories."""

import logging
import asyncio
import os
from typing import List, Dict, Optional
from gpt_researcher import GPTResearcher

from config import settings
from models import NewsStory, Entity, TimelineEvent

# Ensure environment variables are set for GPT Researcher
# GPT Researcher reads these directly from os.environ
if settings.google_api_key:
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key
if settings.tavily_api_key:
    os.environ["TAVILY_API_KEY"] = settings.tavily_api_key
if settings.fast_llm:
    os.environ["FAST_LLM"] = settings.fast_llm
if settings.smart_llm:
    os.environ["SMART_LLM"] = settings.smart_llm
if settings.strategic_llm:
    os.environ["STRATEGIC_LLM"] = settings.strategic_llm
# Critical: Set EMBEDDING to use Google instead of OpenAI
if settings.embedding:
    os.environ["EMBEDDING"] = settings.embedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepNewsResearcher:
    """Performs deep research on news stories using GPT Researcher."""
    
    def __init__(self):
        """Initialize deep researcher."""
        # GPT Researcher can work with Google Gemini instead of OpenAI
        # Check if we have either OpenAI or Google API key
        has_llm_key = settings.openai_api_key or settings.google_api_key
        self.enabled = settings.enable_deep_research and has_llm_key and settings.tavily_api_key
        if not self.enabled:
            logger.warning(
                "Deep research disabled: requires (OPENAI_API_KEY or GOOGLE_API_KEY) and TAVILY_API_KEY"
            )
    
    async def research_story(
        self,
        headline: str,
        entities: List[Entity],
        why_now: str,
        initial_sources: List[str]
    ) -> Dict[str, any]:
        """
        Conduct deep research on a news story.
        
        Args:
            headline: Story headline
            entities: Extracted entities
            why_now: Why this matters now
            initial_sources: Initial source URLs
            
        Returns:
            Dictionary with research results:
                - research_report: Full research report
                - additional_sources: Additional source URLs found
                - research_context: Detailed context
                - key_findings: List of key findings
        """
        if not self.enabled:
            logger.debug("Deep research skipped (disabled)")
            return {
                "research_report": None,
                "additional_sources": [],
                "research_context": "",
                "key_findings": []
            }
        
        try:
            # Construct research query
            entity_names = ", ".join([e.name for e in entities[:5]])
            query = f"{headline}. Context: {why_now}. Key entities: {entity_names}"
            
            logger.info(f"Starting deep research: {headline[:50]}...")
            
            # Initialize researcher
            researcher = GPTResearcher(
                query=query,
                report_type="research_report",
                verbose=False
            )
            
            # Conduct research
            research_result = await researcher.conduct_research()
            
            # Generate report with custom prompt for financial news
            custom_prompt = """
            Based on the research, create a comprehensive financial news analysis with:
            
            1. **Summary**: Key facts and developments (2-3 sentences)
            2. **Market Impact**: How this affects markets, companies, and investors
            3. **Context**: Background information and historical context
            4. **Key Findings**: 4-5 bullet points of most important discoveries
            5. **Timeline**: Chronological sequence of events
            6. **Risk Assessment**: Potential risks and uncertainties
            7. **Related Developments**: Connected news or trends
            
            Format in markdown. Be factual and cite sources.
            """
            
            report = await researcher.write_report(custom_prompt=custom_prompt)
            
            # Get additional information
            research_context = researcher.get_research_context()
            source_urls = researcher.get_source_urls()
            research_sources = researcher.get_research_sources()
            
            # Extract key findings from sources
            key_findings = []
            for source in research_sources[:5]:
                if isinstance(source, dict) and "content" in source:
                    # Take first sentence as key finding
                    content = source["content"]
                    sentences = content.split(".")
                    if sentences:
                        key_findings.append(sentences[0].strip() + ".")
            
            logger.info(
                f"Deep research complete: {len(source_urls)} sources, "
                f"{len(report)} chars report"
            )
            
            return {
                "research_report": report,
                "additional_sources": source_urls,
                "research_context": research_context,
                "key_findings": key_findings
            }
            
        except Exception as e:
            logger.error(f"Deep research failed: {e}", exc_info=True)
            return {
                "research_report": None,
                "additional_sources": [],
                "research_context": "",
                "key_findings": []
            }
    
    async def enrich_story(self, story: NewsStory) -> NewsStory:
        """
        Enrich a story with deep research.
        
        Args:
            story: Original story
            
        Returns:
            Enriched story with additional context
        """
        # Conduct research
        research = await self.research_story(
            headline=story.headline,
            entities=story.entities,
            why_now=story.why_now,
            initial_sources=story.sources
        )
        
        # If research succeeded, enhance the story
        if research["research_report"]:
            # Add research report to draft
            enhanced_draft = f"""{story.draft}

---

## 🔍 Deep Research Analysis

{research['research_report']}

### Additional Sources
{chr(10).join([f"- {url}" for url in research['additional_sources'][:5]])}
"""
            
            # Update story
            story.draft = enhanced_draft
            
            # Add additional sources
            story.sources.extend(research["additional_sources"][:5])
            
            # Remove duplicates from sources
            story.sources = list(dict.fromkeys(story.sources))
            
            logger.info(f"Story enriched with deep research: {story.headline[:50]}...")
        
        return story


async def main():
    """Test deep researcher."""
    from datetime import datetime
    from models import HotnessScore
    
    print("Testing Deep News Researcher")
    print("=" * 80)
    
    # Create sample story
    sample_story = NewsStory(
        id="test_001",
        headline="Major Tech Company Announces AI Breakthrough",
        hotness=0.85,
        hotness_details=HotnessScore(
            overall=0.85,
            unexpectedness=0.8,
            materiality=0.9,
            velocity=0.85,
            breadth=0.8,
            credibility=0.9,
            reasoning="High impact AI announcement from major tech company"
        ),
        why_now="Significant technological advancement with immediate market implications",
        entities=[
            Entity(name="TechCorp", type="company", relevance=1.0, ticker="TECH"),
            Entity(name="AI", type="sector", relevance=0.9)
        ],
        sources=["https://example.com/article1"],
        timeline=[
            TimelineEvent(
                timestamp=datetime.now(),
                description="Announcement made",
                source_url="https://example.com/article1",
                event_type="first_mention"
            )
        ],
        draft="Original draft content here...",
        dedup_group="cluster_001",
        article_count=3
    )
    
    # Test deep research
    researcher = DeepNewsResearcher()
    
    if researcher.enabled:
        enriched_story = await researcher.enrich_story(sample_story)
        
        print("\nEnriched Story:")
        print(f"Headline: {enriched_story.headline}")
        print(f"Sources: {len(enriched_story.sources)}")
        print(f"\nDraft:\n{enriched_story.draft[:500]}...")
    else:
        print("\nDeep research is disabled (missing API keys)")
        print("Set OPENAI_API_KEY and TAVILY_API_KEY to enable")


if __name__ == "__main__":
    asyncio.run(main())

