# Shared Core Components: Domain Logic & Infrastructure

This document provides a deeper dive into key components within the `app/shared/` library, building upon the [Shared Core Library Structure](./shared_structure.md) overview. It focuses on the responsibilities, collaborations, and design of critical domain services, entities, aggregates, and important infrastructure pieces that are utilized by both the Bot and Web applications.

## Core Domain Services (`app/shared/domain/services/`)

Domain services in `app/shared/domain/services/` encapsulate core business logic that doesn\'t naturally fit within a single entity. They operate on domain entities and value objects and utilize repository interfaces for data persistence.

### 1. Authentication Service (`auth/authentication_service.py`)
*   **DDD Role:** Domain Service.
*   **Responsibilities:**
    *   Verifying user credentials (e.g., username/password, or handling OAuth callbacks by validating tokens/codes from external providers like Discord).
    *   Creating and managing user sessions upon successful authentication (e.g., creating session records via `SessionRepository`).
    *   Invalidating sessions (logout).
    *   Potentially handling API key generation and validation if centralized here.
    *   Generating and validating tokens (e.g., JWTs for session or API key representations if used, password reset tokens).
*   **Collaborators:**
    *   `UserRepository`: To fetch user details by username or Discord ID.
    *   `SessionRepository`: To create, read, and delete user sessions.
    *   `KeyRepository` (if managing API keys or other secure tokens).
    *   `EncryptionService` (from `app/shared/infrastructure/encryption/`): For hashing passwords, encrypting/decrypting session data or tokens.
    *   External OAuth providers (indirectly, by processing their responses).

### 2. Authorization Service (`auth/authorization_service.py`)
*   **DDD Role:** Domain Service.
*   **Responsibilities:**
    *   Determining if an authenticated user has the necessary permissions to perform a specific action or access a particular resource.
    *   Evaluating user roles (e.g., `AppRole` linked via `DiscordGuildUser`) against defined permission policies (e.g., from `app/shared/domain/auth/policies/`).
    *   Checking resource ownership where applicable (e.g., can user X edit template Y?).
*   **Collaborators:**
    *   `UserRepository`: To fetch user details, including their roles in specific contexts.
    *   `PermissionService` (if distinct, or logic is within `AuthorizationService`): To manage and look up permission definitions.
    *   `AuthorizationPolicies`: To load and interpret permission rules.
    *   Domain Entities: To check ownership attributes (e.g., `GuildTemplate.creator_user_id`).

### 3. Audit Service (`audit/audit_service.py`)
*   **DDD Role:** Domain Service.
*   **Responsibilities:**
    *   Providing a centralized way to record significant actions performed by users or the system.
    *   Ensuring audit records (`AuditRecord` entity) are created with appropriate context (who, what, when, details).
*   **Collaborators:**
    *   `AuditRepository`: To persist `AuditRecord` entities to the database.
    *   Various application services (in bot/web) and domain services will call this service to log actions.

**Sequence Diagram: User Authentication (Simplified Web Login Example)**

```mermaid
sequenceDiagram
    actor UserBrowser as User via Browser
    participant WebController as AuthController (Web API)
    participant AuthService as AuthenticationService (Shared Domain)
    participant UserRepo as UserRepository (Shared Infra)
    participant SessionRepo as SessionRepository (Shared Infra)
    participant EncryptionService as EncryptionService (Shared Infra)

    UserBrowser->>+WebController: POST /auth/login (credentials)
    WebController->>+AuthService: authenticate_user(username, password)
    AuthService->>+UserRepo: get_user_by_username(username)
    UserRepo-->>-AuthService: user_entity (or null)
    alt User not found
        AuthService-->>WebController: AuthenticationFailureException
        WebController-->>-UserBrowser: HTTP 401 Unauthorized
    else User found
        AuthService->>+EncryptionService: verify_password(password, user_entity.hashed_password)
        EncryptionService-->>-AuthService: is_valid_password (boolean)
        alt Invalid password
            AuthService-->>WebController: AuthenticationFailureException
            WebController-->>-UserBrowser: HTTP 401 Unauthorized
        else Valid password
            AuthService->>+SessionRepo: create_session(user_entity.id)
            SessionRepo-->>-AuthService: session_id
            AuthService-->>WebController: session_id (or user details with session info)
            WebController->>WebController: Set session cookie
            WebController-->>-UserBrowser: HTTP 200 OK (Redirect to dashboard)
        end
    end
```

## Key Domain Entities & Aggregates

Domain Entities represent objects with a distinct identity that persists over time. Aggregates are clusters of entities and value objects treated as a single unit, with one entity acting as the Aggregate Root.

