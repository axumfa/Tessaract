# 🎯 Application Explanation - Fraud Detection System

## 📋 What This Application Is

This is a **Fraud Detection System** built with FastAPI that uses machine learning to predict whether financial transactions are fraudulent or not. The system processes credit card transactions and flags suspicious activity.

**Main Features:**
- REST API with FastAPI (runs on `http://localhost:8000`)
- Machine learning model for fraud prediction
- CSV batch processing
- Redis caching for faster responses
- PostgreSQL database for storing predictions
- Kafka integration for real-time streaming (optional)

---

## 🚀 How The Application Runs

### Architecture Overview

```
FastAPI Service (Port 8000)
├── Machine Learning Model (fraud_detection_model.pkl)
├── Redis Cache (optional - for faster responses)
├── PostgreSQL Database (optional - for storing predictions)
└── Multiple API Endpoints
```

### Running the Application

1. **Start the API server:**
   ```powershell
   # Activate virtual environment
   .\venv\Scripts\Activate.ps1
   
   # Run the server
   uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the API:**
   - **API Documentation:** http://localhost:8000/docs (Swagger UI)
   - **Health Check:** http://localhost:8000/health
   - **Home:** http://localhost:8000/

### Required Services (Optional)

- **Redis:** For caching predictions (speeds up repeat requests)
- **PostgreSQL:** For storing prediction history and statistics
- **Kafka:** For real-time streaming (advanced feature)

The application works WITHOUT these services too, but with reduced functionality.

---

## 📊 What Happens When You Upload a CSV to `/predict/csv`

Here's the **step-by-step process** when you upload a CSV file:

### Step 1: File Upload
- You upload a CSV file through the API endpoint `/predict/csv`
- The file is received as binary data

### Step 2: CSV Parsing
The system reads your CSV and expects these columns:
- `amount` - Transaction amount (float)
- `hour` - Hour of day (0-23, integer)
- `dayofweek` - Day of week (0-6, integer)
- `txns_last_24h` - Number of transactions in last 24 hours (float)
- `amount_last_24h` - Total amount in last 24 hours (float)
- `risk_score` - Risk score (float)
- `transaction_id` - Optional unique ID (string)

**Example CSV format:**
```csv
amount,hour,dayofweek,txns_last_24h,amount_last_24h,risk_score,transaction_id
100.50,14,3,5.0,500.0,25.5,txn-001
2000.00,2,0,1.0,2000.0,4000.0,txn-002
```

### Step 3: Data Validation
- Each row is converted to a `Transaction` object
- Invalid rows are skipped (with warning logged)
- If no `transaction_id` is provided, a UUID is generated automatically

### Step 4: Batch Processing
For each transaction in the CSV:

#### 4a. Check Cache (Redis)
- If Redis is available, checks if this transaction was already processed
- If found in cache, returns cached result (much faster!)
- Cache expires after 3600 seconds (1 hour)

#### 4b. Prepare Data for Model
- Converts transaction data to a pandas DataFrame
- Removes `transaction_id` (not used by model)
- Renames `amount` to `Amount` (model expects capitalized)

#### 4c. Fraud Prediction
- Uses the trained machine learning model (`fraud_detection_model.pkl`)
- Model analyzes 6 features: `Amount`, `hour`, `dayofweek`, `txns_last_24h`, `amount_last_24h`, `risk_score`
- Returns:
  - **is_fraud**: `True` if fraudulent, `False` if legitimate
  - **confidence**: Probability score (0.0 to 1.0)

#### 4d. Cache Result
- Stores prediction in Redis (if available)
- Saves for future fast retrieval

#### 4e. Log to Database
- Saves prediction to PostgreSQL `predictions` table (if available)
- Stores:
  - Transaction ID
  - Transaction data (as JSON)
  - Prediction result
  - Confidence score
  - Timestamp

### Step 5: Generate Summary
After processing all transactions, the system creates a summary:
- **Total transactions** processed
- **Number of fraud cases** detected
- **Fraud percentage**
- **Timestamp** of processing

### Step 6: Return Results
Returns a JSON response with:
```json
{
  "predictions": [
    {
      "transaction_id": "txn-001",
      "is_fraud": false,
      "confidence": 0.95,
      "timestamp": "2024-01-15T14:30:00"
    },
    {
      "transaction_id": "txn-002",
      "is_fraud": true,
      "confidence": 0.87,
      "timestamp": "2024-01-15T14:30:00"
    }
  ],
  "summary": {
    "total_transactions": 2,
    "fraud_count": 1,
    "fraud_percentage": 50.0,
    "timestamp": "2024-01-15T14:30:00"
  }
}
```

---

## 🔍 Complete Flow Diagram

```
CSV Upload
    ↓
