# 4. Database Schema

This document provides an overview of the FoundryCord database schema, designed to support its various features for Discord server management, template design, and user interaction. Understanding the schema is crucial for developers working on features that involve data persistence or retrieval.

## Overview

*   **Type:** PostgreSQL
*   **ORM:** SQLAlchemy (v2.x)
*   **Migration Tool:** Alembic (Migration scripts located in `app/shared/infrastructure/database/migrations`)

## Entity Relationship Diagram (ERD)

Below is an Entity Relationship Diagram illustrating the key tables and their relationships. Due to the number of tables, this ERD focuses on the core entities and their most significant connections. More detailed relationships are described in the "Key Tables" section.

```mermaid
erDiagram
    APP_USERS {
        int id PK
        string discord_id UK "Unique Discord User ID"
        string username
        string avatar
        boolean is_owner
        datetime created_at
        datetime updated_at
    }

    APP_ROLES {
        int id PK
        string name UK
        string description
    }

    DISCORD_GUILDS {
        string guild_id PK "Discord Guild ID"
        string guild_name
        string icon_hash
        datetime created_at
        datetime updated_at
    }

    DISCORD_GUILD_USERS {
        int id PK
        string guild_id FK "References DISCORD_GUILDS"
        int user_id FK "References APP_USERS"
        int role_id FK "References APP_ROLES"
        datetime joined_at
        string nickname
    }

    GUILD_CONFIGS {
        int id PK
        string guild_id FK "References DISCORD_GUILDS, Unique"
        json config_data
        int active_template_id FK "References GUILD_TEMPLATES (nullable)"
        datetime created_at
        datetime updated_at
    }

    GUILD_TEMPLATES {
        int id PK
        string guild_id FK "References DISCORD_GUILDS (nullable, for original snapshot)"
        string template_name
        text template_description
        int creator_user_id FK "References APP_USERS (nullable)"
        boolean is_shared
        datetime created_at
        datetime updated_at
    }

    GUILD_TEMPLATE_CATEGORIES {
        int id PK
        int guild_template_id FK "References GUILD_TEMPLATES"
        string category_name
        int position
        json metadata_json
    }

    GUILD_TEMPLATE_CHANNELS {
        int id PK
        int guild_template_id FK "References GUILD_TEMPLATES"
        string channel_name
        string channel_type
        int position
        text topic
        boolean is_nsfw
        int slowmode_delay
        int parent_category_template_id FK "References GUILD_TEMPLATE_CATEGORIES (nullable)"
        json metadata_json
    }

    GUILD_TEMPLATE_CATEGORY_PERMISSIONS {
        int id PK
        int category_template_id FK "References GUILD_TEMPLATE_CATEGORIES"
        string role_name "Or FK to a potential app_roles or discord_roles table"
        bigint allow_permissions_bitfield
        bigint deny_permissions_bitfield
    }

    GUILD_TEMPLATE_CHANNEL_PERMISSIONS {
        int id PK
        int channel_template_id FK "References GUILD_TEMPLATE_CHANNELS"
        string role_name "Or FK to a potential app_roles or discord_roles table"
        bigint allow_permissions_bitfield
        bigint deny_permissions_bitfield
    }

    UI_LAYOUTS {
        int id PK
        int user_id FK "References APP_USERS"
        string page_identifier "e.g., 'dashboard_main', 'guild_designer'"
        json layout_data "Gridstack layout configuration"
        datetime created_at
        datetime updated_at
    }

    SESSIONS {
        string session_id PK
        int user_id FK "References APP_USERS"
        datetime expires_at
        json data
    }

    API_KEYS {
        string key_hash PK
        int user_id FK "References APP_USERS"
        string description
        datetime expires_at
        datetime created_at
    }

    AUDIT_LOGS {
        int id PK
        int user_id FK "References APP_USERS (nullable, for system actions)"
        string action
        json details
        datetime timestamp
    }

    APP_USERS ||--o{ DISCORD_GUILD_USERS : "participates_in"
    DISCORD_GUILDS ||--o{ DISCORD_GUILD_USERS : "has_member"
    APP_ROLES ||--o{ DISCORD_GUILD_USERS : "assigned_to"
    DISCORD_GUILDS ||--|| GUILD_CONFIGS : "has_one"
    DISCORD_GUILDS ||--o{ GUILD_TEMPLATES : "can_have_snapshot_of (original)"
    APP_USERS ||--o{ GUILD_TEMPLATES : "created_by"
    GUILD_TEMPLATES ||--o{ GUILD_TEMPLATE_CATEGORIES : "contains"
    GUILD_TEMPLATES ||--o{ GUILD_TEMPLATE_CHANNELS : "contains (direct or via category)"
    GUILD_TEMPLATE_CATEGORIES ||--o{ GUILD_TEMPLATE_CHANNELS : "contains"
    GUILD_TEMPLATE_CATEGORIES ||--o{ GUILD_TEMPLATE_CATEGORY_PERMISSIONS : "has_permissions_for"
    GUILD_TEMPLATE_CHANNELS ||--o{ GUILD_TEMPLATE_CHANNEL_PERMISSIONS : "has_permissions_for"
    APP_USERS ||--o{ UI_LAYOUTS : "has_layout_for"
    APP_USERS ||--o{ SESSIONS : "has"
    APP_USERS ||--o{ API_KEYS : "owns"
    APP_USERS ||--o{ AUDIT_LOGS : "performed_by (optional)"
    GUILD_CONFIGS }o--|| GUILD_TEMPLATES : "activates (optional)"

```

