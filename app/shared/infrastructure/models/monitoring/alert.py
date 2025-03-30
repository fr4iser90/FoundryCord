"""
Alert model for system monitoring.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.shared.infrastructure.models import Base

class AlertModel(Base):
    """System alert model"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    level = Column(String(20), nullable=False, index=True)  # info, warning, error, critical
    source = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    expires_at = Column(DateTime, nullable=True)
    alert_data = Column(JSON, nullable=True)  # Renamed from metadata
    
    def __repr__(self):
        return f"<AlertModel(id={self.id}, title='{self.title}', level='{self.level}')>" 