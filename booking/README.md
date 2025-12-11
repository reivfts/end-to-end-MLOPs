# 🏢 Room Booking Service

A modern, full-stack room booking application built with FastAPI backend and HTML/CSS/JavaScript frontend. Features real-time availability checking, time slot management, and Docker support.

## 📋 Features

- ✅ **Room Management** - View all available rooms
- ✅ **Time Slot Booking** - Book rooms for morning, afternoon, or evening
- ✅ **Availability Checking** - Automatic conflict detection
- ✅ **Real-time Updates** - Auto-refreshing booking list
- ✅ **CORS Enabled** - Frontend-backend communication
- ✅ **Docker Support** - Easy containerized deployment
- ✅ **SQLite Database** - Lightweight and portable

## 📁 Project Structure

```
booking/
├── main.py                 # FastAPI backend application
├── booking.html            # Frontend interface
├── schema.sql              # Database schema
├── init-db.py              # Database initialization script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Docker Compose orchestration
├── .dockerignore            # Files to exclude from Docker image
├── README.md               # This file
├── TESTING_GUIDE.md        # Detailed testing instructions
├── DOCKER_GUIDE.md         # Docker usage guide
└── rooms.db                # SQLite database (auto-created)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- Docker & Docker Compose (optional)

### 1. Install Dependencies

```powershell
cd c:\dev\end-to-end-MLOPs\booking
pip install -r requirements.txt
```

### 2. Initialize Database

The database is automatically created on first run of the application. If you want to manually initialize:

```powershell
python init-db.py
```

### 3. Start the Backend Server

```powershell
cd c:\dev\end-to-end-MLOPs\booking
uvicorn main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started server process [1234]
```

### 4. Open the Frontend

Open your browser and navigate to:
```
file:///c:/dev/end-to-end-MLOPs/booking/booking.html
```

Or press `Ctrl+O` in your browser and select the file.

### 5. Start Booking!

1. Enter your name
2. Select a room
3. Choose a date
4. Select a time slot (morning, afternoon, evening)
5. Click "Book Room"

---

## 🐳 Docker Setup

### Using Docker Compose (Recommended)

```powershell
cd c:\dev\end-to-end-MLOPs\booking
docker-compose up -d
```

### Using Docker Directly

```powershell
# Build the image
docker build -t booking-service:latest .

# Run the container
docker run -d -p 8000:8000 --name booking-backend booking-service:latest

# Check logs
docker logs -f booking-backend

# Stop the container
docker stop booking-backend
```

---

## 📡 API Endpoints

### Get All Rooms
```
GET /rooms
```

**Response:**
```json
{
  "rooms": [
    {"id": 1, "name": "Room A"},
    {"id": 2, "name": "Room B"},
    {"id": 3, "name": "Room C"}
  ]
}
```

### Create a Booking
```
POST /bookings
Content-Type: application/json
```

**Request:**
```json
{
  "room_id": 1,
  "date": "2025-12-20",
  "username": "John Doe",
  "time_slot": "morning"
}
```

**Response:**
```json
{
  "message": "Booking created successfully",
  "booking_id": 1
}
```

### Get All Bookings
```
GET /bookings
```

**Response:**
```json
{
  "bookings": [
    {
      "id": 1,
      "room_id": 1,
      "room_name": "Room A",
      "username": "John Doe",
      "date": "2025-12-20",
      "time_slot": "morning"
    }
  ]
}
```

### Cancel a Booking
```
DELETE /bookings/{booking_id}
```

**Response:**
```json
{
  "message": "Booking cancelled successfully"
}
```

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 📝 Time Slots

The service supports three time slots per day:

| Slot | Time | Icon |
|------|------|------|
| Morning | 9AM - 12PM | 🌅 |
| Afternoon | 12PM - 5PM | ☀️ |
| Evening | 5PM - 8PM | 🌙 |

You can book the same room multiple times per day by selecting different time slots.

---

## 🗄️ Database Schema

### Rooms Table
```sql
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
```

### Bookings Table
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    date TEXT NOT NULL,
    time_slot TEXT NOT NULL CHECK(time_slot IN ('morning', 'afternoon', 'evening')),
    FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
)
```

**Indexes:**
- `idx_bookings_room_date` - Quick availability checks
- `idx_bookings_date` - Date-based queries
- `idx_bookings_username` - User-based lookups

---

## 🧪 Testing

For detailed testing instructions, see [TESTING_GUIDE.md](TESTING_GUIDE.md)

Quick test:
```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get

# Get rooms
Invoke-RestMethod -Uri "http://localhost:8000/rooms" -Method Get
```

---

## 🔧 Configuration

### Environment Variables

The application uses the following paths:
- **Database**: `rooms.db` (in the same directory as main.py)
- **Schema**: `schema.sql` (auto-loads on startup if database doesn't exist)

### CORS Settings

Currently allows all origins for development:
```python
allow_origins=["*"]
```

For production, update `main.py`:
```python
allow_origins=["https://yourwebsite.com", "https://www.yourwebsite.com"]
```

---

## 📦 Dependencies

- **fastapi** (0.104.1) - Web framework
- **uvicorn** (0.24.0) - ASGI server
- **pydantic** (2.5.0) - Data validation
- **python-multipart** (0.0.6) - Form handling

See `requirements.txt` for complete list.

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to http://localhost:8000"

**Solution:**
1. Make sure the backend is running: `uvicorn main:app --reload`
2. Check port 8000 isn't blocked
3. Try `http://127.0.0.1:8000` instead

### Issue: "Room already booked for this time slot"

**Solution:**
This is expected! You can only book one person per room per time slot per day. Choose a different time slot or date.

### Issue: "schema.sql not found" (in Docker)

**Solution:**
Make sure `schema.sql` exists in the booking directory before building the Docker image.

### Issue: Database locked

**Solution:**
The database might be in use by another process. Restart the application.

### Issue: CORS errors in browser

**Solution:**
1. Make sure you're opening the HTML file with `file://` protocol
2. Ensure the backend is running on `http://localhost:8000`
3. Check browser console for detailed error messages

---

## 📚 Additional Resources

- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Comprehensive testing instructions
- [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker and container guidance
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

## 🎯 Common Tasks

### Reset the Database
```powershell
Remove-Item rooms.db
# Restart the application to recreate
```

### View Database Contents
```powershell
sqlite3 rooms.db
sqlite> SELECT * FROM bookings;
sqlite> SELECT * FROM rooms;
```

### Change Sample Rooms
Edit `main.py` line 47-51:
```python
sample_rooms = [
    ("Conference Room 1",),
    ("Meeting Room 2",),
    ("Board Room",)
]
```

### Deploy to Production

1. Update CORS origins in `main.py`
2. Use a production ASGI server (Gunicorn + Uvicorn)
3. Set `--reload` to False
4. Use environment variables for sensitive config
5. Deploy with Docker for consistency

---

## 🤝 Contributing

To contribute improvements:

1. Make changes to the code
2. Test locally with `uvicorn main:app --reload`
3. Update documentation if needed
4. Commit and push changes

---

## 📄 License

This project is part of the end-to-end MLOps repository.

---

## ✅ Status

- ✅ Backend API - Fully functional
- ✅ Frontend UI - Fully functional
- ✅ Database - SQLite with auto-initialization
- ✅ Docker Support - Ready for deployment
- ✅ Documentation - Complete

---

## 📞 Support

For issues or questions:
1. Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for testing help
2. Check [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for deployment issues
3. Review application logs: `docker logs booking-backend`

---

**Built with ❤️ using FastAPI + SQLite + HTML/CSS/JS**
