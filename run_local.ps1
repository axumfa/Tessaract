# PowerShell script to run the Fraud Detection API locally

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Fraud Detection API - Local Runner (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Error: Virtual environment not found at venv\Scripts\Activate.ps1" -ForegroundColor Red
    Write-Host "Please create one with: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if model exists
if (-not (Test-Path "src\fraud_detection_model.pkl")) {
    Write-Host "Error: Model not found at src\fraud_detection_model.pkl" -ForegroundColor Red
    Write-Host "Please train the model first by running notebooks/02_model_training.ipynb" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting FastAPI service on http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start FastAPI server
python -m uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8000 --reload

