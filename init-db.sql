-- Create rbac_db if it doesn't exist
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'rbac_db') THEN
      PERFORM pg_sleep(1); -- small delay avoids race conditions
      EXECUTE 'CREATE DATABASE rbac_db';
   END IF;
END
$$;

-- Create booking_db if it doesn't exist
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'booking_db') THEN
      EXECUTE 'CREATE DATABASE booking_db';
   END IF;
END
$$;

-- Create notification_db if it doesn't exist
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'notification_db') THEN
      EXECUTE 'CREATE DATABASE notification_db';
   END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE rbac_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE booking_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE notification_db TO postgres;