Read & Parse CSV
    ↓
For Each Transaction:
    ├─→ Check Redis Cache
    │   ├─→ Found? → Return Cached Result
    │   └─→ Not Found? → Continue
    │
    ├─→ Prepare DataFrame
    │   ├─→ Remove transaction_id
    │   └─→ Rename amount → Amount
    │
    ├─→ Run ML Model Prediction
    │   ├─→ model.predict() → is_fraud (True/False)
    │   └─→ model.predict_proba() → confidence (0.0-1.0)
    │
    ├─→ Cache Result in Redis (if available)
    │
    └─→ Save to PostgreSQL (if available)
        └─→ Store: transaction_id, data, prediction, confidence, timestamp
    ↓
Generate Summary Statistics
    ↓
Return JSON Response with All Predictions + Summary
```

---

## 🎯 Key Endpoints Explained

### 1. `/predict/csv` (POST)
**What it does:** Upload CSV file for batch fraud detection
- Accepts CSV file upload
- Processes all rows
- Returns predictions + summary

### 2. `/predict` (POST)
**What it does:** Predict fraud for a single transaction
- Takes JSON with transaction details
- Returns single prediction

### 3. `/predict/batch` (POST)
**What it does:** Predict fraud for multiple transactions
- Takes JSON array of transactions
- Returns predictions for all

### 4. `/transactions` (GET)
**What it does:** View recent predictions from database
- Returns last N transactions (default: 100)
- Shows prediction history

### 5. `/stats` (GET)
**What it does:** Get fraud statistics dashboard
- Total transactions
- Fraud count & percentage
- Hourly fraud distribution
- Daily trends (last 7 days)

### 6. `/health` (GET)
**What it does:** Check system health
- Returns: model loaded status, database connection status

---

## 📈 Model Details

### Model Type
- **Algorithm:** LightGBM Classifier (from `fraud_detection_model.pkl`)
- **Training:** Trained on credit card transaction data
- **Performance:** High precision and recall (as shown in notebooks)

### Features Used
1. **Amount** - Transaction amount
2. **hour** - Hour of day (0-23)
3. **dayofweek** - Day of week (0-6, Monday=0)
4. **txns_last_24h** - Count of transactions in last 24 hours
5. **amount_last_24h** - Total amount in last 24 hours
6. **risk_score** - Calculated risk score

### Output
- **Binary Classification:** Fraud (True) or Legitimate (False)
- **Confidence Score:** Probability from 0.0 to 1.0

---

## 🔧 Dependencies & Services

### Required
- ✅ **Python 3.11+**
- ✅ **FastAPI** - Web framework
- ✅ **Machine Learning Model** - `src/fraud_detection_model.pkl`

### Optional (App works without these)
- ⚠️ **PostgreSQL** - For storing prediction history
- ⚠️ **Redis** - For caching (speeds up repeated requests)
- ⚠️ **Kafka** - For real-time streaming

---

## 🐛 Troubleshooting

### CSV Upload Not Working?

1. **Check CSV format:**
   - Must have columns: `amount`, `hour`, `dayofweek`, `txns_last_24h`, `amount_last_24h`, `risk_score`
   - Optional: `transaction_id`

2. **Check API logs:**
   - Look for error messages in terminal
   - Invalid rows are skipped with warnings

3. **Model not loaded:**
   - Check if `src/fraud_detection_model.pkl` exists
   - Check `/health` endpoint

### Database/Redis Errors?

- These are **optional services**
- The API works fine without them
- Predictions just won't be cached or stored

---

## 📝 Example CSV File

Save this as `test_transactions.csv`:

```csv
amount,hour,dayofweek,txns_last_24h,amount_last_24h,risk_score,transaction_id
100.50,14,3,5.0,500.0,25.5,txn-001
2000.00,2,0,1.0,2000.0,4000.0,txn-002
50.25,10,1,3.0,150.75,10.0,txn-003
5000.00,23,6,10.0,15000.0,50000.0,txn-004
```

Then test via Swagger UI at `http://localhost:8000/docs`:
1. Find `/predict/csv` endpoint
2. Click "Try it out"
3. Upload your CSV file
4. Click "Execute"
5. See results!

---

## ✅ Summary

**What the `/predict/csv` endpoint does:**
1. ✅ Reads your CSV file
2. ✅ Validates each row
3. ✅ Checks cache for existing predictions
4. ✅ Runs ML model to predict fraud for each transaction
5. ✅ Caches results (if Redis available)
6. ✅ Saves to database (if PostgreSQL available)
7. ✅ Returns predictions + summary statistics

The system is designed to handle batch processing efficiently and provides detailed fraud detection results for all transactions in your CSV file!

