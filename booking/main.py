"""
Booking Service with JWT Auth & RBAC
Room booking with 8 time slots per day
Port: 8001
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import jwt
import requests
import logging
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(correlation_id)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/booking.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Booking Service")

# Add correlation ID middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    logger.info(f"Request started: {request.method} {request.url.path}",
                extra={'correlation_id': correlation_id})
    response = await call_next(request)
    logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}",
                extra={'correlation_id': correlation_id})
    return response

# JWT Configuration (must match gateway)
SECRET_KEY = 'your-secret-key-change-in-production'
ALGORITHM = 'HS256'

# Service URLs
NOTIFICATION_SERVICE = 'http://localhost:8004'

# Time slots (8 slots from 6 AM to 10 PM, 2-hour blocks)
TIME_SLOTS = [
    "6:00 AM - 8:00 AM",
    "8:00 AM - 10:00 AM", 
    "10:00 AM - 12:00 PM",
    "12:00 PM - 2:00 PM",
    "2:00 PM - 4:00 PM",
    "4:00 PM - 6:00 PM",
    "6:00 PM - 8:00 PM",
    "8:00 PM - 10:00 PM"
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def get_db():
    conn = sqlite3.connect("bookings.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            capacity INTEGER DEFAULT 30
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            user_email TEXT NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'cancelled')),
            created_at TEXT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms (id),
            UNIQUE(room_id, date, time_slot, status)
        )
    """)

    # Insert sample rooms
    cur.execute("SELECT COUNT(*) AS c FROM rooms")
    if cur.fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO rooms (name, capacity) VALUES (?, ?)",
            [
                ("Conference Room A", 30),
                ("Conference Room B", 20),
                ("Meeting Room C", 10),
                ("Lecture Hall D", 50)
            ]
        )

    conn.commit()
    conn.close()

init_db()

