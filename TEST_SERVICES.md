# Testing Services Locally

## Prerequisites Needed

To run the TypeScript services (Entryway Hub, RBAC, Booking, GPA), you need:

1. **Node.js** - Install from https://nodejs.org/ (v18+ recommended)
2. **npm** - Comes with Node.js

Currently missing: `npm` is not installed on your system.

## Quick Test Options

### Option 1: Install Node.js (Recommended)

```bash
# macOS with Homebrew
brew install node

# Or download from https://nodejs.org/
```

Then run:
```bash
cd /Users/reivfts/Desktop/cloudMLOPS
./setup.sh
```

### Option 2: Test with Existing Python Services

You already have Python services working! Let's test those:

```bash
# Start your existing Maintenance Service (already has WebSocket)
cd /Users/reivfts/Desktop/cloudMLOPS/maintenance
python websocket_api.py
```

Then open `websocket_frontend.html` in your browser.

### Option 3: Manual Service Start (After installing Node.js)

```bash
# Terminal 1 - GPA Calculator (Port 4004) - No database needed!
cd /Users/reivfts/Desktop/cloudMLOPS/services/gpa-calculator-service
npm install
npm run dev

# Terminal 2 - Entryway Hub (Port 4000) - Uses in-memory users
cd /Users/reivfts/Desktop/cloudMLOPS/services/entryway-hub
npm install
npm run dev

# Test with curl:
curl -X POST http://localhost:4000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"student123"}'
```

## Current Status

✅ **Ready to use (Python)**:
- Maintenance Service (Port 8080) - Your existing NLP ticketing system

⏳ **Needs Node.js**:
- Entryway Hub (Port 4000)
- RBAC Service (Port 4001) - Also needs PostgreSQL
- Booking Service (Port 4002) - Also needs PostgreSQL
- GPA Calculator (Port 4004) - No database needed!

## Quick Win: Start Maintenance Service Now

This already works without any installation:

```bash
cd /Users/reivfts/Desktop/cloudMLOPS/maintenance
python websocket_api.py
```

Then open in browser:
- Frontend: `file:///Users/reivfts/Desktop/cloudMLOPS/maintenance/websocket_frontend.html`
- Or create a ticket via WebSocket

## Install Node.js Now

```bash
# Check if Homebrew is installed
brew --version

# If yes, install Node.js
brew install node

# Verify installation
node --version
npm --version

# Then run
cd /Users/reivfts/Desktop/cloudMLOPS
./setup.sh
```

After Node.js is installed, you can run all the TypeScript services!
