# Refactor Core Dependencies using Interfaces and Dependency Injection

**Goal:** Resolve circular import dependencies involving core components like `ComponentRegistry`, `ServiceFactory`, `FoundryCord`, Components, and Controllers by consistently applying the Interface Segregation Principle (using ABCs) and Dependency Injection (DI). This will eliminate the need for `TYPE_CHECKING` workarounds for these specific cycles and improve overall architecture, testability, and maintainability.

**Related Architectural Concepts:**
*   Dependency Inversion Principle (DIP)
*   Interface Segregation Principle (ISP)
*   Dependency Injection (DI)

## Phase 1: Define Core Interfaces (ABCs)

*   [ ] **Task 1.1:** Create a new directory for application-level interfaces: `app/bot/application/interfaces/`.
*   [ ] **Task 1.2:** Define `IComponentRegistry` in `app/bot/application/interfaces/registry.py`.
    *   Include abstract methods for all public methods currently used by other classes (e.g., `get_component_class`, `get_type_by_key`, `get_definition_by_key`, `register_component`, `initialize`, `get_all_component_types`, `has_component`). Use `abc.ABC` and `@abstractmethod`.
*   [ ] **Task 1.3:** Define `IServiceFactory` in `app/bot/application/interfaces/factory.py`.
    *   Include abstract methods for its public interface (e.g., `get_service`, `has_service`, `register_service`, `initialize_services`, `create_or_get`, `get_services`).
*   [ ] **Task 1.4:** Define `IBot` (or potentially more granular interfaces like `IBotCore`, `IBotServices`) in `app/bot/application/interfaces/bot.py`.
    *   Identify the minimal set of bot attributes/methods needed by dependencies (e.g., `service_factory` attribute, maybe `user` attribute, `get_channel`). Start minimal and add as needed during Phase 3.

## Phase 2: Implement Interfaces

*   [ ] **Task 2.1:** Modify `app/bot/infrastructure/config/registries/component_registry.py`:
    *   Import `IComponentRegistry`.
    *   Make `ComponentRegistry` inherit from `IComponentRegistry`.
    *   Ensure all abstract methods are implemented.
*   [ ] **Task 2.2:** Modify `app/bot/infrastructure/factories/service_factory.py`:
    *   Import `IServiceFactory`.
    *   Make `ServiceFactory` inherit from `IServiceFactory`.
    *   Ensure all abstract methods are implemented.
*   [ ] **Task 2.3:** Modify `app/bot/infrastructure/startup/bot.py`:
    *   Import `IBot` (or relevant bot interfaces).
    *   Make `FoundryCord` inherit from `IBot`.
    *   Ensure all abstract methods are implemented.

## Phase 3: Update Dependencies & Type Hints

*   [ ] **Task 3.1:** Update `app/bot/infrastructure/factories/component_factory.py`:
    *   Import `IComponentRegistry` from `...interfaces.registry`.
    *   Change `__init__` type hint: `component_registry: IComponentRegistry`.
    *   Remove direct import of `ComponentRegistry`.
*   [ ] **Task 3.2:** Update `app/bot/infrastructure/factories/composite/bot_factory.py`:
    *   Import `IComponentRegistry`, `IServiceFactory`, `IBot`.
    *   Change `__init__` type hint: `bot: IBot`.
    *   Change attribute type hints: `component_registry: Optional[IComponentRegistry]`, `service_factory: Optional[IServiceFactory]`.
    *   Remove direct imports of `ComponentRegistry`, `ServiceFactory`, `FoundryCord`.
*   [ ] **Task 3.3:** Update `app/bot/interfaces/dashboards/controller/dashboard_controller.py`:
    *   Import `IComponentRegistry`, `IServiceFactory`, `IBot`.
    *   Modify `__init__` to accept dependencies via parameters: `def __init__(..., bot: IBot, component_registry: IComponentRegistry, data_service: DashboardDataService, ...):` (adjust exact params as needed).
    *   Remove logic fetching services via `bot.service_factory` inside methods; use the injected instances.
    *   Change type hints using `FoundryCord` or `ServiceFactory` to use the interfaces.
*   [ ] **Task 3.4:** Update `app/bot/interfaces/dashboards/components/base_component.py`:
    *   Import `IBot`.
    *   Change `deserialize` type hint: `bot: Optional[IBot] = None`.
    *   Remove direct import of `FoundryCord`.
*   [ ] **Task 3.5:** Update `app/bot/application/services/dashboard/dashboard_data_service.py`:
    *   Import `IBot`, `IServiceFactory`.
    *   Change `__init__` type hint: `bot: IBot`, `service_factory: IServiceFactory`.
    *   Remove direct imports of `FoundryCord`, `ServiceFactory`.
*   [ ] **Task 3.6:** Update `app/bot/infrastructure/config/registries/component_registry.py`:
    *   Import `IBot`.
    *   Change `initialize` type hint: `bot: IBot`.
    *   Change attribute type hint: `bot: Optional[IBot]`.
    *   Remove direct import of `FoundryCord`.
*   [ ] **Task 3.7:** Update `app/bot/infrastructure/startup/bot.py`:
    *   Import `IServiceFactory`.
    *   Change attribute type hint: `service_factory: Optional[IServiceFactory]`.
    *   Remove direct import of `ServiceFactory`.
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