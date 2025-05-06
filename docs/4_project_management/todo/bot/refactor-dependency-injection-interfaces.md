# Refactor Core Dependencies using Interfaces and Dependency Injection

**Goal:** Resolve circular import dependencies involving core components like `ComponentRegistry`, `ServiceFactory`, `FoundryCord`, Components, and Controllers by consistently applying the Interface Segregation Principle (using ABCs) and Dependency Injection (DI). This will eliminate the need for `TYPE_CHECKING` workarounds for these specific cycles and improve overall architecture, testability, and maintainability.

**IMPORTANT RULE:** Bei der Umsetzung dieses Plans werden für die Abhängigkeiten `Bot`, `ServiceFactory`, `ComponentRegistry` und deren Interfaces **KEINE Type Hints** verwendet. Weder in den Interfaces selbst, noch in den Klassen, die sie verwenden.

**Design Decisions & Rationale:**

*   **Interface Placement:** Interfaces defining the *internal management contracts* of the bot (like `ComponentRegistry`, `ServiceFactory`, `Bot`) reside in `app/bot/application/interfaces/`. This maintains separation of concerns; these interfaces describe *how the bot works internally*. Interfaces for *shared data or services* consumed by multiple parts (e.g., `app/web`) would belong in `app/shared`. The web layer should interact with the bot via dedicated shared interfaces/services, not its internal management interfaces.
*   **Interface Naming:** Interfaces are named using simple, descriptive names (e.g., `ComponentRegistry`, `ServiceFactory`) without prefixes like `I`. This follows modern Python conventions. The use of `abc.ABC` (or potentially `typing.Protocol`) and placement within an `interfaces` module clearly indicates their purpose.

**Related Architectural Concepts:**
*   Dependency Inversion Principle (DIP)
*   Interface Segregation Principle (ISP)
*   Dependency Injection (DI)
**Affected:**
*    /app/bot/application/services/dashboard/dashboard_data_service.py
*    /app/bot/infrastructure/config/registries/component_registry.py
*    /app/bot/infrastructure/factories/composite/bot_factory.py
*    /app/bot/infrastructure/startup/bot.py
*    /app/bot/infrastructure/startup/setup_hooks.py
*    /app/bot/interfaces/dashboards/components/base_component.py
*    /app/bot/interfaces/dashboards/components/common/embeds/dashboard_embed.py
*    /app/bot/interfaces/dashboards/components/common/selectors/generic_selector.py

## Phase 1: Define Core Interfaces (ABCs)

*   [x] **Task 1.1:** Create a new directory for application-level interfaces: `app/bot/application/interfaces/`. (Verified directory exists)
*   [ ] **Task 1.2:** Define the `ComponentRegistry` interface in `app/bot/application/interfaces/component_registry.py`.
    *   Use `abc.ABC` and `@abstractmethod`. **KEINE Type Hints** in den Signaturen.
    *   Include abstract methods for:
        *   `register_component(self, component_type, component_class, description, default_config)`
        *   `get_component_class(self, component_type)`
        *   `get_type_by_key(self, component_key)`
        *   `get_definition_by_key(self, component_key)`
        *   `get_all_component_types(self)`
        *   `has_component(self, component_type)`
        *   *(`initialize` ist KEIN Teil des Interfaces)*
*   [ ] **Task 1.3:** Define the `ServiceFactory` interface in `app/bot/application/interfaces/service_factory.py`.
    *   Use `abc.ABC` and `@abstractmethod`. **KEINE Type Hints** in den Signaturen.
    *   Include abstract methods for:
        *   `register_service_creator(self, name, creator, overwrite)`
        *   `register_service(self, name, instance, overwrite)`
        *   `get_service(self, name)`
        *   `has_service(self, name)`
        *   `get_all_services(self)`
        *   *(`initialize_services`, `create`, `create_or_get` sind KEIN Teil des Interfaces)*
