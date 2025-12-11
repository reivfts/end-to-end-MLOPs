# MLOps Platform - End-to-End Microservices Application

A modern microservices application for managing room bookings and maintenance tickets with user authentication. Built with FastAPI, Flask, and vanilla JavaScript.

## 📋 Project Structure

```
c:\dev\end-to-end-MLOps\
├── frontend/                    # Frontend static files (HTML/CSS/JS)
│   ├── index.html              # Home page with login/signup
│   ├── booking-frontend.html   # Room booking system
│   ├── maintenance-frontend.html # Maintenance ticket system
│   └── (more frontend files)
│
├── booking/                     # Room Booking Service
│   ├── main.py                 # FastAPI application
│   ├── schema.sql              # Database schema
│   ├── requirements.txt        # Python dependencies
│   ├── rooms.db                # SQLite database (created on first run)
│   └── venv/                   # Virtual environment
│
├── maintenance/                # Maintenance Ticket Service
│   ├── main.py                 # Flask application
│   ├── requirements.txt        # Python dependencies
│   ├── maintenance_data.json   # Data storage
│   └── venv/                   # Virtual environment
│
├── user-management/            # User Authentication Service
│   ├── main.py                 # Flask application
│   ├── requirements.txt        # Python dependencies
│   └── venv/                   # Virtual environment
│
├── gateway/                     # API Gateway (request router)
│   ├── main.py                 # Flask application
│   ├── requirements.txt        # Python dependencies
│   └── venv/                   # Virtual environment
│
└── notification/               # Notification Service (future)
    ├── main.py
    └── requirements.txt
```

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.8+
- Windows PowerShell or Command Prompt
- Modern web browser

### 1️⃣ Navigate to Project

```bash
cd c:\dev\end-to-end-MLOps
```

### 2️⃣ Create Virtual Environments & Install Dependencies

Run these commands in 5 separate terminal windows:

**Terminal 1 - Booking Service:**
```bash
cd c:\dev\end-to-end-MLOps\booking
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Maintenance Service:**
```bash
cd c:\dev\end-to-end-MLOps\maintenance
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 3 - User Management Service:**
```bash
cd c:\dev\end-to-end-MLOps\user-management
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 4 - API Gateway:**
```bash
cd c:\dev\end-to-end-MLOps\gateway
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 5 - Frontend HTTP Server:**
```bash
cd c:\dev\end-to-end-MLOps
python -m http.server 3000 --directory frontend
```

### 3️⃣ Access the Application

Open your browser and navigate to:
```
http://localhost:3000/index.html
```

## 🔧 Service Architecture

```
┌─────────────────────────────────────────────────────┐
│              Frontend (HTML/JS/CSS)                 │
│         http://localhost:3000                       │
│  - Login/Signup System                              │
│  - Room Booking Interface                           │
│  - Maintenance Ticket System                        │
└────┬──────────────────────────────┬─────────────────┘
     │ HTTP API Calls               │
     ▼                              ▼
┌──────────────────────────────────────────────┐
│  API Gateway (Flask)                         │
│  http://localhost:8080                       │
│  Routes All Requests to Services             │
└────┬─────────────────────────────────────────┘
     │
     ├───────────────┬──────────────┬──────────────┬──────────────┐
     ▼               ▼              ▼              ▼              ▼
┌────────────┐  ┌───────────┐  ┌─────────────┐  ┌────────────┐  ┌──────────────┐
│ Booking    │  │Mainten.   │  │ User        │  │Notif.      │  │ Others       │
│(FastAPI)   │  │(Flask)    │  │(Flask)      │  │(Flask)     │  │              │
│:8000       │  │:8001      │  │:8002        │  │:8003       │  │              │
└────────────┘  └───────────┘  └─────────────┘  └────────────┘  └──────────────┘
     │               │
     ▼               ▼
  rooms.db    maintenance_data.json
```

## 🎯 Features

### Frontend (http://localhost:3000)
- **🔐 Authentication**
  - User registration with email validation
  - Secure login
  - Session persistence
  - Logout functionality

- **🏨 Room Booking**
  - View available rooms
  - Select date and time slot
  - Create bookings
  - Manage your bookings
  - Cancel bookings

- **🔧 Maintenance Tickets**
  - Create support tickets
  - Track ticket status
  - View all tickets

### Microservices

**Booking Service (Port 8000)**
- RESTful API for room management
- Database: SQLite (rooms.db)
- Framework: FastAPI
- CORS enabled

**Maintenance Service (Port 8001)**
- Ticket management API
- Storage: JSON file
- Framework: Flask
- CORS enabled

