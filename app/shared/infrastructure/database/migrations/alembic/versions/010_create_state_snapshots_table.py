"""Create state_snapshots table

Revision ID: 010
Revises: 009
Create Date: 2025-04-27
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009' # Point to the previous migration (seeding definitions)
branch_labels = None
depends_on = None


def upgrade() -> None:
    print(f"Applying migration {revision}: Create state_snapshots table")
    op.create_table(
        'state_snapshots',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")), # Use server default for UUID if possible
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('trigger', sa.String(length=50), nullable=False, index=True),
        sa.Column('context', JSONB(), nullable=True),
        sa.Column('snapshot_data', JSONB(), nullable=False),
        # Optional FK (keep commented if User model/FK setup is separate/later)
        # sa.Column('owner_id', UUID(as_uuid=True), sa.ForeignKey('app_users.id', ondelete='SET NULL'), nullable=True)
    )
    # Example of creating an index explicitly if needed, though index=True does this
    # op.create_index(op.f('ix_state_snapshots_timestamp'), 'state_snapshots', ['timestamp'], unique=False)
    # op.create_index(op.f('ix_state_snapshots_trigger'), 'state_snapshots', ['trigger'], unique=False)
    print(f"Migration {revision} applied successfully.")


def downgrade() -> None:
    print(f"Reverting migration {revision}: Drop state_snapshots table")
    # Drop indexes explicitly if they were created explicitly or if index=True might not handle it on all backends
    # op.drop_index(op.f('ix_state_snapshots_trigger'), table_name='state_snapshots')
    # op.drop_index(op.f('ix_state_snapshots_timestamp'), table_name='state_snapshots')
    op.drop_table('state_snapshots')
    print(f"Migration {revision} reverted successfully.") 