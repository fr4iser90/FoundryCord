"""Database API for simple access to database functions."""
from app.shared.infrastructure.database.core.connection import get_db_connection
from app.shared.infrastructure.database.session.factory import get_session, initialize_session
from app.shared.infrastructure.database.session.context import session_context
from app.shared.infrastructure.database.service import DatabaseService

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
    async with session_context() as session:
        result = await session.execute(query, params)
        return result

async def fetch_all(query, params=None):
    """Execute a query and fetch all results as dictionaries.
    
    Args:
        query: SQL query string
        params: Query parameters
        
    Returns:
        List of result rows as dictionaries
    """
    async with session_context() as session:
        result = await session.execute(query, params)
        return result.fetchall()

async def fetch_one(query, params=None):
    """Execute a query and fetch one result as a dictionary.
    
    Args:
        query: SQL query string
        params: Query parameters
        
    Returns:
        Result row as dictionary or None if no result
    """
    async with session_context() as session:
        result = await session.execute(query, params)
        return result.first()

__all__ = [
    'get_db_connection',
    'get_session',
    'initialize_session',
    'session_context',
    'DatabaseService',
    'fetch_one',
    'fetch_all',
    'execute_query'
] 