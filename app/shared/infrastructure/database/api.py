"""Database API access."""
from app.shared.infrastructure.database.management.connection import get_db_connection
from app.shared.infrastructure.database.management.connection_config import get_async_session

# Determine which implementation to use
def get_db():
    """Get database access object with execute and fetch methods."""
    # Return the connection object from connection.py
    return get_db_connection()

# Keep both functions available for backward compatibility
__all__ = ['get_db', 'get_async_session'] 