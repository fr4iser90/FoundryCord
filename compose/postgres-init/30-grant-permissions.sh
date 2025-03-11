#!/bin/bash
set -e
source /docker-entrypoint-initdb.d/01-vars.sh

echo "Granting permissions to $APP_USER..."
# Datenbank ist jetzt garantiert vorhanden
psql -v ON_ERROR_STOP=1 -U postgres -d "$DB_NAME" <<-EOSQL
    GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$APP_USER";
    GRANT ALL ON SCHEMA public TO "$APP_USER";
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "$APP_USER";
EOSQL

# Speichere Anmeldedaten im gemeinsamen Volume mit korrekten Zugriffsrechten
if [ -d "/var/lib/postgresql/shared" ]; then
    echo "Saving database credentials to shared volume..."
    
    # Ensure directory has proper permissions
    mkdir -p /var/lib/postgresql/shared
    chmod 777 /var/lib/postgresql/shared
    
    # Write credentials with more permissive file mode
    echo "APP_DB_USER=$APP_USER" > /var/lib/postgresql/shared/db_credentials
    echo "APP_DB_PASSWORD=$APP_PASSWORD" >> /var/lib/postgresql/shared/db_credentials
    chmod 666 /var/lib/postgresql/shared/db_credentials
    
    echo "Credentials saved with permissions 666"
fi
