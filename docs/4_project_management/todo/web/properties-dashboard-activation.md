# Properties Panel: Dashboard Activation & Autocomplete TODO

**Goal:** Implement autocomplete for the dashboard selection input and disable/hide dashboard activation controls for voice channels within the Properties Panel of the Guild Designer.

**Related Documentation (Optional):**
*   `app/web/static/js/views/guild/designer/panel/properties.js`

<!--
STATUS: New / Needs Refinement 
-->

## Phase 1: Disable Dashboard Controls for Voice Channels

*   [ ] **Task 1.1:** Modify `populatePanel` function in `properties.js`.
    *   **Depends on (Optional):** N/A
    *   **Affected Files (Optional):**
        *   `app/web/static/js/views/guild/designer/panel/properties.js`
    *   **Definition of Done (DoD) (Optional):**
        *   When a voice channel node is selected in the designer, the 'Dashboard Aktivieren' switch and the 'Selected Dashboards' input area are hidden or disabled in the Properties Panel.
        *   When a text channel node is selected, these controls are visible and populated based on the channel's state (`is_dashboard_enabled` and `dashboard_config_snapshot`).

## Phase 2: Implement Autocomplete (Frontend - Basic)

*   [ ] **Task 2.1:** Add `debounce` import to `properties.js`.
    *   **Depends on (Optional):** N/A
    *   **Affected Files (Optional):**
        *   `app/web/static/js/views/guild/designer/panel/properties.js`
    *   **Definition of Done (DoD) (Optional):**
        *   `debounce` function from `designerUtils.js` is correctly imported.

*   [ ] **Task 2.2:** Implement Autocomplete Logic in `properties.js`.
    *   **Depends on (Optional):** Task 2.1
    *   **Affected Files (Optional):**
        *   `app/web/static/js/views/guild/designer/panel/properties.js`
    *   **Definition of Done (DoD) (Optional):**
        *   Add `input` event listener to dashboard input (`propDashboardAddInput`) triggering a debounced search function.
        *   Implement `handleDashboardSearchInput` to fetch all dashboard configs from `/api/v1/dashboards/configurations` and filter client-side.
        *   Implement `renderAutocompleteSuggestions` to display filtered suggestions in a dropdown (`.autocomplete-suggestions` div).
        *   Implement `handleAutocompleteSelection` to apply the selected dashboard (update state, render badges, clear input) when a suggestion is clicked.

*   [ ] **Task 2.3:** Add CSS Styles for Autocomplete Dropdown.
    *   **Depends on (Optional):** Task 2.2
    *   **Affected Files (Optional):**
        *   `app/web/static/css/views/guild/designer.css`
    *   **Definition of Done (DoD) (Optional):**
        *   CSS rules for `.autocomplete-suggestions` and its list items are added, making the dropdown visible and reasonably styled.

## Phase 3: Autocomplete Refinements (Future Considerations)

*   [ ] **Task 3.1:** Implement Keyboard Navigation for Autocomplete.
    *   **Affected Files (Optional):** `properties.js`
*   [ ] **Task 3.2:** Hide Autocomplete on Click Outside.
    *   **Affected Files (Optional):** `properties.js`
*   [ ] **Task 3.3:** Implement Backend Search API.
    *   **Affected Files (Optional):** Backend Controller for `/api/v1/dashboards/configurations`, `properties.js` (to use new endpoint)

## General Notes / Future Considerations

*   Backend validation should eventually be added to prevent saving dashboard assignments to voice channels via API.
