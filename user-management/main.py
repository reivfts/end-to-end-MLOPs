"""
User Management Service with JWT Auth
Simple CRUD for users and roles
Port: 8002
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
import sqlite3
from functools import wraps
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# JWT Configuration
SECRET_KEY = 'your-secret-key-change-in-production'
ALGORITHM = 'HS256'

# Database setup
def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'faculty', 'student')),
            created_at TEXT NOT NULL
        )
    """)
    
    # Insert default users
    conn.execute("SELECT COUNT(*) as c FROM users")
    if conn.fetchone()['c'] == 0:
        users_data = [
            (str(uuid.uuid4()), 'admin@example.com', 'Admin User', 'admin'),
            (str(uuid.uuid4()), 'faculty@example.com', 'Faculty User', 'faculty'),
            (str(uuid.uuid4()), 'student@example.com', 'Student User', 'student'),
        ]
        conn.executemany(
            "INSERT INTO users (id, email, name, role, created_at) VALUES (?, ?, ?, ?, ?)",
            [(uid, email, name, role, datetime.utcnow().isoformat()) for uid, email, name, role in users_data]
        )
        conn.commit()
    conn.close()

init_db()

# JWT Middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'user') or request.user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint required for microservices"""
    return jsonify({
        "status": "healthy",
        "service": "user-management",
        "version": "1.0.0"
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Basic endpoint to test the service is running"""
    return jsonify({
        "message": "User Management Service is running",
        "service": "user-management"
    }), 200

@app.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({"error": "Missing required fields: username, password"}), 400
        
        username = data['username']
        password = data['password']
        
        # Check if user already exists
        if username in users:
            return jsonify({"error": "Username already exists"}), 409
        
        # Create user
        user_id = str(uuid.uuid4())
        
        users[username] = {
            'id': user_id,
            'username': username,
            'password': password,  # Store password as plain text for simplicity
            'role': data.get('role', 'student'),  # Default to student
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', '')
        }
        
        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id,
            "username": username
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({"error": "Missing username or password"}), 400
        
        username = data['username']
        password = data['password']
        
        # Check if user exists
        if username not in users:
            return jsonify({"error": "Invalid username or password"}), 401
        
        user = users[username]
        
        # Verify password (simple string comparison)
        if user['password'] != password:
            return jsonify({"error": "Invalid username or password"}), 401
        
        # Return user info (without password)
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "role": user['role'],
                "first_name": user['first_name'],
                "last_name": user['last_name']
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['GET'])
def get_all_users():
    """Get all users (admin only for now)"""
    try:
        # Return all users without passwords
        user_list = []
        for username, user_data in users.items():
            user_list.append({
                "id": user_data['id'],
                "username": user_data['username'],
                "role": user_data['role'],
                "first_name": user_data['first_name'],
                "last_name": user_data['last_name']
            })
        
        return jsonify({
            "users": user_list,
            "total": len(user_list)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/<username>', methods=['GET'])
def get_user_by_username(username):
    """Get user by username (for service-to-service calls)"""
    try:
        # Check if user exists
        if username not in users:
            return jsonify({"error": "User not found"}), 404
        
        user = users[username]
        
        # Return user info (without password)
        return jsonify({
            "user": {
                "id": user['id'],
                "username": user['username'],
                "role": user['role'],
                "first_name": user['first_name'],
                "last_name": user['last_name']
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user by ID (admin only)"""
    try:
        # Find user by ID
        username_to_delete = None
        for username, user_data in users.items():
            if user_data['id'] == user_id:
                username_to_delete = username
                break
        
        if username_to_delete is None:
            return jsonify({"error": "User not found"}), 404
        
        # Delete the user
        deleted_user = users.pop(username_to_delete)
        
        return jsonify({
            "message": "User deleted successfully",
            "deleted_user": {
                "id": deleted_user['id'],
                "username": deleted_user['username']
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask development server
    app.run(host='0.0.0.0', port=8002, debug=True)