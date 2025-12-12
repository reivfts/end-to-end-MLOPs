#!/bin/bash

# MLOps Microservices Platform - Quick Setup Script
# This script installs dependencies and sets up the development environment

set -e  # Exit on error

echo "🚀 MLOps Microservices Platform - Quick Setup"
echo "=============================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed. You'll need to install PostgreSQL, Redis, and NATS manually."
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Prerequisites check passed!"
echo ""

# Install Node.js service dependencies
echo "📦 Installing Node.js service dependencies..."
echo ""

services=("entryway-hub" "rbac-service" "booking-service" "gpa-calculator-service")

for service in "${services[@]}"; do
    echo "Installing $service..."
    cd "services/$service"
    npm install
    cd ../..
    echo "✅ $service dependencies installed"
done

echo ""
echo "✅ All Node.js dependencies installed!"
echo ""

# Check Python dependencies
echo "🐍 Checking Python (Maintenance service) dependencies..."
if [ -f "maintenance/requirements_websocket.txt" ]; then
    echo "Python requirements file found. Install with:"
    echo "  cd maintenance && pip install -r requirements_websocket.txt"
fi
echo ""

# Create .env files from examples
echo "⚙️  Creating .env files..."

if [ -f "services/entryway-hub/.env.example" ] && [ ! -f "services/entryway-hub/.env" ]; then
    cp services/entryway-hub/.env.example services/entryway-hub/.env
    echo "✅ Created entryway-hub/.env"
fi

for service in "${services[@]}"; do
    if [ ! -f "services/$service/.env" ]; then
        echo "PORT=400$((${#services[@]} - 1))" > "services/$service/.env"
        echo "NODE_ENV=development" >> "services/$service/.env"
        echo "✅ Created $service/.env"
    fi
done

echo ""

# Start infrastructure with Docker
if command -v docker-compose &> /dev/null; then
    echo "🐳 Starting infrastructure (PostgreSQL, Redis, NATS)..."
    echo "Running: docker-compose up -d postgres redis nats"
    docker-compose up -d postgres redis nats
    echo "✅ Infrastructure services started!"
    echo ""
    
    # Wait for PostgreSQL to be ready
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 5
    
    # Run database migrations
    echo "🗄️  Running database migrations..."
    echo ""
    
    if [ -d "services/rbac-service/prisma" ]; then
        echo "Running RBAC Service migrations..."
        cd services/rbac-service
        npx prisma migrate dev --name init
        npx prisma generate
        cd ../..
        echo "✅ RBAC migrations complete"
    fi
    
    if [ -d "services/booking-service/prisma" ]; then
        echo "Running Booking Service migrations..."
        cd services/booking-service
        npx prisma migrate dev --name init
        npx prisma generate
        cd ../..
        echo "✅ Booking migrations complete"
    fi
    
    echo ""
    echo "✅ Database setup complete!"
else
    echo "⚠️  Docker Compose not found. Please set up PostgreSQL, Redis, and NATS manually."
    echo "   See INSTALLATION.md for details."
fi

echo ""
echo "=============================================="
echo "✅ Setup Complete!"
echo "=============================================="
echo ""
echo "🎉 Your MLOps platform is ready!"
echo ""
echo "To start the services, run these commands in separate terminals:"
echo ""
echo "Terminal 1: cd services/entryway-hub && npm run dev         # Port 4000"
echo "Terminal 2: cd services/rbac-service && npm run dev         # Port 4001"
echo "Terminal 3: cd services/booking-service && npm run dev      # Port 4002"
echo "Terminal 4: cd services/gpa-calculator-service && npm run dev # Port 4004"
echo "Terminal 5: cd maintenance && python websocket_api.py       # Port 8080"
echo ""
echo "Or use Docker Compose:"
echo "  docker-compose up"
echo ""
echo "Default test users:"
echo "  admin@example.com / admin123 (role: admin)"
echo "  faculty@example.com / faculty123 (role: faculty)"
echo "  student@example.com / student123 (role: student)"
echo ""
echo "Documentation:"
echo "  - ARCHITECTURE.md - System architecture and API docs"
echo "  - INSTALLATION.md - Detailed setup instructions"
echo "  - PROJECT_STATUS.md - Current implementation status"
echo ""
echo "Health checks:"
echo "  http://localhost:4000/healthz - Entryway Hub"
echo "  http://localhost:4001/healthz - RBAC Service"
echo "  http://localhost:4002/healthz - Booking Service"
echo "  http://localhost:4004/healthz - GPA Calculator"
echo ""
echo "Happy coding! 🚀"
