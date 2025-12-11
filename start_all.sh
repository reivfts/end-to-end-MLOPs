#!/bin/bash

# CloudMLOPS - Start All Services
# Minimal 6-microservice architecture

echo "🚀 Starting CloudMLOPS Services..."
echo "=================================="

# Kill any existing services
pkill -f "gateway/main.py"
pkill -f "booking/main.py"
pkill -f "maintenance/websocket_api.py"
pkill -f "gpa-calculator/main.py"
pkill -f "user-management/app.py"
pkill -f "notification/app.py"

sleep 2

# Get script directory
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$DIR/venv/bin/python"

echo "Starting services..."

cd "$DIR/gateway" && $VENV main.py > /tmp/gateway.log 2>&1 &
echo "✅ Gateway (Auth) - Port 5001"

cd "$DIR/booking" && $VENV main.py > /tmp/booking.log 2>&1 &
echo "✅ Booking - Port 8001"

cd "$DIR/gpa-calculator" && $VENV main.py > /tmp/gpa.log 2>&1 &
echo "✅ GPA Calculator - Port 8003"

cd "$DIR/user-management" && $VENV app.py > /tmp/usermgmt.log 2>&1 &
echo "✅ User Management - Port 8002"

cd "$DIR/notification" && $VENV app.py > /tmp/notification.log 2>&1 &
echo "✅ Notification - Port 8004"

cd "$DIR/maintenance" && $VENV websocket_api.py > /tmp/maintenance.log 2>&1 &
echo "✅ Maintenance - Port 8080"

sleep 3

echo ""
echo "=================================="
echo "📊 All services started!"
echo ""
echo "🔐 Login Credentials:"
echo "   Admin: admin@example.com / admin123"
echo "   Faculty: faculty@example.com / faculty123"
echo "   Student: student@example.com / student123"
echo ""
echo "🌐 Dashboard: open $DIR/index.html"
echo ""
echo "📝 Logs:"
echo "   Gateway: tail -f /tmp/gateway.log"
echo "   Booking: tail -f /tmp/booking.log"
echo "   GPA: tail -f /tmp/gpa.log"
echo "   Users: tail -f /tmp/usermgmt.log"
echo "   Notifications: tail -f /tmp/notification.log"
echo "   Maintenance: tail -f /tmp/maintenance.log"
echo ""
echo "🛑 Stop all: pkill -f 'venv/bin/python'"
