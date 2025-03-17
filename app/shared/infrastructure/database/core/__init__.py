"""
Database management and connection initialization.
"""
# Import from connection.py
from .connection import (
    DatabaseConnection, 
    get_db_connection,
    ensure_db_initialized,
    # Config helper functions
    get_config,
    set_config
)

# Import from credential_provider.py
from .credentials import (
    DatabaseCredentialManager, 
    AUTO_DB_CREDENTIAL_MANAGEMENT
)

# Import alternate connection config for migrations and specific non-singleton cases
# These will be used only where specifically requested
from .config import (
    # Renamed imports to avoid conflicts with connection.py
    get_async_session as get_direct_async_session,
    get_session as get_direct_session,
    initialize_engine as initialize_direct_engine,
    initialize_session as initialize_direct_session,
    create_db_engine
)

# Import from config.py
from .config import (
    get_database_url,
    create_db_engine
)

# Add DATABASE_URL for backward compatibility
DATABASE_URL = get_database_url()

__all__ = [
    # From connection.py
    "DatabaseConnection", 
    "get_db_connection",
    "ensure_db_initialized",
    "get_config",
    "set_config",
    
    # From credential_provider.py
    "DatabaseCredentialManager",
    "AUTO_DB_CREDENTIAL_MANAGEMENT",
    
    # From config.py (with unique names)
    "get_direct_async_session",
    "get_direct_session",
    "initialize_direct_engine",
    "initialize_direct_session",
    "create_db_engine",
    
    # From config.py
    "get_database_url",
    "create_db_engine",
    "DATABASE_URL",  # Added for backward compatibility
]