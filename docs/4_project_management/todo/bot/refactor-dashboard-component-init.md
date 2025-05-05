# Refactor Dashboard Component Initialization/Registry Interaction TODO

**Goal:** Improve the orchestration of dashboard component creation and configuration loading to eliminate the circular import dependency between `ComponentRegistry`, `BaseComponent`, and various factories, making the architecture cleaner and tests easier to run.

**Related Documentation (Optional):**
*   `docs/3_developer_guides/02_architecture/bot_structure.md`

## Phase 1: Analysis & Decoupling `BaseComponent` Initialization

*   [ ] **Task 1.1:** Identify exactly where `BaseComponent` subclasses (like `DashboardEmbed`, `GenericButtonComponent`) are instantiated.
    *   Likely candidates: `app/bot/infrastructure/factories/component_factory.py`, `app/bot/interfaces/dashboards/controller/dashboard_controller.py`, `app/bot/infrastructure/dashboards/dashboard_registry.py`.
    *   Action: Use `read_file` or search tools to confirm the instantiation locations.
*   [ ] **Task 1.2:** Modify the instantiation logic identified in 1.1:
    *   Fetch the base definition dictionary from `ComponentRegistry.get_definition_by_key(...)` *before* creating the `BaseComponent` instance. Remember to access the actual definition via `['definition']`.
    *   Merge the fetched base definition (deep copy recommended) with the instance-specific settings/config (e.g., `instance_id`, `component_key`, `settings` from layout) to create a final, complete configuration dictionary. Ensure essential keys like `instance_id` and `component_key` are present in the final dict.
    *   Pass **only** this final, merged config dictionary to the `BaseComponent` subclass constructor (e.g., `DashboardEmbed(bot=bot, final_config=merged_config_dict)`). Modify constructors if needed.
*   [ ] **Task 1.3:** Modify `BaseComponent.__init__` to accept the pre-merged config dictionary directly.
    *   Remove the logic within `BaseComponent.__init__` that accesses `bot.component_registry` to fetch and merge the base definition itself.
    *   The `__init__` method should now primarily just store the passed final config dictionary in `self.config` and ensure essential keys like `visible`/`enabled` have defaults.
    *   **Affected Files:**
        *   `app/bot/interfaces/dashboards/components/base_component.py` (Will be modified)
        *   The file(s) identified in Task 1.1 that instantiate components (Will be modified)
        *   `app/bot/infrastructure/config/registries/component_registry.py` (Will NOT be modified, only used)

## Phase 2: Verification & Cleanup

*   [ ] **Task 2.1:** Run existing relevant tests (e.g., `test_dashboard_controller.py`) to ensure the refactoring didn't break dashboard display logic. Adapt tests if constructor signatures changed.
*   [ ] **Task 2.2:** Attempt to remove the `if TYPE_CHECKING:` guard around the `ComponentRegistry` import in `app/bot/infrastructure/factories/composite/bot_factory.py`.
*   [ ] **Task 2.3:** Run the previously failing `ComponentRegistry` tests (`test_component_registry.py`). They should now pass the import stage. Fix any test failures related to the changed instantiation logic if necessary.
*   [ ] **Task 2.4:** Manually test dashboard creation/display in the application to confirm functionality.

## Phase 3: Documentation (Optional)

*   [ ] **Task 3.1:** Update architecture diagrams or descriptions if the component initialization flow has significantly changed.

## General Notes / Future Considerations

*   Consider introducing an interface (`IComponentRegistry`) later if this decoupling isn't sufficient.
*   This refactoring should allow removing the `if TYPE_CHECKING:` guard around the `ComponentRegistry` import in `bot_factory.py`. 