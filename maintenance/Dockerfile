FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir flask flask-cors flask-socketio python-socketio nltk scikit-learn eventlet requests PyJWT

# Download NLTK data
RUN python -m nltk.downloader punkt averaged_perceptron_tagger wordnet stopwords -d /usr/local/share/nltk_data

# Copy application
COPY websocket_api.py ./
COPY main.py* ./
COPY enhanced_model.py* ./
COPY model.py* ./

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/', timeout=5)" || exit 1

# Run application
CMD ["python", "websocket_api.py"]
