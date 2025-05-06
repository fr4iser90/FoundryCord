# Test Suite Structure (`tests/`)

This document outlines the organization of the automated test suite for the FoundryCord project, located within the top-level `tests/` directory. A well-organized test suite is crucial for ensuring tests are discoverable, maintainable, and effectively cover the application code.

## Guiding Principles

*   **Mirror Application Structure:** The directory structure within `tests/unit/` and `tests/integration/` should closely mirror the structure of the `app/` directory (i.e., `app/bot/`, `app/web/`, `app/shared/`). This makes it intuitive to locate tests corresponding to specific application modules.
*   **Separation of Test Types:** Unit tests and integration tests are kept in separate top-level directories (`unit/` and `integration/`) to clearly distinguish their scope and purpose.
*   **Colocation of Fixtures:** Pytest fixtures are defined in `conftest.py` files. A root `tests/conftest.py` can contain globally shared fixtures, while `conftest.py` files within subdirectories (e.g., `tests/unit/bot/conftest.py`) can define fixtures specific to that part of the application.

Refer to the [Testing Guidelines](./../01_getting_started/testing_guidelines.md) for details on testing philosophy, tools, and conventions.

## Key Directory Breakdown (`tests/`)

*   **`tests/unit/`**: Contains all unit tests.
    *   **Structure:** Subdirectories within `tests/unit/` mirror the `app/` directory. For example:
        *   Tests for `app/bot/application/services/some_service.py` would be in `tests/unit/bot/application/services/test_some_service.py`.
        *   Tests for `app/web/interfaces/api/rest/v1/auth/auth_controller.py` would be in `tests/unit/web/interfaces/api/rest/v1/auth/test_auth_controller.py`.
        *   Tests for `app/shared/domain/entities/user_entity.py` would be in `tests/unit/shared/domain/entities/test_user_entity.py`.
    *   **Focus:** Testing individual functions, methods, or classes in isolation, heavily using mocks for dependencies.

*   **`tests/integration/`**: Contains all integration tests.
    *   **Structure:** Similar to `unit/`, subdirectories mirror the `app/` structure where appropriate, focusing on testing interactions between components.
        *   Example: `tests/integration/bot/commands/test_moderation_commands.py` might test the interaction of moderation commands with services and mocked Discord API calls.
        *   Example: `tests/integration/web/services/test_user_auth_flow.py` might test the user authentication flow involving several services and repository interactions (with a test database).
    *   **Focus:** Testing the collaboration between multiple components, modules, or services. May involve limited interaction with real external systems (like a test database) or heavily configured mocks for external APIs.

*   **`tests/functional/` or `tests/e2e/` (Optional):** If End-to-End (E2E) or functional tests are implemented, they would reside in their own top-level directory. These tests typically cover complete user workflows through the UI or API.
    *   *(Currently, a dedicated structure for this is not explicitly defined but can be added if E2E testing is adopted.)*

*   **`tests/conftest.py`**: The root `conftest.py` file is used to define pytest fixtures, hooks, and plugins that are available to all tests in the suite.
    *   Sub-directories (e.g., `tests/unit/bot/conftest.py`) can also have their own `conftest.py` files for fixtures specific to that test group.

*   **`tests/pytest.ini` or `pyproject.toml`**: Configuration file for pytest. It might define markers, default options, paths, etc. (`pyproject.toml` is often used for modern Python projects to consolidate tool configurations, including pytest).

*   **`tests/fixtures/` or `tests/data/` (Optional):** If tests require extensive test data files (e.g., JSON, YAML, text files for mocking responses or providing input), these can be organized in a dedicated subdirectory.

*   **`app/tests/test-results/`**: As seen in the project structure, this specific path under `app/` seems designated for test *output* (e.g., XML reports for CI, HTML coverage reports). This should be gitignored.

## Example Directory Tree (Illustrative)

This tree illustrates the recommended structure based on the guidelines:

```tree
tests/
├── conftest.py         # Global fixtures and hooks
├── pytest.ini          # Pytest configuration (or in pyproject.toml)
├── unit/
│   ├── __init__.py
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── application/
│   │   │   └── services/
│   │   │       └── test_dashboard_lifecycle_service.py
│   │   └── interfaces/
│   │       └── commands/
│   │           └── test_auth_commands.py
│   ├── shared/
│   │   ├── __init__.py
│   │   └── domain/
│   │       └── entities/
│   │           └── test_user_entity.py
│   └── web/
│       ├── __init__.py
│       └── application/
│           └── services/
│               └── test_guild_service.py
└── integration/
    ├── __init__.py
    ├── bot/
    │   └── __init__.py
    │   # ... integration tests for bot components
    └── web/
        └── __init__.py
        # ... integration tests for web components

# Note: The actual app/tests/test-results/ directory is for generated output.
```
