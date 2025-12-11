# 🎉 CloudMLOPS - System Ready!

## ✅ All 6 Microservices Running

```
✅ Gateway Hub (5001)       - JWT Auth + Role-Based Routing
✅ Booking Service (8001)   - Room booking with 8 time slots
✅ User Management (8002)   - User CRUD (Admin only)
✅ GPA Calculator (8003)    - Weighted GPA calculation  
✅ Notifications (8004)     - Event logging & notifications
✅ Maintenance (8080)       - NLP ticketing + WebSocket
```

## 🔐 Login Credentials

| User | Email | Password | Role | Access |
|------|-------|----------|------|--------|
| Admin | admin@example.com | admin123 | admin | `/api/users/*` only |
| Faculty | faculty@example.com | faculty123 | faculty | Booking, GPA, Notifications, Maintenance |
| Student | student@example.com | student123 | student | Booking, GPA, Notifications, Maintenance |

## ✅ Tested & Verified

### Admin Access (Correct ✅)
```bash
✅ Admin CAN access: GET /api/users
❌ Admin CANNOT access: GET /api/booking/rooms (403 Forbidden)
```

### Faculty/Student Access (Correct ✅)
```bash
✅ Faculty CAN access: GET /api/booking/rooms
❌ Faculty CANNOT access: GET /api/users (403 Forbidden)
```

## 🚀 Quick Start

### Start All Services
```bash
./start_all.sh
```

### Stop All Services
```bash
pkill -f 'venv/bin/python'
```

### View Logs
```bash
tail -f /tmp/gateway.log
tail -f /tmp/booking.log
tail -f /tmp/gpa.log
tail -f /tmp/usermgmt.log
tail -f /tmp/notification.log
tail -f /tmp/maintenance.log
```

## 📡 API Examples

### 1. Login (Admin)
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

**Response:**
```json
{
  "accessToken": "eyJhbGci...",
  "user": {
    "id": "admin-001",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

### 2. Admin: Access User Management ✅
```bash
TOKEN="<admin_token>"

curl http://localhost:5001/api/users \
  -H "Authorization: Bearer $TOKEN"
```

**Response:** List of all users ✅

### 3. Admin: Try Accessing Booking ❌
```bash
curl http://localhost:5001/api/booking/rooms \
  -H "Authorization: Bearer $TOKEN"
```

**Response:** 
```json
{
  "error": "Insufficient permissions"
}
```

### 4. Login (Faculty)
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"faculty@example.com","password":"faculty123"}'
```

### 5. Faculty: Access Booking ✅
```bash
FACULTY_TOKEN="<faculty_token>"

curl http://localhost:5001/api/booking/rooms \
  -H "Authorization: Bearer $FACULTY_TOKEN"
```

**Response:** List of 4 rooms ✅

### 6. Faculty: Calculate GPA ✅
```bash
curl -X POST http://localhost:5001/api/gpa/calculate \
  -H "Authorization: Bearer $FACULTY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "classes": [
      {"gpa": 3.7, "weight": 3},
      {"gpa": 4.0, "weight": 3},
      {"gpa": 3.3, "weight": 2}
    ]
  }'
```

**Response:**
```json
{
  "gpa": 3.71,
  "total_classes": 3,
  "total_weight": 8
}
```

### 7. Faculty: Try Accessing Users ❌
```bash
curl http://localhost:5001/api/users \
  -H "Authorization: Bearer $FACULTY_TOKEN"
```

**Response:**
```json
{
  "error": "Insufficient permissions"
}
```

## 🏗️ Architecture Flow

