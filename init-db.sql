-- Create databases for MLOps platform
CREATE DATABASE rbac_db;
CREATE DATABASE booking_db;
CREATE DATABASE notification_db;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE rbac_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE booking_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE notification_db TO postgres;
