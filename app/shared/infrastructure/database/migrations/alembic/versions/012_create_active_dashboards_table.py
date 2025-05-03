"""Create active_dashboards table to track running instances

Revision ID: 012
Revises: 011
Create Date: <will be auto-filled by alembic> # Placeholder
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, BIGINT # Use BIGINT for message_id


# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011' # Point to the previous migration (seeding dashboard templates)
branch_labels = None
depends_on = None


def upgrade() -> None:
    print(f"Applying migration {revision}: Create active_dashboards table")
    op.create_table(
        'active_dashboards',
        sa.Column('id', sa.Integer(), primary_key=True),
        # Rename column and update Foreign Key to point to the renamed configurations table
        sa.Column('dashboard_configuration_id', sa.Integer(), sa.ForeignKey('dashboard_configurations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('guild_id', sa.String(length=30), nullable=False, index=True), # Increased length just in case
        sa.Column('channel_id', sa.String(length=30), nullable=False, index=True), # Increased length
        sa.Column('message_id', BIGINT(), nullable=True, index=True), # Discord Message ID (can be nullable if created before message exists)
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', index=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('error_state', sa.Boolean(), nullable=False, server_default='false', index=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('config_override', JSONB(), nullable=True, comment="Optional JSON to override specific parts of the template config for this instance"),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        # Optional: Update unique constraint name if uncommented later
        # sa.UniqueConstraint('dashboard_configuration_id', 'channel_id', name='uq_active_dashboard_channel')
    )
    # Add specific indexes if needed (index=True already does this for single columns)
    # op.create_index(op.f('ix_active_dashboards_guild_channel'), 'active_dashboards', ['guild_id', 'channel_id'], unique=False)

    print(f"Migration {revision} applied successfully.")


def downgrade() -> None:
    print(f"Reverting migration {revision}: Drop active_dashboards table")
    # Drop indexes explicitly before dropping the table if created explicitly
    # op.drop_index(op.f('ix_active_dashboards_guild_channel'), table_name='active_dashboards')
    op.drop_table('active_dashboards')
    print(f"Migration {revision} reverted successfully.") 