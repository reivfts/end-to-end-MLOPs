"""
HTTP Client with Retry Logic and Circuit Breaker
Resilient inter-service communication
"""

import requests
from typing import Optional, Dict, Any
import time
from functools import wraps
from shared.config import config


class CircuitBreaker:
    """Simple circuit breaker implementation"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half_open'
            else:
                raise Exception(f"Circuit breaker is OPEN. Service unavailable.")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        """Reset circuit breaker on successful call"""
        self.failure_count = 0
        self.state = 'closed'
    
    def on_failure(self):
        """Increment failure count and open circuit if threshold reached"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
            print(f"⚠️  Circuit breaker OPENED after {self.failure_count} failures")


class HTTPClient:
    """HTTP client with retry logic and circuit breaker"""
    
    def __init__(self, 
                 max_retries: int = None,
                 timeout: int = None,
                 backoff_factor: float = None):
        self.max_retries = max_retries or config.REQUEST_RETRY_ATTEMPTS
        self.timeout = timeout or config.REQUEST_TIMEOUT
        self.backoff_factor = backoff_factor or config.REQUEST_RETRY_BACKOFF
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def _get_circuit_breaker(self, url: str) -> CircuitBreaker:
        """Get or create circuit breaker for URL"""
        # Extract host from URL for circuit breaker key
        host = url.split('//')[1].split('/')[0] if '//' in url else url.split('/')[0]
        
        if host not in self.circuit_breakers:
            self.circuit_breakers[host] = CircuitBreaker()
        
        return self.circuit_breakers[host]
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with retries"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Set timeout if not provided
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = self.timeout
                
                response = requests.request(method, url, **kwargs)
                
                # Raise exception for 4xx/5xx status codes
                if response.status_code >= 500:
                    response.raise_for_status()
                
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                
                # Don't retry on 4xx client errors
                if hasattr(e, 'response') and e.response is not None:
                    if 400 <= e.response.status_code < 500:
                        raise e
                
                # Wait before retry with exponential backoff
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor * (2 ** attempt)
                    print(f"⚠️  Request failed (attempt {attempt + 1}/{self.max_retries}). "
                          f"Retrying in {wait_time:.1f}s... Error: {str(e)}")
                    time.sleep(wait_time)
        
        # All retries failed
        raise last_exception
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """POST request with retry and circuit breaker"""
        circuit_breaker = self._get_circuit_breaker(url)
        return circuit_breaker.call(self._make_request, 'POST', url, **kwargs)
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """GET request with retry and circuit breaker"""
        circuit_breaker = self._get_circuit_breaker(url)
        return circuit_breaker.call(self._make_request, 'GET', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """PUT request with retry and circuit breaker"""
        circuit_breaker = self._get_circuit_breaker(url)
        return circuit_breaker.call(self._make_request, 'PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """DELETE request with retry and circuit breaker"""
        circuit_breaker = self._get_circuit_breaker(url)
        return circuit_breaker.call(self._make_request, 'DELETE', url, **kwargs)


# Global HTTP client instance
http_client = HTTPClient()


# Convenience functions
def send_notification(user_id: str, notification_type: str, message: str, token: str) -> bool:
    """Send notification with retry logic"""
    try:
        url = f"{config.get_service_url('notifications')}/notifications"
        response = http_client.post(
            url,
            headers={'Authorization': f'Bearer {token}'},
            json={
                'user_id': user_id,
                'type': notification_type,
                'message': message
            }
        )
        return response.status_code == 201
    except Exception as e:
        print(f"ERROR: Failed to send notification after retries: {e}")
        return False


def notify_admins(action_type: str, message: str, actor_name: str, actor_id: str, token: str) -> bool:
    """Send admin notification with retry logic"""
    try:
        url = f"{config.get_service_url('notifications')}/notifications/admin"
        response = http_client.post(
            url,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={
                'type': action_type,
                'message': message,
                'actor_name': actor_name,
                'actor_id': actor_id
            }
        )
        return response.status_code == 201
    except Exception as e:
        print(f"ERROR: Failed to send admin notification after retries: {e}")
        return False
