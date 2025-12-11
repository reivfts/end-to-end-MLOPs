# Quick Start Guide - 5 Minute Setup

Get the entire MLOps platform running in 5 minutes using Python virtual environments.

## 📋 Prerequisites

- **Python 3.8+** installed
- **Windows PowerShell** (built-in)
- **Modern web browser**
- **c:\dev\end-to-end-MLOps** directory (project root)

## ⚡ Quick Setup (6 Steps)

### Step 1: Open 5 Terminal Windows

Open PowerShell 5 times, or use multiple tabs in one terminal. We'll run one service in each.

### Step 2: Terminal 1 - Booking Service (Port 8000)

Copy and run these commands line by line:

```powershell
cd c:\dev\end-to-end-MLOps\booking
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://localhost:8000
INFO:     Application startup complete
```

### Step 3: Terminal 2 - Maintenance Service (Port 8001)

Copy and run these commands:

```powershell
cd c:\dev\end-to-end-MLOps\maintenance
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Expected Output:**
```
WARNING in flask from werkzeug.serving import run_simple
 * Running on http://localhost:8001
 * Press CTRL+C to quit
```

### Step 4: Terminal 3 - User Management Service (Port 8002)

Copy and run these commands:

```powershell
cd c:\dev\end-to-end-MLOps\user-management
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:8002
 * Press CTRL+C to quit
```

### Step 5: Terminal 4 - API Gateway (Port 8080)

Copy and run these commands:

```powershell
cd c:\dev\end-to-end-MLOps\gateway
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Expected Output:**
```
 * Running on http://localhost:8080
 * Press CTRL+C to quit
```

### Step 6: Terminal 5 - Frontend HTTP Server (Port 3000)

Copy and run this command:

```powershell
cd c:\dev\end-to-end-MLOps
python -m http.server 3000 --directory frontend
```

**Expected Output:**
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

## 🌐 Access the Application

Once all 5 services are running, open your web browser and navigate to:

```
http://localhost:3000/index.html
```

## ✅ Verify Everything Works

### 1. Check Services Running

In browser, go to: `http://localhost:8080/services/health`

Should show:
```json
{
  "gateway": "OK",
  "booking": "OK",
  "maintenance": "OK",
  "user": "OK"
}
```

### 2. Create Test Account

1. Click "Sign Up" button
2. Enter any username, email, and password
3. Click "Sign Up"

Example:
```
Username: testuser
Email: test@example.com
Password: password123
```

### 3. Login

1. Click "Login" button
2. Use your test account credentials
3. Click "Login"

### 4. Create Booking

1. Click "Booking" service card
2. Select a room (Room 101, 102, 103, etc.)
3. Choose a date (today or future)
4. Select a time slot
5. Click "Create Booking"

### 5. Create Maintenance Ticket

1. Click "Maintenance" service card
2. Enter issue description
3. Set priority (Low, Medium, High)
4. Click "Create Ticket"

## 📋 Service Ports & URLs

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Booking | 8000 | http://localhost:8000 |
| Maintenance | 8001 | http://localhost:8001 |
| User Management | 8002 | http://localhost:8002 |
| API Gateway | 8080 | http://localhost:8080 |

## 🔧 Virtual Environment Basics

### Activate Virtual Environment
```powershell
cd c:\dev\end-to-end-MLOps\{service}
.\venv\Scripts\activate
```

### Deactivate Virtual Environment
```powershell
deactivate
```

### Reinstall Dependencies
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Create Fresh Virtual Environment
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

## 🛑 Stop Services

Press **CTRL+C** in each terminal to stop services.

## 🚀 Restart All Services

If services crash or stop:

1. Press **CTRL+C** in each terminal
2. Repeat Steps 2-6 above to restart

Or kill all Python processes:
```powershell
Get-Process python | Stop-Process -Force
```

Then restart services.

## 🐛 Troubleshooting

### "Port Already in Use"

If you see an error like `Address already in use`, kill existing processes:

```powershell
Get-Process python | Stop-Process -Force
```

Then restart services.

### "Module Not Found" Error

Make sure virtual environment is activated:

```powershell
.\venv\Scripts\activate
```

Then reinstall dependencies:

```powershell
pip install -r requirements.txt
```

### "Cannot Connect to Service"

Check that all 5 services are running in their terminals. You should see output like:
- Booking: `Uvicorn running on http://localhost:8000`
- Maintenance: `Running on http://localhost:8001`
- User: `Running on http://127.0.0.1:8002`
- Gateway: `Running on http://localhost:8080`
- Frontend: `Serving HTTP on :: port 3000`

### Database Error

Delete old database and restart:

```powershell
rm c:\dev\end-to-end-MLOps\booking\rooms.db
```

Restart the booking service (Terminal 2) - database will recreate automatically.

### Login Issues

Clear browser cache:
1. Press **F12** to open Developer Tools
2. Go to "Application" tab
3. Click "Clear site data"
4. Refresh page

Or try in private/incognito browser window.

## 📚 Common Commands

### Check Python Version
```powershell
python --version
```

### List Running Python Processes
```powershell
Get-Process python
```

### Install Package in Virtual Environment
```powershell
.\venv\Scripts\activate
pip install package-name
```

### Update All Packages
```powershell
.\venv\Scripts\activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

## 🎯 Next Steps

1. **Read README.md** for full documentation
2. **Explore API endpoints** in service main.py files
3. **Modify frontend** HTML files to customize UI
4. **Add new services** following project guidelines
5. **Deploy to production** (see README.md)

## 📞 Support

If you encounter issues:

1. **Check terminal outputs** - error messages are helpful
2. **Open browser console** (F12) - check for API errors
3. **Verify all 5 services running** - check each terminal
4. **Check ports available** - no service should be blocked
5. **Review README.md** - full documentation

## ✨ What's Included

- ✅ Booking service with room management
- ✅ Maintenance ticket system
- ✅ User authentication with registration
- ✅ API gateway for request routing
- ✅ Frontend with login/signup
- ✅ SQLite database for bookings
- ✅ CORS enabled on all services
- ✅ Virtual environments for each service

---

**Ready to start?** Follow the 6 steps above and you'll be running in 5 minutes!

For detailed documentation, see [README.md](README.md)
