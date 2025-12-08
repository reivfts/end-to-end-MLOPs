"""
IT Maintenance Request API
Users send maintenance requests through this API
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from enhanced_model import analyze_maintenance_request, process_batch_requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connection


@app.route('/', methods=['GET'])
def home():
    """Serve the frontend dashboard"""
    return send_file('frontend.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy'})


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze a single maintenance request
    
    POST /analyze
    Body: {
        "description": "Server is down",
        "system": "Production Server",
        "requester": "John Doe"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: description'
            }), 400
        
        # Use model.py to analyze the request
        result = analyze_maintenance_request(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/analyze-batch', methods=['POST'])
def analyze_batch():
    """
    Analyze multiple maintenance requests at once
    
    POST /analyze-batch
    Body: {
        "requests": [
            {"description": "Server down", "system": "Production"},
            {"description": "Password reset", "system": "Active Directory"}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'requests' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: requests (array)'
            }), 400
        
        # Use model.py to analyze batch
        result = process_batch_requests(data['requests'])
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/priority-levels', methods=['GET'])
def priority_levels():
    """
    Get information about priority levels
    
    GET /priority-levels
    """
    levels = {
        'CRITICAL': {
            'code': 'P0',
            'sla': '15 minutes',
            'score_range': '20+',
            'description': 'Immediate response required'
        },
        'HIGH': {
            'code': 'P1',
            'sla': '1 hour',
            'score_range': '12-19.99',
            'description': 'Respond within 1 hour'
        },
        'MEDIUM': {
            'code': 'P2',
            'sla': '4 hours',
            'score_range': '6-11.99',
            'description': 'Respond within 4 hours'
        },
        'LOW': {
            'code': 'P3',
            'sla': '24 hours',
            'score_range': '3-5.99',
            'description': 'Respond within 24 hours'
        },
        'ROUTINE': {
            'code': 'P4',
            'sla': '48-72 hours',
            'score_range': '0-2.99',
            'description': 'Scheduled maintenance'
        }
    }
    
    return jsonify({
        'success': True,
        'priority_levels': levels
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
