"""
Rate limit model for API access control.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..base import Base

class RateLimit(Base):
    """Rate limiting for API access"""
    __tablename__ = "rate_limits"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False)  # IP or user identifier
    counter = Column(Integer, default=0)
    reset_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<RateLimit(id={self.id}, key='{self.key}', counter={self.counter})>" 