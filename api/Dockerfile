FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Install dependencies as root
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Add a non-root user AFTER dependencies (so pip installs work cleanly)
RUN adduser --disabled-password --gecos '' appuser

# Copy app code
COPY . .

# Switch to non-root user
USER appuser

# Expose port (optional but nice for docs)
EXPOSE 8000

# Healthcheck (optional but useful for k8s / docker-compose)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

# Run uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]