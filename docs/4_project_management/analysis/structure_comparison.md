# Structure Comparison: app/bot vs. app/web vs. app/shared

**Goal:** Analyse the directory structures of `app/bot`, `app/web`, and `app/shared` based on `tree.md` to identify key differences and inform the refactoring plan for `app/bot`.

## Top-Level Directory Comparison

| Directory        | `app/bot` | `app/web` | `app/shared` | Notes                                                                 |
|------------------|-----------|-----------|--------------|-----------------------------------------------------------------------|
| `application`    | Yes       | Yes       | Yes          | Present in all.                                                        |
| `core`           | Yes       | Yes       | No (in tree) | `shared` might have core logic elsewhere, but not a top-level `core` dir. |
| `database`       | Yes       | No        | No (in infra)| `bot` has a specific `database/wireguard`. DB logic usually in `infra`.|
| `domain`         | No        | No        | Yes          | **Major difference:** Only `shared` has a dedicated domain layer.        |
| `infrastructure` | Yes       | Yes       | Yes          | Present in all.                                                        |
| `initializers`   | No        | No        | Yes          | Specific to `shared`.                                                  |
| `interfaces`     | Yes       | Yes       | Yes          | Present in all, but structure varies significantly.                  |
| `test` / `tests` | No (in tree)| No (in tree)| Yes (`test`) | Testing structure seems separate or not fully shown in `tree.md`.      |
| `utils`          | Yes       | No        | No           | `bot` has a top-level `utils`. Utils usually module-specific.        |

## Layer-Specific Analysis (`app/bot` Focus)

### `application` Layer (Bot)

*   **Services:** Located directly under `application/services/*`.
    *   _Comparison:_ `web` uses `application/services/*`, `shared` uses `application/services/*`.
    *   _Action:_ Move `bot` services into a dedicated `application/services/` subdirectory for consistency.
*   **Process:** Contains task definitions (`cleanup`, `security`).
    *   _Comparison:_ `web` has `application/tasks`. `shared` has `application/tasks`.
    *   _Action:_ Rename/move `bot/application/process` to `bot/application/tasks`.
*   **Decorators:** Contains `auth.py`, `respond.py`.
    *   _Comparison:_ Not directly comparable in `web`/`shared` `application` layers in the tree. May belong elsewhere (e.g., `interfaces` dependencies or `shared` utils).
    *   _Action:_ Review placement of decorators.

### `core` Layer (Bot)

*   Contains `main.py`, `lifecycle_manager.py`, `setup_hooks.py`, `shutdown_handler.py`, `workflow_manager.py`.
    *   _Comparison:_ `web`'s `core` contains `main.py`, `lifecycle_manager.py`, `middleware`, `extensions`. `shared` lacks a `core` dir. Some startup logic resides in `shared/infrastructure/startup`.
    *   _Action:_ Evaluate if `bot`'s core startup/lifecycle logic belongs in `infrastructure/startup` or a shared location. Consolidate `WorkflowManager`.
*   **Workflows:** Located under `core/workflows`.
    *   _Comparison:_ `web` also has `core/workflows`.
    *   _Action:_ Structure seems consistent, review specific workflow responsibilities later.

### `infrastructure` Layer (Bot)

*   **Component:** Contains `factory.py`, `registry.py`.
    *   _Comparison:_ `web`/`shared` don't show a top-level `component` directory in `infrastructure`. Related logic might be within `factories` or elsewhere.
    *   _Action:_ Review necessity/placement of this directory. Potentially merge into `factories`.
*   **Config:** Contains various config files.
    *   _Comparison:_ `web` has `infrastructure/config`. `shared` has `infrastructure/config`.
    *   _Action:_ Seems consistent, but review specific config file placement (e.g., `constants` structure).
*   **Dashboards:** Contains `dashboard_registry.py`.
    *   _Comparison:_ Specific to `bot`. Dashboard components/UI are typically `interfaces`. Core registry might be `infrastructure`.
    *   _Action:_ Review placement – is this purely infrastructure, or related to `interfaces/dashboards`?
*   **Data / Data Sources:** Contains registry and implementations.
    *   _Comparison:_ Not directly comparable in `web`/`shared` `infrastructure`. Might relate to `shared/domain/repositories` or specific service infrastructure.
    *   _Action:_ Review placement. Data access often belongs closer to `repositories`.
