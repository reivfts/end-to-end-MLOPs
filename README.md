# Campus Services Hub - Complete Documentation

**Project**: Campus Services Hub  
**Date**: December 13, 2025  
**Branch**: main  
**Status**: Production Ready

---

## System Overview

Campus Services Hub is a microservices platform for university/campus management with role-based access control (RBAC). The system provides secure access to room booking, GPA calculation, maintenance ticketing, and notification services through a centralized JWT-authenticated gateway.

### User Roles and Access

- **Admin**: User management and notification access only
- **Faculty**: Access to booking, GPA calculator, maintenance tickets, and notifications
- **Student**: Access to booking, GPA calculator, maintenance tickets, and notifications

---

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (HTML/JavaScript)                    │
│                       localhost:5001/static                      │
│           Role-Based Navigation | JWT Authentication             │
└───────────────────┬─────────────────────────────────────────────┘
                    │ HTTP/HTTPS Requests
┌───────────────────▼─────────────────────────────────────────────┐
│                Gateway Service (Port 5001)                       │
│           Flask | JWT Auth | API Routing | Static Files         │
└─┬────────┬──────────┬───────────┬─────────────┬─────────────────┘
  │        │          │           │             │
  │ Route  │ Route    │ Route     │ Route       │ Route
  │        │          │           │             │
┌─▼────────┐ ┌▼──────────┐ ┌▼────────────┐ ┌▼──────────┐ ┌▼────────────┐
│User Mgmt │ │  Booking  │ │Maintenance  │ │    GPA    │ │Notification │
│Flask 8002│ │FastAPI8001│ │Flask+WS 8080│ │Flask 8003 │ │Flask 8004   │
│   JWT    │ │   JWT     │ │    JWT      │ │   JWT     │ │    JWT      │
└─────┬────┘ └─────┬─────┘ └─────┬───────┘ └─────┬─────┘ └─────┬───────┘
      │             │             │             │             │
      └─────────────┼─────────────┼─────────────┼─────────────┘
                    │             │             │
            ┌───────▼─────────────▼─────────────▼───────┐
            │              SQLite Databases             │
            │  users.db | bookings.db | maintenance.db  │
            │  gateway.db | notifications.db            │
            └───────────────────────────────────────────┘
```

---

## 🔐 **Authentication & Security**

### **JWT Authentication Flow**
1. **Login**: User authenticates via Gateway → Receives JWT token (24-hour expiry)
2. **Authorization**: Each service independently validates JWT tokens
3. **RBAC**: Token contains role information for permission checks
4. **Security**: All sensitive operations require valid JWT

### **Default Users**
```
Admin:   admin@example.com    / admin123    (Full system access)
Faculty: faculty@example.com  / faculty123  (Enhanced permissions) 
Student: student@example.com  / student123  (Basic access)
```

---

## 🚀 **Services Documentation**

### **1. Gateway Service (Port 5001)** 
**Purpose**: Central authentication hub and API router  
**Tech Stack**: Python Flask + SQLite  
**Database**: `gateway.db`

**Key Features**:
- ✅ JWT token generation and validation
- ✅ User authentication (login/logout)
- ✅ Static file serving (frontend)
- ✅ API routing to all microservices
- ✅ CORS enabled for web clients

**Core Endpoints**:
- `POST /auth/login` - User authentication
- `GET /auth/me` - Current user information
- `POST /api/users` - Create user (Admin only)
- `GET /api/users` - List users
- `DELETE /api/users/{id}` - Delete user (Admin only)

---

### **2. User Management Service (Port 8002)**
**Purpose**: User CRUD operations and role management  
**Tech Stack**: Python Flask + SQLite  
**Database**: `users.db`

**Key Features**:
- ✅ Complete user lifecycle management
- ✅ Role assignment (Student/Faculty/Admin)
- ✅ Admin notification triggers
- ✅ JWT-secured endpoints

**Core Endpoints**:
- `GET /users` - List all users
- `POST /users` - Create new user  
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user
- `GET /users/{id}` - Get user details

---

## 🚀 **Quick Start Guide**

### **1. Start All Services**
```bash
# Start services in order (each in separate terminal)
cd gateway && python3 main.py          # Port 5001
cd user-management && python3 app.py   # Port 8002  
cd booking && python3 main.py          # Port 8001
cd gpa-calculator && python3 main.py   # Port 8003
cd notification && python3 app.py      # Port 8004
cd maintenance && python3 websocket_api.py  # Port 8080
```

### **2. Access the System**
- **Frontend**: http://localhost:5001
- **Login**: Use default credentials above
- **API Docs**: http://localhost:8001/docs (FastAPI auto-docs)

---

## 🎉 **System Status: COMPLETE**

| Service | Port | Status | JWT | Database | Features |
|---------|------|--------|-----|----------|----------|
| Gateway | 5001 | ✅ Complete | ✅ | gateway.db | Auth + Routing |
| User-Mgmt | 8002 | ✅ Complete | ✅ | users.db | CRUD + Notifications |  
| Booking | 8001 | ✅ Complete | ✅ | bookings.db | Reservations + FastAPI |
| GPA | 8003 | ✅ Complete | ✅ | None | Calculations |
| Notification | 8004 | ✅ Complete | ✅ | notifications.db | Admin System |
| Maintenance | 8080 | ✅ Complete | ✅ | maintenance.db | AI + WebSocket |

**Campus Services Hub is production-ready with full RBAC implementation!** 🚀

---

*Last Updated: December 13, 2025 - Complete System Documentation*