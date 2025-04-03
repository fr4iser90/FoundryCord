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
    DatabaseConnection, get_db_connection,
    DatabaseCredentialManager, AUTO_DB_CREDENTIAL_MANAGEMENT
)

# Only after db connection is available, import migrations
from app.shared.infrastructure.database.migrations.wait_for_postgres import wait_for_postgres

# Import models
from app.shared.infrastructure.models import (
    Base,
    AppUserEntity, SessionEntity, RateLimitEntity, AuditLogEntity,
    ChannelMapping, CategoryMapping,
    DashboardMessageEntity,
    Project, Task,
    MetricModel, AlertModel,
    ConfigEntity,
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
    'AppUserEntity', 'SessionEntity', 'RateLimitEntity', 'AuditLogEntity',
    'ChannelMapping', 'CategoryMapping',
    'DashboardMessage',
    'Project', 'Task',
    'MetricModel', 'AlertModel',
    'ConfigEntity',
    'DashboardEntity',
    'DashboardComponentEntity',

    # Database management
    'DatabaseConnection',
    'get_db_connection',
    'DatabaseCredentialManager',
    'AUTO_DB_CREDENTIAL_MANAGEMENT',
    
    # Database initialization
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

