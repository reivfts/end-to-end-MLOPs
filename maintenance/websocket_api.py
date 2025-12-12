"""
WebSocket-enabled IT Maintenance Request API
Real-time ticket updates with admin controls
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send, rooms
from enhanced_model import analyze_maintenance_request, process_batch_requests
import json
import os
from datetime import datetime
import uuid
import jwt
from functools import wraps
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# JWT Configuration (must match gateway)
SECRET_KEY = 'your-secret-key-change-in-production'
ALGORITHM = 'HS256'

# Service URLs
NOTIFICATION_SERVICE = 'http://localhost:8004'

# Helper function to verify JWT token
def verify_token():
    """Verify JWT token and return user info"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None

# Helper function to send notifications
def send_notification(user_id: str, notification_type: str, message: str, token: str):
    """Send notification to the notification service"""
    try:
        requests.post(
            f'{NOTIFICATION_SERVICE}/notifications',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'user_id': user_id,
                'type': notification_type,
                'message': message
            },
            timeout=2
        )
    except Exception as e:
        # Don't fail the main operation if notification fails
        print(f"Failed to send notification: {e}")

def notify_admins(action_type: str, message: str, actor_name: str, actor_id: str, token: str):
    """Send notification to all admin users - non-blocking"""
    try:
        # Use very short timeout and don't wait for response
        requests.post(
            f'{NOTIFICATION_SERVICE}/notifications/admin',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json={
                'type': action_type,
                'message': message,
                'actor_name': actor_name,
                'actor_id': actor_id
            },
            timeout=0.5
        )
    except Exception:
        # Silently fail - notifications are not critical
        pass

# Helper function to broadcast to all connected clients
def broadcast_event(event, data):
    """Broadcast an event to all connected clients"""
    socketio.emit(event, data, namespace='/')


# In-memory storage (can be replaced with database)
tickets = {}
TICKETS_FILE = 'tickets_storage.json'

# Admin password (change this in production!)
ADMIN_PASSWORD = "admin123"


def load_tickets():
    """Load tickets from persistent storage"""
    global tickets
    if os.path.exists(TICKETS_FILE):
        try:
            with open(TICKETS_FILE, 'r') as f:
                tickets = json.load(f)
            print(f"Loaded {len(tickets)} tickets from storage")
        except Exception as e:
            print(f"Error loading tickets: {e}")
            tickets = {}
    else:
        tickets = {}


def save_tickets():
    """Save tickets to persistent storage"""
    try:
        with open(TICKETS_FILE, 'w') as f:
            json.dump(tickets, f, indent=2)
    except Exception as e:
        print(f"Error saving tickets: {e}")


@app.route('/', methods=['GET'])
def home():
    """Serve the frontend dashboard"""
    return send_file('websocket_frontend.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'tickets_count': len(tickets),
        'websocket_enabled': True
    })


@app.route('/tickets', methods=['GET'])
def get_all_tickets():
    """Get all tickets - students see only their own, faculty see all"""
    user = verify_token()
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Filter tickets based on role
    if user['role'] in ['faculty', 'admin']:
        # Faculty and admin see all tickets
        ticket_list = sorted(
            tickets.values(),
            key=lambda x: x.get('priority_score', 0),
            reverse=True
        )
    else:
        # Students see only their own tickets
        user_email = user.get('email', '')
        ticket_list = [
            ticket for ticket in tickets.values()
            if ticket.get('request_details', {}).get('requester', '') == user_email
        ]
        ticket_list = sorted(
            ticket_list,
            key=lambda x: x.get('priority_score', 0),
            reverse=True
        )
    
    return jsonify({
        'success': True,
        'count': len(ticket_list),
        'tickets': ticket_list
    })


