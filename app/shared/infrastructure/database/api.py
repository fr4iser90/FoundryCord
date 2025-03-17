"""Database API for simple access to database functions."""
from app.shared.infrastructure.database.core.connection import get_db_connection
from app.shared.infrastructure.database.session.factory import get_session
from app.shared.infrastructure.database.session.context import session_context

def get_db():
    """Get the database connection object.
    
    This provides methods like execute() and fetch() for direct query execution.
    
    Returns:
        DatabaseConnection: Database connection instance
    """
    return get_db_connection()

async def execute_query(query, params=None):
    """Execute a SQL query and return the result.
    
    Args:
        query: SQL query string
        params: Query parameters
        
    Returns:
        Query result
    """
    db = get_db_connection()
    if params:
        return await db.execute(query, params)
    return await db.execute(query)

async def fetch_all(query, params=None):
    """Execute a query and fetch all results as dictionaries.
    
    Args:
        query: SQL query string
        params: Query parameters
        
    Returns:
        List of result rows as dictionaries
    """
    db = get_db_connection()
    if params:
        return await db.fetch(query, params)
    return await db.fetch(query)

async def fetch_one(query, params=None):
    """Execute a query and fetch one result as a dictionary.
    
    Args:
        query: SQL query string
        params: Query parameters
        
    Returns:
        Result row as dictionary or None if no result
    """
    results = await fetch_all(query, params)
    return results[0] if results else None

__all__ = [
    'get_db',
    'get_session',
    'session_context',
    'execute_query',
    'fetch_all',
    'fetch_one'
] 