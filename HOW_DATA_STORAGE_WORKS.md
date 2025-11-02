# 💾 Как работает сохранение данных

## ✅ Да! Система теперь сохраняет все предсказания

### Что сохраняется автоматически:

При каждом вызове API endpoint `/predict`, `/predict/batch`, или `/predict/csv`, система автоматически:

1. ✅ **Выполняет предсказание** с помощью ML модели
2. ✅ **Сохраняет результат в PostgreSQL**
3. ✅ **Кэширует в Redis** (для быстрого доступа)
4. ✅ **Возвращает результат** клиенту

---

## 📊 Что сохраняется в базе данных

### Таблица `predictions` содержит:

| Поле | Описание | Пример |
|------|----------|--------|
| `id` | Автоматический ID | 1, 2, 3... |
| `transaction_id` | Уникальный ID транзакции | "abc-123-def" |
| `transaction_data` | Все данные транзакции (JSONB) | `{"amount": 100.0, "hour": 14, ...}` |
| `prediction` | Результат: fraud или нет | `true` / `false` |
| `confidence` | Уверенность модели | `0.95` (95%) |
| `timestamp` | Когда было предсказание | `2025-11-01 12:00:00` |

---

## 🔄 Процесс сохранения

### Пример запроса:
```powershell
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

### Что происходит внутри:

1. **API получает запрос** → `/predict` endpoint
2. **Проверяет кэш** → Redis (если уже было предсказание)
3. **Выполняет предсказание** → ML модель
4. **Сохраняет в БД** → PostgreSQL (автоматически!)
5. **Кэширует результат** → Redis (TTL 1 час)
6. **Возвращает ответ** → JSON с результатом

---

## 📈 Примеры сохранения

### Одиночное предсказание:
```python
# При вызове /predict
POST /predict
{
  "amount": 100.50,
  "hour": 14,
  ...
}

# Автоматически сохраняется в БД:
INSERT INTO predictions (
    transaction_id,
    transaction_data,
    prediction,
    confidence
) VALUES (
    'uuid-generated-id',
    '{"amount": 100.50, ...}',
    false,
    0.85
)
```

### Пакетное предсказание:
```python
# При вызове /predict/batch
POST /predict/batch
{
  "transactions": [
    {"amount": 100.0, ...},
    {"amount": 5000.0, ...}
  ]
}

# Каждая транзакция сохраняется отдельно в БД
```

### CSV загрузка:
```python
# При вызове /predict/csv
POST /predict/csv
file: transactions.csv

# Все транзакции из CSV сохраняются в БД
```

---

## 🔍 Как проверить сохраненные данные

### 1. Через API:

```powershell
# Получить последние 10 транзакций
Invoke-RestMethod -Uri "http://localhost:8000/transactions?limit=10"

# Получить статистику
Invoke-RestMethod -Uri "http://localhost:8000/stats"
```

### 2. Через PostgreSQL:

```sql
-- Подключиться к БД
psql -U postgres -d fraud_detection

-- Посмотреть все сохраненные предсказания
SELECT * FROM predictions;

-- Количество записей
SELECT COUNT(*) FROM predictions;

-- Последние 10 предсказаний
SELECT 
    transaction_id,
    prediction,
    confidence,
    timestamp
FROM predictions
ORDER BY timestamp DESC
LIMIT 10;

-- Статистика мошенничества
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN prediction = true THEN 1 ELSE 0 END) as fraud_count,
    AVG(confidence) as avg_confidence
FROM predictions;
```

### 3. Только мошеннические транзакции:

```sql
SELECT 
    transaction_id,
    transaction_data,
    confidence,
    timestamp
FROM predictions
WHERE prediction = true
ORDER BY timestamp DESC;
```

---

## 📊 Использование сохраненных данных

### Dashboard статистика:
```powershell
# Получить полную статистику
$stats = Invoke-RestMethod -Uri "http://localhost:8000/stats"
$stats | ConvertTo-Json -Depth 5

