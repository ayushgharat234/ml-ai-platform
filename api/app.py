from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import pickle
import numpy as np
import redis
import time     
from prometheus_client import Summary, Counter
import json
from typing import List
from prometheus_fastapi_instrumentator import Instrumentator 


app = FastAPI()
Instrumentator().instrument(app).expose(app)

class Features(BaseModel):
    features: List[float]

# Initialize Redis connection with error handling
try:
    redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True, socket_connect_timeout=5, socket_timeout=5)
    # Test connection
    redis_client.ping()
    redis_available = True
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_available = False
    redis_client = None

# Load model with error handling
try:
    model = pickle.load(open("model.pkl", "rb"))
    model_loaded = True
except Exception as e:
    print(f"Error loading model: {e}")
    model_loaded = False
    model = None

@app.get("/")
async def root():
    return {"message": "ML Async API Running.......!"}

PREDICTION_TIME = Summary("prediction_duration_seconds", "Time spent on predictions")
PREDICTION_COUNTER = Counter("predictions_total", "Total number of predictions")

@app.post("/predict/")
@PREDICTION_TIME.time()
async def predict(data: Features):
    if not model_loaded:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Make prediction directly in API for simplicity
        PREDICTION_COUNTER.inc()
        features_array = np.array(data.features).reshape(1, -1)
        prediction = model.predict(features_array)
        probability = model.predict_proba(features_array)
        
        return {
            "prediction": prediction.tolist(),
            "probabilities": probability.tolist(),
            "features": data.features
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.get("/health")
async def health_check():
    redis_status = False
    if redis_client and redis_available:
        try:
            redis_client.ping()
            redis_status = True
        except:
            redis_status = False
    
    return {
        "status": "healthy",
        "model_loaded": model_loaded,
        "redis_connected": redis_status,
        "services": {
            "api": "running",
            "model": "loaded" if model_loaded else "not_loaded",
            "redis": "connected" if redis_status else "disconnected"
        }
    } 