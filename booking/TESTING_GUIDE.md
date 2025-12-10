# Booking Service - Testing Guide

This guide explains how to test the booking service with its front-end.

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Setup & Installation

### 1. Install Dependencies

```powershell
cd c:\dev\end-to-end-MLOPs\booking
pip install -r requirements.txt
```

### 2. Start the Booking Service

Run the FastAPI server:

```powershell
cd c:\dev\end-to-end-MLOPs\booking
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [1234]
```

### 3. Open the Front-End

Open the front-end in your browser:

```
file:///c:/dev/end-to-end-MLOPs/booking/booking.html
```

Or simply open the `booking.html` file directly in your browser.

## Testing Workflows

### Test 1: Basic Room Booking

1. **Fill in the form:**
   - Enter your name (e.g., "John Doe")
   - Select a room (click on "Room A", "Room B", or "Room C")
   - Pick a future date using the date picker

2. **Submit booking:**
   - Click "Book Room" button
   - You should see a success message: "Booking created successfully! 🎉"

3. **Verify:**
   - The form should clear
   - The booking should appear in the "Current Bookings" section on the right

### Test 2: Duplicate Booking Prevention

1. **Create a booking** (following Test 1)
2. **Try to book the same room on the same date:**
   - Select the same room
   - Select the same date
   - Click "Book Room"
   - You should get an error: "Room already booked on this date"

### Test 3: Cancel a Booking

1. **Create a booking** (following Test 1)
2. **Cancel it:**
   - In the "Current Bookings" section, click the "Cancel" button
   - Confirm the cancellation dialog
   - The booking should disappear from the list

### Test 4: Multiple Concurrent Bookings

1. **Create multiple bookings:**
   - Book Room A on Dec 15
   - Book Room B on Dec 15
   - Book Room C on Dec 16
   
2. **Verify:**
   - All bookings should appear in the Current Bookings list
   - You can book the same room on different dates (this is allowed)

### Test 5: Form Validation

1. **Try to book without entering a name:**
   - Leave the name field empty
   - Click "Book Room"
   - You should see error: "Please enter your name"

2. **Try to book without selecting a room:**
   - Enter a name
   - Don't select a room
   - Click "Book Room"
   - You should see error: "Please select a room"

3. **Try to book without selecting a date:**
   - Enter a name
   - Select a room
   - Don't select a date
   - Click "Book Room"
   - You should see error: "Please select a date"

### Test 6: Real-time Updates

1. **Open the front-end in two browser windows/tabs**
2. **In window 1:**
   - Create a booking
3. **In window 2:**
   - Wait for the bookings list to auto-refresh (every 5 seconds)
   - The new booking from window 1 should appear automatically

## API Testing (Using PowerShell)

You can also test the API directly using `curl` or PowerShell's `Invoke-RestMethod`:

### Get all rooms
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/rooms" -Method Get
```

### Create a booking
```powershell
$body = @{
    room_id = 1
    date = "2025-12-20"
    username = "Test User"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/bookings" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

### Get all bookings
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/bookings" -Method Get
```

### Delete a booking (replace 1 with actual booking ID)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/bookings/1" -Method Delete
```

## Database Management

### View the database (SQLite)

The database file is `rooms.db` in the booking folder.

To view it, you can use any SQLite viewer or:

```powershell
# Install sqlite3 if needed
# View all bookings
sqlite3 rooms.db "SELECT * FROM bookings"
sqlite3 rooms.db "SELECT * FROM rooms"
```

### Reset the database

Delete the `rooms.db` file and restart the service:

```powershell
Remove-Item rooms.db
# Then restart the service
```

## Troubleshooting

### Issue: "Unable to connect to http://localhost:8000"

**Solution:** 
- Make sure the booking service is running (`uvicorn main:app --reload`)
- Check that port 8000 is not blocked by a firewall
- Try accessing `http://localhost:8000/rooms` in your browser to verify the API is working

### Issue: CORS errors in browser console

**Solution:**
- The service has CORS enabled for all origins (`allow_origins=["*"]`)
- Make sure you're using `http://localhost:8000` (not https)
- Clear browser cache and reload

### Issue: Bookings list shows "Booking list view not available"

**Solution:**
- The GET `/bookings` endpoint might not be available
- Check that your `main.py` has the latest version with the `@app.get("/bookings")` endpoint
- Restart the service

### Issue: Can't select past dates

**Solution:**
- This is intentional - the date picker is set to minimum date as today
- Future dates are allowed

## Performance Testing

### Test with many bookings

Create 50+ bookings to test performance:

```powershell
# PowerShell script to create 50 bookings
$baseDate = [datetime]"2025-12-10"
for ($i = 0; $i -lt 50; $i++) {
    $date = $baseDate.AddDays($i).ToString("yyyy-MM-dd")
    $room = (($i % 3) + 1)  # Cycle through rooms 1-3
    
    $body = @{
        room_id = $room
        date = $date
        username = "User$i"
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://localhost:8000/bookings" `
      -Method Post `
      -ContentType "application/json" `
      -Body $body
    
    Write-Host "Created booking $($i+1)"
}
```

Then open the front-end and verify it loads and displays all bookings smoothly.

## Summary

The booking service is fully functional and tested when:
- ✅ You can create bookings via the front-end
- ✅ Duplicate bookings are prevented
- ✅ You can cancel bookings
- ✅ The bookings list auto-refreshes
- ✅ Form validation works correctly
- ✅ API endpoints respond correctly

Happy testing!
