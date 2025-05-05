# 3. Backend Architecture

## Overview

Describe the overall approach for the backend API.
*   **Framework:** FastAPI
*   **Language:** Python 3.x
*   **Database ORM:** SQLAlchemy (async with asyncio, v2.x)
*   **Key Principles:** Layered architecture (Controller -> Service -> Repository), Dependency Injection (FastAPI's Depends), Async operations, Shared Core library (`app/shared`).

## Layers

Describe the responsibilities of each layer:

*   **Controller Layer (`app/web/interfaces/api/rest/v1/`):**
    *   Receives HTTP requests via FastAPI routers.
    *   Handles request/response serialization using Pydantic Schemas (`app/web/interfaces/api/rest/v1/schemas/`).
    *   Performs validation, authentication, and authorization checks, often via FastAPI Dependencies (`app/web/interfaces/api/rest/dependencies/`).
    *   Calls the appropriate Application Service layer methods.
    *   Formats HTTP responses or raises HTTPExceptions.
*   **Application Service Layer (`app/web/application/services/`):**
    *   Contains business logic specific to the web application/API use cases.
    *   Orchestrates operations involving multiple domain services or repositories from the Shared Core.
    *   Handles complex validation rules specific to the API context.
    *   May interact with external services (if any).
*   **Domain Service Layer (`app/shared/domain/services/`):**
    *   Contains core, reusable business logic independent of the delivery mechanism (API or Bot).
    *   Examples: `AuthenticationService`, `AuthorizationService`, `GuildTemplateService` (if exists).
    *   Operates on Domain Entities and uses Repository interfaces.
    *   Does NOT directly interact with the database session (delegates to repositories).
*   **Repository Layer (`app/shared/domain/repositories/` for interfaces, `app/shared/infrastructure/repositories/` for implementations):**
    *   Abstracts data access logic behind interfaces defined in the domain.
    *   Implementations (`*_impl.py`) interact directly with the SQLAlchemy session (`app/shared/infrastructure/database/session/`) and ORM Entities.
    *   Provides methods for CRUD operations and specific queries.
*   **Entity/Model Layer (`app/shared/infrastructure/models/`):**
    *   Defines SQLAlchemy ORM models representing database tables.
    *   Includes table definitions, columns, relationships, and constraints.
*   **Schema Layer (`app/web/interfaces/api/rest/v1/schemas/`):**
    *   Defines Pydantic models used specifically for API request validation and response serialization.
    *   Ensures a clear contract for the API, decoupling API structure from internal domain models.

## Database Interaction

*   **Session Management:** Database sessions are managed via SQLAlchemy's async features. A session factory and context manager likely exist in `app/shared/infrastructure/database/session/`. Sessions are typically injected into Repositories or sometimes Services via FastAPI's dependency injection system (using dependencies defined possibly in `app/web/interfaces/api/rest/dependencies/` or `app/shared/infrastructure/database/session/factory.py`).
*   **Transactions:** Transactions are typically managed at the Service layer or within the session context manager. `session.commit()` and `session.rollback()` are called explicitly or handled automatically by the context manager/dependency upon exiting the request scope.
*   **Async Operations:** Utilizes `asyncio` and the `asyncpg` driver for non-blocking database I/O throughout the stack.

## Bot Communication

*   **Backend -> Bot:** The mechanism for the Backend API to trigger actions in the Discord Bot worker needs clarification. Potential options: Database flags, dedicated message queue (e.g., Redis Pub/Sub, RabbitMQ), or an internal RPC/API call. **[Needs Clarification]**
*   **Bot -> Backend/Data:** The Bot worker primarily accesses data via the Shared Core's Repositories, directly interacting with the database. It may potentially call specific, secured Backend API endpoints if needed, but direct DB access via shared modules seems primary.

## Error Handling

*   **Controllers:** Catch specific exceptions from services/repositories and map them to appropriate `fastapi.HTTPException` responses with correct status codes and detail messages. Global exception handlers (defined in `app/web/infrastructure/startup/exception_handlers.py`) might exist for common error types (e.g., 404, 500).
*   **Services/Repositories:** Raise custom exceptions (defined possibly in `app/shared/domain/exceptions.py`) to indicate specific business rule violations or data access issues. Avoid leaking implementation details.

## Authentication & Authorization

*   **Authentication:** Handled via FastAPI middleware (e.g., `app/web/infrastructure/middleware/authentication.py`) likely inspecting session cookies or Authorization headers (e.g., JWT). Relies on shared services like `AuthenticationService` (`app/shared/domain/services/auth/authentication_service.py`) and `SessionRepository` (`app/shared/infrastructure/repositories/auth/session_repository_impl.py`).
*   **Authorization:** Permissions and role checks are likely performed using FastAPI dependencies (`app/web/interfaces/api/rest/dependencies/auth_dependencies.py`) which utilize services like `AuthorizationService` (`app/shared/domain/services/auth/authorization_service.py`) to verify user permissions against required roles or resource ownership. 