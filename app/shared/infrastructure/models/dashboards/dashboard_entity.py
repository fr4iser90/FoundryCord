"""
Dashboard model for UI dashboards.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models import Base

class DashboardEntity(Base):
    """Dashboard configuration model"""
    __tablename__ = "dashboards"
    
    id = Column(Integer, primary_key=True)
    dashboard_type = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    guild_id = Column(String(50), nullable=True, index=True)
    channel_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    update_frequency = Column(Integer, default=300)  # In seconds
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    components = relationship("DashboardComponentEntity", back_populates="dashboard", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DashboardEntity(id={self.id}, type='{self.dashboard_type}', name='{self.name}')>" 