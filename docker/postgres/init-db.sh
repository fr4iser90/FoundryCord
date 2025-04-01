#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."
sleep 10  # Give PostgreSQL time to start up properly

echo "PostgreSQL is up - executing database setup"

# Check for required environment variables
if [ -z "$OWNER" ]; then
    echo "Error: Missing OWNER environment variable. Please set it in the .env file."
    exit 1
fi

# Auto-generate secure passwords if not provided
if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "No POSTGRES_PASSWORD found, generating secure password..."
    POSTGRES_PASSWORD=$(openssl rand -base64 20 | tr -dc 'a-zA-Z0-9' | head -c 20)
    
    # Save credentials to file ONLY in development mode
    if [ "$ENVIRONMENT" = "development" ]; then
        echo "Development mode detected, saving credentials to file..."
        echo "# Auto-generated PostgreSQL credentials" > /var/lib/postgresql/data/.env.credentials
        echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> /var/lib/postgresql/data/.env.credentials
        echo "Password saved to /var/lib/postgresql/data/.env.credentials"
    fi
    
    echo "Generated secure PostgreSQL password"
fi

if [ -z "$APP_DB_PASSWORD" ]; then
    echo "No APP_DB_PASSWORD found, generating secure password..."
    APP_DB_PASSWORD=$(openssl rand -base64 20 | tr -dc 'a-zA-Z0-9' | head -c 20)
    
    # Save to credentials file ONLY in development mode
    if [ "$ENVIRONMENT" = "development" ]; then
        if [ -f "/var/lib/postgresql/data/.env.credentials" ]; then
            echo "APP_DB_PASSWORD=$APP_DB_PASSWORD" >> /var/lib/postgresql/data/.env.credentials
        else
            echo "# Auto-generated PostgreSQL credentials" > /var/lib/postgresql/data/.env.credentials
            echo "APP_DB_PASSWORD=$APP_DB_PASSWORD" >> /var/lib/postgresql/data/.env.credentials
        fi
        echo "App password saved to credentials file"
    fi
    
    echo "Generated secure application database password"
fi

# Set default values for other variables if not provided
APP_DB_USER=${APP_DB_USER:-foundrycord_bot}
POSTGRES_DB=${POSTGRES_DB:-foundrycord}

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
    
    -- Create alembic_version table for migration tracking
    CREATE TABLE IF NOT EXISTS alembic_version (
        version_num VARCHAR(32) NOT NULL,
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
    );
    
    -- Grant all necessary permissions
    GRANT ALL ON SCHEMA public TO "$APP_DB_USER";
    
    -- Grant ALL on existing tables and sequences
    GRANT ALL ON ALL TABLES IN SCHEMA public TO "$APP_DB_USER";
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO "$APP_DB_USER";
    
    -- Grant for FUTURE tables and sequences (wichtig!)
    ALTER DEFAULT PRIVILEGES FOR ROLE "$POSTGRES_USER" IN SCHEMA public 
    GRANT ALL ON TABLES TO "$APP_DB_USER";
    
    ALTER DEFAULT PRIVILEGES FOR ROLE "$POSTGRES_USER" IN SCHEMA public 
    GRANT ALL ON SEQUENCES TO "$APP_DB_USER";
    
    -- Ensure sequence permissions are set correctly
    DO $$
    DECLARE
        seq_name text;
    BEGIN
        FOR seq_name IN 
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
        LOOP
            EXECUTE format(
                'GRANT ALL ON SEQUENCE %I TO %I', 
                seq_name, 
                '$APP_DB_USER'
            );
        END LOOP;
    END $$;

    -- Create security_keys table (this needs to exist before migrations)
    CREATE TABLE IF NOT EXISTS security_keys (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        value TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Grant specific permissions
    GRANT ALL PRIVILEGES ON TABLE security_keys TO "$APP_DB_USER";
    GRANT USAGE, SELECT ON SEQUENCE security_keys_id_seq TO "$APP_DB_USER";
    GRANT ALL PRIVILEGES ON TABLE alembic_version TO "$APP_DB_USER";

    -- Store the database credentials in the security_keys table
    INSERT INTO security_keys (name, value) 
    VALUES ('db_postgres_password', '$POSTGRES_PASSWORD') 
    ON CONFLICT (name) DO UPDATE SET value = '$POSTGRES_PASSWORD';
    
    INSERT INTO security_keys (name, value) 
    VALUES ('db_app_password', '$APP_DB_PASSWORD') 
    ON CONFLICT (name) DO UPDATE SET value = '$APP_DB_PASSWORD';
EOSQL

# Create extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL

# Execute core tables initialization script
echo "Creating core tables..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/init-tables.sql

echo "Database initialization completed successfully"
echo "------------------------------------------------"
echo "Database is ready with secure credentials"
echo "If this is a development environment, credentials are saved in the PostgreSQL volume"
echo "For production, the credentials are stored securely in the database"
echo "------------------------------------------------"