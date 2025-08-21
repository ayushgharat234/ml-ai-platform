from celery import Celery
import pickle
import numpy as np
import logging
import os
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model with error handling
def load_model():
    try:
        model = pickle.load(open("model.pkl", "rb"))
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

model = load_model()
model_loaded = model is not None

# Celery configuration using environment variables
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "db+postgresql://celery_user:celery_pass@db:5432/celery_db")

celery = Celery(
    'tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

@celery.task(
    name='tasks.predict_task',
    bind=True,
    autoretry_for=(Exception,),   # retry on any exception
    retry_backoff=True,           # exponential backoff
    retry_kwargs={'max_retries': 5}  # prevent infinite retries
)
def predict_task(self, features: List[float]):
    global model, model_loaded
    
    if not model_loaded:
        logger.warning("Model not loaded, attempting reload...")
        model = load_model()
        model_loaded = model is not None
        if not model_loaded:
            raise self.retry(exc=ConnectionError("Model not available"))

    try:
        features_array = np.array(features).reshape(1, -1)
        pred = model.predict(features_array)
        prob = model.predict_proba(features_array)
        return {
            "prediction": pred.tolist(),
            "probabilities": prob.tolist()
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise self.retry(exc=e)  # retry prediction with backoff
