# 🗄️ Database Integration Guide

## ✅ Что было сделано

### 1. Создан модуль `src/database.py`
- ✅ Connection pooling для эффективного управления соединениями
- ✅ Автоматическое создание таблиц и индексов
- ✅ Context managers для безопасной работы с БД
- ✅ Правильная обработка ошибок и транзакций
- ✅ Улучшенные функции для работы с данными

### 2. Обновлен `src/fastapi_service.py`
- ✅ Использует новый модуль базы данных
- ✅ Startup/shutdown events для управления lifecycle
- ✅ Улучшенная обработка ошибок
- ✅ Убрано дублирование кода

---

## 🔧 Особенности новой интеграции

### Connection Pooling
```python
# Автоматический пул соединений (1-20 соединений)
_connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=20,
    ...
)
```

**Преимущества:**
- ✅ Эффективное использование ресурсов
- ✅ Автоматическое управление соединениями
- ✅ Защита от перегрузки БД

### Context Managers
```python
# Безопасная работа с БД
with get_db_cursor() as cur:
    cur.execute("SELECT ...")
    # Автоматический commit при успехе
    # Автоматический rollback при ошибке
```

### Индексы для производительности
- ✅ Индекс на `transaction_id` (быстрый поиск)
- ✅ Индекс на `timestamp` (быстрые временные запросы)
- ✅ Индекс на `prediction` (быстрая фильтрация мошенничества)

---

## 📊 Структура базы данных

### Таблица `predictions`
```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE,  -- Уникальный ID транзакции
    transaction_data JSONB,              -- Полные данные транзакции
    prediction BOOLEAN NOT NULL,        -- Результат предсказания
    confidence FLOAT NOT NULL,          -- Уверенность модели
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Индексы
- `idx_predictions_transaction_id` - для поиска по ID
- `idx_predictions_timestamp` - для временных запросов
- `idx_predictions_prediction` - для фильтрации мошенничества

---

## 🚀 Использование

### Автоматическая инициализация
База данных автоматически инициализируется при запуске API:

```python
# В fastapi_service.py
@app.on_event("startup")
async def startup_event():
    init_db()  # Автоматически создает таблицы и индексы
```

### Логирование предсказаний
```python
# Автоматически при каждом предсказании
log_prediction(
    transaction_id="12345",
    transaction_data={"amount": 100.0, ...},
    prediction=True,
    confidence=0.95
)
```

### Получение данных
```python
# Последние транзакции
transactions = get_recent_transactions(limit=100)

