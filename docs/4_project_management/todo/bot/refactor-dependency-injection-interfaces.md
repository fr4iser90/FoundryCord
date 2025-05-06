# Refactor Core Dependencies using Interfaces and Dependency Injection

**Goal:** Resolve circular import dependencies involving core components like `ComponentRegistry`, `ServiceFactory`, `FoundryCord`, Components, and Controllers by consistently applying the Interface Segregation Principle (using ABCs) and Dependency Injection (DI). This will eliminate the need for `TYPE_CHECKING` workarounds for these specific cycles and improve overall architecture, testability, and maintainability.

**Design Decisions & Rationale:**

*   **Interface Placement:** Interfaces defining the *internal management contracts* of the bot (like `ComponentRegistry`, `ServiceFactory`, `Bot`) reside in `app/bot/application/interfaces/`. This maintains separation of concerns; these interfaces describe *how the bot works internally*. Interfaces for *shared data or services* consumed by multiple parts (e.g., `app/web`) would belong in `app/shared`. The web layer should interact with the bot via dedicated shared interfaces/services, not its internal management interfaces.
*   **Interface Naming:** Interfaces are named using simple, descriptive names (e.g., `ComponentRegistry`, `ServiceFactory`) without prefixes like `I`. This follows modern Python conventions. The use of `abc.ABC` (or potentially `typing.Protocol`) and placement within an `interfaces` module clearly indicates their purpose.

**Related Architectural Concepts:**
*   Dependency Inversion Principle (DIP)
*   Interface Segregation Principle (ISP)
*   Dependency Injection (DI)

## Phase 1: Define Core Interfaces (ABCs)

*   [ ] **Task 1.1:** Create a new directory for application-level interfaces: `app/bot/application/interfaces/`.
*   [ ] **Task 1.2:** Define the `ComponentRegistry` interface in `app/bot/application/interfaces/component_registry.py`.
    *   Include abstract methods for all public methods currently used by other classes (e.g., `get_component_class`, `get_type_by_key`, `get_definition_by_key`, `register_component`, `initialize`, `get_all_component_types`, `has_component`). Use `abc.ABC` and `@abstractmethod`.
*   [ ] **Task 1.3:** Define the `ServiceFactory` interface in `app/bot/application/interfaces/service_factory.py`.
    *   Include abstract methods for its public interface (e.g., `get_service`, `has_service`, `register_service`, `initialize_services`, `create_or_get`, `get_services`).
*   [ ] **Task 1.4:** Define the `Bot` interface (or potentially more granular interfaces like `BotCore`, `BotServices`) in `app/bot/application/interfaces/bot.py`.
    *   Identify the minimal set of bot attributes/methods needed by dependencies (e.g., `service_factory` attribute, maybe `user` attribute, `get_channel`). Start minimal and add as needed during Phase 3.

## Phase 2: Implement Interfaces

*   [ ] **Task 2.1:** Modify `app/bot/infrastructure/config/registries/component_registry.py`:
    *   Import `ComponentRegistry` as `ComponentRegistryInterface` from `....application.interfaces.component_registry`. (Use alias to avoid name clash with the class itself).
    *   Make `ComponentRegistry` inherit from `ComponentRegistryInterface`.
    *   Ensure all abstract methods are implemented.
*   [ ] **Task 2.2:** Modify `app/bot/infrastructure/factories/service_factory.py`:
    *   Import `ServiceFactory` as `ServiceFactoryInterface` from `....application.interfaces.service_factory`.
    *   Make `ServiceFactory` inherit from `ServiceFactoryInterface`.
    *   Ensure all abstract methods are implemented.
*   [ ] **Task 2.3:** Modify `app/bot/infrastructure/startup/bot.py`:
    *   Import `Bot` as `BotInterface` (or relevant bot interfaces) from `....application.interfaces.bot`.
    *   Make `FoundryCord` inherit from `BotInterface`.
    *   Ensure all abstract methods are implemented.

## Phase 3: Update Dependencies & Type Hints

*   [ ] **Task 3.1:** Update `app/bot/infrastructure/factories/component_factory.py`:
    *   Import `ComponentRegistry` interface from `....application.interfaces.component_registry`.
    *   Change `__init__` type hint: `component_registry: ComponentRegistry`.
    *   Remove direct import of the concrete `ComponentRegistry` class (if different).
