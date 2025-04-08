# Web Interface Architecture

## Overview

The web interface is split into two main parts:
1. API Interface (`/api`) - For JSON/REST communication
2. Web Interface (`/web`) - For HTML page rendering

## Directory Structure

```
app/web/interfaces/
├── api/                    # API Interface (JSON/REST)
│   └── rest/v1/           # API Version 1
│       ├── auth/          # Authentication API
│       ├── bot/           # Bot Public API
│       ├── owner/         # Owner-only API
│       └── server/        # Server Management API
└── web/                   # Web Interface (HTML)
    └── views/             # Web Views (Templates)
        ├── admin/         # Admin Pages
        ├── auth/          # Auth Pages
        ├── bot/           # Bot Control Pages
        └── owner/         # Owner Pages
```

## Component Responsibilities

### API Controllers (`/api/rest/v1/`)
- Return ONLY JSON responses
- Handle data processing and business logic
- No HTML rendering
- Used by:
  - Frontend JavaScript (AJAX)
  - External API consumers
  - Mobile apps

Example:
```python
@router.get("/api/v1/servers")
async def list_servers():
    return {"servers": [...]}  # JSON
```

### Web Views (`/web/views/`)
- Return ONLY HTML responses
- Render templates
- Handle page structure and navigation
- Use API controllers for data
- No direct database access

Example:
```python
@router.get("/servers")
async def server_page():
    return templates.TemplateResponse("servers.html", {...})  # HTML
```

## Route Patterns

### API Routes
- All under `/api/v1/`
- Return JSON
- Examples:
  - `/api/v1/auth/login`
  - `/api/v1/servers/list`
  - `/api/v1/owner/bot/status`

### Web Routes
- Direct paths without prefix
- Return HTML
- Examples:
  - `/auth/login`
  - `/servers`
  - `/owner/bot`

## Component Types

### Controllers
1. **Auth Controllers**
   - `auth_controller.py` - Authentication and user management
   - Handles: login, logout, user info

2. **Bot Controllers**
   - `bot_control_controller.py` - Bot management (owner only)
   - `bot_public_controller.py` - Public bot information
   - Handles: start/stop bot, status, configuration

3. **Server Controllers**
   - `server_selector_controller.py` - Server selection and management
   - Handles: list servers, switch active server

4. **Owner Controllers**
   - `owner_controller.py` - Owner-specific functionality
   - Handles: system logs, server approvals

### Views
1. **Auth Views**
   - `auth_view.py` - Login pages and OAuth flow
   - Renders: login form, OAuth callback

2. **Bot Views**
   - `bot_control_view.py` - Bot control interface
   - `bot_stats_view.py` - Bot statistics pages
   - Renders: control panel, statistics

3. **Server Views**
   - `server_selector_view.py` - Server selection interface
   - Renders: server list, selector dropdown

4. **Owner Views**
   - `owner_view.py` - Owner control panel
   - Renders: system management pages

## Best Practices

1. **Separation of Concerns**
   - Controllers handle data and logic
   - Views handle presentation
   - No mixing of responsibilities

2. **Route Consistency**
   - API routes always under `/api/v1/`
   - Web routes at root level
   - Clear naming conventions

3. **Response Types**
   - API returns only JSON
   - Views return only HTML
   - No mixing of response types

4. **Data Flow**
   - Views call API controllers for data
   - No direct database access in views
   - Clean separation of layers

## Common Issues to Avoid

1. **Mixed Responsibilities**
   - ❌ Views returning JSON responses
   - ❌ Controllers rendering HTML
   - ✅ Keep clear separation

2. **Inconsistent Routes**
   - ❌ API routes without `/api/v1/` prefix
   - ❌ Mixed prefixes in same component
   - ✅ Follow route patterns

3. **Duplicate Logic**
   - ❌ Same functionality in multiple places
   - ❌ Database access in views
   - ✅ Reuse API controllers
