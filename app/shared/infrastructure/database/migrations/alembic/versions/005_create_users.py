"""Seed initial users and roles

Revision ID: 005
Revises: 004
Create Date: 2024-03-20
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
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()
    
    # Insert roles
    for role in UserRole:
        connection.execute(
            text("""
                INSERT INTO roles (name, description)
                VALUES (CAST(:name AS VARCHAR), CAST(:description AS VARCHAR))
                ON CONFLICT (name) DO NOTHING
            """),
            {
                'name': role.value,
                'description': ROLE_DESCRIPTIONS[role.value]
            }
        )

    # Get owner from environment variable and set as owner
    owner_str = os.getenv('OWNER', '')
    if owner_str and '|' in owner_str:
        username, discord_id = owner_str.split('|')
        connection.execute(
            text("""
                INSERT INTO users (username, discord_id, role_id, is_active)
                SELECT 
                    CAST(:username AS VARCHAR),
                    CAST(:discord_id AS VARCHAR),
                    r.id,
                    TRUE
                FROM roles r
                WHERE r.name = CAST(:role_name AS VARCHAR)
                AND NOT EXISTS (
                    SELECT 1 FROM users u
                    WHERE u.discord_id = CAST(:discord_id AS VARCHAR)
                )
            """),
            {
                'username': username.strip(),
                'discord_id': discord_id.strip(),
                'role_name': UserRole.OWNER.value
            }
        )

def downgrade():
    """Remove seeded roles and users."""
    connection = op.get_bind()
    
    # Remove the owner user
    connection.execute(
        text("""
            DELETE FROM users 
            WHERE role_id IN (
                SELECT id FROM roles 
                WHERE name = :role_name::varchar
            )
        """),
        {'role_name': UserRole.OWNER.value}
    )
    
    # Remove all seeded roles using constants
    for role in UserRole:
        connection.execute(
            text("DELETE FROM roles WHERE name = :role_name::varchar"),
            {'role_name': role.value}
        )