# Improve Web Consistency TODO

**Goal:** Align the `app/web` directory structure and naming conventions more closely with `app/bot` and `app/shared` for better overall project consistency and maintainability.

**Related Documentation:**

*   `docs/4_project_management/analysis/structure_comparison.md`
*   `docs/4_project_management/analysis/tree.md`
*   `docs/3_developer_guides/01_getting_started/coding_conventions.md`

## Phase 1: Rename/Move Top-Level Infrastructure Components

*   [ ] **Task 1.1:** Rename `app/web/infrastructure/setup/` to `app/web/infrastructure/startup/` for consistency with `app/bot`.
*   [ ] **Task 1.2:** Move `app/web/core/` contents (extensions, middleware, workflows) to appropriate subdirectories within `app/web/application/` or `app/web/infrastructure/`.
    *   Potentially: `middleware` -> `app/web/infrastructure/middleware/`
    *   Potentially: `workflows` -> `app/web/application/workflows/`
    *   Potentially: `extensions` -> `app/web/infrastructure/extensions/` (or decide if they belong elsewhere)
*   [ ] **Task 1.3:** Evaluate if `app/web/infrastructure/database/` is needed or if `app/shared/infrastructure/database/` suffices. Remove if redundant.

## Phase 2: Standardize Interface Layer

*   [ ] **Task 2.1:** Ensure API routes under `app/web/interfaces/api/rest/v1/` are grouped logically by feature/domain, similar to how bot commands are organized.
*   [ ] **Task 2.2:** Review `app/web/interfaces/web/views/` - ensure consistent naming and structure, perhaps grouping by feature area more explicitly (e.g., `views/guild/designer/` is good).

## Phase 3: Align Static & Templates

*   [ ] **Task 3.1:** Review `app/web/static/` subdirectories (`css`, `js`). Ensure consistent naming conventions and structure within `components`, `core`, `views`.
*   [ ] **Task 3.2:** Review `app/web/templates/` subdirectories. Ensure similar consistency as static files.

## Phase 4: Verification & Refinement

*   [ ] **Task 4.1:** Run web application and test key features after refactoring.
*   [ ] **Task 4.2:** Update `tree.md` and `structure_comparison.md`.
*   [ ] **Task 4.3:** Update any relevant architecture or developer guide documentation.

## General Notes / Future Considerations

*   Consider if `app/web/application/dtos/` should live within specific service/feature folders in `application` or remain centralized.
*   Evaluate the necessity of the `app/web/infrastructure/factories/` layer - is it complex enough to warrant `base`/`composite` separation like the bot?
