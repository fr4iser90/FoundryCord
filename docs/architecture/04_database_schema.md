# 4. Database Schema

## Overview

Provide a high-level overview of the database design.
*   **Type:** PostgreSQL
*   **ORM:** SQLAlchemy (v2.x)
*   **Migration Tool:** Alembic (Located in `app/shared/infrastructure/database/migrations`)

## Entity Relationship Diagram (ERD)

*Include an image or link to an ERD diagram visualization if possible.* This is the best way to understand the relationships.

(Placeholder for ERD image/link)

## Key Tables

Describe the purpose and key columns/relationships for important tables (Based on models in `app/shared/infrastructure/models/`):

*   **`app_users`:** (`auth/user_entity.py`)
    *   Stores application user information, often linked to Discord accounts.
    *   Key Columns: `id` (PK, Int), `discord_id` (String, unique), `username`, `avatar`, `is_owner` (Boolean).
    *   Relationships: `guild_roles` (to `discord_guild_users`), `sessions`, `keys`.
*   **`discord_guilds`:** (`discord/entities/guild_entity.py`)
    *   Stores basic information about Discord servers (guilds) the bot has interacted with.
    *   Key Columns: `guild_id` (PK, String), `guild_name`, `icon_hash`.
    *   Relationships: `user_roles` (to `discord_guild_users`), `config`, `structure_template`.
*   **`guild_configs`:** (`discord/entities/guild_config_entity.py`)
    *   Stores bot configuration specific to each guild.
    *   Key Columns: `id` (PK, Int), `guild_id` (FK to `discord_guilds.guild_id`, unique), `config_data` (JSON), `active_template_id` (FK to `guild_templates.id`, nullable).
    *   Relationships: `guild`.
*   **`discord_guild_users`:** (`discord/entities/guild_user_entity.py`)
    *   Associates application users with guilds and assigns them a role within that guild context.
    *   Key Columns: `id` (PK, Int), `guild_id` (FK to `discord_guilds.guild_id`), `user_id` (FK to `app_users.id`), `role_id` (FK to `app_roles.id`).
    *   Constraints: `UniqueConstraint('guild_id', 'user_id')`.
    *   Relationships: `user`, `role`, `guild`.
*   **`guild_templates`:** (`guild_templates/guild_template_entity.py`)
    *   Main table for guild structure templates (user-saved or initial snapshots).
    *   Key Columns: `id` (PK, Int), `guild_id` (FK to `discord_guilds.guild_id`, nullable, index, ondelete='SET NULL'), `template_name` (String), `template_description` (Text), `creator_user_id` (FK to `app_users.id`, nullable, index, ondelete='SET NULL'), `is_shared` (Boolean), `created_at` (DateTime), `updated_at` (DateTime).
    *   Note: `is_initial_snapshot` is implied by `creator_user_id IS NULL`.
    *   Relationships: `categories` (1-M), `channels` (1-M), `guild`, `creator`.
*   **`guild_template_categories`:** (`guild_templates/guild_template_category_entity.py`)
    *   Stores categories belonging to a specific template.
    *   Key Columns: `id` (PK, Int), `guild_template_id` (FK to `guild_templates.id`, index, ondelete='CASCADE'), `category_name` (String), `position` (Int), `metadata_json` (JSON).
    *   Relationships: `guild_template`, `channels` (1-M), `permissions` (1-M).
*   **`guild_template_channels`:** (`guild_templates/guild_template_channel_entity.py`)
    *   Stores channels belonging to a specific template.
    *   Key Columns: `id` (PK, Int), `guild_template_id` (FK to `guild_templates.id`, index, ondelete='CASCADE'), `channel_name` (String), `channel_type` (String), `position` (Int), `topic` (Text), `is_nsfw` (Boolean), `slowmode_delay` (Int), `parent_category_template_id` (FK to `guild_template_categories.id`, nullable, index, ondelete='SET NULL'), `metadata_json` (JSON).
    *   Relationships: `guild_template`, `parent_category`, `permissions` (1-M).
*   **`guild_template_category_permissions`:** (`guild_templates/guild_template_category_permission_entity.py`)
    *   Stores permission overwrites for a role on a template category.
    *   Key Columns: `id` (PK, Int), `category_template_id` (FK to `guild_template_categories.id`, index, ondelete='CASCADE'), `role_name` (String), `allow_permissions_bitfield` (BigInt), `deny_permissions_bitfield` (BigInt).
    *   Relationships: `category_template`.
*   **`guild_template_channel_permissions`:** (`guild_templates/guild_template_channel_permission_entity.py`)
    *   Stores permission overwrites for a role on a template channel.
    *   Key Columns: `id` (PK, Int), `channel_template_id` (FK to `guild_template_channels.id`, index, ondelete='CASCADE'), `role_name` (String), `allow_permissions_bitfield` (BigInt), `deny_permissions_bitfield` (BigInt).
    *   Relationships: `channel_template`.
*   **`ui_layouts`:** (`ui/ui_layout_entity.py`)
    *   Stores user-specific UI layout configurations (e.g., Gridstack positions).
    *   Key Columns: `id` (PK, Int), `user_id` (FK to `app_users.id`), `page_identifier` (String, index), `layout_data` (JSON), `created_at` (DateTime), `updated_at` (DateTime).
    *   Constraints: `UniqueConstraint('user_id', 'page_identifier')`.
    *   Relationships: `user`.

*(Add other important tables like `app_roles`, `sessions`, `api_keys` etc. as needed)*

## Relationships

Briefly describe key relationships (See details in table descriptions above):

*   One-to-Many: `guild_templates` -> `guild_template_categories`, `guild_template_channels`.
*   One-to-Many: `guild_template_categories` -> `guild_template_channels` (via `parent_category_template_id`).
*   One-to-Many: `guild_template_categories` -> `guild_template_category_permissions`.
*   One-to-Many: `guild_template_channels` -> `guild_template_channel_permissions`.
*   Many-to-One: `discord_guild_users` -> `app_users`, `discord_guilds`, `app_roles`.
*   One-to-One (effectively via unique constraint): `discord_guilds` -> `guild_configs`.
*   One-to-Many: `app_users` -> `ui_layouts`.

## Indexing Strategy

*   Key indexes are defined on primary keys and foreign keys (see `index=True` in models).
*   Specific indexes exist on `guild_templates.guild_id`, `guild_templates.creator_user_id`, `ui_layouts.page_identifier`.
*   Unique constraints enforce data integrity (e.g., `discord_guild_users`, `ui_layouts`). 