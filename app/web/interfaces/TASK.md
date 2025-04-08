# Route Analysis

## Current Structure Examples
```
/api/v1/servers/list         -> JSON Response
/api/v1/auth/login          -> JSON Response
/api/v1/owner/bot/status    -> JSON Response

/servers                    -> HTML Template
/auth/login                -> HTML Template
/owner/bot                 -> HTML Template
```

## API Controllers Analysis

### 1. auth_controller.py
- **Type**: API (JSON Responses)
- **Current Prefix**: `/api/v1/auth`
- **Routes**:
  - GET `/api/v1/auth/me` -> JSON user info
  - POST `/api/v1/auth/logout` -> JSON status
- **Issues**:
  - ✅ Missing `/api/v1` prefix (FIXED)
  - ✅ Returns proper JSON responses
  - ✅ Clear API functionality

### 2. server_selector_controller.py
- **Type**: API (JSON Responses)
- **Current Prefix**: `/api/v1/servers`
- **Routes**:
  - GET `/api/v1/servers` -> JSON server list
  - GET `/api/v1/servers/current` -> JSON current server
  - POST `/api/v1/servers/select` -> JSON select server
- **Issues**:
  - ✅ Missing `/api` prefix (FIXED)
  - ✅ Returns proper JSON responses
  - ✅ Clear API functionality
  - ✅ Good route structure

### 3. bot_control_controller.py
- **Type**: API (JSON Responses)
- **Current Prefix**: `/api/v1/owner/bot`
- **Routes**:
  - POST `/api/v1/owner/bot/start` -> JSON response
  - POST `/api/v1/owner/bot/stop` -> JSON response
  - POST `/api/v1/owner/bot/restart` -> JSON response
  - GET `/api/v1/owner/bot/config` -> JSON config
  - PUT `/api/v1/owner/bot/config` -> JSON response
  - POST `/api/v1/owner/bot/servers/{guild_id}/join` -> JSON response
  - POST `/api/v1/owner/bot/servers/{guild_id}/leave` -> JSON response
  - GET `/api/v1/owner/bot/status` -> JSON status
  - GET `/api/v1/owner/bot/overview` -> JSON stats
  - POST `/api/v1/owner/bot/workflows/{name}/enable` -> JSON response
  - POST `/api/v1/owner/bot/workflows/{name}/disable` -> JSON response
- **Issues**:
  - ✅ Missing `/api` prefix (FIXED)
  - ✅ Returns proper JSON responses
  - ✅ Clear API functionality
  - ✅ Good route structure

### 4. owner_controller.py
- **Type**: API (JSON Responses)
- **Current Prefix**: `/api/v1/owner`
- **Routes**:
  - GET `/api/v1/owner/servers` -> JSON server list
  - POST `/api/v1/owner/servers/add` -> JSON response
  - DELETE `/api/v1/owner/servers/{guild_id}` -> JSON response
  - GET `/api/v1/owner/bot/config` -> JSON config
  - POST `/api/v1/owner/bot/config` -> JSON response
  - GET `/api/v1/owner/logs` -> JSON logs
  - POST `/api/v1/owner/logs/clear` -> JSON response
- **Issues**:
  - ✅ Missing `/api` prefix (FIXED)
  - ✅ Returns proper JSON responses
  - ✅ Clear API functionality
  - ✅ Good route structure

## Web Views Analysis

### 1. server_selector_view.py
- **Type**: Web View (HTML Responses)
- **Current Prefix**: `/servers`
- **Routes**:
  - GET `/servers/select` -> HTML template
- **Issues**:
  - ✅ Web View returning JSON responses (FIXED)
  - ✅ Using API prefix in web view (FIXED)
  - ✅ Functionality duplicates server_selector_controller.py (FIXED)
  - ✅ No HTML templates being rendered (FIXED)

### 2. auth_view.py
- **Type**: Web View (HTML Responses)
- **Current Prefix**: `/auth`
- **Routes**:
  - GET `/auth/login` -> HTML login page
  - GET `/auth/callback` -> OAuth redirect
  - GET `/auth/logout` -> HTML logout + redirect
  - GET `/auth/discord-login` -> Discord OAuth redirect
- **Issues**:
  - ✅ Proper HTML responses
  - ✅ Clear web view functionality
  - ✅ Good route structure
  - ✅ No API functionality mixed in

### 3. bot_control_view.py
- **Type**: Web View (HTML Responses)
- **Current Prefix**: `/bot`
- **Routes**:
  - GET `/bot/control` -> HTML template
  - GET `/bot/overview` -> HTML template
  - GET `/bot/config` -> HTML template
- **Issues**:
  - ✅ Mixing HTML and JSON responses in same view (FIXED)
  - ✅ API routes should be in bot_control_controller.py (FIXED)
  - ✅ Duplicates functionality from bot_control_controller.py (FIXED)
  - ✅ HTML template route is correct

### 4. owner_view.py
- **Type**: Web View (HTML Responses)
- **Current Prefix**: `/owner`
- **Routes**:
  - GET `/owner/bot-control` -> HTML template
  - GET `/owner/permissions` -> HTML template
  - GET `/owner/logs` -> HTML template
- **Issues**:
  - ✅ Proper HTML responses
  - ✅ Clear web view functionality
  - ✅ Good route structure
  - ✅ Correctly uses API endpoints for data

### 5. bot_public_controller.py
- **Type**: API (JSON Responses)
- **Current Prefix**: `/api/v1/bot-public-info`
- **Routes**:
  - GET `/api/v1/bot-public-info/status` -> JSON status
  - GET `/api/v1/bot-public-info/servers` -> JSON server info
  - GET `/api/v1/bot-public-info/system-resources` -> JSON resources
  - GET `/api/v1/bot-public-info/recent-activities` -> JSON activities
  - GET `/api/v1/bot-public-info/popular-commands` -> JSON commands
- **Issues**:
  - ✅ Missing `/api` prefix (FIXED)
  - ✅ Returns proper JSON responses
  - ✅ Clear API functionality
  - ✅ Good route structure

### 6. debug_view.py
- **Type**: Web View (HTML Responses)
- **Current Prefix**: `/debug`
- **Routes**:
  - GET `/debug` -> HTML template
  - GET `/debug/add-test-guild-form` -> HTML template
- **Issues**:
  - ✅ Mixing HTML and JSON responses in same view (FIXED)
  - ✅ Debug API endpoints should be in separate controller (FIXED)
  - ✅ HTML template routes are correct

### 7. guild_user_management_view.py
- **Type**: Web View (HTML Responses)
- **Current Prefix**: `/guilds/users`
- **Routes**:
  - GET `/guilds/users` -> HTML template
- **Issues**:
  - ✅ Mixing HTML and JSON responses in same view (FIXED)
  - ✅ User management API endpoints should be in separate controller (FIXED)
  - ✅ HTML template route is correct

### 8. admin/user_management_view.py
- **Type**: Web View (HTML Responses)
- **Current Prefix**: `/admin/users`
- **Routes**:
  - GET `/admin/users` -> HTML template
  - GET `/admin/users/edit/{user_id}` -> HTML template
- **Issues**:
  - ✅ Mixing HTML and JSON responses in same view (FIXED)
  - ✅ User management API endpoints moved to controller (FIXED)
  - ✅ HTML template routes are correct
  - ✅ Uses API controller for data operations

## Required Changes