**User Management Service (Port 8002)**
- Authentication & registration
- User profile management
- Storage: In-memory dictionary
- Framework: Flask
- CORS enabled

**API Gateway (Port 8080)**
- Central request routing
- Request forwarding to microservices
- Health check aggregation
- Framework: Flask

## 🌐 API Endpoints

### Booking Service (/api/booking)
```
GET    /rooms              - List all available rooms
POST   /bookings           - Create new booking
GET    /bookings           - List all bookings
GET    /bookings/user/{id} - Get user's bookings
DELETE /bookings/{id}      - Cancel booking
GET    /health             - Health check
```

### Maintenance Service (/api/maintenance)
```
GET    /tickets            - List all tickets
POST   /tickets            - Create new ticket
GET    /tickets/{id}       - Get ticket details
PATCH  /tickets/{id}       - Update ticket
DELETE /tickets/{id}       - Delete ticket
GET    /stats              - Get statistics
GET    /health             - Health check
```

### User Management Service (/api/user)
```
POST   /register           - Register new user
POST   /login              - Login user
GET    /users              - List all users
GET    /users/{username}   - Get user by username
DELETE /users/{id}         - Delete user
GET    /health             - Health check
```

## 📦 Dependencies

### Booking Service
- FastAPI
- Uvicorn (ASGI server)
- SQLite3

### Maintenance Service
- Flask
- Flask-CORS

### User Management Service
- Flask
- Flask-CORS

### API Gateway
- Flask
- Flask-CORS
- Requests

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla)

## 🧪 Testing the Application

### 1. Register a New User
1. Go to http://localhost:3000/index.html
2. Click "Sign Up"
3. Enter username, email, and password
4. Click "Sign Up"

### 2. Login
1. Click "Login" with your credentials
2. You'll see the home page with service options

### 3. Create a Booking
1. Click "Booking" card
2. Select a room
3. Choose a date (today or future)
4. Select time slot (Morning/Afternoon/Evening)
5. Click "Create Booking"

### 4. View Your Bookings
1. Click "My Bookings" tab
2. See all your reservations

### 5. Create Maintenance Ticket
1. Click "Maintenance" card
2. Enter issue description
3. Set priority
4. Click "Create Ticket"

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Kill all Python processes (Windows PowerShell)
Get-Process python | Stop-Process -Force
```

### Database Errors
```bash
# Delete old database and restart booking service
rm c:\dev\end-to-end-MLOps\booking\rooms.db
# Restart booking service - database will recreate with proper schema
```

### Virtual Environment Issues
```bash
# Recreate virtual environment for a service
rm -r booking\venv
python -m venv booking\venv
.\booking\venv\Scripts\activate
pip install -r booking\requirements.txt
```

### Services Not Communicating
1. Ensure all 5 services are running
2. Verify ports are available: 3000, 8000, 8001, 8002, 8080
3. Open browser console (F12) to see API errors
4. Check terminal outputs for error messages

## 📝 Configuration

### Change Service Ports
Edit main.py files:

**booking/main.py:**
```python
uvicorn.run(app, host="localhost", port=8000)
```

**maintenance/main.py, user-management/main.py, gateway/main.py:**
```python
app.run(host='localhost', port=8001)  # or 8002, 8080
```

### Change Frontend Port
```bash
python -m http.server 3001 --directory frontend
```

## 🚀 Deployment

For production:
1. Use production WSGI servers (Gunicorn, Waitress)
2. Enable HTTPS/TLS
3. Implement proper authentication (JWT, OAuth)
4. Use production database (PostgreSQL, MySQL)
5. Set up logging and monitoring
6. Implement API rate limiting
7. Add input validation and sanitization
8. Use environment variables for configuration

## 📚 Project Guidelines

### Adding New Services
1. Create new directory under root
2. Add main.py with Flask/FastAPI app
3. Create requirements.txt with dependencies
4. Update gateway/main.py with new route
5. Update frontend to call new service

### Modifying Database Schema
1. Update schema.sql
2. Delete rooms.db
3. Restart booking service
4. Database recreates with new schema

### Frontend Changes
1. Edit HTML files in /frontend/
2. No build process needed
3. Refresh browser to see changes
4. Check console (F12) for errors

## 📖 Additional Resources

- **Service Details**: Check individual main.py files
- **Database Schema**: See booking/schema.sql
- **Frontend Code**: Check /frontend/ HTML files

## ⚖️ License

Demonstration project for learning microservices architecture.

## 👤 Author

End-to-end MLOps learning project.

---

**Last Updated:** December 11, 2025  
**Status:** ✅ Fully Functional

For issues, check terminal outputs and browser console (F12) for error messages.