## Key Tables & Domain Meaning

This section describes the purpose of key tables, their domain meaning, and how they relate to DDD concepts like Entities and Aggregates. The table names generally correspond to SQLAlchemy models found in `app/shared/infrastructure/models/`.

*   **`app_users`** (Entity: `AppUser`)
    *   **Domain Meaning:** Represents a user of the FoundryCord application. This user may or may not be linked to a Discord account initially but often is. This table is central to authentication, authorization, and tracking user-specific configurations (like UI layouts) or actions (audit logs, template creation).
    *   Key Columns: `id` (PK), `discord_id` (UK, links to Discord identity), `username`, `is_owner`.
    *   Relationships: Many-to-many with `discord_guilds` via `discord_guild_users`; one-to-many with `sessions`, `api_keys`, `ui_layouts`, `guild_templates` (as creator), `audit_logs`.

*   **`app_roles`** (Entity: `AppRole` - *Assumed, needs model verification*)
    *   **Domain Meaning:** Defines application-specific roles (e.g., 'Admin', 'Moderator', 'Designer') used for FoundryCord\'s internal permission system, distinct from Discord roles.
    *   Key Columns: `id` (PK), `name` (UK).
    *   Relationships: One-to-many with `discord_guild_users` (a user has an app role within a specific guild context for FoundryCord features).

*   **`discord_guilds`** (Entity: `DiscordGuild`)
    *   **Domain Meaning:** Represents a Discord server (guild) that has been onboarded or interacted with by FoundryCord. It acts as a root for guild-specific configurations and data.
    *   Key Columns: `guild_id` (PK, Discord snowflake), `guild_name`.
    *   Relationships: One-to-one with `guild_configs`; one-to-many with `discord_guild_users`, `guild_templates` (for initial snapshots).

*   **`discord_guild_users`** (Association Table)
    *   **Domain Meaning:** Links an `app_user` to a `discord_guild` and assigns them an `app_role` within the context of that guild for FoundryCord. This defines a user\'s specific permissions/role for FoundryCord features related to a particular guild.
    *   Key Columns: `guild_id` (FK), `user_id` (FK), `role_id` (FK).

*   **`guild_configs`** (Entity: `GuildConfig`)
    *   **Domain Meaning:** Stores bot and application configurations specific to a particular `discord_guild`. This includes settings like command prefixes (if any), feature toggles for that guild, and importantly, the `active_template_id` which links to the currently applied guild structure template.
    *   Key Columns: `guild_id` (FK, UK), `config_data` (JSON), `active_template_id` (FK).

