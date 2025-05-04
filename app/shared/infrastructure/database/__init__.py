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

# First import the essentials for database connection
from app.shared.infrastructure.database.core import (
    DatabaseConnection, 
    get_db_connection,
    DatabaseCredentialManager, 
    AUTO_DB_CREDENTIAL_MANAGEMENT
)


# Import API functions
from .api import (
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

# Export all components for easy imports elsewhere
__all__ = [
    # Database management
    'DatabaseConnection',
    'get_db_connection',
    'DatabaseCredentialManager',
    'AUTO_DB_CREDENTIAL_MANAGEMENT',
    
    # API functions
    'get_session',
    'initialize_session',
    'session_context',
    'DatabaseService',
    'fetch_one',
    
    # Core functions
    'ensure_db_initialized'
]

