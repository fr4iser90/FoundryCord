"""
Config database model for storing key-value configuration.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..base import Base

class Config(Base):
    """Configuration key-value storage model."""
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Config(key='{self.key}', value='{self.value}')>" 