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
- **Current Prefix**: `/auth`
- **Routes**:
  - GET `/auth/me` -> JSON user info
  - POST `/auth/logout` -> JSON status
- **Issues**:
  - ❌ Missing `/api/v1` prefix
  - ✅ Returns proper JSON responses
  - ✅ Clear API functionality

### 2. server_selector_controller.py
- **Type**: API (JSON Responses)
- **Current Prefix**: `/v1/servers`
- **Routes**:
  - GET `/v1/servers` -> JSON server list
  - GET `/v1/servers/current` -> JSON current server
  - POST `/v1/servers/select` -> JSON select server
- **Issues**:
  - ❌ Missing `/api` prefix
  - ✅ Returns proper JSON responses
  - ✅ Clear API functionality
  - ✅ Good route structure

### 3. bot_control_controller.py
- **Type**: API (JSON Responses)
- **Current Prefix**: `/v1/owner/bot`
- **Routes**:
  - POST `/v1/owner/bot/start` -> JSON response
  - POST `/v1/owner/bot/stop` -> JSON response
  - POST `/v1/owner/bot/restart` -> JSON response
  - GET `/v1/owner/bot/config` -> JSON config
  - PUT `/v1/owner/bot/config` -> JSON response
  - POST `/v1/owner/bot/servers/{guild_id}/join` -> JSON response
  - POST `/v1/owner/bot/servers/{guild_id}/leave` -> JSON response
  - GET `/v1/owner/bot/status` -> JSON status
  - GET `/v1/owner/bot/overview` -> JSON stats
  - POST `/v1/owner/bot/workflows/{name}/enable` -> JSON response
  - POST `/v1/owner/bot/workflows/{name}/disable` -> JSON response
- **Issues**:
  - ❌ Missing `/api` prefix
  - ✅ Returns proper JSON responses
  - ✅ Clear API functionality
  - ✅ Good route structure

### 4. owner_controller.py
- **Type**: API (JSON Responses)
- **Current Prefix**: `/v1/owner`
- **Routes**:
  - GET `/v1/owner/servers` -> JSON server list
  - POST `/v1/owner/servers/add` -> JSON response
  - DELETE `/v1/owner/servers/{guild_id}` -> JSON response
  - GET `/v1/owner/bot/config` -> JSON config
  - POST `/v1/owner/bot/config` -> JSON response
  - GET `/v1/owner/logs` -> JSON logs
  - POST `/v1/owner/logs/clear` -> JSON response
- **Issues**:
  - ❌ Missing `/api` prefix
  - ✅ Returns proper JSON responses
  - ✅ Clear API functionality
  - ✅ Good route structure

## Web Views Analysis

### 1. server_selector_view.py
- **Type**: Should be Web View but currently acts as API
- **Current Prefix**: `/api/servers`
- **Routes**:
  - GET `/api/servers/list` -> JSON server list
  - POST `/api/servers/switch/{guild_id}` -> JSON response
- **Issues**:
  - ❌ Web View returning JSON responses
  - ❌ Using API prefix in web view
  - ❌ Functionality duplicates server_selector_controller.py
  - ❌ No HTML templates being rendered

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
- **Type**: Mixed Web View and API
- **Current Prefix**: `/owner/bot`
- **Routes**:
  - GET `/owner/bot` -> HTML template (✅)
  - POST `/owner/bot/start` -> JSON response (❌)
  - POST `/owner/bot/stop` -> JSON response (❌)
  - POST `/owner/bot/restart` -> JSON response (❌)
  - POST `/owner/bot/servers/add` -> JSON response (❌)
  - DELETE `/owner/bot/servers/{guild_id}` -> JSON response (❌)
  - GET `/owner/bot/servers` -> JSON response (❌)
  - GET `/owner/bot/config` -> JSON response (❌)
  - POST `/owner/bot/servers/{guild_id}/join` -> JSON response (❌)
  - POST `/owner/bot/servers/{guild_id}/leave` -> JSON response (❌)
  - POST `/owner/bot/servers/{guild_id}/access` -> JSON response (❌)
