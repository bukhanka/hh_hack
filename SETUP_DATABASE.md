# 🐘 Настройка PostgreSQL базы данных

## 📦 Что было добавлено

### Новые файлы:
- `docker-compose.yml` - Docker контейнер с PostgreSQL
- `backend/database.py` - SQLAlchemy модели и менеджер БД
- `backend/init_db.sql` - SQL скрипт инициализации
- `.env.example` - Пример конфигурации

### Обновленные файлы:
- `backend/config.py` - добавлена настройка DATABASE_URL
- `backend/api.py` - добавлены эндпоинты истории + сохранение в БД
- `backend/requirements.txt` - добавлены зависимости для PostgreSQL
- Фронтенд в `api.py` - добавлена вкладка "История"

---

## 🚀 Быстрый старт

### 1. Запустить PostgreSQL в Docker

```bash
# В корне проекта
docker-compose up -d

# Проверить что контейнер работает
docker-compose ps
```

Это создаст:
- PostgreSQL 15 на порту **5433** (чтобы не конфликтовать с системным PostgreSQL на 5432)
- База данных: `finhack`
- Пользователь: `radar_user`
- Пароль: `radar_password_2024`
- Volume для хранения данных: `postgres_data`

### 2. Установить зависимости

```bash
cd backend
pip install -r requirements.txt
```

Новые зависимости:
- `sqlalchemy>=2.0.0` - ORM
- `asyncpg>=0.29.0` - асинхронный драйвер PostgreSQL
- `psycopg2-binary>=2.9.9` - синхронный драйвер
- `alembic>=1.13.0` - миграции (опционально)

### 3. Запустить приложение

```bash
cd backend
python api.py
```

При старте автоматически:
- ✅ Создаются таблицы в БД
- ✅ Применяются индексы
- ✅ Проверяется подключение

### 4. Открыть веб-интерфейс

```
http://localhost:8000
```

---

## 📊 Структура базы данных

### Таблица: `radar_runs`
Хранит информацию о каждом запуске обработки новостей.

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | INTEGER | Primary key (автоинкремент) |
| created_at | TIMESTAMP | Время запуска |
| time_window_hours | INTEGER | Окно времени (часы) |
| total_articles_processed | INTEGER | Обработано статей |
| processing_time_seconds | FLOAT | Время обработки |
| hotness_threshold | FLOAT | Порог hotness |
| top_k | INTEGER | Количество top stories |

### Таблица: `stories`
Хранит найденные hot stories.

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | INTEGER | Primary key |
| radar_run_id | INTEGER | Foreign key → radar_runs |
| story_id | VARCHAR | Cluster ID (cluster_0001) |
| headline | TEXT | Заголовок |
| hotness | FLOAT | Оценка горячести |
| why_now | TEXT | Почему важно сейчас |
| draft | TEXT | Черновик статьи |
| dedup_group | VARCHAR | ID группы дубликатов |
| article_count | INTEGER | Статей в кластере |
| hotness_details | JSON | Детальные метрики |
| entities | JSON | Извлеченные сущности |
| sources | JSON | Источники (URLs) |
| timeline | JSON | Timeline событий |
| has_deep_research | BOOLEAN | Deep research проведен |
| research_summary | TEXT | Результат deep research |
| created_at | TIMESTAMP | Время создания |

### Индексы:
- `idx_radar_runs_created_at` - для быстрой сортировки по времени
- `idx_stories_hotness` - для фильтрации по hotness
- `idx_stories_radar_run_id` - для связи с radar_runs

---

## 🌐 Новые API эндпоинты

### 1. GET `/api/history`
Получить историю обработки.

**Параметры:**
- `limit` (int, 1-100, default=50) - количество результатов
- `offset` (int, default=0) - смещение для пагинации

**Пример:**
```bash
curl http://localhost:8000/api/history?limit=10
```

**Ответ:**
```json
{
  "history": [
    {
      "id": 1,
      "created_at": "2025-10-04T12:30:00",
      "time_window_hours": 24,
      "total_articles_processed": 127,
      "processing_time_seconds": 67.3,
      "hotness_threshold": 0.6,
      "top_k": 10,
      "story_count": 5
    }
  ],
  "limit": 10,
  "offset": 0
}
```

### 2. GET `/api/history/{run_id}`
Получить детали конкретного запуска.

**Пример:**
```bash
curl http://localhost:8000/api/history/1
```

**Ответ:**
```json
{
  "id": 1,
  "created_at": "2025-10-04T12:30:00",
  "time_window_hours": 24,
  "total_articles_processed": 127,
  "story_count": 5,
  "stories": [
    {
      "id": "cluster_0001",
      "headline": "Tech Giant Announces...",
      "hotness": 0.87,
      "why_now": "...",
      "entities": [...],
      "sources": [...],
      "timeline": [...],
      "draft": "..."
    }
  ]
}
```

