# 🔧 Исправление проблем PowerShell

## Проблемы, которые встречаются:

### 1. ❌ Проблема с кодировкой (Unicode/Emoji)

**Ошибка:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 1
```

**Причина:** Windows PowerShell использует кодировку cp1251 вместо UTF-8, и эмодзи не отображаются.

**Решение:** Используйте простой текст вместо эмодзи или настройте UTF-8.

### 2. ❌ ParserError в PowerShell

**Ошибка:**
```
ParserError: Неожиданный токен "}" в выражении или инструкции.
```

**Причина:** Проблемы с синтаксисом в многострочных командах или кавычках.

**Решение:** Упростите команды или используйте правильное экранирование.

### 3. ❌ Проблемы с выводом Write-Host

**Ошибка:** Эмодзи отображаются как иероглифы или вызывают ошибки.

**Решение:** Используйте простые символы или настройте кодировку.

---

## ✅ Решения

### Решение 1: Настройка кодировки UTF-8 в PowerShell

Добавьте в начало скриптов:

```powershell
# Установить кодировку UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
```

### Решение 2: Упростить эмодзи

Замените эмодзи на простой текст:

```powershell
# Вместо:
Write-Host "✅ Success" -ForegroundColor Green

# Используйте:
Write-Host "[OK] Success" -ForegroundColor Green
# или
Write-Host "Success" -ForegroundColor Green
```

### Решение 3: Исправить синтаксис многострочных команд

**Проблемный код:**
```powershell
$result = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue; if ($result) { Write-Host "✅ API is running on port $port"; Write-Host ""; try { $health = Invoke-RestMethod -Uri "http://localhost:$port/health"; Write-Host "✅ Health check: $($health | ConvertTo-Json)" } catch { Write-Host "⚠️ Port open but health check failed" } } else { Write-Host "❌ API is NOT running on port 8000" }
```

**Исправленный код:**
```powershell
$result = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($result) {
    Write-Host "API is running on port 8000" -ForegroundColor Green
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health"
        Write-Host "Health check:" -ForegroundColor Cyan
        $health | ConvertTo-Json
    } catch {
        Write-Host "Port open but health check failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "API is NOT running on port 8000" -ForegroundColor Red
}
```

---

## 🔧 Быстрые исправления

### Команда 1: Простая проверка API (без эмодзи)

```powershell
# Проверка порта
$port8000 = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue
$port8001 = Test-NetConnection -ComputerName localhost -Port 8001 -InformationLevel Quiet -WarningAction SilentlyContinue

if ($port8000 -or $port8001) {
    $port = if ($port8000) { 8000 } else { 8001 }
    Write-Host "API is running on port $port" -ForegroundColor Green
    
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:$port/health"
        Write-Host "Status: $($health.status)"
        Write-Host "Model Loaded: $($health.model_loaded)"
        Write-Host "Database Connected: $($health.database_connected)"
    } catch {
        Write-Host "Could not get health status" -ForegroundColor Yellow
    }
} else {
    Write-Host "API is not running" -ForegroundColor Red
}
```

### Команда 2: Проверка здоровья API (упрощенная)

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" | ConvertTo-Json
```

Или для порта 8001:
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/health" | ConvertTo-Json
```

### Команда 3: Тест предсказания (упрощенная)

```powershell
$body = @{
    amount = 100.50
    hour = 14
    dayofweek = 3
    txns_last_24h = 5.0
    amount_last_24h = 500.0
    risk_score = 25.5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body -ContentType "application/json" | ConvertTo-Json
```

---

## 📝 Рекомендации

### 1. Используйте простой текст в скриптах
- Вместо эмодзи используйте: `[OK]`, `[ERROR]`, `[INFO]`
- Или просто цвет: `Write-Host "Success" -ForegroundColor Green`

### 2. Разбивайте длинные команды на несколько строк
```powershell
# Плохо:
$result = Test-NetConnection ...; if ($result) { Write-Host ... } else { ... }

# Хорошо:
$result = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet
if ($result) {
    Write-Host "Port is open"
} else {
    Write-Host "Port is closed"
}
```

### 3. Используйте try-catch правильно
```powershell
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health"
    $response | ConvertTo-Json
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
```

### 4. Настройте кодировку в начале сессии
```powershell
# В начале PowerShell сессии:
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
```

---

## 🚀 Исправленные команды

### Проверка статуса API:
```powershell
$port = 8000
if (-not (Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue)) {
    $port = 8001
}

if (Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue) {
    Write-Host "API URL: http://localhost:$port/docs" -ForegroundColor Cyan
    Invoke-RestMethod -Uri "http://localhost:$port/health"
} else {
    Write-Host "API is not running" -ForegroundColor Red
}
```

### Запуск API:
```powershell
cd D:\Tesseract\Tessaract
.\run.bat
```

### Тест предсказания:
```powershell
$transaction = @{
    amount = 100.50
    hour = 14
    dayofweek = 3
    txns_last_24h = 5.0
    amount_last_24h = 500.0
    risk_score = 25.5
}

$json = $transaction | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $json -ContentType "application/json"
```

---

## ✅ Итог

Основные проблемы:
1. ✅ Кодировка - используйте UTF-8 или простой текст
2. ✅ Эмодзи - замените на текст или цвета
3. ✅ Синтаксис - разбивайте длинные команды на строки

**Самый простой способ:** Используйте файл `run.bat` вместо PowerShell скриптов, или упростите команды, убрав эмодзи.

