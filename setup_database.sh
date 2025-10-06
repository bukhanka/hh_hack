#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Параметры подключения
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="finhack"
DB_USER="radar_user"
DB_PASSWORD="radar_password_2024"
CONTAINER_NAME="finhack_postgres"

echo -e "${GREEN}🚀 Настройка базы данных для Finhack${NC}"
echo ""

# Проверка Docker
echo -e "${YELLOW}[1/6]${NC} Проверка Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не установлен!${NC}"
    echo "Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon не запущен!${NC}"
    echo "Запустите Docker и попробуйте снова."
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker работает"

# Проверка docker-compose
echo -e "${YELLOW}[2/6]${NC} Проверка docker-compose..."
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ docker-compose не установлен!${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} docker-compose доступен"

# Проверка контейнера PostgreSQL
echo -e "${YELLOW}[3/6]${NC} Проверка контейнера PostgreSQL..."
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' ${CONTAINER_NAME})
    if [ "$CONTAINER_STATUS" = "running" ]; then
        echo -e "${GREEN}✓${NC} Контейнер ${CONTAINER_NAME} уже запущен"
    else
        echo -e "${YELLOW}⚠${NC} Контейнер ${CONTAINER_NAME} существует, но не запущен. Запускаем..."
        docker start ${CONTAINER_NAME}
        sleep 3
    fi
else
    echo -e "${YELLOW}⚠${NC} Контейнер не найден. Создаём через docker-compose..."
    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d
    else
        echo -e "${RED}❌ Файл docker-compose.yml не найден!${NC}"
        exit 1
    fi
fi

# Ожидание готовности БД
echo -e "${YELLOW}[4/6]${NC} Ожидание готовности PostgreSQL..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker exec ${CONTAINER_NAME} pg_isready -U ${DB_USER} -d ${DB_NAME} &> /dev/null; then
        echo -e "${GREEN}✓${NC} PostgreSQL готов к работе"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo -n "."
    sleep 1
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo -e "\n${RED}❌ Таймаут ожидания PostgreSQL${NC}"
    echo "Проверьте логи: docker logs ${CONTAINER_NAME}"
    exit 1
fi
echo ""

# Проверка подключения и наличия БД
echo -e "${YELLOW}[5/6]${NC} Проверка базы данных и пользователя..."

# Проверка что БД существует
DB_EXISTS=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -lqt | cut -d \| -f 1 | grep -w ${DB_NAME} | wc -l)

if [ "$DB_EXISTS" -eq "1" ]; then
    echo -e "${GREEN}✓${NC} База данных '${DB_NAME}' существует"
else
    echo -e "${RED}❌ База данных '${DB_NAME}' не найдена${NC}"
    echo "Создаём базу данных..."
    docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -c "CREATE DATABASE ${DB_NAME};" &> /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} База данных создана"
    else
        echo -e "${RED}❌ Не удалось создать базу данных${NC}"
        exit 1
    fi
fi

# Проверка пользователя
USER_EXISTS=$(docker exec ${CONTAINER_NAME} psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'")

if [ "$USER_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓${NC} Пользователь '${DB_USER}' существует"
else
    echo -e "${YELLOW}⚠${NC} Пользователь '${DB_USER}' не найден. Создаём..."
    docker exec ${CONTAINER_NAME} psql -U postgres -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';" &> /dev/null
    docker exec ${CONTAINER_NAME} psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};" &> /dev/null
    echo -e "${GREEN}✓${NC} Пользователь создан"
fi

# Применение миграций
echo -e "${YELLOW}[6/6]${NC} Применение миграций..."

if [ -f "backend/migrations/001_personal_news_tables.sql" ]; then
    # Проверяем существует ли уже таблица user_profiles
    TABLE_EXISTS=$(docker exec ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_profiles');")
    
    if [ "$TABLE_EXISTS" = "t" ]; then
        echo -e "${GREEN}✓${NC} Таблицы уже существуют (миграция применена ранее)"
    else
        echo "Применяем миграцию 001_personal_news_tables.sql..."
        docker exec -i ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} < backend/migrations/001_personal_news_tables.sql > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} Миграция применена успешно"
        else
            echo -e "${RED}❌ Ошибка при применении миграции${NC}"
            echo "Попробуйте применить вручную:"
            echo "docker exec -i ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME} < backend/migrations/001_personal_news_tables.sql"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} Файл миграции не найден (backend/migrations/001_personal_news_tables.sql)"
    echo "Пропускаем..."
fi

# Итоговая информация
echo ""
echo -e "${GREEN}✅ Настройка завершена успешно!${NC}"
echo ""
echo "📊 Информация о подключении:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Host:     ${DB_HOST}"
echo "  Port:     ${DB_PORT}"
echo "  Database: ${DB_NAME}"
echo "  User:     ${DB_USER}"
echo "  Password: ${DB_PASSWORD}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 Connection String:"
echo "  postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo ""
echo "🛠️  Полезные команды:"
echo "  • Подключиться к БД:"
echo "    docker exec -it ${CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME}"
echo ""
echo "  • Просмотр логов:"
echo "    docker logs ${CONTAINER_NAME}"
echo ""
echo "  • Остановить контейнер:"
echo "    docker-compose down"
echo ""
echo "  • Перезапустить контейнер:"
echo "    docker-compose restart"
echo ""
echo -e "${GREEN}🚀 Теперь можно запускать backend!${NC}"

