"""
API Gateway Service with JWT Authentication & Role-Based Routing
Central hub that routes to all microservices based on user role
Port: 5001

Role-Based Access:
- Admin: User Management (RBAC) only
- Faculty/Student: Booking, GPA, Maintenance, Notifications
"""

from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import jwt
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
import uuid
import os
import requests

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# JWT Configuration
SECRET_KEY = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Service URLs
SERVICES = {
    'users': 'http://localhost:8002',
    'booking': 'http://localhost:8001',
    'gpa': 'http://localhost:8003',
    'notifications': 'http://localhost:8004',
    'maintenance': 'http://localhost:8080'
}

# Database setup
def get_db():
    conn = sqlite3.connect('gateway.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'faculty', 'student')),
            created_at TEXT NOT NULL
        )
    """)
    
    # Insert default users
    cur.execute("SELECT COUNT(*) as c FROM users")
    if cur.fetchone()['c'] == 0:
        default_users = [
            ('admin-001', 'admin@example.com', 'Admin User', 'admin123', 'admin'),
            ('faculty-001', 'faculty@example.com', 'Faculty User', 'faculty123', 'faculty'),
            ('student-001', 'student@example.com', 'Student User', 'student123', 'student'),
        ]
        
        for user_id, email, name, password, role in default_users:
            cur.execute("""
                INSERT INTO users (id, email, name, password, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, email, name, password, role, datetime.utcnow().isoformat()))
    
    conn.commit()
    conn.close()

init_db()

