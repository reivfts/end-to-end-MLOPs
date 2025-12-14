"""
Shared Configuration Module for Microservices
Environment-aware configuration for local, Docker, and AWS deployment
"""

import os
from typing import Dict

class Config:
    """Base configuration with environment variable support"""
    
    # Environment
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # JWT Configuration
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '1440'))
    
    # Database Configuration (PostgreSQL for AWS RDS)
    # Falls back to SQLite for local development
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
    
    # PostgreSQL/RDS Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '5432'))
    DB_NAME = os.getenv('DB_NAME', 'campus_services')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # SQLite Configuration (local development)
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', '.')
    
    # Service URLs - Auto-detect environment
    GATEWAY_HOST = os.getenv('GATEWAY_HOST', 'localhost')
    GATEWAY_PORT = int(os.getenv('GATEWAY_PORT', '5001'))
    
    USER_MGMT_HOST = os.getenv('USER_MGMT_HOST', 'localhost')
    USER_MGMT_PORT = int(os.getenv('USER_MGMT_PORT', '8002'))
    
    BOOKING_HOST = os.getenv('BOOKING_HOST', 'localhost')
    BOOKING_PORT = int(os.getenv('BOOKING_PORT', '8001'))
    
    GPA_HOST = os.getenv('GPA_HOST', 'localhost')
    GPA_PORT = int(os.getenv('GPA_PORT', '8003'))
    
    NOTIFICATION_HOST = os.getenv('NOTIFICATION_HOST', 'localhost')
    NOTIFICATION_PORT = int(os.getenv('NOTIFICATION_PORT', '8004'))
    
    MAINTENANCE_HOST = os.getenv('MAINTENANCE_HOST', 'localhost')
    MAINTENANCE_PORT = int(os.getenv('MAINTENANCE_PORT', '8080'))
    
    # HTTP Client Configuration
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))
    REQUEST_RETRY_ATTEMPTS = int(os.getenv('REQUEST_RETRY_ATTEMPTS', '3'))
    REQUEST_RETRY_BACKOFF = float(os.getenv('REQUEST_RETRY_BACKOFF', '1.0'))
    
    @classmethod
    def get_service_url(cls, service: str) -> str:
        """Get service URL based on environment"""
        urls = {
            'gateway': f"http://{cls.GATEWAY_HOST}:{cls.GATEWAY_PORT}",
            'users': f"http://{cls.USER_MGMT_HOST}:{cls.USER_MGMT_PORT}",
            'booking': f"http://{cls.BOOKING_HOST}:{cls.BOOKING_PORT}",
            'gpa': f"http://{cls.GPA_HOST}:{cls.GPA_PORT}",
            'notifications': f"http://{cls.NOTIFICATION_HOST}:{cls.NOTIFICATION_PORT}",
            'maintenance': f"http://{cls.MAINTENANCE_HOST}:{cls.MAINTENANCE_PORT}"
        }
        return urls.get(service, '')
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database connection URL"""
        if cls.DATABASE_TYPE == 'postgresql':
            return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        else:
            return f"sqlite:///{cls.SQLITE_DB_PATH}/app.db"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.ENV == 'production'
    
    @classmethod
    def is_docker(cls) -> bool:
        """Check if running in Docker container"""
        return os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER') == 'true'
    
    @classmethod
    def is_aws(cls) -> bool:
        """Check if running in AWS"""
        return os.getenv('AWS_EXECUTION_ENV') is not None or os.getenv('DEPLOYMENT_ENV') == 'aws'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_TYPE = 'sqlite'


class ProductionConfig(Config):
    """Production configuration for AWS"""
    DEBUG = False
    DATABASE_TYPE = 'postgresql'
    
    # Production should always use environment variables
    @classmethod
    def validate(cls):
        """Validate required production environment variables"""
        required_vars = [
            'JWT_SECRET_KEY',
            'DB_HOST',
            'DB_PASSWORD',
            'DB_USER',
            'DB_NAME'
        ]
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        config = ProductionConfig()
        if config.is_aws():
            config.validate()
        return config
    else:
        return DevelopmentConfig()


# Global config instance
config = get_config()
