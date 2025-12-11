# Room Booking System - Frontend Guide

## Overview

The Room Booking System frontend is a fully-functional web application that allows users to:
- Register and login
- Browse available rooms
- Create new bookings
- View and manage their bookings
- Cancel bookings (only their own)
- View all bookings in the system

## File Location

The frontend is located in the `booking` folder alongside the backend services:
```
booking/
├── main.py                    # FastAPI Backend
├── schema.sql                 # Database Schema
├── frontend.html              # Frontend UI
├── requirements.txt           # Python dependencies
├── USER_BOOKING_GUIDE.md      # API Documentation
├── DOCKER_GUIDE.md
└── TESTING_GUIDE.md
```

## Why Frontend is in Service Folder?

Following the project's pattern (similar to `maintenance/frontend.html`), the frontend is placed within each service folder because:

1. **Co-location**: Frontend and backend for the same service are together
2. **Deployment**: Easier to containerize and deploy as a single unit
3. **Maintainability**: All related code is in one place
4. **Clarity**: Clear relationship between UI and backend API

If you want a separate frontend folder for a unified dashboard across all services, create:
```
frontend/
├── index.html                 # Main dashboard
├── pages/
│   ├── booking.html          # Booking system
│   ├── maintenance.html       # Maintenance tickets
│   └── ...
└── css/
    └── styles.css            # Shared styles
```

## How to Use the Frontend

### 1. Start the Services

**Terminal 1: User Management Service**
```bash
cd user-management
python main.py
# Runs on http://localhost:8002
```

**Terminal 2: Booking Service**
```bash
cd booking
python main.py
# Runs on http://localhost:8000
```

### 2. Open the Frontend

Open `booking/frontend.html` in your web browser:
- Direct: `file:///c:/dev/end-to-end-MLOPs/booking/frontend.html`
- Or serve with a local server (recommended for production):
```bash
cd booking
python -m http.server 8080
# Then visit http://localhost:8080/frontend.html
```

### 3. User Workflow

#### Registration
1. Click "Register" button
2. Fill in username, password, first name, last name
3. Click "Create Account"
4. Login with your new credentials

#### Creating a Booking
1. Login with your credentials
2. Go to "Create Booking" tab
3. Select a room from the available list
4. Choose a date (today or future dates only)
5. Choose a time slot (Morning, Afternoon, or Evening)
6. Click "Create Booking"

#### Managing Bookings
1. Click "My Bookings" tab to see your bookings
2. Each booking card shows:
   - Room name
   - Booking date
   - Time slot
   - When you booked it
3. Click "Cancel Booking" to remove a booking
4. You can only cancel your own bookings

#### Viewing All Bookings
1. Click "All Bookings" tab
2. See all bookings in the system
3. Identify which bookings are yours (marked with ✅)

## Features

### User Authentication
- **Secure Login**: Username and password authentication
- **Registration**: Create new user accounts
- **Session Storage**: User session persists via browser localStorage
- **Logout**: Clear session and return to login screen

### Room Management
- **Room Selection**: Visual grid of available rooms
- **Click to Select**: Rooms highlight when selected
- **Real-time Data**: Rooms loaded from backend

### Booking Creation
- **Date Picker**: Select booking dates (today or future only)
- **Time Slots**: Three options:
  - 🌅 Morning (08:00 - 12:00)
  - ☀️ Afternoon (12:00 - 16:00)
  - 🌙 Evening (16:00 - 20:00)
- **Duplicate Prevention**: System prevents double-booking same room/date/time
- **User Tracking**: All bookings linked to user ID

### Booking Management
- **My Bookings**: View only your bookings with full details
- **All Bookings**: Browse system bookings (read-only)
- **Cancel Booking**: Remove your own bookings
- **Authorization**: Only booking owner can cancel

### User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Alerts**: Success, error, and info notifications
- **Loading States**: Spinner indicators while fetching data
- **Empty States**: Clear messaging when no data available
- **Tab Navigation**: Easy switching between sections

## Frontend Architecture

### HTML Structure
```
Auth Section (Login/Register)
└── Main Content (Hidden until login)
    ├── Header (User Info)
    ├── Alert Container
    ├── Tab Navigation
    └── Tab Content
        ├── Create Booking
        ├── My Bookings
        └── All Bookings
```

### JavaScript Modules

#### Authentication
- `handleLogin()` - Process login request
- `handleRegister()` - Create new account
- `handleLogout()` - Clear session
- `checkAuthStatus()` - Restore session on page load

#### Room Management
- `loadRooms()` - Fetch available rooms
- `renderRooms()` - Display room grid
- `selectRoom()` - Handle room selection

