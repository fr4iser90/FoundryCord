"""
Migration script to seed the database with default channels from hardcoded constants.
This helps in migrating from the existing hardcoded approach to the new data-driven architecture.
"""

from app.bot.domain.channels.models.channel_model import (
    ChannelTemplate, ChannelType, ChannelPermissionLevel, 
    ChannelPermission, ThreadConfig
)
from app.bot.infrastructure.repositories.channel_repository_impl import ChannelRepositoryImpl
from app.bot.domain.categories.repositories.category_repository import CategoryRepository
from app.bot.infrastructure.repositories.category_repository_impl import CategoryRepositoryImpl
from app.shared.infrastructure.database.service import DatabaseService
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

# Assuming these are common Discord role IDs in your server
# Replace with actual role IDs from your server
EVERYONE_ROLE_ID = 0  # This should be the actual @everyone role ID
MEMBER_ROLE_ID = 0    # Member role ID
ADMIN_ROLE_ID = 0     # Admin role ID
OWNER_ROLE_ID = 0     # Owner role ID


# Define default channel templates based on your existing structure
DEFAULT_CHANNELS = [
    # WELCOME category channels
    ChannelTemplate(
        name="welcome",
        description="Welcome to our server!",
        category_name="WELCOME",
        type=ChannelType.TEXT,
        position=0,
        permission_level=ChannelPermissionLevel.PUBLIC,
        permissions=[
            ChannelPermission(
                role_id=EVERYONE_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=False
            ),
            ChannelPermission(
                role_id=ADMIN_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                manage_channel=True
            )
        ],
        topic="Welcome to our Homelab Discord server!",
        metadata={
            "description": "Server welcome channel",
            "icon": "👋",
            "is_welcome": True
        }
    ),
    
    ChannelTemplate(
        name="rules",
        description="Server rules and guidelines",
        category_name="WELCOME",
        type=ChannelType.TEXT,
        position=1,
        permission_level=ChannelPermissionLevel.PUBLIC,
        permissions=[
            ChannelPermission(
                role_id=EVERYONE_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=False
            ),
            ChannelPermission(
                role_id=ADMIN_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                manage_channel=True
            )
        ],
        topic="Please read and follow our server rules",
        metadata={
            "description": "Server rules channel",
            "icon": "📜"
        }
    ),
    
    ChannelTemplate(
        name="announcements",
        description="Server announcements",
        category_name="WELCOME",
        type=ChannelType.ANNOUNCEMENT,
        position=2,
        permission_level=ChannelPermissionLevel.PUBLIC,
        permissions=[
            ChannelPermission(
                role_id=EVERYONE_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=False
            ),
            ChannelPermission(
                role_id=ADMIN_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                manage_channel=True
            )
        ],
        topic="Important server announcements",
        metadata={
            "description": "Server announcements channel",
            "icon": "📢"
        }
    ),
    
    # COMMUNITY category channels
    ChannelTemplate(
        name="general",
        description="General discussion",
        category_name="COMMUNITY",
        type=ChannelType.TEXT,
        position=0,
        permission_level=ChannelPermissionLevel.MEMBER,
        permissions=[
            ChannelPermission(
                role_id=MEMBER_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                add_reactions=True,
                embed_links=True,
                attach_files=True
            )
        ],
        topic="General discussion for all topics",
        metadata={
            "description": "General chat channel",
            "icon": "💬"
        }
    ),
    
    ChannelTemplate(
        name="help",
        description="Get help with your Homelab",
        category_name="COMMUNITY",
        type=ChannelType.TEXT,
        position=1,
        permission_level=ChannelPermissionLevel.MEMBER,
        permissions=[
            ChannelPermission(
                role_id=MEMBER_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                add_reactions=True,
                embed_links=True,
                attach_files=True
            )
        ],
        topic="Ask for help with your Homelab projects",
        metadata={
            "description": "Help channel",
            "icon": "❓"
        }
    ),
    
    ChannelTemplate(
        name="showcase",
        description="Show off your Homelab",
        category_name="COMMUNITY",
        type=ChannelType.TEXT,
        position=2,
        permission_level=ChannelPermissionLevel.MEMBER,
        permissions=[
            ChannelPermission(
                role_id=MEMBER_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                add_reactions=True,
                embed_links=True,
                attach_files=True
            )
        ],
        topic="Show off your Homelab setup and projects",
        metadata={
            "description": "Homelab showcase channel",
            "icon": "🖼️"
        }
    ),
    
    # PROJECTS category channels
    ChannelTemplate(
        name="projects-discussion",
        description="Discuss ongoing projects",
        category_name="PROJECTS",
        type=ChannelType.TEXT,
        position=0,
        permission_level=ChannelPermissionLevel.MEMBER,
        permissions=[
            ChannelPermission(
                role_id=MEMBER_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                add_reactions=True,
                embed_links=True,
                attach_files=True
            )
        ],
        topic="Discuss ongoing Homelab projects",
        metadata={
            "description": "Project discussion channel",
            "icon": "🛠️"
        }
    ),
    
    ChannelTemplate(
        name="project-ideas",
        description="Share and discuss project ideas",
        category_name="PROJECTS",
        type=ChannelType.FORUM,
        position=1,
        permission_level=ChannelPermissionLevel.MEMBER,
        permissions=[
            ChannelPermission(
                role_id=MEMBER_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                add_reactions=True,
                embed_links=True,
                attach_files=True
            )
        ],
        topic="Share and discuss project ideas",
        thread_config=ThreadConfig(
            default_auto_archive_duration=10080,  # 7 days
            default_thread_slowmode_delay=0,
            require_tag=True,
            available_tags=[
                {"name": "Hardware", "emoji": "🔌"},
                {"name": "Software", "emoji": "💻"},
                {"name": "Network", "emoji": "🌐"},
                {"name": "Storage", "emoji": "💾"},
                {"name": "Automation", "emoji": "🤖"}
            ]
        ),
        metadata={
            "description": "Project ideas forum",
            "icon": "💡"
        }
    ),
    
    # GAME SERVERS category channels
    ChannelTemplate(
        name="minecraft",
        description="Minecraft server discussion",
        category_name="GAME SERVERS",
        type=ChannelType.TEXT,
        position=0,
        permission_level=ChannelPermissionLevel.MEMBER,
        permissions=[
            ChannelPermission(
                role_id=MEMBER_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                add_reactions=True,
                embed_links=True,
                attach_files=True
            )
        ],
        topic="Minecraft server discussion and updates",
        metadata={
            "description": "Minecraft server channel",
            "icon": "⛏️",
            "game_type": "minecraft"
        }
    ),
    
    ChannelTemplate(
        name="game-server-requests",
        description="Request new game servers",
        category_name="GAME SERVERS",
        type=ChannelType.TEXT,
        position=1,
        permission_level=ChannelPermissionLevel.MEMBER,
        permissions=[
            ChannelPermission(
                role_id=MEMBER_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                add_reactions=True,
                embed_links=True,
                attach_files=True
            ),
            ChannelPermission(
                role_id=ADMIN_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                manage_channel=True
            )
        ],
        topic="Request new game servers to be added",
        metadata={
            "description": "Game server requests",
            "icon": "🎮"
        }
    ),
    
    # ADMIN category channels
    ChannelTemplate(
        name="admin-chat",
        description="Admin discussion",
        category_name="ADMIN",
        type=ChannelType.TEXT,
        position=0,
        permission_level=ChannelPermissionLevel.ADMIN,
        permissions=[
            ChannelPermission(
                role_id=EVERYONE_ROLE_ID,
                view=False
            ),
            ChannelPermission(
                role_id=ADMIN_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                manage_channel=True,
                embed_links=True,
                attach_files=True,
                add_reactions=True
            )
        ],
        topic="Admin discussion channel",
        metadata={
            "description": "Admin chat channel",
            "icon": "⚙️"
        }
    ),
    
    ChannelTemplate(
        name="bot-commands",
        description="Bot commands channel",
        category_name="ADMIN",
        type=ChannelType.TEXT,
        position=1,
        permission_level=ChannelPermissionLevel.ADMIN,
        permissions=[
            ChannelPermission(
                role_id=EVERYONE_ROLE_ID,
                view=False
            ),
            ChannelPermission(
                role_id=ADMIN_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                use_bots=True
            )
        ],
        topic="Channel for bot commands",
        metadata={
            "description": "Bot commands channel",
            "icon": "🤖"
        }
    ),
    
    ChannelTemplate(
        name="server-logs",
        description="Server logs channel",
        category_name="ADMIN",
        type=ChannelType.TEXT,
        position=2,
        permission_level=ChannelPermissionLevel.ADMIN,
        permissions=[
            ChannelPermission(
                role_id=EVERYONE_ROLE_ID,
                view=False
            ),
            ChannelPermission(
                role_id=ADMIN_ROLE_ID,
                view=True,
                read_messages=True,
                send_messages=False
            )
        ],
        topic="Server logs and events",
        metadata={
            "description": "Server logs channel",
            "icon": "📋",
            "is_log_channel": True
        }
    ),
]


