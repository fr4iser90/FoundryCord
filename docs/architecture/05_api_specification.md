# 5. API Specification

## Overview

This document provides a high-level overview of the REST API.

*   **Framework:** FastAPI
*   **Specification:** OpenAPI 3.x
*   **Authentication:** Session Cookies (Set after successful OAuth2 flow, likely with Discord).

## API Documentation Link

The detailed, auto-generated API documentation (Swagger UI / ReDoc) can be found at:

*   **Swagger UI:** `/docs` (relative to the application root URL)
*   **ReDoc:** `/redoc` (relative to the application root URL)

*Please refer to the links above for detailed information on all endpoints, request/response schemas, parameters, and exact tags used in the OpenAPI schema.*

## Key API Endpoints / Tag Groups

List the main functional groups (tags) of the API, based on controller structure in `app/web/interfaces/api/rest/v1/`:

*   **Auth:** Handles user login (`/auth/login`, `/auth/callback`), logout (`/auth/logout`), and session status (`/auth/me`). Controller: `auth/auth_controller.py`.
*   **Guilds:** Endpoints related to specific guilds. This might be further broken down by sub-tags in the actual API docs:
    *   *Guild Selection:* (`guild/selector/guild_selector_controller.py`)
    *   *Guild Admin:* User management, configuration (`guild/admin/*_controller.py`).
    *   *Guild Template Designer:* Loading, saving, activating templates (`guild/designer/guild_template_controller.py`, covering both specific and general template operations).
*   **UI Layouts:** Saving and loading user-specific UI layouts (e.g., Gridstack). Controller: `ui/layout_controller.py`.
*   **Owner:** Endpoints restricted to the application owner(s) for managing the bot, guilds, monitoring, etc. Controllers: `owner/*_controller.py`.
*   **System:** General system endpoints like health checks. Controller: `system/health_controller.py`.
*   **Home:** Endpoints for the main dashboard/overview page. Controller: `home/overview_controller.py`.
*   **Debug:** Endpoints for debugging purposes (likely development only). Controller: `debug/debug_controller.py`.

## Authentication & Authorization

*   **Authentication:** API requests are primarily authenticated using HTTP Session Cookies managed by the backend. These cookies are typically set after a user successfully completes an OAuth2 authentication flow (e.g., logging in via Discord). Authentication status is checked via middleware (`app/web/core/middleware/authentication.py`) and potentially specific dependencies.
*   **Authorization:** Role-based access control and ownership checks are enforced using FastAPI dependencies (`app/web/interfaces/api/rest/dependencies/auth_dependencies.py`). These dependencies utilize shared authorization services (`app/shared/domain/services/auth/authorization_service.py`) to verify if the authenticated user has the necessary permissions (e.g., 'owner', 'guild_admin') or ownership of the resource being accessed.

## Error Responses

*   Standard HTTP status codes are used for errors (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error).
*   Error responses generally follow the FastAPI default format, often `{"detail": "Error message string or object"}`. Specific validation errors (422) might provide more detailed information about invalid fields. 