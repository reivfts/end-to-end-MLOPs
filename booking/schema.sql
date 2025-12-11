-- Booking Service Database Schema
-- SQLite Database for Room Booking Management

-- Rooms Table
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,  -- Link to user management service
    username TEXT NOT NULL,
    date TEXT NOT NULL,
    time_slot TEXT NOT NULL CHECK(time_slot IN ('morning', 'afternoon', 'evening')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_bookings_room_date ON bookings(room_id, date, time_slot);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(date);
CREATE INDEX IF NOT EXISTS idx_bookings_username ON bookings(username);
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);

-- Sample data (optional - uncomment to auto-populate)
-- INSERT INTO rooms (name) VALUES ('Room A'), ('Room B'), ('Room C');
