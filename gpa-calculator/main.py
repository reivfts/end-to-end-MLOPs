"""
GPA Calculator Service with JWT Auth
Stateless weighted GPA calculation
Port: 8003
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
from functools import wraps
import logging
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(correlation_id)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/gpa.log'),
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

# JWT Configuration
SECRET_KEY = 'your-secret-key-change-in-production'
ALGORITHM = 'HS256'

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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'gpa-calculator',
        'version': '2.0.0'
    }), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'GPA Calculator Service',
        'version': '2.0.0',
        'features': ['JWT Auth', 'Weighted GPA Calculation'],
        'formula': 'Weighted GPA = Σ(gpa × weight) / Σ(weight)'
    }), 200

@app.route('/calculate', methods=['POST'])
@token_required
def calculate_gpa():
    """
    Calculate weighted GPA
    Expected payload:
    {
        "classes": [
            {"gpa": 3.7, "weight": 3},
            {"gpa": 4.0, "weight": 3}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'classes' not in data:
            return jsonify({'error': 'Missing classes array'}), 400
        
        classes = data['classes']
        
        if not classes or len(classes) == 0:
            return jsonify({'error': 'Classes array cannot be empty'}), 400
        
        total_weighted = 0
        total_weight = 0
        
        for i, cls in enumerate(classes):
            if 'gpa' not in cls or 'weight' not in cls:
                return jsonify({'error': 'Each class must have gpa and weight'}), 400
            
            try:
                gpa = float(cls['gpa'])
                weight = float(cls['weight'])
            except (ValueError, TypeError):
                return jsonify({'error': f'Error: Improper format. Class {i+1} has non-numeric values. GPA and weight must be numbers.'}), 400
            
            # Validate GPA range
            if gpa < 0.0 or gpa > 4.0:
                return jsonify({'error': f'GPA must be between 0.0 and 4.0, got {gpa}'}), 400
            
            # Validate weight range
            if weight < 1 or weight > 3:
                return jsonify({'error': f'Weight must be between 1 and 3, got {weight}'}), 400
            
            total_weighted += gpa * weight
            total_weight += weight
        
        if total_weight == 0:
            return jsonify({'error': 'Total weight cannot be zero'}), 400
        
        weighted_gpa = round(total_weighted / total_weight, 2)
        
        return jsonify({
            'gpa': weighted_gpa,
            'total_classes': len(classes),
            'total_weight': total_weight,
            'calculated_by': request.user.get('email', 'unknown')
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Error: Improper format. Please ensure all GPA and weight values are numbers.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("📊 GPA Calculator Service starting on port 8003...")
    print("📐 Formula: Weighted GPA = Σ(gpa × weight) / Σ(weight)")
    print("✅ GPA range: 0.0 - 4.0")
    print("✅ Weight range: 1 - 3")
    app.run(host='0.0.0.0', port=8003, debug=True)
