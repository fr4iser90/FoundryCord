# 5. API Specification

This document provides a high-level overview of the FoundryCord REST API, which serves as the primary interface for the frontend web application and any external clients. It details how to access the auto-generated interactive documentation, outlines key endpoint groups, and explains authentication and authorization mechanisms.

## Overview

*   **Framework:** FastAPI
*   **Specification:** OpenAPI 3.x
*   **Authentication:** Session Cookies (Set after successful OAuth2 flow, likely with Discord).

## API Documentation Link

The detailed, auto-generated API documentation (Swagger UI / ReDoc) can be found at:

*   **Swagger UI:** `/docs` (relative to the application root URL, e.g., `http://localhost:8000/docs`)
*   **ReDoc:** `/redoc` (relative to the application root URL, e.g., `http://localhost:8000/redoc`)

*Please refer to the live, interactive API documentation linked above for definitive information on all endpoints, request/response Pydantic schemas, parameters, and exact tags used in the OpenAPI schema. The explanations below provide a conceptual guide.*

## Key API Endpoints / Tag Groups & Domain Relevance

Listed below are the main functional groups (tags) of the API, typically corresponding to controllers in `app/web/interfaces/api/rest/v1/`. Each group serves distinct domain use cases:

*   **Auth (`auth_controller.py`):**
    *   **Endpoints:** `/auth/login`, `/auth/callback`, `/auth/logout`, `/auth/me`.
    *   **Domain Relevance:** Manages user authentication via OAuth2 (likely with Discord), session creation, and retrieval of the current authenticated user\'s details. Relies on `AuthenticationService` and `SessionRepository` (from `app/shared/`).

*   **Guilds (various controllers under `guild/`):**
    *   **Domain Relevance:** Facilitates all guild-related operations, from selecting a guild to managing its configuration and designing its structure using templates. These endpoints heavily interact with `GuildService`, `TemplateService`, `GuildConfigService`, and related repositories.
    *   **Sub-Groups (Examples):**
        *   *Guild Selection (`guild_selector_controller.py`):* Allows users to list and select the active guild they are managing.
        *   *Guild Admin (`guild/admin/*_controller.py`):* Provides endpoints for guild administrators to manage users within the guild context of FoundryCord and configure guild-specific settings.
        *   *Guild Template Designer (`guild_template_controller.py`, `structure_controller.py`, etc.):* Core of the Guild Designer feature. Endpoints for creating, reading, updating, deleting, and applying guild templates. Also handles import/export or sharing of templates.

*   **Dashboards (various controllers under `dashboards/`):**
    *   **Domain Relevance:** Manages the creation, configuration, and data retrieval for custom web dashboards. Interacts with `DashboardConfigurationService`, `DashboardComponentService`, and UI layout services.
    *   **Endpoints (Examples):** CRUD for dashboard configurations, CRUD for dashboard components/widgets, retrieving data for dashboard widgets.

*   **UI Layouts (`ui/layout_controller.py`):**
    *   **Domain Relevance:** Allows users to save and load their personalized UI layout configurations, particularly for draggable/resizable dashboard elements (e.g., Gridstack). Utilizes `UILayoutService` and `UILayoutRepository`.
    *   **Endpoints:** `POST /ui/layouts`, `GET /ui/layouts/{page_identifier}`.

*   **Owner (various controllers under `owner/`):**
    *   **Domain Relevance:** Provides superuser-level control over the FoundryCord application, including bot lifecycle management, viewing system logs, managing all guilds/users, and accessing system-wide monitoring or state snapshots. These endpoints are heavily restricted and interact with various core services.
    *   **Endpoints (Examples):** Bot control (start/stop/restart signals), log viewing, global guild management, system state monitoring.

*   **System (`system/health_controller.py`):**
    *   **Domain Relevance:** Offers general system-level information, primarily health checks used for monitoring the API\'s operational status.
    *   **Endpoints:** `/system/health`.

*   **Home (`home/overview_controller.py`):**
    *   **Domain Relevance:** Provides data for the main landing page or user overview dashboard after login, potentially aggregating key information or statistics.

*   **Debug (`debug/debug_controller.py`):**
    *   **Domain Relevance:** Contains endpoints specifically for debugging purposes during development. These should not be enabled or accessible in a production environment.

## WebSocket API

*   **Current Status:** FoundryCord does **not** currently utilize WebSocket APIs for client-server communication.
*   **Future Consideration:** WebSocket support was considered (e.g., for real-time log streaming in the `BotLoggerController`) and might be implemented in the future if specific real-time, bidirectional communication needs arise.

## Authentication & Authorization

*   **Authentication:** API requests are primarily authenticated using HTTP Session Cookies managed by the backend. These cookies are typically set after a user successfully completes an OAuth2 authentication flow (e.g., logging in via Discord). Authentication status is checked via middleware (`app/web/core/middleware/authentication.py`) and potentially specific dependencies.
*   **Authorization:** Role-based access control and ownership checks are enforced using FastAPI dependencies (`app/web/interfaces/api/rest/dependencies/auth_dependencies.py`). These dependencies utilize shared authorization services (`app/shared/domain/services/auth/authorization_service.py`) to verify if the authenticated user has the necessary permissions (e.g., 'owner', 'guild_admin') or ownership of the resource being accessed.

## Error Responses

*   Standard HTTP status codes are used for errors (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error).
*   Error responses generally follow the FastAPI default format, often `{"detail": "Error message string or object"}`. Specific validation errors (422) might provide more detailed information about invalid fields. 