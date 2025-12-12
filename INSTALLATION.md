# Installation & Setup Guide

## Project Overview

This is a microservices-based MLOps platform with 6 independent services, RBAC, and event-driven architecture.

### Services Created

1. ✅ **Entryway Hub** (Port 4000) - Auth + API Gateway
2. ✅ **RBAC Service** (Port 4001) - User Management (Admin-only)
3. ✅ **Booking Service** (Port 4002) - Room booking with 8 slots
4. 🔄 **Maintenance Service** (Port 8080) - Existing NLP system (needs RBAC integration)
5. ✅ **GPA Calculator** (Port 4004) - Weighted GPA calculation
6. ⏳ **Notification Service** (Port 4005) - Real-time notifications (to be created)

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+ (for Maintenance service)
- **PostgreSQL** 15+
- **Docker & Docker Compose** (recommended)
- **Redis** 6+
- **NATS** 2.9+

## Quick Start (Docker Compose - Recommended)

### 1. Clone & Navigate

```bash
cd /Users/reivfts/Desktop/cloudMLOPS
```

### 2. Environment Setup

Copy `.env.example` files to `.env` in each service:

```bash
# Entryway Hub
cp services/entryway-hub/.env.example services/entryway-hub/.env

# RBAC Service
cp services/rbac-service/.env services/rbac-service/.env

# Booking Service
cp services/booking-service/.env services/booking-service/.env

# GPA Calculator
cp services/gpa-calculator-service/.env services/gpa-calculator-service/.env
```

### 3. Install Dependencies

```bash
# Install all Node.js service dependencies
cd services/entryway-hub && npm install && cd ../..
cd services/rbac-service && npm install && cd ../..
cd services/booking-service && npm install && cd ../..
cd services/gpa-calculator-service && npm install && cd ../..

# Maintenance service (Python - already set up)
cd maintenance && pip install -r requirements_websocket.txt && cd ..
```

### 4. Start Infrastructure

```bash
# Start PostgreSQL, Redis, NATS
docker-compose up -d postgres redis nats
```

### 5. Database Setup

```bash
# Create databases
docker exec -i $(docker-compose ps -q postgres) psql -U postgres <<EOF
CREATE DATABASE rbac_db;
CREATE DATABASE booking_db;
CREATE DATABASE notification_db;
EOF

# Run migrations
cd services/rbac-service && npx prisma migrate dev --name init && cd ../..
cd services/booking-service && npx prisma migrate dev --name init && cd ../..
```

### 6. Start Services

**Option A: Individual Terminals (for development)**

```bash
# Terminal 1 - Entryway Hub
cd services/entryway-hub && npm run dev

# Terminal 2 - RBAC Service
cd services/rbac-service && npm run dev

# Terminal 3 - Booking Service
cd services/booking-service && npm run dev

# Terminal 4 - Maintenance Service (existing)
cd maintenance && python websocket_api.py

# Terminal 5 - GPA Calculator
cd services/gpa-calculator-service && npm run dev
```

**Option B: Docker Compose (all services)**

```bash
docker-compose up --build
```

### 7. Access Application

- **Frontend**: http://localhost:3000 (when created)
- **Entryway Hub**: http://localhost:4000
- **Health Checks**: 
  - http://localhost:4000/healthz
  - http://localhost:4001/healthz
  - http://localhost:4002/healthz
  - http://localhost:4004/healthz

## Default Test Users

```
Admin:
- Email: admin@example.com
- Password: admin123
- Access: RBAC UI only

Faculty:
- Email: faculty@example.com
- Password: faculty123
- Access: Booking (all), Maintenance (all), GPA

Student:
- Email: student@example.com
- Password: student123
- Access: Booking (own), Maintenance (own), GPA
```

## Manual Installation (No Docker)

### 1. Install PostgreSQL

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Create databases
createdb rbac_db
createdb booking_db
createdb notification_db
```

### 2. Install Redis

```bash
# macOS
brew install redis
brew services start redis
```

### 3. Install NATS

```bash
# macOS
brew install nats-server
nats-server -js &
```

### 4. Install Service Dependencies

```bash
# Each TypeScript service
cd services/entryway-hub && npm install
cd services/rbac-service && npm install
cd services/booking-service && npm install
cd services/gpa-calculator-service && npm install

# Python maintenance service (already done)
cd maintenance && pip install -r requirements_websocket.txt
```

### 5. Run Database Migrations

```bash
cd services/rbac-service
npx prisma migrate dev --name init
npx prisma generate

cd ../booking-service
npx prisma migrate dev --name init
npx prisma generate
```

### 6. Update Environment Variables

Edit `.env` files in each service to match your local setup:

```env
# Example: services/rbac-service/.env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/rbac_db"
NATS_URL=nats://localhost:4222
```

## API Testing

### 1. Login

```bash
curl -X POST http://localhost:4000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"student123"}'

# Response:
# {
#   "accessToken": "eyJhbGc...",
#   "user": {
#     "id": "...",
#     "name": "Student User",
#     "email": "student@example.com",
#     "role": "student"
#   }
# }
```

### 2. Create Booking

```bash
TOKEN="<your_access_token>"

curl -X POST http://localhost:4000/api/booking/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-01-15","slotIndex":3}'

