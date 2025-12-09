from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel
from datetime import datetime
from jinja2 import Template

# Database connection
def get_db():
    conn = sqlite3.connect("rooms.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Rooms table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    # Bookings table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms (id)
        )
    """)

    # Insert sample rooms only once
    cur.execute("SELECT COUNT(*) AS c FROM rooms")
    if cur.fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO rooms (name) VALUES (?)",
            [("Room A",), ("Room B",), ("Room C",)]
        )

    conn.commit()
    conn.close()

init_db()

# Request model
class BookingRequest(BaseModel):
    room_id: int
    date: str
    username: str
    time_slot: str

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/rooms")
def list_rooms():
    conn = get_db()
    rooms = conn.execute("SELECT * FROM rooms").fetchall()
    return {"rooms": [dict(room) for room in rooms]}

@app.post("/bookings")
def create_booking(booking: BookingRequest):
    conn = get_db()
    cur = conn.cursor()

    # Check room
    room = cur.execute("SELECT * FROM rooms WHERE id = ?", (booking.room_id,)).fetchone()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Check availability
    existing = cur.execute(
        "SELECT * FROM bookings WHERE room_id = ? AND date = ? AND time_slot = ?",
        (booking.room_id, booking.date, booking.time_slot)
    ).fetchone()

    if existing:
        raise HTTPException(status_code=400, detail="Room already booked for this time slot on this date")

    # Insert booking
    cur.execute(
        "INSERT INTO bookings (room_id, username, date, time_slot, created_at) VALUES (?, ?, ?, ?, ?)",
        (booking.room_id, booking.username, booking.date, booking.time_slot, datetime.utcnow().isoformat())
    )

    conn.commit()
    booking_id = cur.lastrowid
    conn.close()

    return {"message": "Booking created", "booking_id": booking_id}

@app.get("/bookings")
def list_bookings():
    conn = get_db()
    bookings = conn.execute("""
        SELECT b.id, b.room_id, r.name as room_name, b.username, b.date, b.time_slot, b.created_at 
        FROM bookings b 
        JOIN rooms r ON b.room_id = r.id 
        ORDER BY b.date DESC, b.time_slot ASC
    """).fetchall()
    conn.close()
    return {"bookings": [dict(booking) for booking in bookings]}

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int):
    conn = get_db()
    cur = conn.cursor()

    deleted = cur.execute("DELETE FROM bookings WHERE id = ?", (booking_id,)).rowcount
    conn.commit()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Booking not found")

    conn.close()
    return {"message": "Booking deleted"}