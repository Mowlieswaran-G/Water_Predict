# Base image: Python 3.11 slim
FROM python:3.11-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    FLASK_APP=app.py

# Set working directory inside container
WORKDIR /app

# Install system dependencies including curl for container health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for caching layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure outputs directory and data directory exist
RUN mkdir -p /app/outputs /app/data

# Expose application port
EXPOSE 5000 10000

# Healthcheck to verify the web service is responding
HEALTHCHECK --interval=20s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/healthz || exit 1

# Run with Gunicorn WSGI server for production (supports dynamic cloud PORT or 5000)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 app:app"]
