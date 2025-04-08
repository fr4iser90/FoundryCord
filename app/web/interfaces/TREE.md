# Current vs. Desired Structure

## Current Structure
```
app/web/interfaces/
├── api/
│   └── rest/v1/
│       ├── auth/           # Auth API
│       ├── bot/           # Bot Public API
│       ├── dashboard/     # Dashboard API
│       ├── guild/         # Guild Config API
│       ├── owner/         # Owner API
│       ├── server/        # Server API
│       └── system/        # System Health API
└── web/
    └── views/
        ├── admin/         # Admin Views
        ├── auth/          # Auth Views
        ├── bot/           # Bot Views
        ├── debug/         # Debug Views
        ├── guilds/        # Guild Views
        ├── home/          # Home Views
        ├── main/          # Main Views
        ├── navbar/        # Navigation Views
        └── owner/         # Owner Views
```

## Missing API Controllers
We need to create these new API controllers:

1. `/api/rest/v1/debug/`
   - `debug_controller.py` - Move debug endpoints from debug_view.py

2. `/api/rest/v1/guild/users/`
   - `guild_user_management_controller.py` - Move user management endpoints

3. `/api/rest/v1/admin/`
   - `admin_controller.py` - Move admin endpoints

## Required Moves

### 1. Debug Functionality
- Move from: `web/views/debug/debug_view.py`
- To: `api/rest/v1/debug/debug_controller.py`
- Keep only HTML rendering in debug_view.py

### 2. Guild User Management
- Move from: `web/views/guilds/user_management_view.py`
- To: `api/rest/v1/guild/users/guild_user_management_controller.py`
- Keep only HTML rendering in user_management_view.py

### 3. Server Selection
- Move from: `web/views/navbar/server_selector_view.py`
- Already have: `api/rest/v1/server/server_selector_controller.py`
- Update view to use controller

### 4. Bot Control
- Move from: `web/views/owner/bot_control_view.py`
- Already have: `api/rest/v1/owner/bot_control_controller.py`
- Update view to use controller

## Final Structure
```
app/web/interfaces/
├── api/
│   └── rest/v1/
│       ├── admin/         # Admin API
│       ├── auth/          # Auth API
│       ├── bot/           # Bot API
│       ├── dashboard/     # Dashboard API
│       ├── debug/         # Debug API
│       ├── guild/         # Guild API
│       │   └── users/     # Guild User Management
│       ├── owner/         # Owner API
│       ├── server/        # Server API
│       └── system/        # System Health API
└── web/
    └── views/            # All views ONLY render HTML
        ├── admin/        # Admin pages
        ├── auth/         # Auth pages
        ├── bot/          # Bot pages
        ├── debug/        # Debug pages
        ├── guild/       # Guild pages
        ├── home/         # Home pages
        ├── main/         # Main pages
        ├── navbar/       # Navigation components
        └── owner/        # Owner pages
```

## Implementation Steps

1. Create new API controller directories:
   ```bash
   mkdir -p app/web/interfaces/api/rest/v1/{debug,admin}
   mkdir -p app/web/interfaces/api/rest/v1/guild/users
   ```

2. Create new controller files:
   ```bash
   touch app/web/interfaces/api/rest/v1/debug/debug_controller.py
   touch app/web/interfaces/api/rest/v1/guild/users/guild_user_management_controller.py
   touch app/web/interfaces/api/rest/v1/admin/admin_controller.py
   ```

3. Move API functionality from views to controllers
4. Update views to use API controllers
5. Update frontend JavaScript to use new API endpoints

