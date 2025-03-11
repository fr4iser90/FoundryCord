#!/bin/bash
source /docker-entrypoint-initdb.d/01-vars.sh

echo "Schritt 2: Anwendungsbenutzer $APP_USER anlegen falls nicht vorhanden..."

# Sicherstellen, dass APP_PASSWORD nicht leer ist
if [ -z "$APP_PASSWORD" ]; then
  APP_PASSWORD="${APP_DB_PASSWORD:-$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)}"
fi

psql -v ON_ERROR_STOP=1 -U postgres <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$APP_USER') THEN
            CREATE USER "$APP_USER" WITH PASSWORD '$APP_PASSWORD';
            RAISE NOTICE 'Benutzer $APP_USER erstellt';
        ELSE
            -- Update password for existing user
            ALTER USER "$APP_USER" WITH PASSWORD '$APP_PASSWORD';
            RAISE NOTICE 'Password für $APP_USER aktualisiert';
        END IF;
    END \$\$;
EOSQL