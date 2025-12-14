"""
Database Migration Script
Migrate data from SQLite to PostgreSQL
"""

import sqlite3
import sys
import os

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import psycopg2
    from psycopg2.extras import execute_values
    POSTGRESQL_AVAILABLE = True
except ImportError:
    print("ERROR: psycopg2 not installed. Install with: pip install psycopg2-binary")
    POSTGRESQL_AVAILABLE = False
    sys.exit(1)


def migrate_users(sqlite_conn, pg_conn):
    """Migrate users table"""
    print("Migrating users...")
    
    # Read from SQLite
    sqlite_cursor = sqlite_conn.execute("SELECT id, email, name, password, role, created_at FROM users")
    users = sqlite_cursor.fetchall()
    
    if not users:
        print("  No users to migrate")
        return
    
    # Write to PostgreSQL
    pg_cursor = pg_conn.cursor()
    
    insert_query = """
        INSERT INTO users (id, email, name, password, role, created_at)
        VALUES %s
        ON CONFLICT (email) DO UPDATE SET
            name = EXCLUDED.name,
            password = EXCLUDED.password,
            role = EXCLUDED.role
    """
    
    execute_values(pg_cursor, insert_query, users)
    pg_conn.commit()
    print(f"  ✅ Migrated {len(users)} users")


def migrate_rooms(sqlite_conn, pg_conn):
    """Migrate rooms table"""
    print("Migrating rooms...")
    
    sqlite_cursor = sqlite_conn.execute("SELECT name, capacity FROM rooms")
    rooms = sqlite_cursor.fetchall()
    
    if not rooms:
        print("  No rooms to migrate")
        return
    
    pg_cursor = pg_conn.cursor()
    
    insert_query = """
        INSERT INTO rooms (name, capacity)
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    
    execute_values(pg_cursor, insert_query, rooms)
    pg_conn.commit()
    print(f"  ✅ Migrated {len(rooms)} rooms")


def migrate_bookings(sqlite_conn, pg_conn):
    """Migrate bookings table"""
    print("Migrating bookings...")
    
    sqlite_cursor = sqlite_conn.execute("""
        SELECT room_id, user_id, user_email, date, time_slot, status, created_at
        FROM bookings
    """)
    bookings = sqlite_cursor.fetchall()
    
    if not bookings:
        print("  No bookings to migrate")
        return
    
    pg_cursor = pg_conn.cursor()
    
    insert_query = """
        INSERT INTO bookings (room_id, user_id, user_email, date, time_slot, status, created_at)
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    
    execute_values(pg_cursor, insert_query, bookings)
    pg_conn.commit()
    print(f"  ✅ Migrated {len(bookings)} bookings")


def migrate_notifications(sqlite_conn, pg_conn):
    """Migrate notifications table"""
    print("Migrating notifications...")
    
    sqlite_cursor = sqlite_conn.execute("""
        SELECT id, user_id, type, message, is_read, created_at
        FROM notifications
    """)
    notifications = sqlite_cursor.fetchall()
    
    if not notifications:
        print("  No notifications to migrate")
        return
    
    pg_cursor = pg_conn.cursor()
    
    insert_query = """
        INSERT INTO notifications (id, user_id, type, message, is_read, created_at)
        VALUES %s
        ON CONFLICT (id) DO NOTHING
    """
    
    execute_values(pg_cursor, insert_query, notifications)
    pg_conn.commit()
    print(f"  ✅ Migrated {len(notifications)} notifications")


def main():
    """Main migration function"""
    print("=" * 60)
    print("Campus Services Hub - Database Migration")
    print("SQLite → PostgreSQL")
    print("=" * 60)
    
    # Get PostgreSQL connection details
    pg_host = input("PostgreSQL Host (default: localhost): ").strip() or "localhost"
    pg_port = input("PostgreSQL Port (default: 5432): ").strip() or "5432"
    pg_database = input("PostgreSQL Database (default: campus_services): ").strip() or "campus_services"
    pg_user = input("PostgreSQL User (default: postgres): ").strip() or "postgres"
    pg_password = input("PostgreSQL Password: ").strip()
    
    # Get SQLite paths
    print("\nSQLite database locations:")
    gateway_db = input("Gateway DB path (default: ./gateway.db): ").strip() or "./gateway.db"
    users_db = input("Users DB path (default: ./user-management/users.db): ").strip() or "./user-management/users.db"
    bookings_db = input("Bookings DB path (default: ./booking/bookings.db): ").strip() or "./booking/bookings.db"
    notifications_db = input("Notifications DB path (default: ./notification/notifications.db): ").strip() or "./notification/notifications.db"
    
    try:
        # Connect to PostgreSQL
        print("\n🔌 Connecting to PostgreSQL...")
        pg_conn = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            database=pg_database,
            user=pg_user,
            password=pg_password
        )
        print("✅ Connected to PostgreSQL")
        
        # Migrate users
        if os.path.exists(users_db):
            print(f"\n📂 Opening {users_db}...")
            sqlite_conn = sqlite3.connect(users_db)
            migrate_users(sqlite_conn, pg_conn)
            sqlite_conn.close()
        else:
            print(f"⚠️  Users database not found: {users_db}")
        
        # Migrate rooms and bookings
        if os.path.exists(bookings_db):
            print(f"\n📂 Opening {bookings_db}...")
            sqlite_conn = sqlite3.connect(bookings_db)
            migrate_rooms(sqlite_conn, pg_conn)
            migrate_bookings(sqlite_conn, pg_conn)
            sqlite_conn.close()
        else:
            print(f"⚠️  Bookings database not found: {bookings_db}")
        
        # Migrate notifications
        if os.path.exists(notifications_db):
            print(f"\n📂 Opening {notifications_db}...")
            sqlite_conn = sqlite3.connect(notifications_db)
            migrate_notifications(sqlite_conn, pg_conn)
            sqlite_conn.close()
        else:
            print(f"⚠️  Notifications database not found: {notifications_db}")
        
        pg_conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Verify data in PostgreSQL")
        print("2. Update .env file with PostgreSQL credentials")
        print("3. Set DATABASE_TYPE=postgresql")
        print("4. Restart all services")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    if not POSTGRESQL_AVAILABLE:
        sys.exit(1)
    main()