#### Booking Management
- `loadMyBookings()` - Fetch user's bookings
- `loadAllBookings()` - Fetch all system bookings
- `handleCreateBooking()` - Submit new booking
- `handleCancelBooking()` - Delete booking
- `renderMyBookings()` - Display user bookings
- `renderAllBookings()` - Display all bookings

#### UI Control
- `switchTab()` - Navigate between sections
- `showAlert()` - Display notification
- `resetBookingForm()` - Clear form inputs

### CSS Features
- **Gradient Background**: Purple gradient theme
- **Card Layout**: Responsive grid system
- **Animations**: Smooth transitions and fades
- **Color Coding**: Time slot badges with colors
- **Mobile Responsive**: Breakpoints for 768px and below
- **Accessibility**: Clear color contrast and readable fonts

## API Integration

The frontend communicates with two services:

### User Management Service
```
Base URL: http://localhost:8002

POST /auth/login
POST /auth/register
```

### Booking Service
```
Base URL: http://localhost:8000

GET /rooms
POST /bookings
GET /bookings
GET /bookings/user/{user_id}
DELETE /bookings/{booking_id}
```

## Configuration

### Service URLs

Located at the top of the JavaScript section:
```javascript
const USER_SERVICE_URL = 'http://localhost:8002';
const BOOKING_SERVICE_URL = 'http://localhost:8000';
```

To change ports or server addresses, modify these variables.

### Styling

All styles are inline in the `<style>` tag. To customize:

**Theme Colors**
- Primary Blue: `#667eea`
- Dark Blue: `#5568d3`
- Red Danger: `#e74c3c`
- Gray: `#95a5a6`

**Fonts**
- Primary Font: Segoe UI, Tahoma, Geneva, Verdana, sans-serif

**Breakpoints**
- Mobile: 768px and below

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Internet Explorer: ❌ Not supported (uses modern JavaScript)

## Troubleshooting

### "Connection Error" Messages

**Problem**: Frontend can't connect to backend services

**Solution**:
1. Verify both services are running (`http://localhost:8002` and `http://localhost:8000`)
2. Check service URLs in JavaScript configuration
3. Ensure CORS is enabled in backend (already configured in `booking/main.py`)
4. Check browser console for specific error messages

### "Login Failed"

**Problem**: Invalid credentials

**Solution**:
1. Verify username and password are correct
2. Register a new account if user doesn't exist
3. Check user management service is running

### Booking Won't Create

**Problem**: "Room already booked for this time slot"

**Solution**:
1. Choose a different time slot
2. Choose a different date
3. Select a different room

### Can't Cancel Booking

**Problem**: "You can only cancel bookings you created"

**Solution**:
1. Only the user who created a booking can cancel it
2. Check you're logged in as the correct user
3. Look for your bookings in "My Bookings" tab

## Deployment

### Local Development
```bash
python -m http.server 8080
# Visit http://localhost:8080/frontend.html
```

### Docker
Include in `Dockerfile`:
```dockerfile
FROM nginx:alpine
COPY frontend.html /usr/share/nginx/html/index.html
EXPOSE 80
```

### Production Considerations

1. **CORS**: Configure to specific domain instead of "*"
2. **Security**: Use HTTPS and secure authentication tokens
3. **Error Handling**: Add comprehensive error logging
4. **Performance**: Minify HTML, CSS, and JavaScript
5. **Caching**: Implement browser caching strategies
6. **Environment Variables**: Use environment-specific URLs

## Future Enhancements

1. **Search & Filter**: Find bookings by room, date, or user
2. **Booking History**: View past bookings
3. **Recurring Bookings**: Create repeating bookings
4. **Notifications**: Email/SMS booking confirmations
5. **Admin Panel**: Admin-specific features
6. **Availability Calendar**: Visual calendar view
7. **Dark Mode**: Alternative theme
8. **Multi-language**: Support multiple languages
9. **Real-time Updates**: WebSocket notifications
10. **Export**: Download booking reports (PDF/Excel)

## File Structure Summary

```
booking/
├── frontend.html              ← YOU ARE HERE
├── main.py                    ← FastAPI backend (port 8000)
├── schema.sql                 ← Database schema
├── requirements.txt           ← Python packages
├── USER_BOOKING_GUIDE.md      ← API documentation
├── FRONTEND_GUIDE.md          ← This file
└── rooms.db                   ← SQLite database (created on first run)
```

## Support

For issues or questions:
1. Check the API documentation in `USER_BOOKING_GUIDE.md`
2. Review backend logs in terminal where `python main.py` is running
3. Check browser console (F12) for JavaScript errors
4. Verify service health at `/health` endpoints
