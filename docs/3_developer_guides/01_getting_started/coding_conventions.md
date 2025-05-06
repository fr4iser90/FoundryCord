# 8. Coding Conventions & Patterns

This document outlines the coding style, naming conventions, design patterns, and other best practices to be followed when contributing to the [FoundryCord](../../../1_introduction/glossary.md#foundrycord) project. Adhering to these conventions ensures code consistency, readability, and maintainability.

## Code Style

*   **Python:** [PEP 8](https://www.python.org/dev/peps/pep-0008/) is the standard. Code formatting is strictly enforced by [Black](https://black.readthedocs.io/), and linting by [Flake8](https://flake8.pycqa.org/). Refer to the project\'s `pyproject.toml` (for Black) and `.flake8` (if present, otherwise defaults) for specific configurations.
*   **JavaScript:** *Currently, no specific linter (e.g., ESLint) or formatter (e.g., Prettier) is formally configured in the project.* If these tools are adopted, this section must be updated with links to their configuration and chosen style guide (e.g., StandardJS, Airbnb).
*   **CSS:** *Currently, no specific linter (e.g., Stylelint) is formally configured.* If adopted, link to its configuration here. For class names, `kebab-case` is predominantly used (see Naming Conventions).
*   **Imports (Python):** Follow standard PEP 8 guidelines. The use of [isort](https://pycqa.github.io/isort/) is highly recommended to automatically sort imports, which improves readability and helps prevent merge conflicts. *Currently, `isort` is not explicitly configured in CI/pre-commit hooks.*

## Naming Conventions

*   **Python Variables:** `snake_case`
*   **Python Functions:** `snake_case`
*   **Python Classes:** `PascalCase`
*   **Python Modules:** `snake_case.py`
*   **JavaScript Variables:** `camelCase` (Assumed standard)
*   **JavaScript Functions:** `camelCase` (Assumed standard)
*   **JavaScript Classes:** `PascalCase` (Assumed standard)
*   **JavaScript Modules:** Mixed (`camelCase.js` and `kebab-case.js` observed in some areas). *A consistent standard (e.g., `kebab-case.js` for general modules, `PascalCase.js` if the file primarily exports a class of the same name) should be decided upon and enforced.*
*   **CSS Classes:** `kebab-case` (e.g., `widget-header`, `btn-primary`). This is the preferred and observed convention.
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

*   Use comments primarily to explain **why** a piece of code exists or **why** a complex decision was made, not *what* the code does (unless the code is exceptionally complex and its operation isn\'t obvious from reading it).
*   **Docstrings (Google Style):** All public modules, classes, functions, and methods **must** have docstrings following the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
*   Keep comments and docstrings **up-to-date** with code changes.
*   **Avoid commented-out code.** Use version control (Git) to track historical code.

## Testing

*   **Framework:** pytest (with `pytest-asyncio`, `pytest-cov`).
*   **Types:** Aim for a mix of Unit, Integration, and potentially Functional tests.
    *   Unit: Test individual functions/classes in isolation (mocks used heavily).
    *   Integration: Test interactions between components (e.g., service layer with mocked repositories, controller with mocked services).
    *   Functional (End-to-End): Test complete user flows (potentially using tools like `httpx` against a running test instance).
*   **Location:** Tests reside in the top-level `/tests` directory, mirroring the `app/` structure (e.g., `tests/unit/shared/domain/services/`).
*   **Fixtures:** Use pytest fixtures (`conftest.py`) extensively for setting up test data, resources (like test database sessions), and mocks.
*   **Mocks/Stubs:** Use `unittest.mock` (via pytest) for isolating components during unit testing. 