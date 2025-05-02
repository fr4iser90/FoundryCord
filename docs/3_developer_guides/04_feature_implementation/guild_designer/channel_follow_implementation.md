# Channel Follow Implementation

**(Related: [Structure Workflow Overview](./structure_workflow.md), [Structure Workflow TODO](./structure_workflow_todo.md))**

This document outlines the implementation details for the Channel Follow feature in the FoundryCord bot.

## Database Schema

### ChannelFollowEntity

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.shared.infrastructure.models import Base

class ChannelFollowEntity(Base):
    """Entity for tracking channel following relationships"""
    __tablename__ = "channel_follows"
    
    id = Column(Integer, primary_key=True)
    source_channel_id = Column(String(50), nullable=False, index=True)  # Channel being followed (announcement channel)
    target_channel_id = Column(String(50), nullable=False, index=True)  # Channel receiving content
    guild_id = Column(String(50), nullable=False, index=True)  # Server ID
    webhook_id = Column(String(50), nullable=True)  # Discord-generated webhook ID
    webhook_token = Column(String(255), nullable=True)  # Discord-generated webhook token (sensitive)
    is_active = Column(Boolean, default=True)  # Whether the follow is active
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ChannelFollowEntity(id={self.id}, source={self.source_channel_id}, target={self.target_channel_id})>"
```

## Repository Interface

### Domain Layer

```python

```

## Repository Implementation

### Infrastructure Layer


## Service Implementation



## Discord Bot Command Example

Here's an example of how to implement the `/follow` slash command:



## REST API Implementation



## Integration with Dashboard Panels

To integrate channel follows with dashboard panels, implement methods that automatically create or update dashboard panels in follower channels:



## Migration Script

```python
"""Migration script for adding channel follows table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20240729001122'
down_revision = '20240729001121'
branch_labels = None
depends_on = None

def upgrade():
    # Create channel_follows table
    op.create_table(
        'channel_follows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_channel_id', sa.String(length=50), nullable=False),
        sa.Column('target_channel_id', sa.String(length=50), nullable=False),
        sa.Column('guild_id', sa.String(length=50), nullable=False),
        sa.Column('webhook_id', sa.String(length=50), nullable=True),
        sa.Column('webhook_token', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index('ix_channel_follows_source_channel_id', 'channel_follows', ['source_channel_id'])
    op.create_index('ix_channel_follows_target_channel_id', 'channel_follows', ['target_channel_id'])
    op.create_index('ix_channel_follows_guild_id', 'channel_follows', ['guild_id'])
    
    # Add unique constraint to prevent duplicate follows
    op.create_unique_constraint('uq_channel_follows_source_target', 'channel_follows', ['source_channel_id', 'target_channel_id'])

def downgrade():
    # Drop the table
    op.drop_table('channel_follows')
``` 