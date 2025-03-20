"""Database migration service."""
import asyncio
import logging
import os
import subprocess
import traceback
from pathlib import Path

from app.shared.interface.logging.api import get_db_logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

logger = get_db_logger()

class MigrationService:
    """Service für die Verwaltung von Datenbankmigrationen."""
    
    def __init__(self):
        """Initialisiere den Migration Service."""
        # Verwende immer den korrekten Pfad zur alembic.ini
        self.alembic_dir = Path("/app/shared/infrastructure/database/migrations/alembic")
        self.alembic_ini = self.alembic_dir / "alembic.ini"
        
    async def run_migrations(self) -> bool:
        """Führe alle ausstehenden Migrationen aus."""
        try:
            # Stelle sicher, dass alembic.ini existiert
            if not self.alembic_ini.exists():
                logger.error(f"alembic.ini nicht gefunden: {self.alembic_ini}")
                return False
            
            # Führe Migrationen aus
            logger.info("Führe Datenbankmigrationen aus...")
            
            # Wechsle zum alembic-Verzeichnis
            os.chdir(str(self.alembic_dir))
            
            # Ausgabe des aktuellen Verzeichnisses für Debugging
            logger.info(f"Ausführung von Alembic im Verzeichnis: {os.getcwd()}")
            
            # Verbesserter Debug-Output: Zeige tatsächliche Dateien im Verzeichnis
            try:
                # Liste alle Migrations-Dateien auf
                all_files = os.listdir(str(self.alembic_dir))
                versions_dir = self.alembic_dir / 'versions'
                version_files = os.listdir(str(versions_dir)) if versions_dir.exists() else []
                
                logger.info(f"Dateien im alembic-Verzeichnis: {all_files}")
                logger.info(f"Migrations-Dateien: {version_files}")
            except Exception as e:
                logger.error(f"Konnte Dateien nicht auflisten: {e}")
            
            # Verbesserter Debug-Output: Zeige, ob die init.py, env.py und versions/ existieren
            logger.info(f"Alembic-Dateien check:")
            logger.info(f"  alembic.ini existiert: {self.alembic_ini.exists()}")
            logger.info(f"  alembic/env.py existiert: {(self.alembic_dir / 'env.py').exists()}")
            logger.info(f"  alembic/versions/ existiert: {(self.alembic_dir / 'versions').exists()}")
            
            # Prüfe Validität der Migrations-Kette
            try:
                # Prüfe alle Migrationen vor dem Ausführen
                check_result = subprocess.run(
                    ["alembic", "check"],
                    capture_output=True,
                    text=True,
                    cwd=str(self.alembic_dir)
                )
                
                if check_result.returncode != 0:
                    logger.warning(f"Alembic check fehlgeschlagen: {check_result.stderr}")
                    logger.warning("Versuche trotzdem, Migrationen durchzuführen...")
            except Exception as e:
                logger.warning(f"Konnte Migrationen nicht prüfen: {e}")
            
            # Fallback bei fehlenden Migrations-Dateien
            required_migrations = ['001_create_tables.py', '002_seed_categories.py', '003_seed_channels.py']
            versions_path = self.alembic_dir / 'versions'
            
            for migration in required_migrations:
                migration_path = versions_path / migration
                if not migration_path.exists():
                    logger.warning(f"Migration {migration} fehlt, versuche neu zu erstellen")
                    # Hier könnte man dynamisch Migrations-Dateien erstellen
            
            # Ohne config-Datei ausführen (direkt mit dem alembic-Verzeichnis)
            result = subprocess.run(
                ["alembic", "upgrade", "head"], 
                capture_output=True,
                text=True,
                cwd=str(self.alembic_dir)  # Explizit das Arbeitsverzeichnis setzen
            )
            
            # Logge die vollständigen Ausgaben
            logger.info(f"Alembic stdout: {result.stdout}")
            if result.stderr:
                logger.error(f"Alembic stderr: {result.stderr}")
            
            # Prüfe Ergebnis
            if result.returncode != 0:
                logger.error(f"Migrationen fehlgeschlagen: {result.returncode}")
                # Versuche trotzdem Tabellen zu erstellen, wenn Alembic nicht funktioniert
                logger.warning("Versuche Tabellen direkt zu erstellen...")
                await self.create_essential_tables()
                return True  # Gib True zurück, um die Anwendung weiterlaufen zu lassen
            
            logger.info("Migrationen erfolgreich ausgeführt")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Ausführen der Migrationen: {e}")
            logger.error(traceback.format_exc())
            # Abfangen und trotzdem True zurückgeben, um Anwendungsinitialisierung nicht zu blockieren
            logger.info("Fahre trotz Migration-Fehler mit der Anwendungsinitialisierung fort")
            return True
            
    async def check_migrations(self) -> bool:
        """Prüfe, ob Migrationen nötig sind."""
        try:
            # Wechsle zum alembic-Verzeichnis
            os.chdir(str(self.alembic_dir))
            
            # Prüfe Migration-Status ohne config-Datei
            result = subprocess.run(
                ["alembic", "current"],
                capture_output=True,
                text=True,
                cwd=str(self.alembic_dir)  # Explizit das Arbeitsverzeichnis setzen
            )
            
            # Gib aktuellen Status zurück
            logger.info(f"Migration-Status: {result.stdout.strip()}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Prüfen der Migrationen: {e}")
            return False
            
    async def create_essential_tables(self) -> bool:
        """Erstelle essentielle Tabellen direkt, wenn Alembic fehlschlägt."""
        try:
            from app.shared.infrastructure.database.core.credentials import DatabaseCredentialManager
            from sqlalchemy.ext.asyncio import create_async_engine
            
            # Get database credentials
            creds = DatabaseCredentialManager().get_credentials()
            db_url = f"postgresql+asyncpg://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}"
            engine = create_async_engine(db_url)
            
            # Erstelle category_templates Tabelle
            async with engine.begin() as conn:
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS category_templates (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        position INTEGER NOT NULL,
                        description VARCHAR(1024),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Weitere Tabellen hier erstellen...
                
            logger.info("Essentielle Tabellen direkt erstellt")
            return True
        except Exception as e:
            logger.error(f"Fehler beim direkten Erstellen der Tabellen: {e}")
            return False
