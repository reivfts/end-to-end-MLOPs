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

# Endpoints
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'user-management', 'version': '2.0.0'}), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'User Management Service',
        'version': '2.0.0',
        'features': ['JWT Auth', 'User CRUD', 'Role Management']
    }), 200

@app.route('/users', methods=['GET'])
@token_required
@admin_required
def get_all_users():
    """Get all users (admin only)"""
    conn = get_db()
    users = conn.execute("SELECT id, email, name, role, created_at FROM users").fetchall()
    conn.close()
    return jsonify({'users': [dict(user) for user in users]}), 200

@app.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get user by ID (own profile or admin)"""
    if request.user['userId'] != user_id and request.user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    user = conn.execute("SELECT id, email, name, role, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': dict(user)}), 200

@app.route('/users', methods=['POST'])
@token_required
@admin_required
def create_user():
    """Create new user (admin only)"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'name', 'role']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if data['role'] not in ['admin', 'faculty', 'student']:
            return jsonify({'error': 'Invalid role'}), 400
        
        conn = get_db()
        
        # Check if email exists
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (data['email'],)).fetchone()
        if existing:
            conn.close()
            return jsonify({'error': 'Email already exists'}), 409
        
        user_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO users (id, email, name, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, data['email'], data['name'], data['role'], datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'User created', 'userId': user_id}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """Update user (own profile or admin)"""
    if request.user['userId'] != user_id and request.user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        conn = get_db()
        
        # Build update query
        updates = []
        params = []
        
        if 'name' in data:
            updates.append("name = ?")
            params.append(data['name'])
        
        # Only admin can change roles
        if 'role' in data:
            if request.user['role'] != 'admin':
                conn.close()
                return jsonify({'error': 'Only admins can change roles'}), 403
            if data['role'] not in ['admin', 'faculty', 'student']:
                conn.close()
                return jsonify({'error': 'Invalid role'}), 400
            updates.append("role = ?")
            params.append(data['role'])
        
        if not updates:
            conn.close()
            return jsonify({'error': 'No valid fields to update'}), 400
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        result = conn.execute(query, params)
        conn.commit()
        
        if result.rowcount == 0:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        conn.close()
        return jsonify({'message': 'User updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    conn = get_db()
    result = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    
    if result.rowcount == 0:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    conn.close()
    return jsonify({'message': 'User deleted successfully'}), 200

@app.route('/users/by-role/<role>', methods=['GET'])
@token_required
def get_users_by_role(role):
    """Get users by role"""
    if role not in ['admin', 'faculty', 'student']:
        return jsonify({'error': 'Invalid role'}), 400
    
    conn = get_db()
    users = conn.execute(
        "SELECT id, email, name, role, created_at FROM users WHERE role = ?", 
        (role,)
    ).fetchall()
    conn.close()
    
    return jsonify({'role': role, 'users': [dict(user) for user in users]}), 200

if __name__ == '__main__':
    print("👥 User Management Service starting on port 8002...")
    print("✅ Default users created (admin, faculty, student)")
    app.run(host='0.0.0.0', port=8002, debug=True)
