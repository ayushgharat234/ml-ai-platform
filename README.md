# AI Platform - System Architecture

## Overview
This is a microservices-based AI platform that provides machine learning prediction capabilities through a REST API. The system uses a distributed architecture with separate services for API handling, background task processing, and data storage.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Web Browser   │    │   API Clients   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     FastAPI Service       │
                    │     (Port 8000)           │
                    │  - REST API Endpoints     │
                    │  - Request Validation     │
                    │  - Direct Predictions     │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      Redis Service        │
                    │     (Port 6379)           │
                    │  - Message Broker         │
                    │  - Task Queue             │
                    │  - Caching Layer          │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   Celery Worker Service   │
                    │  - Background Tasks       │
                    │  - ML Model Processing    │
                    │  - Async Predictions      │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   PostgreSQL Database     │
                    │     (Port 5432)           │
                    │  - Task Results Storage   │
                    │  - Application Data       │
                    └───────────────────────────┘
```

## Components Breakdown

### 1. **FastAPI Service** (`api/`)
- **Purpose**: Main API gateway and request handler
- **Port**: 8000
- **Key Features**:
  - REST API endpoints for predictions
  - Request validation using Pydantic
  - Health monitoring
  - Direct ML model predictions (synchronous)
  - Redis connectivity for caching

**Endpoints**:
- `GET /` - Service status
- `GET /health` - Health check with model and Redis status
- `POST /predict/` - Make predictions with feature data

### 2. **Redis Service**
- **Purpose**: Message broker and caching layer
- **Port**: 6379
- **Key Features**:
  - Task queue management for Celery
  - Caching layer for API responses
  - Health monitoring with ping checks

### 3. **Celery Worker Service** (`worker/`)
- **Purpose**: Background task processing
- **Key Features**:
  - Asynchronous ML model predictions
  - Task queue processing
  - Error handling and logging
  - Redis-based task distribution

### 4. **PostgreSQL Database**
- **Purpose**: Persistent data storage
- **Port**: 5432
- **Key Features**:
  - Task result storage
  - Application data persistence
  - Health monitoring with pg_isready

## Data Flow

### Synchronous Prediction Flow:
```
1. Client → FastAPI (/predict/)
2. FastAPI → Load ML Model
3. FastAPI → Process Features
4. FastAPI → Return Prediction + Probabilities
```

### Asynchronous Prediction Flow (via Celery):
```
1. Client → FastAPI (/predict/async)
2. FastAPI → Redis (Task Queue)
3. Redis → Celery Worker
4. Celery Worker → Load ML Model
5. Celery Worker → Process Features
6. Celery Worker → Store Results (PostgreSQL)
7. Client → Check Task Status
```

## ML Model

- **Model Type**: Logistic Regression (scikit-learn)
- **Dataset**: Iris dataset (4 features, 3 classes)
- **Training**: Done via `train_and_save_model.py`
- **Storage**: Pickle format (`model.pkl`)
- **Features**: [sepal_length, sepal_width, petal_length, petal_width]

## Issues Fixed

### 1. **Import Error Resolution**
- **Problem**: API tried to import from `worker.tasks` across containers
- **Solution**: Removed cross-container imports, made API self-contained

### 2. **Redis Connection Issues**
- **Problem**: Worker used `localhost:6379` instead of service name
- **Solution**: Changed to `redis:6379` for container communication

### 3. **Docker Configuration**
- **Problem**: Inconsistent Python versions (3.10 vs 3.11)
- **Solution**: Standardized to Python 3.10 across all services

### 4. **Error Handling**
- **Problem**: No error handling for model loading or predictions
- **Solution**: Added comprehensive try-catch blocks and logging

### 5. **Health Monitoring**
- **Problem**: No health checks for services
- **Solution**: Added healthcheck endpoints and Docker healthchecks

### 6. **Dependency Management**
- **Problem**: Unversioned dependencies
- **Solution**: Pinned all package versions for consistency

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.10+ (for local development)

### Quick Start
```bash
# Build and start all services
docker-compose up --build

# Test the API
python test_api.py

# View logs
docker-compose logs -f api
```

### API Usage

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Make Prediction
```bash
curl -X POST http://localhost:8000/predict/ \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

## Monitoring and Debugging

### Service Health
- **API**: `http://localhost:8000/health`
- **Redis**: `docker exec redis_container redis-cli ping`
- **PostgreSQL**: `docker exec postgres pg_isready -U celery_user -d celery_db`

### Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs api
docker-compose logs worker
docker-compose logs redis
```

### Container Status
```bash
docker-compose ps
```

## Development

### Adding New Endpoints
1. Edit `api/app.py`
2. Add new route handlers
3. Update requirements if needed
4. Rebuild containers

### Modifying ML Model
1. Update `train_and_save_model.py`
2. Run training script
3. Copy new `model.pkl` to both `api/` and `worker/` directories
4. Rebuild containers

### Scaling
- **API**: Scale with `docker-compose up --scale api=3`
- **Worker**: Scale with `docker-compose up --scale worker=2`
- **Redis**: Use Redis Cluster for production
- **Database**: Use managed PostgreSQL service for production

## Production Considerations

1. **Security**: Add authentication, HTTPS, input validation
2. **Monitoring**: Add Prometheus/Grafana for metrics
3. **Logging**: Centralized logging with ELK stack
4. **Backup**: Database backup strategies
5. **Load Balancing**: Use nginx or cloud load balancer
6. **Environment Variables**: Use `.env` files for configuration 