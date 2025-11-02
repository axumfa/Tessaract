# PowerShell script to setup database connection
# Helps configure PostgreSQL connection for the API

Write-Host "PostgreSQL Database Setup" -ForegroundColor Cyan
Write-Host "=" * 50
Write-Host ""

# Check if PostgreSQL is installed
try {
    $psql = Get-Command psql -ErrorAction Stop
    Write-Host "[OK] PostgreSQL client found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] PostgreSQL is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install PostgreSQL from:" -ForegroundColor Yellow
    Write-Host "  https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or see INSTALL_POSTGRESQL.md for detailed instructions"
    exit 1
}

Write-Host ""
Write-Host "Enter database connection details:" -ForegroundColor Cyan
Write-Host ""

# Get connection details
$dbHost = Read-Host "Database Host [localhost]"
if ([string]::IsNullOrWhiteSpace($dbHost)) { $dbHost = "localhost" }

$dbPort = Read-Host "Database Port [5432]"
if ([string]::IsNullOrWhiteSpace($dbPort)) { $dbPort = "5432" }

$dbName = Read-Host "Database Name [fraud_detection]"
if ([string]::IsNullOrWhiteSpace($dbName)) { $dbName = "fraud_detection" }

$dbUser = Read-Host "Database User [postgres]"
if ([string]::IsNullOrWhiteSpace($dbUser)) { $dbUser = "postgres" }

$securePassword = Read-Host "Database Password" -AsSecureString
$dbPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
)

Write-Host ""
Write-Host "Testing connection..." -ForegroundColor Cyan

# Test connection
$env:PGPASSWORD = $dbPassword
try {
    $result = psql -h $dbHost -p $dbPort -U $dbUser -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Connection successful!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Connection failed" -ForegroundColor Red
        Write-Host $result
        exit 1
    }
} catch {
    Write-Host "[ERROR] Connection test failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check if database exists
Write-Host ""
Write-Host "Checking database..." -ForegroundColor Cyan
$dbExists = psql -h $dbHost -p $dbPort -U $dbUser -d postgres -lqt | Select-String -Pattern "\b$dbName\b"
if ($dbExists) {
    Write-Host "[OK] Database '$dbName' exists" -ForegroundColor Green
} else {
    Write-Host "[INFO] Database '$dbName' does not exist. Creating..." -ForegroundColor Yellow
    $createResult = psql -h $dbHost -p $dbPort -U $dbUser -d postgres -c "CREATE DATABASE $dbName;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Database created successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to create database" -ForegroundColor Red
        Write-Host $createResult
        exit 1
    }
}

Write-Host ""
Write-Host "Setting environment variables..." -ForegroundColor Cyan

# Set environment variables for current session
$env:DB_HOST = $dbHost
$env:DB_PORT = $dbPort
$env:DB_NAME = $dbName
$env:DB_USER = $dbUser
$env:DB_PASSWORD = $dbPassword

Write-Host "  DB_HOST = $dbHost"
Write-Host "  DB_PORT = $dbPort"
Write-Host "  DB_NAME = $dbName"
Write-Host "  DB_USER = $dbUser"
Write-Host "  DB_PASSWORD = [hidden]"

# Save to .env file
Write-Host ""
Write-Host "Saving to .env file..." -ForegroundColor Cyan
@"
DB_HOST=$dbHost
DB_PORT=$dbPort
DB_NAME=$dbName
DB_USER=$dbUser
DB_PASSWORD=$dbPassword
"@ | Out-File -FilePath ".env" -Encoding utf8 -NoNewline

Write-Host "[OK] Saved to .env file" -ForegroundColor Green

# Create PowerShell script to set env vars
Write-Host ""
Write-Host "Creating set_db_env.ps1..." -ForegroundColor Cyan
@"
# Auto-generated script to set database environment variables
`$env:DB_HOST = "$dbHost"
`$env:DB_PORT = "$dbPort"
`$env:DB_NAME = "$dbName"
`$env:DB_USER = "$dbUser"
`$env:DB_PASSWORD = "$dbPassword"
"@ | Out-File -FilePath "set_db_env.ps1" -Encoding utf8

Write-Host "[OK] Created set_db_env.ps1" -ForegroundColor Green

Write-Host ""
Write-Host "=" * 50
Write-Host "[SUCCESS] Database connection configured!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart the API: .\run.bat" -ForegroundColor Yellow
Write-Host "  2. Run tests again: .\run_tests.bat" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or use the environment variables in current session:" -ForegroundColor Cyan
Write-Host "  Variables are already set for this PowerShell session" -ForegroundColor Yellow

