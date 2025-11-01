# Simple test script to verify the API is working

Write-Host "🧪 Testing Fraud Detection API..." -ForegroundColor Cyan
Write-Host ""

$API_URL = "http://localhost:8000"

# Test 1: Health Check
Write-Host "1️⃣  Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$API_URL/health" -Method Get
    Write-Host "   ✅ Health Check Passed" -ForegroundColor Green
    Write-Host "   Model Loaded: $($health.model_loaded)" -ForegroundColor White
    Write-Host "   Database Connected: $($health.database_connected)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "   ❌ Health Check Failed" -ForegroundColor Red
    Write-Host "   Make sure the API is running on port 8000" -ForegroundColor Yellow
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Home Endpoint
Write-Host "2️⃣  Testing Home Endpoint..." -ForegroundColor Yellow
try {
    $home = Invoke-RestMethod -Uri "$API_URL/" -Method Get
    Write-Host "   ✅ Home Endpoint Working" -ForegroundColor Green
    Write-Host "   Message: $($home.message)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "   ❌ Home Endpoint Failed" -ForegroundColor Red
}

# Test 3: Single Prediction
Write-Host "3️⃣  Testing Single Prediction..." -ForegroundColor Yellow
try {
    $transaction = @{
        amount = 100.50
        hour = 14
        dayofweek = 3
        txns_last_24h = 5.0
        amount_last_24h = 500.0
        risk_score = 25.5
    } | ConvertTo-Json

    $prediction = Invoke-RestMethod -Uri "$API_URL/predict" -Method Post -Body $transaction -ContentType "application/json"
    Write-Host "   ✅ Prediction Successful" -ForegroundColor Green
    Write-Host "   Transaction ID: $($prediction.transaction_id)" -ForegroundColor White
    Write-Host "   Is Fraud: $($prediction.is_fraud)" -ForegroundColor White
    Write-Host "   Confidence: $([math]::Round($prediction.confidence * 100, 2))%" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "   ❌ Prediction Failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Batch Prediction
Write-Host "4️⃣  Testing Batch Prediction..." -ForegroundColor Yellow
try {
    $batch = @{
        transactions = @(
            @{
                amount = 50.00
                hour = 10
                dayofweek = 1
                txns_last_24h = 3.0
                amount_last_24h = 150.0
                risk_score = 15.0
            },
            @{
                amount = 5000.00
                hour = 2
                dayofweek = 0
                txns_last_24h = 1.0
                amount_last_24h = 5000.0
                risk_score = 10000.0
            }
        )
    } | ConvertTo-Json

    $batchPred = Invoke-RestMethod -Uri "$API_URL/predict/batch" -Method Post -Body $batch -ContentType "application/json"
    Write-Host "   ✅ Batch Prediction Successful" -ForegroundColor Green
    Write-Host "   Total Transactions: $($batchPred.summary.total_transactions)" -ForegroundColor White
    Write-Host "   Fraud Count: $($batchPred.summary.fraud_count)" -ForegroundColor White
    Write-Host "   Fraud Percentage: $([math]::Round($batchPred.summary.fraud_percentage, 2))%" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "   ❌ Batch Prediction Failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Stats Endpoint (if database is connected)
Write-Host "5️⃣  Testing Stats Endpoint..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$API_URL/stats" -Method Get
    Write-Host "   ✅ Stats Retrieved" -ForegroundColor Green
    Write-Host "   Total Transactions: $($stats.total_transactions)" -ForegroundColor White
    Write-Host "   Fraud Count: $($stats.fraud_count)" -ForegroundColor White
    Write-Host "   Fraud Percentage: $([math]::Round($stats.fraud_percentage, 2))%" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "   ⚠️  Stats Endpoint Not Available (Database may not be connected)" -ForegroundColor Yellow
    Write-Host "   This is OK if you're not using PostgreSQL" -ForegroundColor White
    Write-Host ""
}

Write-Host "✅ All Tests Completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 API Documentation: $API_URL/docs" -ForegroundColor Cyan

