FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed (e.g. gcc for numpy/scipy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create appuser and set permissions
RUN adduser --disabled-password --gecos '' appuser 

# Copy requirements separately for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Switch to non-root user
USER appuser

# Healthcheck to ensure Celery is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD celery -A tasks inspect ping || exit 1

# Run Celery worker
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]