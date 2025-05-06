# Guild Designer: Structure & Template Application Workflows

**(See also: [Guild Designer Main TODO](../../../../4_project_management/todo/guild_designer.md))**

## Overview

This document outlines the key workflows the FoundryCord bot employs to manage Discord server structures (categories, channels, permissions). These workflows are central to the **Guild Designer** feature, particularly when applying saved templates to a server, but also underpin direct structural manipulation commands if implemented.

The primary goals of these workflows are:
1.  Accurately translating a `GuildTemplate` definition into a live Discord server structure.
2.  Creating, updating, and deleting categories and channels based on template or direct commands.
3.  Managing permission overwrites for roles on these structural elements.
4.  Handling specialized channel features like Channel Following and embedded Dashboard Panels.

## Key Structural Feature Implementations

### 1. Channel Following
*   **Purpose:** Allows announcement channels to be "followed," automatically crossposting their messages to other designated channels.
*   **FoundryCord Implementation:** The bot facilitates the setup and tracking of these follow relationships. Discord's underlying mechanism often involves webhooks that Discord itself manages when a follow is initiated via their API.
*   **Details:** For an in-depth explanation of the entity, repository, services, and workflows involved, see: **[Channel Follow Implementation Details](./channel_follow_implementation.md)**.

### 2. Dashboard Panels in Channels
*   **Purpose:** Enables embedding interactive UI panels (dashboards) directly within Discord channels. These panels can display real-time data, statistics, or provide control interfaces.
*   **FoundryCord Implementation:**
    *   Dashboards are constructed as Discord messages with rich embeds and interactive components (buttons, select menus).
    *   The `DashboardLifecycleService` (in `app/bot/application/services/dashboard/`) manages the creation, updating, and interaction handling for these dashboard messages.
    *   `DashboardController` (in `app/bot/interfaces/dashboards/controller/`) handles user interactions originating from these components.
    *   Configurations and content definitions are often stored in the database using entities like `DashboardEntity` and `DashboardComponentEntity` (from `app/shared/`).
    *   Data displayed is fetched by `DashboardDataService` or similar services.

## Core Workflows for Template Application

When a `GuildTemplate` is applied to a Discord server, several coordinated workflows are executed. The overall orchestration is typically handled by a `TemplateApplicationWorkflow` (conceptual, likely part of `app/bot/application/workflows/guild/template_application.py`).

### 1. Category & Channel Creation/Update Workflow
*   **Responsibility:** Iterates through category and channel definitions in the `GuildTemplate` and creates or updates them on the target Discord server.
*   **Process:**
    1.  The `TemplateApplicationWorkflow` retrieves the `GuildTemplate` with all its child entities (`GuildTemplateCategory`, `GuildTemplateChannel`).
    2.  For each category in the template: Calls a `CategorySetupService` (or similar in `app/bot/application/services/category/`) which uses a `CategoryBuilder` to prepare parameters and then interacts with a `DiscordInteractionService` (or directly with `nextcord`) to create/update the category on Discord.
    3.  For each channel in the template: Calls a `ChannelSetupService` (or similar in `app/bot/application/services/channel/`) which uses a `ChannelBuilder` and `ChannelFactory` to prepare parameters (including parent category linkage) and then interacts with `DiscordInteractionService` to create/update the channel.
    4.  Mappings between template entity IDs and actual Discord entity IDs are maintained during the process for subsequent steps like permission application.
*   **Key Modules:** `TemplateApplicationWorkflow`, `CategorySetupService`, `ChannelSetupService`, `CategoryBuilder`, `ChannelBuilder`, `DiscordInteractionService`, `GuildTemplateRepository`, `CategoryRepository`, `ChannelRepository`.
*   *(A sequence diagram for this part of the template application can be found in `docs/3_developer_guides/03_core_components/bot_internals.md`.)*

### 2. Permission Application Workflow (Template Context)
*   **Responsibility:** Applies permission overwrites defined in the `GuildTemplate` to the newly created or existing categories and channels on the target Discord server.
*   **Process:** (See sequence diagram below)
    1.  After categories and channels are created/updated, the `TemplateApplicationWorkflow` iterates through `GuildTemplateCategoryPermission` and `GuildTemplateChannelPermission` entities associated with the template.
    2.  For each permission entity: It resolves the stored `role_name` to an actual `nextcord.Role` object on the target guild (this might involve fetching roles from the guild or assuming roles with specific names exist).
    3.  It retrieves the actual Discord ID of the category or channel using the mapping created during the creation phase.
    4.  It constructs a `nextcord.PermissionOverwrite` object using the `allow_permissions_bitfield` and `deny_permissions_bitfield` from the template permission entity.
    5.  It calls the appropriate `nextcord` method (e.g., `category.set_permissions()` or `channel.set_permissions()`) via a `DiscordInteractionService` to apply the overwrite.
*   **Key Modules:** `TemplateApplicationWorkflow`, `DiscordInteractionService`, `GuildRepository` (to fetch roles), `GuildTemplateCategoryPermission` / `GuildTemplateChannelPermission` entities.

**Sequence Diagram: Applying Template Permissions**
```mermaid
sequenceDiagram
    participant TplAppWF as TemplateApplicationWorkflow
    participant DiscService as DiscordInteractionService
    participant GuildRepo as GuildRepository (Shared)
    participant DiscordAPI as Discord API

    TplAppWF->>TplAppWF: For each Category/Channel Permission in Template
    TplAppWF->>GuildRepo: get_guild_roles(guild_id)
    GuildRepo-->>TplAppWF: List of actual_discord_roles
    TplAppWF->>TplAppWF: Resolve template_permission.role_name to actual_discord_role
    alt Role not found on Guild
        TplAppWF->>TplAppWF: Log warning / Handle error (e.g., skip permission)
        continue
    end
    TplAppWF->>TplAppWF: Get mapped_discord_entity_id (Category or Channel)
    TplAppWF->>DiscService: apply_permission_overwrite(mapped_discord_entity_id, actual_discord_role, allow_bits, deny_bits)
    DiscService->>+DiscordAPI: Edit Channel Permissions (for Category/Channel)
    DiscordAPI-->>-DiscService: Success/Failure
    DiscService-->>TplAppWF: Result
    TplAppWF->>TplAppWF: Log permission application status
```

## Integration Points

These structure workflows heavily integrate with:

*   **Discord API:** For all direct manipulations of server categories, channels, permissions, and webhooks.
*   **Shared Repositories (`app/shared/`):** For persisting and retrieving `GuildTemplate` data, `ChannelFollow` records, `DashboardEntity` configurations, and other related entities.
*   **Shared Domain Services (`app/shared/`):** For core logic like audit logging (`AuditService`).
*   **Bot Application Services (`app/bot/application/services/`):** Specialized services for category, channel, and dashboard setup and management.
*   **Bot Infrastructure (`app/bot/infrastructure/`):** Components for Discord interaction, configuration access. 