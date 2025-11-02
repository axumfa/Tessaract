@echo off
REM Quick script to check database connection

echo Checking database connection...
echo.

REM Load .env file if exists
if exist ".env" (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        set "%%a=%%b"
    )
    echo [OK] Configuration loaded from .env
) else (
    echo [WARN] .env file not found
    echo Using default values or environment variables
)

echo.
echo Testing database connection...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

REM Run test script
python test_database.py

if %errorlevel% == 0 (
    echo.
    echo [SUCCESS] Database connection is working!
) else (
    echo.
    echo [ERROR] Database connection failed
    echo.
    echo Troubleshooting:
    echo   1. Check if PostgreSQL is running
    echo   2. Verify credentials in .env file
    echo   3. Make sure database 'fraud_detection' exists
    echo.
)

pause

