import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models.base import Base # More explicit import
# Correct import path and entity name for the User
from app.shared.infrastructure.models.auth import AppUserEntity 

class UILayoutEntity(Base):
    """
    Database entity for storing user-specific UI layouts.
    """
    __tablename__ = 'ui_layouts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('app_users.id'), nullable=False)
    page_identifier = Column(String, nullable=False, index=True) # e.g., 'guild_designer_12345', 'home_dashboard'
    layout_data = Column(JSON, nullable=False) # Stores the Gridstack layout structure
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Correct relationship target class name
    user = relationship("AppUserEntity")

    # Ensure a user can only have one layout per page identifier
    __table_args__ = (UniqueConstraint('user_id', 'page_identifier', name='_user_page_layout_uc'),)

    def __repr__(self):
        return f"<UILayoutEntity(id={self.id}, user_id={self.user_id}, page='{self.page_identifier}')>"