### 1. User Aggregate
*   **Aggregate Root:** `AppUser` (represented by `app_users` table, model: `app/shared/infrastructure/models/auth/user_entity.py`).
*   **Description:** Represents a user of the FoundryCord system. The `AppUser` is central to identity, authentication, and authorization.
*   **Boundaries/Owned Entities:** While not strictly enforced by the ORM as a single object in all operations, the concept of a User aggregate includes:
    *   `Session` entities (user\'s active login sessions).
    *   `ApiKey` entities (API keys issued to the user).
    *   `UILayout` entities (user\'s personalized UI configurations).
    *   `DiscordGuildUser` (linking AppUser to Guilds and AppRoles).
*   **Responsibilities of Root (`AppUser`):** Manages its own identity attributes. Business rules related to user status (active/inactive), ownership of related data, and primary authentication attributes are conceptually tied here.

### 2. GuildTemplate Aggregate
*   **Aggregate Root:** `GuildTemplate` (represented by `guild_templates` table, model: `app/shared/infrastructure/models/guild_templates/guild_template_entity.py`).
*   **Description:** Represents a complete, potentially complex Discord server structure (categories, channels, roles, permissions) that can be designed, saved, and applied to guilds. This is the core of the Guild Designer feature.
*   **Boundaries/Owned Entities:** The `GuildTemplate` aggregate directly owns and manages the lifecycle of:
    *   `GuildTemplateCategory` entities.
    *   `GuildTemplateChannel` entities (which can be parented by categories within the same template).
    *   `GuildTemplateCategoryPermission` and `GuildTemplateChannelPermission` entities (value objects or child entities detailing role-based permission overwrites).
*   **Responsibilities of Root (`GuildTemplate`):**
    *   Ensures the internal consistency of the template structure (e.g., valid channel types, correct parenting).
    *   Manages overall template metadata (name, description, creator, shared status).
    *   Operations like adding/removing categories/channels or updating permissions are performed through methods on or services acting upon the `GuildTemplate` aggregate.

## Core Repository Interfaces & Implementations

The Repository pattern (`app/shared/domain/repositories/` for interfaces, `app/shared/infrastructure/repositories/` for implementations) is used to abstract data persistence logic, decoupling domain and application services from specific database technologies (SQLAlchemy in this case).

*   **`UserRepository` (`domain/auth/user_repository.py`, `infrastructure/auth/user_repository_impl.py`):**
    *   **Responsibility:** Provides methods for CRUD operations on `AppUser` entities (e.g., find by ID, find by Discord ID, find by username, save user).
*   **`GuildTemplateRepository` (`domain/guild_templates/guild_template_repository.py`, `infrastructure/guild_templates/guild_template_repository_impl.py`):**
    *   **Responsibility:** Provides methods for CRUD operations on `GuildTemplate` aggregates, including fetching a template with all its categories, channels, and permissions, and saving changes to the entire aggregate.

## Key Shared Infrastructure Components

### 1. Database Session Management (`app/shared/infrastructure/database/session/factory.py`)
*   **Responsibility:** Provides a centralized mechanism (e.g., a session factory or a context manager) for creating and managing SQLAlchemy database sessions.
*   **Usage:** Sessions are typically injected into repository implementations or application services (often via FastAPI dependencies for web requests or context managers for bot operations) to ensure that all database operations within a unit of work occur within the same session and transaction.

### 2. Encryption Service (`app/shared/infrastructure/encryption/encryption_service.py`)
*   **Responsibility:** Handles encryption and decryption of sensitive data, and hashing of passwords or other secrets. It likely uses robust cryptographic libraries.
*   **Collaborators:** `KeyManagementService` (for managing encryption keys), Python cryptography libraries.
*   **Usage:** Used by `AuthenticationService` for password verification, potentially for encrypting sensitive configuration values or session data.

### 3. Logging Configuration & Services (`app/shared/application/logging/` & `app/shared/infrastructure/logging/`)
*   **Responsibility:** Provides a shared setup for logging (`log_config.py`), common formatters, and base logging services or handlers (like a `DBHandler` to store logs in the database if implemented).
*   **Usage:** Both Bot and Web applications initialize their logging using this shared configuration, ensuring consistent log formats and allowing for centralized log management strategies.

## Critical Shared Algorithms & Logic

*(This section will be populated as specific complex shared algorithms are identified. Examples might include permission inheritance/resolution logic within the `AuthorizationService`, or complex data mapping/transformation logic used by both Bot and Web.)*
