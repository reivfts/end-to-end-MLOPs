# Booking Service - Docker Guide

This guide explains how to build and run the booking service backend using Docker.

## Prerequisites

- Docker installed ([Download Docker Desktop](https://www.docker.com/products/docker-desktop))
- Docker Compose installed (included with Docker Desktop)

## Quick Start with Docker Compose

### 1. Build and Start the Container

```powershell
cd c:\dev\end-to-end-MLOPs\booking
docker-compose up -d
```

The `-d` flag runs it in the background. You should see:
```
Creating booking-backend ... done
```

### 2. Verify the Service is Running

```powershell
# Check if container is running
docker ps

# Or test the API
Invoke-RestMethod -Uri "http://localhost:8000/rooms" -Method Get
```

### 3. View Logs

```powershell
# Follow logs in real-time
docker-compose logs -f

# Or just the latest logs
docker-compose logs
```

### 4. Stop the Service

```powershell
docker-compose down
```

---

## Manual Docker Build & Run

If you prefer to build and run manually without docker-compose:

### 1. Build the Image

```powershell
cd c:\dev\end-to-end-MLOPs\booking
docker build -t booking-service:latest .
```

### 2. Run the Container

```powershell
docker run -d `
  -p 8000:8000 `
  -v ${PWD}/rooms.db:/app/rooms.db `
  --name booking-backend `
  booking-service:latest
```

### 3. Stop the Container

```powershell
docker stop booking-backend
docker rm booking-backend
```

---

## Docker Commands Reference

### View Running Containers

```powershell
docker ps
```

### View All Containers (including stopped)

```powershell
docker ps -a
```

### View Container Logs

```powershell
# Follow logs
docker logs -f booking-backend

# Last 100 lines
docker logs --tail 100 booking-backend
```

### Execute Command in Container

```powershell
# Get a shell inside the container
docker exec -it booking-backend sh

# Run a command
docker exec booking-backend python -c "import sqlite3; print('SQLite working!')"
```

### Remove Container

```powershell
docker stop booking-backend
docker rm booking-backend
```

### Remove Image

```powershell
docker rmi booking-service:latest
```

### Clean Up All Unused Resources

```powershell
docker system prune -a
```

---

## Testing with Docker

Once your container is running, test it the same way:

### 1. Open Frontend

Open `booking.html` in your browser:
```
file:///c:/dev/end-to-end-MLOPs/booking/booking.html
```

### 2. Test API Endpoints

```powershell
# Get all rooms
Invoke-RestMethod -Uri "http://localhost:8000/rooms" -Method Get

# Create a booking
$body = @{
    room_id = 1
    date = "2025-12-20"
    username = "Docker Test"
    time_slot = "morning"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/bookings" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

# Get all bookings
Invoke-RestMethod -Uri "http://localhost:8000/bookings" -Method Get
```

---

## Docker Compose File Explained

```yaml
version: '3.8'                    # Docker Compose version

services:
  booking-backend:               # Service name
    build:                        # Build configuration
      context: .                  # Current directory
      dockerfile: Dockerfile      # Use Dockerfile
    ports:
      - "8000:8000"              # Map port 8000 host -> container
    volumes:
      - ./rooms.db:/app/rooms.db  # Persist database between restarts
    environment:
      - PYTHONUNBUFFERED=1       # Show Python output immediately
    container_name: booking-backend
    restart: unless-stopped       # Auto-restart on crash
```

---

## Dockerfile Explained

```dockerfile
FROM python:3.9-slim
# Use lightweight Python 3.9 image

WORKDIR /app
# Set working directory inside container

COPY requirements.txt .
COPY main.py .
# Copy files from host to container

RUN pip install --no-cache-dir -r requirements.txt
# Install Python dependencies (--no-cache-dir saves space)

EXPOSE 8000
# Document that port 8000 is used (doesn't actually publish it)

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/rooms')" || exit 1
# Check every 30 seconds if the service is healthy

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# Start the service when container starts
```

---

## Troubleshooting

### Issue: "Docker daemon is not running"

**Solution:**
- Open Docker Desktop application
- Wait for it to fully start

### Issue: Port 8000 already in use

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or use a different port in docker-compose.yml
# Change: "8000:8000" to "8001:8000"
```

### Issue: Container exits immediately

**Solution:**
```powershell
# Check logs
docker logs booking-backend

# Look for errors in requirements.txt or main.py
```

### Issue: Database not persisting

**Solution:**
- Make sure the volume is defined in docker-compose.yml
- The database file should be at `./rooms.db`

### Issue: Cannot connect to http://localhost:8000

**Solution:**
```powershell
# Verify container is running
docker ps

# Check if port is mapped correctly
docker port booking-backend

# Test from inside container
docker exec booking-backend curl http://localhost:8000/rooms
```

---

## Environment Variables

To pass environment variables to the container, add them to docker-compose.yml:

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - BOOKING_DB_PATH=/app/rooms.db
  # Add more as needed
```

---

## Multi-Stage Build (Optional - for production)

For a smaller image size, you can use a multi-stage Dockerfile:

```dockerfile
# Stage 1: Build
FROM python:3.9 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY main.py .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Summary

✅ **Docker Benefits:**
- Consistent environment across machines
- Easy deployment
- Isolated from system Python
- Simple scaling

✅ **Quick Commands:**
```powershell
docker-compose up -d          # Start
docker-compose logs -f        # View logs
docker-compose down           # Stop
```

Happy containerizing! 🐳
