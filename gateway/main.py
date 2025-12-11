from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
SERVICES = {
    'booking': 'http://localhost:8000',
    'maintenance': 'http://localhost:8001',
    'user': 'http://localhost:8002',
    'notification': 'http://localhost:8003'
}

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def gateway_health():
    """Gateway health endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'API Gateway',
        'port': 8080,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/services/health', methods=['GET'])
def services_health():
    """Check health of all connected services"""
    health_status = {
        'gateway': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {}
    }
    
    for service_name, service_url in SERVICES.items():
        try:
            response = requests.get(f'{service_url}/health', timeout=2)
            health_status['services'][service_name] = {
                'status': 'online' if response.status_code == 200 else 'error',
                'port': SERVICES[service_name].split(':')[-1]
            }
        except:
            health_status['services'][service_name] = {
                'status': 'offline',
                'port': SERVICES[service_name].split(':')[-1]
            }
    
    return jsonify(health_status), 200

# ============================================================================
# BOOKING SERVICE ROUTES (Port 8000)
# ============================================================================

@app.route('/api/booking/rooms', methods=['GET'])
def get_rooms():
    """Get all rooms from booking service"""
    try:
        response = requests.get(f"{SERVICES['booking']}/rooms")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error getting rooms: {e}")
        return jsonify({'error': 'Booking service unavailable'}), 503

@app.route('/api/booking/bookings', methods=['GET', 'POST'])
def manage_bookings():
    """Get or create bookings"""
    try:
        if request.method == 'GET':
            response = requests.get(f"{SERVICES['booking']}/bookings")
        else:
            response = requests.post(
                f"{SERVICES['booking']}/bookings",
                json=request.get_json(),
                headers={'Content-Type': 'application/json'}
            )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error managing bookings: {e}")
        return jsonify({'error': 'Booking service unavailable'}), 503

@app.route('/api/booking/bookings/<int:booking_id>', methods=['GET', 'DELETE'])
def manage_booking(booking_id):
    """Get or delete specific booking"""
    try:
        if request.method == 'GET':
            response = requests.get(f"{SERVICES['booking']}/bookings/{booking_id}")
        else:
            response = requests.delete(
                f"{SERVICES['booking']}/bookings/{booking_id}",
                json=request.get_json(),
                headers={'Content-Type': 'application/json'}
            )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error managing booking {booking_id}: {e}")
        return jsonify({'error': 'Booking service unavailable'}), 503

@app.route('/api/booking/bookings/user/<int:user_id>', methods=['GET'])
def get_user_bookings(user_id):
    """Get bookings for specific user"""
    try:
        response = requests.get(f"{SERVICES['booking']}/bookings/user/{user_id}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error getting user bookings: {e}")
        return jsonify({'error': 'Booking service unavailable'}), 503

# ============================================================================
# MAINTENANCE SERVICE ROUTES (Port 8001)
# ============================================================================

@app.route('/api/maintenance/tickets', methods=['GET', 'POST'])
def manage_tickets():
    """Get or create maintenance tickets"""
    try:
        if request.method == 'GET':
            response = requests.get(f"{SERVICES['maintenance']}/tickets")
        else:
            response = requests.post(
                f"{SERVICES['maintenance']}/tickets",
                json=request.get_json(),
                headers={'Content-Type': 'application/json'}
            )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error managing tickets: {e}")
        return jsonify({'error': 'Maintenance service unavailable'}), 503

@app.route('/api/maintenance/tickets/<int:ticket_id>', methods=['GET', 'PATCH', 'DELETE'])
def manage_ticket(ticket_id):
    """Get, update, or delete specific ticket"""
    try:
        if request.method == 'GET':
            response = requests.get(f"{SERVICES['maintenance']}/tickets/{ticket_id}")
        elif request.method == 'PATCH':
            response = requests.patch(
                f"{SERVICES['maintenance']}/tickets/{ticket_id}",
                json=request.get_json(),
                headers={'Content-Type': 'application/json'}
            )
        else:  # DELETE
            response = requests.delete(f"{SERVICES['maintenance']}/tickets/{ticket_id}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error managing ticket {ticket_id}: {e}")
        return jsonify({'error': 'Maintenance service unavailable'}), 503

# ============================================================================
# USER SERVICE ROUTES (Port 8002)
# ============================================================================

@app.route('/api/user/login', methods=['POST'])
@app.route('/api/user/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        response = requests.post(
            f"{SERVICES['user']}/login",
            json=request.get_json(),
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({'detail': 'User service unavailable'}), 503

@app.route('/api/user/register', methods=['POST'])
@app.route('/api/user/auth/register', methods=['POST'])
def register():
    """User registration"""
    try:
        response = requests.post(
            f"{SERVICES['user']}/register",
            json=request.get_json(),
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return jsonify({'detail': 'User service unavailable'}), 503

@app.route('/api/user/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        response = requests.get(f"{SERVICES['user']}/users")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return jsonify({'error': 'User service unavailable'}), 503

@app.route('/api/user/users/<username>', methods=['GET'])
def get_user(username):
    """Get specific user by username"""
    try:
        response = requests.get(f"{SERVICES['user']}/users/{username}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error getting user {username}: {e}")
        return jsonify({'error': 'User service unavailable'}), 503

@app.route('/api/user/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_user(user_id):
    """Get, update, or delete specific user by ID"""
    try:
        if request.method == 'GET':
            response = requests.get(f"{SERVICES['user']}/users/{user_id}")
        elif request.method == 'PUT':
            response = requests.put(
                f"{SERVICES['user']}/users/{user_id}",
                json=request.get_json(),
                headers={'Content-Type': 'application/json'}
            )
        else:  # DELETE
            response = requests.delete(f"{SERVICES['user']}/users/{user_id}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error managing user {user_id}: {e}")
        return jsonify({'error': 'User service unavailable'}), 503

# ============================================================================
# NOTIFICATION SERVICE ROUTES (Port 8003)
# ============================================================================

@app.route('/api/notification/send', methods=['POST'])
def send_notification():
    """Send a notification"""
    try:
        response = requests.post(
            f"{SERVICES['notification']}/notify",
            json=request.get_json(),
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return jsonify({'error': 'Notification service unavailable'}), 503

@app.route('/api/notification/notifications', methods=['GET'])
def get_notifications():
    """Get all notifications"""
    try:
        response = requests.get(f"{SERVICES['notification']}/notifications")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return jsonify({'error': 'Notification service unavailable'}), 503

# ============================================================================
# GATEWAY INFO ENDPOINT
# ============================================================================

@app.route('/api/gateway/info', methods=['GET'])
def gateway_info():
    """Get gateway information and available endpoints"""
    return jsonify({
        'name': 'API Gateway',
        'port': 8080,
        'version': '1.0',
        'services': {
            'booking': {
                'url': SERVICES['booking'],
                'port': 8000,
                'endpoints': [
                    'GET /api/booking/rooms',
                    'GET /api/booking/bookings',
                    'POST /api/booking/bookings',
                    'GET /api/booking/bookings/<id>',
                    'DELETE /api/booking/bookings/<id>',
                    'GET /api/booking/bookings/user/<user_id>'
                ]
            },
            'maintenance': {
                'url': SERVICES['maintenance'],
                'port': 8001,
                'endpoints': [
                    'GET /api/maintenance/tickets',
                    'POST /api/maintenance/tickets',
                    'GET /api/maintenance/tickets/<id>',
                    'PATCH /api/maintenance/tickets/<id>',
                    'DELETE /api/maintenance/tickets/<id>'
                ]
            },
            'user': {
                'url': SERVICES['user'],
                'port': 8002,
                'endpoints': [
                    'POST /api/user/auth/login',
                    'POST /api/user/auth/register',
                    'GET /api/user/users',
                    'GET /api/user/users/<username>',
                    'GET /api/user/users/<id>',
                    'PUT /api/user/users/<id>',
                    'DELETE /api/user/users/<id>'
                ]
            },
            'notification': {
                'url': SERVICES['notification'],
                'port': 8003,
                'endpoints': [
                    'POST /api/notification/send',
                    'GET /api/notification/notifications'
                ]
            }
        },
        'health_check': '/health',
        'services_health': '/services/health'
    }), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': f'The requested path does not exist',
        'available_endpoints': '/api/gateway/info'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("🚀 API Gateway starting on http://localhost:8080")
    print("\n📚 Available endpoints:")
    print("  - GET  /health              (Gateway health)")
    print("  - GET  /services/health     (All services health)")
    print("  - GET  /api/gateway/info    (Gateway info & endpoints)")
    print("\n🔗 Service Routes:")
    print("  - /api/booking/*            (Booking Service - Port 8000)")
    print("  - /api/maintenance/*        (Maintenance Service - Port 8001)")
    print("  - /api/user/*               (User Service - Port 8002)")
    print("  - /api/notification/*       (Notification Service - Port 8003)")
    print("\n" + "="*60)
    
    app.run(debug=True, host='localhost', port=8080)
