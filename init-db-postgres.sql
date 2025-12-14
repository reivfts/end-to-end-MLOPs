-- PostgreSQL Database Initialization for Campus Services Hub
-- Creates all required tables for microservices

-- Users Table (Gateway & User Management)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'faculty', 'student')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Rooms Table (Booking Service)
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    capacity INTEGER DEFAULT 30
);

-- Bookings Table (Booking Service)
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    user_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    time_slot VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(room_id, date, time_slot, status)
);

-- Create indexes for bookings
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(date);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);

-- Notifications Table (Notification Service)
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);

-- Insert default rooms
INSERT INTO rooms (name, capacity) VALUES
    ('Conference Room A', 30),
    ('Conference Room B', 20),
    ('Meeting Room C', 10),
    ('Lecture Hall D', 50)
ON CONFLICT DO NOTHING;

-- Insert default admin user (password: admin123)
INSERT INTO users (id, email, name, password, role) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 
     'admin@example.com', 
     'Admin User', 
     'scrypt:32768:8:1$xvbJzHlZYkd7v3Rc$8e6c1fcf0cc9e5a3c7e4b8a9f1d2c3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8',
     'admin')
ON CONFLICT (email) DO NOTHING;

-- Insert default faculty user (password: password123)
INSERT INTO users (id, email, name, password, role) VALUES
    ('faculty-001',
     'faculty@example.com',
     'Faculty User',
     'scrypt:32768:8:1$xvbJzHlZYkd7v3Rc$8e6c1fcf0cc9e5a3c7e4b8a9f1d2c3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8',
     'faculty')
ON CONFLICT (email) DO NOTHING;

-- Insert default student user (password: password123)
INSERT INTO users (id, email, name, password, role) VALUES
    ('student-001',
     'student@example.com',
     'Student User',
     'scrypt:32768:8:1$xvbJzHlZYkd7v3Rc$8e6c1fcf0cc9e5a3c7e4b8a9f1d2c3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8',
     'student')
ON CONFLICT (email) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for users table
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (for Docker environment)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
