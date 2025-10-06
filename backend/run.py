#!/usr/bin/env python3
"""Simple runner script for the RADAR system."""

import asyncio
import sys
from radar import FinancialNewsRadar


async def run_radar(hours: int = 24, top_k: int = 10, threshold: float = 0.5):
    """Run the RADAR system and display results."""
    
    print("=" * 80)
    print("Financial News RADAR - Hot News Detection System")
    print("=" * 80)
    print(f"\nParameters:")
    print(f"  Time window: {hours} hours")
    print(f"  Top stories: {top_k}")
    print(f"  Hotness threshold: {threshold}")
    print("\nProcessing...\n")
    
    radar = FinancialNewsRadar()
    
    response = await radar.process_news(
        time_window_hours=hours,
        top_k=top_k,
        hotness_threshold=threshold
    )
    
    print("\n" + "=" * 80)
    print(f"RESULTS")
    print("=" * 80)
    print(f"Processed: {response.total_articles_processed} articles")
    print(f"Found: {len(response.stories)} hot stories")
    print(f"Processing time: {response.processing_time_seconds:.1f}s")
    print("=" * 80)
    
    for i, story in enumerate(response.stories, 1):
        print(f"\n{'='*80}")
        print(f"STORY #{i}: {story.headline}")
        print(f"{'='*80}")
        print(f"🔥 Hotness: {story.hotness:.2f} ({int(story.hotness * 100)}%)")
        print(f"📊 Articles in cluster: {story.article_count}")
        
        print(f"\n💡 Why Now:")
        print(f"   {story.why_now}")
        
        print(f"\n🏢 Entities:")
        for entity in story.entities[:8]:
            ticker_str = f" [{entity.ticker}]" if entity.ticker else ""
            print(f"   - {entity.name} ({entity.type}){ticker_str} - relevance: {entity.relevance:.2f}")
        
        print(f"\n📈 Hotness Breakdown:")
        print(f"   Unexpectedness: {story.hotness_details.unexpectedness:.2f}")
        print(f"   Materiality: {story.hotness_details.materiality:.2f}")
        print(f"   Velocity: {story.hotness_details.velocity:.2f}")
        print(f"   Breadth: {story.hotness_details.breadth:.2f}")
        print(f"   Credibility: {story.hotness_details.credibility:.2f}")
        
        print(f"\n🔍 Analysis:")
        print(f"   {story.hotness_details.reasoning}")
        
        print(f"\n⏱️ Timeline:")
        for event in story.timeline[:5]:
            print(f"   {event.timestamp.strftime('%Y-%m-%d %H:%M')} - {event.description}")
        
        print(f"\n📰 DRAFT PUBLICATION:")
        print("   " + "-" * 76)
        for line in story.draft.split('\n'):
            print(f"   {line}")
        print("   " + "-" * 76)
        
        print(f"\n🔗 Sources ({len(story.sources)}):")
        for url in story.sources[:5]:
            print(f"   - {url}")
        
        if i < len(response.stories):
            print("\n")


def main():
    """Main entry point."""
    # Parse command line arguments
    hours = 24
    top_k = 10
    threshold = 0.5
    
    if len(sys.argv) > 1:
        hours = int(sys.argv[1])
    if len(sys.argv) > 2:
        top_k = int(sys.argv[2])
    if len(sys.argv) > 3:
        threshold = float(sys.argv[3])
    
    asyncio.run(run_radar(hours, top_k, threshold))


if __name__ == "__main__":
    main()

