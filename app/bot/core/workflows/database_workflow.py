import logging
import asyncio
from typing import Dict, Any, Optional
import nextcord  # Geändert von discord zu nextcord
from sqlalchemy import text  # Wichtig: text direkt importieren

from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class DatabaseWorkflow(BaseWorkflow):
    """Workflow for database operations"""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "database"
        self.db_service = None
    
    async def initialize(self):
        """Initialize the database workflow"""
        logger.info("Initializing database connection")
        
        try:
            # Import database service
            from app.shared.infrastructure.database.service import DatabaseService
            
            # Create database service
            self.db_service = DatabaseService()
            
            # Da weder initialize() noch is_ready() existieren, 
            # versuchen wir, eine einfache Verbindung herzustellen
            # um zu prüfen, ob die Datenbank verfügbar ist
            try:
                # Prüfen, ob wir eine Engine bekommen können
                engine = self.db_service.get_engine()
                if engine:
                    # Versuchen, eine einfache Abfrage auszuführen
                    async with engine.connect() as conn:
                        # Einfache Abfrage, um zu prüfen, ob die Verbindung funktioniert
                        await conn.execute(text("SELECT 1"))  # text() direkt verwenden
                    logger.info("Database connection verified successfully")
                    return True
                else:
                    logger.error("Failed to get database engine")
                    return False
            except Exception as db_error:
                logger.error(f"Database connection test failed: {db_error}")
                return False
            
        except Exception as e:
            logger.error(f"Error initializing database workflow: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def cleanup(self):
        """Cleanup database resources"""
        logger.info("Cleaning up database resources")
        
        try:
            if self.db_service:
                # Check if cleanup method exists before calling it
                if hasattr(self.db_service, 'cleanup') and callable(self.db_service.cleanup):
                    await self.db_service.cleanup()
                elif hasattr(self.db_service, 'close') and callable(self.db_service.close):
                    await self.db_service.close()
                elif hasattr(self.db_service, 'dispose') and callable(self.db_service.dispose):
                    await self.db_service.dispose()
                else:
                    # Wenn keine Cleanup-Methode vorhanden ist, versuchen wir,
                    # die Engine zu schließen, falls sie existiert
                    engine = getattr(self.db_service, 'engine', None)
                    if engine and hasattr(engine, 'dispose'):
                        await engine.dispose()
            
            logger.info("Database resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up database resources: {e}")
    
    def get_db_service(self):
        """Get the database service"""
        return self.db_service
