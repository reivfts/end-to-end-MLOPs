"""
User Management Service
Handles user authentication, registration, and profile management
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Simple in-memory user storage (use database in production)
users = {}

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

@app.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({"detail": "Missing required fields: username, email, password"}), 400
        
        username = data['username']
        email = data['email']
        password = data['password']
        
        # Check if user already exists
        if username in users:
            return jsonify({"detail": "Username already exists"}), 409
        
        # Check if email already exists
        for user_data in users.values():
            if user_data['email'] == email:
                return jsonify({"detail": "Email already registered"}), 409
        
        # Create user
        user_id = str(uuid.uuid4())
        
        users[username] = {
            'id': user_id,
            'username': username,
            'email': email,
            'password': password,  # Store password as plain text for simplicity
            'role': data.get('role', 'user'),
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', '')
        }
        
        return jsonify({
            "message": "User registered successfully",
            "id": user_id,
            "username": username,
            "email": email
        }), 201
        
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """Authenticate user login"""
    try:
        data = request.get_json()
        
        # Validate required fields - accept both email and username
        if not data:
            return jsonify({"detail": "Missing request body"}), 400
        
        # Support login by email or username
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        
        if not password:
            return jsonify({"detail": "Missing password"}), 400
        
        user = None
        
        # Try to find user by email
        if email:
            for u in users.values():
                if u['email'] == email:
                    user = u
                    break
        
        # Try to find user by username
        if not user and username:
            if username in users:
                user = users[username]
        
        if not user:
            return jsonify({"detail": "Invalid email/username or password"}), 401
        
        # Verify password
        if user['password'] != password:
            return jsonify({"detail": "Invalid email/username or password"}), 401
        
        # Return user info (without password)
        return jsonify({
            "message": "Login successful",
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "role": user['role']
        }), 200
        
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

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