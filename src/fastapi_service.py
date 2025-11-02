from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
import joblib
import pandas as pd
import numpy as np
from lightgbm import LGBMClassifier
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
import datetime
import os
from fastapi.middleware.cors import CORSMiddleware
import logging
import csv
import io

# Load .env file if it exists (before importing database module)
try:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from load_env import load_env_file
    load_env_file()
except Exception:
    pass  # Continue if .env loading fails

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import Redis cache
from src.redis_cache import get_cached_transaction, cache_transaction

# Import database module
from src.database import (
    init_db,
    is_db_available,
    log_prediction,
    get_recent_transactions,
    get_fraud_stats,
    close_db_pool
)

# Initialize database connection pool
db_available = init_db()

app = FastAPI(title="Fraud Detection API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load trained model
try:
    model = joblib.load('src/fraud_detection_model.pkl')
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    model = None

# Define request body schema
class Transaction(BaseModel):
    amount: float
    hour: int
    dayofweek: int
    txns_last_24h: float
    amount_last_24h: float
    risk_score: float
    transaction_id: Optional[str] = None

class BatchTransactions(BaseModel):
    transactions: List[Transaction]

class PredictionResponse(BaseModel):
    transaction_id: str
    is_fraud: bool
    confidence: float
    timestamp: str

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    summary: dict

# log_prediction function is now imported from database module

@app.get("/")
def home():
    return {"message": "Fraud Detection API is running!"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "database_connected": is_db_available()
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_fraud(transaction: Transaction):
    """Predict fraud for a single transaction"""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Generate transaction ID if not provided
        transaction_id = transaction.transaction_id or str(uuid.uuid4())
        
        # Check cache first
        cached_result = get_cached_transaction(transaction_id)
        if cached_result:
            return PredictionResponse(
                transaction_id=transaction_id,
                is_fraud=cached_result["is_fraud"],
                confidence=cached_result["confidence"],
                timestamp=datetime.datetime.now().isoformat()
            )
        
        # Prepare data for prediction
        df = pd.DataFrame([transaction.dict()])
        
        # Remove transaction_id from features
        if "transaction_id" in df.columns:
            df = df.drop("transaction_id", axis=1)
        
        # Ensure feature names match the model's training data
        df.rename(columns={"amount": "Amount"}, inplace=True)
        
        # Predict fraud using the trained model
        is_fraud = bool(model.predict(df)[0])
        
        # Get prediction probabilities for confidence score
        proba = model.predict_proba(df)[0]
        confidence = float(proba[1] if is_fraud else proba[0])
        
        # Cache the result
        result = {
            "is_fraud": is_fraud,
            "confidence": confidence
        }
        cache_transaction(transaction_id, result)
        
        # Log prediction to database (non-blocking, returns immediately)
        log_prediction(
            transaction_id=transaction_id,
            transaction_data=transaction.dict(),
            prediction=is_fraud,
            confidence=confidence
        )
        
        return PredictionResponse(
            transaction_id=transaction_id,
            is_fraud=is_fraud,
            confidence=confidence,
            timestamp=datetime.datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(batch: BatchTransactions):
    """Predict fraud for a batch of transactions"""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        predictions = []
        
        # Optimize: Create DataFrame for all transactions at once
        transactions_data = [t.dict() for t in batch.transactions]
        df = pd.DataFrame(transactions_data)
        
        # Remove transaction_id from features if present
        if "transaction_id" in df.columns:
            df_features = df.drop("transaction_id", axis=1)
        else:
            df_features = df.copy()
        
        # Ensure feature names match the model's training data
        if "amount" in df_features.columns:
            df_features.rename(columns={"amount": "Amount"}, inplace=True)
        
        # Predict for all transactions at once (much faster!)
        fraud_predictions = model.predict(df_features)
        fraud_probabilities = model.predict_proba(df_features)
        
        # Process results
        for i, transaction in enumerate(batch.transactions):
            transaction_id = transaction.transaction_id or str(uuid.uuid4())
            
            # Check cache first
            cached_result = get_cached_transaction(transaction_id)
            if cached_result:
                predictions.append(
                    PredictionResponse(
                        transaction_id=transaction_id,
                        is_fraud=cached_result["is_fraud"],
                        confidence=cached_result["confidence"],
                        timestamp=datetime.datetime.now().isoformat()
                    )
                )
                continue
            
            # Use batch prediction results (already computed)
            is_fraud = bool(fraud_predictions[i])
            proba = fraud_probabilities[i]
            confidence = float(proba[1] if is_fraud else proba[0])
            
            # Cache the result
            result = {
                "is_fraud": is_fraud,
                "confidence": confidence
            }
            cache_transaction(transaction_id, result)
            
            # Log prediction to database
            log_prediction(
                transaction_id=transaction_id,
                transaction_data=transaction.dict(),
                prediction=is_fraud,
                confidence=confidence
            )
            
            predictions.append(
                PredictionResponse(
                    transaction_id=transaction_id,
                    is_fraud=is_fraud,
                    confidence=confidence,
                    timestamp=datetime.datetime.now().isoformat()
                )
            )
        
        # Generate summary statistics
        fraud_count = sum(1 for p in predictions if p.is_fraud)
        total_count = len(predictions)
        
        summary = {
            "total_transactions": total_count,
            "fraud_count": fraud_count,
            "fraud_percentage": (fraud_count / total_count) * 100 if total_count > 0 else 0,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return BatchPredictionResponse(
            predictions=predictions,
            summary=summary
        )
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/csv")
async def predict_from_csv(file: UploadFile = File(...)):
    """Predict fraud from CSV file upload"""
    if model is None:
        logger.error("Model not loaded. Check if fraud_detection_model.pkl exists in src directory")
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Log file details
        logger.info(f"Received CSV file: {file.filename}, content_type: {file.content_type}")
        
        # Read CSV file
        contents = await file.read()
        try:
            text_content = contents.decode('utf-8')
            logger.info("Successfully decoded CSV content as UTF-8")
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            text_content = contents.decode('latin-1')
            logger.info("Decoded CSV content as latin-1")
            
        buffer = io.StringIO(text_content)
        csv_reader = csv.DictReader(buffer)
        
        # Validate CSV headers
        headers = csv_reader.fieldnames
        logger.info(f"CSV headers: {headers}")
        
        # Define field mappings (your CSV format -> expected format)
        field_mappings = {
            'Amount': 'amount',  # Map 'Amount' to 'amount'
            'hour': 'hour',     # These are already correct
            'dayofweek': 'dayofweek',
            'txns_last_24h': 'txns_last_24h',
            'amount_last_24h': 'amount_last_24h',
            'risk_score': 'risk_score'
        }
        
        # Check if required fields exist (using original column names)
        required_fields = ['Amount', 'hour', 'dayofweek', 'txns_last_24h', 'amount_last_24h', 'risk_score']
        missing_fields = [field for field in required_fields if field not in headers]
        if missing_fields:
            error_msg = f"Missing required columns: {missing_fields}"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        transactions = []
        row_count = 0
        error_count = 0
        
        for row in csv_reader:
            row_count += 1
            try:
                # Log row data for debugging
                logger.debug(f"Processing row {row_count}: {row}")
                
                # Convert string values to appropriate types using the correct column names
                transaction = Transaction(
                    amount=float(row.get('Amount', 0)),  # Use 'Amount' instead of 'amount'
                    hour=int(row.get('hour', 0)),
                    dayofweek=int(row.get('dayofweek', 0)),
                    txns_last_24h=float(row.get('txns_last_24h', 0)),
                    amount_last_24h=float(row.get('amount_last_24h', 0)),
                    risk_score=float(row.get('risk_score', 0)),
                    transaction_id=row.get('Time', str(uuid.uuid4()))  # Use 'Time' as transaction_id if available
                )
                transactions.append(transaction)
            except ValueError as ve:
                error_count += 1
                logger.warning(f"Invalid value in row {row_count}: {str(ve)}")
            except Exception as e:
                error_count += 1
                logger.warning(f"Error processing row {row_count}: {str(e)}")
        
        if not transactions:
            error_msg = f"No valid transactions found in CSV. Processed {row_count} rows with {error_count} errors."
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"Successfully processed {len(transactions)} transactions from CSV")
        
        # Use batch prediction logic
        batch = BatchTransactions(transactions=transactions)
        result = predict_batch(batch)
        
        # Add processing summary to response
        result.summary.update({
            "total_rows_processed": row_count,
            "valid_transactions": len(transactions),
            "errors": error_count
        })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"CSV prediction error: {str(e)}"
        logger.error(error_msg, exc_info=True)  # Include stack trace
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/transactions")
def get_recent_transactions_endpoint(limit: int = 100):
    """Get recent transactions from the database"""
    try:
        transactions = get_recent_transactions(limit)
        # Convert RealDictRow to dict and format timestamp
        formatted_transactions = []
        for row in transactions:
            formatted_transactions.append({
                "transaction_id": row['transaction_id'],
                "transaction_data": row['transaction_data'],
                "is_fraud": row['prediction'],
                "confidence": float(row['confidence']),
                "timestamp": row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp'])
            })
        return {"transactions": formatted_transactions}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Database query error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/stats")
def get_fraud_stats_endpoint():
    """Get fraud statistics for dashboard"""
    try:
        return get_fraud_stats()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Stats query error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    if not init_db():
        logger.warning("Database initialization failed. Some features may not work.")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    close_db_pool()
    logger.info("Application shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)