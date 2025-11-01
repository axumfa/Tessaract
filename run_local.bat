@echo off
REM Windows batch script to run the Fraud Detection API locally

echo ============================================================
echo Fraud Detection API - Local Runner (Windows)
echo ============================================================
echo.

REM Check if virtual environment exists (handle both Windows and Unix-style venvs)
if exist "venv\Scripts\python.exe" (
    echo Virtual environment found (Windows style), using Python from venv...
    set PATH=%~dp0venv\Scripts;%PATH%
    set PYTHON_CMD=venv\Scripts\python.exe
) else (
    if exist "venv\bin\python" (
        echo Virtual environment found (Unix style), using Python from venv...
        set PATH=%~dp0venv\bin;%PATH%
        set PYTHON_CMD=venv\bin\python
    ) else (
        echo Warning: Virtual environment not found
        echo Please create one with: python -m venv venv
        pause
        exit /b 1
    )
)

REM Check if model exists
if not exist "src\fraud_detection_model.pkl" (
    echo Error: Model not found at src\fraud_detection_model.pkl
    echo Please train the model first by running notebooks/02_model_training.ipynb
    pause
    exit /b 1
)

echo.
echo Starting FastAPI service on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

REM Change to project directory and run FastAPI
cd /d %~dp0
%PYTHON_CMD% -m uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8000 --reload

pause

