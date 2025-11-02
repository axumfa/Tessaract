# 🧪 Руководство по тестированию

## 🚀 Быстрый запуск тестов

### Способ 1: PowerShell скрипт (рекомендуется)
```powershell
.\run_tests.ps1
```

Скрипт автоматически:
- ✅ Проверит, запущен ли API
- ✅ Определит порт (8000 или 8001)
- ✅ Запустит все тесты
- ✅ Покажет результаты

### Способ 2: Ручной запуск
```powershell
# Убедитесь что API запущен
.\run.bat

# В другом терминале:
.\venv\Scripts\python.exe test_everything.py
```

---

## 📋 Что тестируется

### ✅ Основные тесты:

1. **API Health Check**
   - Проверка доступности API
   - Загрузка модели
   - Подключение к базе данных

2. **Home Endpoint**
   - Главная страница API

3. **Single Prediction**
   - Одиночное предсказание
   - Проверка всех полей ответа
   - Сохранение в БД

4. **Batch Prediction**
   - Пакетные предсказания
   - Обработка нескольких транзакций

5. **Get Transactions**
   - Получение сохраненных транзакций
   - Проверка сохранения данных

6. **Get Statistics**
   - Статистика мошенничества
   - Агрегированные данные

7. **Multiple Predictions**
   - Стресс-тест (5 транзакций)
   - Проверка производительности

8. **Invalid Input**
   - Обработка некорректных данных
   - Валидация входных данных

9. **Edge Cases**
   - Экстремальные значения
   - Большие суммы

---

## 📊 Интерпретация результатов

### ✅ PASS (Зеленый)
- Тест пройден успешно
- Функция работает корректно

### ⚠️ WARN (Желтый)
- Не критичная проблема
- Например: база данных не подключена (но API работает)

### ❌ FAIL (Красный)
- Критичная проблема
- Требует внимания

---

## 🔍 Что делать если тесты не проходят

### Проблема: "Cannot connect to API"

**Решение:**
1. Запустите API:
   ```powershell
   .\run.bat
   ```
2. Дождитесь сообщения:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```
3. Запустите тесты снова:
   ```powershell
   .\run_tests.ps1
   ```

### Проблема: "Model not loaded"

**Решение:**
- Проверьте наличие файла `src/fraud_detection_model.pkl`
- Убедитесь что модель находится в правильной папке

### Проблема: "Database not connected"

**Решение:**
1. Установите PostgreSQL (см. `INSTALL_POSTGRESQL.md`)
2. Создайте базу данных:
   ```sql
   CREATE DATABASE fraud_detection;
   ```
3. Установите переменные окружения:
   ```powershell
   $env:DB_HOST="localhost"
   $env:DB_NAME="fraud_detection"
   $env:DB_USER="postgres"
   $env:DB_PASSWORD="your_password"
   ```
4. Перезапустите API

### Проблема: "Transaction not saved to DB"

**Решение:**
- Это предупреждение, если БД не подключена
- Если БД подключена, подождите 1-2 секунды и проверьте снова

---

## 📈 Пример успешного запуска

```
============================================================
Fraud Detection API - Comprehensive Test Suite
============================================================
API URL: http://localhost:8000

Running tests...
------------------------------------------------------------
[OK] API Health Check
[OK] Model Loaded
[OK] Database Connected
[OK] Home Endpoint
[OK] Single Prediction - Transaction ID: abc12345..., Fraud: False, Confidence: 85.00%
[OK] Batch Prediction - Processed: 2, Fraud: 1
[OK] Multiple Predictions (5) - Processed in 2.45s
[OK] Get Transactions - Retrieved 10 transactions
[OK] Transaction Saved to DB
[OK] Get Statistics - Total: 8, Fraud: 1 (12.50%)
[OK] Invalid Input Handling - Correctly rejected with HTTP 422
[OK] Edge Cases (Large Amounts)

------------------------------------------------------------

Test Summary:
  Passed:  12
  Failed:  0
  Warnings: 0
  Total:   12

[SUCCESS] All critical tests passed!
```

---

## 🛠️ Расширенное тестирование

### Тест конкретного endpoint:
```python
import requests

# Простой тест
response = requests.get("http://localhost:8000/health")
print(response.json())
```

### Тест с кастомными данными:
```python
# В test_everything.py можно добавить свои тесты
def test_custom_scenario():
    # Ваш тест
    pass
```

---

## 📝 Логирование

Результаты тестов сохраняются в:
- Консольный вывод (real-time)
- Можно перенаправить в файл:
  ```powershell
  .\run_tests.ps1 | Tee-Object -FilePath test_results.txt
  ```

---

## ✅ Чек-лист перед тестированием

- [ ] API запущен (`.\run.bat`)
- [ ] Модель загружена (файл `fraud_detection_model.pkl` существует)
- [ ] PostgreSQL установлен и запущен (опционально, но желательно)
- [ ] База данных создана (опционально)
- [ ] Переменные окружения установлены (опционально)

---

**🎯 Запустите `.\run_tests.ps1` для полного тестирования системы!**

