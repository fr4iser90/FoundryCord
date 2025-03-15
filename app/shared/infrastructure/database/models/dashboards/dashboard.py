from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.shared.infrastructure.database.models.base import Base

class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    dashboard_type = Column(String, nullable=False, index=True)  # welcome, monitoring, project, etc.
    guild_id = Column(String, nullable=False, index=True)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=True)  # The main message ID, if applicable
    position = Column(Integer, default=0)  # For ordering dashboards
    is_active = Column(Boolean, default=True)
    update_frequency = Column(Integer, default=300)  # seconds
    config = Column(JSON, nullable=True)  # Additional configuration
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    components = relationship("DashboardComponent", back_populates="dashboard", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dashboard(id={self.id}, type='{self.dashboard_type}', title='{self.title}')>"
