from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# Data storage file
DATA_FILE = 'maintenance_data.json'

# Load existing data or create new
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'tickets': []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Initialize data
data = load_data()

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Maintenance Service',
        'port': 8001,
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================================================
# TICKET ENDPOINTS
# ============================================================================

@app.route('/tickets', methods=['GET'])
def get_tickets():
    """Get all maintenance tickets"""
    return jsonify({
        'tickets': data['tickets'],
        'count': len(data['tickets'])
    }), 200

@app.route('/tickets', methods=['POST'])
def create_ticket():
    """Create a new maintenance ticket"""
    try:
        payload = request.get_json()
        
        # Validate required fields
        if not payload or 'description' not in payload:
            return jsonify({'error': 'Description is required'}), 400
        
        # Create new ticket
        ticket_id = len(data['tickets']) + 1
        new_ticket = {
            'id': ticket_id,
            'description': payload.get('description'),
            'system': payload.get('system', 'General'),
            'requester': payload.get('requester', 'Anonymous'),
            'priority': payload.get('priority', 'medium'),
            'status': payload.get('status', 'open'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        data['tickets'].append(new_ticket)
        save_data(data)
        
        return jsonify({
            'message': 'Ticket created successfully',
            'ticket': new_ticket
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get specific ticket by ID"""
    for ticket in data['tickets']:
        if ticket['id'] == ticket_id:
            return jsonify(ticket), 200
    
    return jsonify({'error': 'Ticket not found'}), 404

@app.route('/tickets/<int:ticket_id>', methods=['PATCH'])
def update_ticket(ticket_id):
    """Update specific ticket"""
    try:
        payload = request.get_json()
        
        for ticket in data['tickets']:
            if ticket['id'] == ticket_id:
                # Update fields
                if 'description' in payload:
                    ticket['description'] = payload['description']
                if 'status' in payload:
                    ticket['status'] = payload['status']
                if 'priority' in payload:
                    ticket['priority'] = payload['priority']
                if 'system' in payload:
                    ticket['system'] = payload['system']
                
                ticket['updated_at'] = datetime.now().isoformat()
                save_data(data)
                
                return jsonify({
                    'message': 'Ticket updated successfully',
                    'ticket': ticket
                }), 200
        
        return jsonify({'error': 'Ticket not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    """Delete specific ticket"""
    global data
    
    for i, ticket in enumerate(data['tickets']):
        if ticket['id'] == ticket_id:
            deleted_ticket = data['tickets'].pop(i)
            save_data(data)
            
            return jsonify({
                'message': 'Ticket deleted successfully',
                'ticket': deleted_ticket
            }), 200
    
    return jsonify({'error': 'Ticket not found'}), 404

# ============================================================================
# STATISTICS
# ============================================================================

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get ticket statistics"""
    stats = {
        'total': len(data['tickets']),
        'by_status': {},
        'by_priority': {}
    }
    
    # Count by status
    for ticket in data['tickets']:
        status = ticket.get('status', 'open')
        priority = ticket.get('priority', 'medium')
        
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
    
    return jsonify(stats), 200

# ============================================================================
# CLEAR ALL DATA (for testing)
# ============================================================================

@app.route('/clear', methods=['POST'])
def clear_data():
    """Clear all tickets (for testing only)"""
    global data
    data = {'tickets': []}
    save_data(data)
    
    return jsonify({'message': 'All tickets cleared'}), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("🔧 Maintenance Service starting on http://localhost:8001")
    print("\n📚 Available endpoints:")
    print("  - GET    /health              (Health check)")
    print("  - GET    /tickets             (Get all tickets)")
    print("  - POST   /tickets             (Create new ticket)")
    print("  - GET    /tickets/<id>        (Get specific ticket)")
    print("  - PATCH  /tickets/<id>        (Update ticket)")
    print("  - DELETE /tickets/<id>        (Delete ticket)")
    print("  - GET    /stats               (Get statistics)")
    print("  - POST   /clear               (Clear all tickets)")
    print("\n" + "="*60)
    
    app.run(debug=True, host='localhost', port=8001)
