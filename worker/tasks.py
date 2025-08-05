from celery import Celery 
import pickle 
import numpy as np 
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model with error handling
try:
    model = pickle.load(open("model.pkl", "rb"))
    logger.info("Model loaded successfully")
    model_loaded = True
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model_loaded = False
    model = None

# Celery configuration with retry settings
celery = Celery('tasks', broker="redis://redis:6379/0")

# Configure Celery for better reliability
celery.conf.update(
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery.task 
def predict_task(features: list[float]):
    if not model_loaded:
        raise Exception("Model not loaded")
    
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
        raise Exception(f"Prediction failed: {str(e)}")