*   **`guild_templates`** (Aggregate Root, Entity: `GuildTemplate`)
    *   **Domain Meaning:** This is a central entity representing a saved, reusable Discord server structure. It\'s the core of the Guild Designer feature. A template can be an initial snapshot of an existing guild or a user-designed structure.
    *   **As an Aggregate:** A `GuildTemplate` is the root of an aggregate that includes `GuildTemplateCategories`, `GuildTemplateChannels`, and their respective permission overrides. Changes to the template structure are managed through the `GuildTemplate` root.
    *   Key Columns: `id` (PK), `template_name`, `creator_user_id` (FK), `is_shared`.
    *   Relationships: One-to-many with `guild_template_categories` and `guild_template_channels`.

*   **`guild_template_categories`** (Entity: `GuildTemplateCategory`, part of `GuildTemplate` Aggregate)
    *   **Domain Meaning:** Defines a category within a `guild_template`.
    *   Key Columns: `guild_template_id` (FK), `category_name`, `position`.
    *   Relationships: One-to-many with `guild_template_channels` (as parent), one-to-many with `guild_template_category_permissions`.

*   **`guild_template_channels`** (Entity: `GuildTemplateChannel`, part of `GuildTemplate` Aggregate)
    *   **Domain Meaning:** Defines a channel (text, voice, etc.) within a `guild_template`, optionally parented by a `guild_template_category`.
    *   Key Columns: `guild_template_id` (FK), `channel_name`, `channel_type`, `parent_category_template_id` (FK).
    *   Relationships: One-to-many with `guild_template_channel_permissions`.

*   **`guild_template_category_permissions`** / **`guild_template_channel_permissions`** (Value Objects or Entities, part of `GuildTemplate` Aggregate)
    *   **Domain Meaning:** Define permission overwrites (allow/deny bitfields) for a specific role (identified by `role_name`) on a template category or channel. The `role_name` would ideally map to Discord roles that are expected to exist when the template is applied.

*   **`ui_layouts`** (Entity: `UILayout`)
    *   **Domain Meaning:** Stores user-specific UI layout customizations, primarily for drag-and-drop dashboards (e.g., Gridstack positions for widgets on a specific page).
    *   Key Columns: `user_id` (FK), `page_identifier` (UK with user_id), `layout_data` (JSON).

*   **`sessions`** (Entity: `Session`)
    *   **Domain Meaning:** Manages user sessions for the web application, enabling persistent logins.
    *   Key Columns: `session_id` (PK), `user_id` (FK), `expires_at`.

*   **`api_keys`** (Entity: `ApiKey`)
    *   **Domain Meaning:** Stores API keys that can be issued to users for programmatic access to FoundryCord\'s API.
    *   Key Columns: `key_hash` (PK), `user_id` (FK), `expires_at`.

*   **`audit_logs`** (Entity: `AuditLog`)
    *   **Domain Meaning:** Records significant actions performed by users or the system for auditing and troubleshooting purposes.
    *   Key Columns: `user_id` (FK, nullable), `action`, `details` (JSON).

*(This list is not exhaustive but covers the main entities. Other tables like `security_keys`, `log_entries`, `state_snapshots`, etc., support specific infrastructure or operational concerns.)*

## Relationships & Data Integrity

*   **Foreign Keys:** Enforce referential integrity between related tables (e.g., a `guild_config` must belong to an existing `discord_guild`). `ON DELETE` policies (e.g., `CASCADE`, `SET NULL`) are defined in the SQLAlchemy models to manage cascading effects.
*   **Indexes:** Primary keys are automatically indexed. Foreign keys and frequently queried columns (especially those used in `WHERE` clauses or `JOIN` conditions) are indexed to improve query performance (e.g., `guild_id` on `guild_templates`).
*   **Unique Constraints:** Ensure data uniqueness where required (e.g., a user can only have one layout for a specific page `(user_id, page_identifier)` in `ui_layouts`; `discord_id` in `app_users`).

## Indexing Strategy

*   Primary keys are automatically indexed.
*   Foreign keys are generally indexed (as specified by `index=True` in SQLAlchemy models) to optimize join operations.
*   Specific indexes are created for columns frequently used in lookups or filtering, for example:
    *   `app_users.discord_id`
    *   `guild_templates.guild_id`
    *   `guild_templates.creator_user_id`
    *   `ui_layouts.page_identifier`
    *   `guild_configs.active_template_id`
*   Unique constraints (e.g., on `discord_guild_users (guild_id, user_id)`, `ui_layouts (user_id, page_identifier)`) also create implicit indexes and enforce data integrity. 