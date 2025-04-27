# State Monitor Feature TODO

## Phase 1: Grundlage & Wichtige Verbesserungen

- [x] Implement Search/Filter function in `jsonViewer.js`.
- [x] Improve CSS styles in `json-viewer.css` for readability.
- [x] Implement automatic snapshot trigger on JS errors in `bridgeErrorHandler.js`.
- [x] Update `state_monitor.md` with completed Phase 1 features.

## Phase 2: Tiefere Integration & Kontext & DB Storage

- [x] Implement dedicated renderers for `consoleLogs` and `javascriptErrors` in `stateMonitorRenderer.js`.
- [x] Extend `stateBridge.collectState` and callers to pass a `context` object.
- [x] **DB Storage:** Define SQLAlchemy model `StateSnapshot` (`id`, `timestamp`, `trigger`, `context`, `snapshot_data`).
- [x] **DB Storage:** Create Alembic migration `010_create_state_snapshots_table.py`.
- [x] **DB Storage:** Implement backend service `save_snapshot` with logic to limit stored snapshots (e.g., delete oldest if count > N).
- [x] **DB Storage:** Integrate `save_snapshot` into manual capture endpoint (`/api/v1/owner/state/snapshot` POST, trigger: 'user_capture').
- [x] **DB Storage:** Create new backend endpoint (`/api/v1/owner/state/log-browser-snapshot`) for frontend triggers (e.g., JS errors) to call, which then uses `save_snapshot` (trigger: 'js_error').
- [ ] TODO: Add proper auth/security to /log-browser-snapshot endpoint later.
- [x] Implement internal backend API endpoint to trigger server snapshots and log their IDs.
- [x] **DB Storage:** Ensure internal trigger endpoint also uses `save_snapshot` (trigger: 'internal_api').
- [-] ~~Implement basic server-side snapshot storage (e.g., file/temp DB) and retrieval endpoint by ID.~~ (Superseded by DB approach)
- [x] **DB Storage:** Implement backend service/repository functions `get_snapshot_by_id` and `list_recent_snapshots`.
- [x] **DB Storage:** Implement/Update retrieval API endpoints (`/api/v1/owner/state/snapshot/{snapshot_id}` GET and `/api/v1/owner/state/snapshots/list` GET).
- [ ] Update `state_monitor.md` with completed Phase 2 features.

## Phase 3: Usability & Weitere Features

- [x] Implement a custom modal component for browser collector approval.
- [x] Implement Summary Panel in the UI.
- [ ] **DB Retrieval:** Implement UI widget/section to list recent snapshots from the `/list` endpoint.
- [ ] **DB Retrieval:** Implement UI functionality to load and display a selected snapshot from the list.
- [ ] Add specific collectors for key features/modules as needed.
- [ ] (Optional) Implement snapshot comparison functionality.
- [ ] (Optional) Implement configurable auto-refresh interval/collectors.
- [ ] (Optional) Implement configurable snapshot limit (N) for storage.
- [ ] Update `state_monitor.md` with completed Phase 3 features.


