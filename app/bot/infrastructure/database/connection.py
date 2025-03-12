from app.bot.infrastructure.database.models.config import initialize_engine, initialize_session, engine, AsyncSession
from sqlalchemy import text
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from app.bot.infrastructure.logging.logger import logger

class DatabaseConnection:
    """Connection wrapper for database operations"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
    
    async def ensure_initialized(self):
        """Ensure the engine and session factory are initialized"""
        if self.engine is None:
            from app.bot.infrastructure.database.models.config import engine, initialize_engine
            if engine is None:
                await initialize_engine()
            self.engine = engine
            
            self.session_factory = sessionmaker(
                self.engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
    
    async def get_session(self):
        await self.ensure_initialized()
        session = self.session_factory()
        logger.debug("New database session created")
        return session
    
    async def execute(self, query, params=None):
        """Execute a query"""
        async with await self.get_session() as session:
            result = await session.execute(text(query), params)
            await session.commit()  # Commit after execution
            logger.debug("Database session closed")
            return result
    
    async def fetch_one(self, query, params=None):
        """Fetch a single row"""
        async with await self.get_session() as session:
            result = await session.execute(text(query), params)
            row = result.fetchone()
            logger.debug("Database session closed")
            
            if row is None:
                return None
                
            # If this is a Row object with column names, convert to dict
            if hasattr(row, '_mapping'):
                return dict(row._mapping)
                
            # Fall back to using the keys from the result
            column_names = result.keys()
            return dict(zip(column_names, row))
            
    async def fetch_all(self, query, params=None):
        """Fetch multiple rows"""
        async with await self.get_session() as session:
            result = await session.execute(text(query), params)
            rows = result.fetchall()
            logger.debug("Database session closed")
            
            if not rows:
                return []
                
            # Convert rows to dictionaries
            column_names = result.keys()
            return [dict(zip(column_names, row)) for row in rows]

def get_db_connection():
    """Get a database connection instance"""
    return DatabaseConnection()
