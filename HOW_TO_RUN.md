# 🚀 How to Run the Fraud Detection System

## Quick Steps (3 minutes)

### Step 1: Open PowerShell in this folder
- Right-click in this folder → "Open in Terminal" or "Open PowerShell window here"

### Step 2: Activate Virtual Environment
```powershell
venv\Scripts\Activate.ps1
```

If you see `(venv)` at the start of your prompt, you're good! ✅

### Step 3: Start the API Server
```powershell
uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8000 --reload
```

Wait until you see:
```
✅  Fraud Detection API is running.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test It!
Open your browser and go to:
- **http://localhost:8000/docs** (Interactive API Documentation)
- **http://localhost:8000/health** (Health Check)

---

## 📋 Detailed Step-by-Step Guide

### Prerequisites Check

✅ **Python 3.9+ installed?**
```powershell
python --version
```
Should show Python 3.9 or higher.

✅ **Virtual environment exists?**
```powershell
dir venv
```
If not, create it:
```powershell
python -m venv venv
```

✅ **Dependencies installed?**
```powershell
pip list | findstr fastapi
```
If not installed, run:
```powershell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Method 1: Simple Batch File (Easiest)

Just double-click `run.bat` or run:
```cmd
run.bat
```

This will:
- ✅ Activate virtual environment
- ✅ Start the API on port 8000
- ✅ Show you the API documentation URL

### Method 2: PowerShell Script (Full Features)

```powershell
.\run.ps1
```

This will:
- ✅ Check and start Redis (if installed)
- ✅ Check for Kafka (optional)
- ✅ Start FastAPI
- ✅ Show all endpoints

**Note:** If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Method 3: Manual Start (Full Control)

```powershell
# 1. Activate virtual environment
venv\Scripts\Activate.ps1

# 2. Start FastAPI
uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧪 Testing the API

### Option 1: Use the Test Script
In a new PowerShell window (keep API running):
```powershell
.\test_api.ps1
```

### Option 2: Use the Browser
1. Go to: http://localhost:8000/docs
2. Click on `/predict`
3. Click "Try it out"
4. Enter test data:
```json
{
  "amount": 100.50,
  "hour": 14,
  "dayofweek": 3,
  "txns_last_24h": 5.0,
  "amount_last_24h": 500.0,
  "risk_score": 25.5
}
```
5. Click "Execute"

### Option 3: Use PowerShell
```powershell
$body = @{
    amount = 100.50
    hour = 14
    dayofweek = 3
    txns_last_24h = 5.0
    amount_last_24h = 500.0
    risk_score = 25.5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Body $body -ContentType "application/json"
```

---

## 🔧 Troubleshooting

### ❌ "Module not found"
```powershell
pip install -r requirements.txt
```

### ❌ "Port 8000 already in use"
Change the port:
```powershell
uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8001 --reload
```
Then use: http://localhost:8001/docs

### ❌ "Model not found"
Make sure these files exist in `src/` folder:
- `fraud_detection_model.pkl`
- `xgb_model.pkl`

### ❌ "Cannot activate venv"
If `Activate.ps1` doesn't work, try:
```powershell
venv\Scripts\activate
```

### ❌ "Database connection failed"
**This is OK!** The API will still work. You just won't store predictions.
To fix (optional):
1. Install PostgreSQL
2. Create database: `CREATE DATABASE fraud_detection;`
3. Set environment variables:
```powershell
$env:DB_HOST="localhost"
$env:DB_NAME="fraud_detection"
$env:DB_USER="postgres"
$env:DB_PASSWORD="your_password"
```

---

## 📊 Available Endpoints

Once running, you can access:

| Endpoint | URL | Description |
|----------|-----|-------------|
| **Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health** | http://localhost:8000/health | Check if API is running |
| **Predict** | http://localhost:8000/predict | Single transaction prediction |
| **Batch** | http://localhost:8000/predict/batch | Multiple transactions |
| **Stats** | http://localhost:8000/stats | Fraud statistics |
| **Transactions** | http://localhost:8000/transactions | Recent predictions |

---

## ✅ Success Checklist

- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API server running (see "Uvicorn running on...")
- [ ] Can access http://localhost:8000/docs in browser
- [ ] Health check returns `{"status": "healthy"}`

---

## 🎯 Quick Command Reference

```powershell
# Activate venv
venv\Scripts\Activate.ps1

# Install/Update dependencies
pip install -r requirements.txt

# Start API
uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8000 --reload

# Test API (in new terminal)
.\test_api.ps1

# Stop API
Press Ctrl+C in the terminal running uvicorn
```

---

## 🆘 Still Having Issues?

1. **Check Python version**: `python --version` (needs 3.9+)
2. **Reinstall dependencies**: `pip install -r requirements.txt --force-reinstall`
3. **Check if port is free**: `netstat -ano | findstr :8000`
4. **Try different port**: Change `--port 8000` to `--port 8001`

---

**🎉 You're all set! Open http://localhost:8000/docs to start using the API!**

