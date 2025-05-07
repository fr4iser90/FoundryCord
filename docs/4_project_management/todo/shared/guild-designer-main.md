# Guild Designer TODO

**Goal:** Implement a web-based visual editor for creating, managing, and applying guild structure templates (channels, categories, permissions) and associated dashboard configurations to Discord guilds.

**Related Documentation (Optional):**
*   [Structure Workflow documentation](../../3_developer_guides/04_feature_implementation/guild_designer/structure_workflow.md)
*   [Structure Workflow detailed TODO list](../../3_developer_guides/04_feature_implementation/guild_designer/structure_workflow_todo.md)

## Phase 1: Saving Edited Structure & Basic Actions

*   [x] **Implement Frontend Save Logic:**
    *   [x] **Capture Moves:** Enhanced `move_node.jstree` event handler.
    *   [x] **Track Changes:** Implemented dirty state tracking (`designerState.js`).
    *   [x] **Format Data:** Created `formatStructureForApi` in `designerUtils.js`.
    *   [x] **Add Save Button:** Added in `index.html`.
    *   [x] **Trigger Save:** Implemented `handleSaveStructureClick` in `designerEvents.js` (PUT).
    *   [x] **Save As New Modal:** Implemented (`saveAsNewModal.js`, `save_as_new_modal.html`).
    *   [x] **Handle Save As New:** Implemented listener for `saveAsNewConfirmed` in `designerEvents.js` (POST).
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/designerState.js`
        *   `app/web/static/js/views/guild/designer/designerUtils.js`
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
        *   `app/web/static/js/views/guild/designer/modal/saveAsNewModal.js`
        *   `app/web/templates/views/guild/designer/index.html`
        *   `app/web/templates/components/guild/designer/panel/save_as_new_modal.html`
*   [x] **Implement Frontend Logic for Toolbar "Activate" Button:**
    *   [x] **UI:** Add/uncomment "Activate" button in `index.html` toolbar.
    *   [x] **Listener:** Add listener in `initializeDesignerEventListeners` calling `handleToolbarActivateClick`.
    *   [x] **Handler:** Implement `handleToolbarActivateClick` to call API, update state/toolbar, dispatch event.
    *   [x] **Confirmation:** Add confirmation modal (`activateConfirmModal.js`, `activate_confirm_modal.html`).
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
        *   `app/web/static/js/views/guild/designer/index.js`
        *   `app/web/static/js/views/guild/designer/designerState.js`
        *   `app/web/static/js/views/guild/designer/modal/activateConfirmModal.js`
        *   `app/web/templates/views/guild/designer/index.html`
        *   `app/web/templates/components/guild/designer/panel/activate_confirm_modal.html`
*   [x] **Update Core State/Loading Logic for Activation:**
    *   [x] **Loading:** Update `fetchGuildTemplate` and `handleTemplateDataLoad` to use `is_active` status.
    *   [x] **State:** Ensure `designerState.js` tracks `currentTemplateIsActive`.
    *   [x] **Button States:** Implement `updateToolbarButtonStates`.
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/index.js`
        *   `app/web/static/js/views/guild/designer/designerState.js`
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
*   [x] **Ensure `templateList.js` Updates on Activation:**
    *   [x] **Listener:** Add listener for `templateActivated` event to re-initialize list.
    *   [x] **Refactor:** Activate button dispatches `requestActivateTemplate` handled by `designerEvents.js`.
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/widget/templateList.js`
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
*   [x] **Create Backend Save API Endpoints:**
    *   [x] **API Route (PUT):** Defined `PUT /api/v1/templates/guilds/{template_id}/structure`.
    *   [x] **API Route (POST):** Defined `POST /api/v1/templates/guilds/from_structure`.
    *   [x] **Payload Schemas:** Created `GuildStructureUpdatePayload` & `GuildStructureTemplateCreateFromStructure`.
    *   [x] **Service Logic (PUT):** Implemented `update_template_structure`.
    *   [x] **Service Logic (POST):** Implemented `create_template_from_structure`.
    *   [x] **Database Interaction:** Ensured services use session correctly.
    *   **Affected Files:**
        *   `app/web/interfaces/api/rest/v1/guild/designer/guild_template_controller.py`
        *   `app/web/interfaces/api/rest/v1/guild/designer/guild_template_schemas.py`
        *   `app/web/application/services/template/template_service.py`
        *   `app/shared/infrastructure/repositories/guild_templates.py` (Verify path)
*   [x] **Create Backend Activate API Endpoint:**
    *   [x] **API Route (POST):** Define `POST /api/v1/templates/guilds/{template_id}/activate`.
    *   [x] **Service Logic:** Implement `activate_template` to set `is_active` flag.
    *   [x] **Permissions:** Basic check implemented.
    *   **Affected Files:**
        *   `app/web/interfaces/api/rest/v1/guild/designer/guild_template_controller.py`
        *   `app/web/application/services/template/template_service.py`
*   [x] **Refactor Core Bot Workflows/Services:** Implemented session-based repository handling.
    *   **Affected Files:** (Various bot workflow/service files)

## Phase 2: Applying Template to Discord

*   [x] **Complete Bot `apply_template` Logic:**
    *   **Enhancements:**
        *   [x] Fetch full template structure from DB.
        *   [x] Fetch current guild structure from Discord.
        *   [x] Implement comparison logic (diffing).
        *   [x] Call Discord API functions (Create, Delete, Update names/topics/types).
        *   [ ] **Reorder** categories/channels (**Deferred: Future Sync Job**).
        *   [x] Update `discord_channel_id` in DB.
    *   **Affected Files:**
        *   `app/bot/core/workflows/guild/guild_workflow.py`
        *   `app/bot/application/services/discord/discord_query_service.py`
        *   `app/shared/infrastructure/repositories/guild_templates.py` (Verify path)
*   [x] **Add "Apply Template" Trigger:**
    *   [x] **UI Button:** Add "Apply to Discord" button.
    *   [x] **UI Setting:** Add "Clean Apply" (`template_delete_unmanaged`) checkbox.
    *   [x] **Frontend Logic:** Add event listener and confirmation dialog.
    *   [x] **Backend API (Apply):** Create `POST /api/v1/guilds/{guild_id}/template/apply`.
    *   [x] **Backend API (Settings):** Create `PUT /guilds/{guild_id}/template/settings`.
    *   [x] **Trigger Workflow:** Apply API calls `guild_workflow.apply_template`.
    *   **Affected Files:**
        *   `app/web/templates/views/guild/designer/index.html`
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
        *   `app/web/interfaces/api/rest/v1/guild/designer/guild_template_controller.py`
        *   `app/bot/core/workflows/guild/guild_workflow.py`
*   [x] **Deletion Safety:**
    *   [x] **Prevent Initial Snapshot Deletion:** Disable delete button for `is_initial_snapshot` templates.
    *   [x] **Add Delete Confirmation Modal:** Create modal and JS logic.
    *   [x] **Modify Delete Handlers:** Use events to trigger modal.
    *   [x] **Refresh List after Delete:** Ensure list widgets refresh.
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/widget/templateList.js`
        *   `app/web/static/js/views/guild/shared/sharedTemplateList.js` (Verify path)
        *   `app/web/static/js/views/guild/designer/modal/deleteModal.js`
        *   `app/web/templates/components/guild/designer/panel/delete_confirmation_modal.html`

