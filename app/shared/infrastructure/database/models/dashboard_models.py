from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy.sql import func
from .base import Base

class DashboardMessage(Base):
    __tablename__ = "dashboard_messages"
    
    id = Column(Integer, primary_key=True)
    dashboard_type = Column(String, unique=True, index=True)
    message_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DashboardMessage(dashboard_type='{self.dashboard_type}', message_id={self.message_id})>"
