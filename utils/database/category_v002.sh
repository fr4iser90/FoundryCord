#!/bin/bash
# category_v002.sh - Script zum Aktualisieren der Datenbankstruktur
# Besonders hilfreich für Container-Umgebungen ohne interaktiven Zugriff

set -e  # Skript beenden wenn ein Befehl fehlschlägt

echo "=== Homelab Discord Bot: Datenbank-Update-Tool ==="
echo "Starte Datenbank-Migration für CategoryMapping Tabelle..."

# Prüfe, ob wir im Container oder lokal ausgeführt werden
IN_CONTAINER=false
if [ -f "/.dockerenv" ]; then
    IN_CONTAINER=true
    echo "Ausführung innerhalb des Containers erkannt"
fi

# Wenn nicht im Container, dann über Docker ausführen
if [ "$IN_CONTAINER" = false ]; then
    echo "Führe Skript im Discord-Bot-Container aus..."
    CONTAINER_ID=$(docker ps -qf "name=homelab-discord-bot")
    
    if [ -z "$CONTAINER_ID" ]; then
        echo "Fehler: Discord Bot Container nicht gefunden!"
        exit 1
    fi
    
    docker exec -it "$CONTAINER_ID" bash -c "/infrastrucure/database/migrations/category_v002.sh"
    exit $?
fi

# Ab hier läuft das Skript im Container
echo "Erstelle temporäre Python-Datei zur Datenbank-Reparatur..."

# Temporäre Python-Datei erstellen
cat > /tmp/fix_category_mapping.py << 'EOL'
import asyncio
from sqlalchemy import text
from app.bot.infrastructure.database.models.config import initialize_engine
from app.bot.infrastructure.logging import logger

async def fix_category_mapping_table():
    try:
        print("Starte Datenbank-Reparatur für CategoryMapping...")
        engine = await initialize_engine()
        
        async with engine.begin() as conn:
            # 1. Prüfen, ob die Tabelle existiert
            result = await conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'category_mappings')"
            ))
            table_exists = result.scalar()
            
            if not table_exists:
                print("Tabelle category_mappings existiert nicht - keine Aktion notwendig")
                return
            
            # 2. Prüfen, ob die Spalte category_type existiert
            result = await conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'category_mappings' AND column_name = 'category_type')"
            ))
            column_exists = result.scalar()
            
            if column_exists:
                print("Spalte category_type existiert bereits - keine Aktion notwendig")
                return
            
            print("Spalte category_type fehlt - führe Reparatur durch...")
            
            # 3. Sichern der vorhandenen Daten
            result = await conn.execute(text("SELECT * FROM category_mappings"))
            rows = result.fetchall()
            print(f"Gesichert: {len(rows)} Einträge")
            
            # 4. Tabelle umbenennen
            await conn.execute(text("ALTER TABLE category_mappings RENAME TO category_mappings_old"))
            print("Tabelle umbenannt zu category_mappings_old")
            
            # 5. Neue Tabelle mit korrektem Schema erstellen
            await conn.execute(text("""
                CREATE TABLE category_mappings (
                    id SERIAL PRIMARY KEY,
                    guild_id VARCHAR,
                    category_id VARCHAR,
                    category_name VARCHAR,
                    category_type VARCHAR DEFAULT 'homelab',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT uix_category_guild_type UNIQUE (guild_id, category_type)
                )
            """))
            print("Neue Tabelle category_mappings erstellt")
            
            # 6. Index erstellen
            await conn.execute(text("CREATE INDEX ix_category_mappings_guild_id ON category_mappings (guild_id)"))
            print("Index auf guild_id erstellt")
            
            # 7. Daten migrieren
            for row in rows:
                await conn.execute(text("""
                    INSERT INTO category_mappings (id, guild_id, category_id, category_name, created_at, updated_at)
                    VALUES (:id, :guild_id, :category_id, :category_name, :created_at, :updated_at)
                """), {
                    'id': row[0],
                    'guild_id': row[1],
                    'category_id': row[2],
                    'category_name': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                })
            print(f"Daten migriert: {len(rows)} Einträge")
            
            # 8. Alte Tabelle löschen
            await conn.execute(text("DROP TABLE category_mappings_old"))
            print("Alte Tabelle gelöscht")
            
            print("Datenbank-Reparatur erfolgreich abgeschlossen!")
    
    except Exception as e:
        print(f"Fehler bei der Datenbank-Reparatur: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(fix_category_mapping_table())
EOL

echo "Führe Python-Skript zur Datenbank-Reparatur aus..."
cd /app/bot && python -m /tmp/fix_category_mapping.py

# Lösche temporäre Datei
rm /tmp/fix_category_mapping.py

echo "=== Datenbank-Update abgeschlossen ==="
echo "Bot muss nun neu gestartet werden mit: docker-compose restart bot"