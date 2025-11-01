@echo off
REM Simple batch script to run FastAPI service on Windows

echo 🚀 Starting Fraud Detection System...

REM Activate virtual environment
echo 🔹 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if FastAPI port is available
netstat -ano | findstr :8000 >nul
if %errorlevel% == 0 (
    echo ⚠️  Port 8000 is already in use.
    echo 🔹 Trying to start on port 8001...
    set FASTAPI_PORT=8001
) else (
    set FASTAPI_PORT=8000
)

REM Start FastAPI
echo 🔹 Starting FastAPI API on port %FASTAPI_PORT%...
echo 📖 API will be available at: http://localhost:%FASTAPI_PORT%
echo 📖 API Docs: http://localhost:%FASTAPI_PORT%/docs
echo.
echo Press Ctrl+C to stop the server...
echo.

uvicorn src.fastapi_service:app --host 0.0.0.0 --port %FASTAPI_PORT% --reload

pause

