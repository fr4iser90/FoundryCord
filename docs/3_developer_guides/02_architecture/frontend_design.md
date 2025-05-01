# 2. Frontend Architecture

## Overview

Describe the overall approach for the frontend.
*   **Frameworks/Libraries:** Jinja2 for templating (server-side rendering via FastAPI), Vanilla JavaScript (ES6+), Bootstrap 5 for styling and basic components, Gridstack.js for widget layout, jsTree for structure visualization, jQuery (primarily as a dependency for jsTree).
*   **Structure:** JavaScript code is organized primarily into three top-level directories:
    *   `core/`: Global initialization (`main.js`), theme switching (`theme.js`), and potentially other core functionalities.
    *   `components/`: Contains potentially reusable UI components or logic (e.g., `components/common/notifications.js`, `components/guildSelector.js`, `components/layout/gridManager.js`).
    *   `views/`: Contains JavaScript specific to particular pages or sections of the application, mirroring the template structure (e.g., `views/guild/designer/`, `views/owner/state-monitor/`).

## Key Modules/Components

Describe the purpose of important JS modules, especially within the Guild Designer (`views/guild/designer/`):

*   **`core/main.js`:** Global entry point, likely handles initialization of theme, common components, etc.
*   **`views/guild/designer/index.js`:** Main entry point specifically for the Guild Designer page, orchestrates initialization of designer-specific modules.
*   **`views/guild/designer/designerState.js`:** Manages shared state specific to the designer (e.g., current template ID, name, dirty status, active status).
*   **`views/guild/designer/designerEvents.js`:** Centralized handling of custom events (`loadTemplateData`, `structureChanged`) and main toolbar button listeners (Save, Activate, etc.) within the designer.
*   **`views/guild/designer/designerUtils.js`:** Utility functions specifically used within the Guild Designer context.
*   **`views/guild/designer/designerLayout.js`:** Handles the specific Gridstack initialization and layout loading/saving logic for the Guild Designer page, likely utilizing `components/layout/gridManager.js`.
*   **`components/layout/gridManager.js`:** Provides the core reusable logic for managing Gridstack layouts.
*   **`views/guild/designer/designerWidgets.js`:** Orchestrates the population and updating of content within the Gridstack widgets specific to the designer.
*   **`views/guild/designer/widget/`:** Contains modules for individual Gridstack widgets within the designer (e.g., `templateList.js`, `structureTree.js`, `sharedTemplateList.js`).
*   **`views/guild/designer/modal/`:** Contains modules for individual Bootstrap modals used in the designer (e.g., `shareModal.js`, `deleteModal.js`, `saveAsNewModal.js`).
*   **`views/guild/designer/panel/`:** Contains modules responsible for the content of side panels within the designer (e.g., `properties.js`, `toolboxList.js`).
*   **`components/common/notifications.js`:** Handles displaying toast notifications.
*   **Utility Functions:** Utility functions tend to be scoped within specific views (like `designerUtils.js`) or components (`components/common/dateTimeUtils.js`) rather than a single top-level `utils/` directory. `apiRequest.js` seems missing or located elsewhere, potentially integrated into specific modules or needing creation.

## Data Flow

How does data flow through the frontend? (Conceptual flow remains largely the same, paths updated implicitly by module descriptions above)

*   **Initial Load:** `core/main.js` initializes global elements. `views/guild/designer/index.js` fetches initial designer data, initializes specific components like the GridManager via `designerLayout.js`.
*   **Template Loading:** `views/guild/designer/widget/templateList.js` or `sharedTemplateList.js` fetch data via API, dispatch `loadTemplateData` event.
*   **Event Handling:** `views/guild/designer/designerEvents.js` listens for `loadTemplateData`, updates state via `designerState.js`, calls `designerWidgets.js` to populate widgets.
*   **Widget Population:** `views/guild/designer/designerWidgets.js` calls individual widget initializers (e.g., `initializeStructureTree` within `structureTree.js`).
*   **Structure Changes:** `views/guild/designer/widget/structureTree.js` detects changes via jsTree events, dispatches `structureChanged` event.
*   **Saving:** `views/guild/designer/designerEvents.js` listens for `structureChanged`, updates UI state (e.g., enabling save button) via `designerState.js` and potentially direct DOM manipulation. Save button click triggers API call (PUT/POST).

## State Management

*   How is application state managed? Primarily decentralized within specific view modules. For the Guild Designer, state is managed within `views/guild/designer/designerState.js`.
*   How is UI state synchronized with application state? Mainly through event listeners and explicit function calls updating the DOM or component states (e.g., `updateButtonStates` in `designerEvents.js` reading from `designerState.js`).

## Styling

*   Bootstrap 5 as base.
*   Custom CSS organized by components (`static/css/components/`) and views (`static/css/views/`). Matches the structure.
*   Theme support (`static/css/themes/`). Matches the structure. 