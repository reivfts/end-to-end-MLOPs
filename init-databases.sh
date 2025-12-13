#!/bin/bash
# Initialize PostgreSQL databases with error handling
# This script won't crash the container if databases already exist

set +e  # Don't exit on errors

psql -U postgres <<EOF
CREATE DATABASE rbac_db;
CREATE DATABASE booking_db;
CREATE DATABASE notification_db;

GRANT ALL PRIVILEGES ON DATABASE rbac_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE booking_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE notification_db TO postgres;
EOF

# Always exit successfully to prevent container crash
exit 0
