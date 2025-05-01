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
from abc import ABC, abstractmethod
from typing import List, Optional
from app.shared.domain.models.channel_follow import ChannelFollow

class ChannelFollowRepository(ABC):
    """Repository interface for channel follows"""
    
    @abstractmethod
    async def create_follow(self, source_channel_id: str, target_channel_id: str, 
                           guild_id: str, webhook_id: str, webhook_token: str) -> ChannelFollow:
        """Create a new channel follow relationship"""
        pass
    
    @abstractmethod
    async def get_follow_by_id(self, follow_id: int) -> Optional[ChannelFollow]:
        """Get a follow relationship by ID"""
        pass
    
    @abstractmethod
    async def get_follow_by_channels(self, source_channel_id: str, 
                                    target_channel_id: str) -> Optional[ChannelFollow]:
        """Get a follow relationship by source and target channel IDs"""
        pass
    
    @abstractmethod
    async def get_follows_by_source(self, source_channel_id: str) -> List[ChannelFollow]:
        """Get all follows where the specified channel is the source"""
        pass
    
    @abstractmethod
    async def get_follows_by_target(self, target_channel_id: str) -> List[ChannelFollow]:
        """Get all follows where the specified channel is the target"""
        pass
    
    @abstractmethod
    async def get_follows_by_guild(self, guild_id: str) -> List[ChannelFollow]:
        """Get all follows in a specific guild"""
        pass
    
    @abstractmethod
    async def update_follow(self, follow: ChannelFollow) -> ChannelFollow:
        """Update an existing follow relationship"""
        pass
    
    @abstractmethod
    async def delete_follow(self, follow_id: int) -> bool:
        """Delete a follow relationship"""
        pass
    
    @abstractmethod
    async def deactivate_follow(self, follow_id: int) -> bool:
        """Deactivate a follow relationship (set is_active to False)"""
        pass
```

## Repository Implementation

### Infrastructure Layer

```python
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.domain.repositories.channel_follow_repository import ChannelFollowRepository
from app.shared.domain.models.channel_follow import ChannelFollow
from app.shared.infrastructure.models.channel_follow_entity import ChannelFollowEntity
from typing import List, Optional

