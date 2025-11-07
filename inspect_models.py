from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import joblib
import pandas as pd
import datetime
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Model Fraud Detection API")

# Load ALL models
models = {}
model_files = {
    'lightgbm': 'src/fraud_detection_model.pkl',
    'isolation_forest': 'src/isolation_model.pkl',
    'random_forest': 'src/rf_model.pkl',
    'xgboost': 'src/xgb_model.pkl'
}

for name, path in model_files.items():
    try:
        models[name] = joblib.load(path)
        logger.info(f"✅ Loaded {name} model")
    except Exception as e:
        logger.warning(f"⚠️  Could not load {name}: {str(e)}")

class Transaction(BaseModel):
    amount: float
    hour: int
    dayofweek: int
    txns_last_24h: float
    amount_last_24h: float
    risk_score: float
    transaction_id: Optional[str] = None

class MultiModelResponse(BaseModel):
    transaction_id: str
    final_decision: str  # "FRAUD", "SAFE", "REVIEW"
    confidence: float
    models_used: Dict[str, dict]
    is_anomaly: bool
    timestamp: str

@app.get("/")
def home():
    return {
        "message": "Multi-Model Fraud Detection API",
        "models_loaded": list(models.keys()),
        "endpoints": ["/predict", "/predict/ensemble", "/health"]
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "models": {name: "loaded" for name in models.keys()}
    }

@app.post("/predict/single")
def predict_single_model(transaction: Transaction, model_name: str = "lightgbm"):
    """Use a single specific model"""
    if model_name not in models:
        raise HTTPException(400, f"Model '{model_name}' not available")
    
    model = models[model_name]
    transaction_id = transaction.transaction_id or str(uuid.uuid4())
    
    df = pd.DataFrame([{
        'Amount': transaction.amount,
        'hour': transaction.hour,
        'dayofweek': transaction.dayofweek,
        'txns_last_24h': transaction.txns_last_24h,
        'amount_last_24h': transaction.amount_last_24h,
        'risk_score': transaction.risk_score
    }])
    
    is_fraud = bool(model.predict(df)[0])
    
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(df)[0]
        confidence = float(proba[1] if is_fraud else proba[0])
    else:
        confidence = 1.0 if is_fraud else 0.0
    
    return {
        "transaction_id": transaction_id,
        "model_used": model_name,
        "is_fraud": is_fraud,
        "confidence": confidence,
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.post("/predict/ensemble", response_model=MultiModelResponse)
def predict_ensemble(transaction: Transaction):
    """
    Use ALL models and combine their predictions
    This is the most accurate approach!
    """
    transaction_id = transaction.transaction_id or str(uuid.uuid4())
    
    df = pd.DataFrame([{
        'Amount': transaction.amount,
        'hour': transaction.hour,
        'dayofweek': transaction.dayofweek,
        'txns_last_24h': transaction.txns_last_24h,
        'amount_last_24h': transaction.amount_last_24h,
        'risk_score': transaction.risk_score
    }])
    
    # Collect predictions from all models
    predictions = {}
    votes = {"fraud": 0, "safe": 0}
    
    # Supervised models (LightGBM, RF, XGBoost)
    for name in ['lightgbm', 'random_forest', 'xgboost']:
        if name in models:
            model = models[name]
            is_fraud = bool(model.predict(df)[0])
            proba = model.predict_proba(df)[0]
            confidence = float(proba[1] if is_fraud else proba[0])
            
            predictions[name] = {
                "is_fraud": is_fraud,
                "confidence": confidence,
                "fraud_probability": float(proba[1])
            }
            
            if is_fraud:
                votes["fraud"] += 1
            else:
                votes["safe"] += 1
    
    # Isolation Forest (anomaly detection)
    is_anomaly = False
    if 'isolation_forest' in models:
        iso_model = models['isolation_forest']
        # Isolation Forest: -1 = anomaly, 1 = normal
        prediction = iso_model.predict(df)[0]
        is_anomaly = (prediction == -1)
        
        # Get anomaly score
        anomaly_score = iso_model.score_samples(df)[0]
        
        predictions['isolation_forest'] = {
            "is_anomaly": is_anomaly,
            "anomaly_score": float(anomaly_score),
            "interpretation": "Unusual pattern detected" if is_anomaly else "Normal pattern"
        }
    
    # Final decision logic
    fraud_percentage = (votes["fraud"] / (votes["fraud"] + votes["safe"])) * 100
    
    # Calculate average confidence
    avg_confidence = sum(p["confidence"] for p in predictions.values() if "confidence" in p) / max(len([p for p in predictions.values() if "confidence" in p]), 1)
    
    # Decision rules
    if votes["fraud"] >= 2:  # Majority vote
        final_decision = "FRAUD"
    elif is_anomaly and votes["fraud"] >= 1:  # Anomaly + at least one fraud vote
        final_decision = "REVIEW"  # Flag for manual review
    elif is_anomaly:
        final_decision = "REVIEW"
    else:
        final_decision = "SAFE"
    
    logger.info(f"Transaction {transaction_id}: {final_decision} (Fraud votes: {votes['fraud']}/{votes['fraud'] + votes['safe']}, Anomaly: {is_anomaly})")
    
    return MultiModelResponse(
        transaction_id=transaction_id,
        final_decision=final_decision,
        confidence=avg_confidence,
        models_used=predictions,
        is_anomaly=is_anomaly,
        timestamp=datetime.datetime.now().isoformat()
    )

@app.post("/predict")
def predict_default(transaction: Transaction):
    """Default endpoint - uses ensemble for best accuracy"""
    return predict_ensemble(transaction)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)