```
┌─────────────────────────────────────────────────┐
│           LOGIN (Gateway Port 5001)             │
│  POST /auth/login → Returns JWT Token          │
└──────────────────┬──────────────────────────────┘
                   │
           ┌───────┴────────┐
           │  Check Role    │
           └───────┬────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
     ADMIN                FACULTY/STUDENT
        │                     │
        ▼                     ▼
┌───────────────┐    ┌──────────────────────────┐
│ /api/users/*  │    │ /api/booking/*          │
│               │    │ /api/gpa/*              │
│ User Mgmt     │    │ /api/notifications/*    │
│ (Port 8002)   │    │ /api/maintenance/*      │
└───────────────┘    └──────────────────────────┘
```

## 📊 Service Endpoints via Gateway

### Admin Only
- `GET /api/users` - List all users
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `GET /api/users/by-role/{role}` - Filter by role

### Faculty/Student Only
**Booking:**
- `GET /api/booking/rooms` - List rooms
- `GET /api/booking/slots` - List time slots
- `POST /api/booking/bookings` - Create booking
- `GET /api/booking/bookings` - List bookings
- `DELETE /api/booking/bookings/{id}` - Cancel booking
- `GET /api/booking/my-bookings` - My bookings

**GPA:**
- `POST /api/gpa/calculate` - Calculate GPA

**Notifications:**
- `GET /api/notifications` - List notifications
- `POST /api/notifications` - Create notification
- `PUT /api/notifications/{id}/read` - Mark as read
- `GET /api/notifications/unread` - Unread count

**Maintenance:**
- Access via WebSocket: `http://localhost:8080/websocket_frontend.html`

## 🎯 Key Features

### 1. **Role-Based Access Control (RBAC)**
- ✅ Admin: User management ONLY
- ✅ Faculty/Student: All other services
- ✅ Gateway validates roles before routing
- ✅ Backend services also validate JWT

### 2. **JWT Authentication**
- ✅ Secure token-based authentication
- ✅ 24-hour token expiration
- ✅ Token includes user role
- ✅ All requests verified

### 3. **Microservices Architecture**
- ✅ 6 independent services
- ✅ Each service has own database (SQLite)
- ✅ Gateway acts as single entry point
- ✅ Service-to-service isolation

### 4. **Original Functionality Preserved**
- ✅ Booking with 8 time slots
- ✅ GPA calculator (weighted)
- ✅ Maintenance NLP ticketing
- ✅ User management
- ✅ Notifications

## 🌐 Dashboard Access

Open `index.html` in your browser:
- Interactive UI for all services
- Test authentication
- Test role-based access
- Real-time API testing

## 📁 Project Structure

```
cloudMLOPS/
├── gateway/              # Port 5001 - Hub with JWT & Routing
│   └── main.py
├── booking/              # Port 8001 - Room booking
│   └── main.py
├── user-management/      # Port 8002 - User CRUD (Admin only)
│   └── app.py
├── gpa-calculator/       # Port 8003 - GPA calculation
│   └── main.py
├── notification/         # Port 8004 - Notifications
│   └── app.py
├── maintenance/          # Port 8080 - Ticketing + WebSocket
│   └── websocket_api.py
├── index.html           # Dashboard
├── start_all.sh         # Startup script
└── README_ARCHITECTURE.md  # Full documentation
```

## 🎓 Assignment Requirements Met

✅ **6 Microservices** - All implemented and running
✅ **JWT Authentication** - Token-based auth on gateway
✅ **RBAC** - Admin vs Faculty/Student separation
✅ **Gateway Hub** - Central routing based on roles
✅ **Service Isolation** - Each service independent
✅ **REST APIs** - All services expose REST endpoints
✅ **WebSocket** - Maintenance service real-time updates
✅ **Database** - Each service has own SQLite database
✅ **Documentation** - Complete API docs and README

## 🚀 Ready for AWS Deployment

All services are containerizable and ready for:
- AWS ECS/EKS (Docker containers)
- AWS API Gateway (Replace Flask gateway)
- AWS RDS (Replace SQLite)
- AWS Lambda (Serverless option)
- AWS Elastic Beanstalk (Easy deployment)

---

**🎉 System is fully operational and tested!**
**All services running on localhost, role-based routing working perfectly!**
