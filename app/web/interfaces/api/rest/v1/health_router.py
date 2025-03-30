# Create this new file for health and debug endpoints
from fastapi import APIRouter, Depends, Request
import os
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.shared.infrastructure.database import get_db_connection

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "web": "available",
            "database": "available"
        }
    }

@router.get("/debug")
async def debug():
    return {
        "python_path": sys.path,
        "bot_interface_available": bot_interface is not None,
        # Rest of your debug information
    }

@router.get("/db-test")
async def test_db_connection(session: AsyncSession = Depends(get_db_connection)):
    """Test database connection"""
    try:
        # Try a simple query
        result = await session.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "result": result.scalar()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        } 
    
