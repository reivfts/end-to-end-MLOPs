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
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(correlation_id)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/usermgmt.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Add correlation ID to all requests
@app.before_request
def before_request():
    request.correlation_id = str(uuid.uuid4())
    logger.info(f"Request started: {request.method} {request.path}",
                extra={'correlation_id': request.correlation_id})

@app.after_request
def after_request(response):
    logger.info(f"Request completed: {request.method} {request.path} - Status: {response.status_code}",
                extra={'correlation_id': getattr(request, 'correlation_id', 'N/A')})
    return response

# Gateway service URL for creating login credentials
GATEWAY_URL = 'http://localhost:5001'
NOTIFICATION_SERVICE = 'http://localhost:8004'

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
    cur = conn.cursor()
    count = cur.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
    if count == 0:
        users_data = [
            (str(uuid.uuid4()), 'admin@example.com', 'Admin User', 'admin'),
            (str(uuid.uuid4()), 'faculty@example.com', 'Faculty User', 'faculty'),
            (str(uuid.uuid4()), 'student@example.com', 'Student User', 'student'),
        ]
        cur.executemany(
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

def notify_admins(action_type, message, actor_name, actor_id, token):
    """Send notification to all admin users - non-blocking"""
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = {
            'type': action_type,
            'message': message,
            'actor_name': actor_name,
            'actor_id': actor_id
        }
        # Very short timeout, don't block the main operation
        requests.post(f"{NOTIFICATION_SERVICE}/notifications/admin", 
                     json=payload, headers=headers, timeout=0.5)
    except Exception:
        # Silently fail - notifications are not critical
        pass

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
        
        # Password is required for login credentials
        if 'password' not in data:
            return jsonify({'error': 'Password is required'}), 400
        
        if data['role'] not in ['admin', 'faculty', 'student']:
            return jsonify({'error': 'Invalid role'}), 400
        
        conn = get_db()
        
        # Check if email exists
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (data['email'],)).fetchone()
        if existing:
            conn.close()
            return jsonify({'error': 'Email already exists'}), 409
        
        user_id = str(uuid.uuid4())
        
        # Create user in user-management database
        conn.execute(
            "INSERT INTO users (id, email, name, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, data['email'], data['name'], data['role'], datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        
        # Also create login credentials in gateway by calling its register endpoint
        try:
            register_response = requests.post(
                f'{GATEWAY_URL}/auth/register',
                json={
                    'email': data['email'],
                    'password': data['password'],
                    'name': data['name'],
                    'role': data['role']
                },
                timeout=5
            )
            
            if not register_response.ok:
                # Rollback - delete from user-management database
                conn = get_db()
                conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                conn.close()
                
                error_msg = register_response.json().get('error', 'Failed to create login credentials')
                return jsonify({'error': f'Failed to create login credentials: {error_msg}'}), 500
                
        except requests.exceptions.RequestException as e:
            # Rollback - delete from user-management database  
            conn = get_db()
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            
            return jsonify({'error': f'Failed to connect to authentication service: {str(e)}'}), 500
        
        # Notify admins
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            notify_admins(
                'user_created',
                f"Created new {data['role']} user: {data['name']} ({data['email']})",
                request.user.get('name', 'Unknown'),
                request.user['userId'],
                token
            )
        
        return jsonify({'message': 'User created successfully with login credentials', 'userId': user_id}), 201
        
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
        
        # Get user email for syncing with gateway
        user = conn.execute("SELECT email FROM users WHERE id = ?", (user_id,)).fetchone()
        user_email = user['email'] if user else None
        
        conn.close()
        
        # Sync role change with gateway if role was updated
        if 'role' in data and user_email:
            try:
                auth_header = request.headers.get('Authorization')
                
                # Get gateway users to find matching user by email
                gateway_users_response = requests.get(
                    f'{GATEWAY_URL}/users',
                    headers={'Authorization': auth_header},
                    timeout=5
                )
                
                if gateway_users_response.ok:
                    gateway_users = gateway_users_response.json().get('users', [])
                    gateway_user = next((u for u in gateway_users if u['email'] == user_email), None)
                    
                    if gateway_user:
                        # Update role in gateway
                        update_response = requests.put(
                            f'{GATEWAY_URL}/users/{gateway_user["id"]}',
                            headers={'Authorization': auth_header, 'Content-Type': 'application/json'},
                            json={'role': data['role']},
                            timeout=5
                        )
                        
                        if not update_response.ok:
                            logger.warning(f"Failed to sync role change with gateway: {update_response.text}",
                                         extra={'correlation_id': getattr(request, 'correlation_id', 'N/A')})
            except Exception as e:
                logger.warning(f"Failed to sync role change with gateway: {str(e)}",
                             extra={'correlation_id': getattr(request, 'correlation_id', 'N/A')})
                # Don't fail the request if gateway sync fails
        
        # Notify admins about the update
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            conn = get_db()
            updated_user = conn.execute("SELECT name, email, role FROM users WHERE id = ?", (user_id,)).fetchone()
            conn.close()
            
            if updated_user:
                change_desc = []
                if 'name' in data:
                    change_desc.append(f"name to '{data['name']}'")
                if 'role' in data:
                    change_desc.append(f"role to '{data['role']}'")
                
                changes = " and ".join(change_desc)
                notify_admins(
                    'user_updated',
                    f"Updated user {updated_user['name']} ({updated_user['email']}): changed {changes}",
                    request.user.get('name', 'Unknown'),
                    request.user['userId'],
                    token
                )
        
        return jsonify({'message': 'User updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    
    # Prevent admin from deleting themselves
    if request.user['userId'] == user_id:
        return jsonify({'error': 'You cannot delete your own account'}), 403
    
    conn = get_db()
    
    # Get user email before deleting
    user = conn.execute("SELECT email FROM users WHERE id = ?", (user_id,)).fetchone()
    
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    user_email = user['email']
    
    # Delete from user-management database
    result = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    # Also delete from gateway authentication database
    try:
        # Call gateway's internal delete endpoint
        # We need to find the user in gateway by email since IDs might differ
        auth_header = request.headers.get('Authorization')
        
        # First, get all users from gateway to find the matching one
        gateway_users_response = requests.get(
            f'{GATEWAY_URL}/users',
            headers={'Authorization': auth_header},
            timeout=5
        )
        
        if gateway_users_response.ok:
            gateway_users = gateway_users_response.json().get('users', [])
            # Find user with matching email
            gateway_user = next((u for u in gateway_users if u['email'] == user_email), None)
            
            if gateway_user:
                # Delete from gateway
                delete_response = requests.delete(
                    f'{GATEWAY_URL}/users/{gateway_user["id"]}',
                    headers={'Authorization': auth_header},
                    timeout=5
                )
                
                if not delete_response.ok:
                    logger.warning(f"Failed to delete user from gateway authentication: {delete_response.text}",
                                 extra={'correlation_id': getattr(request, 'correlation_id', 'N/A')})
    except Exception as e:
        logger.warning(f"Failed to sync user deletion with gateway: {str(e)}",
                     extra={'correlation_id': getattr(request, 'correlation_id', 'N/A')})
        # Don't fail the request if gateway sync fails
    
    # Notify admins about deletion
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(' ')[1]
        notify_admins(
            'user_deleted',
            f"Deleted user: {user_email}",
            request.user.get('name', 'Unknown'),
            request.user['userId'],
            token
        )
    
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
    logger.info("👥 User Management Service starting on port 8002...", extra={'correlation_id': 'startup'})
    logger.info("✅ Default users created (admin, faculty, student)", extra={'correlation_id': 'startup'})
    app.run(host='0.0.0.0', port=8002, debug=True)
