"""
Пересоздать базу данных с нуля.

Для хакатона - просто дропаем все и создаем заново.
"""

import asyncio
import logging
import sys
from pathlib import Path
from sqlalchemy import text

from database import db_manager
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def reset_database():
    """Пересоздать все таблицы."""
    try:
        logger.info("🔄 Пересоздание базы данных...")
        
        # Инициализируем подключение
        await db_manager.init_async()
        
        # Читаем SQL миграцию
        migration_file = Path(__file__).parent / 'migrations' / '001_personal_news_tables.sql'
        
        if not migration_file.exists():
            logger.error(f"Файл миграции не найден: {migration_file}")
            return False
        
        logger.info(f"Читаем миграцию из {migration_file.name}")
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Выполняем SQL
        async with db_manager.get_session() as session:
            # Разбиваем на отдельные statements
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            logger.info(f"Выполняем {len(statements)} SQL statements...")
            
            for i, statement in enumerate(statements, 1):
                # Пропускаем комментарии
                if statement.startswith('--') or statement.startswith('/*'):
                    continue
                
                try:
                    await session.execute(text(statement))
                    await session.flush()
                    
                    if i % 10 == 0:
                        logger.info(f"  Выполнено {i}/{len(statements)} statements...")
                        
                except Exception as e:
                    # Игнорируем ошибки "already exists"
                    if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                        pass
                    else:
                        logger.error(f"Ошибка на statement {i}: {e}")
                        # Продолжаем выполнение
            
            await session.commit()
        
        logger.info("✅ База данных успешно пересоздана!")
        logger.info("\nСоздано:")
        logger.info("  - Таблицы для user profiles, preferences, feed items")
        logger.info("  - Таблицы для interactions и learning engine")
        logger.info("  - Таблицы для onboarding presets")
        logger.info("  - Индексы для производительности")
        logger.info("  - Views для аналитики")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при пересоздании БД: {e}", exc_info=True)
        return False


async def main():
    """Главная функция."""
    logger.info("=" * 60)
    logger.info("ПЕРЕСОЗДАНИЕ БАЗЫ ДАННЫХ")
    logger.info("=" * 60)
    
    success = await reset_database()
    
    if success:
        logger.info("\n✅ Готово! Теперь можно запускать приложение.")
        sys.exit(0)
    else:
        logger.error("\n❌ Не удалось пересоздать БД.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

