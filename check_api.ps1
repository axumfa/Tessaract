# Simplified API check script (no emoji, UTF-8 safe)

# Set UTF-8 encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Checking API status..." -ForegroundColor Cyan
Write-Host ""

# Check which port is in use
$port8000 = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue
$port8001 = Test-NetConnection -ComputerName localhost -Port 8001 -InformationLevel Quiet -WarningAction SilentlyContinue

$port = $null
if ($port8000) {
    $port = 8000
} elseif ($port8001) {
    $port = 8001
}

if ($port) {
    Write-Host "[OK] API is running on port $port" -ForegroundColor Green
    Write-Host ""
    
    try {
        Write-Host "Health Check:" -ForegroundColor Cyan
        $health = Invoke-RestMethod -Uri "http://localhost:$port/health" -TimeoutSec 3
        Write-Host "  Status: $($health.status)" -ForegroundColor White
        Write-Host "  Model Loaded: $($health.model_loaded)" -ForegroundColor White
        Write-Host "  Database Connected: $($health.database_connected)" -ForegroundColor White
        Write-Host ""
        Write-Host "Access URLs:" -ForegroundColor Cyan
        Write-Host "  API Docs: http://localhost:$port/docs" -ForegroundColor Yellow
        Write-Host "  Health: http://localhost:$port/health" -ForegroundColor Yellow
        Write-Host "  Predict: http://localhost:$port/predict" -ForegroundColor Yellow
    } catch {
        Write-Host "[WARNING] Could not get health status: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[ERROR] API is not running on ports 8000 or 8001" -ForegroundColor Red
    Write-Host ""
    Write-Host "To start the API, run:" -ForegroundColor Cyan
    Write-Host "  .\run.bat" -ForegroundColor Yellow
}

