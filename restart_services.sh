#!/bin/bash

# Kill existing services
lsof -ti:8002 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:8001 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:5001 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:8003 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:8004 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:8080 2>/dev/null | xargs kill -9 2>/dev/null

sleep 2

VENV="/Users/reivfts/Desktop/cloudMLOPS/venv/bin/python"

# Start all services
cd /Users/reivfts/Desktop/cloudMLOPS/user-management
$VENV app.py > /tmp/usermgmt.log 2>&1 &
echo "Started User Management (8002)"

cd /Users/reivfts/Desktop/cloudMLOPS/booking
$VENV main.py > /tmp/booking.log 2>&1 &
echo "Started Booking (8001)"

cd /Users/reivfts/Desktop/cloudMLOPS/gpa-calculator
$VENV main.py > /tmp/gpa.log 2>&1 &
echo "Started GPA Calculator (8003)"

cd /Users/reivfts/Desktop/cloudMLOPS/notification
$VENV app.py > /tmp/notification.log 2>&1 &
echo "Started Notification (8004)"

cd /Users/reivfts/Desktop/cloudMLOPS/maintenance
$VENV websocket_api.py > /tmp/maintenance.log 2>&1 &
echo "Started Maintenance (8080)"

cd /Users/reivfts/Desktop/cloudMLOPS/gateway
$VENV main.py > /tmp/gateway.log 2>&1 &
echo "Started Gateway (5001)"

sleep 3

echo ""
echo "All services started!"
echo "Gateway: http://localhost:5001"
