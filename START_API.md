# 🚀 Как запустить и проверить API

## Быстрый старт

### Вариант 1: Простой скрипт (рекомендуется)

**В PowerShell:**
```powershell
.\run.bat
```

**В обычной командной строке (CMD):**
```cmd
run.bat
```

Скрипт автоматически:
- ✅ Проверит виртуальное окружение
- ✅ Установит зависимости (если нужно)
- ✅ Запустит API на порту 8000

---

## Проверка статуса API

### Способ 1: Через браузер

Откройте в браузере:
- **http://localhost:8000/docs** — интерактивная документация
- **http://localhost:8000/health** — проверка здоровья API

### Способ 2: Через PowerShell

```powershell
# Проверка порта
Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet

# Проверка health endpoint
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Или через curl
curl http://localhost:8000/health
```

### Способ 3: Используйте скрипт

```powershell
.\test_api.ps1
```

---

## Ручной запуск

### Шаг 1: Активировать виртуальное окружение

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
venv\Scripts\activate.bat
```

### Шаг 2: Запустить API

```powershell
python -m uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8000 --reload
```

Флаг `--reload` включает автоматическую перезагрузку при изменении кода.

---

## Проверка работы API

### 1. Health Check

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

Должен вернуть:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": false
}
```

### 2. Тест предсказания

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

### 3. Открыть документацию

Просто откройте в браузере:
**http://localhost:8000/docs**

Там можно:
- ✅ Увидеть все endpoints
- ✅ Протестировать API интерактивно
- ✅ Увидеть схемы данных

---

## Остановка API

### Если запущен через скрипт:
Нажмите `Ctrl+C` в окне терминала

### Если запущен как фоновый процесс:
```powershell
# Найти процесс
Get-Process | Where-Object {$_.ProcessName -eq "python"}

# Остановить (замените ID на реальный)
Stop-Process -Id <PROCESS_ID> -Force
```

Или найти и остановить через порт:
```powershell
$port = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port) {
    Stop-Process -Id $port.OwningProcess -Force
}
```

---

## Решение проблем

### ❌ "Port 8000 already in use"

**Решение:** Используйте другой порт:
```powershell
python -m uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8001 --reload
```

### ❌ "Module not found"

**Решение:** Установите зависимости:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ❌ "python-multipart not found"

**Решение:**
```powershell
pip install python-multipart
```

### ❌ API не отвечает

**Проверьте:**
1. Виртуальное окружение активировано?
2. Все зависимости установлены?
3. Модель файл существует? (`src/fraud_detection_model.pkl`)

---

## Полезные команды

### Просмотр логов в реальном времени
API автоматически показывает логи при запуске.

### Проверка всех endpoints
```powershell
# Список всех endpoints
curl http://localhost:8000/docs
```

### Полный тест API
```powershell
.\test_api.ps1
```

---

## Готовые скрипты

| Скрипт | Описание |
|--------|----------|
| `run.bat` | Запуск API (Windows) |
| `setup.bat` | Первоначальная настройка |
| `test_api.ps1` | Тестирование API |
| `fix_pydantic.bat` | Исправление pydantic |

---

**✅ После запуска API будет доступен на http://localhost:8000**

