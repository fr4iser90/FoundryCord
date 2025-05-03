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
    from app.shared.infrastructure.database.seeds.dashboard_templates.common.buttons import DEFAULT_BUTTONS as COMMON_BUTTONS
    from app.shared.infrastructure.database.seeds.dashboard_templates.common.embeds import DEFAULT_EMBEDS as COMMON_EMBEDS
    from app.shared.infrastructure.database.seeds.dashboard_templates.common.messages import DEFAULT_MESSAGES as COMMON_MESSAGES
    from app.shared.infrastructure.database.seeds.dashboard_templates.common.modals import DEFAULT_MODALS as COMMON_MODALS
    from app.shared.infrastructure.database.seeds.dashboard_templates.common.selectors import DEFAULT_SELECTORS as COMMON_SELECTORS
    from app.shared.infrastructure.database.seeds.dashboard_templates.common.views import DEFAULT_VIEWS as COMMON_VIEWS
except ImportError as e:
    print(f"Could not import common seeds: {e}")
    COMMON_BUTTONS, COMMON_EMBEDS, COMMON_MESSAGES, COMMON_MODALS, COMMON_SELECTORS, COMMON_VIEWS = {}, {}, {}, {}, {}, {}

try:
    from app.shared.infrastructure.database.seeds.dashboard_templates.gamehub.buttons import GAMEHUB_BUTTONS
    from app.shared.infrastructure.database.seeds.dashboard_templates.gamehub.embeds import GAMEHUB_EMBEDS
    from app.shared.infrastructure.database.seeds.dashboard_templates.gamehub.messages import GAMEHUB_MESSAGES
    from app.shared.infrastructure.database.seeds.dashboard_templates.gamehub.modals import GAMEHUB_MODALS
    from app.shared.infrastructure.database.seeds.dashboard_templates.gamehub.selectors import GAMEHUB_SELECTORS
    from app.shared.infrastructure.database.seeds.dashboard_templates.gamehub.views import GAMEHUB_VIEWS
except ImportError as e:
    print(f"Could not import gamehub seeds: {e}")
    GAMEHUB_BUTTONS, GAMEHUB_EMBEDS, GAMEHUB_MESSAGES, GAMEHUB_MODALS, GAMEHUB_SELECTORS, GAMEHUB_VIEWS = {}, {}, {}, {}, {}, {}

try:
    from app.shared.infrastructure.database.seeds.dashboard_templates.monitoring.buttons import MONITORING_BUTTONS
    from app.shared.infrastructure.database.seeds.dashboard_templates.monitoring.embeds import MONITORING_EMBEDS
    from app.shared.infrastructure.database.seeds.dashboard_templates.monitoring.messages import MONITORING_MESSAGES
    from app.shared.infrastructure.database.seeds.dashboard_templates.monitoring.modals import MONITORING_MODALS
    from app.shared.infrastructure.database.seeds.dashboard_templates.monitoring.selectors import MONITORING_SELECTORS
    from app.shared.infrastructure.database.seeds.dashboard_templates.monitoring.views import MONITORING_VIEWS
except ImportError as e:
    print(f"Could not import monitoring seeds: {e}")
    MONITORING_BUTTONS, MONITORING_EMBEDS, MONITORING_MESSAGES, MONITORING_MODALS, MONITORING_SELECTORS, MONITORING_VIEWS = {}, {}, {}, {}, {}, {}

try:
    from app.shared.infrastructure.database.seeds.dashboard_templates.project.buttons import PROJECT_BUTTONS
    from app.shared.infrastructure.database.seeds.dashboard_templates.project.embeds import PROJECT_EMBEDS
    from app.shared.infrastructure.database.seeds.dashboard_templates.project.messages import PROJECT_MESSAGES
    from app.shared.infrastructure.database.seeds.dashboard_templates.project.modals import PROJECT_MODALS
    from app.shared.infrastructure.database.seeds.dashboard_templates.project.selectors import PROJECT_SELECTORS
    from app.shared.infrastructure.database.seeds.dashboard_templates.project.views import PROJECT_VIEWS
except ImportError as e:
    print(f"Could not import project seeds: {e}")
    PROJECT_BUTTONS, PROJECT_EMBEDS, PROJECT_MESSAGES, PROJECT_MODALS, PROJECT_SELECTORS, PROJECT_VIEWS = {}, {}, {}, {}, {}, {}

try:
    from app.shared.infrastructure.database.seeds.dashboard_templates.welcome.buttons import WELCOME_BUTTONS
    from app.shared.infrastructure.database.seeds.dashboard_templates.welcome.embeds import WELCOME_EMBEDS
    from app.shared.infrastructure.database.seeds.dashboard_templates.welcome.messages import WELCOME_MESSAGES # Check if exists
    from app.shared.infrastructure.database.seeds.dashboard_templates.welcome.modals import WELCOME_MODALS
    from app.shared.infrastructure.database.seeds.dashboard_templates.welcome.selectors import WELCOME_SELECTORS
    from app.shared.infrastructure.database.seeds.dashboard_templates.welcome.views import WELCOME_VIEWS
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
    """Helper function to format data for bulk insert.
    Ensures that the definition dictionary has valid metadata fields
    (display_name, category) before converting to JSON.
    """
    data = []
    for key, definition_dict in seed_dict.items():
        # Ensure definition_dict is a dictionary
        if not isinstance(definition_dict, dict):
            print(f"Warning: Skipping non-dict definition for key '{key}' in {dashboard_type}/{component_type}")
            continue
            
        # Ensure metadata exists and is a dictionary
        metadata = definition_dict.setdefault('metadata', {}) 
        if not isinstance(metadata, dict):
             print(f"Warning: Replacing non-dict metadata for key '{key}' in {dashboard_type}/{component_type}")
             metadata = {}
             definition_dict['metadata'] = metadata
             
        # --- Ensure display_name exists (snake_case) --- 
        if 'display_name' not in metadata or not metadata.get('display_name'):
            if 'displayName' in metadata and metadata.get('displayName'):
                 print(f"Warning: Found 'displayName' (camelCase) instead of 'display_name' for key '{key}'. Converting.")
                 metadata['display_name'] = metadata.pop('displayName') 
            else:
                default_display_name = key.replace('_', ' ').title()
                print(f"Warning: Missing or empty 'display_name' for key '{key}' in {dashboard_type}/{component_type}. Using default: '{default_display_name}'")
                metadata['display_name'] = default_display_name
        elif 'displayName' in metadata: 
             print(f"Warning: Found both 'display_name' and 'displayName' for key '{key}'. Removing camelCase version.")
             metadata.pop('displayName')
        # -------------------------------------------
        
        # --- Ensure category exists --- 
        if 'category' not in metadata or not metadata.get('category') or not isinstance(metadata.get('category'), str):
            # Use component_type as a default category if category is missing/invalid
            default_category = component_type.replace('_', ' ').title() if component_type else 'General'
            print(f"Warning: Missing or invalid 'category' for key '{key}' in {dashboard_type}/{component_type}. Using default: '{default_category}'")
            metadata['category'] = default_category
        # -----------------------------
        
        # Ensure other required sub-schemas exist as empty lists/dicts if needed (optional, based on schema)
        # definition_dict.setdefault('config_schema', [])
        # definition_dict.setdefault('preview_hints', None) # Or {} if it's a required dict

        data.append({
            'dashboard_type': dashboard_type,
            'component_type': component_type,
            'component_key': key,
            'definition': json.dumps(definition_dict) # Convert the potentially modified dict to JSON
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
