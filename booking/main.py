from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Database connection
DB_PATH = r"rooms.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database from schema.sql if it doesn't exist."""
    if os.path.exists(DB_PATH):
        print(f"✅ Database '{DB_PATH}' already exists.")
        return
    
    schema_file = "schema.sql"
    if not os.path.exists(schema_file):
        print(f"❌ Error: {schema_file} not found!")
        return
    
    try:
        print(f"\n📂 Loading schema from {schema_file}...")
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Read and execute schema.sql
        with open(schema_file, 'r') as f:
            schema = f.read()
        
        cur.executescript(schema)
        conn.commit()
        print("✅ Database schema created successfully!")
        
        # Insert sample rooms
        print("\n📝 Inserting sample rooms...")
        sample_rooms = [
            ("Room A",),
            ("Room B",),
            ("Room C",)
        ]
        
        cur.executemany("INSERT INTO rooms (name) VALUES (?)", sample_rooms)
        conn.commit()
        print("✅ Sample rooms inserted:")
        print("   - Room A")
        print("   - Room B")
        print("   - Room C")
        
        conn.close()
        print(f"\n✅ Database initialization complete!\n")
        
    except sqlite3.IntegrityError as e:
        print(f"\n❌ Integrity error (duplicate rooms?): {e}")
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

# Initialize database on startup
init_db()

# Request models
class BookingRequest(BaseModel):
    room_id: int
    date: str
    user_id: str  # Add user_id
    username: str
    time_slot: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "room_id": 1,
                "date": "2025-12-20",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john_doe",
                "time_slot": "morning"
            }
        }

class CancelBookingRequest(BaseModel):
    user_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

# Response models
class Room(BaseModel):
    id: int
    name: str

class Booking(BaseModel):
    id: int
    room_id: int
    room_name: Optional[str] = None
    user_id: str
    username: str
    date: str
    time_slot: str
    created_at: Optional[str] = None

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/rooms", response_model=dict, tags=["Rooms"])
def list_rooms():
    """
    Get all available rooms.
    
    Returns a list of all rooms in the system.
    """
    try:
        conn = get_db()
        rooms = conn.execute("SELECT * FROM rooms").fetchall()
        conn.close()
        return {"rooms": [dict(room) for room in rooms]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/bookings", tags=["Bookings"])
def create_booking(booking: BookingRequest):
    """
    Create a new room booking.
    
    - **room_id**: ID of the room to book
    - **date**: Date of booking (YYYY-MM-DD)
    - **user_id**: ID of the user making the booking (from user management)
    - **username**: Username of the person making the booking
    - **time_slot**: Time slot (morning, afternoon, or evening)
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        # Check room exists
        room = cur.execute("SELECT * FROM rooms WHERE id = ?", (booking.room_id,)).fetchone()
        if not room:
            conn.close()
            raise HTTPException(status_code=404, detail="Room not found")

        # Check availability
        existing = cur.execute(
            "SELECT * FROM bookings WHERE room_id = ? AND date = ? AND time_slot = ?",
            (booking.room_id, booking.date, booking.time_slot)
        ).fetchone()

        if existing:
            conn.close()
            raise HTTPException(status_code=400, detail="Room already booked for this time slot on this date")

        # Insert booking
        cur.execute(
            "INSERT INTO bookings (room_id, user_id, username, date, time_slot) VALUES (?, ?, ?, ?, ?)",
            (booking.room_id, booking.user_id, booking.username, booking.date, booking.time_slot)
        )

        conn.commit()
        booking_id = cur.lastrowid
        conn.close()

        return {
            "message": "Booking created successfully",
            "booking_id": booking_id,
            "booking": {
                "id": booking_id,
                "room_id": booking.room_id,
                "user_id": booking.user_id,
                "username": booking.username,
                "date": booking.date,
                "time_slot": booking.time_slot
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/bookings", response_model=dict, tags=["Bookings"])
def list_bookings():
    """
    Get all current bookings.
    
    Returns a list of all bookings sorted by date and time slot.
    """
    try:
        conn = get_db()
        bookings = conn.execute("""
            SELECT b.id, b.room_id, r.name as room_name, b.user_id, b.username, b.date, b.time_slot, b.created_at
            FROM bookings b 
            JOIN rooms r ON b.room_id = r.id 
            ORDER BY b.date DESC, b.time_slot ASC
        """).fetchall()
        conn.close()
        return {"bookings": [dict(booking) for booking in bookings]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/bookings/user/{user_id}", response_model=dict, tags=["Bookings"])
def list_user_bookings(user_id: str):
    """
    Get all bookings for a specific user.
    
    - **user_id**: ID of the user to fetch bookings for
    """
    try:
        conn = get_db()
        bookings = conn.execute("""
            SELECT b.id, b.room_id, r.name as room_name, b.user_id, b.username, b.date, b.time_slot, b.created_at
            FROM bookings b 
            JOIN rooms r ON b.room_id = r.id 
            WHERE b.user_id = ?
            ORDER BY b.date DESC, b.time_slot ASC
        """, (user_id,)).fetchall()
        conn.close()
        return {"bookings": [dict(booking) for booking in bookings], "total": len(bookings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/bookings/{booking_id}", tags=["Bookings"])
def delete_booking(booking_id: int, cancel_request: CancelBookingRequest):
    """
    Cancel a booking. Only the user who created the booking can cancel it.
    
    - **booking_id**: ID of the booking to cancel
    - **user_id**: ID of the user attempting to cancel (from request body)
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        # Fetch the booking
        booking = cur.execute(
            "SELECT * FROM bookings WHERE id = ?", (booking_id,)
        ).fetchone()

        if not booking:
            conn.close()
            raise HTTPException(status_code=404, detail="Booking not found")

        # Verify the user is the booking creator
        if booking['user_id'] != cancel_request.user_id:
            conn.close()
            raise HTTPException(
                status_code=403,
                detail="You can only cancel bookings you created"
            )

        # Delete the booking
        cur.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()

        return {
            "message": "Booking cancelled successfully",
            "cancelled_booking": {
                "id": booking_id,
                "room_name": booking['username'],
                "date": booking['date'],
                "time_slot": booking['time_slot']
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("\n🏨 Booking Service starting on http://localhost:8000")
    print("\n📚 Available endpoints:")
    print("  - GET    /rooms              (List all rooms)")
    print("  - POST   /bookings           (Create new booking)")
    print("  - GET    /bookings           (List all bookings)")
    print("  - GET    /bookings/user/{id} (Get user's bookings)")
    print("  - DELETE /bookings/{id}      (Cancel booking)")
    print("  - GET    /health             (Health check)")
    print("\n" + "="*60 + "\n")
    uvicorn.run(app, host="localhost", port=8000)