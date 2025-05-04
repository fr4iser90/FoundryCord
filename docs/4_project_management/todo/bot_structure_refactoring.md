# Bot Structure Refactoring TODO

**Goal:** Refactor the `app/bot` directory structure to align with the organizational patterns observed in `app/web` and `app/shared` (referencing `structure.md` and `tree.md`), improving clarity and maintainability.

**Related Documentation (Optional):**
*   `docs/4_project_management/todo/structure.md`
*   `docs/4_project_management/todo/tree.md`

## Phase 1: Analyse & Initial Restructuring Plan

*   [x] **Task 1:** Analyse `app/bot` structure against `app/web` and `app/shared` (using `tree.md` and `structure.md`). Identify key deviations and list components/modules needing relocation (e.g., services in `application/services` vs. directly in `application`, infrastructure components like factories, monitoring, etc.).
    *   **Affected Files:**
        *   See Analysis: `docs/4_project_management/analysis/structure_comparison.md`
*   [ ] **Task 2:** Define specific file/directory move/rename operations based on the structure analysis.
    *   **Affected Files:** (Proposed Plan)
        *   **Create `domain` Layer:**
            *   `mkdir app/bot/domain/`
        *   **Refactor `application` Layer:**
            *   `mkdir app/bot/application/services/`
            *   `mv app/bot/application/services/* app/bot/application/services/` (Excluding `__init__`, verify specific dirs: auth, category, channel, etc.)
            *   `mv app/bot/application/process app/bot/application/tasks`
            *   (Postpone Decision: `app/bot/application/decorators/`)
        *   **Refactor `core` Layer:**
            *   (Postpone Decision: `main.py`, `lifecycle_manager.py`, etc. -> `infrastructure/startup`?)
        *   **Refactor `infrastructure` Layer:**
            *   `mkdir app/bot/infrastructure/state/` (If not exists)
            *   `mv app/bot/infrastructure/state/collectors/* app/bot/infrastructure/state/collectors/` (Verify alignment with shared)
            *   `mv app/bot/infrastructure/state/bot_state_collectors.py app/bot/infrastructure/state/` (Or integrate)
            *   `mkdir app/bot/infrastructure/monitoring/` (If not exists)
            *   (Postpone Decision: Align `monitoring/*` with shared)
            *   (Postpone Decision: Consolidate/Move `component`, `data*`, `managers`, `messaging`)
            *   `mkdir app/bot/interfaces/api/` (If not exists)
            *   `mv app/bot/infrastructure/internal_api app/bot/interfaces/api/internal` (Rename to `internal`?)
            *   (Postpone Decision: Review `factories` structure)
            *   `mkdir app/bot/infrastructure/wireguard/` (Or feature module)
            *   `mv app/bot/database/wireguard app/bot/infrastructure/wireguard/`
            *   `mkdir app/bot/core/middleware/` (If not exists, or shared)
            *   `mv app/bot/infrastructure/rate_limiting app/bot/core/middleware/rate_limiting`
        *   **Refactor `interfaces` Layer:**
            *   (Postpone Decision: Major restructure needed, e.g., `api`/`views`)
        *   **Relocate Top-Level `utils`:**
            *   `mv app/bot/utils/vars.py` (Target TBD: module or shared)
            *   `rmdir app/bot/utils/` (After move)

## Phase 2: Implement Initial Moves

*   [ ] **Task:** [Placeholder]
    *   **Affected Files:**
        *   `path/to/file`

## General Notes / Future Considerations

*   [ ] Add any relevant notes here. 