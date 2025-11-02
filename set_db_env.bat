@echo off
REM Quick script to set database environment variables and save to .env file

echo ============================================================
echo PostgreSQL Database Configuration
echo ============================================================
echo.

set DB_HOST=localhost
set DB_NAME=fraud_detection
set DB_USER=postgres

echo Enter PostgreSQL password for user 'postgres':
set /p DB_PASSWORD=

echo.
echo Setting environment variables for this session...
set DB_HOST=%DB_HOST%
set DB_NAME=%DB_NAME%
set DB_USER=%DB_USER%
set DB_PASSWORD=%DB_PASSWORD%

echo.
echo Saving to .env file...
(
echo DB_HOST=%DB_HOST%
echo DB_NAME=%DB_NAME%
echo DB_USER=%DB_USER%
echo DB_PASSWORD=%DB_PASSWORD%
) > .env

echo [OK] Configuration saved to .env file
echo.
echo Environment variables configured:
echo   DB_HOST=%DB_HOST%
echo   DB_NAME=%DB_NAME%
echo   DB_USER=%DB_USER%
echo   DB_PASSWORD=****
echo.
echo ============================================================
echo IMPORTANT: Restart the API to use these settings!
echo ============================================================
echo.
echo To restart API:
echo   1. Stop current API (Ctrl+C in API terminal)
echo   2. Run: run.bat
echo.
echo Or if API is not running, just run: run.bat
echo.
pause

