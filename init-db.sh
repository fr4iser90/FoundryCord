#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create application database if not exists
    SELECT 'CREATE DATABASE ${POSTGRES_DB}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}');

    -- Create application user
    DO \$\$ 
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$APP_DB_USER') THEN
            CREATE USER "$APP_DB_USER" WITH PASSWORD '$APP_DB_PASSWORD';
        END IF;
    END \$\$;

    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$APP_DB_USER";
    GRANT ALL ON SCHEMA public TO "$APP_DB_USER";
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "$APP_DB_USER";
EOSQL

# Create extensions and set up schema
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL