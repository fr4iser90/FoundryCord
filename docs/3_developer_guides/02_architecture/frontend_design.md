# 2. Frontend Architecture & Design

This document describes the architecture and design principles for the FoundryCord frontend, which includes server-rendered Jinja2 templates and client-side JavaScript for interactivity and dynamic updates.

## Overview

*   **Core Technologies:**
    *   **Server-Side Templating:** [Jinja2](https://jinja.palletsprojects.com/) (rendered by the FastAPI backend) for initial page structure and data.
    *   **Client-Side Scripting:** Vanilla JavaScript (ES6+) for interactivity, DOM manipulation, and API communication.
    *   **Styling:** [Bootstrap 5](https://getbootstrap.com/) for responsive layout and core UI components, augmented by custom CSS.
    *   **Specialized UI Libraries:**
        *   [Gridstack.js](https://gridstackjs.com/): For creating draggable and resizable widget layouts (e.g., dashboards).
        *   [jsTree](https://www.jstree.com/): For displaying and interacting with hierarchical tree structures (e.g., Guild Designer channel/category list).
        *   [jQuery](https://jquery.com/): Primarily included as a dependency for jsTree and potentially for some older utility functions or Bootstrap components that might still rely on it.
*   **Build Process:** Currently, there is no dedicated JavaScript/CSS build tool (like Webpack or Vite) specified. Static assets are managed manually and served directly by FastAPI.
*   **Structure (`static/js/`):** Client-side JavaScript is organized into three main top-level directories under `static/js/`:
    *   `core/`: Global initialization (`main.js`), theme switching (`theme.js`), and potentially other core functionalities.
    *   `components/`: Contains potentially reusable UI components or logic (e.g., `components/common/notifications.js`, `components/guildSelector.js`, `components/layout/gridManager.js`).
    *   `views/`: Contains JavaScript specific to particular pages or sections of the application, mirroring the template structure (e.g., `views/guild/designer/`, `views/owner/state-monitor/`).
*   **`views/guild/designer/designerLayout.js`:** Handles the specific Gridstack initialization and layout loading/saving logic for the Guild Designer page, likely utilizing the more generic `components/layout/gridManager.js`.
*   **`components/layout/gridManager.js`:** Provides reusable core logic for managing Gridstack.js layouts across different parts of the application.
*   **`views/guild/designer/designerWidgets.js`:** Orchestrates the population and updating of content within the Gridstack widgets specific to the Guild Designer.

## Key Modules/Components

Describe the purpose of important JS modules, especially within the Guild Designer (`views/guild/designer/`):

*   **`core/main.js`:** Global entry point, likely handles initialization of theme, common components, etc.
*   **`views/guild/designer/index.js`:** Main entry point specifically for the Guild Designer page, orchestrates initialization of designer-specific modules.
*   **`views/guild/designer/designerState.js`:** Manages shared state specific to the designer (e.g., current template ID, name, dirty status, active status).
*   **`views/guild/designer/designerEvents.js`:** Centralized handling of custom events (`loadTemplateData`, `structureChanged`) and main toolbar button listeners (Save, Activate, etc.) within the designer.
*   **`views/guild/designer/designerUtils.js`:** Utility functions specifically used within the Guild Designer context.
*   **`views/guild/designer/designerWidgets.js`:** Orchestrates the population and updating of content within the Gridstack widgets specific to the designer.
*   **`views/guild/designer/widget/`:** Contains modules for individual Gridstack widgets within the designer (e.g., `templateList.js`, `structureTree.js`, `sharedTemplateList.js`).
*   **`views/guild/designer/modal/`:** Contains modules for individual Bootstrap modals used in the designer (e.g., `shareModal.js`, `deleteModal.js`, `saveAsNewModal.js`).
*   **`views/guild/designer/panel/`:** Contains modules responsible for the content of side panels within the designer (e.g., `properties.js`, `toolbox.js`).
*   **`components/common/notifications.js`:** Handles displaying toast-style notifications to the user.
*   **Utility Functions:** Utility functions tend to be scoped within specific view modules (e.g., `designerUtils.js`) or common component modules (e.g., `components/common/dateTimeUtils.js`) rather than a single top-level `utils/` directory.

## API Communication

*   Client-side JavaScript communicates with the backend REST API primarily using the browser's native **`fetch()` API**.
*   There is currently no standardized, project-wide wrapper module for API requests (e.g., a dedicated `apiRequest.js`). `fetch()` calls are typically made directly within the modules that require data or need to trigger backend actions.
*   Requests are made to endpoints defined in `app/web/interfaces/api/rest/v1/`. Authentication is handled via session cookies (see `api_specification.md`).

## Data Flow (Example: Guild Designer)

*   **Initial Load:** `core/main.js` initializes global elements. `views/guild/designer/index.js` fetches initial designer data, initializes specific components like the GridManager via `designerLayout.js`.
*   **Template Loading:** `views/guild/designer/widget/templateList.js` or `sharedTemplateList.js` fetch data via API, dispatch `loadTemplateData` event.
*   **Event Handling:** `views/guild/designer/designerEvents.js` listens for `loadTemplateData`, updates state via `designerState.js`, calls `designerWidgets.js` to populate widgets.
*   **Widget Population:** `views/guild/designer/designerWidgets.js` calls individual widget initializers (e.g., `initializeStructureTree` within `structureTree.js`).
*   **Structure Changes:** `views/guild/designer/widget/structureTree.js` detects changes via jsTree events, dispatches `structureChanged` event.
*   **Saving:** `views/guild/designer/designerEvents.js` listens for `structureChanged`, updates UI state (e.g., enabling save button) via `designerState.js` and potentially direct DOM manipulation. Save button click triggers API call (PUT/POST).

## State Management

*   **General Approach:** For most parts of the application, client-side state is managed locally within specific view modules or components. There is no global frontend state management library (like Redux or Vuex) currently in use.
*   **Guild Designer Specific State:** The more complex Guild Designer page utilizes a dedicated module, `views/guild/designer/designerState.js`, to manage its shared state (e.g., current template ID, name, dirty status, active status). This provides a more centralized state for this specific feature.
*   **UI Synchronization:** UI state (e.g., button enabled/disabled, content visibility) is synchronized with application state primarily through:
    *   Event listeners that trigger UI updates when specific custom events occur (common in the Guild Designer).
    *   Explicit function calls that update DOM elements or component properties based on state changes.

## Styling (`static/css/`)

*   Bootstrap 5 as base.
*   Custom CSS organized by components (`static/css/components/`) and views (`static/css/views/`). Matches the structure.
*   Theme support (`static/css/themes/`). Matches the structure. 