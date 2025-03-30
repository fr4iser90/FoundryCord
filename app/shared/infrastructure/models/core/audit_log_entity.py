"""
Audit log model for system action tracking.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.shared.infrastructure.models import Base

class AuditLogEntity(Base):
    """Audit log for tracking actions in the system"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    action = Column(String(100), nullable=False, index=True)
    actor_id = Column(String(100), nullable=True, index=True)  # User ID or system
    actor_type = Column(String(50), nullable=False, default="user")  # user, system, bot
    resource_type = Column(String(100), nullable=True, index=True)  # e.g., "user", "channel", "message"
    resource_id = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)  # Additional structured data
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    def __repr__(self):
        return f"<AuditLogEntity(id={self.id}, action='{self.action}', actor='{self.actor_id}')>" 