# JWT Helper Functions
def create_access_token(user_data):
    """Create JWT access token"""
    payload = {
        'userId': user_data['id'],
        'email': user_data['email'],
        'role': user_data['role'],
        'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication Middleware
def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated

def role_required(*allowed_roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            if request.user['role'] not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# Health Check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'gateway',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Authentication Endpoints
@app.route('/auth/login', methods=['POST'])
def login():
    """Login endpoint - returns JWT token"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Missing email or password'}), 400
        
        email = data['email']
        password = data['password']
        
        # Find user
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if not user or user['password'] != password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create token
        user_data = {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        }
        
        token = create_access_token(user_data)
        
        return jsonify({
            'accessToken': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current user info from token"""
    return jsonify({
        'user': {
            'id': request.user['userId'],
            'email': request.user['email'],
            'role': request.user['role']
        }
    }), 200

@app.route('/auth/register', methods=['POST'])
def register():
    """Register new user (admin only in production)"""
    try:
        data = request.get_json()
        
        required_fields = ['email', 'password', 'name', 'role']
        if not data or not all(k in data for k in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate role
        if data['role'] not in ['admin', 'faculty', 'student']:
            return jsonify({'error': 'Invalid role'}), 400
        
        conn = get_db()
        
        # Check if user exists
        existing = conn.execute('SELECT id FROM users WHERE email = ?', (data['email'],)).fetchone()
        if existing:
            conn.close()
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        user_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO users (id, email, name, password, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, data['email'], data['name'], data['password'], 
              data['role'], datetime.utcnow().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'User registered successfully',
            'userId': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Management Endpoints
@app.route('/users', methods=['GET'])
@token_required
@role_required('admin')
def get_users():
    """Get all users (admin only)"""
    conn = get_db()
    users = conn.execute("""
        SELECT id, email, name, role, created_at 
        FROM users 
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    
    return jsonify({
        'users': [dict(user) for user in users]
    }), 200

@app.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get user by ID (own profile or admin)"""
    # Users can only view their own profile unless they're admin
    if request.user['userId'] != user_id and request.user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    user = conn.execute("""
        SELECT id, email, name, role, created_at 
        FROM users 
        WHERE id = ?
    """, (user_id,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': dict(user)}), 200

@app.route('/users/<user_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_user(user_id):
    """Delete user (admin only)"""
    conn = get_db()
    result = conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    
    if result.rowcount == 0:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    conn.close()
    return jsonify({'message': 'User deleted successfully'}), 200

# Service Info
@app.route('/', methods=['GET'])
def home():
    """Redirect to login page"""
    return send_from_directory('static', 'login.html')

# Proxy helper function
def proxy_request(service_url, path, method='GET', data=None):
    """Forward request to backend service"""
    try:
        url = f"{service_url}{path}"
        headers = {}
        
        # Forward authorization header
        if 'Authorization' in request.headers:
            headers['Authorization'] = request.headers['Authorization']
        
        # Forward request
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return jsonify({'error': 'Method not allowed'}), 405
        
        # Return response
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/json')
        )
    
    except requests.exceptions.ConnectionError:
        return jsonify({'error': f'Service unavailable: {service_url}'}), 503
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Service timeout'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ADMIN-ONLY ROUTES ====================
# User Management Service (Port 8002) - Admin Only

@app.route('/api/users', methods=['GET', 'POST'])
@token_required
@role_required('admin')
def users_list():
    """Admin only: List or create users"""
    if request.method == 'GET':
        return proxy_request(SERVICES['users'], '/users', 'GET')
    else:
        return proxy_request(SERVICES['users'], '/users', 'POST', request.get_json())

@app.route('/api/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
@role_required('admin')
def users_detail(user_id):
    """Admin only: Get, update, or delete user"""
    return proxy_request(SERVICES['users'], f'/users/{user_id}', request.method, request.get_json())

@app.route('/api/users/by-role/<role>', methods=['GET'])
@token_required
@role_required('admin')
def users_by_role(role):
    """Admin only: Get users by role"""
    return proxy_request(SERVICES['users'], f'/users/by-role/{role}', 'GET')

# ==================== FACULTY/STUDENT ROUTES ====================
# Booking Service (Port 8001)

@app.route('/api/booking/rooms', methods=['GET'])
@token_required
@role_required('faculty', 'student')
def booking_rooms():
    """Faculty/Student: List available rooms"""
    return proxy_request(SERVICES['booking'], '/rooms', 'GET')

@app.route('/api/booking/slots', methods=['GET'])
@token_required
@role_required('faculty', 'student')
def booking_slots():
    """Faculty/Student: List time slots"""
    return proxy_request(SERVICES['booking'], '/slots', 'GET')

@app.route('/api/booking/bookings', methods=['GET', 'POST'])
@token_required
@role_required('faculty', 'student')
def booking_list():
    """Faculty/Student: List or create bookings"""
    if request.method == 'GET':
        return proxy_request(SERVICES['booking'], '/bookings', 'GET')
    else:
        return proxy_request(SERVICES['booking'], '/bookings', 'POST', request.get_json())

@app.route('/api/booking/bookings/<int:booking_id>', methods=['DELETE'])
@token_required
@role_required('faculty', 'student')
def booking_delete(booking_id):
    """Faculty/Student: Cancel booking"""
    return proxy_request(SERVICES['booking'], f'/bookings/{booking_id}', 'DELETE')

@app.route('/api/booking/my-bookings', methods=['GET'])
@token_required
@role_required('faculty', 'student')
def booking_my():
    """Faculty/Student: Get my bookings"""
    return proxy_request(SERVICES['booking'], '/my-bookings', 'GET')

# GPA Calculator Service (Port 8003)

@app.route('/api/gpa/calculate', methods=['POST'])
@token_required
@role_required('faculty', 'student')
def gpa_calculate():
    """Faculty/Student: Calculate GPA"""
    return proxy_request(SERVICES['gpa'], '/calculate', 'POST', request.get_json())

# Notification Service (Port 8004)

@app.route('/api/notifications', methods=['GET', 'POST'])
@token_required
@role_required('faculty', 'student')
def notifications_list():
    """Faculty/Student: List or create notifications"""
    if request.method == 'GET':
        return proxy_request(SERVICES['notifications'], '/notifications', 'GET')
    else:
        return proxy_request(SERVICES['notifications'], '/notifications', 'POST', request.get_json())

@app.route('/api/notifications/<notif_id>/read', methods=['PUT'])
@token_required
@role_required('faculty', 'student')
def notifications_read(notif_id):
    """Faculty/Student: Mark notification as read"""
    return proxy_request(SERVICES['notifications'], f'/notifications/{notif_id}/read', 'PUT')

@app.route('/api/notifications/unread', methods=['GET'])
@token_required
@role_required('faculty', 'student')
def notifications_unread():
    """Faculty/Student: Get unread count"""
    return proxy_request(SERVICES['notifications'], '/notifications/unread', 'GET')

# Maintenance Service (Port 8080) - WebSocket handled separately

@app.route('/api/maintenance/info', methods=['GET'])
@token_required
@role_required('faculty', 'student')
def maintenance_info():
    """Faculty/Student: Get maintenance service info"""
    return jsonify({
        'service': 'Maintenance Ticketing',
        'port': 8080,
        'type': 'WebSocket',
        'url': 'ws://localhost:8080',
        'frontend': 'http://localhost:8080/websocket_frontend.html'
    }), 200

# ============================================================
# Frontend Routes - Serve HTML Pages
# ============================================================

@app.route('/login.html')
def login_page():
    """Serve login page"""
    return send_from_directory('static', 'login.html')

@app.route('/dashboard.html')
def dashboard_page():
    """Serve dashboard page"""
    return send_from_directory('static', 'dashboard.html')

@app.route('/booking.html')
def booking_page():
    """Serve booking page"""
    return send_from_directory('static', 'booking.html')

@app.route('/gpa.html')
def gpa_page():
    """Serve GPA calculator page"""
    return send_from_directory('static', 'gpa.html')

@app.route('/users.html')
def users_page():
    """Serve user management page"""
    return send_from_directory('static', 'users.html')

@app.route('/maintenance.html')
def maintenance_page():
    """Serve maintenance page"""
    return send_from_directory('static', 'maintenance.html')

@app.route('/notifications.html')
def notifications_page():
    """Serve notifications page"""
    return send_from_directory('static', 'notifications.html')

if __name__ == '__main__':
    print("🚪 API Gateway Hub starting on port 5001...")
    print("📝 Default users:")
    print("   Admin: admin@example.com / admin123")
    print("   Faculty: faculty@example.com / faculty123")
    print("   Student: student@example.com / student123")
    print("")
    print("🔐 Role-Based Access:")
    print("   Admin → User Management only")
    print("   Faculty/Student → Booking, GPA, Notifications, Maintenance")
    print("")
    print("🌐 Frontend available at: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
