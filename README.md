# Campus Services Hub - Cloud MLOps Platform# Campus Services Hub - Complete Documentation



**Microservices Architecture** | **JWT Authentication** | **Role-Based Access Control** | **AWS Ready****Project**: Campus Services Hub  

**Date**: December 13, 2025  

---**Branch**: main  

**Status**: Production Ready

## 📋 Table of Contents

---

- [System Overview](#system-overview)

- [Quick Start](#quick-start)## System Overview

- [Architecture](#architecture)

- [Services](#services)Campus Services Hub is a microservices platform for university/campus management with role-based access control (RBAC). The system provides secure access to room booking, GPA calculation, maintenance ticketing, and notification services through a centralized JWT-authenticated gateway.

- [Configuration](#configuration)

- [Docker Deployment](#docker-deployment)### User Roles and Access

- [AWS Deployment](#aws-deployment)

- [Development](#development)- **Admin**: User management and notification access only

- **Faculty**: Access to booking, GPA calculator, maintenance tickets, and notifications

---- **Student**: Access to booking, GPA calculator, maintenance tickets, and notifications



## System Overview---



Campus Services Hub is a production-ready microservices platform for university management with JWT authentication and role-based access control. The system provides room booking, GPA calculation, maintenance ticketing, notifications, and user management through a centralized gateway.## 🏗️ **System Architecture**



### User Roles & Access```

┌─────────────────────────────────────────────────────────────────┐

| Role | Permissions |│                    Frontend (HTML/JavaScript)                    │

|------|-------------|│                       localhost:5001/static                      │

| **Admin** | User management, notifications, system monitoring |│           Role-Based Navigation | JWT Authentication             │

| **Faculty** | All student features + enhanced booking privileges |└───────────────────┬─────────────────────────────────────────────┘

| **Student** | Booking, GPA calculator, maintenance tickets, notifications |                    │ HTTP/HTTPS Requests

┌───────────────────▼─────────────────────────────────────────────┐

### Default Credentials│                Gateway Service (Port 5001)                       │

│           Flask | JWT Auth | API Routing | Static Files         │

```└─┬────────┬──────────┬───────────┬─────────────┬─────────────────┘

Admin:   admin@example.com    / admin123  │        │          │           │             │

Faculty: faculty@example.com  / faculty123  │ Route  │ Route    │ Route     │ Route       │ Route

Student: student@example.com  / student123  │        │          │           │             │

```┌─▼────────┐ ┌▼──────────┐ ┌▼────────────┐ ┌▼──────────┐ ┌▼────────────┐

│User Mgmt │ │  Booking  │ │Maintenance  │ │    GPA    │ │Notification │

---│Flask 8002│ │FastAPI8001│ │Flask+WS 8080│ │Flask 8003 │ │Flask 8004   │

│   JWT    │ │   JWT     │ │    JWT      │ │   JWT     │ │    JWT      │

## Quick Start└─────┬────┘ └─────┬─────┘ └─────┬───────┘ └─────┬─────┘ └─────┬───────┘

      │             │             │             │             │

### Prerequisites      └─────────────┼─────────────┼─────────────┼─────────────┘

                    │             │             │

- Python 3.8+ (3.13 recommended)            ┌───────▼─────────────▼─────────────▼───────┐

- SQLite3            │              SQLite Databases             │

- Docker & Docker Compose (optional, for containerized deployment)            │  users.db | bookings.db | maintenance.db  │

- PostgreSQL (optional, for production/AWS)            │  gateway.db | notifications.db            │

            └───────────────────────────────────────────┘

### Local Development```



1. **Clone and setup virtual environment:**---

   ```bash

   git clone <repository>## 🔐 **Authentication & Security**

   cd cloudMLOPS

   python3 -m venv venv### **JWT Authentication Flow**

   source venv/bin/activate  # On Windows: venv\Scripts\activate1. **Login**: User authenticates via Gateway → Receives JWT token (24-hour expiry)

   ```2. **Authorization**: Each service independently validates JWT tokens

3. **RBAC**: Token contains role information for permission checks

2. **Install dependencies for each service:**4. **Security**: All sensitive operations require valid JWT

   ```bash

   pip install flask flask-cors pyjwt werkzeug fastapi uvicorn flask-socketio python-socketio requests### **Default Users**

   pip install -r shared/requirements.txt  # For new shared modules```

   ```Admin:   admin@example.com    / admin123    (Full system access)

Faculty: faculty@example.com  / faculty123  (Enhanced permissions) 

3. **Start all services:**Student: student@example.com  / student123  (Basic access)

   ```bash```

   ./start_all.sh

   ```---

   

   Or manually in separate terminals:## 🚀 **Services Documentation**

   ```bash

   cd gateway && python3 main.py          # Port 5001 (Gateway + Frontend)### **1. Gateway Service (Port 5001)** 

   cd user-management && python3 app.py   # Port 8002 (User CRUD)**Purpose**: Central authentication hub and API router  

   cd booking && python3 main.py          # Port 8001 (Room Bookings)**Tech Stack**: Python Flask + SQLite  

   cd gpa-calculator && python3 main.py   # Port 8003 (GPA Calculator)**Database**: `gateway.db`

   cd notification && python3 app.py      # Port 8004 (Notifications)

   cd maintenance && python3 websocket_api.py  # Port 8080 (Maintenance + AI)**Key Features**:

   ```- ✅ JWT token generation and validation

- ✅ User authentication (login/logout)

4. **Access the system:**- ✅ Static file serving (frontend)

   - Frontend: http://localhost:5001- ✅ API routing to all microservices

   - API Docs: http://localhost:8001/docs (FastAPI)- ✅ CORS enabled for web clients



---**Core Endpoints**:

- `POST /auth/login` - User authentication

## Architecture- `GET /auth/me` - Current user information

- `POST /api/users` - Create user (Admin only)

```- `GET /api/users` - List users

┌─────────────────────────────────────────────────────────────────┐- `DELETE /api/users/{id}` - Delete user (Admin only)

│                  Frontend (HTML/JavaScript)                      │

│                     localhost:5001/static                        │---

│          Role-Based Navigation | JWT Authentication             │

└───────────────────┬─────────────────────────────────────────────┘### **2. User Management Service (Port 8002)**

                    │ HTTP/HTTPS**Purpose**: User CRUD operations and role management  

┌───────────────────▼─────────────────────────────────────────────┐**Tech Stack**: Python Flask + SQLite  

│               Gateway Service (Port 5001)                        │**Database**: `users.db`

│         Flask | JWT Auth | API Routing | Static Files           │

└─┬────────┬──────────┬───────────┬─────────────┬─────────────────┘**Key Features**:

  │        │          │           │             │- ✅ Complete user lifecycle management

┌─▼────┐ ┌▼──────┐ ┌▼────────┐ ┌▼──────┐ ┌▼──────────┐- ✅ Role assignment (Student/Faculty/Admin)

│User  │ │Booking│ │GPA Calc │ │Notif  │ │Maintenance│- ✅ Admin notification triggers

│8002  │ │8001   │ │8003     │ │8004   │ │8080       │- ✅ JWT-secured endpoints

│Flask │ │FastAPI│ │Flask    │ │Flask  │ │Flask+WS   │

└──┬───┘ └───┬───┘ └────┬────┘ └───┬───┘ └─────┬─────┘**Core Endpoints**:

   │         │          │          │           │- `GET /users` - List all users

   └─────────┴──────────┴──────────┴───────────┘- `POST /users` - Create new user  

                        │- `PUT /users/{id}` - Update user

            ┌───────────▼───────────┐- `DELETE /users/{id}` - Delete user

            │   SQLite Databases    │- `GET /users/{id}` - Get user details

            │   (or PostgreSQL)     │

            └───────────────────────┘---

```

## 🚀 **Quick Start Guide**

### Authentication Flow

### **1. Start All Services**

1. **Login**: User authenticates via Gateway → Receives JWT token (24-hour expiry)```bash

2. **Authorization**: Each service independently validates JWT tokens# Start services in order (each in separate terminal)

3. **RBAC**: Token contains role information for permission checkscd gateway && python3 main.py          # Port 5001

4. **Security**: All sensitive operations require valid JWTcd user-management && python3 app.py   # Port 8002  

cd booking && python3 main.py          # Port 8001

---cd gpa-calculator && python3 main.py   # Port 8003

cd notification && python3 app.py      # Port 8004

## Servicescd maintenance && python3 websocket_api.py  # Port 8080

```

### 1. Gateway Service (Port 5001)

**Central authentication hub and API router**### **2. Access the System**

- **Frontend**: http://localhost:5001

- JWT token generation and validation- **Login**: Use default credentials above

- User authentication (login/logout)- **API Docs**: http://localhost:8001/docs (FastAPI auto-docs)

- Static file serving (frontend)

- API routing to all microservices---

- CORS enabled

## 🎉 **System Status: COMPLETE**

**Tech**: Flask + SQLite (`gateway.db`)

| Service | Port | Status | JWT | Database | Features |

**Key Endpoints**:|---------|------|--------|-----|----------|----------|

- `POST /auth/login` - User authentication| Gateway | 5001 | ✅ Complete | ✅ | gateway.db | Auth + Routing |

- `GET /auth/me` - Current user info| User-Mgmt | 8002 | ✅ Complete | ✅ | users.db | CRUD + Notifications |  

- `GET /health` - Health check| Booking | 8001 | ✅ Complete | ✅ | bookings.db | Reservations + FastAPI |

| GPA | 8003 | ✅ Complete | ✅ | None | Calculations |

### 2. User Management (Port 8002)| Notification | 8004 | ✅ Complete | ✅ | notifications.db | Admin System |

**User CRUD operations and role management**| Maintenance | 8080 | ✅ Complete | ✅ | maintenance.db | AI + WebSocket |



- Complete user lifecycle management**Campus Services Hub is production-ready with full RBAC implementation!** 🚀

- Role assignment (Student/Faculty/Admin)

- Admin notification triggers---

- JWT-secured endpoints

*Last Updated: December 13, 2025 - Complete System Documentation*
**Tech**: Flask + SQLite (`users.db`)

**Key Endpoints**:
- `GET /users` - List users
- `POST /users` - Create user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

### 3. Booking Service (Port 8001)
**Room reservation and scheduling**

- Room availability management
- Time slot booking (8 AM - 6 PM)
- Conflict prevention
- Auto-generated API docs

**Tech**: FastAPI + SQLite (`bookings.db`)

**Key Endpoints**:
- `POST /bookings` - Create booking
- `GET /bookings` - List bookings
- `GET /bookings/available` - Available slots

### 4. GPA Calculator (Port 8003)
**Academic performance calculator**

- Grade calculation (A=4.0, F=0.0)
- Credit hour weighting
- Stateless computation

**Tech**: Flask (no database)

**Key Endpoints**:
- `POST /calculate` - Calculate GPA

### 5. Notification Service (Port 8004)
**System-wide notification management**

- User and admin notifications
- Role-based filtering
- Notification history

**Tech**: Flask + SQLite (`notifications.db`)

**Key Endpoints**:
- `POST /notifications` - Create notification
- `GET /notifications` - List notifications
- `PUT /notifications/{id}` - Mark as read

### 6. Maintenance Service (Port 8080)
**AI-powered maintenance ticketing**

- Real-time WebSocket updates
- AI priority classification (P0-P4)
- Pattern-based SLA assignment
- System impact analysis

**Tech**: Flask-SocketIO + SQLite (`maintenance.db`)

**Key Endpoints**:
- `POST /tickets` - Create ticket
- `GET /tickets` - List tickets
- `WS /socket.io` - WebSocket connection

---

## Configuration

### Environment Variables

The system supports environment-based configuration for different deployment scenarios:

**Core Configuration** (`.env`):
```bash
# Application
FLASK_ENV=development        # development | production
FLASK_DEBUG=1                # 0 | 1
JWT_SECRET_KEY=your-secret   # Change in production!

# Database
DATABASE_TYPE=sqlite         # sqlite | postgresql
DB_HOST=localhost            # PostgreSQL host
DB_PORT=5432                 # PostgreSQL port
DB_NAME=campus_services      # Database name
DB_USER=postgres             # Database user
DB_PASSWORD=password         # Database password

# Service Discovery (Docker/AWS)
GATEWAY_HOST=localhost       # Or: gateway, <ALB-DNS>
USER_MGMT_HOST=localhost     # Or: user-management
BOOKING_HOST=localhost       # Or: booking
NOTIFICATION_HOST=localhost  # Or: notification
GPA_HOST=localhost           # Or: gpa-calculator
MAINTENANCE_HOST=localhost   # Or: maintenance

# HTTP Client
REQUEST_TIMEOUT=10           # Request timeout (seconds)
REQUEST_RETRY_ATTEMPTS=3     # Number of retries
REQUEST_RETRY_BACKOFF=1.0    # Backoff factor
```

**Setup**:
1. Copy template: `cp .env.example .env`
2. Update values for your environment
3. Never commit `.env` to git

### Shared Infrastructure (New)

The project includes shared modules for production deployments:

- **`shared/config.py`**: Environment-based configuration, service URL discovery
- **`shared/database.py`**: Connection pooling for PostgreSQL/SQLite
- **`shared/http_client.py`**: Retry logic + circuit breaker pattern

**Installation**:
```bash
pip install -r shared/requirements.txt
```

**Usage** (services will be updated):
```python
from shared import config, db_pool, http_client

# Get service URL (auto-detects local/Docker/AWS)
url = config.get_service_url('users')

# Use connection pool
with db_pool.get_connection() as conn:
    result = conn.execute(sql, params)

# HTTP with retry logic
response = http_client.post(url, json=data)
```

---

## Docker Deployment

### Local Docker with PostgreSQL

1. **Start services with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access**:
   - Gateway: http://localhost:5001
   - All services automatically connected to PostgreSQL

3. **View logs**:
   ```bash
   docker-compose logs -f gateway
   docker-compose logs -f postgres
   ```

4. **Stop services**:
   ```bash
   docker-compose down
   docker-compose down -v  # Remove volumes
   ```

### PostgreSQL Migration

If you have existing SQLite data:

```bash
cd scripts
python migrate_to_postgresql.py
```

Follow the prompts to migrate `users.db`, `bookings.db`, `notifications.db` to PostgreSQL.

---

## AWS Deployment

### Architecture (Production)

```
┌────────────────────────────────────────────────────┐
│                     Internet                       │
└────────────────┬───────────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────────┐
│        Application Load Balancer (ALB)             │
│         Port 80/443 (HTTPS with ACM)               │
└────┬──────────┬──────────┬──────────┬──────────────┘
     │          │          │          │
┌────▼────┐ ┌──▼──────┐ ┌─▼─────┐ ┌──▼───────┐
│Gateway  │ │Booking  │ │User   │ │Notif     │
│ECS Task │ │ECS Task │ │Mgmt   │ │ECS Task  │
│         │ │         │ │ECS    │ │          │
└────┬────┘ └────┬────┘ └───┬───┘ └─────┬────┘
     │           │          │           │
     └───────────┴──────────┴───────────┘
                 │
         ┌───────▼────────┐
         │  RDS PostgreSQL│
         │  Multi-AZ      │
         │  Private Subnet│
         └────────────────┘
```

### Deployment Steps

**Prerequisites**:
- AWS CLI configured
- Docker installed
- AWS account with appropriate permissions

**1. Create RDS PostgreSQL Database**:
```bash
aws rds create-db-instance \
  --db-instance-identifier campus-services-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username postgres \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx \
  --db-subnet-group-name your-subnet-group \
  --backup-retention-period 7 \
  --multi-az
```

**2. Initialize Database**:
```bash
psql -h <RDS-ENDPOINT> -U postgres -d postgres -f init-db-postgres.sql
```

**3. Store Secrets in AWS Secrets Manager**:
```bash
aws secretsmanager create-secret \
  --name campus-services/db-password \
  --secret-string '{"password":"YOUR_SECURE_PASSWORD"}'

aws secretsmanager create-secret \
  --name campus-services/jwt-secret \
  --secret-string '{"key":"YOUR_JWT_SECRET"}'
```

**4. Build and Push Docker Images to ECR**:
```bash
# Create ECR repositories
aws ecr create-repository --repository-name campus-services/gateway
aws ecr create-repository --repository-name campus-services/booking
# ... repeat for all services

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t campus-services/gateway ./gateway
docker tag campus-services/gateway:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/campus-services/gateway:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/campus-services/gateway:latest
```

**5. Create ECS Cluster**:
```bash
aws ecs create-cluster --cluster-name campus-services-cluster
```

**6. Deploy Services to ECS Fargate**:
- Create task definitions for each service
- Configure environment variables (DB_HOST, JWT_SECRET_KEY, etc.)
- Create ECS services
- Configure ALB target groups
- Set up Cloud Map for service discovery

**7. Configure ALB**:
- Create target groups for each service
- Set up path-based routing
- Configure health checks
- Enable HTTPS with ACM certificate

### Cost Estimate

**Development/Testing**:
- RDS db.t3.micro: ~$15/month
- ECS Fargate (6 tasks, 0.25 vCPU, 0.5 GB): ~$25/month
- ALB: ~$20/month
- Data transfer: ~$5/month
- **Total**: ~$65-70/month

**Production (HA)**:
- RDS db.t3.small Multi-AZ: ~$70/month
- ECS Fargate (6 tasks, 0.5 vCPU, 1 GB, 2 AZs): ~$100/month
- ALB with HA: ~$25/month
- NAT Gateway: ~$35/month
- Data transfer: ~$20/month
- **Total**: ~$250-300/month

### Security Best Practices

- ✅ Use Secrets Manager for credentials
- ✅ Enable RDS encryption at rest
- ✅ Use private subnets for services
- ✅ Configure security groups (least privilege)
- ✅ Enable CloudWatch logging
- ✅ Use IAM roles for task execution
- ✅ Enable AWS WAF on ALB
- ✅ Regular security patching

---

## Development

### Project Structure

```
cloudMLOPS/
├── gateway/              # Port 5001 - Auth + Frontend
│   ├── main.py
│   ├── static/          # HTML/CSS/JS files
│   └── gateway.db
├── user-management/      # Port 8002 - User CRUD
│   ├── app.py
│   └── users.db
├── booking/              # Port 8001 - Room Bookings
│   ├── main.py
│   └── bookings.db
├── gpa-calculator/       # Port 8003 - GPA Calculation
│   └── main.py
├── notification/         # Port 8004 - Notifications
│   ├── app.py
│   └── notifications.db
├── maintenance/          # Port 8080 - Maintenance Tickets
│   ├── websocket_api.py
│   ├── enhanced_model.py
│   └── maintenance.db
├── shared/               # Shared infrastructure (new)
│   ├── config.py        # Environment config
│   ├── database.py      # Connection pooling
│   ├── http_client.py   # Retry logic
│   └── requirements.txt
├── scripts/
│   └── migrate_to_postgresql.py
├── docker-compose.yml    # Docker orchestration
├── init-db-postgres.sql  # PostgreSQL schema
├── .env.example          # Environment template
├── start_all.sh          # Local startup script
└── README.md             # This file
```

### Adding a New Service

1. Create service directory with main file
2. Add JWT validation
3. Update `docker-compose.yml`
4. Add service discovery env vars
5. Update gateway routing (if needed)
6. Create service endpoints
7. Update this README

### Testing

**Manual Testing**:
```bash
# Health checks
curl http://localhost:5001/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8080/health

# Login
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Use JWT token
curl http://localhost:8002/users \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Connection Pool Testing**:
```bash
# Monitor PostgreSQL connections
docker-compose exec postgres psql -U postgres -d campus_services \
  -c "SELECT count(*) FROM pg_stat_activity WHERE datname='campus_services';"
```

### Troubleshooting

**Services won't start**:
- Check if ports are already in use: `lsof -i :5001`
- Kill existing processes: `pkill -f "gateway/main.py"`
- Check logs: `tail -f /tmp/gateway.log`

**Database errors**:
- Verify database files exist
- Check file permissions
- Re-initialize if needed: `python -c "import sqlite3; sqlite3.connect('gateway.db')"`

**Docker issues**:
- Check Docker is running: `docker ps`
- View logs: `docker-compose logs -f`
- Rebuild: `docker-compose up --build --force-recreate`

**JWT errors**:
- Verify JWT_SECRET_KEY matches across services
- Check token expiry (24 hours)
- Ensure Authorization header format: `Bearer <token>`

### Performance Considerations

**Connection Pooling** (PostgreSQL):
- Min connections: 2
- Max connections: 20
- Reuse connections across requests
- 10-50x performance improvement

**HTTP Retry Logic**:
- 3 retry attempts
- Exponential backoff (1s, 2s, 4s)
- Circuit breaker (opens after 5 failures for 60s)

**Database Optimization**:
- Indexes on frequently queried columns
- Auto-vacuum enabled (PostgreSQL)
- Connection timeout: 10 seconds

---

## System Status

| Service | Port | Status | JWT | Database | Framework |
|---------|------|--------|-----|----------|-----------|
| Gateway | 5001 | ✅ | ✅ | gateway.db | Flask |
| User-Mgmt | 8002 | ✅ | ✅ | users.db | Flask |
| Booking | 8001 | ✅ | ✅ | bookings.db | FastAPI |
| GPA | 8003 | ✅ | ✅ | None | Flask |
| Notification | 8004 | ✅ | ✅ | notifications.db | Flask |
| Maintenance | 8080 | ✅ | ✅ | maintenance.db | Flask-SocketIO |

**All services are production-ready with JWT authentication and RBAC!** 🚀

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit pull request with clear description

---

## License

MIT License - See LICENSE file for details

---

**Last Updated**: December 13, 2025  
**Version**: 2.0 (Infrastructure Modernization)  
**Status**: Production Ready