### 3. DELETE `/api/history/cleanup`
Удалить старые запуски.

**Параметры:**
- `keep_last_n` (int, 10-500, default=100) - сколько оставить

**Пример:**
```bash
curl -X DELETE "http://localhost:8000/api/history/cleanup?keep_last_n=50"
```

---

## 💻 Использование веб-интерфейса

### Вкладка "🚀 New Scan"
- Настроить параметры (time window, top K, threshold)
- Нажать "Scan for Hot News"
- Результат автоматически сохранится в БД

### Вкладка "📜 History"
- Показывает последние 20 запусков
- Каждый запуск содержит:
  - Дату и время
  - Количество найденных stories
  - Статистику обработки
- **Клик на запуск** → загружает детали и показывает stories

---

## 🛠️ Управление Docker

### Просмотр логов:
```bash
docker-compose logs -f postgres
```

### Остановить PostgreSQL:
```bash
docker-compose stop
```

### Запустить снова:
```bash
docker-compose start
```

### Полная пересборка:
```bash
docker-compose down -v  # Удалит данные!
docker-compose up -d
```

### Подключиться к БД напрямую:
```bash
docker exec -it finhack_postgres psql -U radar_user -d finhack
```

SQL команды:
```sql
-- Посмотреть таблицы
\dt

-- Количество запусков
SELECT COUNT(*) FROM radar_runs;

-- Последние 5 запусков
SELECT id, created_at, story_count, total_articles_processed 
FROM radar_runs 
ORDER BY created_at DESC 
LIMIT 5;

-- Самые горячие stories
SELECT headline, hotness, created_at 
FROM stories 
ORDER BY hotness DESC 
LIMIT 10;
```

---

## 🔧 Настройка через .env

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
# Отредактируйте .env своими ключами
```

Чтобы изменить параметры БД:
```env
DATABASE_URL=postgresql+asyncpg://username:password@host:port/database
```

---

## 📈 Что сохраняется

### При каждом запуске `/api/process`:

1. **Метаданные запуска** в `radar_runs`:
   - Когда запущено
   - Сколько статей обработано
   - Время выполнения
   - Использованные параметры

2. **Все найденные stories** в `stories`:
   - Headline, hotness score
   - Why now объяснение
   - Entities (компании, сектора)
   - Sources (URLs источников)
   - Timeline событий
   - Полный draft
   - Deep research результаты (если применимо)

### Что НЕ сохраняется:
- Сырые RSS статьи (только агрегированные stories)
- Промежуточные embeddings (только в памяти для текущей сессии)
- In-memory кэш (сбрасывается при рестарте)

---

## 🎯 Примеры использования

### Python скрипт для работы с БД:

```python
from database import db_manager
import asyncio

async def get_top_stories():
    # Получить последние 10 запусков
    history = await db_manager.get_radar_history(limit=10)
    
    for run in history:
        print(f"Run {run['id']}: {run['created_at']}")
        print(f"  Stories: {run['story_count']}")
        print(f"  Articles: {run['total_articles_processed']}")
        print()

asyncio.run(get_top_stories())
```

### Очистка старых данных:

```python
# Оставить только последние 50 запусков
await db_manager.delete_old_runs(keep_last_n=50)
```

---

## 🚨 Troubleshooting

### Ошибка: "connection refused"
```bash
# Проверить что контейнер запущен
docker-compose ps

# Перезапустить
docker-compose restart postgres
```

### Ошибка: "database does not exist"
```bash
# Пересоздать контейнер
docker-compose down
docker-compose up -d
```

### Ошибка: "password authentication failed"
```bash
# Проверить DATABASE_URL в .env или config.py
# Убедиться что credentials совпадают с docker-compose.yml
```

### Медленные запросы:
```sql
-- Проверить индексы
SELECT * FROM pg_indexes WHERE tablename IN ('radar_runs', 'stories');

-- Пересоздать индексы (если нужно)
REINDEX TABLE stories;
```

---

## 📦 Миграции (опционально)

Если нужно изменить структуру БД:

```bash
# Инициализация Alembic
cd backend
alembic init alembic

# Создать миграцию
alembic revision --autogenerate -m "Add new column"

# Применить миграцию
alembic upgrade head
```

---

## ✅ Готово!

Теперь у вас есть:
- ✅ PostgreSQL в Docker
- ✅ Автоматическое сохранение результатов
- ✅ История обработки в веб-интерфейсе
- ✅ API для работы с историей
- ✅ Персистентное хранилище данных

**Каждый запуск обработки новостей сохраняется в БД и доступен через вкладку "История"!** 🎉

