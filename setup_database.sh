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
POSTGRES_USER="postgres"  # Суперпользователь для создания БД и пользователя

echo -e "${GREEN}🚀 Настройка базы данных для Finhack (системный PostgreSQL)${NC}"
echo ""

# Проверка PostgreSQL
echo -e "${YELLOW}[1/5]${NC} Проверка PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL (psql) не установлен!${NC}"
    echo "Установите: sudo apt-get install postgresql postgresql-client"
    exit 1
fi

# Проверка что PostgreSQL запущен
if ! pg_isready -h ${DB_HOST} -p ${DB_PORT} &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL не запущен!${NC}"
    echo "Запустите: sudo systemctl start postgresql"
    exit 1
fi
echo -e "${GREEN}✓${NC} PostgreSQL работает"

# Проверка и создание пользователя
echo -e "${YELLOW}[2/5]${NC} Проверка пользователя..."
USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" 2>/dev/null)

if [ "$USER_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓${NC} Пользователь '${DB_USER}' существует"
else
    echo "Создаём пользователя '${DB_USER}'..."
    sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';" &> /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Пользователь создан"
    else
        echo -e "${RED}❌ Не удалось создать пользователя${NC}"
        exit 1
    fi
fi

# Проверка и создание базы данных
echo -e "${YELLOW}[3/5]${NC} Проверка базы данных..."
DB_EXISTS=$(sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -w ${DB_NAME} | wc -l)

if [ "$DB_EXISTS" -eq "1" ]; then
    echo -e "${GREEN}✓${NC} База данных '${DB_NAME}' существует"
else
    echo "Создаём базу данных '${DB_NAME}'..."
    sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};" &> /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} База данных создана"
    else
        echo -e "${RED}❌ Не удалось создать базу данных${NC}"
        exit 1
    fi
fi

# Выдача прав пользователю
echo -e "${YELLOW}[4/5]${NC} Настройка прав доступа..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};" &> /dev/null
sudo -u postgres psql -d ${DB_NAME} -c "GRANT ALL ON SCHEMA public TO ${DB_USER};" &> /dev/null
sudo -u postgres psql -d ${DB_NAME} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER};" &> /dev/null
echo -e "${GREEN}✓${NC} Права настроены"

# Применение миграций
echo -e "${YELLOW}[5/5]${NC} Применение миграций..."

# Миграция 001: Основные таблицы
if [ -f "backend/migrations/001_personal_news_tables.sql" ]; then
    # Проверяем существует ли уже таблица user_profiles
    TABLE_EXISTS=$(PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_profiles');" 2>/dev/null)
    
    if [ "$TABLE_EXISTS" = "t" ]; then
        echo -e "${GREEN}✓${NC} Миграция 001 уже применена"
    else
        echo "Применяем миграцию 001_personal_news_tables.sql..."
        PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} < backend/migrations/001_personal_news_tables.sql > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} Миграция 001 применена успешно"
        else
            echo -e "${RED}❌ Ошибка при применении миграции 001${NC}"
            echo "Попробуйте применить вручную:"
            echo "PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} < backend/migrations/001_personal_news_tables.sql"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} Файл миграции 001 не найден"
    echo "Пропускаем..."
fi

# Миграция 002: Добавление last_feed_check
if [ -f "backend/migrations/002_add_last_feed_check.sql" ]; then
    # Проверяем существует ли уже колонка last_feed_check
    COLUMN_EXISTS=$(PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -tAc "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'last_feed_check');" 2>/dev/null)
    
    if [ "$COLUMN_EXISTS" = "t" ]; then
        echo -e "${GREEN}✓${NC} Миграция 002 уже применена"
    else
        echo "Применяем миграцию 002_add_last_feed_check.sql..."
        PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} < backend/migrations/002_add_last_feed_check.sql > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} Миграция 002 применена успешно"
        else
            echo -e "${RED}❌ Ошибка при применении миграции 002${NC}"
            echo "Попробуйте применить вручную:"
            echo "PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} < backend/migrations/002_add_last_feed_check.sql"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} Файл миграции 002 не найден"
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
echo "    PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME}"
echo ""
echo "  • Или через sudo:"
echo "    sudo -u postgres psql -d ${DB_NAME}"
echo ""
echo "  • Удалить всё и начать заново:"
echo "    sudo -u postgres psql -c \"DROP DATABASE IF EXISTS ${DB_NAME};\""
echo "    sudo -u postgres psql -c \"DROP USER IF EXISTS ${DB_USER};\""
echo ""
echo -e "${GREEN}🚀 Теперь можно запускать backend!${NC}"