*   [ ] **Task 3.2:** Update `app/bot/infrastructure/factories/composite/bot_factory.py`:
    *   Import `ComponentRegistry`, `ServiceFactory`, `Bot` interfaces.
    *   Change `__init__` type hint: `bot: Bot`.
    *   Change attribute type hints: `component_registry: Optional[ComponentRegistry]`, `service_factory: Optional[ServiceFactory]`.
    *   Remove direct imports of concrete `ComponentRegistry`, `ServiceFactory`, `FoundryCord` classes.
*   [ ] **Task 3.3:** Update `app/bot/interfaces/dashboards/controller/dashboard_controller.py`:
    *   Import `ComponentRegistry`, `ServiceFactory`, `Bot` interfaces.
    *   Modify `__init__` to accept dependencies via parameters: `def __init__(..., bot: Bot, component_registry: ComponentRegistry, data_service: DashboardDataService, ...):` (adjust exact params as needed).
    *   Remove logic fetching services via `bot.service_factory` inside methods; use the injected instances.
    *   Change type hints using concrete `FoundryCord` or `ServiceFactory` to use the interfaces.
*   [ ] **Task 3.4:** Update `app/bot/interfaces/dashboards/components/base_component.py`:
    *   Import `Bot` interface.
    *   Change `deserialize` type hint: `bot: Optional[Bot] = None`.
    *   Remove direct import of concrete `FoundryCord` class.
*   [ ] **Task 3.5:** Update `app/bot/application/services/dashboard/dashboard_data_service.py`:
    *   Import `Bot`, `ServiceFactory` interfaces.
    *   Change `__init__` type hint: `bot: Bot`, `service_factory: ServiceFactory`.
    *   Remove direct imports of concrete `FoundryCord`, `ServiceFactory` classes.
*   [ ] **Task 3.6:** Update `app/bot/infrastructure/config/registries/component_registry.py`:
    *   Import `Bot` interface.
    *   Change `initialize` type hint: `bot: Bot`.
    *   Change attribute type hint: `bot: Optional[Bot]`.
    *   Remove direct import of concrete `FoundryCord` class.
*   [ ] **Task 3.7:** Update `app/bot/infrastructure/startup/bot.py`:
    *   Import `ServiceFactory` interface.
    *   Change attribute type hint: `service_factory: Optional[ServiceFactory]`.
    *   Remove direct import of concrete `ServiceFactory` class.
*   [ ] **Task 3.8:** Review other potentially affected files (e.g., other factories, services, workflows) and update imports/type hints to use interfaces where appropriate.

## Phase 4: Solidify Dependency Injection Wiring

*   [ ] **Task 4.1:** Review `app/bot/infrastructure/startup/setup_hooks.py` and `app/bot/infrastructure/startup/bot.py`:
    *   Ensure concrete instances (`ComponentRegistry`, `ServiceFactory`, etc.) are created correctly.
    *   Ensure these concrete instances are *injected* into the constructors of dependent objects (like `ComponentFactory`, `DashboardDataService`, Workflows) according to the updated `__init__` signatures expecting Interfaces.
*   [ ] **Task 4.2:** Review `app/bot/infrastructure/factories/service_factory.py`:
    *   Ensure it correctly creates and returns *concrete* service instances, even if consumers type hint against interfaces.
*   [ ] **Task 4.3:** Review `app/bot/infrastructure/dashboards/dashboard_registry.py`:
    *   Update the creation of `DashboardController` in `activate_or_update_dashboard` to correctly pass the required dependencies (e.g., `component_registry`, `data_service`) obtained via the injected `bot` (which should provide access via its interface).

## Phase 5: Verification

*   [ ] **Task 5.1:** Remove all `TYPE_CHECKING` blocks that were only needed for the now-resolved cycles involving the refactored components (carefully verify each one is no longer needed). Keep blocks needed for other reasons.
*   [ ] **Task 5.2:** Run static analysis (`mypy`, `pylint`) to check for type errors and other issues.
*   [ ] **Task 5.3:** Run all relevant unit tests (e.g., `test_component_registry.py`, `test_dashboard_controller.py`, `test_service_factory.py`). Fix any failures caused by the refactoring.
*   [ ] **Task 5.4:** Attempt to start the bot application. Check logs for errors.
*   [ ] **Task 5.5:** Perform manual testing of core features (e.g., dashboard display, command execution) to ensure functionality remains intact. 