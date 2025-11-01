# Quick Start Guide

## 🚀 Fastest Way to Run (Windows)

### Step 1: Install Dependencies

```powershell
# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### Step 2: Set Up Database (Optional)

If you want to use PostgreSQL for storing predictions:

1. Install PostgreSQL from https://www.postgresql.org/download/
2. Create a database:
   ```sql
   CREATE DATABASE fraud_detection;
   ```
3. Set environment variables (PowerShell):
   ```powershell
   $env:DB_HOST="localhost"
   $env:DB_NAME="fraud_detection"
   $env:DB_USER="postgres"
   $env:DB_PASSWORD="your_password"
   ```

**Note:** The API will work without PostgreSQL, but predictions won't be stored.

### Step 3: Start Redis (Optional but Recommended)

Redis is used for caching. You can run without it, but caching won't work.

1. Download Redis for Windows: https://github.com/microsoftarchive/redis/releases
2. Run `redis-server.exe`
3. Or install via WSL: `wsl sudo apt-get install redis-server`

### Step 4: Run the API

#### Option A: Simple Batch Script (Easiest)
```cmd
run.bat
```

#### Option B: PowerShell Script (Full Features)
```powershell
.\run.ps1
```

#### Option C: Manual Start
```powershell
# Activate venv
venv\Scripts\Activate.ps1

# Start API
uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8000 --reload
```

### Step 5: Test the API

Open your browser or use curl:

1. **Health Check:**
   ```
   http://localhost:8000/health
   ```

2. **API Documentation:**
   ```
   http://localhost:8000/docs
   ```

3. **Make a Prediction:**
   ```powershell
   # PowerShell
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

## ✅ What You Need Installed

### Required:
- ✅ Python 3.9+ 
- ✅ pip (comes with Python)

### Optional (but recommended):
- ⚠️ PostgreSQL (for data storage)
- ⚠️ Redis (for caching)
- ⚠️ Kafka (for streaming - only if using Kafka features)

## 🎯 Minimal Setup (Just API)

If you just want to test the API without databases:

```powershell
# 1. Install dependencies
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Run API
uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8000 --reload
```

The API will work, but:
- ❌ Predictions won't be cached (Redis)
- ❌ Predictions won't be stored (PostgreSQL)
- ✅ Predictions will still work!

## 🔧 Troubleshooting

### "Module not found"
```powershell
pip install -r requirements.txt
```

### "Port already in use"
Change the port:
```powershell
uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8001 --reload
```

### "Model not found"
Make sure these files exist in `src/`:
- `fraud_detection_model.pkl`
- `xgb_model.pkl`

### "Database connection failed"
The API will still work! It just won't store predictions. To fix:
1. Install PostgreSQL
2. Create database
3. Set environment variables

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check API documentation at `http://localhost:8000/docs` when running
- Explore the notebooks in `notebooks/` to understand model training

## 🆘 Need Help?

1. Check the full [README.md](README.md)
2. Verify all prerequisites are installed
3. Check the API health endpoint: `http://localhost:8000/health`

