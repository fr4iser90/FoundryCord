#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."
sleep 10  # Give PostgreSQL time to start up properly

echo "PostgreSQL is up - executing database setup"

# Create databases and users
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    -- Create application user if not exists
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$APP_DB_USER') THEN
            CREATE USER "$APP_DB_USER" WITH PASSWORD '$APP_DB_PASSWORD';
            RAISE NOTICE 'Created user $APP_DB_USER';
        ELSE
            RAISE NOTICE 'User $APP_DB_USER already exists';
        END IF;
    END \$\$;

    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$APP_DB_USER";
    \c $POSTGRES_DB
    GRANT ALL ON SCHEMA public TO "$APP_DB_USER";
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "$APP_DB_USER";
EOSQL

# Create extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL

echo "Database initialization completed successfully"