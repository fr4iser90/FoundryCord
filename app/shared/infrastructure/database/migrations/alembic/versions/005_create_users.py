"""Seed initial users migration

Revision ID: 005
Revises: 004
Create Date: 2024-03-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import os

# revision identifiers
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    # Get super admins from env and seed them
    super_admins_str = os.getenv('SUPER_ADMINS', '')
    if super_admins_str:
        for admin in super_admins_str.split(','):
            if '|' in admin:
                username, discord_id = admin.split('|')
                op.execute(
                    """
                    INSERT INTO users (username, discord_id, is_admin, is_active)
                    VALUES (:username, :discord_id, TRUE, TRUE)
                    """,
                    {
                        'username': username.strip(),
                        'discord_id': discord_id.strip()
                    }
                )

def downgrade():
    op.execute("DELETE FROM users WHERE is_admin = TRUE")
