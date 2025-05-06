# Channel Follow Implementation Details

**(Related: [Structure Workflow Overview](./structure_workflow.md))**

This document outlines the implementation details for the Channel Follow feature in the FoundryCord bot, allowing announcement channels to be "followed" by other channels, effectively crossposting messages.

## Feature Overview & Purpose

Discord allows users to manually follow Announcement Channels, causing messages from the source to be published to a channel in their own server. This feature in FoundryCord aims to provide:
1.  Programmatic management of these follow relationships via bot commands or potentially a web UI.
2.  Local tracking of these relationships for auditing, display, or extended features.
3.  A consistent way to handle the underlying Discord webhook mechanism used for this feature.

## Database Schema

The `ChannelFollowEntity` stores the relationship between a source (announcement) channel and a target (follower) channel.

### `ChannelFollowEntity` (DDD Entity)

*   **Purpose:** Represents a single follow link from a `source_channel_id` to a `target_channel_id` within a specific `guild_id`.
*   **Key Attributes:**
    *   `webhook_id`, `webhook_token`: Stores the Discord-generated webhook credentials used to publish messages to the `target_channel_id`. These are crucial for the crossposting mechanism.
    *   `is_active`: Allows for soft deletion or temporary disabling of a follow.

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.shared.infrastructure.models import Base # Assuming Base is your declarative base

class ChannelFollowEntity(Base):
    """Entity for tracking channel following relationships"""
    __tablename__ = "channel_follows"
    
    id = Column(Integer, primary_key=True)
    source_channel_id = Column(String(50), nullable=False, index=True)  # Announcement channel ID being followed
    target_channel_id = Column(String(50), nullable=False, index=True)  # Channel ID receiving the content
    guild_id = Column(String(50), nullable=False, index=True)          # Guild ID where the target_channel_id resides
    webhook_id = Column(String(50), nullable=True)                     # Discord-generated webhook ID for the target channel
    webhook_token = Column(String(255), nullable=True)                 # Discord-generated webhook token (sensitive)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('source_channel_id', 'target_channel_id', name='uq_channel_follows_source_target'),)
    
    def __repr__(self):
        return f"<ChannelFollowEntity(id={self.id}, source={self.source_channel_id}, target={self.target_channel_id})>"
```

## Repository Layer

### `ChannelFollowRepository` Interface (Domain Layer - `app/shared/domain/repositories/channel_follow_repository.py` - Example)

```python
from abc import ABC, abstractmethod
from typing import List, Optional
# from app.shared.domain.entities import ChannelFollow # Assuming a domain entity distinct from ORM model if needed
from app.shared.infrastructure.models.discord.entities.channel_follow_entity import ChannelFollowEntity # Or directly use the ORM model as entity

class IChannelFollowRepository(ABC):

    @abstractmethod
    async def add_follow(self, follow_entity: ChannelFollowEntity) -> ChannelFollowEntity:
        pass

    @abstractmethod
    async def get_follow(self, source_channel_id: str, target_channel_id: str) -> Optional[ChannelFollowEntity]:
        pass

    @abstractmethod
    async def list_follows_by_source(self, source_channel_id: str) -> List[ChannelFollowEntity]:
        pass

    @abstractmethod
    async def list_follows_by_target(self, target_channel_id: str) -> List[ChannelFollowEntity]:
        pass

    @abstractmethod
    async def remove_follow(self, source_channel_id: str, target_channel_id: str) -> bool:
        pass

    @abstractmethod
    async def update_webhook_details(self, follow_id: int, webhook_id: str, webhook_token: str) -> Optional[ChannelFollowEntity]:
        pass