# Response:
# {
#   "id": "...",
#   "date": "2025-01-15",
#   "slotIndex": 3,
#   "status": "CONFIRMED"
# }
```

### 3. Calculate GPA

```bash
curl -X POST http://localhost:4000/api/gpa/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "classes": [
      {"gpa": 3.7, "weight": 3},
      {"gpa": 3.3, "weight": 2}
    ]
  }'

# Response:
# {"gpa": 3.54}
```

### 4. Create Maintenance Request (WebSocket)

Connect to `ws://localhost:8080` and emit:

```javascript
socket.emit('analyze_ticket', {
  text: "Projector in Room 204 not working"
});

// Receives:
// {
#   "id": "...",
#   "priority_level": "High",
#   "status": "open",
#   ...
# }
```

## Project Structure

```
cloudMLOPS/
├── services/
│   ├── entryway-hub/         ✅ Auth + Gateway
│   ├── rbac-service/         ✅ User Management
│   ├── booking-service/      ✅ Room Booking
│   ├── gpa-calculator-service/ ✅ GPA Calculator
│   └── notification-service/  ⏳ To be created
├── maintenance/              🔄 Existing (needs RBAC)
│   ├── websocket_api.py
│   ├── enhanced_model.py
│   └── websocket_frontend.html
├── frontend/                 ⏳ To be created
│   └── React + Tailwind
├── docker-compose.yml        ✅ Created
├── ARCHITECTURE.md           ✅ Documentation
└── README.md                 Existing

✅ = Completed
🔄 = Needs enhancement
⏳ = Pending
```

## Next Steps

### Phase 1: Complete Core Services ✅
- [x] Entryway Hub (Auth + Gateway)
- [x] RBAC Service
- [x] Booking Service
- [x] GPA Calculator

### Phase 2: Remaining Services
- [ ] Notification Service (WebSocket + NATS subscriber)
- [ ] Enhance Maintenance Service with RBAC
  - Add JWT verification
  - Filter by userId for students
  - Keep existing NLP functionality

### Phase 3: Frontend
- [ ] React app with Tailwind CSS
- [ ] Role-based navigation
- [ ] Login page
- [ ] RBAC UI (admin only)
- [ ] Booking UI
- [ ] Maintenance UI
- [ ] GPA Calculator UI
- [ ] Notification toasts

### Phase 4: Production Ready
- [ ] Docker images for all services
- [ ] Kubernetes manifests
- [ ] CI/CD pipelines
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Unit & integration tests
- [ ] Monitoring & logging

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -ti:4000
# Kill process
kill -9 <PID>
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
pg_isready

# Reset database
dropdb rbac_db && createdb rbac_db
cd services/rbac-service && npx prisma migrate dev
```

### NATS Connection Failed

```bash
# Check NATS is running
nats server check

# Restart NATS
nats-server -js &
```

### TypeScript Compilation Errors

```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

## Development Commands

### Run in Development Mode

```bash
# Each service
cd services/<service-name>
npm run dev   # Auto-reload on changes
```

### Build for Production

```bash
cd services/<service-name>
npm run build
npm start
```

### Database Commands

```bash
# Generate Prisma client
npx prisma generate

# Create migration
npx prisma migrate dev --name <migration-name>

# View database
npx prisma studio
```

### Docker Commands

```bash
# Build all services
docker-compose build

# Start specific service
docker-compose up entryway-hub

# View logs
docker-compose logs -f <service-name>

# Stop all
docker-compose down

# Reset everything
docker-compose down -v
docker-compose up --build
```

## Testing the System

### 1. Test RBAC (Admin Only)

```bash
# Login as admin
curl -X POST http://localhost:4000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Get token from response, then:
TOKEN="<admin_token>"

# List users
curl http://localhost:4000/api/rbac/users \
  -H "Authorization: Bearer $TOKEN"

# Create user
curl -X POST http://localhost:4000/api/rbac/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"newuser@example.com",
    "name":"New User",
    "password":"password123",
    "role":"student"
  }'

# Update role
curl -X PATCH http://localhost:4000/api/rbac/users/<user-id>/role \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"faculty"}'
```

### 2. Test Booking (Student)

```bash
# Login as student
TOKEN="<student_token>"

# View available slots for a date
curl "http://localhost:4000/api/booking/bookings?date=2025-01-15" \
  -H "Authorization: Bearer $TOKEN"

# Create booking
curl -X POST http://localhost:4000/api/booking/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-01-15","slotIndex":2}'

# View my bookings
curl http://localhost:4000/api/booking/bookings/mine \
  -H "Authorization: Bearer $TOKEN"

# Cancel booking
curl -X PATCH "http://localhost:4000/api/booking/bookings/<booking-id>/cancel" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Test GPA Calculator

```bash
curl -X POST http://localhost:4000/api/gpa/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "classes": [
      {"gpa": 4.0, "weight": 3},
      {"gpa": 3.5, "weight": 2},
      {"gpa": 3.8, "weight": 3}
    ]
  }'

# Expected: {"gpa": 3.79}
```

## Security Notes

- Change `JWT_SECRET` in production
- Use HTTPS in production
- Implement rate limiting
- Add input validation middleware
- Enable CORS only for trusted origins
- Use environment variables for all secrets
- Rotate JWT tokens regularly

## Support

- GitHub Issues: https://github.com/reivfts/end-to-end-MLOPs/issues
- Documentation: See ARCHITECTURE.md
- API Docs: `/api-docs` endpoint on each service

## License

MIT
