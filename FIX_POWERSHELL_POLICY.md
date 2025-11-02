# 🔧 Исправление проблемы PowerShell Execution Policy

## ❌ Проблема

```
.\run_tests.ps1 : Невозможно загрузить файл ... так как выполнение сценариев отключено
```

## ✅ Решение 1: Использовать .bat файл (рекомендуется)

Просто используйте:
```cmd
run_tests.bat
```

Этот файл работает без изменения политики PowerShell.

---

## ✅ Решение 2: Изменить политику выполнения PowerShell

### Временное изменение (для текущей сессии):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\run_tests.ps1
```

### Постоянное изменение (для текущего пользователя):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Требует подтверждения:**
- Нажмите `Y` для подтверждения

### Проверка текущей политики:
```powershell
Get-ExecutionPolicy
```

---

## ✅ Решение 3: Запуск с обходом политики

```powershell
powershell -ExecutionPolicy Bypass -File .\run_tests.ps1
```

Или:
```powershell
powershell.exe -ExecutionPolicy RemoteSigned -File .\run_tests.ps1
```

---

## ✅ Решение 4: Прямой запуск Python теста

```powershell
# Активировать venv
.\venv\Scripts\Activate.ps1

# Запустить тесты напрямую
python test_everything.py
```

Или с указанием порта:
```powershell
python test_everything.py http://localhost:8000
```

---

## 🎯 Рекомендация

**Самый простой способ:**
```cmd
run_tests.bat
```

Это работает сразу без изменения настроек!

---

## 🔍 Проверка политики выполнения

```powershell
# Посмотреть текущую политику
Get-ExecutionPolicy -List

# Результат покажет:
#    Scope ExecutionPolicy
#    ----- ---------------
# MachinePolicy       Undefined
#    UserPolicy       Undefined
#       Process       Undefined
#   CurrentUser       Restricted  <- Это может быть проблемой
#  LocalMachine       Restricted
```

---

## 📝 Подробнее о политиках

| Политика | Описание |
|----------|----------|
| **Restricted** | Блокирует все скрипты (по умолчанию) |
| **RemoteSigned** | Разрешает локальные скрипты, требует подписи для удаленных |
| **AllSigned** | Требует подписи для всех скриптов |
| **Unrestricted** | Разрешает все (небезопасно) |
| **Bypass** | Полностью отключает проверки (только для текущего запуска) |

---

## 🚀 Быстрый старт

### Вариант А (рекомендуется):
```cmd
run_tests.bat
```

### Вариант Б:
```powershell
# Установить политику один раз
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Затем запускать как обычно
.\run_tests.ps1
```

### Вариант В:
```powershell
# Запуск с обходом
powershell -ExecutionPolicy Bypass -File .\run_tests.ps1
```

---

**✅ Используйте `run_tests.bat` - это самый простой способ!**

