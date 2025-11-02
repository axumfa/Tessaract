@echo off
REM Batch script to run tests (works without PowerShell execution policy)

echo ============================================================
echo Fraud Detection API - Test Runner
echo ============================================================
echo.

REM Check which port API is running on
python -c "import socket; s = socket.socket(); result = s.connect_ex(('localhost', 8000)); s.close(); exit(0 if result == 0 else 1)" 2>nul
if %errorlevel% == 0 (
    set API_PORT=8000
    echo [OK] API detected on port 8000
    goto :run_tests
)

python -c "import socket; s = socket.socket(); result = s.connect_ex(('localhost', 8001)); s.close(); exit(0 if result == 0 else 1)" 2>nul
if %errorlevel% == 0 (
    set API_PORT=8001
    echo [OK] API detected on port 8001
    goto :run_tests
)

echo [ERROR] API is not running!
echo.
echo Please start the API first:
echo   run.bat
echo.
pause
exit /b 1

:run_tests
echo.
echo Running comprehensive tests...
echo.

REM Activate virtual environment and run tests
call venv\Scripts\activate.bat
python test_everything.py http://localhost:%API_PORT%

if %errorlevel% == 0 (
    echo.
    echo [SUCCESS] All tests passed!
) else (
    echo.
    echo [WARNING] Some tests failed or had warnings
)

pause

