FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt* ./

# Install Python dependencies
RUN pip install --no-cache-dir flask flask-cors requests PyJWT psycopg2-binary

# Copy application
COPY app.py ./
COPY main.py* ./

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health', timeout=5)" || exit 1

# Run application
CMD ["python", "app.py"]
