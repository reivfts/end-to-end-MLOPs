# User-Based Booking System Implementation Guide

## Overview
The booking system now integrates with the user management service to track which user created each booking. Only the user who created a booking can cancel it.

## Key Features

### 1. User-Linked Bookings
- Each booking is now linked to a specific user via `user_id`
- The `user_id` comes from the user management service during login
- Bookings track both `user_id` (UUID) and `username` (readable name)

### 2. Authorization Control
- Only the user who created a booking can cancel it
- Attempting to cancel someone else's booking returns a 403 Forbidden error
- The system verifies ownership before processing cancellations

### 3. User-Specific Queries
- Users can view only their own bookings
- Admins can view all bookings

## API Endpoints

### Create a Booking
**Endpoint:** `POST /bookings`

**Request Body:**
```json
{
    "room_id": 1,
    "date": "2025-12-20",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "time_slot": "morning"
}
```

**Response (Success - 200):**
```json
{
    "message": "Booking created successfully",
    "booking_id": 1,
    "booking": {
        "id": 1,
        "room_id": 1,
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "john_doe",
        "date": "2025-12-20",
        "time_slot": "morning"
    }
}
```

**Response (Room Already Booked - 400):**
```json
{
    "detail": "Room already booked for this time slot on this date"
}
```

### Get All Bookings
**Endpoint:** `GET /bookings`

**Response:**
```json
{
    "bookings": [
        {
            "id": 1,
            "room_id": 1,
            "room_name": "Room A",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "john_doe",
            "date": "2025-12-20",
            "time_slot": "morning",
            "created_at": "2025-12-10T10:30:00"
        }
    ]
}
```

### Get User's Bookings
**Endpoint:** `GET /bookings/user/{user_id}`

**Example:** `GET /bookings/user/550e8400-e29b-41d4-a716-446655440000`

**Response:**
```json
{
    "bookings": [
        {
            "id": 1,
            "room_id": 1,
            "room_name": "Room A",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "john_doe",
            "date": "2025-12-20",
            "time_slot": "morning",
            "created_at": "2025-12-10T10:30:00"
        }
    ],
    "total": 1
}
```

### Cancel a Booking
**Endpoint:** `DELETE /bookings/{booking_id}`

**Request Body:**
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (Success - 200):**
```json
{
    "message": "Booking cancelled successfully",
    "cancelled_booking": {
        "id": 1,
        "room_name": "john_doe",
        "date": "2025-12-20",
        "time_slot": "morning"
    }
}
```

**Response (Unauthorized - 403):**
```json
{
    "detail": "You can only cancel bookings you created"
}
```

**Response (Booking Not Found - 404):**
```json
{
    "detail": "Booking not found"
}
```

## Workflow Example

### Step 1: User Registration/Login
```bash
POST http://localhost:8002/auth/login
{
    "username": "john_doe",
    "password": "password123"
}

# Response:
{
    "message": "Login successful",
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "john_doe",
        "role": "student",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

**Save the `user_id` from the response!**

### Step 2: Create a Booking
```bash
POST http://localhost:8000/bookings
{
    "room_id": 1,
    "date": "2025-12-20",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "time_slot": "morning"
}

# Response:
{
    "message": "Booking created successfully",
    "booking_id": 1,
    "booking": {...}
}
```

**Save the `booking_id` from the response!**

### Step 3: View Your Bookings
```bash
GET http://localhost:8000/bookings/user/550e8400-e29b-41d4-a716-446655440000

# Response:
{
    "bookings": [
        {
            "id": 1,
            "room_id": 1,
            "room_name": "Room A",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "john_doe",
            "date": "2025-12-20",
            "time_slot": "morning",
            "created_at": "2025-12-10T10:30:00"
        }
    ],
    "total": 1
}
```

### Step 4: Cancel a Booking
```bash
DELETE http://localhost:8000/bookings/1
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
}

# Response:
{
    "message": "Booking cancelled successfully",
    "cancelled_booking": {
        "id": 1,
        "room_name": "john_doe",
        "date": "2025-12-20",
        "time_slot": "morning"
    }
}
```

## Database Schema

### Bookings Table
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,              -- UUID from user management
    username TEXT NOT NULL,             -- Readable username
    date TEXT NOT NULL,                 -- Booking date (YYYY-MM-DD)
    time_slot TEXT NOT NULL,            -- 'morning', 'afternoon', or 'evening'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms (id)
);
```

## Important Notes

1. **User ID Format**: The `user_id` should be the UUID returned by the user management service during login
2. **Authorization**: Always include the user's `user_id` when canceling a booking
3. **Time Slots**: Valid time slots are: `morning`, `afternoon`, `evening`
4. **Date Format**: Use ISO format for dates: `YYYY-MM-DD`
5. **Double Booking Prevention**: The system prevents double-booking for the same room, date, and time slot
6. **Timestamps**: All bookings automatically record when they were created

## Security Considerations

- User IDs are required for all booking operations
- Authorization is enforced at the API level
- Users cannot modify or cancel other users' bookings
- The system validates user ownership before deletion
