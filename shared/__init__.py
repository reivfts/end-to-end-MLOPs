"""
Shared utilities and configuration for microservices
"""

from shared.config import config, get_config
from shared.database import db_pool, get_db_connection, query, execute, execute_many
from shared.http_client import http_client, send_notification, notify_admins

__all__ = [
    'config',
    'get_config',
    'db_pool',
    'get_db_connection',
    'query',
    'execute',
    'execute_many',
    'http_client',
    'send_notification',
    'notify_admins'
]
