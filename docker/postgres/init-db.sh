#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."
sleep 10  # Give PostgreSQL time to start up properly

echo "PostgreSQL is up - executing database setup"

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
APP_DB_USER=${APP_DB_USER:-homelab_discord_bot}
POSTGRES_DB=${POSTGRES_DB:-homelab}

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
    
    -- Create security_keys table for storing credentials
    CREATE TABLE IF NOT EXISTS security_keys (
        id SERIAL PRIMARY KEY,
        key_name VARCHAR(255) NOT NULL UNIQUE,
        key_value TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Store the database credentials in the security_keys table
    INSERT INTO security_keys (key_name, key_value) 
    VALUES ('db_postgres_password', '$POSTGRES_PASSWORD') 
    ON CONFLICT (key_name) DO UPDATE SET key_value = '$POSTGRES_PASSWORD', updated_at = CURRENT_TIMESTAMP;
    
    INSERT INTO security_keys (key_name, key_value) 
    VALUES ('db_app_password', '$APP_DB_PASSWORD') 
    ON CONFLICT (key_name) DO UPDATE SET key_value = '$APP_DB_PASSWORD', updated_at = CURRENT_TIMESTAMP;
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