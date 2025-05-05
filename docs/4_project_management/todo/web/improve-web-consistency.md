# Improve Web Consistency TODO (Revised & Safer Plan v2)

**Goal:** Align the `app/web` directory structure and naming conventions more closely with `app/bot` and `app/shared` by moving files and renaming directories, then accurately fixing imports **without deleting critical application logic**.

**Related Documentation:**

*   `docs/4_project_management/analysis/structure_comparison.md`
*   `docs/4_project_management/analysis/tree.md`
*   `docs/3_developer_guides/01_getting_started/coding_conventions.md`

## Phase 1: Carefully Relocate Core and Infrastructure Components

*   [ ] **Task 1.1:** Rename `app/web/infrastructure/setup/` directory to `app/web/infrastructure/startup/`.
    *   Action: `mv app/web/infrastructure/setup/ app/web/infrastructure/startup/`
*   [ ] **Task 1.2:** Move contents of the `app/web/core/` directory to their appropriate new locations in `application` or `infrastructure` layers. **DO NOT DELETE `app/web/core/` YET.**
    *   Action: `mkdir -p app/web/infrastructure/middleware`
    *   Action: `mv app/web/core/middleware/* app/web/infrastructure/middleware/`
    *   Action: `mkdir -p app/web/application/workflows`
    *   Action: `mv app/web/core/workflows/* app/web/application/workflows/`
    *   Action: `mkdir -p app/web/infrastructure/extensions`
    *   Action: `mv app/web/core/extensions/* app/web/infrastructure/extensions/`
    *   Action: **Move core application setup:** `mv app/web/core/main.py app/web/infrastructure/startup/main_app.py` (Verify file exists first)
    *   Action: **Move lifecycle:** `mv app/web/core/lifecycle_manager.py app/web/infrastructure/startup/lifecycle_manager.py` (Verify file exists first)
    *   Action: **Move workflow manager:** `mv app/web/core/workflow_manager.py app/web/application/workflow_manager.py` (Verify file exists first)
    *   Action: **Move exception handlers:** `mv app/web/core/exception_handlers.py app/web/infrastructure/startup/exception_handlers.py` (Verify file exists first)
    *   Action: **Move middleware registry:** `mv app/web/core/middleware_registry.py app/web/infrastructure/startup/middleware_registry.py` (Verify file exists first)
    *   Action: **Move router registry:** `mv app/web/core/router_registry.py app/web/infrastructure/startup/router_registry.py` (Verify file exists first)
    *   Action: Review `app/web/core/` for any other remaining files and move them appropriately.
*   [ ] **Task 1.3:** Evaluate `app/web/infrastructure/database/`. 
    *   Action: Check contents (`ls app/web/infrastructure/database/`). 
    *   Action: If **only** `__init__.py` exists, remove it: `rm -rf app/web/infrastructure/database/`. Otherwise, keep it.

## Phase 2: Identify Broken Imports

*   [ ] **Task 2.1:** Search the codebase (primarily `app/web` and `app/shared`) for Python import statements referencing the old paths:
    *   Search Pattern 1: `app.web.infrastructure.setup`
    *   Search Pattern 2: `app.web.core.middleware`
    *   Search Pattern 3: `app.web.core.workflows`
    *   Search Pattern 4: `app.web.core.extensions`
    *   Search Pattern 5: `app.web.core.main`
    *   Search Pattern 6: `app.web.core.lifecycle_manager`
    *   Search Pattern 7: `app.web.core.workflow_manager`
    *   Search Pattern 8: `app.web.core.exception_handlers`
    *   Search Pattern 9: `app.web.infrastructure.middleware_registry`
    *   Search Pattern 10: `app.web.core.router_registry`
    *   Search Pattern 11: `app.web.infrastructure.database` (If removed in 1.3)
    *   Action: List all files containing these imports.

## Phase 3: Determine Correct New Import Paths

*   [ ] **Task 3.1:** Analyze the search results from Phase 2 and the actual file moves performed in Phase 1.
*   [ ] **Task 3.2:** Create an accurate mapping of `old_import_path -> new_import_path` for each identified broken import.
    *   Example Mapping:
        *   `app.web.infrastructure.setup` -> `app.web.infrastructure.startup`
        *   `app.web.core.middleware` -> `app.web.infrastructure.middleware`
        *   `app.web.core.main` -> `app.web.infrastructure.startup.main_app` (Verify based on Task 1.2 outcome)
        *   ... etc. for all patterns found in Phase 2.

## Phase 4: Apply Import Fixes (Manual/IDE)

*   [ ] **Task 4.1:** Using the accurate mapping from Phase 3, perform the necessary Find/Replace operations in your IDE across the affected files.
    *   **Mapping (Old Path -> New Path):**
        *   `app.web.infrastructure.setup` -> `app.web.infrastructure.startup`
        *   `app.web.core.middleware` -> `app.web.infrastructure.middleware`
        *   `app.web.infrastructure.middleware_registry` -> `app.web.infrastructure.startup.middleware_registry`
        *   `app.web.core.workflows` -> `app.web.application.workflows`
        *   `app.web.core.extensions` -> `app.web.infrastructure.extensions`
        *   `app.web.core.main` -> `app.web.infrastructure.startup.main_app`
        *   `app.web.core.lifecycle_manager` -> `app.web.infrastructure.startup.lifecycle_manager`
        *   `app.web.core.workflow_manager` -> `app.web.application.workflow_manager`
        *   `app.web.core.exception_handlers` -> `app.web.infrastructure.startup.exception_handlers`
        *   `app.web.core.router_registry` -> `app.web.infrastructure.startup.router_registry`

## Phase 5: Standardize Interface Layer (Review Only)

*   [ ] **Task 5.1:** Review API routes under `app/web/interfaces/api/rest/v1/`. Check if grouping is logical. Note potential improvements, **do not change yet**.
*   [ ] **Task 5.2:** Review `app/web/interfaces/web/views/`. Check naming and structure consistency. Note potential improvements, **do not change yet**.

## Phase 6: Align Static & Templates (Review Only)

*   [ ] **Task 6.1:** Review `app/web/static/` subdirectories (`css`, `js`). Check naming and structure. Note potential improvements, **do not change yet**.
*   [ ] **Task 6.2:** Review `app/web/templates/` subdirectories. Check naming and structure. Note potential improvements, **do not change yet**.

## Phase 7: Verification & Documentation

*   [ ] **Task 7.1:** Attempt to run the web application locally (e.g., via Docker Compose) and test key features to ensure functionality after refactoring and import fixes.
*   [ ] **Task 7.2:** If Task 7.1 is successful, update `tree.md` and `structure_comparison.md` with the final structure.
*   [ ] **Task 7.3:** If Task 7.1 is successful, update relevant architecture documentation (`web_structure.md`, `backend_design.md`) to reflect the new structure and paths.

## Phase 8: Final Cleanup (Optional)

*   [ ] **Task 8.1:** ONLY AFTER verifying the application works correctly (Task 7.1): Check if `app/web/core/` is now empty. If it is, delete it: `rm -rf app/web/core/`.

## General Notes / Future Considerations

*   Consider if `app/web/application/dtos/` should live within specific service/feature folders in `application` or remain centralized.
*   Evaluate the necessity of the `app/web/infrastructure/factories/` layer - is it complex enough to warrant `base`/`composite` separation like the bot?
