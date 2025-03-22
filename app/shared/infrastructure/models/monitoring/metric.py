"""
Metric model for system monitoring.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.sql import func
from ..base import Base

class MetricModel(Base):
    """System metric measurement model"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)  # cpu, memory, disk, network, etc.
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)  # %, MB, GB, etc.
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    host = Column(String(100), nullable=True, index=True)
    service = Column(String(100), nullable=True, index=True)
    metric_data = Column(JSON, nullable=True)  # Renamed from metadata
    
    def __repr__(self):
        return f"<MetricModel(id={self.id}, name='{self.name}', value={self.value})>" 