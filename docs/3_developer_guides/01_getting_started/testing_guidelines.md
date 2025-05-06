# Testing Guidelines

This document outlines the philosophy, tools, conventions, and best practices for writing tests within the [FoundryCord](../../../1_introduction/glossary.md#foundrycord) project. Adhering to these guidelines helps ensure code quality, maintainability, and prevents regressions.

**Goal:** Ensure code quality, maintainability, and prevent regressions through consistent and effective testing practices across all components of [FoundryCord](../../../1_introduction/glossary.md#foundrycord) (Bot, Web, Shared).

## Testing Philosophy

*   **Prioritize Unit Tests:** Focus primarily on unit tests to verify the logic of individual classes and functions in isolation. This ensures tests are fast, reliable, and pinpoint failures accurately.
*   **Integration Tests for Interactions:** Use integration tests judiciously to verify the interaction between different components (e.g., service and database, command and workflow) or with external systems (like the Discord API, though heavily mocked).
*   **Test Behavior, Not Implementation:** Write tests that verify the expected *outcome* or *behavior* of a function or class, rather than testing the exact internal steps it takes. This makes tests less brittle to refactoring.
*   **Readability:** Tests should be clear, concise, and easy to understand. They serve as living documentation.

## Tools

*   **Test Runner:** [`pytest`](https://docs.pytest.org/)
*   **Async Support:** [`pytest-asyncio`](https://pytest-asyncio.readthedocs.io/) (automatically used via `pytest`)
*   **Mocking:** [`pytest-mock`](https://pytest-mock.readthedocs.io/) (provides the `mocker` fixture)

## Structure & Location

*   Tests reside in the top-level `tests/` directory.
*   Mirror the application structure within `tests/unit/` and `tests/integration/`.
    *   Example: Tests for `app/bot/application/services/auth_service.py` should be in `tests/unit/bot/application/services/test_auth_service.py`.
    *   Example: Integration tests for the bot's startup sequence might be in `tests/integration/bot/startup/test_startup.py`.

## Naming Conventions

*   **Files:** Test files must start with `test_` (e.g., `test_service_factory.py`).
*   **Functions:** Test functions must start with `test_` (e.g., `def test_register_service_creator():`).
*   **Clarity:** Use descriptive names for test functions that indicate what scenario or behavior is being tested (e.g., `test_login_fails_with_invalid_password`).

## Fixtures (`@pytest.fixture`)

*   Use fixtures to set up reusable test contexts, data, or mock objects.
*   Define fixtures in the test file itself or in a shared `conftest.py` file within a test directory for broader reuse.
*   Scope fixtures appropriately (`function`, `class`, `module`, `session`) based on their required lifetime and setup cost. Default is `function`.

## Mocking (`mocker` fixture)

*   Use the `mocker` fixture (from `pytest-mock`) to patch dependencies.
*   **Mock Dependencies, Not the Target:** Mock objects that the code-under-test *depends on* (e.g., other services, repository calls, Discord API interactions via the `bot` object). Avoid mocking the class or function you are currently testing, if possible.
*   **Targeting:** Use string paths relative to where the dependency is *looked up*, not where it's defined (e.g., `mocker.patch('app.bot.application.services.some_service.DatabaseRepository')` if `some_service.py` imports `DatabaseRepository`).
*   **`AsyncMock`:** Use `mocker.AsyncMock` for mocking `async` functions or methods.
*   **Specify Return Values/Side Effects:** Configure mocks using `return_value`, `side_effect`, etc., to simulate the behavior of the dependency.

## Assertions (`assert`)

*   Use standard Python `assert` statements. `pytest` provides detailed introspection on assertion failures.
*   Be specific about what you are asserting. Check return values, attribute changes, exceptions raised (`pytest.raises`), or calls to mocks (`mock_object.assert_called_once_with(...)`).

## Running Tests

*   Use the provided Nix environment to ensure consistency.
*   Run tests using the command: `nix-shell --run "pytest [optional_path_to_test_file_or_dir]"`
    *   Running without a path executes all tests found by `pytest`.
    *   Specifying a path runs only tests within that file or directory.

## Coverage (Optional)

*   While not strictly enforced yet, aiming for good test coverage, especially for critical business logic and complex functions, is encouraged. Tools like `pytest-cov` can be integrated later.

## Extending Tests

*   When adding new features or fixing bugs, add corresponding unit tests.
*   If a bug is found that wasn't caught by tests, write a test that reproduces the bug *before* fixing the code. Ensure the test passes after the fix.
