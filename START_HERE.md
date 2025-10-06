# 🚀 Быстрый старт с PostgreSQL

## 1️⃣ Запустить PostgreSQL

```bash
# В корне проекта
docker-compose up -d
```

## 2️⃣ Установить зависимости

```bash
cd backend
pip install -r requirements.txt
```

## 3️⃣ Настроить .env (если еще не настроено)

Добавьте в ваш `.env` файл:

```env
# Database URL (уже настроен для Docker)
DATABASE_URL=postgresql+asyncpg://radar_user:radar_password_2024@localhost:5432/finhack
```

## 4️⃣ Запустить приложение

```bash
cd backend
python api.py
```

## 5️⃣ Открыть веб-интерфейс

```
http://localhost:8000
```

---

## 🎯 Что нового?

### Две вкладки в интерфейсе:

#### 🚀 New Scan
- Запуск новой обработки новостей
- Результаты автоматически сохраняются в БД

#### 📜 History
- **Список всех предыдущих запусков**
- Показывает дату, количество stories, статистику
- **Кликните на запуск** чтобы посмотреть детали и stories

---

## 📊 API эндпоинты

```bash
# Получить историю
curl http://localhost:8000/api/history

# Получить детали запуска
curl http://localhost:8000/api/history/1

# Очистить старые запуски (оставить последние 50)
curl -X DELETE "http://localhost:8000/api/history/cleanup?keep_last_n=50"
```

---

## 🛠️ Управление Docker

```bash
# Просмотр логов
docker-compose logs -f postgres

# Остановить
docker-compose stop

# Запустить снова
docker-compose start

# Удалить с данными
docker-compose down -v
```

---

## 📖 Подробная документация

См. `SETUP_DATABASE.md` для полной информации.

