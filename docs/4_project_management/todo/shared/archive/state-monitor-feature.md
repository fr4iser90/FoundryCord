# State Monitor Feature TODO

**Goal:** Implement a robust state monitoring system allowing manual and triggered snapshots (e.g., on JS errors) of frontend and potentially backend state, storing them in the database for debugging, and providing a UI to view and manage these snapshots.

**Related Documentation (Optional):**
*   `docs/features/state_monitor/state_monitor.md` (Needs update)

## Phase 1: Foundation & Key Improvements

*   [x] **Task 1.1:** Implement Search/Filter function in JSON Viewer.
    *   **Affected Files:**
        *   `app/web/static/js/components/common/jsonViewer.js`
*   [x] **Task 1.2:** Improve CSS styles for JSON Viewer readability.
    *   **Affected Files:**
        *   `app/web/static/css/components/json-viewer.css`
*   [x] **Task 1.3:** Implement automatic snapshot trigger on JS errors.
    *   **Affected Files:**
        *   `app/web/static/js/core/state-bridge/bridgeErrorHandler.js`
*   [x] **Task 1.4:** Update documentation with completed Phase 1 features.
    *   **Affected Files:**
        *   `docs/features/state_monitor/state_monitor.md`

## Phase 2: Deeper Integration, Context & DB Storage

*   [x] **Task 2.1:** Implement dedicated renderers for `consoleLogs` and `javascriptErrors`.
    *   **Affected Files:**
        *   `app/web/static/js/views/owner/state-monitor/panel/stateMonitorRenderer.js`
*   [x] **Task 2.2:** Extend state collection to include context.
    *   **Affected Files:**
        *   `app/web/static/js/core/state-bridge/stateBridge.js` (and callers)
*   [x] **Task 2.3:** Implement DB Storage - Define Model & Migration.
    *   **Affected Files:**
        *   `app/shared/infrastructure/models/monitoring/state_snapshot.py` (New or existing?)
        *   `app/shared/infrastructure/database/migrations/versions/010_create_state_snapshots_table.py`
*   [x] **Task 2.4:** Implement DB Storage - Backend service to save snapshots (with limits).
    *   **Affected Files:**
        *   `app/web/application/services/monitoring/state_snapshot_service.py` (New or existing?)
*   [x] **Task 2.5:** Implement DB Storage - Integrate `save_snapshot` into manual capture endpoint.
    *   **Affected Files:**
        *   `app/web/interfaces/api/rest/v1/owner/state_monitor_controller.py` (Endpoint: `POST /api/v1/owner/state/snapshot`)
*   [x] **Task 2.6:** Implement DB Storage - Create endpoint for frontend triggers (`/log-browser-snapshot`).
    *   **Affected Files:**
        *   `app/web/interfaces/api/rest/v1/owner/state_monitor_controller.py` (Endpoint: `POST /api/v1/owner/state/log-browser-snapshot`)
*   [x] **Task 2.7:** Add authentication to `/log-browser-snapshot` endpoint.
    *   **Affected Files:**
        *   `app/web/interfaces/api/rest/v1/owner/state_monitor_controller.py`
*   [x] **Task 2.8:** Implement internal backend API endpoint to trigger server snapshots.
    *   **Affected Files:** (Internal API definition/controller)
*   [x] **Task 2.9:** Implement DB Storage - Ensure internal trigger endpoint uses `save_snapshot`.
    *   **Affected Files:** (Internal API endpoint implementation)
*   [x] **Task 2.10:** Implement DB Storage - Backend service/repository functions for retrieval (`get_snapshot_by_id`, `list_recent_snapshots`).
    *   **Affected Files:**
        *   `app/web/application/services/monitoring/state_snapshot_service.py` (New or existing?)
        *   `app/shared/infrastructure/repositories/monitoring/state_snapshot_repository.py` (New or existing?)
*   [x] **Task 2.11:** Implement DB Storage - API endpoints for retrieval (`GET /snapshot/{id}`, `GET /snapshots/list`).
    *   **Affected Files:**
        *   `app/web/interfaces/api/rest/v1/owner/state_monitor_controller.py`
*   [x] **Task 2.12:** Update documentation with completed Phase 2 features.
    *   **Affected Files:**
        *   `docs/features/state_monitor/state_monitor.md`

## Phase 3: Usability & Further Features

*   [x] **Task 3.1:** Implement a custom modal component for browser collector approval.
    *   **Affected Files:** (JS/HTML for the new modal component)
*   [x] **Task 3.2:** Implement Summary Panel in the UI.
    *   **Affected Files:** (JS/HTML for the summary panel widget/component)
*   [x] **Task 3.3:** Implement UI widget/section to list recent snapshots.
    *   **Affected Files:** (JS/HTML for the snapshot list widget)
*   [x] **Task 3.4:** Implement UI functionality to load and display a selected snapshot.
    *   **Affected Files:** (JS logic in snapshot list and viewer widgets)
*   [ ] **Task 3.5:** Add specific collectors for key features/modules as needed.
    *   **Affected Files:** (Relevant feature JS modules, `stateBridge.js`)
*   [ ] **Task 3.6 (Optional):** Implement snapshot comparison functionality.
    *   **Affected Files:** (New comparison logic/UI components)
*   [ ] **Task 3.7 (Optional):** Implement configurable snapshot limit (N) for storage.
    *   **Affected Files:**
        *   `app/web/application/services/monitoring/state_snapshot_service.py`
        *   (Configuration file/mechanism)
*   [ ] **Task 3.8:** Update documentation with completed Phase 3 features.
    *   **Affected Files:**
        *   `docs/features/state_monitor/state_monitor.md`

## General Notes / Future Considerations

*   [ ] Ensure error handling is robust for snapshot creation and retrieval.
*   [ ] Consider performance implications of storing large snapshots.
*   [-] ~~Basic server-side file storage~~ (Superseded by DB approach).


