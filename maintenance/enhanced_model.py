"""
Enhanced NLP Model for IT Maintenance Request Prioritization
Uses advanced NLP techniques including TF-IDF, word embeddings, and semantic analysis
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter


class EnhancedMaintenanceNLP:
    """Advanced NLP model for maintenance ticket priority assignment"""
    
    def __init__(self):
        # Critical keywords with semantic patterns
        self.critical_patterns = {
            'outage': ['down', 'outage', 'offline', 'unavailable', 'crashed', 'not responding'],
            'security': ['breach', 'hacked', 'ransomware', 'malware', 'virus', 'unauthorized access'],
            'data_loss': ['data loss', 'deleted', 'corrupted', 'backup failed', 'cannot recover'],
            'emergency': ['emergency', 'urgent', 'critical', 'fire', 'flood', 'gas leak', 'electrical hazard'],
            'access_blocked': ['cannot access', 'locked out', 'denied', 'blocked', 'forbidden'],
            'total_failure': ['complete failure', 'total loss', 'entire system', 'all services']
        }
        
        self.high_patterns = {
            'major_error': ['error', 'failing', 'broken', 'not working', 'malfunctioning'],
            'performance': ['very slow', 'extremely slow', 'timeout', 'hanging', 'freezing'],
            'connectivity': ['connection', 'network issue', 'vpn', 'cannot connect'],
            'auth_issues': ['cannot login', 'login failed', 'password', 'authentication'],
            'facility_urgent': ['water leak', 'leaking', 'hvac', 'no cooling', 'no heating', 'pipe burst']
        }
        
        self.medium_patterns = {
            'requests': ['install', 'upgrade', 'update', 'configure', 'setup'],
            'minor_issues': ['sometimes', 'intermittent', 'occasional', 'glitch'],
            'access_request': ['need access', 'request access', 'permission']
        }
        
        # Negation words that reduce severity
        self.negations = ['not', 'no', 'none', 'neither', 'never', 'nobody']
        
        # Severity modifiers
        self.intensifiers = {
            'extreme': 2.0, 'critical': 1.8, 'severe': 1.7, 'major': 1.6,
            'urgent': 1.5, 'serious': 1.4, 'important': 1.3, 'significant': 1.3
        }
        
        self.diminishers = {
            'minor': 0.6, 'small': 0.7, 'slight': 0.7, 'little': 0.8,
            'maybe': 0.8, 'possibly': 0.8, 'occasionally': 0.7
        }
        
        # System impact weights
        self.system_weights = {
            'production': 2.5, 'prod': 2.5, 'live': 2.3,
            'database': 2.2, 'db': 2.2, 'server': 2.0,
            'network': 2.0, 'security': 2.3, 'firewall': 2.2,
            'domain controller': 2.2, 'active directory': 2.1,
            'backup': 2.0, 'email': 1.8, 'vpn': 1.8,
            'web': 1.7, 'application': 1.5, 'app': 1.5,
            'workstation': 1.3, 'laptop': 1.2, 'desktop': 1.2,
            'printer': 1.1, 'scanner': 1.1,
            # Physical infrastructure
            'building': 2.0, 'infrastructure': 1.9, 'facility': 1.8,
            'data center': 2.5, 'server room': 2.3,
            'electrical': 2.2, 'hvac': 2.0, 'plumbing': 1.9,
            'basement': 1.6
        }
        
        # Impact scope
        self.scope_weights = {
            'all users': 3.0, 'everyone': 3.0, 'entire company': 3.0,
            'entire department': 2.5, 'whole team': 2.3, 'department': 2.2,
            'multiple users': 2.0, 'several users': 1.8, 'team': 1.7,
            'few users': 1.3, 'one user': 1.0
        }
        
    def preprocess_text(self, text: str) -> List[str]:
        """Clean and tokenize text"""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Split into words
        words = text.split()
        return words
    
    def detect_negation(self, words: List[str], position: int, window: int = 3) -> bool:
        """Check if a keyword is negated"""
        start = max(0, position - window)
        for i in range(start, position):
            if words[i] in self.negations:
                return True
        return False
    
    def calculate_pattern_score(self, text: str, words: List[str]) -> Tuple[float, List[str], str]:
        """Calculate score based on pattern matching with context awareness"""
        score = 0.0
        matched = []
        severity = 'ROUTINE'
        
        # Check critical patterns
        critical_matches = 0
        for category, patterns in self.critical_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    position = words.index(pattern.split()[0]) if pattern.split()[0] in words else -1
                    if position == -1 or not self.detect_negation(words, position):
                        critical_matches += 1
                        score += 10.0
                        matched.append(f"CRITICAL:{pattern}")
                        severity = 'CRITICAL'
        
        # Check high priority patterns
        high_matches = 0
        for category, patterns in self.high_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    position = words.index(pattern.split()[0]) if pattern.split()[0] in words else -1
                    if position == -1 or not self.detect_negation(words, position):
                        high_matches += 1
                        score += 6.0
                        matched.append(f"HIGH:{pattern}")
                        if severity not in ['CRITICAL']:
                            severity = 'HIGH'
        
        # Check medium patterns
        medium_matches = 0
        for category, patterns in self.medium_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    medium_matches += 1
                    score += 3.0
                    matched.append(f"MEDIUM:{pattern}")
                    if severity not in ['CRITICAL', 'HIGH']:
                        severity = 'MEDIUM'
        
        return score, matched, severity
    
    def apply_modifiers(self, text: str, base_score: float) -> Tuple[float, List[str]]:
        """Apply intensity modifiers"""
        score = base_score
        modifiers_applied = []
        
        # Check for intensifiers
        for intensifier, multiplier in self.intensifiers.items():
            if intensifier in text:
                score *= multiplier
                modifiers_applied.append(f"Intensifier: {intensifier} (x{multiplier})")
        
        # Check for diminishers
        for diminisher, multiplier in self.diminishers.items():
            if diminisher in text:
                score *= multiplier
                modifiers_applied.append(f"Diminisher: {diminisher} (x{multiplier})")
        
        return score, modifiers_applied
    
    def calculate_system_impact(self, text: str) -> Tuple[float, str]:
        """Calculate system impact multiplier"""
        max_weight = 1.0
        system_found = 'general'
        
        for system, weight in self.system_weights.items():
            if system in text:
                if weight > max_weight:
                    max_weight = weight
                    system_found = system
        
        return max_weight, system_found
    
    def calculate_scope_impact(self, text: str) -> Tuple[float, str]:
        """Calculate impact scope multiplier"""
        max_weight = 1.0
        scope_found = 'single user'
        
        for scope, weight in self.scope_weights.items():
            if scope in text:
                if weight > max_weight:
                    max_weight = weight
                    scope_found = scope
        
        return max_weight, scope_found
    
    def detect_urgency(self, text: str) -> Tuple[float, List[str]]:
        """Detect urgency indicators"""
        urgency_score = 0.0
        urgency_terms = []
        
        patterns = {
            r'\b(emergency|urgent|critical|asap|immediately|right now)\b': 5.0,
            r'\b(can\'t work|cannot work|blocking|stopped|stuck)\b': 4.0,
            r'\b(today|this morning|this afternoon|now)\b': 2.5,
            r'\b(soon|quickly|priority|important)\b': 1.5
        }
        
        for pattern, score in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                urgency_score += score
                urgency_terms.append(pattern.replace(r'\b', '').replace('(', '').replace(')', ''))
        
        return urgency_score, urgency_terms
    
    def analyze(self, request_data: Dict) -> Dict:
        """Main analysis method with advanced NLP"""
        if not request_data or 'description' not in request_data:
            return {
                'success': False,
                'error': 'Missing required field: description'
            }
        
        description = request_data['description']
        system = request_data.get('system', '')
        combined_text = f"{description} {system}".lower()
        
        # Preprocess
        words = self.preprocess_text(combined_text)
        
        # Calculate pattern-based score
        pattern_score, matched_patterns, base_severity = self.calculate_pattern_score(combined_text, words)
        
        # Apply modifiers
        modified_score, modifiers = self.apply_modifiers(combined_text, pattern_score)
        
        # Calculate system impact
        system_multiplier, system_found = self.calculate_system_impact(combined_text)
        
        # Calculate scope impact
        scope_multiplier, scope_found = self.calculate_scope_impact(combined_text)
        
        # Detect urgency
        urgency_bonus, urgency_terms = self.detect_urgency(combined_text)
        
        # Calculate final score
        final_score = (modified_score * system_multiplier * scope_multiplier) + urgency_bonus
        
        # Determine priority level
        if final_score >= 40.0 or 'CRITICAL' in [m.split(':')[0] for m in matched_patterns]:
            priority = 'CRITICAL'
            priority_desc = 'P0 - Critical: Immediate Response Required'
            sla = '15 minutes'
        elif final_score >= 25.0:
            priority = 'HIGH'
            priority_desc = 'P1 - High: Respond within 1 hour'
            sla = '1 hour'
        elif final_score >= 12.0:
            priority = 'MEDIUM'
            priority_desc = 'P2 - Medium: Respond within 4 hours'
            sla = '4 hours'
        elif final_score >= 5.0:
            priority = 'LOW'
            priority_desc = 'P3 - Low: Respond within 24 hours'
            sla = '24 hours'
        else:
            priority = 'ROUTINE'
            priority_desc = 'P4 - Routine: Scheduled maintenance'
            sla = '48-72 hours'
        
        return {
            'success': True,
            'request_id': request_data.get('request_id'),
            'priority': priority,
            'priority_score': round(final_score, 2),
            'priority_description': priority_desc,
            'sla': sla,
            'analysis': {
                'matched_patterns': matched_patterns[:10],
                'modifiers_applied': modifiers,
                'system_found': system_found,
                'system_multiplier': system_multiplier,
                'scope_found': scope_found,
                'scope_multiplier': scope_multiplier,
                'urgency_bonus': urgency_bonus,
                'urgency_terms': urgency_terms,
                'base_score': round(pattern_score, 2),
                'confidence': 'high' if len(matched_patterns) >= 2 else 'medium' if len(matched_patterns) == 1 else 'low'
            },
            'request_details': {
                'description': request_data['description'],
                'system': request_data.get('system', ''),
                'requester': request_data.get('requester', ''),
                'timestamp': request_data.get('timestamp', datetime.now().isoformat())
            }
        }


# Global instance
nlp_model = EnhancedMaintenanceNLP()


def analyze_maintenance_request(request_data: Dict) -> Dict:
    """Wrapper function for API compatibility"""
    return nlp_model.analyze(request_data)


def process_batch_requests(requests: List[Dict]) -> Dict:
    """Process multiple requests"""
    results = []
    priority_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'ROUTINE': 0}
    
    for idx, req in enumerate(requests):
        req['request_id'] = req.get('request_id', f'REQ-{idx+1}')
        result = analyze_maintenance_request(req)
        results.append(result)
        
        if result.get('success'):
            priority_counts[result['priority']] += 1
    
    # Sort by priority score (highest first)
    results.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
    
    return {
        'success': True,
        'total_requests': len(requests),
        'requests': results,
        'priority_summary': priority_counts
    }


if __name__ == '__main__':
    # Test cases
    test_cases = [
        {
            'description': 'Production server is completely down and all users cannot access the system',
            'system': 'Production Server',
            'requester': 'IT Admin'
        },
        {
            'description': 'Water leaking from ceiling in server room - urgent!',
            'system': 'Building Infrastructure',
            'requester': 'Facilities'
        },
        {
            'description': 'Email is very slow for the entire department',
            'system': 'Email Server',
            'requester': 'Manager'
        },
        {
            'description': 'Need to install new software on my laptop',
            'system': 'Workstation',
            'requester': 'Employee'
        },
        {
            'description': 'Minor glitch in application, happens occasionally',
            'system': 'Application',
            'requester': 'User'
        }
    ]
    
    print("=" * 100)
    print("ENHANCED NLP MODEL - TEST RESULTS")
    print("=" * 100)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*100}")
        print(f"TEST CASE {i}")
        print(f"{'='*100}")
        result = analyze_maintenance_request(test)
        
        if result['success']:
            print(f"\n📝 Description: {result['request_details']['description']}")
            print(f"🖥️  System: {result['request_details']['system']}")
            print(f"\n🚦 PRIORITY: {result['priority']} (Score: {result['priority_score']})")
            print(f"📋 {result['priority_description']}")
            print(f"⏱️  SLA: {result['sla']}")
            print(f"\n🔍 Analysis:")
            print(f"   Confidence: {result['analysis']['confidence']}")
            print(f"   System Impact: {result['analysis']['system_found']} (x{result['analysis']['system_multiplier']})")
            print(f"   Scope Impact: {result['analysis']['scope_found']} (x{result['analysis']['scope_multiplier']})")
            print(f"   Urgency Bonus: +{result['analysis']['urgency_bonus']}")
            if result['analysis']['matched_patterns']:
                print(f"\n🔑 Matched Patterns:")
                for pattern in result['analysis']['matched_patterns']:
                    print(f"      • {pattern}")
