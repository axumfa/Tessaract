# 🐘 Установка PostgreSQL для Windows

## Способ 1: Установщик Windows (рекомендуется)

### Шаг 1: Скачать PostgreSQL

1. Перейдите на официальный сайт: https://www.postgresql.org/download/windows/
2. Нажмите **"Download the installer"**
3. Выберите версию (рекомендуется **PostgreSQL 15** или новее)
4. Скачайте установщик для Windows x86-64

### Шаг 2: Установка

1. **Запустите установщик** (например, `postgresql-15.x-x64.exe`)

2. **Мастер установки:**
   - Нажмите **"Next"** на всех экранах
   - Выберите папку установки (по умолчанию: `C:\Program Files\PostgreSQL\15`)
   - Выберите компоненты (оставьте все по умолчанию):
     - ✅ PostgreSQL Server
     - ✅ pgAdmin 4 (графический интерфейс)
     - ✅ Stack Builder
     - ✅ Command Line Tools

3. **Настройка данных:**
   - Папка данных: `C:\Program Files\PostgreSQL\15\data` (по умолчанию)
   - Нажмите **"Next"**

4. **Пароль суперпользователя:**
   - ⚠️ **ВАЖНО:** Запомните пароль для пользователя `postgres`!
   - Введите пароль (например: `postgres` или более надежный)
   - Подтвердите пароль
   - **Запишите пароль** — он понадобится позже!

5. **Порт:**
   - Оставьте по умолчанию: **5432**
   - Нажмите **"Next"**

6. **Локаль:**
   - Оставьте по умолчанию: `[Default locale]`
   - Нажмите **"Next"**

7. **Готово к установке:**
   - Проверьте настройки
   - Нажмите **"Next"** для начала установки

8. **Завершение установки:**
   - ✅ Снимите галочку с **"Launch Stack Builder"** (не нужно)
   - ✅ Оставьте галочку на **"Launch pgAdmin 4"** (полезно)
   - Нажмите **"Finish"**

### Шаг 3: Проверка установки

**Откройте PowerShell или CMD и выполните:**

```powershell
# Проверка версии PostgreSQL
psql --version

# Проверка, что сервис запущен
Get-Service -Name postgresql*
```

Если команда `psql` не найдена, добавьте PostgreSQL в PATH:

1. Откройте **Системные переменные окружения**
2. Найдите переменную `Path`
3. Добавьте: `C:\Program Files\PostgreSQL\15\bin`
4. Перезапустите терминал

---

## Способ 2: Через Chocolatey (для опытных пользователей)

Если у вас установлен Chocolatey:

```powershell
# Установка PostgreSQL
choco install postgresql15

# Или последней версии
choco install postgresql
```

---

## Способ 3: Через Docker (альтернатива)

Если у вас установлен Docker:

```powershell
# Запуск PostgreSQL в Docker контейнере
docker run --name postgres-fraud -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=fraud_detection -p 5432:5432 -d postgres:15

# Проверка
docker ps
```

**Преимущества Docker:**
- ✅ Легко запустить/остановить
- ✅ Не засоряет систему
- ✅ Легко удалить

---

## Настройка базы данных для Fraud Detection API

### Вариант 1: Через psql (командная строка)

1. **Откройте PowerShell как Администратор**

2. **Подключитесь к PostgreSQL:**
   ```powershell
   psql -U postgres
   ```
   Введите пароль, который вы установили

3. **Создайте базу данных:**
   ```sql
   CREATE DATABASE fraud_detection;
   ```

4. **Проверьте:**
   ```sql
   \l
   ```
   Должна появиться база данных `fraud_detection`

5. **Выйдите:**
   ```sql
   \q
   ```

### Вариант 2: Через pgAdmin 4 (графический интерфейс)

1. **Откройте pgAdmin 4** (из меню Start или из установки)

2. **Подключитесь к серверу:**
   - Правой кнопкой на **"Servers"** → **"Create"** → **"Server"**
   - **General**:
     - Name: `Fraud Detection Server`
   - **Connection**:
     - Host: `localhost`
     - Port: `5432`
     - Username: `postgres`
     - Password: ваш пароль
   - Нажмите **"Save"**

3. **Создайте базу данных:**
   - Правой кнопкой на **"Databases"** → **"Create"** → **"Database"**
   - Database name: `fraud_detection`
   - Owner: `postgres`
   - Нажмите **"Save"**

---

## Настройка FastAPI для подключения к PostgreSQL

### Шаг 1: Установите переменные окружения

**PowerShell:**
```powershell
# Временно (только для текущей сессии)
$env:DB_HOST="localhost"
$env:DB_NAME="fraud_detection"
$env:DB_USER="postgres"
$env:DB_PASSWORD="your_password_here"
```

**Или создайте файл `.env`** (в корне проекта):

```env
DB_HOST=localhost
DB_NAME=fraud_detection
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### Шаг 2: Перезапустите API

```powershell
# Остановите текущий API (Ctrl+C)
# Затем запустите снова
.\run.bat
```

### Шаг 3: Проверьте подключение

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8001/health"

# Должен вернуть:
# {
#   "status": "healthy",
#   "model_loaded": true,
#   "database_connected": true  ← должно быть true!
# }
```

---

## Полезные команды PostgreSQL

### Подключение к базе данных:
```powershell
psql -U postgres -d fraud_detection
```

### Просмотр таблиц:
```sql
\dt
```

### Просмотр структуры таблицы:
```sql
\d predictions
```

### Просмотр данных:
```sql
SELECT * FROM predictions LIMIT 10;
```

### Статистика:
```sql
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN prediction = true THEN 1 ELSE 0 END) as fraud_count
FROM predictions;
```

---

## Решение проблем

### ❌ "psql не является внутренней или внешней командой"

**Решение:** Добавьте PostgreSQL в PATH:
1. Найдите папку установки: `C:\Program Files\PostgreSQL\15\bin`
2. Добавьте в переменную `Path` в системных настройках
3. Перезапустите терминал

### ❌ "Connection refused" или "Could not connect to server"

**Решение:** Проверьте, запущен ли сервис PostgreSQL:
```powershell
# Проверка статуса
Get-Service -Name postgresql*

# Запуск сервиса (если остановлен)
Start-Service postgresql-x64-15
```

Или через Services:
1. Нажмите `Win + R`
2. Введите `services.msc`
3. Найдите **PostgreSQL x64-15**
4. Убедитесь, что статус: **Running**

### ❌ "Password authentication failed"

**Решение:**
1. Проверьте правильность пароля
2. Попробуйте сбросить пароль:
   ```powershell
   # Остановить службу
   Stop-Service postgresql-x64-15
   
   # Изменить пароль в файле pg_hba.conf
   # (требует редактирования конфига, сложнее)
   ```

Или просто переустановите PostgreSQL с известным паролем.

### ❌ "Database does not exist"

**Решение:** Создайте базу данных:
```sql
psql -U postgres
CREATE DATABASE fraud_detection;
\q
```

---

## Быстрая установка (TL;DR)

1. Скачайте: https://www.postgresql.org/download/windows/
2. Установите (пароль: `postgres`)
3. Создайте БД: `psql -U postgres` → `CREATE DATABASE fraud_detection;`
4. Настройте переменные окружения
5. Перезапустите API

---

## Дополнительные ресурсы

- **Официальная документация:** https://www.postgresql.org/docs/
- **pgAdmin документация:** https://www.pgadmin.org/docs/
- **Tutorial:** https://www.postgresqltutorial.com/

---

**✅ После установки PostgreSQL ваш API сможет сохранять предсказания и показывать статистику!**