*   [ ] **Task 1.4:** Define the `Bot` interface in `app/bot/application/interfaces/bot.py`.
    *   Use `abc.ABC` and `@abstractmethod` / `@property`. **KEINE Type Hints**.
    *   Include abstract properties/methods for:
        *   `service_factory` (property, gibt `ServiceFactoryInterface` zurück)
        *   `user` (property, gibt `nextcord.User` / `ClientUser` zurück)
        *   `loop` (property, gibt `asyncio.AbstractEventLoop` zurück)
        *   `get_channel(self, id)` (Methode)
        *   `get_guild(self, id)` (Methode)
        *   *(Weitere bei Bedarf hinzufügen, z.B. für Events oder Config)*

## Phase 2: Implement Interfaces

*   [ ] **Task 2.1:** Modify `app/bot/infrastructure/config/registries/component_registry.py`:
    *   Import `ComponentRegistry` as `ComponentRegistryInterface` from `....application.interfaces.component_registry`. (Use alias to avoid name clash with the class itself).
    *   Make `ComponentRegistry` inherit from `ComponentRegistryInterface`.
    *   Ensure all abstract methods aus Task 1.2 sind implementiert.
*   [ ] **Task 2.2:** Modify `app/bot/infrastructure/factories/service_factory.py`:
    *   Import `ServiceFactory` as `ServiceFactoryInterface` from `....application.interfaces.service_factory`.
    *   Make `ServiceFactory` inherit from `ServiceFactoryInterface`.
    *   Ensure all abstract methods aus Task 1.3 sind implementiert.
*   [ ] **Task 2.3:** Modify `app/bot/infrastructure/startup/bot.py`:
    *   Import `Bot` as `BotInterface` from `....application.interfaces.bot`.
    *   Make `FoundryCord` inherit from `BotInterface`.
    *   Ensure all abstract methods/properties aus Task 1.4 sind implementiert.

## Phase 3: Update Dependencies & Remove Type Hints

**Regel:** Für die Abhängigkeiten `Bot`, `ServiceFactory`, `ComponentRegistry` **alle** Type Hints in den folgenden Dateien entfernen. Nur die Imports auf die Interfaces umstellen.

*   [ ] **Task 3.1:** Update `app/bot/infrastructure/factories/component_factory.py`:
    *   Import `ComponentRegistryInterface` from `....application.interfaces.component_registry`.
    *   Im `__init__`, Parameter `component_registry` **ohne Type Hint** lassen.
    *   Entferne direkten Import der konkreten `ComponentRegistry` Klasse.
*   [ ] **Task 3.2:** Update `app/bot/infrastructure/factories/composite/bot_factory.py`:
    *   Import `ComponentRegistryInterface`, `ServiceFactoryInterface`, `BotInterface`.
    *   Im `__init__`, Parameter `bot` **ohne Type Hint** lassen.
    *   Attribute `component_registry`, `service_factory` **ohne Type Hint** lassen.
    *   Entferne direkte Imports der konkreten Klassen.
*   [ ] **Task 3.3:** Update `app/bot/interfaces/dashboards/controller/dashboard_controller.py`:
    *   Import `ComponentRegistryInterface`, `ServiceFactoryInterface`, `BotInterface`.
    *   Im `__init__` die Parameter `bot`, `component_registry` **ohne Type Hint** lassen. (`data_service` kann seinen Hint behalten, falls es keine Zirkel verursacht).
    *   Entferne Logik, die Services via `bot.service_factory` holt.
    *   Entferne direkte Imports der konkreten Klassen.
*   [ ] **Task 3.4:** Update `app/bot/interfaces/dashboards/components/base_component.py`:
    *   Import `BotInterface`.
    *   Im `__init__` (oder wo `bot` übergeben wird), Parameter `bot` **ohne Type Hint** lassen.
    *   Entferne direkten Import der konkreten `FoundryCord` Klasse.
*   [ ] **Task 3.5:** Update `app/bot/application/services/dashboard/dashboard_data_service.py`:
    *   Import `BotInterface`, `ServiceFactoryInterface`.
    *   Im `__init__`, Parameter `bot`, `service_factory` **ohne Type Hint** lassen.
    *   Entferne direkte Imports der konkreten Klassen.
