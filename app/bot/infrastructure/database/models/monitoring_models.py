from sqlalchemy import Column, BigInteger, String, Float, DateTime, JSON, ForeignKey, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from .base import Base

class AlertSeverity(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class MetricModel(Base):
    __tablename__ = 'metrics'
    
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String)
    service = Column(String, index=True, nullable=True)  # Which service/component this metric belongs to
    category = Column(String, index=True, nullable=True)  # For grouping similar metrics
    timestamp = Column(DateTime, default=func.now(), index=True)
    extra_data = Column(JSON, nullable=True)
    
    # Additional index for time-series queries
    __table_args__ = (
        Index('idx_metrics_name_timestamp', 'name', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Metric(name='{self.name}', value={self.value}, unit='{self.unit}')>"

class AlertModel(Base):
    __tablename__ = 'alerts'
    
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, index=True)
    source = Column(String, nullable=False, index=True)
    service = Column(String, index=True, nullable=True)  # Which service/component this alert belongs to
    timestamp = Column(DateTime, default=func.now(), index=True)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, ForeignKey('users.discord_id'), nullable=True)
    details = Column(JSON, nullable=True)
    
    # Relationship to user who acknowledged
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])
    
    def __repr__(self):
        return f"<Alert(name='{self.name}', severity='{self.severity}', status='{self.status}')>"