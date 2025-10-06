# 🎯 Двухрежимная платформа агрегации новостей

> **HeadHunter Case Solution** - персональный агрегатор новостей с ML-обучением + финансовый RADAR

## 🚀 Быстрый старт

### Автоматическая установка (рекомендуется)

```bash
# 1. База данных (автоматически)
# Скрипт проверит Docker, создаст контейнер PostgreSQL, 
# создаст БД и пользователя, применит миграции
./setup_database.sh

# 2. Backend
cd backend
cp env.example .env
# Отредактируйте .env и добавьте свои API ключи
pip install -r requirements.txt
python run.py

# 3. Frontend
cd frontend
cp env.example .env.local
npm install
npm run dev
```

### Ручная установка

```bash
# 1. База данных
docker-compose up -d
docker exec -i finhack_postgres psql -U radar_user -d finhack < backend/migrations/001_personal_news_tables.sql

# 2-3. Backend и Frontend (см. выше)
```

**Доступ:** http://localhost:3000

---

## 📋 Что реализовано

### ✅ Требования задания (100%)
- **Персональный агрегатор** - настраиваемые источники
- **Регулярное обновление** - автоматическое каждые 15 минут
- **Источники на выбор** - 4 готовых пресета + кастомизация
- **Краткие описания** - 2-3 предложения (Gemini суммаризация)
- **Простой UX** - Next.js + Tailwind + Framer Motion
- **Без повторов** - semantic deduplication через embeddings

### 🌟 Бонусные фичи
- **ML-обучение** - адаптация к лайкам/дизлайкам пользователя
- **Умный онбординг** - 4 пресета для быстрого старта
- **Фильтры** - по ключевым словам и статусам
- **Статистика** - аналитика активности за N дней
- **Background worker** - автообновление + переобучение моделей
- **Персистентность** - PostgreSQL (не файлы/localStorage)
- **Два режима** - Personal Aggregator + Financial RADAR

---

## 🏗️ Архитектура

```
                 Единая инфраструктура
     ┌─────────────────────────────────────────┐
     │  NewsCollector  │  Deduplicator  │  DB  │
     └────────────┬────────────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
   Financial RADAR    Personal Aggregator
   (анализ новостей)  (персональная лента)
```

---

## 🎯 Режимы работы

### 1. Personal Aggregator (`/personal`)
**Персональный агрегатор новостей с ML-обучением**

- Настраиваемые RSS источники
- Генерация кратких описаний (2-3 предложения)
- Фильтрация по ключевым словам
- Лайки/дизлайки → ML учится
- Автоматическое обновление лент
- Статистика и аналитика

**API:** 15+ endpoints для управления лентой, preferences, interactions

### 2. Financial RADAR (`/financial`)
**Система анализа горячих финансовых новостей**

- Многомерная оценка "hotness" (5 метрик)
- Извлечение сущностей (компании, тикеры)
- Deep research для топовых новостей (20+ источников)
- Автоматическая генерация черновиков статей

---

## 🔧 Технологии

**Backend:**
- Python 3.10+, FastAPI, PostgreSQL
- Google Gemini 2.0 Flash (LLM + embeddings)
- APScheduler (background jobs)
- SQLAlchemy (ORM)

**Frontend:**
- Next.js 14, TypeScript
- Tailwind CSS, Framer Motion
- Axios, Lucide Icons

---

## 📊 Уникальные фичи

| Фича | Реализация |
|------|-----------|
| **ML-обучение** | Анализ лайков/дизлайков → автообновление весов keywords |
| **Semantic dedup** | Embeddings через Gemini → кластеризация похожих новостей |
| **Background automation** | 4 scheduled jobs (обновление, обучение, cleanup, кеш) |
| **Multi-user ready** | PostgreSQL + миграции + user isolation |
| **Production-ready** | Error handling, logging, API docs, миграции БД |

---

## 📁 Структура проекта

```
finhack/
├── backend/
│   ├── api.py                    # FastAPI (все endpoints)
│   ├── background_worker.py      # Автоматизация
│   ├── modes/
│   │   ├── financial/            # Financial RADAR
│   │   └── personal/             # Personal Aggregator
│   │       ├── news_aggregator.py
│   │       ├── learning_engine.py    # ML обучение
│   │       ├── smart_updater.py      # Инкрементальное обновление
│   │       └── feed_storage.py       # Управление лентой
│   └── migrations/
│       └── 001_personal_news_tables.sql
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Главная (выбор режима)
│   │   ├── onboarding/page.tsx   # Онбординг (4 шага)
│   │   ├── personal/page.tsx     # Personal Aggregator
│   │   └── financial/page.tsx    # Financial RADAR
│   └── lib/
│       ├── api.ts                # API client
│       └── types.ts              # TypeScript типы
│
└── docs/
    ├── hh_case.md                # Задание
    ├── VIDEO_PRESENTATION_PLAN.md # План презентации
    └── QUICK_START_GUIDE.md      # Подробная инструкция
```

---

## 🎓 Для HeadHunter

### Соответствие критериям оценки:

✅ **Работоспособность** - всё работает, production-ready  
✅ **UX** - онбординг, фильтры, статистика, анимации  
✅ **Качество сводок** - Gemini суммаризация (2-3 предложения)  
✅ **Разнообразие источников** - RSS + ссылки на оригиналы  
✅ **Дедупликация** - semantic clustering через embeddings  
✅ **Бонусы** - ML обучение, автоматизация, два режима в одном!

### Инновации:
- **ML-персонализация** - система учится на поведении пользователя
- **Двухрежимность** - два продукта на единой инфраструктуре
- **Background automation** - не просто агрегатор, а умная система

---

## 📖 Документация

- **[VIDEO_PRESENTATION_PLAN.md](VIDEO_PRESENTATION_PLAN.md)** - план презентации для видео

---

## 📧 Контакты

**Repository:** GitHub (ссылка)  
**Live Demo:** (ссылка на деплой)  
**Video:** (ссылка на презентацию)

---

**Лицензия:** MIT