*   [ ] **Task 3.6:** Update `app/bot/infrastructure/config/registries/component_registry.py`:
    *   Import `BotInterface`.
    *   Attribut `bot` **ohne Type Hint** lassen.
    *   Entferne direkten Import der konkreten `FoundryCord` Klasse.
*   [ ] **Task 3.7:** Update `app/bot/infrastructure/startup/bot.py`:
    *   Import `ServiceFactoryInterface`.
    *   Attribut `service_factory` **ohne Type Hint** lassen.
    *   Entferne direkten Import der konkreten `ServiceFactory` Klasse.
*   [ ] **Task 3.8 (Konkretisiert):** Überprüfe und aktualisiere (Imports ersetzen, Type Hints entfernen) für die Kernabhängigkeiten in folgenden Dateien:
    *   `app/tests/unit/bot/infrastructure/config/registries/test_component_registry.py`
    *   `app/bot/infrastructure/dashboards/dashboard_registry.py`
    *   `app/bot/infrastructure/startup/setup_hooks.py`
    *   `app/bot/infrastructure/factories/composite/workflow_factory.py` *(Prüfen!)*
    *   `app/bot/application/workflows/dashboard_workflow.py`
    *   `app/bot/interfaces/dashboards/components/common/selectors/generic_selector.py`
    *   `app/bot/interfaces/dashboards/components/common/embeds/dashboard_embed.py`
    *   `app/bot/infrastructure/startup/main.py`
    *   `app/bot/application/workflows/guild_template_workflow.py`
    *   *(Weitere Workflows/Commands/Services, die `bot`, `service_factory` oder `component_registry` direkt importieren oder als Type Hint verwenden)*

## Phase 4: Solidify Dependency Injection Wiring

*   [ ] **Task 4.1:** Review `app/bot/infrastructure/startup/setup_hooks.py` und `app/bot/infrastructure/startup/bot.py`:
    *   Sicherstellen, dass die konkreten Instanzen (`ComponentRegistry`, `ServiceFactory`) korrekt erstellt werden.
    *   Sicherstellen, dass diese Instanzen korrekt im `bot` (`FoundryCord`) gespeichert werden (`self.service_factory = ...`, `self.component_registry = self.service_factory.get_service('component_registry')`).
    *   Sicherstellen, dass der `bot` (als `self`) korrekt an abhängige Objekte (z.B. Workflows im `WorkflowManager`) übergeben wird.
*   [ ] **Task 4.2:** Review `app/bot/infrastructure/factories/service_factory.py`:
    *   Sicherstellen, dass `get_service` die **konkreten** Service-Instanzen zurückgibt.
*   [ ] **Task 4.3:** Review `app/bot/infrastructure/dashboards/dashboard_registry.py`:
    *   Im `__init__`: Sicherstellen, dass `bot`, `component_registry`, `service_factory` korrekt übergeben und gespeichert werden (ohne Type Hints).
    *   In `activate_or_update_dashboard`: Sicherstellen, dass `self.bot`, `self.component_registry` und der via `self.service_factory.get_service('dashboard_data_service')` geholte `data_service` korrekt an den `DashboardController.__init__` übergeben werden.

## Phase 5: Verification

*   [ ] **Task 5.1:** Entferne alle verbleibenden `TYPE_CHECKING` Blöcke, die NUR wegen der Zirkelabhängigkeiten zwischen Bot/Factory/Registry nötig waren.
*   [ ] **Task 5.2:** Static analysis (`mypy`, `pylint`) laufen lassen. Fehler bezüglich fehlender Type Hints für Bot/Factory/Registry ignorieren wir, andere Fehler beheben.
*   [ ] **Task 5.3:** Relevante Unit-Tests ausführen (z.B. `test_component_registry.py`, `test_dashboard_controller.py`, `test_service_factory.py`). Fehler beheben.
*   [ ] **Task 5.4:** Bot starten. Logs auf Fehler prüfen.
*   [ ] **Task 5.5:** Manuelles Testen der Kernfeatures (Dashboard-Anzeige, Commands). 