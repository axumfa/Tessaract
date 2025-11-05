# 📍 Where Are The Results? - CSV Prediction Guide

## ✅ Fixed Issues

I've fixed the CSV parsing problem! The code now:
- ✅ Handles float values for `hour` and `dayofweek` (converts them to integers)
- ✅ Handles case-insensitive column names (`Amount` vs `amount`)
- ✅ Provides better error messages
- ✅ Shows how many rows were skipped

---

## 🔍 Where to Find Your Results

When you upload a CSV to `/predict/csv`, the results are returned as **JSON in the HTTP response**. Here's where to find them:

### Option 1: Swagger UI (Recommended - Easiest!)

1. **Open Swagger UI:** http://localhost:8000/docs
2. **Find the `/predict/csv` endpoint** (scroll down to find it)
3. **Click "Try it out"**
4. **Click "Choose File"** and select your CSV file
5. **Click "Execute"** (blue button)
6. **See the results!** They appear in two sections:

   **a) Response body** (scroll down in the Swagger UI):
   ```json
   {
     "predictions": [
       {
         "transaction_id": "...",
         "is_fraud": true/false,
         "confidence": 0.95,
         "timestamp": "2025-11-01T13:41:17.015000"
       },
       ...
     ],
     "summary": {
       "total_transactions": 10,
       "fraud_count": 2,
       "fraud_percentage": 20.0,
       "timestamp": "2025-11-01T13:41:17.015000"
     }
   }
   ```

   **b) Response Code:** Should show `200 OK` if successful

### Option 2: Using PowerShell / curl

If you're using PowerShell or curl, the JSON response is printed to the console:

```powershell
# Using PowerShell
$response = Invoke-RestMethod -Uri "http://localhost:8000/predict/csv" `
    -Method Post `
    -InFile "your_file.csv" `
    -ContentType "multipart/form-data"

# Print results
$response | ConvertTo-Json -Depth 10

# Or view summary
$response.summary

# View predictions
$response.predictions
```

```bash
# Using curl
curl -X POST "http://localhost:8000/predict/csv" \
  -F "file=@your_file.csv"
```

The JSON response will be displayed in your terminal.

### Option 3: Using Python

```python
import requests

# Upload CSV
with open('your_file.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict/csv',
        files={'file': f}
    )

# Get results as JSON
results = response.json()

# Print summary
print(f"Total transactions: {results['summary']['total_transactions']}")
print(f"Fraud cases: {results['summary']['fraud_count']}")
print(f"Fraud percentage: {results['summary']['fraud_percentage']}%")

# Print all predictions
for pred in results['predictions']:
    print(f"Transaction {pred['transaction_id']}: {'FRAUD' if pred['is_fraud'] else 'LEGITIMATE'} (confidence: {pred['confidence']:.2f})")
```

### Option 4: Using Browser DevTools (Advanced)

If you're using a web interface:

1. Open **Developer Tools** (F12)
2. Go to **Network** tab
3. Upload your CSV file
4. Find the request to `/predict/csv`
5. Click on it
6. View the **Response** tab to see the JSON results

---

## 📊 Understanding the Results

The response contains two main parts:

### 1. `predictions` Array
Each prediction has:
- **`transaction_id`**: Unique ID for the transaction
- **`is_fraud`**: `true` if fraudulent, `false` if legitimate
- **`confidence`**: Probability score (0.0 to 1.0) - higher is more confident
- **`timestamp`**: When the prediction was made

### 2. `summary` Object
Overall statistics:
- **`total_transactions`**: Total number of transactions processed
- **`fraud_count`**: Number of transactions flagged as fraud
- **`fraud_percentage`**: Percentage of transactions that are fraudulent
- **`timestamp`**: When the batch was processed

---

## 🐛 Troubleshooting

### "No valid transactions found in CSV"
- Check your CSV format
- Make sure columns are: `amount`, `hour`, `dayofweek`, `txns_last_24h`, `amount_last_24h`, `risk_score`
- Check the terminal logs for specific row errors

### Results not showing in Swagger UI?
1. Scroll down in the Swagger UI response section
2. Make sure you clicked "Execute"
3. Check for errors in the Response Code section
4. Look at the terminal/console for error messages

### Some rows are being skipped?
- Check the terminal logs - it will show which rows and why
- Common issues:
  - Missing required columns
  - Invalid data types
  - Empty values in required fields

---

## 📝 Example Response

Here's what a successful response looks like:

```json
{
  "predictions": [
    {
      "transaction_id": "168320.0",
      "is_fraud": false,
      "confidence": 0.98,
      "timestamp": "2025-11-01T13:41:17.015000"
    },
    {
      "transaction_id": "139915.0",
      "is_fraud": false,
      "confidence": 0.92,
      "timestamp": "2025-11-01T13:41:17.020000"
    },
    {
      "transaction_id": "123903.0",
      "is_fraud": true,
      "confidence": 0.87,
      "timestamp": "2025-11-01T13:41:17.025000"
    }
  ],
  "summary": {
    "total_transactions": 3,
    "fraud_count": 1,
    "fraud_percentage": 33.33,
    "timestamp": "2025-11-01T13:41:17.030000"
  }
}
```

---

## ✅ Quick Checklist

After uploading your CSV:
- [ ] Response code is `200 OK`
- [ ] JSON response appears in Swagger UI / terminal
- [ ] `summary.total_transactions` matches your CSV row count (minus headers)
- [ ] `predictions` array has the same number of items as valid rows
- [ ] Check terminal logs if rows were skipped

---

**Remember:** The results are in the HTTP response body as JSON. If you're using Swagger UI, scroll down after clicking "Execute" to see the response!

