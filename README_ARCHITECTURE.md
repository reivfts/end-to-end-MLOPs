# CloudMLOPS - 6 Microservices Architecture

Production-ready microservices system with JWT authentication and role-based access control.

## 🏗️ Architecture

```
                    ┌─────────────────────────┐
                    │   Gateway Hub (5001)    │
                    │  JWT Auth + Routing     │
                    └───────────┬─────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
           ADMIN ROLE      FACULTY ROLE    STUDENT ROLE
                │               │               │
                ▼               ▼               ▼
        ┌──────────────┐  ┌────────────────────────────┐
        │ User Mgmt    │  │   Booking (8001)           │
        │ (8002)       │  │   GPA Calculator (8003)    │
        │ RBAC Only    │  │   Notifications (8004)     │
        └──────────────┘  │   Maintenance (8080)       │
                          └────────────────────────────┘
```

## 🎯 Services

### 1. **Gateway Hub** (Port 5001)
- **Tech**: Flask + JWT
- **Purpose**: Central authentication and role-based routing
- **Features**:
  - JWT token generation and validation
  - Role-based access control (Admin/Faculty/Student)
  - Proxy routing to backend services
  - User database (SQLite)

**Role Access:**
- **Admin**: `/api/users/*` (User Management only)
- **Faculty/Student**: `/api/booking/*`, `/api/gpa/*`, `/api/notifications/*`, `/api/maintenance/*`

### 2. **Booking Service** (Port 8001)
- **Tech**: FastAPI + SQLite
- **Purpose**: Room booking with time slot management
- **Features**:
  - 8 time slots per day (6 AM - 10 PM, 2-hour blocks)
  - 4 conference rooms
  - Double-booking prevention
  - RBAC: Faculty can cancel any booking, Students can cancel own only

**Endpoints:**
- `GET /rooms` - List available rooms
- `GET /slots` - List 8 time slots
- `POST /bookings` - Create booking
- `GET /bookings` - List bookings (filtered by role)
- `DELETE /bookings/{id}` - Cancel booking
- `GET /my-bookings` - Get user's bookings

### 3. **User Management** (Port 8002)
- **Tech**: Flask + SQLite
- **Purpose**: User CRUD operations (Admin only)
- **Features**:
  - Create, Read, Update, Delete users
  - Role management (admin/faculty/student)
  - User search by role

**Endpoints:**
- `GET /users` - List all users (admin only)
- `POST /users` - Create user (admin only)
- `GET /users/{id}` - Get user details
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user (admin only)
- `GET /users/by-role/{role}` - Filter by role

### 4. **GPA Calculator** (Port 8003)
- **Tech**: Flask
- **Purpose**: Weighted GPA calculation
- **Features**:
  - Stateless calculation
  - GPA range: 0.0 - 4.0
  - Weight range: 1 - 3
  - Formula: Σ(gpa × weight) / Σ(weight)

**Endpoints:**
- `POST /calculate` - Calculate weighted GPA

**Request:**
```json
{
  "classes": [
    {"gpa": 3.7, "weight": 3},
    {"gpa": 4.0, "weight": 3}
  ]
}
```

### 5. **Notification Service** (Port 8004)
- **Tech**: Flask + SQLite
- **Purpose**: Event logging and notification history
- **Features**:
  - Create notifications for users
  - Mark as read/unread
  - Get unread count
  - Admin sees all, users see own

**Endpoints:**
- `POST /notifications` - Create notification
- `GET /notifications` - List notifications
- `PUT /notifications/{id}/read` - Mark as read
- `GET /notifications/unread` - Get unread count

### 6. **Maintenance Service** (Port 8080)
- **Tech**: Flask + WebSocket + NLP
- **Purpose**: Maintenance ticketing with priority analysis
- **Features**:
  - NLP-powered priority detection
  - Real-time WebSocket updates
  - Admin dashboard for ticket management
  - Priority levels: Low, Medium, High, Critical

**Access:**
- WebSocket Dashboard: `http://localhost:8080/websocket_frontend.html`

## 🔐 Authentication & Authorization

### Default Users

| Email | Password | Role | Access |
|-------|----------|------|--------|
| admin@example.com | admin123 | admin | User Management only |
| faculty@example.com | faculty123 | faculty | Booking, GPA, Notifications, Maintenance |
| student@example.com | student123 | student | Booking, GPA, Notifications, Maintenance |

### JWT Token Flow

1. **Login**: `POST /auth/login` → Returns JWT token
2. **Use Token**: Include in header: `Authorization: Bearer <token>`
3. **Gateway validates**: Checks role and routes to appropriate service
4. **Backend services**: Also validate JWT for security

