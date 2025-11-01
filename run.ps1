# PowerShell script to start Fraud Detection System on Windows

Write-Host "🚀 Starting Fraud Detection System..." -ForegroundColor Green

# Set port variables
$FASTAPI_PORT = 8000
$KAFKA_PORT = 9092
$ZOOKEEPER_PORT = 2181
$REDIS_PORT = 6379

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
        return $connection.TcpTestSucceeded
    } catch {
        return $false
    }
}

# Function to kill a process using a port
function Stop-ProcessOnPort {
    param([int]$Port)
    try {
        $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
                   Select-Object -ExpandProperty OwningProcess -First 1
        if ($process) {
            Write-Host "🛑 Killing process $process using port $Port..." -ForegroundColor Yellow
            Stop-Process -Id $process -Force
            Start-Sleep -Seconds 2
        }
    } catch {
        # Port not in use or no process found
    }
}

# Function to wait for a service to start
function Wait-ForService {
    param([int]$Port, [string]$Name)
    Write-Host "⏳ Waiting for $Name to start on port $Port..." -ForegroundColor Cyan
    $timeout = 60
    $elapsed = 0
    while (-not (Test-Port -Port $Port)) {
        if ($elapsed -ge $timeout) {
            Write-Host "❌ Timeout waiting for $Name" -ForegroundColor Red
            return $false
        }
        Start-Sleep -Seconds 2
        $elapsed += 2
    }
    Write-Host "✅ $Name is running on port $Port." -ForegroundColor Green
    return $true
}

# Activate Virtual Environment
Write-Host "🔹 Activating virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
}

# Check if dependencies are installed
Write-Host "🔹 Checking dependencies..." -ForegroundColor Cyan
try {
    python -c "import fastapi, redis, kafka" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
        pip install -r requirements.txt
    }
} catch {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

# Start Redis
Write-Host "🔹 Checking Redis..." -ForegroundColor Cyan
$redisRunning = Get-Process -Name redis-server -ErrorAction SilentlyContinue
if ($redisRunning) {
    Write-Host "✅ Redis is already running." -ForegroundColor Green
} else {
    Write-Host "🔹 Starting Redis..." -ForegroundColor Cyan
    $redisPath = Get-Command redis-server -ErrorAction SilentlyContinue
    if ($redisPath) {
        Start-Process -FilePath "redis-server" -WindowStyle Hidden
        Wait-ForService -Port $REDIS_PORT -Name "Redis"
    } else {
        Write-Host "⚠️  Redis not found in PATH. Please install Redis or start it manually." -ForegroundColor Yellow
        Write-Host "   You can download Redis from: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Yellow
    }
}

# Start Zookeeper (optional - only if Kafka is needed)
Write-Host "🔹 Checking Zookeeper..." -ForegroundColor Cyan
if (Test-Port -Port $ZOOKEEPER_PORT) {
    Write-Host "✅ Zookeeper is already running." -ForegroundColor Green
} else {
    Write-Host "⚠️  Zookeeper not running. Kafka features will not work." -ForegroundColor Yellow
    Write-Host "   To start Zookeeper, navigate to Kafka directory and run:" -ForegroundColor Yellow
    Write-Host "   bin\windows\zookeeper-server-start.bat config\zookeeper.properties" -ForegroundColor Yellow
}

# Start Kafka (optional - only if Kafka is needed)
Write-Host "🔹 Checking Kafka..." -ForegroundColor Cyan
if (Test-Port -Port $KAFKA_PORT) {
    Write-Host "✅ Kafka is already running." -ForegroundColor Green
} else {
    Write-Host "⚠️  Kafka not running. Kafka features will not work." -ForegroundColor Yellow
    Write-Host "   To start Kafka, navigate to Kafka directory and run:" -ForegroundColor Yellow
    Write-Host "   bin\windows\kafka-server-start.bat config\server.properties" -ForegroundColor Yellow
}

# Kill any existing FastAPI process using the port
Stop-ProcessOnPort -Port $FASTAPI_PORT

# Start FastAPI
if (-not (Test-Port -Port $FASTAPI_PORT)) {
    Write-Host "🔹 Starting FastAPI API on port $FASTAPI_PORT..." -ForegroundColor Cyan
    
    # Start FastAPI in background
    $fastapiJob = Start-Job -ScriptBlock {
        param($port)
        Set-Location $using:PWD
        & "venv\Scripts\python.exe" -m uvicorn src.fastapi_service:app --host 0.0.0.0 --port $port
    } -ArgumentList $FASTAPI_PORT
    
    Wait-ForService -Port $FASTAPI_PORT -Name "FastAPI"
    
    if (Test-Port -Port $FASTAPI_PORT) {
        Write-Host "✅ FastAPI started successfully!" -ForegroundColor Green
        Write-Host "📖 API Documentation: http://localhost:$FASTAPI_PORT/docs" -ForegroundColor Cyan
        Write-Host "❤️  Health Check: http://localhost:$FASTAPI_PORT/health" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Failed to start FastAPI" -ForegroundColor Red
    }
} else {
    Write-Host "✅ FastAPI is already running on port $FASTAPI_PORT." -ForegroundColor Green
}

# Start Kafka Producer (if Kafka is running)
if (Test-Port -Port $KAFKA_PORT) {
    Write-Host "🔹 Starting Kafka Producer..." -ForegroundColor Cyan
    Start-Process -FilePath "python" -ArgumentList "src/kafka_producer.py" -WindowStyle Hidden
    
    Write-Host "🔹 Starting Kafka Consumer..." -ForegroundColor Cyan
    Start-Process -FilePath "python" -ArgumentList "src/kafka_consumer.py" -WindowStyle Hidden
}

Write-Host ""
Write-Host "✅ Fraud Detection System is running!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Available Endpoints:" -ForegroundColor Cyan
Write-Host "   • API Docs: http://localhost:$FASTAPI_PORT/docs" -ForegroundColor White
Write-Host "   • Health: http://localhost:$FASTAPI_PORT/health" -ForegroundColor White
Write-Host "   • Predict: http://localhost:$FASTAPI_PORT/predict" -ForegroundColor White
Write-Host "   • Stats: http://localhost:$FASTAPI_PORT/stats" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services..." -ForegroundColor Yellow

# Keep script alive and handle cleanup
try {
    while ($true) {
        Start-Sleep -Seconds 5
        # Check if FastAPI is still running
        if (-not (Test-Port -Port $FASTAPI_PORT)) {
            Write-Host "⚠️  FastAPI stopped unexpectedly" -ForegroundColor Yellow
            break
        }
    }
} finally {
    Write-Host ""
    Write-Host "🛑 Stopping all services..." -ForegroundColor Yellow
    
    # Stop FastAPI job if it exists
    if ($fastapiJob) {
        Stop-Job -Job $fastapiJob -ErrorAction SilentlyContinue
        Remove-Job -Job $fastapiJob -ErrorAction SilentlyContinue
    }
    
    # Kill processes on ports
    Stop-ProcessOnPort -Port $FASTAPI_PORT
    
    Write-Host "✅ Services stopped." -ForegroundColor Green
}

