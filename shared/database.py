"""
Database Abstraction Layer
Supports both PostgreSQL (AWS RDS) and SQLite (local dev) with connection pooling
"""

import sqlite3
from typing import Optional, Any, List, Dict
from contextlib import contextmanager
import os
import threading

try:
    import psycopg2
    from psycopg2 import pool
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

from shared.config import config


class DatabasePool:
    """Thread-safe database connection pool"""
    
    def __init__(self):
        self.db_type = config.DATABASE_TYPE
        self._local = threading.local()
        self._pool = None
        
        if self.db_type == 'postgresql' and POSTGRESQL_AVAILABLE:
            self._init_postgresql_pool()
        else:
            self._init_sqlite()
    
    def _init_postgresql_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=20,
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            print(f"✅ PostgreSQL connection pool initialized ({config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME})")
        except Exception as e:
            print(f"❌ Failed to initialize PostgreSQL pool: {e}")
            print("⚠️  Falling back to SQLite")
            self.db_type = 'sqlite'
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Initialize SQLite (no pooling needed, uses thread-local connections)"""
        self.db_type = 'sqlite'
        print(f"✅ Using SQLite database at {config.SQLITE_DB_PATH}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool (context manager)"""
        if self.db_type == 'postgresql' and self._pool:
            conn = self._pool.getconn()
            try:
                yield conn
            finally:
                self._pool.putconn(conn)
        else:
            # SQLite - use thread-local connection
            if not hasattr(self._local, 'conn') or self._local.conn is None:
                db_path = os.path.join(config.SQLITE_DB_PATH, 'app.db')
                self._local.conn = sqlite3.connect(db_path, check_same_thread=False)
                self._local.conn.row_factory = sqlite3.Row
            
            yield self._local.conn
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results as list of dicts"""
        with self.get_connection() as conn:
            if self.db_type == 'postgresql':
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                cursor.close()
                return results
            else:
                cursor = conn.execute(query, params or ())
                return [dict(row) for row in cursor.fetchall()]
    
    def execute_write(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected row count or last row ID"""
        with self.get_connection() as conn:
            if self.db_type == 'postgresql':
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                rowcount = cursor.rowcount
                cursor.close()
                return rowcount
            else:
                cursor = conn.execute(query, params or ())
                conn.commit()
                return cursor.lastrowid
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute batch INSERT/UPDATE with multiple parameter sets"""
        with self.get_connection() as conn:
            if self.db_type == 'postgresql':
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                rowcount = cursor.rowcount
                cursor.close()
                return rowcount
            else:
                cursor = conn.executemany(query, params_list)
                conn.commit()
                return cursor.rowcount
    
    def close_all(self):
        """Close all connections in pool"""
        if self.db_type == 'postgresql' and self._pool:
            self._pool.closeall()
        elif hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None


# Global database pool instance
db_pool = DatabasePool()


# Convenience functions
def get_db_connection():
    """Get database connection (for backward compatibility)"""
    return db_pool.get_connection()


def query(sql: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Execute SELECT query"""
    return db_pool.execute_query(sql, params)


def execute(sql: str, params: tuple = None) -> int:
    """Execute INSERT/UPDATE/DELETE query"""
    return db_pool.execute_write(sql, params)


def execute_many(sql: str, params_list: List[tuple]) -> int:
    """Execute batch INSERT/UPDATE"""
    return db_pool.execute_many(sql, params_list)
