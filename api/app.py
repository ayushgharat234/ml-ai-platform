from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from prometheus_fastapi_instrumentator import Instrumentator
from celery import Celery
from celery.result import AsyncResult
import os

# Initialize FastAPI app
app = FastAPI(title="ML Async API", version="1.0")
Instrumentator().instrument(app).expose(app)

# Celery configuration using environment variables
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "db+postgresql://celery_user:celery_pass@db:5432/celery_db")

celery_app = Celery(
    "tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Input schema
class Features(BaseModel):
    features: List[float]

@app.get("/")
async def root():
    return {"message": "ML Async API Running!"}

@app.post("/predict/", status_code=202)
async def predict(data: Features):
    """
    Dispatch a prediction task to the Celery worker.
    """
    try:
        task = celery_app.send_task("tasks.predict_task", args=[data.features])
        return {"task_id": task.id, "status": "Task submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    """
    Fetch the result of a prediction task.
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        if not task_result.ready():
            return {"task_id": task_id, "status": task_result.status, "result": None}
        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching result: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    """
    return {
        "status": "healthy",
        "broker_url": CELERY_BROKER_URL,
        "backend": CELERY_RESULT_BACKEND,
    }