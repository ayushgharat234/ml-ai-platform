FROM python:3.10-slim AS worker

WORKDIR /app

RUN adduser --disabled-password --gecos '' appuser 
USER appuser

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD celery -A tasks inspect ping || exit 1

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]