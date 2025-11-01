@echo off
REM Fix pydantic version compatibility issue

echo 🔧 Fixing pydantic compatibility issue...
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ❌ Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

echo.
echo 🔹 Upgrading pydantic to compatible version...
pip install --upgrade "pydantic>=1.10.12"
if errorlevel 1 (
    echo ❌ Failed to upgrade pydantic
    pause
    exit /b 1
)

echo.
echo ✅ Pydantic upgraded successfully!
echo.
echo You can now run: run.bat
pause

