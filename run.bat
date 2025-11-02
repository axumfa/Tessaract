@echo off
REM Simple batch script to run FastAPI service on Windows

echo 🚀 Starting Fraud Detection System...
echo.

REM Load environment variables from .env file if it exists
if exist ".env" (
    echo 🔹 Loading database configuration from .env file...
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        REM Skip empty lines and comments
        if not "%%a"=="" if not "%%a"=="REM" (
            set "%%a=%%b"
        )
    )
    echo [OK] Configuration loaded
    echo.
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo 🔹 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment. Please install Python first.
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created.
)

REM Activate virtual environment
echo 🔹 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Check if uvicorn is installed
python -c "import uvicorn" 2>nul
if errorlevel 1 (
    echo ❌ Dependencies not installed!
    echo 🔹 Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies.
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed.
    echo.
)

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

python -m uvicorn src.fastapi_service:app --host 0.0.0.0 --port %FASTAPI_PORT% --reload

pause

