# Web Application Internals & Core Components

This document delves into the internal workings of selected core components and workflows within the FoundryCord Web Application (`app/web/`), including its interaction with frontend static assets (`static/`, `templates/`). It builds upon the foundational understanding provided by the [Web Application Structure](./web_structure.md) document and aims to clarify responsibilities, collaborations, and complex interactions.

## Key Application Services (`app/web/application/services/`)

Web application services encapsulate the business logic for use cases initiated via the web interface (API calls or page requests). They orchestrate shared domain services and repositories.

### 1. Guild Template Management Service (`template/management_service.py` or `template/template_service.py`)
*   **Responsibility:** Handles the creation, updating, and deletion of Guild Templates initiated from the web interface (e.g., Guild Designer). It processes data from API requests, validates it, and uses shared domain services/repositories (`GuildTemplateRepository`, `GuildTemplate` entity) to persist changes.
*   **Collaborators:**
    *   `GuildTemplateRepository` (Shared): For DB operations on templates.
    *   `GuildTemplate` Entity (Shared): Represents the template data.
    *   Potentially `ValidationService` or Pydantic models for input validation.
    *   `AuditService` (Shared): To log template management actions.
*   **Domain Relevance:** Powers the backend logic for the Guild Designer feature, enabling users to save and manage their server structure designs.

### 2. Dashboard Configuration Service (`dashboards/dashboard_configuration_service.py`)
*   **Responsibility:** Manages the configuration of user-customizable web dashboards. This includes saving dashboard layouts, widget selections, and widget-specific settings.
*   **Collaborators:**
    *   `DashboardConfigurationRepository` (Shared): To persist dashboard configs.
    *   `UILayoutRepository` (Shared): To save/load Gridstack layout data associated with dashboards.
    *   `DashboardComponentDefinitionRepository` (Shared): To validate widget types.
*   **Domain Relevance:** Enables the persistence and retrieval of personalized dashboard setups for users.

### 3. Guild Service (`guild/guild_service.py` & `guild/query_service.py`)
*   **Responsibility:** Provides services related to guild information and management from the web perspective. This could include fetching guild lists for selection, retrieving guild-specific configurations or details for display, and potentially administrative actions if not handled by a more specific `GuildManagementService`.
*   **Collaborators:**
    *   `GuildRepository` (Shared): For fetching guild data.
    *   `GuildConfigRepository` (Shared): For guild-specific settings.
    *   `DiscordQueryService` (Bot - if some live data is proxied, or Shared - if direct DB access for bot-populated guild info).
*   **Domain Relevance:** Supports various UI features that require information about Discord guilds linked to the user or system.

## Key API Controllers & View Handlers

### 1. `GuildTemplateController` (`app/web/interfaces/api/rest/v1/guild/designer/guild_template_controller.py`)
*   **Role:** Main API endpoint handler for all Guild Template CRUD (Create, Read, Update, Delete) operations originating from the Guild Designer frontend.
*   **Responsibilities:**
    *   Receives HTTP requests (e.g., `POST` to save, `PUT` to update, `GET` to load, `DELETE` to remove).
    *   Uses Pydantic schemas for request payload validation and response serialization.
    *   Calls `TemplateManagementService` (or similar application service) to perform the actual business logic.
    *   Handles API responses and HTTP status codes.
*   **Key Collaborators:** `TemplateManagementService`, Pydantic Schemas, FastAPI Dependencies (for auth).

