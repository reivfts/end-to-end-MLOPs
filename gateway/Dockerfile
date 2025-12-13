FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (create if doesn't exist)
COPY requirements.txt* ./

# Install Python dependencies
RUN pip install --no-cache-dir flask flask-cors PyJWT

# Copy application
COPY main.py ./
COPY static/ ./static/

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001', timeout=5)"

# Run application
CMD ["python", "main.py"]