def seed_channels():
    """Seed the database with default channels"""
    db_service = DatabaseService()
    channel_repo = ChannelRepositoryImpl(db_service)
    category_repo = CategoryRepositoryImpl(db_service)
    
    # Create channels from templates
    for template in DEFAULT_CHANNELS:
        # Find category
        category = category_repo.get_category_by_name(template.category_name)
        if not category:
            logger.warning(f"Category not found: {template.category_name} for channel {template.name}")
            continue
        
        # Check if channel already exists in this category
        existing = channel_repo.get_channel_by_name_and_category(template.name, category.id)
        if not existing:
            channel = channel_repo.create_from_template(template, category_id=category.id)
            logger.info(f"Created channel: {template.name} in category {template.category_name}")
        else:
            logger.info(f"Channel already exists: {template.name} in category {template.category_name}")

def check_and_seed_channels():
    """Check if channels exist and seed only if needed"""
    db_service = DatabaseService()
    channel_repo = ChannelRepositoryImpl(db_service)
    
    # Check if we have any channels
    channels = channel_repo.get_all_channels()
    
    if not channels:
        logger.info("No channels found in database, seeding default channels")
        seed_channels()
        logger.info("Default channels seeded successfully")
    else:
        logger.info(f"Found {len(channels)} existing channels, skipping channel seeding")

if __name__ == "__main__":
    seed_channels() 