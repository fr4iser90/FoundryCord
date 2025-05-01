# 8. Coding Conventions & Patterns

## Code Style

*   **Python:** PEP 8. Enforced by Black (formatting) and Flake8 (linting). Configuration likely standard, check root config files if needed (`pyproject.toml`? `.flake8`?).
*   **JavaScript:** [Needs Definition - Specify standard, e.g., StandardJS, Airbnb, Prettier defaults]. No explicit linter/formatter configuration found in project structure. Recommend adding Prettier/ESLint.
*   **CSS:** [Needs Definition - Specify standard, e.g., BEM, stylelint rules]. `kebab-case` seems to be used for class names. Recommend adding stylelint.
*   **Imports (Python):** Follow standard PEP 8 guidelines. Use of `isort` is recommended but not explicitly configured.

## Naming Conventions

*   **Python Variables:** `snake_case`
*   **Python Functions:** `snake_case`
*   **Python Classes:** `PascalCase`
*   **Python Modules:** `snake_case.py`
*   **JavaScript Variables:** `camelCase` (Assumed standard)
*   **JavaScript Functions:** `camelCase` (Assumed standard)
*   **JavaScript Classes:** `PascalCase` (Assumed standard)
*   **JavaScript Modules:** Mixed (`camelCase.js` and `kebab-case.js` observed). [Needs Consistency Definition - Prefer `camelCase.js` or `PascalCase.js`?]
*   **CSS Classes:** `kebab-case` (e.g., `widget-header`, `btn-primary`).
*   **Database Tables:** `snake_case`, plural (e.g., `app_users`, `guild_templates`).
*   **Database Columns:** `snake_case`.

## Design Patterns

List key design patterns observed or intended in the project:

*   **Layered Architecture:** Strictly enforced (Web: Controller -> Application Service -> Domain Service -> Repository | Bot: Cog/Command -> Service -> Repository).
*   **Repository Pattern:** Used for data access abstraction (Interfaces in `shared/domain/repositories`, Implementations in `shared/infrastructure/repositories`).
*   **Dependency Injection:** Heavily used by FastAPI (`Depends`) for injecting services, repositories, sessions into controllers and dependencies.
*   **Observer Pattern (Events):** Used in the frontend JavaScript for communication between loosely coupled components (e.g., `loadTemplateData`, `structureChanged` custom events via `EventTarget`).
*   **Factory Pattern:** Used for creating complex objects or managing instantiation logic (e.g., Session Factory `shared/infrastructure/database/session/factory.py`, Bot/Web Factories in `infrastructure/factories/`).
*   *(Add others if identified, e.g., Singleton for some managers?)*

## Logging

*   **Standard Library:** Python's built-in `logging` module.
*   **Configuration:** Centralized configuration likely loaded via `app/shared/application/logging/log_config.py`. Formatters defined in `app/shared/application/logging/formatters.py`. Includes specific handlers (e.g., console, potentially file or database via `app/shared/infrastructure/logging/handlers/db_handler.py`).
*   **Levels:** Follow standard logging level semantics (DEBUG for detailed info, INFO for operational messages, WARNING for potential issues, ERROR for errors, CRITICAL for severe errors).
*   **Format:** Standardized log format including timestamp, level, logger name, and message (see formatters).

## Error Handling

*   **Exceptions:** Prefer specific custom exceptions (potentially defined in `app/shared/domain/exceptions.py` or similar) over generic `Exception` in services and repositories.
*   **API Errors:** Controllers should catch custom exceptions and map them to appropriate `fastapi.HTTPException`s with user-friendly messages and correct status codes. Use global exception handlers (`app/web/core/exception_handlers.py`) for broad error categories.
*   **Service/Repo Errors:** Raise specific custom exceptions. Avoid returning `None` to indicate errors where possible; prefer exceptions.

## Comments

*   Use comments primarily to explain *why* a piece of code exists or why a complex decision was made, not *what* the code does (unless exceptionally complex).
*   Use **Docstrings (Google Style)** for all public modules, classes, functions, and methods.
*   Keep comments up-to-date with code changes.
*   Avoid commented-out code; use version control (Git) instead.

## Testing

*   **Framework:** pytest (with `pytest-asyncio`, `pytest-cov`).
*   **Types:** Aim for a mix of Unit, Integration, and potentially Functional tests.
    *   Unit: Test individual functions/classes in isolation (mocks used heavily).
    *   Integration: Test interactions between components (e.g., service layer with mocked repositories, controller with mocked services).
    *   Functional (End-to-End): Test complete user flows (potentially using tools like `httpx` against a running test instance).
*   **Location:** Tests reside in the top-level `/tests` directory, mirroring the `app/` structure (e.g., `tests/unit/shared/domain/services/`).
*   **Fixtures:** Use pytest fixtures (`conftest.py`) extensively for setting up test data, resources (like test database sessions), and mocks.
*   **Mocks/Stubs:** Use `unittest.mock` (via pytest) for isolating components during unit testing. 