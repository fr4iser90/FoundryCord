# Toolbox & Channels List: Dashboard Drag-and-Drop TODO

**Goal:** Enable dragging "Saved Configuration" dashboards from the Toolbox panel and dropping them onto Text Channel items in the "Channels" list widget to automatically associate ("activate") the dashboard with that channel.

**Related Documentation (Optional):**
*   `app/web/static/js/views/guild/designer/panel/toolbox.js`
*   `app/web/static/js/views/guild/designer/widget/channelsList.js`

<!--
STATUS: New / Needs Refinement 
-->

## Phase 1: Make Saved Configurations Draggable

*   [ ] **Task 1.1:** Enhance Rendering of Saved Configurations in `toolbox.js`.
    *   **Depends on (Optional):** N/A
    *   **Affected Files (Optional):**
        *   `app/web/static/js/views/guild/designer/panel/toolbox.js`
        *   `app/web/static/css/views/guild/designer.css`
    *   **Definition of Done (DoD) (Optional):**
        *   In `renderToolboxComponents`, saved configurations are rendered as distinct, interactive objects:
            *   Use `<li>` elements with both `toolbox-item` AND `toolbox-load-config-item` classes to maintain draggability and click-to-load functionality
            *   Add `data-component-key` set to the config ID
            *   Add `data-component-type` set to `saved_dashboard_config`
            *   Store full configuration object as JSON string in `data-config-object`
        *   **WICHTIG:** Beim Draggen wird die Dashboard-Konfiguration als Data-Attribut am Helper-Element gespeichert (z.B. `ui.helper.data('dashboardConfig', configObj)`).
        *   Visual styling makes saved configurations appear as distinct, interactive objects:
            *   Add CSS styles to make them visually distinct from regular list items
            *   Include hover states and visual affordances indicating they are interactive
            *   Style should suggest both draggability and clickability
        *   Maintain existing click-to-load functionality while adding drag capability:
            *   Ensure click event listener in `initializeToolbox` still works with new class structure
            *   Verify no conflicts between click and drag initialization (nutze z.B. distance-Threshold)
            *   Test that both clicking to load and starting a drag operation work correctly

*   [ ] **Task 1.2:** Update `makeItemsDraggable` in `toolbox.js` for `dragstart`.
    *   **Depends on (Optional):** Task 1.1
    *   **Affected Files (Optional):**
        *   `app/web/static/js/views/guild/designer/panel/toolbox.js`
    *   **Definition of Done (DoD) (Optional):**
        *   Der Helper für Saved Configs speichert die Dashboard-Daten als Data-Attribut (`ui.helper.data('dashboardConfig', ...)`).
        *   Click und Drag sind sauber getrennt (z.B. mit distance: 5).
        *   Helper-Objekt zeigt nur Icon + Name.

## Phase 2: Implement Drop Target Logic (Channels List & Structure Tree)

*   [ ] **Task 2.1:** Add Drop Listeners to Text Channels in **Channels List** (`channelsList.js`).
    *   **Depends on (Optional):** N/A
    *   **Affected Files (Optional):**
        *   `app/web/static/js/views/guild/designer/widget/channelsList.js`
    *   **Definition of Done (DoD) (Optional):**
        *   Text channel `<li>` elements have `dragover`, `dragleave`, and `drop` event listeners.
        *   `dragover` calls `preventDefault()` and adds a highlight class (`.drop-target-active`).
        *   `dragleave` removes the highlight class.

*   [ ] **Task 2.2:** Implement Drop Handler Logic in **Channels List** (`channelsList.js`).
    *   **Depends on (Optional):** Task 1.2, Task 2.1
    *   **Affected Files (Optional):**
        *   `app/web/static/js/views/guild/designer/widget/channelsList.js`
    *   **Definition of Done (DoD) (Optional):**
        *   Der Drop-Handler liest die Dashboard-Daten aus `ui.helper.data('dashboardConfig')` aus.
        *   Es wird geprüft, ob der Drop auf einem Text-Channel erfolgt.
        *   State wird aktualisiert, UI und Toolbar werden geupdated, Success-Toast wird angezeigt.
        *   Drop-Highlight und Fehler-Feedback sind implementiert.

*   [ ] **Task 2.3:** Configure Drop Handling in **Structure Tree** (`structureTree.js`).
    *   **Depends on (Optional):** N/A
    *   **Affected Files (Optional):**
        *   `app/web/static/js/views/guild/designer/widget/structureTree.js`
    *   **Definition of Done (DoD) (Optional):**
        *   jsTree's DND (Drag and Drop) plugin is configured to allow dropping onto tree nodes representing text channels.
        *   Event listeners (e.g., `dnd_stop.vakata`, `move_node.jstree` or relevant jsTree DND events) are used to detect drops of external items (like dashboards from the toolbox).
        *   Visual highlighting is applied to text channel nodes during `dragover` (if feasible and consistent with jsTree's capabilities).

*   [ ] **Task 2.4:** Implement Drop Handler Logic in **Structure Tree** (`structureTree.js`).
    *   **Depends on (Optional):** Task 1.2, Task 2.3
    *   **Affected Files (Optional):**
        *   `app/web/static/js/views/guild/designer/widget/structureTree.js`
    *   **Definition of Done (DoD) (Optional):**
        *   Der Drop-Handler liest die Dashboard-Daten aus `ui.helper.data('dashboardConfig')` aus.
        *   Es wird geprüft, ob der Drop auf einem Text-Channel erfolgt.
        *   State wird aktualisiert, UI und Toolbar werden geupdated, Success-Toast wird angezeigt.
        *   Drop-Highlight und Fehler-Feedback sind implementiert.

*   [ ] **Task 2.5:** Add/Update CSS Styles for Drop Target Highlight (Tree & List).
    *   **Depends on (Optional):** Task 2.1, Task 2.3
    *   **Affected Files (Optional):**
        *   `app/web/static/css/views/guild/designer.css`
    *   **Definition of Done (DoD) (Optional):**
        *   CSS rules provide clear visual feedback for valid drop targets in both the Channels List widget and the Structure Tree widget. This might involve adjusting selectors or adding new ones specific to jsTree nodes.

## Phase 3: Refinements (Future Considerations)

*   [ ] **Task 3.1:** Improve visual feedback for non-text channels during drag (e.g., prevent highlight or show "not allowed").
*   [ ] **Task 3.2:** Add visual indicator to toolbox items when they are "in use" on one or more channels.

## General Notes / Future Considerations

*   Consider if other toolbox items (like API components) should also be draggable onto channels.