@app.route('/tickets/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get a specific ticket"""
    if ticket_id in tickets:
        return jsonify({
            'success': True,
            'ticket': tickets[ticket_id]
        })
    return jsonify({
        'success': False,
        'error': 'Ticket not found'
    }), 404


@app.route('/tickets/<ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    """Update a ticket's status - faculty can update any, students only their own"""
    user = verify_token()
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if ticket_id not in tickets:
        return jsonify({
            'success': False,
            'error': 'Ticket not found'
        }), 404
    
    # Check permissions
    ticket = tickets[ticket_id]
    if user['role'] == 'student':
        # Students can only update their own tickets
        if ticket.get('request_details', {}).get('requester', '') != user.get('email', ''):
            return jsonify({
                'success': False,
                'error': 'You can only update your own tickets'
            }), 403
    
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing status field'
            }), 400
        
        # Update the ticket status
        old_status = tickets[ticket_id]['status']
        tickets[ticket_id]['status'] = data['status']
        tickets[ticket_id]['updated_at'] = datetime.utcnow().isoformat()
        save_tickets()
        
        # Broadcast update to all connected clients
        broadcast_event('ticket_updated', tickets[ticket_id])
        
        # Notify admins about the update
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            ticket_desc = ticket.get('request_details', {}).get('description', 'maintenance ticket')
            short_desc = ticket_desc[:30] + '...' if len(ticket_desc) > 30 else ticket_desc
            
            notify_admins(
                'maintenance_updated',
                f"{user.get('name', 'User')} updated ticket status from '{old_status}' to '{data['status']}' for: {short_desc}",
                user.get('name', 'Unknown'),
                user['userId'],
                token
            )
        
        return jsonify({
            'success': True,
            'message': 'Ticket updated successfully',
            'ticket': tickets[ticket_id]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/tickets/<ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    """Delete a ticket - faculty can delete any, students only their own"""
    user = verify_token()
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if ticket_id not in tickets:
        return jsonify({
            'success': False,
            'error': 'Ticket not found'
        }), 404
    
    # Check permissions
    ticket = tickets[ticket_id]
    if user['role'] == 'student':
        # Students can only delete their own tickets
        if ticket.get('request_details', {}).get('requester', '') != user.get('email', ''):
            return jsonify({
                'success': False,
                'error': 'You can only delete your own tickets'
            }), 403
    
    try:
        deleted_ticket = tickets.pop(ticket_id)
        save_tickets()
        
        # Broadcast deletion to all connected clients
        broadcast_event('ticket_deleted', {'ticket_id': ticket_id})
        
        # Send notification to the ticket owner
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            ticket_description = deleted_ticket.get('request_details', {}).get('description', 'maintenance request')
            # Extract first 50 chars of description for notification
            short_desc = ticket_description[:50] + '...' if len(ticket_description) > 50 else ticket_description
            
            send_notification(
                user['userId'],
                'maintenance_deleted',
                f"Your maintenance ticket was deleted: {short_desc}",
                token
            )
            
            # Notify admins about the deletion
            requester = deleted_ticket.get('request_details', {}).get('requester', 'Unknown')
            if user['userId'] == deleted_ticket.get('user_id', ''):
                notify_admins(
                    'maintenance_deleted',
                    f"{user.get('name', 'User')} deleted their own maintenance ticket: {short_desc}",
                    user.get('name', 'Unknown'),
                    user['userId'],
                    token
                )
            else:
                notify_admins(
                    'maintenance_deleted',
                    f"{user.get('name', 'User')} deleted {requester}'s maintenance ticket: {short_desc}",
                    user.get('name', 'Unknown'),
                    user['userId'],
                    token
                )
        
        return jsonify({
            'success': True,
            'message': 'Ticket deleted successfully',
            'ticket': deleted_ticket
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a single maintenance request"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: description'
            }), 400
        
        # Generate unique ticket ID
        ticket_id = str(uuid.uuid4())
        data['request_id'] = ticket_id
        
        # Analyze with NLP model
        result = analyze_maintenance_request(data)
        
        if result.get('success'):
            # Add default status and timestamps
            result['status'] = 'open'
            result['created_at'] = datetime.utcnow().isoformat()
            result['updated_at'] = datetime.utcnow().isoformat()
            
            # Store ticket
            tickets[ticket_id] = result
            save_tickets()
            
            # Broadcast to all connected clients
            broadcast_event('new_ticket', result)
            
            # Notify admins about new ticket
            user = verify_token()
            if user:
                auth_header = request.headers.get('Authorization')
                if auth_header:
                    token = auth_header.split(' ')[1]
                    ticket_desc = data.get('description', 'maintenance request')
                    short_desc = ticket_desc[:30] + '...' if len(ticket_desc) > 30 else ticket_desc
                    priority = result.get('priority_score', 0)
                    
                    notify_admins(
                        'maintenance_created',
                        f"{user.get('name', 'User')} created a new maintenance ticket (Priority: {priority:.1f}): {short_desc}",
                        user.get('name', 'Unknown'),
                        user['userId'],
                        token
                    )
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connection"""
    print(f'Client connected: {request.sid}')
    # Send current tickets to newly connected client
    emit('initial_tickets', {
        'tickets': list(tickets.values()),
        'count': len(tickets)
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f'Client disconnected: {request.sid}')


@socketio.on('submit_ticket')
def handle_submit_ticket(data):
    """Handle ticket submission via WebSocket"""
    try:
        if not data or 'description' not in data:
            emit('error', {'message': 'Missing required field: description'})
            return
        
        # Generate unique ticket ID
        ticket_id = str(uuid.uuid4())
        data['request_id'] = ticket_id
        
        # Analyze with NLP model
        result = analyze_maintenance_request(data)
        
        if result.get('success'):
            # Store ticket
            tickets[ticket_id] = result
            save_tickets()
            
            # Broadcast to all clients
            broadcast_event('new_ticket', result)
            
            # Notify admins about new ticket (WebSocket submission)
            # Note: WebSocket connections don't have auth headers easily accessible
            # So we'll include basic info from the data
            requester = data.get('requester', 'Unknown')
            ticket_desc = data.get('description', 'maintenance request')
            short_desc = ticket_desc[:30] + '...' if len(ticket_desc) > 30 else ticket_desc
            priority = result.get('priority_score', 0)
            
            # We can't easily get token from WebSocket, so log for now
            print(f"New ticket created via WebSocket by {requester}: {short_desc} (Priority: {priority:.1f})")
            
            # Confirm to sender
            emit('ticket_submitted', result)
        else:
            emit('error', {'message': result.get('error', 'Analysis failed')})
            
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('admin_command')
def handle_admin_command(data):
    """Handle admin commands: delete, update_status"""
    try:
        password = data.get('password')
        command = data.get('command')
        
        # Verify admin password
        if password != ADMIN_PASSWORD:
            emit('error', {'message': 'Invalid admin password'})
            return
        
        if command == 'delete':
            ticket_id = data.get('ticket_id')
            if ticket_id in tickets:
                deleted_ticket = tickets.pop(ticket_id)
                save_tickets()
                
                # Broadcast deletion to all clients
                broadcast_event('ticket_deleted', {
                    'ticket_id': ticket_id,
                    'deleted_ticket': deleted_ticket
                })
                
                emit('admin_success', {
                    'message': f'Ticket {ticket_id} deleted',
                    'action': 'delete'
                })
            else:
                emit('error', {'message': 'Ticket not found'})
        
        elif command == 'update_status':
            ticket_id = data.get('ticket_id')
            new_status = data.get('status')
            
            # Validate status
            valid_statuses = ['open', 'viewed', 'in-progress', 'completed']
            if new_status not in valid_statuses:
                emit('error', {'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'})
                return
            
            if ticket_id in tickets:
                old_status = tickets[ticket_id].get('status', 'open')
                tickets[ticket_id]['status'] = new_status
                tickets[ticket_id]['admin_modified'] = True
                tickets[ticket_id]['modified_at'] = datetime.now().isoformat()
                
                # Track status change timestamp
                if new_status == 'viewed':
                    tickets[ticket_id]['viewed_at'] = datetime.now().isoformat()
                elif new_status == 'in-progress':
                    tickets[ticket_id]['in_progress_at'] = datetime.now().isoformat()
                elif new_status == 'completed':
                    tickets[ticket_id]['completed_at'] = datetime.now().isoformat()
                
                save_tickets()
                
                # Broadcast update to all clients
                broadcast_event('ticket_updated', tickets[ticket_id])
                
                emit('admin_success', {
                    'message': f'Ticket status updated from "{old_status}" to "{new_status}"',
                    'action': 'update_status'
                })
            else:
                emit('error', {'message': 'Ticket not found'})
        
        elif command == 'update_priority':
            ticket_id = data.get('ticket_id')
            new_priority = data.get('priority')
            
            if ticket_id in tickets:
                tickets[ticket_id]['priority'] = new_priority
                tickets[ticket_id]['admin_modified'] = True
                tickets[ticket_id]['modified_at'] = datetime.now().isoformat()
                save_tickets()
                
                # Broadcast update to all clients
                broadcast_event('ticket_updated', tickets[ticket_id])
                
                emit('admin_success', {
                    'message': f'Ticket {ticket_id} priority updated to {new_priority}',
                    'action': 'update'
                })
            else:
                emit('error', {'message': 'Ticket not found'})
        
        else:
            emit('error', {'message': f'Unknown command: {command}'})
            
    except Exception as e:
        emit('error', {'message': f'Admin command error: {str(e)}'})


@socketio.on('get_stats')
def handle_get_stats():
    """Get real-time statistics"""
    stats = {
        'total': len(tickets),
        'CRITICAL': 0,
        'HIGH': 0,
        'MEDIUM': 0,
        'LOW': 0,
        'ROUTINE': 0,
        'resolved': 0
    }
    
    for ticket in tickets.values():
        priority = ticket.get('priority', 'ROUTINE')
        stats[priority] = stats.get(priority, 0) + 1
        if ticket.get('status') == 'resolved':
            stats['resolved'] += 1
    
    emit('stats_update', stats)


if __name__ == '__main__':
    # Load existing tickets on startup
    load_tickets()
    
    print(f"Starting WebSocket-enabled Maintenance Ticketing System")
    print(f"Loaded {len(tickets)} existing tickets")
    print(f"Admin password: {ADMIN_PASSWORD}")
    print(f"Running on http://127.0.0.1:8080")
    
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
