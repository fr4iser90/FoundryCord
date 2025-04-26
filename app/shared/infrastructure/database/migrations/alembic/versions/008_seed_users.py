"""Seed initial app_users and app_roles

Revision ID: 008
Revises: 007
Create Date: 2025-04-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import os
from app.shared.infrastructure.constants.user_constants import (
    UserRole,
    ROLE_DESCRIPTIONS
)

# revision identifiers
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()
    
    # Insert app_roles with permissions
    for role in UserRole:
        connection.execute(
            text("""
                INSERT INTO app_roles (name, description, permissions)
                VALUES (CAST(:name AS VARCHAR), CAST(:description AS VARCHAR), CAST(:permissions AS VARCHAR))
                ON CONFLICT (name) DO NOTHING
            """),
            {
                'name': role.value,
                'description': ROLE_DESCRIPTIONS[role.value],
                'permissions': 'default'  # You might want to adjust this based on your permission system
            }
        )

    # Get owner from environment variable and set as owner
    owner_str = os.getenv('OWNER', '')
    if owner_str and '|' in owner_str:
        username, discord_id = owner_str.split('|')
        connection.execute(
            text("""
                INSERT INTO app_users (username, discord_id, is_owner, is_active)
                VALUES (
                    CAST(:username AS VARCHAR),
                    CAST(:discord_id AS VARCHAR),
                    TRUE,
                    TRUE
                )
                ON CONFLICT (discord_id) DO UPDATE 
                SET is_owner = TRUE
            """),
            {
                'username': username.strip(),
                'discord_id': discord_id.strip()
            }
        )

def downgrade():
    """Remove seeded app_roles and app_users."""
    connection = op.get_bind()
    
    # Remove the owner user
    connection.execute(
        text("""
            DELETE FROM app_users 
            WHERE is_owner = TRUE
        """)
    )
    
    # Remove all seeded app_roles using constants
    for role in UserRole:
        connection.execute(
            text("DELETE FROM app_roles WHERE name = :role_name::varchar"),
            {'role_name': role.value}
        )