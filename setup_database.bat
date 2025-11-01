@echo off
REM Script to help setup PostgreSQL database for Fraud Detection API

echo 🐘 PostgreSQL Database Setup for Fraud Detection API
echo.

REM Check if psql is available
where psql >nul 2>&1
if errorlevel 1 (
    echo ❌ PostgreSQL is not installed or not in PATH!
    echo.
    echo Please:
    echo 1. Install PostgreSQL from: https://www.postgresql.org/download/windows/
    echo 2. Add PostgreSQL bin folder to PATH:
    echo    C:\Program Files\PostgreSQL\15\bin
    echo 3. Restart terminal and run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ PostgreSQL found!
echo.

REM Get database credentials
echo Enter PostgreSQL credentials:
echo.

set /p DB_HOST="Database Host [localhost]: "
if "%DB_HOST%"=="" set DB_HOST=localhost

set /p DB_NAME="Database Name [fraud_detection]: "
if "%DB_NAME%"=="" set DB_NAME=fraud_detection

set /p DB_USER="Database User [postgres]: "
if "%DB_USER%"=="" set DB_USER=postgres

set /p DB_PASSWORD="Database Password: "
if "%DB_PASSWORD%"=="" (
    echo ❌ Password is required!
    pause
    exit /b 1
)

echo.
echo 🔹 Creating database %DB_NAME%...
echo.

REM Set password for psql
set PGPASSWORD=%DB_PASSWORD%

REM Check if database exists
psql -h %DB_HOST% -U %DB_USER% -lqt | findstr /C:"%DB_NAME%" >nul
if %errorlevel% == 0 (
    echo ⚠️  Database %DB_NAME% already exists!
    set /p CREATE_DB="Do you want to drop and recreate it? (y/N): "
    if /i "%CREATE_DB%"=="y" (
        echo 🔹 Dropping existing database...
        psql -h %DB_HOST% -U %DB_USER% -d postgres -c "DROP DATABASE IF EXISTS %DB_NAME%;"
    ) else (
        echo ✅ Using existing database.
        goto :set_env
    )
)

REM Create database
psql -h %DB_HOST% -U %DB_USER% -d postgres -c "CREATE DATABASE %DB_NAME%;"
if errorlevel 1 (
    echo ❌ Failed to create database!
    echo Please check your credentials and try again.
    pause
    exit /b 1
)

echo ✅ Database %DB_NAME% created successfully!
echo.

:set_env
echo 🔹 Setting environment variables...
echo.

echo DB_HOST=%DB_HOST%
echo DB_NAME=%DB_NAME%
echo DB_USER=%DB_USER%
echo DB_PASSWORD=***

REM Save to .env file
echo DB_HOST=%DB_HOST% > .env
echo DB_NAME=%DB_NAME% >> .env
echo DB_USER=%DB_USER% >> .env
echo DB_PASSWORD=%DB_PASSWORD% >> .env

echo.
echo ✅ Environment variables saved to .env file
echo.

REM Note: In batch files, you can't set environment variables for parent shell
REM So we'll create a PowerShell script to set them
echo # PowerShell script to set environment variables > set_db_env.ps1
echo $env:DB_HOST="%DB_HOST%" >> set_db_env.ps1
echo $env:DB_NAME="%DB_NAME%" >> set_db_env.ps1
echo $env:DB_USER="%DB_USER%" >> set_db_env.ps1
echo $env:DB_PASSWORD="%DB_PASSWORD%" >> set_db_env.ps1

echo.
echo ✅ Setup complete!
echo.
echo To use the database with your API:
echo 1. Run: .\set_db_env.ps1
echo 2. Then run: .\run.bat
echo.
echo Or manually set environment variables in PowerShell:
echo $env:DB_HOST="%DB_HOST%"
echo $env:DB_NAME="%DB_NAME%"
echo $env:DB_USER="%DB_USER%"
echo $env:DB_PASSWORD="%DB_PASSWORD%"
echo.
pause


