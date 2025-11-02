# PowerShell script to run comprehensive tests
# Automatically detects API port and runs all tests

# Set execution policy for this session (if needed)
$ErrorActionPreference = "Continue"

$separator = "=" * 60
Write-Host $separator
Write-Host "Fraud Detection API - Test Runner"
Write-Host "=" * 60
Write-Host ""

# Check which port API is running on
$port8000 = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue
$port8001 = Test-NetConnection -ComputerName localhost -Port 8001 -InformationLevel Quiet -WarningAction SilentlyContinue

$apiPort = $null
if ($port8000) {
    $apiPort = 8000
    Write-Host "[OK] API detected on port 8000" -ForegroundColor Green
} elseif ($port8001) {
    $apiPort = 8001
    Write-Host "[OK] API detected on port 8001" -ForegroundColor Green
} else {
    Write-Host "[ERROR] API is not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start the API first:" -ForegroundColor Yellow
    Write-Host "  .\run.bat" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or in a new terminal window:" -ForegroundColor Yellow
    Write-Host "  cd D:\Tesseract\Tessaract" -ForegroundColor Cyan
    Write-Host "  .\run.bat" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "Running comprehensive tests..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1" | Out-Null
}

# Run tests
$apiUrl = "http://localhost:$apiPort"
& "venv\Scripts\python.exe" test_everything.py $apiUrl

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "[SUCCESS] All tests passed!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Some tests failed or had warnings" -ForegroundColor Yellow
}

exit $exitCode

