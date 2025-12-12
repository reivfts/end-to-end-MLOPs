FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements_websocket.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements_websocket.txt

# Download NLTK data (required for NLP analysis)
RUN python -m nltk.downloader punkt stopwords wordnet averaged_perceptron_tagger -d /usr/local/share/nltk_data

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "websocket_api.py"]