### 2. Guild Designer View (`app/web/interfaces/web/views/guild/designer/index_view.py` - example)
*   **Role:** Handles requests for the main Guild Designer page.
*   **Responsibilities:**
    *   Authenticates and authorizes the user.
    *   Fetches any necessary initial data required to render the page (e.g., list of user\'s guilds, available base templates) by calling relevant application services.
    *   Renders the main Jinja2 template for the Guild Designer, passing the fetched data to the template context.
*   **Key Collaborators:** FastAPI (for routing), Jinja2 (for templating), relevant Application Services (e.g., `GuildQueryService`, `TemplateQueryService`).

## Core Web Workflows & Interactions

### Saving a Guild Template from the Designer

This workflow describes the process when a user saves changes to a guild template using the web-based Guild Designer.

*   **Trigger:** User clicks a "Save" or "Update" button in the Guild Designer UI.
*   **Key Steps & Collaborators:** (See sequence diagram below)
    1.  **Frontend (JS):** Gathers the current template data (structure, settings) from the client-side state (e.g., `designerState.js` and jsTree data).
    2.  **API Call:** Frontend JS makes an API call (e.g., `PUT /api/v1/guild-templates/{template_id}`) to the `GuildTemplateController`, sending the template data in the request body.
    3.  **Controller (`GuildTemplateController`):** Receives the request, validates the payload using Pydantic schemas. Injects authenticated user context.
    4.  **Application Service (`TemplateManagementService`):** The controller calls this service with the validated template data and user context.
    5.  **Domain Logic/Persistence:** The service interacts with the `GuildTemplate` aggregate (via `GuildTemplateRepository`) to update the template structure, categories, channels, and permissions in the database.
    6.  **Audit:** Logs the save action via `AuditService`.
    7.  **Response:** The service returns a success/failure status to the controller, which then forms an appropriate HTTP response to the frontend.
    8.  **Frontend (JS):** Receives the API response and updates the UI accordingly (e.g., shows a success notification, clears dirty state).

**Sequence Diagram: Saving Guild Template**

```mermaid
sequenceDiagram
    participant JSDesigner as Frontend JS (Guild Designer)
    participant APIController as GuildTemplateController (Web API)
    participant AppService as TemplateManagementService (Web App)
    participant TemplateRepo as GuildTemplateRepository (Shared)
    participant AuditService as AuditService (Shared)
    participant Database

    JSDesigner->>+APIController: PUT /api/v1/guild-templates/{id} (templateData)
    APIController->>APIController: Validate templateData (Pydantic)
    alt Invalid Data
        APIController-->>-JSDesigner: HTTP 422 Unprocessable Entity
    else Valid Data
        APIController->>+AppService: save_template(user, template_id, validatedData)
        AppService->>+TemplateRepo: get_template_aggregate_by_id(template_id)
        TemplateRepo->>+Database: SELECT template and related data
        Database-->>-TemplateRepo: Existing Template Aggregate
        TemplateRepo-->>-AppService: Existing Template Aggregate
        AppService->>AppService: Update aggregate with validatedData
        AppService->>+TemplateRepo: save_template_aggregate(updatedAggregate)
        TemplateRepo->>+Database: UPDATE/INSERT categories, channels, permissions
        Database-->>-TemplateRepo: Success
        TemplateRepo-->>-AppService: Success
        AppService->>+AuditService: log_event(user, "template_updated", {template_id})
        AuditService-->>-AppService: Logged
        AppService-->>-APIController: SuccessResult
        APIController-->>-JSDesigner: HTTP 200 OK (or updated template data)
    end
```

## Frontend-Backend Interaction Patterns

*   **Data Fetching:** Frontend typically fetches data via `GET` requests to API endpoints on page load or when specific UI components need to refresh.
*   **Data Modification:** User actions that modify data (create, update, delete) trigger `POST`, `PUT`, or `DELETE` requests to the API.
*   **Asynchronous Operations:** All API calls from the frontend are asynchronous (`fetch` API), using `async/await` or Promises to handle responses and update the UI without blocking.
*   **Error Handling:** Frontend JS includes `try...catch` blocks or `.catch()` on Promises to handle API errors (e.g., network issues, 4xx/5xx responses) and display appropriate messages to the user (e.g., via `notifications.js`).
*   **State Updates:** On successful API responses (especially for data modification), the frontend updates its local state and/or re-fetches data to reflect changes in the UI.

Refer to [Frontend Architecture & Design](./frontend_design.md) for client-side JavaScript details and [API Specification](./api_specification.md) for REST API contract details.

## Critical Web-Specific Algorithms & Logic

*(This section can be populated if specific complex algorithms are identified within the web application layer, such as intricate data aggregation for specific views, complex form processing and validation beyond Pydantic, or unique UI rendering logic that is primarily server-driven.)*
