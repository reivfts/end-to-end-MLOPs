-- Create databases (executed directly, not in a function)
CREATE DATABASE IF NOT EXISTS rbac_db;
CREATE DATABASE IF NOT EXISTS booking_db;
CREATE DATABASE IF NOT EXISTS notification_db;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE rbac_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE booking_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE notification_db TO postgres;
