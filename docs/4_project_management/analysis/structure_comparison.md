# Structure Comparison: app/bot vs. app/web vs. app/shared

**Goal:** Analyse the directory structures of `app/bot`, `app/web`, and `app/shared` based on the latest `tree.md` to identify key differences and track alignment progress.

## Top-Level Directory Comparison (Based on `tree.md` generated on [Date of Generation - Check `tree.md`])

| Layer/Directory  | `app/bot`           | `app/web`                     | `app/shared`                    | Notes                                                                    |
|------------------|---------------------|-------------------------------|---------------------------------|--------------------------------------------------------------------------|
| `application`    | Yes (Services, Tasks, Workflows) | Yes (Services, Tasks)         | Yes (Logging, Services, Tasks)  | Core application logic/services. Bot/Web have workflows.                    |
| `core`           | No (Merged into `infrastructure/startup`) | Yes (Web-specific setup, extensions) | No                              | Bot's core startup logic moved to `infra/startup`. Web has web-core.       |
| `domain`         | Yes (Currently empty) | No                            | Yes (Audit, Auth, Monitoring, Repos interfaces, Domain Services) | **DDD Alignment:** Bot domain exists, Shared holds common domain. Correct. |
| `infrastructure` | Yes (Bot-specific)  | Yes (Web-specific)            | Yes (Common DB, Models, Repos impl., Security, Logging, State etc.) | Clear separation of infra concerns.                                      |
| `interfaces`     | Yes (Commands, Dashboards, Internal API) | Yes (REST API, Web Views)     | Yes (`interface` - Singular)    | Clear separation of interface types. `shared` uses singular `interface`. |
| `static`         | No                  | Yes (CSS, JS)                 | No                              | Web frontend assets.                                                     |
| `templates`      | No                  | Yes (HTML Templates)          | No                              | Web frontend templates.                                                  |
| `initializers`   | No                  | No                            | Yes                             | Specific to `shared` initialization.                                     |
| `test`           | No                  | No                            | Yes (`test/infrastructure`)     | Test location seems specific to `shared` or outside these app dirs.        |

## Layer-Specific Analysis (Focus on Alignment and Structure)

### `application` Layer

*   **Services:** `bot`, `web`, and `shared` appropriately place services here, often structured by feature/domain (e.g., `bot/application/services/category`, `web/application/services/guild`). **Status:** Good alignment.
*   **Tasks:** `bot` uses `tasks/process`, while `web`/`shared` use `tasks`. **Action:** Consider renaming `bot/application/tasks/process` to `bot/application/tasks` for consistency.
*   **Workflows:** Present in `bot` and `web` (`core/workflows` in web's case, `application/workflows` in bot's). This reflects application-specific orchestration logic. `bot`'s structure with subdirectories for complex workflows is good. **Status:** Appropriate placement.
*   **Logging (Shared):** `shared/application/logging` holds common log config. **Status:** Correct.

### `domain` Layer

*   **`bot/domain`:** Exists but is empty. Correctly established placeholder for future Bot-specific domain logic/entities not suitable for `shared`. **Status:** Good.
*   **`shared/domain`:** Rich with core entities, repository interfaces, domain services (Auth, Audit, Monitoring), etc. Correctly serves as the common domain model. **Status:** Good.

### `infrastructure` Layer

*   **Separation:** Clear separation between `bot` (Discord interactions, bot monitoring collectors, bot state), `web` (OAuth, web setup), and `shared` (Database, ORM Models, Repo Implementations, Encryption, common Logging/State). **Status:** Good alignment.
*   **`bot/infrastructure/factories`:** The `base`/`composite` structure seems reasonable for managing bot factory complexity. **Status:** Okay.
*   **`bot/infrastructure/monitoring` & `state`:** Correctly holds implementation details for checkers, collectors specific to the bot. **Status:** Good.
*   **`shared/infrastructure/models`:** Contains SQLAlchemy models (Entities). Correct placement for data mapping infrastructure. **Status:** Good.
*   **`shared/infrastructure/repositories`:** Contains repository implementations. Correctly separated from domain interfaces. **Status:** Good.

### `interfaces` Layer

*   **Separation:** Clear distinction: `bot` handles Discord commands, dashboard interactions (components/controller), and an internal API. `web` handles the REST API and HTML views. **Status:** Good alignment.
*   **`bot/interfaces/dashboards`:** The separation into `components` and `controller` is a good pattern. **Status:** Good.
*   **`shared/interface` (Singular):** Contains logging API/factories. The singular form is slightly inconsistent with the other `interfaces` directories. **Action:** Consider renaming to `interfaces` for consistency, or keep as is if intended.

## Summary & Conclusion

The current structure shows **significant progress** towards a clean, well-defined architecture:

*   **DDD Alignment:** The `app/bot` structure now strongly aligns with DDD principles (`application`, `domain`, `infrastructure`, `interfaces`), mirroring the structure established in `app/shared`.
*   **Clear Boundaries:** Responsibilities are well-separated between `bot`, `web`, and `shared` across all major layers.
*   **Consistency:** High level of consistency in structuring services, repositories, and infrastructure components.

**Minor Refinement Points:**

1.  Rename `app/bot/application/tasks/process` to `app/bot/application/tasks`.
2.  Consider renaming `app/shared/interface` to `app/shared/interfaces` for naming consistency across top-level directories.

Overall, the refactoring appears successful in achieving a much cleaner and more maintainable structure for the `app/bot` component, integrating well with `app/web` and `app/shared`. 