#!/bin/bash
source /docker-entrypoint-initdb.d/01-vars.sh

echo "Schritt 1: Datenbank anlegen falls nicht vorhanden..."
psql -v ON_ERROR_STOP=1 -U postgres <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME') THEN
            CREATE DATABASE "$DB_NAME";
            RAISE NOTICE 'Datenbank $DB_NAME erstellt';
        ELSE
            RAISE NOTICE 'Datenbank $DB_NAME existiert bereits';
        END IF;
    END \$\$;
EOSQL