```

### Implementation (Infrastructure Layer - `app/shared/infrastructure/repositories/discord/channel_follow_repository_impl.py` - Conceptual)
*   Implements `IChannelFollowRepository` using SQLAlchemy.
*   Handles database session management for CRUD operations on `ChannelFollowEntity`.

## Service Layer (`app/bot/application/services/channel/channel_follow_service.py` - Example)

### `ChannelFollowService` (Application Service)
*   **Responsibilities:**
    *   Orchestrating the creation and deletion of channel follow relationships.
    *   Validating inputs (e.g., checking if source channel is an announcement channel, if target channel exists and bot has permissions).
    *   Interacting with the Discord API to:
        *   Verify channel types.
        *   Create a webhook in the target channel when a follow is initiated by Discord's API (`POST /channels/{channel.id}/followers`). Discord handles webhook creation itself for this specific API.
        *   Or, if managing webhooks manually (not standard for this Discord feature, but if custom implementation): create a webhook in the target channel, then subscribe the source channel to it (less likely for direct "follow" feature).
        *   Delete the corresponding Discord webhook or unfollow when a relationship is removed.
    *   Persisting `ChannelFollowEntity` records via `ChannelFollowRepository` (including webhook details if obtained).
*   **Collaborators:**
    *   `IChannelFollowRepository`
    *   `DiscordQueryService` (or similar Discord API interaction service from `app/bot/`)
    *   Potentially `GuildConfigRepository` or `GuildRepository` (to check bot permissions or guild features).

**Sequence Diagram: Setting up a Channel Follow (Bot Command)**

```mermaid
sequenceDiagram
    participant User
    participant BotCmd as Bot Slash Command (`/follow add`)
    participant FollowService as ChannelFollowService
    participant DiscordService as DiscordInteractionService
    participant DiscordAPI as Discord API
    participant FollowRepo as ChannelFollowRepository
    participant Database

    User->>+BotCmd: /follow add source_channel_id target_channel_id
    BotCmd->>+FollowService: setup_follow(guild_id, source_id, target_id)
    FollowService->>+DiscordService: get_channel_details(source_id)
    DiscordService-->>-FollowService: source_channel_info (is_announcement?)
    alt Source is not Announcement Channel
        FollowService-->>BotCmd: Error: Source must be Announcement
        BotCmd-->>-User: Error Message
    end
    FollowService->>+DiscordService: get_channel_details(target_id)
    DiscordService-->>-FollowService: target_channel_info (exists? bot_permissions?)
    alt Target invalid or no permission
        FollowService-->>BotCmd: Error: Target invalid or permissions lacking
        BotCmd-->>-User: Error Message
    end

    FollowService->>+FollowRepo: get_follow(source_id, target_id)
    FollowRepo-->>-FollowService: existing_follow (or None)
    alt Follow already exists
        FollowService-->>BotCmd: Error: Already following
        BotCmd-->>-User: Error Message
    end

    Note over FollowService, DiscordAPI: Discord's `POST /channels/{source_channel_id}/followers` with `webhook_channel_id: target_channel_id` handles webhook creation internally.
    FollowService->>+DiscordService: follow_discord_channel(source_id, target_id)
    DiscordService->>+DiscordAPI: POST /channels/{source_id}/followers (payload: {webhook_channel_id: target_id})
    DiscordAPI-->>-DiscordService: Success (implicitly webhook created by Discord)
    DiscordService-->>-FollowService: Success (webhook details might not be directly returned here by Discord)
    
    FollowService->>+FollowRepo: add_follow(guild_id, source_id, target_id, webhook_id_placeholder, webhook_token_placeholder) 
    Note over FollowService: Webhook ID/Token might be populated later if discoverable, or left null if Discord manages it opaquely via this API.
    FollowRepo->>+Database: INSERT INTO channel_follows
    Database-->>-FollowRepo: New FollowEntity
    FollowRepo-->>-FollowService: New FollowEntity
    FollowService-->>BotCmd: Success
    BotCmd-->>-User: Success Message
```

## Discord Bot Command Example (`app/bot/interfaces/commands/.../follow_commands.py` - Conceptual)

```python
# Conceptual example
# Assuming nextcord and services are set up

class FollowCommands(commands.Cog):
    def __init__(self, bot, channel_follow_service: ChannelFollowService):
        self.bot = bot
        self.channel_follow_service = channel_follow_service

    @nextcord.slash_command(name="follow", description="Manage channel follows.")
    async def follow_group(self, interaction: nextcord.Interaction):
        pass # Parent command

    @follow_group.subcommand(name="add", description="Follow an announcement channel.")
    async def add_follow_cmd(
        self, 
        interaction: nextcord.Interaction, 
        source_channel: nextcord.abc.GuildChannel, # Use appropriate type hint for announcement channel
        target_channel: nextcord.TextChannel
    ):
        await interaction.response.defer(ephemeral=True)
        try:
            if source_channel.type != nextcord.ChannelType.news:
                await interaction.followup.send("Error: Source channel must be an Announcement channel.")
                return

            # Further permission checks for bot in target_channel might be needed here or in service
            
            result_entity = await self.channel_follow_service.setup_follow(
                guild_id=str(interaction.guild_id),
                source_channel_id=str(source_channel.id),
                target_channel_id=str(target_channel.id)
            )
            await interaction.followup.send(f"Successfully started following {source_channel.mention} in {target_channel.mention}.")
        except Exception as e:
            # Log error e
            await interaction.followup.send(f"An error occurred: {e}")

    # ... other subcommands like remove, list ...
```

## REST API Implementation (If Applicable)

*   If channel following management is exposed via the Web UI, REST API endpoints would be needed.
*   **Endpoints (Conceptual):**
    *   `POST /api/v1/guilds/{guild_id}/channel-follows`: Create a follow.
        *   Request Body: `{ "source_channel_id": "...", "target_channel_id": "..." }`
    *   `DELETE /api/v1/guilds/{guild_id}/channel-follows`: Delete a follow (using query params or body for source/target).
    *   `GET /api/v1/guilds/{guild_id}/channel-follows?source_channel_id=...`: List follows for a source.
*   **Controllers:** Would use `ChannelFollowService` similarly to bot commands.
*   **Authentication/Authorization:** Standard API auth (session cookies) and relevant permissions (e.g., guild admin).

## Integration with Dashboard Panels

*   **Display:** A dashboard panel could list active channel follows for a guild or for a specific announcement channel.
*   **Management:** Buttons on a dashboard panel could trigger bot commands or API calls to add/remove follows.
*   **Data Source:** The `ChannelFollowRepository` would be the source of data for such panels.

## Migration Script (Alembic)

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