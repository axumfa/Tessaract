@echo off
REM Setup script - Install dependencies and prepare the environment

echo 🔧 Setting up Fraud Detection System...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🔹 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created.
) else (
    echo ✅ Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo 🔹 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment!
    pause
    exit /b 1
)
echo.

REM Upgrade pip
echo 🔹 Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo 🔹 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies!
    pause
    exit /b 1
)
echo.

REM Verify installation
echo 🔹 Verifying installation...
python -c "import fastapi; import uvicorn; import pandas; import joblib" 2>nul
if errorlevel 1 (
    echo ⚠️  Some dependencies may not be installed correctly.
) else (
    echo ✅ All required packages are installed.
)
echo.

echo ✅ Setup complete!
echo.
echo You can now run the API with:
echo   run.bat
echo   or
echo   python -m uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8000 --reload
echo.
pause

