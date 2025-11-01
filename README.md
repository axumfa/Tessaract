# Tesseract - Fraud Detection System

An end-to-end fraud detection system with real-time transaction processing, machine learning models, and streaming capabilities.

## 🏗️ Architecture

- **FastAPI REST API**: Main API service for fraud prediction
- **Kafka Streaming**: Real-time transaction processing pipeline
- **Redis Cache**: Caching layer for faster predictions
- **PostgreSQL**: Database for storing predictions and statistics
- **Docker**: Containerized deployment
- **AWS Lambda**: Serverless fraud detection function

## 📋 Prerequisites

Before running the system, ensure you have:

- **Python 3.9+** (project uses Python 3.11)
- **PostgreSQL** installed and running
- **Redis** installed and running
- **Kafka & Zookeeper** installed (for streaming features)
- **Docker** installed (optional, for containerized deployment)
- **Virtual Environment** activated

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Set Up Database (PostgreSQL)

Create a database and set environment variables:

```bash
# Windows PowerShell
$env:DB_HOST="localhost"
$env:DB_NAME="fraud_detection"
$env:DB_USER="postgres"
$env:DB_PASSWORD="your_password"

# Windows CMD
set DB_HOST=localhost
set DB_NAME=fraud_detection
set DB_USER=postgres
set DB_PASSWORD=your_password

# macOS/Linux
export DB_HOST=localhost
export DB_NAME=fraud_detection
export DB_USER=postgres
export DB_PASSWORD=your_password
```

The FastAPI service will automatically create the `predictions` table on first run.

### 3. Start Required Services

#### Option A: Manual Start (Windows)

1. **Start PostgreSQL** (if not running as a service)
2. **Start Redis**:
   ```powershell
   redis-server
   ```
3. **Start Zookeeper** (if using Kafka):
   ```bash
   # Navigate to Kafka directory
   bin\windows\zookeeper-server-start.bat config\zookeeper.properties
   ```
4. **Start Kafka** (in another terminal):
   ```bash
   # Navigate to Kafka directory
   bin\windows\kafka-server-start.bat config\server.properties
   ```

#### Option B: Automated Script (Recommended)

**Windows PowerShell:**
```powershell
.\run.ps1
```

**macOS/Linux:**
```bash
chmod +x run.sh
./run.sh
```

### 4. Run the FastAPI Service

```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Start the API server
uvicorn src.fastapi_service:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

## 🎯 Usage Examples

### 1. Single Transaction Prediction

```bash
# Using curl
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.50,
    "hour": 14,
    "dayofweek": 3,
    "txns_last_24h": 5.0,
    "amount_last_24h": 500.0,
    "risk_score": 25.5
  }'
```

### 2. Batch Prediction

```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {
        "amount": 100.50,
        "hour": 14,
        "dayofweek": 3,
        "txns_last_24h": 5.0,
        "amount_last_24h": 500.0,
        "risk_score": 25.5
      },
      {
        "amount": 2000.00,
        "hour": 2,
        "dayofweek": 0,
        "txns_last_24h": 1.0,
        "amount_last_24h": 2000.0,
        "risk_score": 4000.0
      }
    ]
  }'
```

### 3. CSV Upload

```bash
curl -X POST "http://localhost:8000/predict/csv" \
  -F "file=@path/to/transactions.csv"
```

### 4. View Statistics

```bash
curl "http://localhost:8000/stats"
```

### 5. View Recent Transactions

```bash
curl "http://localhost:8000/transactions?limit=10"
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check |
| `/predict` | POST | Single transaction prediction |
| `/predict/batch` | POST | Batch transaction prediction |
| `/predict/csv` | POST | CSV file upload prediction |
| `/transactions` | GET | Get recent transactions |
| `/stats` | GET | Get fraud statistics |

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t fraud-detection .
```

### Run Docker Container

```bash
docker run -p 8000:8000 \
  -e DB_HOST=host.docker.internal \
  -e DB_NAME=fraud_detection \
  -e DB_USER=postgres \
  -e DB_PASSWORD=your_password \
  fraud-detection
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_NAME` | Database name | `fraud_detection` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `SNS_TOPIC_ARN` | AWS SNS topic ARN (for Lambda) | - |

### Model Files

The system uses multiple model files:
- `src/fraud_detection_model.pkl` - Main FastAPI model
- `src/xgb_model.pkl` - XGBoost model (Kafka/Lambda)
- `src/rf_model.pkl` - Random Forest model
- `src/isolation_model.pkl` - Isolation Forest model

## 📝 Data Format

### Transaction Schema

```json
{
  "amount": 100.50,
  "hour": 14,
  "dayofweek": 3,
  "txns_last_24h": 5.0,
  "amount_last_24h": 500.0,
  "risk_score": 25.5,
  "transaction_id": "optional-uuid"
}
```

## 🔍 Troubleshooting

### Common Issues

1. **Model not found error**
   - Ensure model files exist in `src/` directory
   - Check file paths in code

2. **Database connection failed**
   - Verify PostgreSQL is running
   - Check environment variables
   - Ensure database exists

3. **Redis connection failed**
   - Start Redis server: `redis-server`
   - Verify Redis is running on port 6379

4. **Kafka connection failed**
   - Ensure Zookeeper is running first
   - Start Kafka server
   - Verify Kafka is running on port 9092

5. **Port already in use**
   - Change port in FastAPI: `--port 8001`
   - Or kill process using the port

## 📦 Project Structure

```
Tessaract/
├── data/                    # Data files
│   ├── creditcard.csv
│   └── *_processed_transactions.csv
├── notebooks/              # Jupyter notebooks
│   ├── 01_data_preprocessing.ipynb
│   └── 02_model_training.ipynb
├── src/                    # Source code
│   ├── fastapi_service.py  # Main API
│   ├── aws_lambda.py       # Lambda function
│   ├── kafka_producer.py   # Kafka producer
│   ├── kafka_consumer.py   # Kafka consumer
│   ├── redis_cache.py      # Redis caching
│   └── *.pkl              # Model files
├── Dockerfile
├── requirements.txt
├── run.sh                  # Linux/macOS run script
├── run.ps1                 # Windows PowerShell script
└── README.md
```

## 🧪 Development

### Training Models

Models can be trained using the Jupyter notebooks:
1. `notebooks/01_data_preprocessing.ipynb` - Data preprocessing
2. `notebooks/02_model_training.ipynb` - Model training

### Running Tests

```bash
# Add tests when available
pytest tests/
```

## 📄 License

This project is part of the Tesseract fraud detection system.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guide
- Add tests for new features
- Update documentation