### Role-Based Access Control

```python
# Admin Access
GET /api/users              # ✅ Allowed
GET /api/booking/rooms      # ❌ Forbidden

# Faculty/Student Access  
GET /api/users              # ❌ Forbidden
GET /api/booking/rooms      # ✅ Allowed
POST /api/gpa/calculate     # ✅ Allowed
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install packages
pip install Flask Flask-CORS fastapi uvicorn PyJWT requests flask-socketio nltk scikit-learn
```

### 2. Start All Services

```bash
./start_all.sh
```

Or manually:

```bash
# Gateway (must start first)
cd gateway && python main.py &

# Booking
cd booking && python main.py &

# GPA Calculator
cd gpa-calculator && python main.py &

# User Management
cd user-management && python app.py &

# Notifications
cd notification && python app.py &

# Maintenance
cd maintenance && python websocket_api.py &
```

### 3. Open Dashboard

```bash
open index.html
```

## 📡 API Examples

### Login

```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"faculty@example.com","password":"faculty123"}'
```

**Response:**
```json
{
  "accessToken": "eyJhbGci...",
  "user": {
    "id": "...",
    "email": "faculty@example.com",
    "role": "faculty"
  }
}
```

### Create Booking (via Gateway)

```bash
TOKEN="your_jwt_token"

curl -X POST http://localhost:5001/api/booking/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "date": "2025-12-15",
    "time_slot": "10:00-12:00"
  }'
```

### Calculate GPA (via Gateway)

```bash
curl -X POST http://localhost:5001/api/gpa/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "classes": [
      {"gpa": 3.7, "weight": 3},
      {"gpa": 4.0, "weight": 3}
    ]
  }'
```

### Get Users (Admin only, via Gateway)

```bash
ADMIN_TOKEN="admin_jwt_token"

curl http://localhost:5001/api/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## 🗂️ Database Schema

### Gateway Database (`gateway.db`)

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'faculty', 'student')),
    created_at TEXT NOT NULL
);
```

### Booking Database (`bookings.db`)

```sql
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    capacity INTEGER
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    user_email TEXT NOT NULL,
    date TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    status TEXT CHECK(status IN ('active', 'cancelled')),
    created_at TEXT NOT NULL,
    UNIQUE(room_id, date, time_slot, status)
);
```

## 🛠️ Development

### Port Allocation

| Service | Port | Protocol |
|---------|------|----------|
| Gateway Hub | 5001 | HTTP/REST |
| Booking | 8001 | HTTP/REST |
| User Management | 8002 | HTTP/REST |
| GPA Calculator | 8003 | HTTP/REST |
| Notifications | 8004 | HTTP/REST |
| Maintenance | 8080 | HTTP/WebSocket |

### Logs

```bash
# View all logs
tail -f /tmp/gateway.log
tail -f /tmp/booking.log
tail -f /tmp/gpa.log
tail -f /tmp/usermgmt.log
tail -f /tmp/notification.log
tail -f /tmp/maintenance.log
```

### Stop All Services

```bash
pkill -f 'venv/bin/python'
```

## 🔒 Security Notes

1. **JWT Secret**: Change `SECRET_KEY` in production
2. **Password Hashing**: Currently plain text - use bcrypt in production
3. **HTTPS**: Use reverse proxy (nginx) with SSL in production
4. **CORS**: Currently allows all origins - restrict in production
5. **Rate Limiting**: Add rate limiting for production
6. **Input Validation**: All services validate inputs

## 📦 AWS Deployment

### Recommended Architecture

```
┌─────────────────┐
│   API Gateway   │ (AWS API Gateway or ALB)
└────────┬────────┘
         │
    ┌────┴────┐
    │   ECS   │ (6 containers, one per service)
    └────┬────┘
         │
    ┌────┴────┐
    │   RDS   │ (PostgreSQL - optional, currently SQLite)
    └─────────┘
```

### Docker Compose (Included)

```bash
docker-compose up -d
```

## 🎨 Frontend Integration

Access services through Gateway Hub only:

```javascript
// Login
const response = await fetch('http://localhost:5001/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email, password})
});

const {accessToken, user} = await response.json();

// Use token for all requests
const bookings = await fetch('http://localhost:5001/api/booking/bookings', {
  headers: {'Authorization': `Bearer ${accessToken}`}
});
```

## 📝 License

MIT License

## 👥 Contributors

CloudMLOPS Team - End-to-End MLOps Project
