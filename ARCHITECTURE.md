# MLOps Microservices Platform - Architecture Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│                      http://localhost:3000                       │
│        Role-Based Navigation | Tailwind CSS | WebSocket         │
└───────────────────┬─────────────────────────────────────────────┘
                    │ HTTP/WebSocket
┌───────────────────▼─────────────────────────────────────────────┐
│                    Entryway Hub (Port 4000)                      │
│              JWT Auth | API Gateway | Proxy Routes              │
└─┬────────┬──────────┬───────────┬─────────────┬─────────────────┘
  │        │          │           │             │
  │ Proxy  │ Proxy    │ Proxy     │ Proxy       │ Proxy
  │        │          │           │             │
┌─▼────┐ ┌▼──────┐ ┌▼────────┐ ┌▼──────┐ ┌────▼──────┐
│ RBAC │ │Booking│ │Mainten- │ │  GPA  │ │Notification│
│ 4001 │ │ 4002  │ │ance 8080│ │ 4004  │ │   4005     │
└─┬────┘ └┬──────┘ └┬────────┘ └┬──────┘ └────┬───────┘
  │       │         │           │             │
  └───────┴─────────┴───────────┴─────────────┘
                    │
            ┌───────▼────────┐
            │  NATS (4222)   │
            │  Event Bus     │
            └────────────────┘
                    │
        ┌───────────┼───────────┐
   ┌────▼────┐ ┌───▼────┐ ┌───▼────┐
   │PostgreSQL│ │ Redis  │ │Python  │
   │  5432   │ │  6379  │ │  NLP   │
   └─────────┘ └────────┘ └────────┘
```

## Service Details

### 1. Entryway Hub (Port 4000)
- **Tech**: TypeScript, Express
- **Purpose**: Authentication & API Gateway
- **Features**:
  - JWT authentication (bcrypt)
  - Token generation & verification
  - Proxies all API requests to services
  - Forwards user context in headers
- **Default Users**:
  - admin@example.com / admin123
  - faculty@example.com / faculty123
  - student@example.com / student123

### 2. RBAC Service (Port 4001)
- **Tech**: TypeScript, Express, Prisma, PostgreSQL
- **Purpose**: User & Role Management
- **Access**: Admin only
- **Features**:
  - User CRUD operations
  - Role management (admin/faculty/student)
  - Publishes user events to NATS
- **Database**: `rbac_db`

### 3. Booking Service (Port 4002)
- **Tech**: TypeScript, Express, Prisma, PostgreSQL
- **Purpose**: Room booking with time slots
- **Features**:
  - 8 slots/day (2-hour blocks, 16-hour day)
  - Double-booking prevention
  - Faculty: manage ALL bookings
  - Students: manage OWN bookings
- **Database**: `booking_db`

### 4. Maintenance Service (Port 8080)
- **Tech**: Python, Flask, Flask-SocketIO, NLTK
- **Purpose**: NLP-powered ticketing system
- **Features**:
  - **Existing NLP model preserved** (`enhanced_model.py`)
  - Priority analysis with pattern matching
  - WebSocket real-time updates
  - Status workflow: open → viewed → in-progress → completed
  - Faculty: see ALL requests
  - Students: see OWN requests
- **Storage**: JSON file (`tickets_storage.json`)
- **Enhancement**: Added RBAC middleware

### 5. GPA Calculator (Port 4004)
- **Tech**: TypeScript, Express
- **Purpose**: Weighted GPA calculation
- **Features**:
  - Stateless API
  - Formula: Σ(gpa×weight) / Σ(weight)
  - Validation: GPA 0.0-4.0, Weight 1-3
- **No database needed**

### 6. Notification Service (Port 4005)
- **Tech**: TypeScript, Express, Socket.io, Prisma
- **Purpose**: Real-time notifications
- **Features**:
  - Subscribes to all NATS events
  - WebSocket for real-time toasts
  - Notification history
  - In-app popups for key events
- **Database**: `notification_db`

## Role-Based Access Control

| Service | Admin | Faculty | Student |
|---------|-------|---------|---------|
| RBAC | ✅ Full | ❌ No access | ❌ No access |
| Booking | ❌ Hidden | ✅ All bookings | ✅ Own bookings |
| Maintenance | ❌ Hidden | ✅ All requests | ✅ Own requests |
| GPA | ❌ Hidden | ✅ Calculate | ✅ Calculate |

## API Endpoints

### Entryway Hub (4000)
```
POST   /auth/login                 - Login
GET    /auth/me                    - Get current user
GET    /auth/.well-known/jwks.json - JWKS endpoint
POST   /auth/logout                - Logout

