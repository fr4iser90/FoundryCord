from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Text, BigInteger
from sqlalchemy.orm import relationship

# Import the Base from the shared models
from app.shared.database.models.base import Base
from app.shared.database.models.dashboard_models import DashboardMessage as DashboardModel


class DashboardModel(Base):
    """SQLAlchemy model using the existing dashboard_messages table"""
    __tablename__ = "dashboard_messages"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    dashboard_type = Column(String, unique=True, index=True)
    message_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    updated_at = Column(DateTime)
    
    # Add these properties to map to the expected fields
    @property
    def user_id(self):
        """Extract user_id from dashboard_type"""
        return self.dashboard_type.split('_')[0] if self.dashboard_type else "unknown"
    
    @property
    def title(self):
        """Use dashboard_type as title or extract from message_id data"""
        return self.dashboard_type
        
    @property
    def description(self):
        """Default description"""
        return "Dashboard"
    
    @property
    def layout_config(self):
        """Default empty config"""
        return {}
    
    @property
    def is_public(self):
        """Default public status"""
        return False
    
    @property
    def created_at(self):
        """Use updated_at for created_at"""
        return self.updated_at
    
    # This is a virtual relationship, as widgets would be stored in the message content
    @property
    def widgets(self):
        return []


class WidgetModel(Base):
    """Model to handle widget operations, but store in message content"""
    __tablename__ = "widget_references"
    
    # This table doesn't actually exist, it's just for the ORM interface
    # Set this to True to prevent SQLAlchemy from creating the table
    __abstract__ = True
    
    id = Column(String, primary_key=True)
    dashboard_id = Column(String, ForeignKey('dashboard_messages.id'))
    widget_type = Column(String)
    title = Column(String)
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=2)
    height = Column(Integer, default=2)
    config = Column(JSON, default={})
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    # Relationship
    dashboard = relationship("DashboardModel", foreign_keys=[dashboard_id])

# Additional web-specific methods can be added here if needed 