## Phase 3: Full Designer Editing Capabilities

*   [ ] **Add Elements (Toolbox):**
    *   [x] **Toolbox UI:** Create draggable elements for new categories/channels.
    *   [ ] **Tree Drag-and-Drop:** Configure jsTree to accept drop Dashboards from Toolbox. (Also update PropertiesJs instantly then)
    *   [x] **Input Modal:** Create/use modal for naming new Dashboard.
    *   [x?] **Component Dashboard-Builder Drag-and-Drop:** Configure dashboardEditor to accept drop Component from Toolbox.
    *   [ ] **Frontend State:** Add temporary node, track in `state.pendingAdditions`, set dirty.
    *   [ ] **Backend API (POST):** Define endpoints for adding elements (or use `from_structure`?).
    *   [ ] **Backend Logic:** Implement service/repo methods to create DB entities.
    *   [ ] **Frontend Call:** Trigger POST calls directly after modal confirmation.
    *   [ ] **UI Update:** Update temp node with real ID after success.
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/panel/toolbox.js`
        *   `app/web/templates/components/guild/designer/panel/toolbox.html`
        *   `app/web/static/js/views/guild/designer/widget/structureTree.js`
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
        *   `app/web/application/services/template/template_service.py`
        *   `app/web/interfaces/api/rest/v1/guild/designer/guild_template_controller.py`
        *   `app/shared/infrastructure/repositories/guild_templates.py` (Verify path)
*   [ ] **Improve Widget Synchronization:**
    *   [ ] **Events:** Define clear events (`propertyUpdated`, `nodeDeleted`, `nodeAdded`).
    *   [ ] **Listeners:** Ensure all relevant widgets listen and update accordingly.
    *   **Affected Files:**
        *   All widget JS files (e.g., `structureTree.js`, `properties.js`, etc.)
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
        *   `app/web/static/js/views/guild/designer/designerState.js`

## Phase 4: Dashboard Configuration Builder (Designer)

*   **Goal:** Allow users to create and configure **Saved Dashboard Configurations** using predefined components. Provide a live preview. These configurations are independent saved states.
*   **Core Principle (Save/Share/Copy):** Creating/using saved/shared configurations creates independent copies in `dashboard_templates`. No persistent link/inheritance.
*   **Editing Scope:** Builder edits **Saved Configurations** (`dashboard_templates`). Editing live instances (`active_dashboards`) is future functionality.
*   [ ] **Database & Seeds:**
    *   [x] `dashboard_templates` table exists.
    *   [x] `dashboard_component_definitions` table exists and is seeded.
    *   [ ] Clarify: Schema for `dashboard_templates` (name, description, ID, `config` JSON) exists.
    *   **Affected Files:**
        *   `app/shared/infrastructure/models/dashboards/dashboard_template.py` (Verify name)
        *   `app/shared/infrastructure/database/seeds/dashboard_templates/`
*   [x] **Backend - Component API:**
    *   [x] **New Endpoint (`GET /api/v1/dashboards/components`):** Returns available components.
    *   **Affected Files:**
        *   `app/web/interfaces/api/rest/v1/dashboards/dashboard_component_controller.py` (Verify name)
        *   `app/web/application/services/dashboards/dashboard_component_service.py` (Verify name)
*   [ ] **Backend - Variables API (Optional/Placeholder):**
    *   [ ] **New Endpoint (`GET /api/v1/dashboards/variables`):** Returns available template variables.
    *   **Affected Files:** (New controller/service needed)
*   [x] **Backend - Saved Dashboard Configuration Management API:**
    *   **API Naming:** Endpoint prefix `/configurations` manages `dashboard_templates`.
    *   [x] **API Design:** Define CRUD endpoints (`POST`, `GET` list, `GET` single, `PUT`, `DELETE`).
    *   [x] **Service/Repo:** Implement logic using `DashboardConfigurationEntity`.
    *   **Affected Files:**
        *   `app/web/interfaces/api/rest/v1/dashboards/dashboard_configuration_controller.py` (Verify name)
        *   `app/web/application/services/dashboards/dashboard_configuration_service.py` (Verify name)
        *   `app/shared/infrastructure/repositories/dashboards/dashboard_configuration_repository.py` (Verify name)
        *   `app/shared/infrastructure/models/dashboards/dashboard_template.py` (Verify name/entity)
*   [ ] **Frontend - Toolbox Refactoring:**
    *   [x] **Implement Tabs:** Update HTML/JS for tabs ("Structure", "Dashboards").
    *   [x] **Fetch Components:** Load component definitions (`GET /api/v1/dashboards/components`).
    *   [x] **Display Components:** Show components in tab as draggable items.
    *   [ ] **Define Shared Cache:** Create mechanism (e.g., `designerComponentCache.js`).
    *   [ ] **Populate Cache:** Store fetched definitions in cache.
    *   [ ] **"Dashboards" Tab:**
        *   [x] Add "New Dashboard Config" item/button.
        *   [x] Add listener to button: Calls `POST .../configurations`, gets ID, dispatches `dashboardConfigCreated`.
        *   [ ] **Fetch Saved Configurations:** Call `GET .../configurations`.
        *   [ ] **Display Saved Configurations:** Render clickable list.
        *   [ ] **Add Click Listener:** Attach listener to list items.
        *   [ ] **Handle Click:** Fetch full config (`GET .../configurations/{id}`) and dispatch `dashboardConfigLoaded`.
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/panel/toolbox.js`
        *   `app/web/templates/components/guild/designer/panel/toolbox.html`
        *   `app/web/static/js/views/guild/designer/designerComponentCache.js` (New or state)