*   **Discord:** Contains `command_sync_service.py`, etc.
    *   _Comparison:_ Discord-specific infra.
    *   _Action:_ Seems reasonable placement for Discord platform interactions.
*   **Factories:** Contains multiple factory types.
    *   _Comparison:_ `web` and `shared` also have factories (though `shared` tree doesn't show them directly under `infrastructure`). Structure (`base`, `composite`, `discord`, `service`) seems complex.
    *   _Action:_ Ensure factory structure is consistent and logical across `bot`, `web`, `shared`.
*   **Internal API:** Contains `routes.py`, `server.py`.
    *   _Comparison:_ `web` handles APIs via `interfaces/api`.
    *   _Action:_ This likely belongs in `bot/interfaces/api` if it's an external-facing API, or needs renaming if truly internal communication.
*   **Managers:** Contains `dashboard_manager.py`.
    *   _Comparison:_ Unclear equivalent. Might be closer to `application` services or `core` workflows.
    *   _Action:_ Review purpose and placement.
*   **Messaging:** Contains `http_client.py`, `message_sender.py`.
    *   _Comparison:_ General utility, potentially `shared/infrastructure`?
    *   _Action:_ Review placement.
*   **Monitoring:** Contains `checkers`, `collectors`.
    *   _Comparison:_ `shared` has `domain/monitoring` and `infrastructure/state/collectors`. `web` doesn't show dedicated monitoring infra.
    *   _Action:_ Consolidate monitoring logic. Placement needs alignment with `shared`. Potentially move `collectors` definition to `domain` and implementation to `infrastructure`.
*   **Rate Limiting:** Contains middleware/service.
    *   _Comparison:_ `web` has `core/middleware`.
    *   _Action:_ Align placement, potentially under `core/middleware` or a shared middleware location.
*   **State:** Contains `bot_state_collectors.py`, `collectors`.
    *   _Comparison:_ `shared` has `infrastructure/state/collectors`.
    *   _Action:_ Align with `shared`. Move state collection logic to `infrastructure/state`.

### `interfaces` Layer (Bot)

*   **Commands:** Contains command handlers grouped by feature.
*   **Dashboards:** Contains dashboard UI components (`common`, `factories`, `ui`) and `controller`.
    *   _Comparison:_ `web` uses `interfaces/api` for data/logic and `interfaces/web/views` + `templates` + `static` for presentation. `bot` mixes UI components and controllers here.
    *   _Action:_ Major restructuring likely needed. Separate API/logic (controllers?) from presentation components. Align with `web`'s approach if applicable, or define a clear structure for bot-specific interfaces.

### Other (`bot`)

*   **`database/wireguard`:** Highly specific. Likely belongs within a `wireguard` feature module's infrastructure.
*   **`utils/vars.py`:** General utils should ideally be within specific modules or `shared`.
*   **Missing `domain` layer:** Core bot concepts, entities, and business logic lack a dedicated layer.

## Summary of Key Deviations & Areas for Refactoring (`app/bot`)

1.  **Missing `domain` Layer:** Introduce a `domain` layer for core bot entities, value objects, and potentially repository interfaces.
2.  **`application` Layer:**
    *   Create `services` subdirectory.
    *   Rename/move `process` to `tasks`.
    *   Re-evaluate `decorators` placement.
3.  **`core` Layer:**
    *   Review startup/lifecycle logic placement (consider `infrastructure/startup`).
    *   Consolidate `WorkflowManager`.
4.  **`infrastructure` Layer:**
    *   Align `monitoring` and `state` collectors with `shared` structure.
    *   Review/consolidate `component`, `data`/`data_sources`, `managers`, `messaging`.
    *   Move `internal_api` to `interfaces/api`.
    *   Review `factories` structure for consistency.
    *   Relocate `database/wireguard`.
    *   Align `rate_limiting` placement (e.g., `core/middleware`).
5.  **`interfaces` Layer:**
    *   Restructure significantly. Separate data/logic (controllers/API?) from presentation components. Consider adopting a pattern similar to `web` (`api`/`views`) if appropriate. Define clear boundaries.
6.  **Top-Level `utils`:** Relocate contents to relevant modules or `shared`. 