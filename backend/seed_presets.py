"""Seed onboarding presets into database."""

import asyncio
import logging
from database import db_manager, OnboardingPreset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


PRESETS_DATA = [
    {
        "preset_key": "tech-enthusiast",
        "name": "Технофил",
        "emoji": "💻",
        "description": "Для тех, кто живёт технологиями: программирование, AI, стартапы, новые гаджеты",
        "categories": ["Технологии", "IT", "Стартапы", "AI"],
        "keywords": [
            "AI", "Python", "JavaScript", "Machine Learning", "нейросети",
            "ChatGPT", "стартап", "разработка", "программирование", "OpenAI",
            "Google", "Meta", "Apple", "Microsoft", "тестирование"
        ],
        "sources": [
            "https://habr.com/ru/rss/hub/programming/all/?fl=ru",
            "https://habr.com/ru/rss/hub/artificial_intelligence/all/?fl=ru",
            "https://www.cnews.ru/inc/rss/news.xml",
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml",
            "https://vc.ru/rss/all",
            "https://tjournal.ru/rss",
            "https://dev.to/feed",
        ],
        "sort_order": 1
    },
    {
        "preset_key": "business-pro",
        "name": "Бизнес-профи",
        "emoji": "💼",
        "description": "Деловые новости: стартапы, инвестиции, IPO, венчурный капитал, экономика",
        "categories": ["Бизнес", "Финансы", "Стартапы", "Инвестиции"],
        "keywords": [
            "стартапы", "инвестиции", "IPO", "венчур", "финансирование",
            "раунд", "сделка", "M&A", "акции", "биржа", "экономика",
            "бизнес", "предприниматель", "Forbes", "funding"
        ],
        "sources": [
            "https://www.rbc.ru/v10/rss/news/news.rss",
            "https://www.vedomosti.ru/rss/news",
            "https://www.kommersant.ru/RSS/news.xml",
            "https://www.forbes.ru/newsfeed/rss",
            "https://vc.ru/rss/all",
            "https://www.finam.ru/international/newsrss/",
            "https://quote.rbc.ru/news/rss/",
        ],
        "sort_order": 2
    },
    {
        "preset_key": "science-lover",
        "name": "Научный энтузиаст",
        "emoji": "🔬",
        "description": "Наука и исследования: открытия, эксперименты, космос, медицина, биология",
        "categories": ["Наука", "Исследования", "Космос", "Медицина"],
        "keywords": [
            "исследование", "открытие", "эксперимент", "учёные", "космос",
            "NASA", "SpaceX", "медицина", "биология", "физика", "химия",
            "нобелевская", "прорыв", "научный", "лаборатория"
        ],
        "sources": [
            "https://nplus1.ru/rss",
            "https://www.popmech.ru/feed/",
            "https://elementy.ru/rss/news",
            "https://www.space.com/feeds/all",
            "https://naked-science.ru/feed",
            "https://www.scientificamerican.com/feed/",
        ],
        "sort_order": 3
    },
    {
        "preset_key": "all-rounder",
        "name": "Всё понемногу",
        "emoji": "🌍",
        "description": "Сбалансированная подборка новостей из всех сфер: технологии, бизнес, наука, общество",
        "categories": ["Общие новости", "Технологии", "Бизнес", "Наука"],
        "keywords": [
            "новости", "события", "важное", "главное", "топ",
            "мир", "Россия", "политика", "общество"
        ],
        "sources": [
            "https://lenta.ru/rss",
            "https://tass.ru/rss/v2.xml",
            "https://ria.ru/export/rss2/archive/index.xml",
            "https://meduza.io/rss/all",
            "https://www.gazeta.ru/export/rss/lenta.xml",
            "https://habr.com/ru/rss/hub/programming/all/?fl=ru",
            "https://www.rbc.ru/v10/rss/news/news.rss",
            "https://nplus1.ru/rss",
            "https://vc.ru/rss/all",
            "https://tjournal.ru/rss",
        ],
        "sort_order": 4
    }
]


async def seed_presets():
    """Seed onboarding presets into database."""
    
    logger.info("Initializing database connection...")
    await db_manager.init_async()
    
    logger.info(f"Seeding {len(PRESETS_DATA)} onboarding presets...")
    
    async with db_manager.get_session() as session:
        from sqlalchemy import select
        from sqlalchemy.dialects.postgresql import insert
        
        for preset_data in PRESETS_DATA:
            # Check if preset already exists
            result = await session.execute(
                select(OnboardingPreset).where(
                    OnboardingPreset.preset_key == preset_data["preset_key"]
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.info(f"Preset '{preset_data['preset_key']}' already exists, updating...")
                # Update existing
                existing.name = preset_data["name"]
                existing.emoji = preset_data["emoji"]
                existing.description = preset_data["description"]
                existing.categories = preset_data["categories"]
                existing.keywords = preset_data["keywords"]
                existing.sources = preset_data["sources"]
                existing.sort_order = preset_data["sort_order"]
                existing.is_active = True
            else:
                logger.info(f"Creating preset '{preset_data['preset_key']}'...")
                # Create new
                preset = OnboardingPreset(
                    preset_key=preset_data["preset_key"],
                    name=preset_data["name"],
                    emoji=preset_data["emoji"],
                    description=preset_data["description"],
                    categories=preset_data["categories"],
                    keywords=preset_data["keywords"],
                    sources=preset_data["sources"],
                    is_active=True,
                    sort_order=preset_data["sort_order"]
                )
                session.add(preset)
        
        await session.flush()
    
    logger.info("✅ Successfully seeded all presets!")
    
    # Verify
    async with db_manager.get_session() as session:
        result = await session.execute(select(OnboardingPreset))
        presets = result.scalars().all()
        logger.info(f"Total presets in database: {len(presets)}")
        for preset in presets:
            logger.info(f"  - {preset.emoji} {preset.name} ({preset.preset_key})")


async def main():
    """Main entry point."""
    try:
        await seed_presets()
    except Exception as e:
        logger.error(f"Error seeding presets: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