*   [ ] **Frontend - Dashboard Editor Widget (Builder):**
    *   [x] **Define Widget:** `dashboard-editor` defined.
    *   [x] **Register Widget:** Registered.
    *   [ ] **Update Widget Logic:**
        *   [ ] **Access Cache on Drop:** Look up definition from cache.
        *   [x] **Add `currentEditingDashboardId` state.**
        *   [x] **Listen for `dashboardConfigLoaded` event:** Update `currentEditingDashboardId`.
        *   [ ] **Handle Drop:** Store full component instance data in `this.components`.
        *   [ ] **Trigger Save:** Remove automatic save; only via Config Widget button.
    *   [ ] **UI Layout:** Design builder interface.
    *   [x] Implement drag-and-drop receiving.
    *   [ ] **Component Handling:** Render fields, allow reorder/remove, persist arrangement.
    *   [ ] **Variable Integration:** Fetch variables, provide UI.
    *   [ ] **Config Generation:** Generate `config` JSON on save.
    *   [ ] **Save/Load Logic:** Implement `loadDashboardConfig(configId)` and `saveDashboardConfig()`.
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/widget/dashboardEditor.js`
        *   `app/web/static/js/views/guild/designer/designerLayout.js`
        *   `app/web/static/js/views/guild/designer/designerWidgets.js`
        *   `app/web/static/js/views/guild/designer/designerState.js`
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
*   [ ] **Frontend - Dashboard Configuration Widget (Metadata Editor):**
    *   [x] **Define Widget:** `dashboard-configuration` defined.
    *   [x] **Register Widget:** Registered.
    *   [ ] **UI:** Create inputs for Name, Description, etc. Add "Save Configuration" button.
    *   [x] **Logic:**
        *   [x] Listen for `dashboardConfigLoaded` event: Update ID, load/display metadata.
        *   [ ] Implement Save: On button click, get values, call `PUT .../configurations/{id}`.
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/widget/dashboardConfiguration.js` (New or existing?)
        *   `app/web/static/js/views/guild/designer/designerLayout.js`
        *   `app/web/static/js/views/guild/designer/designerWidgets.js`
        *   `app/web/static/js/views/guild/designer/designerState.js`
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
*   [ ] **Frontend - Dashboard Preview Widget:**
    *   [x] **Define Widget:** `dashboard-preview` defined.
    *   [x] **Register Widget:** Registered.
    *   [x] **Update Logic:**
        *   [x] Listen for `dashboardConfigLoaded` event: Update ID, call `loadPreview(id)`.
    *   [ ] **Rendering Logic:**
        *   [ ] Implement `loadPreview(configId)`: Fetch config data, parse `config`.
        *   [ ] **Render:** Create HTML to approximate Discord look based on `config`.
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/widget/dashboardPreview.js`
        *   `app/web/static/js/views/guild/designer/designerLayout.js`
        *   `app/web/static/js/views/guild/designer/designerWidgets.js`
        *   `app/web/static/js/views/guild/designer/designerState.js`
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
*   [ ] **Frontend - Inter-Widget Communication:**
    *   [x] **Define State/Events:** Mechanism exists for `dashboardConfigLoaded`, `dashboardConfigCreated`.
    *   [x] **Implement Listeners/Dispatchers:** Ensure Toolbox, Editor, Config, Preview react.
    *   [ ] **Toolbox Dispatcher:** Ensure Toolbox correctly dispatches `dashboardConfigLoaded`.
    *   **Affected Files:**
        *   `app/web/static/js/views/guild/designer/designerState.js`
        *   `app/web/static/js/views/guild/designer/designerEvents.js`
        *   All relevant widget JS files.
*   [ ] **Save/Share/Copy Functionality (Backend):**
    *   [ ] **New Service/Endpoints:** Create dedicated service/API endpoints (e.g., `/share`, `/copy`).
    *   [ ] **DB Changes:** Add `is_shared`, `creator_user_id` flags/columns to `dashboard_templates`.
    *   [ ] **Copy Logic:** Implement deep copy mechanism for configurations.
    *   **Affected Files:** (New Service), `app/shared/infrastructure/models/dashboards/dashboard_template.py`
*   [ ] **Channel Assignment & Live Instances (Separate Task / Future):**
    *   [ ] Design UI/UX for assigning a Saved Configuration ID to a channel.
    *   [ ] Implement Bot logic (create `active_dashboards` entry, store template ID, render/manage).
    *   [ ] Design UI/UX and API for editing live instances.
    *   **Affected Files:** (New Bot logic, new UI components, new API endpoints)

## Phase 5: Guild Structure Template - Channel Dashboard Association

*   **Workflow:** Snapshotting Dashboard Configs into Channel Templates.
*   **Goal:** When associating a dashboard with a channel in the Guild Structure Designer, copy the selected master Dashboard Template's `config` JSON and store it directly within the `guild_template_channels` record for that channel. The live bot will use this copied config.
*   **Steps:**
    1.  [x] **Database Schema Change:** Modify migration `003`, update model `GuildTemplateChannelEntity`.
        *   **Affected Files:**
            *   `app/shared/infrastructure/database/migrations/versions/003_...py`
            *   `app/shared/infrastructure/models/guild_templates/guild_template_channels.py`
    2.  [x] **Backend API & Services:** Update schemas, services (`structure_service`, `query_service`), controller (`structure_controller`).
        *   **Affected Files:**
            *   `app/web/interfaces/api/rest/v1/guild/designer/guild_template_schemas.py`
            *   `app/web/application/services/template/structure_service.py` (Verify name)
            *   `app/web/application/services/template/query_service.py` (Verify name)
            *   `app/web/interfaces/api/rest/v1/guild/designer/structure_controller.py` (Verify name)
    3.  [x] **Frontend (Properties Panel - `properties.js`):**
        *   [x] **Modify `handleDashboardAddInputKeydown`:** Fetch templates, find by name, copy config, store snapshot in state, update display.
        *   [x] **Modify Display Logic (`renderDashboardBadges`):** Accept snapshot, display name/badge with remove button.
        *   [x] **Modify Remove Logic (`handleRemoveDashboardSnapshot`):** Update state to `null`.
        *   [x] **Update `populatePanel` / `resetPanel`:** Correctly read/clear snapshot.
        *   **Affected Files:**
            *   `app/web/static/js/views/guild/designer/widget/properties.js`
            *   `app/web/static/js/views/guild/designer/designerState.js`
            *   `app/web/static/js/views/guild/designer/designerEvents.js`
    4.  [x] **Bot Logic (Apply Template):** Modify workflow to read snapshot JSON from `guild_template_channels` and use it.
        *   **Affected Files:**
            *   `app/bot/core/workflows/guild/guild_workflow.py` (or relevant bot apply logic)

## Phase 6: Future Enhancements

*   [ ] **Implement Scheduled Template Sync Job:**
    *   [ ] **Scheduler Setup:** Set up bot-side scheduler.
    *   [ ] **Sync Workflow/Service:** Create new workflow/service.
    *   [ ] **Core Sync Logic:** Implement guild-specific execution, fetch template/live structure, diff, create/delete/update, implement reordering.
    *   [ ] **Reverse Sync (Flag-Based):** Detect unmanaged elements, check flag, create in template, remove flag.
    *   [ ] **Configuration:** Make interval/flags configurable.
    *   **Affected Files:** (New scheduler config, new workflow/service file)
*   [ ] **UI/UX Enhancements (Lower Priority):**
    *   [x] **Improve Visual Accuracy:** Adjust sorting for uncategorized channels.
        *   **Affected Files:**
            *   `app/web/static/js/views/guild/designer/widget/structureTree.js`
            *   `app/web/static/js/views/guild/designer/widget/channelsList.js`
    *   [ ] **Toolbox Panel:** Implement drag/drop for new elements, integrate with Save.
        *   **Affected Files:**
            *   `app/web/static/js/views/guild/designer/panel/toolbox.js`
            *   `app/web/static/js/views/guild/designer/widget/structureTree.js`
    *   [ ] **Refine Share Modal:** (Further details needed)
        *   **Affected Files:** `app/web/templates/views/guild/designer/index.html`

## General Notes / Future Considerations

*   Items previously under "--- Previous/Other Sections ---" have been integrated or are covered by future phases.
*   Ensure consistent use of `guild_template_id` vs. `dashboard_configuration_id` where appropriate.
*   Review permissions checks across all new API endpoints.
