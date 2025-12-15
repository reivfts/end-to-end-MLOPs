# Campus Services Hub - Microservices Platform

**Microservices Architecture** | **JWT Authentication** | **Role-Based Access Control** | **AI-Powered** | **Docker Ready**

> A production-ready campus management platform with 6 independent microservices, PostgreSQL/SQLite abstraction, correlation IDs, and comprehensive logging.

**Repository**: [reivfts/end-to-end-MLOPs](https://github.com/reivfts/end-to-end-MLOPs)  
**Last Updated**: December 15, 2025  
**Status**: Production Ready 

---

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Services](#services)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [Development](#development)
- [API Documentation](#api-documentation)
- [CI/CD Pipeline](#cicd-pipeline)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## System Overview

Campus Services Hub modernizes university operations through a microservices architecture. The system provides room booking, GPA calculations, AI-powered maintenance ticketing, notifications, and user management—all secured with JWT authentication and role-based access control.

### Key Features

✅ **6 Independent Microservices** - Separate databases, independent deployment  
✅ **JWT Authentication** - Secure token-based auth (HS256, 24-hour expiry)  
✅ **Role-Based Access Control** - Admin/Faculty/Student permissions  
✅ **Database Abstraction Layer** - SQLite (dev) or PostgreSQL (production)  
✅ **Connection Pooling** - Thread-safe PostgreSQL connection pool (2-20 connections)  
✅ **Distributed Tracing** - Correlation IDs track requests across all services  
✅ **Comprehensive Logging** - Python logging with structured format, dual output (file + stdout)  
✅ **Docker Support** - Full containerization with docker-compose orchestration  
✅ **CI/CD Pipeline** - GitHub Actions for automated testing and Docker builds  
✅ **AI Integration** - DistilBERT NLP model for maintenance ticket classification  
✅ **WebSocket Support** - Real-time updates for maintenance ticket status

### User Roles & Access

| Role | Permissions |
|------|-------------|
| **Admin** | User management, notifications, system monitoring |
| **Faculty** | Booking, GPA calculator, maintenance tickets, notifications |
| **Student** | Booking, GPA calculator, maintenance tickets, notifications |

### Default Credentials

```
Admin:   admin@example.com    / admin123
Faculty: faculty@example.com  / faculty123
Student: student@example.com  / student123
```

---

## Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│               Frontend (HTML/JavaScript/CSS)                     │
│                   Served from Port 5001/static                   │
│        Role-Based Navigation | JWT in localStorage               │
└───────────────────┬─────────────────────────────────────────────┘
                    │ HTTP/REST Requests (JSON)
                    │ Authorization: Bearer <JWT>
┌───────────────────▼─────────────────────────────────────────────┐
│              Gateway Service (Port 5001)                         │
│    Flask | JWT Validation | API Router | Static File Server     │
│    Correlation IDs | Logging | CORS | RBAC Enforcement          │
└─┬────────┬──────────┬───────────┬─────────────┬─────────────────┘
  │        │          │           │             │
  │ /api/  │ /api/    │ /api/     │ /api/       │ /api/
  │ users  │ booking  │ maintenance│ gpa        │ notifications
  │        │          │           │             │
┌─▼────────┐┌▼─────────┐┌▼──────────┐┌▼─────────┐┌▼─────────────┐
│User Mgmt ││ Booking  ││Maintenance││   GPA    ││Notification  │
│Flask 8002││FastAPI   ││Flask+WS   ││Flask 8003││Flask 8004    │
│          ││8001      ││8080       ││          ││              │
│JWT Auth  ││JWT Auth  ││JWT+WS Auth││JWT Auth  ││JWT Auth      │
│CRUD Ops  ││Async API ││AI Model   ││Stateless ││Event System  │
└─────┬────┘└─────┬────┘└─────┬─────┘└──────────┘└─────┬────────┘
      │           │           │                         │
      │           │           │                         │
      └───────────┴───────────┴─────────────────────────┘
                              │
            ┌─────────────────▼─────────────────┐
            │   shared/ Database Abstraction    │
            │   config.py | database.py         │
            │   http_client.py (retry logic)    │
            └───────────────────────────────────┘
                      │               │
         ┌────────────▼─────┐   ┌────▼───────────────────┐
         │ SQLite (Local Dev)│   │PostgreSQL (Docker/Prod)│
         │ - gateway.db     │   │ - campus_services DB   │
         │ - users.db       │   │ - users table          │
         │ - bookings.db    │   │ - bookings table       │
         │ - notifications  │   │ - notifications table  │
         │   .db            │   │ - Connection Pool      │
         │ (4 separate DBs) │   │ (Shared instance)      │
         └──────────────────┘   └────────────────────────┘
```

### Service Communication

- **Frontend → Gateway**: HTTP/REST with JWT in Authorization header
- **Gateway → Services**: HTTP/REST proxy with JWT forwarding
- **Services → Database**: Connection pool (PostgreSQL) or direct (SQLite)
- **Services → Notification**: HTTP POST for event notifications
- **Maintenance ↔ Clients**: WebSocket (Socket.IO) for real-time updates

---

## Quick Start

### Prerequisites

- **Python 3.8+** (3.13 recommended)
- **Git** (for cloning repository)
- **Docker & Docker Compose** (optional, for containerized deployment)
- **PostgreSQL** (optional, for production; included in docker-compose)

### Option 1: Local Development (SQLite)

```bash
# 1. Clone repository
git clone https://github.com/reivfts/end-to-end-MLOPs.git
cd end-to-end-MLOPs

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies for all services
pip install flask flask-cors pyjwt werkzeug requests
pip install fastapi uvicorn
pip install flask-socketio python-socketio
pip install transformers torch sentencepiece protobuf
pip install -r shared/requirements.txt

# 4. Start all services (uses SQLite by default)
bash start_all.sh

# 5. Access the application
# Frontend: http://localhost:5001
# Login with default credentials above
```

### Option 2: Docker Deployment (PostgreSQL)

```bash
# 1. Clone repository
git clone https://github.com/reivfts/end-to-end-MLOPs.git
cd end-to-end-MLOPs

# 2. Start all services with PostgreSQL
docker-compose up --build

# 3. Access the application
# Frontend: http://localhost:5001
# PostgreSQL: localhost:5432 (campus_services DB)
# All services auto-connected via Docker network
```

### Verify Services Running

```bash
# Check all services are healthy
curl http://localhost:5001/health  # Gateway
curl http://localhost:8001/health  # Booking
curl http://localhost:8002/health  # User Management
curl http://localhost:8003/health  # GPA Calculator
curl http://localhost:8004/health  # Notification
curl http://localhost:8080/health  # Maintenance

# All should return: {"status": "healthy"}
```

---

## Services

### 1. Gateway Service (Port 5001)

**Purpose**: Central authentication hub and API router

**Technology**: Flask + SQLite/PostgreSQL  
**Database**: `gateway.db` (SQLite) or `campus_services.users` (PostgreSQL)  
**Entry Point**: `gateway/main.py`

**Responsibilities**:
- JWT token generation and validation
- User authentication (login/logout)
- API routing to all microservices
- Static file serving (frontend HTML/CSS/JS)
- CORS configuration
- Correlation ID generation
- Request/response logging

**Key Endpoints**:
- `POST /auth/login` - User authentication, returns JWT token
- `GET /auth/me` - Get current user information from JWT
- `POST /auth/register` - Register new user account
- `GET /health` - Health check endpoint
- `GET /` - Serve frontend dashboard
- `GET /<page>.html` - Serve frontend pages (booking, gpa, etc.)
- `/api/*` - Proxy requests to backend services

### 2. User Management Service (Port 8002)

**Purpose**: User CRUD operations and role management

**Technology**: Flask + SQLite/PostgreSQL  
**Database**: `user-management/users.db` or PostgreSQL `users` table  
**Entry Point**: `user-management/app.py`

**Responsibilities**:
- Complete user lifecycle management (Create, Read, Update, Delete)
- Role assignment (Admin/Faculty/Student)
- Password hashing (Werkzeug security)
- Notification triggers on user changes
- Sync with gateway for authentication consistency

**Key Endpoints**:
- `GET /users` - List all users (paginated)
- `POST /users` - Create new user
- `GET /users/{id}` - Get user details
- `PUT /users/{id}` - Update user information
- `DELETE /users/{id}` - Delete user
- `GET /users/by-role/{role}` - Filter users by role

### 3. Booking Service (Port 8001)

**Purpose**: Room reservation and scheduling system

**Technology**: FastAPI (async) + SQLite/PostgreSQL  
**Database**: `booking/bookings.db` or PostgreSQL `bookings` table  
**Entry Point**: `booking/main.py`

**Responsibilities**:
- Room availability management
- Time slot booking (8 AM - 6 PM, hourly slots)
- Double-booking prevention (unique constraints)
- Student-only cancellation enforcement
- Notification integration on booking events
- Auto-generated API documentation (FastAPI Swagger)

**Key Endpoints**:
- `GET /rooms` - List available rooms
- `POST /bookings` - Create new booking
- `GET /bookings` - List all bookings
- `GET /bookings/user/{user_id}` - Get user's bookings
- `DELETE /bookings/{id}` - Cancel booking (students only can cancel own)
- `GET /bookings/available` - Get available time slots
- `GET /docs` - Interactive API documentation (Swagger UI)

### 4. GPA Calculator Service (Port 8003)

**Purpose**: Academic grade point average calculator

**Technology**: Flask (stateless, no database)  
**Entry Point**: `gpa-calculator/main.py`

**Responsibilities**:
- Weighted GPA calculation (A=4.0, B=3.0, C=2.0, D=1.0, F=0.0)
- Credit hour weighting
- JSON input/output
- Stateless computation (no data persistence)

**Key Endpoints**:
- `POST /calculate` - Calculate GPA from grades
  - Input: `{"courses": [{"grade": "A", "credits": 3}, ...]}`
  - Output: `{"gpa": 3.67, "total_credits": 12}`

### 5. Notification Service (Port 8004)

**Purpose**: System-wide notification and event management

**Technology**: Flask + SQLite/PostgreSQL  
**Database**: `notification/notifications.db` or PostgreSQL `notifications` table  
**Entry Point**: `notification/app.py`

**Responsibilities**:
- User-specific notifications
- Admin/system-wide notifications
- Role-based filtering
- Read/unread status tracking
- Notification history and persistence

**Key Endpoints**:
- `POST /notifications` - Create notification
- `GET /notifications` - List notifications
- `GET /notifications/user/{user_id}` - User's notifications
- `PUT /notifications/{id}` - Mark notification as read
- `DELETE /notifications/{id}` - Delete notification

### 6. Maintenance Service (Port 8080)

**Purpose**: AI-powered maintenance ticketing with real-time updates

**Technology**: Flask-SocketIO + WebSocket + DistilBERT NLP  
**Database**: In-memory (could be persisted to PostgreSQL)  
**Entry Point**: `maintenance/websocket_api.py`  
**AI Model**: `maintenance/enhanced_model.py`

**Responsibilities**:
- Maintenance ticket creation and management
- **AI Classification**: NLP-based ticket categorization (Plumbing, Electrical, HVAC, IT, etc.)
- **Priority Detection**: Identifies urgent keywords (flood, fire, emergency)
- Real-time WebSocket updates (Socket.IO)
- Batch ticket processing
- Pattern-based SLA assignment
- System impact analysis

**Key Endpoints**:
- `POST /tickets` - Create maintenance ticket (AI auto-categorizes)
- `GET /tickets` - List all tickets
- `GET /tickets/{id}` - Get ticket details
- `PUT /tickets/{id}` - Update ticket status
- `WS /socket.io` - WebSocket connection for real-time updates
- `GET /` - Serve WebSocket frontend (`websocket_frontend.html`)

**AI Model Details**:
- **Model**: DistilBERT (distilled BERT, 40% smaller, 60% faster)
- **Categories**: Plumbing, Electrical, HVAC, Carpentry, Cleaning, IT, Security, Other
- **Priority**: Urgent/Standard based on keyword detection
- **Inference Time**: ~200ms per ticket

---

## Configuration

### Environment Variables

The system supports environment-based configuration via `.env` file:

```bash
# Application Environment
FLASK_ENV=development        # development | production
FLASK_DEBUG=1                # 0 (off) | 1 (on)

# Security
JWT_SECRET_KEY=your-secret-key-change-in-production  # CRITICAL: Change in production!

# Database Configuration
DATABASE_TYPE=sqlite         # sqlite | postgresql
DB_HOST=localhost            # PostgreSQL host (or 'postgres' in Docker)
DB_PORT=5432                 # PostgreSQL port
DB_NAME=campus_services      # Database name
DB_USER=postgres             # Database username
DB_PASSWORD=postgres         # Database password

# Service Discovery (for Docker/AWS deployment)
DOCKER_CONTAINER=false       # true if running in Docker
GATEWAY_HOST=localhost       # Or: gateway (Docker), <ALB-DNS> (AWS)
USER_MGMT_HOST=localhost     # Or: user-management (Docker)
BOOKING_HOST=localhost       # Or: booking (Docker)
NOTIFICATION_HOST=localhost  # Or: notification (Docker)
GPA_HOST=localhost           # Or: gpa-calculator (Docker)
MAINTENANCE_HOST=localhost   # Or: maintenance (Docker)

# HTTP Client Configuration
REQUEST_TIMEOUT=10           # Request timeout in seconds
REQUEST_RETRY_ATTEMPTS=3     # Number of retry attempts
REQUEST_RETRY_BACKOFF=1.0    # Backoff factor for exponential backoff
```

**Setup Instructions**:
```bash
# 1. Copy example configuration
cp .env.example .env

# 2. Edit .env with your values
nano .env  # or vim, code, etc.

# 3. IMPORTANT: Change JWT_SECRET_KEY to a secure random string
# Generate secure key: python -c "import secrets; print(secrets.token_hex(32))"

# 4. Never commit .env to git (already in .gitignore)
```

### Shared Infrastructure

The `shared/` directory contains reusable modules for production deployments:

**`shared/config.py`**:
- Environment variable loading
- Service URL discovery (local/Docker/AWS)
- Configuration validation

**`shared/database.py`**:
- Database abstraction layer
- Connection pooling for PostgreSQL (ThreadedConnectionPool, 2-20 connections)
- Thread-local SQLite connections
- Automatic fallback to SQLite if PostgreSQL unavailable

**`shared/http_client.py`**:
- HTTP client with retry logic (3 attempts, exponential backoff)
- Circuit breaker pattern (opens after 5 failures for 60 seconds)
- Timeout handling
- Request correlation ID propagation

**Installation**:
```bash
pip install -r shared/requirements.txt
```

**Usage Example**:
```python
from shared import config, db_pool, http_client

# Get service URL (auto-detects environment)
user_service_url = config.get_service_url('users')

# Use connection pool
with db_pool.get_connection() as conn:
    cursor = conn.execute("SELECT * FROM users WHERE role = ?", ("student",))
    results = cursor.fetchall()

# HTTP with retry logic and circuit breaker
response = http_client.post(
    f"{user_service_url}/users",
    json={"name": "John Doe", "email": "john@example.com"}
)
```

---

## Docker Deployment

### Docker Compose Architecture

The `docker-compose.yml` orchestrates all 6 microservices + PostgreSQL database:

**Services Included**:
- `gateway` - Port 5001
- `user-management` - Port 8002
- `booking` - Port 8001
- `gpa-calculator` - Port 8003
- `notification` - Port 8004
- `maintenance` - Port 8080
- `postgres` - Port 5432 (PostgreSQL 15-alpine)

### Quick Start

```bash
# Start all services (builds images if needed)
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f gateway
docker-compose logs -f postgres

# Stop all services
docker-compose down

# Stop and remove volumes (deletes database data)
docker-compose down -v
```

### PostgreSQL Initialization

On first run, PostgreSQL automatically:
1. Creates `campus_services` database
2. Runs `init-db-postgres.sql` (creates all tables, indexes, constraints)
3. Sets up health checks (`pg_isready`)

**Database Schema** (`init-db-postgres.sql`):
- `users` table (UUID primary key, email index, role check constraint)
- `rooms` table (serial ID, name, capacity)
- `bookings` table (foreign key to rooms, unique constraint on room/date/time)
- `notifications` table (UUID primary key, user_id index)
- Indexes on frequently queried columns (email, date, user_id)

### Access Services

```bash
# Frontend
http://localhost:5001

# API Endpoints
http://localhost:5001/health  # Gateway
http://localhost:8001/docs     # Booking API docs (Swagger)
http://localhost:8001/health   # Booking health
# ... (all services have /health)

# PostgreSQL
psql -h localhost -U postgres -d campus_services
# Password: postgres (default, change in .env)
```

### Useful Docker Commands

```bash
# View running containers
docker ps

# Exec into container
docker-compose exec gateway bash
docker-compose exec postgres psql -U postgres -d campus_services

# View database connections
docker-compose exec postgres psql -U postgres -d campus_services \
  -c "SELECT count(*) FROM pg_stat_activity WHERE datname='campus_services';"

# Rebuild specific service
docker-compose up --build gateway

# View resource usage
docker stats

# Clean up everything
docker-compose down -v --remove-orphans
docker system prune -a  # CAUTION: Removes all unused Docker data
```

### Migrating SQLite to PostgreSQL

If you have existing SQLite data:

```bash
# 1. Ensure PostgreSQL is running
docker-compose up -d postgres

# 2. Run migration script
cd scripts
python migrate_to_postgresql.py

# 3. Follow prompts (provide DB host, port, credentials)

# 4. Update .env to use PostgreSQL
DATABASE_TYPE=postgresql
DB_HOST=localhost  # or 'postgres' if in Docker
```

---

## Development

### Project Structure

```
cloudMLOPS/
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # GitHub Actions CI/CD pipeline
├── gateway/
│   ├── Dockerfile
│   ├── main.py                 # Gateway service entry point
│   ├── gateway.db              # SQLite database (local dev)
│   └── static/                 # Frontend files
│       ├── login.html          # Login page
│       ├── dashboard.html      # Main dashboard
│       ├── booking.html        # Room booking UI
│       ├── gpa.html            # GPA calculator UI
│       ├── maintenance.html    # Maintenance tickets UI
│       ├── notifications.html  # Notifications UI
│       └── users.html          # User management UI (Admin)
├── user-management/
│   ├── Dockerfile
│   ├── main.py                 # Original user service
│   ├── app.py                  # Active user service (with logging)
│   ├── requirements.txt
│   └── users.db                # SQLite database (local dev)
├── booking/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── main.py                 # FastAPI booking service
│   ├── requirements.txt
│   └── bookings.db             # SQLite database (local dev)
├── gpa-calculator/
│   ├── Dockerfile
│   └── main.py                 # Stateless GPA calculator
├── notification/
│   ├── Dockerfile
│   ├── main.py                 # Original notification service
│   ├── app.py                  # Active notification service (with logging)
│   └── notifications.db        # SQLite database (local dev)
├── maintenance/
│   ├── Dockerfile
│   ├── websocket_api.py        # WebSocket-enabled maintenance API
│   ├── enhanced_model.py       # AI model for ticket classification
│   ├── websocket_frontend.html # Real-time WebSocket UI
│   └── requirements_websocket.txt
├── shared/                     # Shared infrastructure (new)
│   ├── __init__.py
│   ├── config.py               # Environment configuration
│   ├── database.py             # Connection pooling
│   ├── http_client.py          # Retry logic & circuit breaker
│   └── requirements.txt
├── scripts/
│   └── migrate_to_postgresql.py  # SQLite → PostgreSQL migration
├── .env.example                # Environment variable template
├── .gitignore
├── docker-compose.yml          # Docker orchestration
├── init-db-postgres.sql        # PostgreSQL schema initialization
├── start_all.sh                # Local startup script (SQLite mode)
└── README.md                   # This file
```

### Local Development Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Start services manually (each in separate terminal)
cd gateway && python main.py          # Port 5001
cd user-management && python app.py   # Port 8002
cd booking && python main.py          # Port 8001
cd gpa-calculator && python main.py   # Port 8003
cd notification && python app.py      # Port 8004
cd maintenance && python websocket_api.py  # Port 8080

# OR use start_all.sh (starts all in background)
bash start_all.sh

# 3. View logs
tail -f /tmp/gateway.log
tail -f /tmp/booking.log
tail -f /tmp/usermgmt.log
tail -f /tmp/gpa.log
tail -f /tmp/notification.log
tail -f /tmp/maintenance.log

# 4. Stop services
pkill -f "gateway/main.py"
pkill -f "booking/main.py"
pkill -f "user-management/app.py"
pkill -f "gpa-calculator/main.py"
pkill -f "notification/app.py"
pkill -f "maintenance/websocket_api.py"
```

### Adding a New Service

1. **Create service directory**: `mkdir new-service`
2. **Create main file**: `new-service/main.py`
3. **Add JWT validation**:
   ```python
   import jwt
   SECRET_KEY = 'your-secret-key-change-in-production'
   
   def verify_jwt(token):
       try:
           return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
       except:
           return None
   ```
4. **Add health endpoint**:
   ```python
   @app.route('/health')
   def health():
       return jsonify({"status": "healthy"})
   ```
5. **Create Dockerfile**: See existing services for template
6. **Update `docker-compose.yml`**: Add new service definition
7. **Update gateway routing** (if needed): Add proxy routes in `gateway/main.py`
8. **Add to `start_all.sh`**: Include startup command
9. **Update this README**: Document new service

### Code Quality Tools

```bash
# Install dev dependencies
pip install flake8 black isort pytest

# Format code
black . --exclude venv
isort . --skip venv

# Lint code
flake8 . --exclude=venv --max-line-length=100

# Run tests (if tests exist)
pytest tests/
```

---

## API Documentation

### Authentication Flow

1. **Login**: POST `/auth/login` with email/password
2. **Receive JWT**: Response includes token with 24-hour expiry
3. **Store Token**: Frontend stores in localStorage
4. **Authorize Requests**: Include in header: `Authorization: Bearer <token>`
5. **JWT Validation**: Each service validates token independently
6. **Token Expiry**: After 24 hours, user must login again

### Example API Calls

**Login**:
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"student123"}'

# Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "3",
    "email": "student@example.com",
    "name": "Student User",
    "role": "student"
  }
}
```

**Get Current User**:
```bash
curl http://localhost:5001/auth/me \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**List Rooms**:
```bash
curl http://localhost:5001/api/booking/rooms \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Create Booking**:
```bash
curl -X POST http://localhost:5001/api/booking/bookings \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "date": "2025-12-20",
    "time_slot": "10:00 AM - 11:00 AM"
  }'
```

**Calculate GPA**:
```bash
curl -X POST http://localhost:5001/api/gpa/calculate \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "courses": [
      {"grade": "A", "credits": 3},
      {"grade": "B", "credits": 4},
      {"grade": "A", "credits": 3}
    ]
  }'

# Response: {"gpa": 3.7, "total_credits": 10}
```

**Create Maintenance Ticket**:
```bash
curl -X POST http://localhost:5001/api/maintenance/tickets \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Broken projector in Lecture Hall B",
    "description": "The projector is not turning on"
  }'

# Response includes AI-generated category and priority
```

### Interactive API Docs

FastAPI provides auto-generated interactive documentation:

**Booking Service Swagger UI**: http://localhost:8001/docs

Features:
- Try out API endpoints directly in browser
- See request/response schemas
- Authentication support
- No additional configuration needed

---

## CI/CD Pipeline

### GitHub Actions Workflow

Location: `.github/workflows/ci-cd.yml`

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs**:

1. **Lint & Code Quality**
   - Black formatter check
   - isort import sorting check
   - Flake8 linting (critical errors only)

2. **Test Services**
   - Python 3.11 environment
   - Install all dependencies
   - Run pytest (unit + integration tests)
   - Generate coverage report

3. **Build Docker Images**
   - Build all 6 service images
   - Tag with commit SHA
   - Push to Docker Hub (on main branch only)
   - Images: `<username>/campus-gateway`, `<username>/campus-booking`, etc.

4. **Security Scan**
   - Scan Docker images for vulnerabilities
   - Check dependencies for known CVEs

**View Pipeline**: https://github.com/reivfts/end-to-end-MLOPs/actions

---

## Testing

### Manual Testing

**Health Checks**:
```bash
# Test all service health endpoints
for port in 5001 8001 8002 8003 8004 8080; do
  echo "Testing port $port..."
  curl http://localhost:$port/health
done
```

**Authentication Test**:
```bash
# 1. Login and capture token
TOKEN=$(curl -s -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"student123"}' \
  | jq -r '.token')

echo "Token: $TOKEN"

# 2. Test authenticated endpoint
curl http://localhost:5001/api/booking/rooms \
  -H "Authorization: Bearer $TOKEN"
```

**Database Connection Test**:
```bash
# PostgreSQL
docker-compose exec postgres psql -U postgres -d campus_services \
  -c "SELECT count(*) FROM users;"

# SQLite (local)
sqlite3 gateway/gateway.db "SELECT count(*) FROM users;"
```

### Automated Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_gateway.py

# Run tests matching pattern
pytest -k "test_auth"
```

### Load Testing

```bash
# Install Apache Bench
# macOS: brew install httpd
# Ubuntu: sudo apt-get install apache2-utils

# Test login endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 -p login.json -T application/json \
  http://localhost:5001/auth/login

# Where login.json contains:
# {"email":"student@example.com","password":"student123"}
```

### Correlation ID Testing

```bash
# Make a request and check logs
curl http://localhost:5001/api/booking/rooms \
  -H "Authorization: Bearer <TOKEN>"

# View correlation ID in logs
tail -f /tmp/gateway.log | grep "correlation_id"
tail -f /tmp/booking.log | grep "correlation_id"

# Should see same correlation ID across both services for one request
```

---

## Troubleshooting

### Services Won't Start

**Problem**: Port already in use
```bash
# Find process using port
lsof -i :5001

# Kill process
kill -9 <PID>

# Or kill all Python services
pkill -f "main.py"
pkill -f "app.py"
pkill -f "websocket_api.py"
```

**Problem**: Module not found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r shared/requirements.txt
pip install -r booking/requirements.txt
pip install -r user-management/requirements.txt
pip install -r maintenance/requirements_websocket.txt
```

### Database Errors

**Problem**: SQLite database locked
```bash
# Database might be in use by another process
# Solution: Close other connections or restart service
pkill -f "gateway/main.py"
python gateway/main.py
```

**Problem**: PostgreSQL connection refused
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres

# Verify connection
psql -h localhost -U postgres -d campus_services
```

**Problem**: Tables don't exist
```bash
# Reinitialize PostgreSQL
docker-compose down -v  # CAUTION: Deletes all data
docker-compose up -d postgres

# Or manually run init script
psql -h localhost -U postgres -d campus_services -f init-db-postgres.sql
```

### JWT Authentication Errors

**Problem**: "Invalid token" or "Token expired"
```bash
# Check JWT_SECRET_KEY matches across services
grep JWT_SECRET_KEY .env

# Verify token is valid (decode without verification)
python -c "import jwt, sys; print(jwt.decode(sys.argv[1], options={'verify_signature': False}))" <TOKEN>

# Token expires after 24 hours - login again
```

**Problem**: 403 Forbidden (wrong role)
```bash
# Check user role
curl http://localhost:5001/auth/me \
  -H "Authorization: Bearer <TOKEN>"

# Admin endpoints require admin role
# Student endpoints require student/faculty role
```

### Docker Issues

**Problem**: Container keeps restarting
```bash
# View container logs
docker-compose logs -f gateway

# Check for port conflicts
docker-compose ps
lsof -i :5001

# Rebuild and restart
docker-compose up --build --force-recreate gateway
```

**Problem**: PostgreSQL data persists when it shouldn't
```bash
# Remove volumes and restart
docker-compose down -v
docker-compose up -d
```

**Problem**: Out of disk space
```bash
# Clean up Docker
docker system df  # View disk usage
docker system prune -a  # Remove unused data
docker volume prune  # Remove unused volumes
```

### Logging Issues

**Problem**: No logs appearing
```bash
# Check log files exist
ls -la /tmp/*.log

# Verify logging is configured
grep "logging.basicConfig" gateway/main.py

# Check file permissions
chmod 666 /tmp/*.log

# View logs in real-time
tail -f /tmp/gateway.log
```

**Problem**: Correlation IDs not working
```bash
# Verify correlation_id in logs
grep correlation_id /tmp/gateway.log

# Check before_request middleware is running
curl http://localhost:5001/health
tail -1 /tmp/gateway.log  # Should show correlation_id
```

### Performance Issues

**Problem**: Slow API responses
```bash
# Check connection pool status (PostgreSQL)
docker-compose exec postgres psql -U postgres -d campus_services \
  -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# Monitor database queries
docker-compose exec postgres psql -U postgres -d campus_services \
  -c "SELECT query, query_start FROM pg_stat_activity WHERE state = 'active';"

# Check for long-running transactions
docker-compose exec postgres psql -U postgres -d campus_services \
  -c "SELECT * FROM pg_stat_activity WHERE state != 'idle' AND query_start < now() - interval '1 minute';"
```

**Problem**: High memory usage
```bash
# Check Docker resource usage
docker stats

# Restart services
docker-compose restart

# Check for connection leaks
grep "connection" /tmp/*.log | grep -i "error"
```

### AI Model Issues (Maintenance Service)

**Problem**: Model fails to load
```bash
# Check transformers library installed
pip show transformers

# Download model manually
python -c "from transformers import AutoModel; AutoModel.from_pretrained('distilbert-base-uncased')"

# Check disk space (model is ~250MB)
df -h
```

**Problem**: Slow ticket classification
```bash
# Normal inference time: ~200ms
# If slower, check CPU usage
top -p $(pgrep -f websocket_api)

# Consider using GPU if available (requires PyTorch GPU support)
```

### Getting Help

**Check logs first**:
```bash
tail -100 /tmp/gateway.log
tail -100 /tmp/booking.log
# ... check all service logs
```

**Enable debug mode**:
```bash
# In .env
FLASK_DEBUG=1
FLASK_ENV=development

# Restart services
bash start_all.sh
```

**Report issues**:
- GitHub Issues: https://github.com/reivfts/end-to-end-MLOPs/issues
- Include: Error message, logs, steps to reproduce

---

## System Status

| Service | Port | Status | Auth | Database | Framework | Features |
|---------|------|--------|------|----------|-----------|----------|
| Gateway | 5001 | ✅ Ready | JWT | SQLite/PostgreSQL | Flask | Auth, Routing, Static Files, Logging |
| User Mgmt | 8002 | ✅ Ready | JWT | SQLite/PostgreSQL | Flask | CRUD, RBAC, Notifications, Logging |
| Booking | 8001 | ✅ Ready | JWT | SQLite/PostgreSQL | FastAPI | Async, Swagger Docs, Logging |
| GPA Calc | 8003 | ✅ Ready | JWT | None | Flask | Stateless, Logging |
| Notification | 8004 | ✅ Ready | JWT | SQLite/PostgreSQL | Flask | Events, History, Logging |
| Maintenance | 8080 | ✅ Ready | JWT+WS | In-Memory | Flask-SocketIO | AI, WebSocket, Real-time, Logging |

**Shared Infrastructure**: ✅ Connection pooling, retry logic, circuit breaker, correlation IDs

**CI/CD**: ✅ GitHub Actions (lint, test, build, security scan)

**Deployment**: ✅ Docker Compose, PostgreSQL 15, health checks

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add amazing feature"`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open Pull Request with detailed description

**Code Standards**:
- Follow PEP 8 style guide
- Add docstrings to functions
- Include type hints where applicable
- Write unit tests for new features
- Update README for new functionality

---

## License

MIT License - See LICENSE file for details.

---

## Acknowledgments

- **FastAPI** - Modern async web framework
- **Flask** - Lightweight WSGI framework
- **PostgreSQL** - Robust relational database
- **HuggingFace Transformers** - Pre-trained NLP models
- **Docker** - Containerization platform
- **GitHub Actions** - CI/CD automation

---

## Contact

**Repository**: https://github.com/reivfts/end-to-end-MLOPs  
**Author**: reivfts  
**Last Updated**: December 15, 2025  
**Version**: 3.0 - Production Ready with Database Abstraction & Comprehensive Logging

---

**🚀 Campus Services Hub is production-ready with full microservices architecture, PostgreSQL support, correlation IDs, and CI/CD pipeline!**