# Proxy routes (requires JWT)
/api/rbac/*          → RBAC Service
/api/booking/*       → Booking Service
/api/maintenance/*   → Maintenance Service
/api/gpa/*           → GPA Service
/api/notifications/* → Notification Service
```

### RBAC Service (4001) - Admin Only
```
GET    /users           - List all users
POST   /users           - Create user
PATCH  /users/:id/role  - Update role
DELETE /users/:id       - Delete user
```

### Booking Service (4002)
```
GET    /bookings?date=YYYY-MM-DD - List bookings for date
GET    /bookings/mine            - Current user's bookings
POST   /bookings                 - Create booking
       Body: {"date":"2025-01-10","slotIndex":3}
PATCH  /bookings/:id/cancel      - Cancel booking
```

### Maintenance Service (8080)
```
POST   /requests      - Create maintenance request
GET    /requests/mine - Student's own requests
GET    /requests      - Faculty only (all requests)
PATCH  /requests/:id  - Update status

WebSocket Events:
- analyze_ticket   (client → server)
- new_ticket      (server → clients)
- ticket_updated  (server → clients)
- ticket_deleted  (server → clients)
- admin_command   (admin actions)
```

### GPA Calculator (4004)
```
POST /calculate
Body: {
  "classes": [
    {"gpa": 3.7, "weight": 3},
    {"gpa": 3.3, "weight": 2}
  ]
}
Response: {"gpa": 3.54}
```

### Notification Service (4005)
```
GET    /notifications        - List user's notifications
PATCH  /notifications/:id/read - Mark as read

WebSocket:
- Connect with JWT
- Receive 'notification' events
```

## Event-Driven Communication

### NATS Topics

```
user.created        (RBAC → Notification)
user.updated        (RBAC → Notification)
user.deleted        (RBAC → Notification)

booking.created     (Booking → Notification)
booking.cancelled   (Booking → Notification)

maintenance.created (Maintenance → Notification)
maintenance.updated (Maintenance → Notification)
```

### Event Payloads

**booking.created:**
```json
{
  "userId": "uuid",
  "bookingId": "uuid",
  "date": "2025-01-10",
  "slotIndex": 3,
  "slotTime": "6:00 AM - 8:00 AM"
}
```

**maintenance.created:**
```json
{
  "userId": "uuid",
  "ticketId": "uuid",
  "title": "Projector issue",
  "priority": "High",
  "status": "open"
}
```

## Frontend Architecture

### Routes
```
/login       - Login page (public)
/rbac        - User management (admin only)
/booking     - Room booking (faculty/student)
/maintenance - Maintenance requests (faculty/student)
/gpa         - GPA calculator (faculty/student)
```

### Components

```
src/
├── App.tsx                 # Root component, Router
├── components/
│   ├── Login.tsx           # Login form
│   ├── Navigation.tsx      # Role-based nav
│   ├── Toast.tsx           # Notification toasts
│   ├── RBAC/
│   │   └── UserManagement.tsx
│   ├── Booking/
│   │   ├── BookingList.tsx
│   │   ├── BookingForm.tsx
│   │   └── SlotPicker.tsx
│   ├── Maintenance/
│   │   ├── TicketList.tsx
│   │   └── TicketForm.tsx
│   └── GPA/
│       └── GPACalculator.tsx
├── hooks/
│   ├── useAuth.ts          # Authentication hook
│   ├── useWebSocket.ts     # WebSocket connection
│   └── useNotifications.ts # Notification handling
├── services/
│   ├── api.ts              # Axios instance
│   └── auth.ts             # Auth utilities
└── context/
    └── AuthContext.tsx     # Global auth state
```

### Role-Based Navigation Logic

```typescript
const Navigation = () => {
  const { user } = useAuth();

  if (user.role === 'admin') {
    return <Link to="/rbac">RBAC</Link>;
  }

  return (
    <>
      <Link to="/booking">Booking</Link>
      <Link to="/maintenance">Maintenance</Link>
      <Link to="/gpa">GPA Calculator</Link>
    </>
  );
};
```

## Security Implementation

### JWT Flow

1. User logs in at Entryway Hub
2. Hub verifies credentials, generates JWT
3. JWT contains: `{userId, email, role, exp}`
4. Frontend stores JWT in localStorage
5. All requests include: `Authorization: Bearer <token>`
6. Gateway validates JWT, extracts user info
7. Gateway forwards to services with headers:
   - `x-user-id`
   - `x-user-email`
   - `x-user-role`
8. Services trust gateway's headers

### Middleware Example

```typescript
// Gateway forwards user context
export const authenticate = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  const decoded = jwt.verify(token, JWT_SECRET);
  
  req.headers['x-user-id'] = decoded.userId;
  req.headers['x-user-email'] = decoded.email;
  req.headers['x-user-role'] = decoded.role;
  
  next();
};

// Service reads headers
export const requireRole = (...roles) => {
  return (req, res, next) => {
    const userRole = req.headers['x-user-role'];
    if (!roles.includes(userRole)) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    next();
  };
};
```

## Booking Service - Time Slots

### Slot Calculation

```
Day: 16 hours (e.g., 6 AM - 10 PM)
Slot Duration: 2 hours
Total Slots: 8 per day

Slot Index | Time Range
-----------|---------------
0          | 6:00 AM - 8:00 AM
1          | 8:00 AM - 10:00 AM
2          | 10:00 AM - 12:00 PM
3          | 12:00 PM - 2:00 PM
4          | 2:00 PM - 4:00 PM
5          | 4:00 PM - 6:00 PM
6          | 6:00 PM - 8:00 PM
7          | 8:00 PM - 10:00 PM
```

### Double-Booking Prevention

```typescript
// Before creating booking
const existing = await prisma.booking.findFirst({
  where: {
    date: bookingDate,
    slotIndex: requestedSlot,
    status: 'CONFIRMED'
  }
});

if (existing) {
  throw new Error('Slot already booked');
}
```

## Maintenance Service - NLP Integration

### Existing NLP Functionality (Preserved)

```python
# enhanced_model.py - No changes needed
def analyze_maintenance_request(text):
    # Pattern matching
    # Priority scoring
    # Urgency detection
    # Confidence levels
    return {
        "priority_score": 85,
        "priority_level": "High",
        "confidence": "high",
        "matched_patterns": [...],
        "analysis": {...}
    }
```

### New RBAC Layer (Added)

```python
# websocket_api.py - Enhanced with RBAC
@socketio.on('analyze_ticket')
def handle_ticket(data):
    # Extract user from JWT headers
    user_id = request.headers.get('x-user-id')
    user_role = request.headers.get('x-user-role')
    
    # Existing NLP analysis
    analysis = analyze_maintenance_request(data['text'])
    
    # Store with user association
    ticket = {
        'id': uuid4(),
        'userId': user_id,
        'analysis': analysis,
        # ... rest of ticket
    }
    
    # Broadcast based on role
    if user_role == 'faculty':
        broadcast_to_all(ticket)
    else:
        send_to_user(user_id, ticket)
```

### RBAC Query Logic

```python
# GET /requests
def get_requests():
    user_role = request.headers.get('x-user-role')
    user_id = request.headers.get('x-user-id')
    
    if user_role == 'faculty':
        # Faculty see all
        return get_all_tickets()
    else:
        # Students see own
        return get_tickets_by_user(user_id)
```

## Notification Examples

### Booking Created
```
Title: "Booking Confirmed"
Message: "Booking for 2025-01-10 slot 6:00 AM - 8:00 AM"
Type: "success"
```

### Maintenance Created
```
Title: "Maintenance Request Submitted"
Message: "Maintenance request successfully made. Priority: High"
Type: "success"
```

### Maintenance Updated
```
Title: "Request Status Changed"
Message: "Status of maintenance request has been updated: in-progress"
Type: "info"
```

### Role Changed (Admin action)
```
Title: "Role Updated"
Message: "Your role has been updated to faculty"
Type: "warning"
```

## Development Workflow

### 1. Start Infrastructure
```bash
docker-compose up -d postgres redis nats
```

### 2. Start Backend Services
```bash
# Terminal 1 - Entryway Hub
cd services/entryway-hub && npm run dev

# Terminal 2 - RBAC
cd services/rbac-service && npm run dev

# Terminal 3 - Booking
cd services/booking-service && npm run dev

# Terminal 4 - Maintenance (existing Python)
cd maintenance && python websocket_api.py

# Terminal 5 - GPA
cd services/gpa-calculator-service && npm run dev

# Terminal 6 - Notification
cd services/notification-service && npm run dev
```

### 3. Start Frontend
```bash
cd frontend && npm start
```

### 4. Test Flow

1. Login as student
2. Create booking → see toast notification
3. Create maintenance request → NLP analysis + toast
4. Calculate GPA
5. Logout, login as faculty
6. View all bookings/maintenance requests
7. Logout, login as admin
8. Manage users in RBAC UI

## Deployment

### Docker Compose Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

Each service needs:
- `JWT_SECRET` (must match across all services)
- `DATABASE_URL`
- `NATS_URL`
- `REDIS_URL`

## Testing

### Unit Tests
```bash
npm test
```

### Integration Tests
```bash
npm run test:integration
```

### E2E Tests (Playwright)
```bash
npm run test:e2e
```

## Monitoring & Observability

- Health checks: `/healthz` on all services
- Structured logging (Winston)
- Request tracing with correlation IDs
- Metrics: Prometheus + Grafana
- Error tracking: Sentry

## Next Steps

1. ✅ Entryway Hub created
2. ✅ RBAC Service created
3. 🔄 Booking Service (in progress)
4. ⏳ GPA Calculator Service
5. ⏳ Notification Service  
6. ⏳ Enhance Maintenance with RBAC
7. ⏳ Build React Frontend
8. ⏳ Docker Compose setup
9. ⏳ Documentation & Testing

## Current Status

**Completed:**
- Project structure
- Entryway Hub (Auth + Gateway)
- RBAC Service with Prisma
- Architecture documentation

**In Progress:**
- Booking Service
- Frontend setup

**Pending:**
- GPA Calculator
- Notification Service
- Maintenance RBAC integration
- Docker Compose
- Frontend development
