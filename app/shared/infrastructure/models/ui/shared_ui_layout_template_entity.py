from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.shared.infrastructure.models.base import Base # More explicit import
from app.shared.infrastructure.models.auth import AppUserEntity 

class SharedUILayoutTemplateEntity(Base):
    """
    SQLAlchemy model representing a shared UI layout template.
    These templates are typically created by users to be shared across guilds or users.
    """
    __tablename__ = 'shared_ui_layout_templates'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    layout_data = Column(JSON, nullable=False) # Stores the Gridstack layout structure, lock state, etc.

    creator_user_id = Column(Integer, ForeignKey('app_users.id', name='fk_shared_ui_layouts_user_id', ondelete='SET NULL'), nullable=True) # Link to the user who created/shared it

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional: Define relationship back to the user if needed elsewhere
    # created_by = relationship("AppUserEntity")

    def __repr__(self):
        return f"<SharedUILayoutTemplateEntity(id={self.id}, name='{self.name}')>"