# Результат:
{
  "total_transactions": 150,
  "fraud_count": 12,
  "fraud_percentage": 8.0,
  "hourly_stats": [
    {"hour": 0, "total": 5, "fraud_count": 1, ...},
    {"hour": 1, "total": 8, "fraud_count": 0, ...},
    ...
  ],
  "daily_stats": [
    {"date": "2025-11-01", "total": 50, "fraud_count": 4, ...},
    ...
  ]
}
```

### Анализ трендов:
```sql
-- Мошенничество по часам
SELECT 
    EXTRACT(HOUR FROM timestamp) as hour,
    COUNT(*) as total,
    SUM(CASE WHEN prediction = true THEN 1 ELSE 0 END) as fraud_count,
    ROUND(
        SUM(CASE WHEN prediction = true THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 
        2
    ) as fraud_percentage
FROM predictions
GROUP BY hour
ORDER BY fraud_percentage DESC;
```

---

## ✅ Преимущества сохранения данных

1. **История предсказаний** - Все предсказания сохраняются
2. **Аналитика** - Можно анализировать тренды мошенничества
3. **Аудит** - Полная история всех транзакций
4. **Отладка** - Можно проверить, почему было предсказание
5. **ML улучшение** - Данные можно использовать для retraining

---

## 🔄 Обновление существующих записей

Если транзакция с таким же `transaction_id` уже существует:

```sql
-- Автоматически обновляется (ON CONFLICT)
INSERT INTO predictions (...)
VALUES (...)
ON CONFLICT (transaction_id) 
DO UPDATE SET 
    transaction_data = EXCLUDED.transaction_data,
    prediction = EXCLUDED.prediction,
    confidence = EXCLUDED.confidence,
    timestamp = CURRENT_TIMESTAMP
```

Это означает:
- ✅ Дубликаты автоматически обновляются
- ✅ Последнее предсказание перезаписывает старое
- ✅ Timestamp обновляется

---

## 📈 Пример использования

### Сценарий: Тестирование API

```powershell
# 1. Сделать несколько предсказаний
for ($i=1; $i -le 10; $i++) {
    $body = @{
        amount = (Get-Random -Minimum 10 -Maximum 1000)
        hour = (Get-Random -Minimum 0 -Maximum 23)
        dayofweek = (Get-Random -Minimum 0 -Maximum 6)
        txns_last_24h = 5.0
        amount_last_24h = 500.0
        risk_score = (Get-Random -Minimum 10 -Maximum 100)
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body -ContentType "application/json"
    Start-Sleep -Milliseconds 500
}

# 2. Проверить, что все сохранилось
$transactions = Invoke-RestMethod -Uri "http://localhost:8000/transactions?limit=10"
Write-Host "Saved transactions: $($transactions.transactions.Count)"

# 3. Получить статистику
$stats = Invoke-RestMethod -Uri "http://localhost:8000/stats"
Write-Host "Total: $($stats.total_transactions), Fraud: $($stats.fraud_count)"
```

---

## 🎯 Итог

**✅ ДА! Система автоматически сохраняет все предсказания:**

- ✅ Каждое предсказание → БД
- ✅ Все данные транзакции → JSONB поле
- ✅ Результат и уверенность → BOOLEAN и FLOAT
- ✅ Timestamp → автоматически
- ✅ Доступ через API endpoints
- ✅ Доступ через SQL запросы

**Просто используйте API как обычно - все сохраняется автоматически!**

---

## 📝 Примечания

1. **База данных должна быть настроена** - PostgreSQL должен быть запущен
2. **Переменные окружения** - Должны быть установлены для подключения
3. **Автоматическое создание таблиц** - Таблицы создаются при первом запуске
4. **Нет данных?** - Проверьте health endpoint: `database_connected` должен быть `true`

---

**🎉 Теперь все ваши тесты и предсказания сохраняются в базе данных!**