# Статистика мошенничества
stats = get_fraud_stats()
```

---

## ⚙️ Конфигурация

### Переменные окружения
```bash
DB_HOST=localhost          # Хост PostgreSQL
DB_NAME=fraud_detection    # Имя базы данных
DB_USER=postgres           # Пользователь
DB_PASSWORD=your_password  # Пароль
DB_PORT=5432              # Порт (опционально)
```

### Установка переменных (PowerShell)
```powershell
$env:DB_HOST="localhost"
$env:DB_NAME="fraud_detection"
$env:DB_USER="postgres"
$env:DB_PASSWORD="your_password"
```

### Установка переменных (Linux/Mac)
```bash
export DB_HOST=localhost
export DB_NAME=fraud_detection
export DB_USER=postgres
export DB_PASSWORD=your_password
```

---

## 🔍 Проверка работы

### 1. Проверка подключения
```powershell
# Health check endpoint
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Должно вернуть:
# {
#   "status": "healthy",
#   "model_loaded": true,
#   "database_connected": true  ← должно быть true!
# }
```

### 2. Тест записи
```powershell
# Сделать предсказание (автоматически сохранится в БД)
$body = @{
    amount = 100.50
    hour = 14
    dayofweek = 3
    txns_last_24h = 5.0
    amount_last_24h = 500.0
    risk_score = 25.5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body -ContentType "application/json"
```

### 3. Проверка данных
```powershell
# Получить последние транзакции
Invoke-RestMethod -Uri "http://localhost:8000/transactions?limit=10"

# Получить статистику
Invoke-RestMethod -Uri "http://localhost:8000/stats"
```

### 4. Проверка в PostgreSQL
```sql
-- Подключиться к БД
psql -U postgres -d fraud_detection

-- Проверить таблицу
SELECT COUNT(*) FROM predictions;

-- Посмотреть последние записи
SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;

-- Проверить индексы
\di predictions
```

---

## 🛠️ Устранение проблем

### Проблема: "Database not available"

**Причины:**
1. PostgreSQL не запущен
2. Неправильные credentials
3. База данных не создана

**Решение:**
```bash
# 1. Проверить PostgreSQL
Get-Service postgresql*

# 2. Создать базу данных
psql -U postgres
CREATE DATABASE fraud_detection;

# 3. Проверить переменные окружения
echo $env:DB_HOST
echo $env:DB_NAME
echo $env:DB_USER
```

### Проблема: "Connection refused"

**Решение:**
1. Проверить, что PostgreSQL запущен
2. Проверить порт (по умолчанию 5432)
3. Проверить настройки firewall

### Проблема: "Table doesn't exist"

**Решение:**
Таблицы создаются автоматически при первом запуске.
Если проблема сохраняется:
```python
# Вручную вызвать
from src.database import init_db
init_db()
```

---

## 📈 Производительность

### Оптимизации:
- ✅ Connection pooling (переиспользование соединений)
- ✅ Индексы на часто используемых полях
- ✅ Batch operations где возможно
- ✅ Оптимизированные SQL запросы

### Мониторинг:
```sql
-- Количество активных соединений
SELECT count(*) FROM pg_stat_activity WHERE datname = 'fraud_detection';

-- Размер таблицы
SELECT pg_size_pretty(pg_total_relation_size('predictions'));

-- Статистика использования индексов
SELECT * FROM pg_stat_user_indexes WHERE tablename = 'predictions';
```

---

## 🔐 Безопасность

### Рекомендации:
1. ✅ Использовать переменные окружения для паролей
2. ✅ Не хранить пароли в коде
3. ✅ Использовать отдельного пользователя БД (не postgres)
4. ✅ Настроить SSL для production

### Создание пользователя:
```sql
-- Создать пользователя для приложения
CREATE USER fraud_app_user WITH PASSWORD 'strong_password';

-- Дать права на базу данных
GRANT ALL PRIVILEGES ON DATABASE fraud_detection TO fraud_app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fraud_app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fraud_app_user;
```

---

## 🧪 Тестирование

### Unit тесты:
```python
# tests/test_database.py
from src.database import init_db, log_prediction, get_recent_transactions

def test_log_prediction():
    assert log_prediction("test_id", {}, True, 0.95) == True

def test_get_transactions():
    transactions = get_recent_transactions(10)
    assert isinstance(transactions, list)
```

---

## ✅ Преимущества новой интеграции

### По сравнению со старым кодом:
1. ✅ **Connection Pooling** - эффективное использование ресурсов
2. ✅ **Автоматическое управление транзакциями** - меньше ошибок
3. ✅ **Индексы** - быстрые запросы
4. ✅ **Переиспользование кода** - DRY принцип
5. ✅ **Улучшенная обработка ошибок** - более надежно
6. ✅ **Готовность к production** - правильные практики

---

## 📚 Дополнительные ресурсы

- PostgreSQL Connection Pooling: https://www.postgresql.org/docs/current/libpq-pooling.html
- psycopg2 Documentation: https://www.psycopg.org/docs/
- FastAPI Database: https://fastapi.tiangolo.com/tutorial/sql-databases/

---

## 🎯 Следующие шаги

После интеграции можно:
1. ✅ Добавить миграции (Alembic)
2. ✅ Добавить тесты
3. ✅ Настроить мониторинг
4. ✅ Оптимизировать запросы
5. ✅ Добавить резервное копирование

---

**✅ База данных успешно интегрирована!**

