import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.shared.infrastructure.models import Base

class StateSnapshot(Base):
    """
    SQLAlchemy model for storing state monitor snapshots.
    """
    __tablename__ = 'state_snapshots'

    # Core Columns
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    trigger = Column(String(50), nullable=False, index=True) # e.g., 'user_capture', 'js_error', 'internal_api'
    
    # JSON Data Columns (using JSONB for PostgreSQL)
    context = Column(JSONB, nullable=True) # Optional context metadata 
    snapshot_data = Column(JSONB, nullable=False) # The actual snapshot JSON

    # Optional Relationships / Foreign Keys
    # Assuming you have a User model defined elsewhere (e.g., in models/auth/user.py)
    # owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True) 
    # owner = relationship("User") 

    # Representation for logging/debugging
    def __repr__(self):
        return f"<StateSnapshot(id={self.id}, timestamp='{self.timestamp}', trigger='{self.trigger}')>"
