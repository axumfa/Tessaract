# 🚀 Быстрая настройка базы данных

## ⚡ Самый быстрый способ

### Вариант 1: Автоматическая настройка (рекомендуется)
```powershell
.\setup_db_connection.ps1
```

Скрипт автоматически:
- ✅ Проверит PostgreSQL
- ✅ Протестирует подключение
- ✅ Создаст базу данных (если нужно)
- ✅ Установит переменные окружения
- ✅ Сохранит в `.env` файл

### Вариант 2: Ручная настройка

#### Шаг 1: Установите переменные окружения
```powershell
$env:DB_HOST="localhost"
$env:DB_NAME="fraud_detection"
$env:DB_USER="postgres"
$env:DB_PASSWORD="your_password"
```

#### Шаг 2: Создайте базу данных
```powershell
psql -U postgres
CREATE DATABASE fraud_detection;
\q
```

#### Шаг 3: Перезапустите API
```powershell
.\run.bat
```

---

## 🔍 Проверка подключения

### Проверка 1: Health endpoint
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

Должно показать:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true  ← должно быть true!
}
```

### Проверка 2: Тест подключения
```powershell
.\venv\Scripts\python.exe test_database.py
```

### Проверка 3: Проверить сохранение данных
```powershell
# Сделать предсказание
$body = @{
    amount = 100.50
    hour = 14
    dayofweek = 3
    txns_last_24h = 5.0
    amount_last_24h = 500.0
    risk_score = 25.5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body -ContentType "application/json"

# Проверить, что сохранилось
Invoke-RestMethod -Uri "http://localhost:8000/transactions?limit=1"
```

---

## ❌ Если PostgreSQL не установлен

1. Установите PostgreSQL (см. `INSTALL_POSTGRESQL.md`)
2. Или используйте API без БД (предсказания будут работать, но не сохраняться)

---

## ⚠️ Важно

После настройки переменных окружения:
1. **Перезапустите API** (`Ctrl+C` и затем `.\run.bat`)
2. API подхватит новые переменные окружения при запуске

---

**💡 Используйте `.\setup_db_connection.ps1` для автоматической настройки!**

