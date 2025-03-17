"""
Migration script to seed the database with default categories from hardcoded constants.
This helps in migrating from the existing hardcoded approach to the new data-driven architecture.
"""

from app.bot.domain.categories.models.category_model import CategoryTemplate, CategoryPermissionLevel, CategoryPermission
from app.bot.infrastructure.repositories.category_repository_impl import CategoryRepositoryImpl
from app.shared.infrastructure.database.database_service import DatabaseService
from app.shared.interface.logging.api import get_db_logger

logger = get_db_logger()

# Assuming these are common Discord role IDs in your server
# Replace with actual role IDs from your server
EVERYONE_ROLE_ID = 0  # This should be the actual @everyone role ID
MEMBER_ROLE_ID = 0    # Member role ID
ADMIN_ROLE_ID = 0     # Admin role ID
OWNER_ROLE_ID = 0     # Owner role ID


# Define default category templates based on your existing structure
DEFAULT_CATEGORIES = [
    # Example: WELCOME category
    CategoryTemplate(
        name="WELCOME",
        position=0,
        permission_level=CategoryPermissionLevel.PUBLIC,
        permissions=[
            CategoryPermission(
                role_id=EVERYONE_ROLE_ID,
                view=True,
                send_messages=False
            ),
            CategoryPermission(
                role_id=ADMIN_ROLE_ID,
                view=True,
                send_messages=True,
                manage_messages=True,
                manage_channels=True,
                manage_category=True
            )
        ],
        metadata={
            "description": "Welcome and information channels",
            "icon": "👋"
        }
    ),
    
    # Example: COMMUNITY category
    CategoryTemplate(
        name="COMMUNITY",
        position=1,
        permission_level=CategoryPermissionLevel.MEMBER,
        permissions=[
            CategoryPermission(
                role_id=EVERYONE_ROLE_ID,
                view=False
            ),
            CategoryPermission(
                role_id=MEMBER_ROLE_ID,
                view=True,
                send_messages=True
            ),
            CategoryPermission(
                role_id=ADMIN_ROLE_ID,
                view=True,
                send_messages=True,
                manage_messages=True,
                manage_channels=True
            )
        ],
        metadata={
            "description": "Community discussion channels",
            "icon": "💬"
        }
    ),
    
    # Example: PROJECTS category
    CategoryTemplate(
        name="PROJECTS",
        position=2,
        permission_level=CategoryPermissionLevel.MEMBER,
        permissions=[
            CategoryPermission(
                role_id=MEMBER_ROLE_ID,
                view=True,
                send_messages=True
            )
        ],
        metadata={
            "description": "Project collaboration channels",
            "icon": "🛠️"
        }
    ),
    
    # Example: GAME SERVERS category
    CategoryTemplate(
        name="GAME SERVERS",
        position=3,
        permission_level=CategoryPermissionLevel.MEMBER,
        permissions=[
            CategoryPermission(
                role_id=MEMBER_ROLE_ID,
                view=True,
                send_messages=True
            )
        ],
        metadata={
            "description": "Game server information and management",
            "icon": "🎮"
        }
    ),
    
    # Example: ADMIN category
    CategoryTemplate(
        name="ADMIN",
        position=4,
        permission_level=CategoryPermissionLevel.ADMIN,
        permissions=[
            CategoryPermission(
                role_id=EVERYONE_ROLE_ID,
                view=False
            ),
            CategoryPermission(
                role_id=ADMIN_ROLE_ID,
                view=True,
                send_messages=True,
                manage_messages=True,
                manage_channels=True,
                manage_category=True
            )
        ],
        metadata={
            "description": "Administrative channels",
            "icon": "⚙️"
        }
    ),
]


def seed_categories():
    """Seed the database with default categories"""
    db_service = DatabaseService()
    category_repo = CategoryRepositoryImpl(db_service)
    
    # Create categories from templates
    for template in DEFAULT_CATEGORIES:
        # Check if category already exists
        existing = category_repo.get_category_by_name(template.name)
        if not existing:
            category = category_repo.create_from_template(template)
            logger.info(f"Created category: {template.name}")
        else:
            logger.info(f"Category already exists: {template.name}")

def check_and_seed_categories():
    """Check if categories exist and seed only if needed"""
    db_service = DatabaseService()
    category_repo = CategoryRepositoryImpl(db_service)
    
    # Check if we have any categories
    categories = category_repo.get_all_categories()
    
    if not categories:
        logger.info("No categories found in database, seeding default categories")
        seed_categories()
        logger.info("Default categories seeded successfully")
    else:
        logger.info(f"Found {len(categories)} existing categories, skipping category seeding")
        
if __name__ == "__main__":
    seed_categories() 