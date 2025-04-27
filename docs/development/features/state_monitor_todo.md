# State Monitor Feature TODO

## Phase 1: Grundlage & Wichtige Verbesserungen

- [x] Implement Search/Filter function in `jsonViewer.js`.
- [x] Improve CSS styles in `json-viewer.css` for readability.
- [x] Implement automatic snapshot trigger on JS errors in `bridgeErrorHandler.js`.
- [x] Update `state_monitor.md` with completed Phase 1 features.

## Phase 2: Tiefere Integration & Kontext

- [x] Implement dedicated renderers for `consoleLogs` and `javascriptErrors` in `stateMonitorRenderer.js`.
- [x] Implement internal backend API endpoint to trigger server snapshots and log their IDs.
- [x] Extend `stateBridge.collectState` and callers to pass a `context` object.
- [x] Implement basic server-side snapshot storage (e.g., file/temp DB) and retrieval endpoint by ID.
- [x] Update `state_monitor.md` with completed Phase 2 features.

## Phase 3: Usability & Weitere Features

- [x] Implement a custom modal component for browser collector approval.
- [x] Implement Summary Panel in the UI.
- [ ] Add specific collectors for key features/modules as needed.
- [ ] (Optional) Implement snapshot comparison functionality.
- [ ] (Optional) Implement configurable auto-refresh interval/collectors.
- [ ] Update `state_monitor.md` with completed Phase 3 features.
