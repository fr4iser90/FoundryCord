# REST API Documentation

This document outlines the structure and endpoints for the REST API.

## V1 API (`/api/v1`)

All V1 endpoints are prefixed with `/api/v1`.

### Authentication (`/auth`)

Handles user login, logout, session management via Discord OAuth.

- `GET /auth/login`: Redirects user to Discord for authentication.
- `GET /auth/callback`: Handles the callback from Discord, exchanges code, sets session.
- `GET /auth/logout`: Clears user session and redirects.
- `POST /auth/logout`: (Alternative method for logout, functionality likely same as GET).
- `GET /auth/me`: Returns information about the currently logged-in user.
- `POST /auth/refresh`: Refreshes the user's access token (if applicable).

### Guild Configuration (`/guilds/{guild_id}/config`)

Manages specific configurations for a given guild.

- `GET /guilds/{guild_id}/config`: Get specific configuration for a guild.
- `PUT /guilds/{guild_id}/config`: Update specific configuration for a guild.
- `GET /guilds/{guild_id}/permissions`: Get specific permissions settings for a guild.
- `PUT /guilds/{guild_id}/permissions`: Update specific permissions settings for a guild.

### Guild User Management (`/guilds/{guild_id}/users`)

Manages users within the context of a specific guild.

- `GET /guilds/{guild_id}/users/{user_id}`: Get details about a specific user within the guild.
- `PUT /guilds/{guild_id}/users/{user_id}/role`: Update a user's role within the specific guild.
- `PUT /guilds/{guild_id}/users/{user_id}/app-role`: Update a user's *application-wide* role (requires elevated permissions).
- `POST /guilds/{guild_id}/users/{user_id}/kick`: Remove a user from the guild (bot action).

### Guild Selection (`/servers`)

Handles selecting the active guild for the user session and listing available guilds.

- `GET /servers/`: List guilds available to the current user (typically approved/member of).
- `GET /servers/current`: Get the currently selected guild from the user's session.
- `POST /servers/select/{guild_id}`: Set the selected guild in the user's session.

### Guild Structure Templates

Manages reusable templates based on Discord server structures (categories, channels, permissions).

**A. General Template Operations (`/api/v1/templates/guilds`)**

*Controller: `GuildTemplateController` (Uses `general_template_router`)*

- **`GET /api/v1/templates/guilds/`**
    - **Purpose:** List all accessible Guild Structure Templates (e.g., created by the user).
    - **Response:** `GuildTemplateListResponseSchema` (containing `template_id`, `template_name`, `created_at`, `guild_id`).
    - *Status: Implemented.*
- **`GET /api/v1/templates/guilds/{template_id}`**
    - **Purpose:** Get the full structure of a specific Guild Structure Template by its database ID.
    - **Response:** `GuildTemplateResponseSchema` (detailed structure).
    - *Status: Implemented.*
- **`DELETE /api/v1/templates/guilds/{template_id}`**
    - **Purpose:** Delete a specific Guild Structure Template.
    - **Response:** HTTP 204 No Content.
    - *Status: Implemented.*
- **`POST /api/v1/templates/guilds/`**
    - **Purpose:** Create a new Guild Structure Template (e.g., from scratch or referencing a source).
    - *Status: Not Implemented.*

**B. Guild-Specific Template Operations (`/guilds/{guild_id}/template`)**

*Controller: `GuildTemplateController` (Uses `router`)*

- **`GET /guilds/{guild_id}/template`**
    - **Purpose:** Get the specific Guild Structure Template associated with this guild (if one exists).
    - **Response:** `GuildTemplateResponseSchema` (detailed structure).
    - *Status: Exists.*
- **`POST /guilds/{guild_id}/template/save-as`**
    - **Purpose:** Create a new Guild Structure Template by snapshotting the structure of the specified guild.
    - **Input:** `GuildTemplateCreateSchema` (template name, description).
    - **Response:** HTTP 201 Created.
    - *Status: Exists.*

### Home Overview (`/home`)

Endpoints for the main dashboard/homepage.

- **`GET /home/stats`**: Get overview statistics.

### System (`/system`)

Endpoints for system status and health checks.

- **`GET /system/status`**: Get system health (CPU, memory, disk).
- **`GET /system/ping`**: Simple ping endpoint.

### Owner Controls (`/owner`)

Endpoints restricted to the application owner.

- **General Owner (`/owner`)**
    - `GET /status`: Get detailed system status.
    - `POST /maintenance`: Toggle maintenance mode.
    - `POST /backup`: Create system backup.
- **Bot Control (`/owner/bot`)**
    - `POST /start`, `/stop`, `/restart`: Control the Discord bot process (Not Implemented).
    - `GET /status`: Get bot status (Not Implemented).
    - `GET /config`, `PUT /config`: Manage bot configuration (Not Implemented).
- **Bot Logger (`/owner/bot/logger`)**
    - `GET /logs`: Fetch logs from the internal bot API.
- **Server Management (`/owner/servers`)**
    - `GET /`: Legacy endpoint? Get list of servers (approved status only).
    - `GET /manageable`: Get list of ALL servers for management UI.
    - `GET /{server_id}`: Get details of a specific server.
    - `POST /{server_id}/access`: Update server access status (approve, reject, etc.).
    - `POST /{server_id}/restart`, `/stop`, `/start`: Control server process (Not Implemented).
    - `GET /{server_id}/status`: Get server status (Not Implemented).

### Admin Controls

Endpoints restricted to administrators (potentially subset of owner).

- **General Admin (`/admin`)**
    - `GET /users`: Get all users.
    - `GET /guilds`: Get all guilds.
    - `GET /system`: Get system info.
    - `POST /maintenance`: Toggle maintenance mode.
- **User Management (`/users`)**
    - `GET /`: List all users (Appears redundant with `GET /admin/users` unless different filtering applies).
    - `GET /{user_id}`: Get specific user details.
    - `POST /{user_id}/roles`: Update user's app-wide roles.
    - `DELETE /{user_id}`: Delete a user.

### Debug (`/debug`)

Endpoints for debugging purposes.

- `GET /error`: Test error handling.
- `GET /auth-test`: Test authentication dependency.
- `GET /db-test`: Test database connection.
- `GET /log-test`: Test logging.
