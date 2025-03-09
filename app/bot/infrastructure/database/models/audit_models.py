from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, JSON
from datetime import datetime
from .base import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String, ForeignKey('users.discord_id'))
    action = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuditLog(user_id='{self.user_id}', action='{self.action}')>"
