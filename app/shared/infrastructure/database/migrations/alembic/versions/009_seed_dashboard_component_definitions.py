"""Seed dashboard component definitions

Revision ID: 009
Revises: 008
Create Date: 2025-04-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
import json # Import json library

# revision identifiers, used by Alembic. Adjust if needed.
revision = '009' # <-- Stelle sicher, dass das die ID ist, die Alembic generiert hat
down_revision = '008' # <-- Muss auf die vorherige Migration zeigen
branch_labels = None
depends_on = None

# Import all the seed dictionaries
# Adjust paths if your structure is different
try:
    from app.shared.infrastructure.database.seeds.dashboard_instances.common.buttons import DEFAULT_BUTTONS as COMMON_BUTTONS
    from app.shared.infrastructure.database.seeds.dashboard_instances.common.embeds import DEFAULT_EMBEDS as COMMON_EMBEDS
    from app.shared.infrastructure.database.seeds.dashboard_instances.common.messages import DEFAULT_MESSAGES as COMMON_MESSAGES
    from app.shared.infrastructure.database.seeds.dashboard_instances.common.modals import DEFAULT_MODALS as COMMON_MODALS
    from app.shared.infrastructure.database.seeds.dashboard_instances.common.selectors import DEFAULT_SELECTORS as COMMON_SELECTORS
    from app.shared.infrastructure.database.seeds.dashboard_instances.common.views import DEFAULT_VIEWS as COMMON_VIEWS
except ImportError as e:
    print(f"Could not import common seeds: {e}")
    COMMON_BUTTONS, COMMON_EMBEDS, COMMON_MESSAGES, COMMON_MODALS, COMMON_SELECTORS, COMMON_VIEWS = {}, {}, {}, {}, {}, {}

try:
    from app.shared.infrastructure.database.seeds.dashboard_instances.gamehub.buttons import GAMEHUB_BUTTONS
    from app.shared.infrastructure.database.seeds.dashboard_instances.gamehub.embeds import GAMEHUB_EMBEDS
    from app.shared.infrastructure.database.seeds.dashboard_instances.gamehub.messages import GAMEHUB_MESSAGES
    from app.shared.infrastructure.database.seeds.dashboard_instances.gamehub.modals import GAMEHUB_MODALS
    from app.shared.infrastructure.database.seeds.dashboard_instances.gamehub.selectors import GAMEHUB_SELECTORS
    from app.shared.infrastructure.database.seeds.dashboard_instances.gamehub.views import GAMEHUB_VIEWS
except ImportError as e:
    print(f"Could not import gamehub seeds: {e}")
    GAMEHUB_BUTTONS, GAMEHUB_EMBEDS, GAMEHUB_MESSAGES, GAMEHUB_MODALS, GAMEHUB_SELECTORS, GAMEHUB_VIEWS = {}, {}, {}, {}, {}, {}

try:
    from app.shared.infrastructure.database.seeds.dashboard_instances.monitoring.buttons import MONITORING_BUTTONS
    from app.shared.infrastructure.database.seeds.dashboard_instances.monitoring.embeds import MONITORING_EMBEDS
    from app.shared.infrastructure.database.seeds.dashboard_instances.monitoring.messages import MONITORING_MESSAGES
    from app.shared.infrastructure.database.seeds.dashboard_instances.monitoring.modals import MONITORING_MODALS
    from app.shared.infrastructure.database.seeds.dashboard_instances.monitoring.selectors import MONITORING_SELECTORS
    from app.shared.infrastructure.database.seeds.dashboard_instances.monitoring.views import MONITORING_VIEWS
except ImportError as e:
    print(f"Could not import monitoring seeds: {e}")
    MONITORING_BUTTONS, MONITORING_EMBEDS, MONITORING_MESSAGES, MONITORING_MODALS, MONITORING_SELECTORS, MONITORING_VIEWS = {}, {}, {}, {}, {}, {}

try:
    from app.shared.infrastructure.database.seeds.dashboard_instances.project.buttons import PROJECT_BUTTONS
    from app.shared.infrastructure.database.seeds.dashboard_instances.project.embeds import PROJECT_EMBEDS
    from app.shared.infrastructure.database.seeds.dashboard_instances.project.messages import PROJECT_MESSAGES
    from app.shared.infrastructure.database.seeds.dashboard_instances.project.modals import PROJECT_MODALS
    from app.shared.infrastructure.database.seeds.dashboard_instances.project.selectors import PROJECT_SELECTORS
    from app.shared.infrastructure.database.seeds.dashboard_instances.project.views import PROJECT_VIEWS
except ImportError as e:
    print(f"Could not import project seeds: {e}")
    PROJECT_BUTTONS, PROJECT_EMBEDS, PROJECT_MESSAGES, PROJECT_MODALS, PROJECT_SELECTORS, PROJECT_VIEWS = {}, {}, {}, {}, {}, {}

try:
    from app.shared.infrastructure.database.seeds.dashboard_instances.welcome.buttons import WELCOME_BUTTONS
    from app.shared.infrastructure.database.seeds.dashboard_instances.welcome.embeds import WELCOME_EMBEDS
    from app.shared.infrastructure.database.seeds.dashboard_instances.welcome.messages import WELCOME_MESSAGES # Check if exists
    from app.shared.infrastructure.database.seeds.dashboard_instances.welcome.modals import WELCOME_MODALS
    from app.shared.infrastructure.database.seeds.dashboard_instances.welcome.selectors import WELCOME_SELECTORS
    from app.shared.infrastructure.database.seeds.dashboard_instances.welcome.views import WELCOME_VIEWS
except ImportError as e:
    print(f"Could not import welcome seeds: {e}")
    WELCOME_BUTTONS, WELCOME_EMBEDS, WELCOME_MESSAGES, WELCOME_MODALS, WELCOME_SELECTORS, WELCOME_VIEWS = {}, {}, {}, {}, {}, {}

# Define the table structure for bulk insert
dashboard_component_definitions_table = table(
    'dashboard_component_definitions',
    column('dashboard_type', sa.String),
    column('component_type', sa.String),
    column('component_key', sa.String),
    column('definition', sa.JSON) # Use JSON type here
)

def _prepare_data(seed_dict, dashboard_type, component_type):
    """Helper function to format data for bulk insert."""
    data = []
    for key, definition_dict in seed_dict.items():
        data.append({
            'dashboard_type': dashboard_type,
            'component_type': component_type,
            'component_key': key,
            'definition': json.dumps(definition_dict) # Convert dict to JSON string
        })
    return data

def upgrade() -> None:
    """Seed the dashboard_component_definitions table."""
    seed_data = []

    # Collect data from all imported dictionaries
    seed_data.extend(_prepare_data(COMMON_BUTTONS, 'common', 'button'))
    seed_data.extend(_prepare_data(COMMON_EMBEDS, 'common', 'embed'))
    seed_data.extend(_prepare_data(COMMON_MESSAGES, 'common', 'message'))
    seed_data.extend(_prepare_data(COMMON_MODALS, 'common', 'modal'))
    seed_data.extend(_prepare_data(COMMON_SELECTORS, 'common', 'selector'))
    seed_data.extend(_prepare_data(COMMON_VIEWS, 'common', 'view'))

    seed_data.extend(_prepare_data(GAMEHUB_BUTTONS, 'gamehub', 'button'))
    seed_data.extend(_prepare_data(GAMEHUB_EMBEDS, 'gamehub', 'embed'))
    seed_data.extend(_prepare_data(GAMEHUB_MESSAGES, 'gamehub', 'message'))
    seed_data.extend(_prepare_data(GAMEHUB_MODALS, 'gamehub', 'modal'))
    seed_data.extend(_prepare_data(GAMEHUB_SELECTORS, 'gamehub', 'selector'))
    seed_data.extend(_prepare_data(GAMEHUB_VIEWS, 'gamehub', 'view'))

    seed_data.extend(_prepare_data(MONITORING_BUTTONS, 'monitoring', 'button'))
    seed_data.extend(_prepare_data(MONITORING_EMBEDS, 'monitoring', 'embed'))
    seed_data.extend(_prepare_data(MONITORING_MESSAGES, 'monitoring', 'message'))
    seed_data.extend(_prepare_data(MONITORING_MODALS, 'monitoring', 'modal'))
    seed_data.extend(_prepare_data(MONITORING_SELECTORS, 'monitoring', 'selector'))
    seed_data.extend(_prepare_data(MONITORING_VIEWS, 'monitoring', 'view'))

    seed_data.extend(_prepare_data(PROJECT_BUTTONS, 'project', 'button'))
    seed_data.extend(_prepare_data(PROJECT_EMBEDS, 'project', 'embed'))
    seed_data.extend(_prepare_data(PROJECT_MESSAGES, 'project', 'message'))
    seed_data.extend(_prepare_data(PROJECT_MODALS, 'project', 'modal'))
    seed_data.extend(_prepare_data(PROJECT_SELECTORS, 'project', 'selector'))
    seed_data.extend(_prepare_data(PROJECT_VIEWS, 'project', 'view'))

    seed_data.extend(_prepare_data(WELCOME_BUTTONS, 'welcome', 'button'))
    seed_data.extend(_prepare_data(WELCOME_EMBEDS, 'welcome', 'embed'))
    # Ensure WELCOME_MESSAGES exists or handle the case where it doesn't
    if 'WELCOME_MESSAGES' in globals() and WELCOME_MESSAGES:
       seed_data.extend(_prepare_data(WELCOME_MESSAGES, 'welcome', 'message'))
    seed_data.extend(_prepare_data(WELCOME_MODALS, 'welcome', 'modal'))
    seed_data.extend(_prepare_data(WELCOME_SELECTORS, 'welcome', 'selector'))
    seed_data.extend(_prepare_data(WELCOME_VIEWS, 'welcome', 'view'))


    if seed_data:
        print(f"Inserting {len(seed_data)} component definitions...")
        # Perform the bulk insert
        op.bulk_insert(dashboard_component_definitions_table, seed_data)
    else:
        print("No component definitions found to seed.")


def downgrade() -> None:
    """Remove the seeded dashboard component definitions."""
    print("Deleting all data from dashboard_component_definitions...")
    # Delete all rows from the table
    op.execute('DELETE FROM dashboard_component_definitions')
    print("Data deleted.")
