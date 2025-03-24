"""
Connection management for database operations.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from sqlalchemy import select, update, text
import os
import asyncio

from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.models import Config
from .config import get_database_url

logger = get_bot_logger()

# Create a session proxy that adds the fetch method
class SessionProxy:
    """Proxy for SQLAlchemy session with additional methods."""
    
    def __init__(self, session):
        self._session = session
        
    async def execute(self, query, *args, **kwargs):
        """Execute a SQL query."""
        if isinstance(query, str):
            return await self._session.execute(text(query), *args, **kwargs)
        return await self._session.execute(query, *args, **kwargs)
        
    async def fetch(self, query, *args, **kwargs):
        """Execute a query and return results as dictionaries."""
        result = await self.execute(query, *args, **kwargs)
        return [dict(row) for row in result.mappings()]
        
    async def commit(self):
        """Commit the transaction."""
        await self._session.commit()
        
    async def rollback(self):
        """Rollback the transaction."""
        await self._session.rollback()
        
    async def close(self):
        """Close the session."""
        await self._session.close()
        
    def __getattr__(self, name):
        """Delegate all other attributes to the underlying session."""
        return getattr(self._session, name)


# Stelle sicher, dass wir die Datenbankverbindungsdaten aus der Umgebung bekommen
def get_database_connection_string():
    """Get database connection string from environment variables."""
    db_user = os.environ.get('APP_DB_USER')
    db_password = os.environ.get('APP_DB_PASSWORD')
    db_host = os.environ.get('POSTGRES_HOST')
    db_port = os.environ.get('POSTGRES_PORT')
    db_name = os.environ.get('POSTGRES_DB')
    
    if not all([db_user, db_password, db_host, db_port, db_name]):
        logger.warning("Missing database environment variables!")
        # Logge die vorhandenen Variablen, um Fehler zu finden
        for name, value in [
            ('APP_DB_USER', db_user),
            ('POSTGRES_HOST', db_host),
            ('POSTGRES_PORT', db_port),
            ('POSTGRES_DB', db_name)
        ]:
            logger.warning(f"{name}: {value or '[NOT SET]'}")
            
        # Fallback auf Standard-URL wenn Umgebungsvariablen fehlen
        return os.environ.get("DATABASE_URL", "postgresql+asyncpg://homelab_discord_bot:homelab_discord_bot_password@homelab-postgres:5432/homelab")
    
    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

class DatabaseConnection:
    """Database connection manager."""
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._engine = None
            cls._session_factory = None
        return cls._instance
    
    async def initialize(self, connection_string=None):
        """Initialize database connection.
        
        Args:
            connection_string: PostgreSQL connection string.
            If None, uses environment variables.
        """
        if connection_string is None:
            connection_string = get_database_url()
            
        if not connection_string:
            raise ValueError("No database connection string provided")
            
        logger.info(f"Initializing database connection")
        
        # Create engine with proper SQLAlchemy imports
        from sqlalchemy.ext.asyncio import create_async_engine
            
        self._engine = create_async_engine(
            connection_string, 
            echo=False,
            future=True
        )
        
        self._session_factory = sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        
        logger.info("Database connection initialized successfully")
        
    @asynccontextmanager
    async def session(self):
        """Get database session as async context manager.
        
        Yields:
            AsyncSession: Database session.
        """
        if self._session_factory is None:
            await self.initialize()
            
        session = self._session_factory()
        try:
            yield session
        finally:
            await session.close()
            
    async def get_session(self):
        """Get a new database session directly.
        
        Returns:
            AsyncSession: Database session.
        """
        if self._session_factory is None:
            await self.initialize()
            
        return self._session_factory()
    
    # Add transaction support for the repository
    @asynccontextmanager
    async def transaction(self):
        """Begin a transaction and return a session proxy.
        
        This context manager yields a session proxy with a transaction started.
        The transaction is committed when the context exits without an exception,
        or rolled back if an exception occurs.
        
        Yields:
            SessionProxy: Session proxy with active transaction.
        """
        if self._session_factory is None:
            await self.initialize()
            
        session = self._session_factory()
        session_proxy = SessionProxy(session)
        
        try:
            async with session.begin():
                yield session_proxy
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction error: {e}")
            raise
        finally:
            await session.close()
            
    # Add execute method for running SQL statements
    async def execute(self, query, *args, **kwargs):
        """Execute a SQL statement.
        
        Args:
            query: SQL query string
            *args: Positional arguments for the query
            **kwargs: Keyword arguments for the query
            
        Returns:
            Result of the execution
        """
        async with self.session() as session:
            result = await session.execute(text(query), *args, **kwargs)
            await session.commit()
            return result
            
    # Add fetch method for retrieving data
    async def fetch(self, query, *args, **kwargs):
        """Execute a query and fetch all results.
        
        Args:
            query: SQL query string
            *args: Positional arguments for the query
            **kwargs: Keyword arguments for the query
            
        Returns:
            List of result rows as dictionaries
        """
        async with self.session() as session:
            result = await session.execute(text(query), *args, **kwargs)
            return [dict(row) for row in result.mappings()]
    
    # Keep compatibility with existing code
    def initialize_engine(self, connection_string=None):
        """Initialize SQLAlchemy engine.
        
        Args:
            connection_string: Optional database connection string.
                If not provided, uses DATABASE_URL from environment.
        
        Returns:
            SQLAlchemy async engine instance
        """
        self.initialize(connection_string)
        return self._engine
        
    def initialize_session(self, engine=None):
        """Initialize the SQLAlchemy session factory.
        
        Args:
            engine: Optional SQLAlchemy engine instance.
                If not provided, uses internal engine.
        
        Returns:
            SQLAlchemy async session factory
        """
        if engine is not None:
            self._engine = engine
            
        if self._engine is None:
            self.initialize_engine()
            
        self._session_factory = sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        
        return self._session_factory

async def ensure_db_initialized():
    """
    Ensure database is initialized before proceeding.
    Retries connection until successful or max retries reached.
    """
    max_retries = 10
    retry_delay = 2  # seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            conn = await get_db_connection()
            async with conn.session() as session:
                # Try a simple query to verify connection
                await session.execute(select(1))
                logger.info("Database connection established successfully")
                return True
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt}/{max_retries} failed: {str(e)}")
            if attempt == max_retries:
                logger.error("Failed to connect to database after maximum retries")
                return False
            await asyncio.sleep(retry_delay)
    
    return False

# Singleton instance
_connection = None

async def get_db_connection():
    """Get database connection singleton.
    
    Returns:
        DatabaseConnection: Database connection instance.
    """
    global _connection
    if _connection is None:
        _connection = DatabaseConnection()
    return _connection

# Compatibility functions matching what was previously in config.py
@asynccontextmanager
async def get_session():
    """Context manager for database sessions.
    
    Yields:
        SQLAlchemy async session
    """
    conn = await get_db_connection()
    async with conn.session() as session:
        yield session

async def get_async_session():
    """Get a direct database session.
    
    Returns:
        AsyncSession: Database session.
    """
    conn = await get_db_connection()
    return await conn.get_session()

# Config utility functions
async def get_config(session, key):
    """Get a configuration value from the database.
    
    Args:
        session: SQLAlchemy async session
        key: Configuration key to retrieve
        
    Returns:
        Configuration value or None if not found
    """
    result = await session.execute(
        select(Config).where(Config.key == key)
    )
    config = result.scalars().first()
    return config.value if config else None

async def set_config(session, key, value):
    """Set a configuration value in the database.
    
    Args:
        session: SQLAlchemy async session
        key: Configuration key to set
        value: Configuration value
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if config exists
        result = await session.execute(
            select(Config).where(Config.key == key)
        )
        config = result.scalars().first()
        
        if config:
            # Update existing config
            await session.execute(
                update(Config)
                .where(Config.key == key)
                .values(value=value)
            )
        else:
            # Create new config
            config = Config(key=key, value=value)
            session.add(config)
            
        await session.commit()
        return True
    except Exception:
        await session.rollback()
        return False
