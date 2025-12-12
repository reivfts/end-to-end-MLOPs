"""
Notification Service
Simple event logging and notification history
Port: 8004
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
import sqlite3
from functools import wraps
from datetime import datetime
import uuid
import requests

app = Flask(__name__)
CORS(app)

# JWT Configuration
SECRET_KEY = 'your-secret-key-change-in-production'
ALGORITHM = 'HS256'

# Database setup
def get_db():
    conn = sqlite3.connect('notifications.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            read BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
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

# Endpoints
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'notification', 'version': '2.0.0'}), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'Notification Service',
        'version': '2.0.0',
        'features': ['Event Notifications', 'Notification History']
    }), 200

@app.route('/notifications', methods=['POST'])
@token_required
def create_notification():
    """Create a new notification"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['user_id', 'type', 'message']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db()
        notif_id = str(uuid.uuid4())
        
        conn.execute("""
            INSERT INTO notifications (id, user_id, type, message, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (notif_id, data['user_id'], data['type'], data['message'], datetime.utcnow().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Notification created', 'notificationId': notif_id}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notifications', methods=['GET'])
@token_required
def get_notifications():
    """Get user's notifications"""
    conn = get_db()
    
    # Users see only their own notifications, admin sees all
    if request.user['role'] == 'admin':
        notifications = conn.execute("""
            SELECT * FROM notifications ORDER BY created_at DESC LIMIT 100
        """).fetchall()
    else:
        notifications = conn.execute("""
            SELECT * FROM notifications 
            WHERE user_id = ? 
            ORDER BY created_at DESC LIMIT 50
        """, (request.user['userId'],)).fetchall()
    
    conn.close()
    return jsonify({'notifications': [dict(n) for n in notifications]}), 200

@app.route('/notifications/<notif_id>/read', methods=['PUT'])
@token_required
def mark_as_read(notif_id):
    """Mark notification as read"""
    conn = get_db()
    
    # Check if notification belongs to user
    notif = conn.execute("SELECT * FROM notifications WHERE id = ?", (notif_id,)).fetchone()
    
    if not notif:
        conn.close()
        return jsonify({'error': 'Notification not found'}), 404
    
    if notif['user_id'] != request.user['userId'] and request.user['role'] != 'admin':
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Notification marked as read'}), 200

@app.route('/notifications/unread', methods=['GET'])
@token_required
def get_unread_count():
    """Get count of unread notifications"""
    conn = get_db()
    result = conn.execute("""
        SELECT COUNT(*) as count FROM notifications 
        WHERE user_id = ? AND read = 0
    """, (request.user['userId'],)).fetchone()
    conn.close()
    
    return jsonify({'unreadCount': result['count']}), 200

@app.route('/notifications/admin', methods=['POST'])
@token_required
def notify_admins():
    """Create notifications for all admin users"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['type', 'message', 'actor_name', 'actor_id']):
            return jsonify({'error': 'Missing required fields: type, message, actor_name, actor_id'}), 400
        
        # Get user-management service to fetch admin users
        USER_MGMT_URL = 'http://localhost:8002'
        try:
            # Get all users to filter admins - use short timeout
            auth_header = request.headers.get('Authorization')
            headers = {'Authorization': auth_header} if auth_header else {}
            response = requests.get(f"{USER_MGMT_URL}/users", headers=headers, timeout=1)
            
            if response.status_code == 200:
                users = response.json().get('users', [])
                admin_ids = [user['id'] for user in users if user.get('role') == 'admin']
            else:
                # Fallback to known admin IDs
                admin_ids = ['admin-001']
        except:
            # Fallback to known admin IDs if service is unavailable
            admin_ids = ['admin-001']
        
        conn = get_db()
        timestamp = datetime.utcnow().isoformat()
        notification_ids = []
        
        # Format message with timestamp and actor info
        formatted_message = f"[{timestamp}] {data['actor_name']} (ID: {data['actor_id'][:8]}...): {data['message']}"
        
        # Create notification for each admin
        for admin_id in admin_ids:
            # Don't notify the actor if they're an admin
            if admin_id == data['actor_id']:
                continue
                
            notif_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO notifications (id, user_id, type, message, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (notif_id, admin_id, data['type'], formatted_message, timestamp))
            notification_ids.append(notif_id)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': f'Notified {len(notification_ids)} admin(s)',
            'notificationIds': notification_ids
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🔔 Notification Service starting on port 8004...")
    print("✅ Event logging and notification history")
    app.run(host='0.0.0.0', port=8004, debug=True)