# JWT Authentication
def verify_token(authorization: Optional[str] = Header(None)):
    """Verify JWT token and extract user info"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        token = authorization.split(' ')[1]  # Bearer <token>
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Helper function to send notifications
def send_notification(user_id: str, notification_type: str, message: str, token: str):
    """Send notification to the notification service"""
    try:
        requests.post(
            f'{NOTIFICATION_SERVICE}/notifications',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'user_id': user_id,
                'type': notification_type,
                'message': message
            },
            timeout=2
        )
    except Exception as e:
        # Don't fail the main operation if notification fails
        logger.warning(f"Failed to send notification: {e}", extra={'correlation_id': 'notification'})

def notify_admins(action_type: str, message: str, actor_name: str, actor_id: str, token: str):
    """Send notification to all admin users - non-blocking"""
    try:
        # Use very short timeout and don't wait for response
        requests.post(
            f'{NOTIFICATION_SERVICE}/notifications/admin',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json={
                'type': action_type,
                'message': message,
                'actor_name': actor_name,
                'actor_id': actor_id
            },
            timeout=0.5
        )
    except Exception:
        # Silently fail - notifications are not critical
        pass

# Request Models
class BookingRequest(BaseModel):
    room_id: int
    date: str  # YYYY-MM-DD
    time_slot: str
    purpose: Optional[str] = "Meeting"

# Endpoints
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "booking",
        "version": "2.0.0",
        "time_slots": len(TIME_SLOTS)
    }

@app.get("/")
def home():
    return {
        "service": "Booking Service",
        "version": "2.0.0",
        "features": ["JWT Auth", "RBAC", "8 Time Slots", "Room Booking"],
        "time_slots": TIME_SLOTS
    }

@app.get("/rooms")
def list_rooms(user: dict = Depends(verify_token)):
    """List all available rooms"""
    conn = get_db()
    rooms = conn.execute("SELECT * FROM rooms").fetchall()
    conn.close()
    return {"rooms": [dict(room) for room in rooms]}

@app.get("/slots")
def list_time_slots(user: dict = Depends(verify_token)):
    """List all available time slots"""
    return {
        "slots": [{"index": i, "time": slot} for i, slot in enumerate(TIME_SLOTS)]
    }

@app.post("/bookings")
def create_booking(booking: BookingRequest, user: dict = Depends(verify_token), authorization: str = Header(None)):
    """Create a new booking (all authenticated users)"""
    
    # Validate time slot
    if booking.time_slot not in TIME_SLOTS:
        raise HTTPException(status_code=400, detail=f"Invalid time slot. Must be one of: {TIME_SLOTS}")
    
    conn = get_db()
    cur = conn.cursor()

    # Check if room exists
    room = cur.execute("SELECT * FROM rooms WHERE id = ?", (booking.room_id,)).fetchone()
    if not room:
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found")

    # Check for existing active booking
    existing = cur.execute("""
        SELECT * FROM bookings 
        WHERE room_id = ? AND date = ? AND time_slot = ? AND status = 'active'
    """, (booking.room_id, booking.date, booking.time_slot)).fetchone()

    if existing:
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail=f"Room {room['name']} is already booked for {booking.time_slot} on {booking.date}"
        )

    # Create booking
    cur.execute("""
        INSERT INTO bookings (room_id, user_id, user_email, date, time_slot, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        booking.room_id, 
        user['userId'], 
        user['email'],
        booking.date, 
        booking.time_slot, 
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    booking_id = cur.lastrowid
    conn.close()

    # Send notification
    token = authorization.split(' ')[1] if authorization else None
    if token:
        send_notification(
            user['userId'],
            'booking_created',
            f"Your booking for {room['name']} on {booking.date} at {booking.time_slot} was created successfully.",
            token
        )
        
        # Notify admins
        notify_admins(
            'booking_created',
            f"{user.get('name', 'User')} created a booking for {room['name']} on {booking.date} at {booking.time_slot}",
            user.get('name', 'Unknown'),
            user['userId'],
            token
        )

    return {
        "message": "Booking created successfully",
        "booking_id": booking_id,
        "room": room['name'],
        "date": booking.date,
        "time_slot": booking.time_slot
    }

@app.get("/bookings")
def list_bookings(user: dict = Depends(verify_token)):
    """
    List bookings based on user role:
    - Students: see only their own bookings with full details
    - Faculty/Admin: see all bookings with full details
    """
    conn = get_db()
    
    if user['role'] == 'student':
        # Students see only their own bookings
        bookings = conn.execute("""
            SELECT b.*, r.name as room_name
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            WHERE b.user_id = ? AND b.status = 'active'
            ORDER BY b.date DESC, b.time_slot ASC
        """, (user['userId'],)).fetchall()
    else:
        # Faculty and admin see all bookings
        bookings = conn.execute("""
            SELECT b.*, r.name as room_name
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            WHERE b.status = 'active'
            ORDER BY b.date DESC, b.time_slot ASC
        """).fetchall()
    
    conn.close()
    return {"bookings": [dict(booking) for booking in bookings]}

@app.get("/bookings/{date}")
def get_bookings_by_date(date: str, room_id: Optional[int] = None, user: dict = Depends(verify_token)):
    """Get all bookings for a specific date, optionally filtered by room
    - Students: See which slots are taken but not who booked them
    - Faculty: See all booking details including who booked
    """
    conn = get_db()
    
    if room_id:
        bookings = conn.execute("""
            SELECT b.*, r.name as room_name
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            WHERE b.date = ? AND b.room_id = ? AND b.status = 'active'
            ORDER BY b.time_slot ASC
        """, (date, room_id)).fetchall()
    else:
        bookings = conn.execute("""
            SELECT b.*, r.name as room_name
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            WHERE b.date = ? AND b.status = 'active'
            ORDER BY b.time_slot ASC
        """, (date,)).fetchall()
    
    conn.close()
    
    # For students, hide user details
    if user['role'] == 'student':
        sanitized_bookings = []
        for booking in bookings:
            b_dict = dict(booking)
            # Only show if it's their own booking or just mark as occupied
            if b_dict['user_id'] != user['userId']:
                # Hide user details for other people's bookings
                b_dict['user_id'] = 'occupied'
                b_dict['user_email'] = 'Occupied'
            sanitized_bookings.append(b_dict)
        return {"date": date, "bookings": sanitized_bookings}
    
    # Faculty see everything
    return {"date": date, "bookings": [dict(booking) for booking in bookings]}

@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, user: dict = Depends(verify_token), authorization: str = Header(None)):
    """
    Cancel a booking:
    - Students: can only cancel their own bookings
    - Faculty/Admin: can cancel any booking
    """
    conn = get_db()
    cur = conn.cursor()

    # Get booking with room info
    booking = cur.execute("""
        SELECT b.*, r.name as room_name
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.id = ? AND b.status = 'active'
    """, (booking_id,)).fetchone()

    if not booking:
        conn.close()
        raise HTTPException(status_code=404, detail="Booking not found or already cancelled")

    # Check permissions
    if user['role'] == 'student' and booking['user_id'] != user['userId']:
        conn.close()
        raise HTTPException(
            status_code=403, 
            detail="Students can only cancel their own bookings"
        )

    # Cancel booking (soft delete)
    cur.execute("""
        UPDATE bookings SET status = 'cancelled' WHERE id = ?
    """, (booking_id,))
    
    conn.commit()
    conn.close()

    # Send notification to the booking owner
    token = authorization.split(' ')[1] if authorization else None
    if token:
        send_notification(
            booking['user_id'],
            'booking_deleted',
            f"Your booking for {booking['room_name']} on {booking['date']} at {booking['time_slot']} was deleted.",
            token
        )
        
        # Notify admins about the cancellation
        actor_name = user.get('name', 'Unknown')
        affected_user_id = booking['user_id']
        
        # Determine who affected
        if user['userId'] == affected_user_id:
            notify_admins(
                'booking_deleted',
                f"{actor_name} deleted their own booking for {booking['room_name']} on {booking['date']} at {booking['time_slot']}",
                actor_name,
                user['userId'],
                token
            )
        else:
            notify_admins(
                'booking_deleted',
                f"{actor_name} deleted {booking['user_name'] if 'user_name' in booking.keys() else 'a user'}'s booking for {booking['room_name']} on {booking['date']} at {booking['time_slot']}",
                actor_name,
                user['userId'],
                token
            )

    return {
        "message": "Booking cancelled successfully",
        "notification": "Booking cancelled successfully",
        "booking_id": booking_id
    }

@app.get("/my-bookings")
def get_my_bookings(user: dict = Depends(verify_token)):
    """Get current user's active bookings"""
    conn = get_db()
    bookings = conn.execute("""
        SELECT b.*, r.name as room_name
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        WHERE b.user_id = ? AND b.status = 'active'
        ORDER BY b.date ASC, b.time_slot ASC
    """, (user['userId'],)).fetchall()
    conn.close()
    
    return {
        "user": user['email'],
        "bookings": [dict(booking) for booking in bookings]
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("📅 Booking Service starting on port 8001...", extra={'correlation_id': 'startup'})
    logger.info("🕐 Available time slots:", extra={'correlation_id': 'startup'})
    for i, slot in enumerate(TIME_SLOTS):
        logger.info(f"   {i}: {slot}", extra={'correlation_id': 'startup'})
    uvicorn.run(app, host="0.0.0.0", port=8001)