class ChannelFollowRepositoryImpl(ChannelFollowRepository):
    """Implementation of channel follow repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _entity_to_model(self, entity: ChannelFollowEntity) -> ChannelFollow:
        """Convert database entity to domain model"""
        return ChannelFollow(
            id=entity.id,
            source_channel_id=entity.source_channel_id,
            target_channel_id=entity.target_channel_id,
            guild_id=entity.guild_id,
            webhook_id=entity.webhook_id,
            webhook_token=entity.webhook_token,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def _model_to_entity(self, model: ChannelFollow) -> ChannelFollowEntity:
        """Convert domain model to database entity"""
        return ChannelFollowEntity(
            id=model.id,
            source_channel_id=model.source_channel_id,
            target_channel_id=model.target_channel_id,
            guild_id=model.guild_id,
            webhook_id=model.webhook_id,
            webhook_token=model.webhook_token,
            is_active=model.is_active
        )
    
    async def create_follow(self, source_channel_id: str, target_channel_id: str, 
                           guild_id: str, webhook_id: str, webhook_token: str) -> ChannelFollow:
        """Create a new channel follow relationship"""
        entity = ChannelFollowEntity(
            source_channel_id=source_channel_id,
            target_channel_id=target_channel_id,
            guild_id=guild_id,
            webhook_id=webhook_id,
            webhook_token=webhook_token,
            is_active=True
        )
        self.session.add(entity)
        await self.session.flush()
        
        return self._entity_to_model(entity)
    
    async def get_follow_by_id(self, follow_id: int) -> Optional[ChannelFollow]:
        """Get a follow relationship by ID"""
        result = await self.session.execute(
            select(ChannelFollowEntity).where(ChannelFollowEntity.id == follow_id)
        )
        entity = result.scalar_one_or_none()
        return self._entity_to_model(entity) if entity else None
    
    async def get_follow_by_channels(self, source_channel_id: str, 
                                    target_channel_id: str) -> Optional[ChannelFollow]:
        """Get a follow relationship by source and target channel IDs"""
        result = await self.session.execute(
            select(ChannelFollowEntity).where(
                and_(
                    ChannelFollowEntity.source_channel_id == source_channel_id,
                    ChannelFollowEntity.target_channel_id == target_channel_id
                )
            )
        )
        entity = result.scalar_one_or_none()
        return self._entity_to_model(entity) if entity else None
    
    async def get_follows_by_source(self, source_channel_id: str) -> List[ChannelFollow]:
        """Get all follows where the specified channel is the source"""
        result = await self.session.execute(
            select(ChannelFollowEntity).where(
                ChannelFollowEntity.source_channel_id == source_channel_id
            )
        )
        entities = result.scalars().all()
        return [self._entity_to_model(entity) for entity in entities]
    
    async def get_follows_by_target(self, target_channel_id: str) -> List[ChannelFollow]:
        """Get all follows where the specified channel is the target"""
        result = await self.session.execute(
            select(ChannelFollowEntity).where(
                ChannelFollowEntity.target_channel_id == target_channel_id
            )
        )
        entities = result.scalars().all()
        return [self._entity_to_model(entity) for entity in entities]
    
    async def get_follows_by_guild(self, guild_id: str) -> List[ChannelFollow]:
        """Get all follows in a specific guild"""
        result = await self.session.execute(
            select(ChannelFollowEntity).where(
                ChannelFollowEntity.guild_id == guild_id
            )
        )
        entities = result.scalars().all()
        return [self._entity_to_model(entity) for entity in entities]
    
    async def update_follow(self, follow: ChannelFollow) -> ChannelFollow:
        """Update an existing follow relationship"""
        entity = self._model_to_entity(follow)
        self.session.add(entity)
        await self.session.flush()
        return follow
    
    async def delete_follow(self, follow_id: int) -> bool:
        """Delete a follow relationship"""
        entity = await self.session.get(ChannelFollowEntity, follow_id)
        if not entity:
            return False
        
        await self.session.delete(entity)
        return True
    
    async def deactivate_follow(self, follow_id: int) -> bool:
        """Deactivate a follow relationship (set is_active to False)"""
        entity = await self.session.get(ChannelFollowEntity, follow_id)
        if not entity:
            return False
        
        entity.is_active = False
        self.session.add(entity)
        return True
```

## Service Implementation

```python
from typing import List, Optional, Tuple
import nextcord
from app.shared.domain.repositories.channel_follow_repository import ChannelFollowRepository
from app.shared.domain.models.channel_follow import ChannelFollow
from app.shared.domain.services.channel_service import ChannelService
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class ChannelFollowService:
    """Service for managing channel follows"""
    
    def __init__(self, channel_follow_repo: ChannelFollowRepository, channel_service: ChannelService, bot):
        self.channel_follow_repo = channel_follow_repo
        self.channel_service = channel_service
        self.bot = bot
    
    async def follow_channel(self, source_channel_id: str, target_channel_id: str, guild_id: str) -> Tuple[bool, Optional[ChannelFollow], str]:
        """Create a follow relationship between two channels
        
        Args:
            source_channel_id: ID of the channel to follow (must be a news channel)
            target_channel_id: ID of the channel that will receive content
            guild_id: ID of the guild/server
            
        Returns:
            Tuple containing:
            - Success flag (bool)
            - Created follow object (ChannelFollow or None)
            - Error message if any (str)
        """
        try:
            # Check if follow already exists
            existing_follow = await self.channel_follow_repo.get_follow_by_channels(
                source_channel_id, target_channel_id
            )
            
            if existing_follow:
                return False, None, "This channel is already being followed by the target channel."
            
            # Get Discord channel objects
            source_channel = await self.bot.fetch_channel(int(source_channel_id))
            target_channel = await self.bot.fetch_channel(int(target_channel_id))
            
            # Validate channel types
            if not isinstance(source_channel, nextcord.TextChannel) or source_channel.type != nextcord.ChannelType.news:
                return False, None, "Source channel must be an announcement channel."
            
            if not isinstance(target_channel, nextcord.TextChannel):
                return False, None, "Target channel must be a text channel."
            
            # Create follow using Discord API
            try:
                follow_data = await source_channel.follow(destination=target_channel)
                
                # Save to database
                channel_follow = await self.channel_follow_repo.create_follow(
                    source_channel_id=source_channel_id,
                    target_channel_id=target_channel_id,
                    guild_id=guild_id,
                    webhook_id=str(follow_data.webhook.id) if follow_data.webhook else None,
                    webhook_token=follow_data.webhook.token if follow_data.webhook else None
                )
                
                logger.info(f"Channel {source_channel_id} is now followed by {target_channel_id}")
                return True, channel_follow, ""
                
            except nextcord.Forbidden:
                return False, None, "Bot does not have permission to create follows."
            except nextcord.HTTPException as e:
                return False, None, f"Discord API error: {str(e)}"
            
        except Exception as e:
            logger.error(f"Error following channel: {str(e)}")
            return False, None, f"Unexpected error: {str(e)}"
    
    async def unfollow_channel(self, source_channel_id: str, target_channel_id: str) -> Tuple[bool, str]:
        """Remove a follow relationship between two channels"""
        try:
            # Find the follow relationship
            follow = await self.channel_follow_repo.get_follow_by_channels(
                source_channel_id, target_channel_id
            )
            
            if not follow:
                return False, "Follow relationship not found."
            
            # We can't directly remove follows through Discord API,
            # but we can remove it from our database
            success = await self.channel_follow_repo.delete_follow(follow.id)
            
            if success:
                logger.info(f"Removed follow relationship: {source_channel_id} -> {target_channel_id}")
                return True, ""
            else:
                return False, "Failed to remove follow relationship."
            
        except Exception as e:
            logger.error(f"Error unfollowing channel: {str(e)}")
            return False, f"Unexpected error: {str(e)}"
    
    async def get_followed_channels(self, guild_id: str) -> List[ChannelFollow]:
        """Get all channel follow relationships in a guild"""
        return await self.channel_follow_repo.get_follows_by_guild(guild_id)
```

## Discord Bot Command Example

Here's an example of how to implement the `/follow` slash command:

```python
import nextcord
from nextcord import SlashOption, Interaction
from nextcord.ext import commands
from app.bot.core.workflows.base_workflow import BaseWorkflow
from app.shared.application.services.channel_follow_service import ChannelFollowService
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class ChannelFollowCommands(commands.Cog):
    """Commands for managing channel follows"""
    
    def __init__(self, bot):
        self.bot = bot
        self.channel_follow_service = None  # Will be injected
    
    @nextcord.slash_command(
        name="follow",
        description="Follow an announcement channel to receive its messages in this channel",
        default_member_permissions=nextcord.Permissions(manage_channels=True)
    )
    async def follow_command(
        self, 
        interaction: Interaction,
        source_channel: nextcord.TextChannel = SlashOption(
            name="channel",
            description="The announcement channel to follow",
            required=True
        )
    ):
        """Follow an announcement channel"""
        await interaction.response.defer(ephemeral=True)
        
        # Get the target channel from the interaction
        target_channel = interaction.channel
        guild_id = str(interaction.guild_id)
        
        # Call service to create follow
        success, follow, error_msg = await self.channel_follow_service.follow_channel(
            source_channel_id=str(source_channel.id),
            target_channel_id=str(target_channel.id),
            guild_id=guild_id
        )
        
        if success:
            await interaction.followup.send(
                f"✅ This channel is now following announcements from {source_channel.mention}.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ Failed to follow channel: {error_msg}",
                ephemeral=True
            )
    
    @nextcord.slash_command(
        name="unfollow",
        description="Stop following an announcement channel",
        default_member_permissions=nextcord.Permissions(manage_channels=True)
    )
    async def unfollow_command(
        self, 
        interaction: Interaction,
        source_channel: nextcord.TextChannel = SlashOption(
            name="channel",
            description="The announcement channel to unfollow",
            required=True
        )
    ):
        """Stop following an announcement channel"""
        await interaction.response.defer(ephemeral=True)
        
        # Get the target channel from the interaction
        target_channel = interaction.channel
        
        # Call service to remove follow
        success, error_msg = await self.channel_follow_service.unfollow_channel(
            source_channel_id=str(source_channel.id),
            target_channel_id=str(target_channel.id)
        )
        
        if success:
            await interaction.followup.send(
                f"✅ This channel has stopped following {source_channel.mention}.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ Failed to unfollow channel: {error_msg}",
                ephemeral=True
            )
    
    @nextcord.slash_command(
        name="follows",
        description="List all followed channels",
        default_member_permissions=nextcord.Permissions(manage_channels=True)
    )
    async def list_follows_command(self, interaction: Interaction):
        """List all followed channels"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = str(interaction.guild_id)
        follows = await self.channel_follow_service.get_followed_channels(guild_id)
        
        if not follows:
            await interaction.followup.send(
                "📝 No channels are being followed in this server.",
                ephemeral=True
            )
            return
        
        # Build embed with follow information
        embed = nextcord.Embed(
            title="Channel Follows",
            description="List of announcement channels being followed in this server.",
            color=nextcord.Color.blue()
        )
        
        for follow in follows:
            source_channel = self.bot.get_channel(int(follow.source_channel_id))
            target_channel = self.bot.get_channel(int(follow.target_channel_id))
            
            source_name = source_channel.mention if source_channel else f"Unknown ({follow.source_channel_id})"
            target_name = target_channel.mention if target_channel else f"Unknown ({follow.target_channel_id})"
            
            embed.add_field(
                name=f"Follow {follow.id}",
                value=f"Source: {source_name}\nTarget: {target_name}\nActive: {'Yes' if follow.is_active else 'No'}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(ChannelFollowCommands(bot))
```

## REST API Implementation

```python
from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List
from app.shared.application.services.channel_follow_service import ChannelFollowService
from app.shared.domain.models.channel_follow import ChannelFollow
from app.shared.infrastructure.api.dto.channel_follow_dto import (
    ChannelFollowCreateRequest, 
    ChannelFollowResponse,
    ChannelFollowListResponse
)
from app.shared.infrastructure.api.dependencies import get_channel_follow_service, get_current_user

router = APIRouter(prefix="/channel-follows", tags=["Channel Follows"])

@router.post("/", response_model=ChannelFollowResponse, status_code=status.HTTP_201_CREATED)
async def create_channel_follow(
    data: ChannelFollowCreateRequest = Body(...),
    channel_follow_service: ChannelFollowService = Depends(get_channel_follow_service),
    current_user = Depends(get_current_user)
):
    """Create a new channel follow relationship"""
    success, follow, error_msg = await channel_follow_service.follow_channel(
        source_channel_id=data.source_channel_id,
        target_channel_id=data.target_channel_id,
        guild_id=data.guild_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    return ChannelFollowResponse(
        id=follow.id,
        source_channel_id=follow.source_channel_id,
        target_channel_id=follow.target_channel_id,
        guild_id=follow.guild_id,
        is_active=follow.is_active,
        created_at=follow.created_at
    )

@router.get("/guild/{guild_id}", response_model=ChannelFollowListResponse)
async def get_follows_by_guild(
    guild_id: str,
    channel_follow_service: ChannelFollowService = Depends(get_channel_follow_service),
    current_user = Depends(get_current_user)
):
    """Get all channel follows in a guild"""
    follows = await channel_follow_service.get_followed_channels(guild_id)
    
    return ChannelFollowListResponse(
        follows=[
            ChannelFollowResponse(
                id=follow.id,
                source_channel_id=follow.source_channel_id,
                target_channel_id=follow.target_channel_id,
                guild_id=follow.guild_id,
                is_active=follow.is_active,
                created_at=follow.created_at
            ) for follow in follows
        ]
    )

@router.delete("/{follow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel_follow(
    follow_id: int,
    channel_follow_service: ChannelFollowService = Depends(get_channel_follow_service),
    current_user = Depends(get_current_user)
):
    """Delete a channel follow relationship"""
    follow = await channel_follow_service.get_follow_by_id(follow_id)
    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel follow not found"
        )
    
    success, error_msg = await channel_follow_service.unfollow_channel(
        source_channel_id=follow.source_channel_id,
        target_channel_id=follow.target_channel_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
```

## Integration with Dashboard Panels

To integrate channel follows with dashboard panels, implement methods that automatically create or update dashboard panels in follower channels:

```python
async def create_dashboard_with_follow(self, source_channel_id: str, dashboard_type: str, guild_id: str) -> Tuple[bool, str]:
    """Create a dashboard in a source channel and set up follows for all target channels
    
    Args:
        source_channel_id: The announcement channel to create the dashboard in
        dashboard_type: Type of dashboard to create
        guild_id: The guild/server ID
        
    Returns:
        Tuple with success flag and error message if any
    """
    try:
        # 1. Create dashboard in source channel
        dashboard = await self.dashboard_service.create_dashboard(
            channel_id=source_channel_id,
            dashboard_type=dashboard_type,
            guild_id=guild_id
        )
        
        if not dashboard:
            return False, "Failed to create dashboard in source channel"
        
        # 2. Find all channels following this source
        follows = await self.channel_follow_repo.get_follows_by_source(source_channel_id)
        
        # 3. Create matching dashboards in each follower
        for follow in follows:
            if follow.is_active:
                await self.dashboard_service.create_dashboard(
                    channel_id=follow.target_channel_id,
                    dashboard_type=dashboard_type,
                    guild_id=guild_id,
                    source_dashboard_id=dashboard.id  # Link to source
                )
        
        return True, ""
        
    except Exception as e:
        logger.error(f"Error creating dashboard with follows: {str(e)}")
        return False, f"Unexpected error: {str(e)}"
```

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