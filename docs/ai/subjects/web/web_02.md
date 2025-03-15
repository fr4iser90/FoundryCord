
# Web Interface Implementation Guide

## Overview

This document outlines the implementation strategy for a user-friendly web interface that allows end-users to build customized dashboards. The system will authenticate users via Discord, store dashboard configurations in the database, and enable the bot to render these dashboards within Discord.

## Key Components

1. **Discord OAuth Authentication**
   - JWT-based authentication flow
   - User identity verification through Discord
   - Role-based access control aligned with Discord bot roles

2. **Web UI Dashboard Builder**
   - Drag-and-drop interface for dashboard creation
   - Component library with monitoring widgets, charts, and controls
   - Layout management with responsive design options

+-----------------------------------------------------------------------------------+
| [🏠 Menü]   [📂 Projekte]    [⚙️ Einstellungen]   [🔄 Refresh]   [👤 User]  |
+-----------------------------------------------------------------------------------+
|  [📂 Komponenten]   |    🖥 Arbeitsfläche      |  🛠 Eigenschaften / Templates  |
|  [📊 Charts]       |    [Widget 1]            |  [Name: Widget 1]              |
|  [📈 Graphen]      |    [Widget 2]            |  [Farbe: Blau]                 |
|  [🔧 Controls]     |    [Widget 3]            |  [Größe: 300px]                |
|  [🖼 Bilder]       |    [Drag & Drop Bereich] |  [Datenquelle]                 |
+-----------------------------------------------------------------------------------+


3. **Dashboard Configuration Storage**
   - Database schema for storing dashboard definitions
   - Version control for dashboard configurations
   - User preferences and settings storage

4. **Bot Integration Layer**
   - Configuration retrieval from app.bot.database
   - Dashboard rendering in Discord channels
   - Real-time updates when configurations change

5. **API Services**
   - RESTful endpoints for dashboard operations
   - WebSocket connections for real-time updates
   - Integration with existing monitoring collectors

## Implementation Steps

### Phase 1: Authentication System
1. Implement Discord OAuth flow
2. Create JWT token generation and validation
3. Develop user session management
4. Set up role-based permissions synced with Discord

### Phase 2: Web Interface Development
1. Build core dashboard builder components
2. Implement drag-and-drop functionality
3. Create widget library with visualization options
4. Develop dashboard preview functionality

### Phase 3: Database Integration
1. Design schema for dashboard configurations
2. Implement CRUD operations for dashboards
3. Create migration path for existing dashboards
4. Add versioning and backup capabilities

### Phase 4: Bot Integration
1. Create dashboard retrieval service in bot
2. Develop rendering engine for Discord output
3. Implement real-time update subscriptions
4. Add dashboard command handlers

## Discord Authentication Implementation

The authentication flow should:

1. Redirect users to Discord OAuth
2. Receive authorization code and exchange for tokens
3. Validate user identity and server membership
4. Generate JWT tokens for session management

### Implementation Details
```python
# infrastructure/web/auth/discord_auth_service.py
class DiscordAuthService:
    """Handles Discord OAuth authentication and JWT token management."""
    
    def __init__(self, config_service, jwt_service):
        self.config = config_service
        self.jwt_service = jwt_service
        self.discord_api_client = DiscordAPIClient()
        
    async def get_oauth_url(self, redirect_uri):
        """Generate Discord OAuth URL with appropriate scopes."""
        client_id = self.config.get("DISCORD_BOT_TOKEN")
        return f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify%20guilds"
        
    async def exchange_code(self, code, redirect_uri):
        """Exchange authorization code for access token."""
        token_data = await self.discord_api_client.exchange_code(
            code=code,
            client_id=self.config.get("DISCORD_BOT_TOKEN"),
            client_secret=self.config.get("DISCORD_BOT_SECRET"),
            redirect_uri=redirect_uri
        )
        return token_data
        
    async def get_user_data(self, access_token):
        """Retrieve user data from Discord API."""
        return await self.discord_api_client.get_current_user(access_token)
        
    async def create_jwt_token(self, user_data, guild_memberships):
        """Create JWT token with user information and permissions."""
        payload = {
            "sub": user_data["id"],
            "name": user_data["username"],
            "avatar": user_data["avatar"],
            "guilds": [g["id"] for g in guild_memberships],
            "permissions": await self._calculate_permissions(user_data["id"], guild_memberships)
        }
        return self.jwt_service.generate_token(payload)
        
    async def _calculate_permissions(self, user_id, guild_memberships):
        """Calculate user permissions based on Discord roles."""
        # Implementation details
```

## Dashboard Builder UI Components

The web UI should include:

1. Component palette with drag-and-drop widgets
2. Layout grid for positioning elements
3. Properties panel for configuring widgets
4. Template library for quick starts
5. Preview mode showing Discord rendering

## Database Schema Design

```sql
CREATE TABLE dashboards (
    id UUID PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    layout JSONB NOT NULL,
    owner_id VARCHAR(20) NOT NULL,
    guild_id VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    version INT NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE dashboard_widgets (
    id UUID PRIMARY KEY,
    dashboard_id UUID REFERENCES dashboards(id),
    widget_type VARCHAR(50) NOT NULL,
    config JSONB NOT NULL,
    position JSONB NOT NULL,
    title VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE user_preferences (
    user_id VARCHAR(20) PRIMARY KEY,
    preferences JSONB NOT NULL DEFAULT '{}'
);
```

## Benefits

1. **User Empowerment**: End users can create dashboards without coding knowledge
2. **Flexibility**: Wide range of visualization and layout options
3. **Integration**: Seamless connection between web UI and Discord bot
4. **Consistency**: Standardized approach to dashboard creation and rendering
5. **Scalability**: Database-driven approach supports large numbers of dashboards

## Additional Recommendations

1. **Implement caching** for frequently accessed dashboards
2. **Add template galleries** for common use cases
3. **Create sharable dashboards** between Discord servers
4. **Develop dashboard analytics** to track usage
5. **Build export/import functionality** for backup and migration