- **Issues**:
  - ❌ Mixing HTML and JSON responses in same view
  - ❌ API routes should be in bot_control_controller.py
  - ❌ Duplicates functionality from bot_control_controller.py
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
- **Current Prefix**: `/v1/bot-public-info`
- **Routes**:
  - GET `/v1/bot-public-info/status` -> JSON status
  - GET `/v1/bot-public-info/servers` -> JSON server info
  - GET `/v1/bot-public-info/system-resources` -> JSON resources
  - GET `/v1/bot-public-info/recent-activities` -> JSON activities
  - GET `/v1/bot-public-info/popular-commands` -> JSON commands
- **Issues**:
  - ❌ Missing `/api` prefix
  - ✅ Returns proper JSON responses
  - ✅ Clear API functionality
  - ✅ Good route structure

### 6. debug_view.py
- **Type**: Mixed Web View and API
- **Current Prefix**: `/debug`
- **Routes**:
  - GET `/debug` -> HTML template (✅)
  - GET `/debug/guilds` -> JSON response (❌)
  - GET `/debug/add-test-guild-form` -> HTML template (✅)
  - POST `/debug/add-test-guild` -> JSON response (❌)
  - GET `/debug/db-status` -> JSON response (❌)
  - POST `/debug/add-test-guild-with-details` -> JSON response (❌)
  - GET `/debug/check-schema` -> JSON response (❌)
- **Issues**:
  - ❌ Mixing HTML and JSON responses in same view
  - ❌ Debug API endpoints should be in separate controller
  - ✅ HTML template routes are correct

### 7. guild_user_management_view.py
- **Type**: Mixed Web View and API
- **Current Prefix**: `/guilds/users`
- **Routes**:
  - GET `/guilds/users` -> HTML template (✅)
  - GET `/guilds/users/{user_id}` -> JSON response (❌)
  - PUT `/guilds/users/{user_id}/role` -> JSON response (❌)
  - PUT `/guilds/users/{user_id}/app-role` -> JSON response (❌)
  - POST `/guilds/users/{user_id}/kick` -> JSON response (❌)
- **Issues**:
  - ❌ Mixing HTML and JSON responses in same view
  - ❌ User management API endpoints should be in separate controller
  - ✅ HTML template route is correct

## Required Changes
1. auth_controller.py:
   - Change router prefix from `/auth` to `/api/v1/auth`
   - Update any frontend JavaScript calls to match new routes

2. server_selector_controller.py:
   - Change router prefix from `/v1/servers` to `/api/v1/servers`
   - Update any frontend JavaScript calls to match new routes

3. server_selector_view.py:
   - Move JSON endpoints to server_selector_controller.py
   - Create proper HTML template for server selector
   - Change to render HTML template instead of returning JSON
   - Remove `/api` prefix from routes
   - Update frontend JavaScript to use API endpoints instead

4. auth_view.py:
   - ✅ No changes needed - already follows correct pattern

5. bot_control_view.py:
   - Move all JSON endpoints to bot_control_controller.py
   - Keep only HTML template rendering
   - Update frontend JavaScript to use API endpoints
   - Remove duplicate API functionality

6. bot_control_controller.py:
   - Change router prefix from `/v1/owner/bot` to `/api/v1/owner/bot`
   - Update any frontend JavaScript calls to match new routes

7. owner_controller.py:
   - Change router prefix from `/v1/owner` to `/api/v1/owner`
   - Update any frontend JavaScript calls to match new routes

8. owner_view.py:
   - ✅ No changes needed - already follows correct pattern

9. bot_public_controller.py:
   - Change router prefix from `/v1/bot-public-info` to `/api/v1/bot-public-info`
   - Update any frontend JavaScript calls to match new routes

10. debug_view.py:
    - Create new debug_controller.py for API endpoints
    - Move all JSON endpoints to debug_controller.py
    - Keep only HTML template rendering in view
    - Update frontend JavaScript to use API endpoints

11. guild_user_management_view.py:
    - Create new guild_user_management_controller.py for API endpoints
    - Move all JSON endpoints to the new controller
    - Keep only HTML template rendering in view
    - Update frontend JavaScript to use API endpoints

## Implementation Order
1. First fix all API routes to have proper `/api/v1` prefix
2. Then create new controllers for mixed views
3. Move JSON endpoints to appropriate controllers
4. Update frontend JavaScript to use new API routes
5. Clean up views to only render HTML templates

Would you like me to start implementing these changes in a specific order?