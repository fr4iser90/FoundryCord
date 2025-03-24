"""
Database Package for HomeLab Discord Bot

This package provides database connectivity, models, and repositories for 
PostgreSQL interactions. It implements a clean architecture approach with
repository patterns for data access.

Database Structure:
- PostgreSQL for persistent storage
- SQLAlchemy as the ORM for Python interactions
- Alembic for database migrations
- Asyncio-compatible database operations

Environment Configuration:
- POSTGRES_HOST: Database host (default: postgres)
- POSTGRES_PORT: Database port (default: 5432)
- POSTGRES_DB: Database name (default: homelab)
- APP_DB_USER: Application database user (default: homelab_discord_bot)
- APP_DB_PASSWORD: Application database password
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

# Configure module logger
logger = logging.getLogger("homelab.database")

# First import the essentials for database connection
from app.shared.infrastructure.database.core import (
    DatabaseConnection, get_db_connection,
    DatabaseCredentialManager, AUTO_DB_CREDENTIAL_MANAGEMENT
)

# Only after db connection is available, import migrations
from app.shared.infrastructure.database.migrations.init_db import init_db, is_database_empty
from app.shared.infrastructure.database.migrations.wait_for_postgres import wait_for_postgres

# Import models
from app.shared.infrastructure.models import (
    Base,
    User, Session, RateLimit, AuditLog,
    ChannelMapping, CategoryMapping,
    DashboardMessageEntity,
    Project, Task,
    MetricModel, AlertModel,
    Config,
    DashboardEntity,
    DashboardComponentEntity
)



# Import API functions
from .api import (
    get_db_connection,
    get_session,
    initialize_session,
    session_context,
    DatabaseService,
    fetch_one
)

# Import core functions
from .core import (
    ensure_db_initialized
)

# Import additional components
from app.shared.infrastructure.database.api import get_session
from app.shared.infrastructure.database.service import DatabaseService

# Import the bootstrapper directly instead of individual initialization functions
from app.shared.infrastructure.database.bootstrapper import initialize_database

# Export all components for easy imports elsewhere
__all__ = [
    # Primary entry point for database initialization 
    'initialize_database',
    
    # Models
    'Base',
    'User', 'Session', 'RateLimit', 'AuditLog',
    'ChannelMapping', 'CategoryMapping',
    'DashboardMessage',
    'Project', 'Task',
    'MetricModel', 'AlertModel',
    'Config',
    'DashboardEntity',
    'DashboardComponentEntity',

    # Database management
    'DatabaseConnection',
    'get_db_connection',
    'DatabaseCredentialManager',
    'AUTO_DB_CREDENTIAL_MANAGEMENT',
    
    # Database initialization
    'init_db',
    'is_database_empty',
    'wait_for_postgres',
    
    # API functions
    'get_db_connection',
    'get_session',
    'initialize_session',
    'session_context',
    'DatabaseService',
    'fetch_one',
    
    # Core functions
    'ensure_db_initialized',
    'AsyncSession'
]

# Database utility functions
async def get_database_status():
    """
    Get the current status of the database connection.
    
    Returns:
        dict: Status information including connection state,
              database version, and connection details
    """
    try:
        conn = get_db_connection()
        result = await conn.fetch_one("SELECT version();")
        return {
            "status": "connected",
            "version": result.get("version"),
            "details": "PostgreSQL connection successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "details": "Failed to connect to PostgreSQL database"
        }

# Database connection setup function
async def setup_database_connection():
    """
    Set up and return a database connection for use in application components.
    This function centralizes database connection logic.
    
    Returns:
        AsyncSession: An active database session
    """
    return await get_session()