# Guild Designer TODO

## Core Functionality

### Phase 1: Saving Edited Structure & Basic Actions

*   [x] **Implement Frontend Save Logic:**
    *   [x] **Capture Moves:** Enhanced `move_node.jstree` event handler.
    *   [x] **Track Changes:** Implemented dirty state tracking (`designerState.js`).
    *   [x] **Format Data:** Created `formatStructureForApi` in `designerUtils.js`.
    *   [x] **Add Save Button:** Added in `index.html`.
    *   [x] **Trigger Save:** Implemented `handleSaveStructureClick` in `designerEvents.js` (PUT).
    *   [x] **Save As New Modal:** Implemented (`saveAsNewModal.js`, `save_as_new_modal.html`).
    *   [x] **Handle Save As New:** Implemented listener for `saveAsNewConfirmed` in `designerEvents.js` (POST).
*   [ ] **Implement Frontend Logic for Toolbar "Activate" Button:**
    *   **Target File:** `designerEvents.js` (listener setup), `index.js`/`designerState.js` (state/button updates).
    *   **UI:** Add/uncomment "Activate" button in `index.html` toolbar.
    *   **Listener:** Add listener in `initializeDesignerEventListeners` (`designerEvents.js`) calling `handleToolbarActivateClick`.
    *   **Handler:** Implement `handleToolbarActivateClick` to call `POST /api/v1/templates/guilds/{template_id}/activate`, update state, update toolbar buttons via `updateButtonStates`, dispatch `templateActivated` event.
    *   **Consideration:** Add confirmation modal.
*   [ ] **Update Core State/Loading Logic for Activation:**
    *   **Target File:** `index.js` (or refactored core module), `designerState.js`.
    *   **Loading:** Update `loadTemplateStructure` (or equivalent) to fetch `is_active` status and store in `state`.
    *   **State:** Ensure `designerState.js` tracks `currentTemplateIsActive`.
    *   **Button States:** Update `updateButtonStates` to manage the *toolbar* button's state based on `currentTemplateIsActive`.
*   [ ] **Ensure `templateList.js` Updates on Activation:**
    *   **Target File:** `templateList.js`.
    *   **Listener:** Add listener for `templateActivated` event to re-initialize the list with the correct active indicator.
*   [x] **Create Backend Save API Endpoints:**
    *   [x] **API Route (PUT):** Defined `PUT /api/v1/templates/guilds/{template_id}/structure`.
    *   [x] **API Route (POST):** Defined `POST /api/v1/templates/guilds/from_structure`.
    *   [x] **Payload Schemas:** Created `GuildStructureUpdatePayload` & `GuildStructureTemplateCreateFromStructure`.
    *   [x] **Service Logic (PUT):** Implemented `update_template_structure`.
    *   [x] **Service Logic (POST):** Implemented `create_template_from_structure`.
    *   [x] **Database Interaction:** Ensured services use session correctly.
*   [ ] **Create Backend Activate API Endpoint:**
    *   [ ] **API Route (POST):** Define `POST /api/v1/templates/guilds/{template_id}/activate` in `guild_template_controller.py`.
    *   [ ] **Service Logic:** Implement `activate_template` in `template_service.py` to set `is_active` flag (ensure only one per guild).
    *   [ ] **Permissions:** Ensure only owner or GUILD ADMIN can activate.

### Phase 2: Applying Template to Discord

*   [ ] **Complete Bot `apply_template` Logic:**
    *   **Target File:** `app/bot/workflows/guild_workflow.py` (function `apply_template`).
    *   **Enhancements:**
        *   Fetch the full template structure (categories and channels with positions/parents) from the database using `GuildTemplateService`.
        *   Fetch the *current* guild structure directly from Discord using the Discord service (`app/services/discord_service.py` or similar).
        *   Implement comparison logic (diffing) between the template and the live Discord state.
        *   Call Discord API functions (via the service) to:
            *   Create missing categories/channels based on the template.
            *   Delete extra categories/channels not in the template (consider making this optional/configurable).
            *   Update names, topics, types if they differ.
            *   **Reorder** categories and channels using Discord's bulk update endpoints if possible, or individual position updates otherwise, to match the template's `position` and parent structure.
*   [ ] **Add "Apply Template" Trigger:**
    *   **UI Button:** Add an "Apply to Discord" button in `app/web/templates/views/guild/designer/index.html` (perhaps near the "Save" button, enabled only when the template is saved and active?).
    *   **Frontend Logic:** Add event listener in `app/web/static/js/views/guild/designer/index.js` for the apply button. It should likely call a new backend endpoint. Add confirmation dialog.
    *   **Backend API:** Create a new endpoint `POST /api/v1/guilds/{guild_id}/apply_template` (or similar) in `app/api/v1/endpoints/guilds.py`.
    *   **Trigger Workflow:** This API endpoint should call the `guild_workflow.apply_template` function, likely passing the `guild_id` and potentially the `active_template_id` associated with that guild.
*   [x] **Deletion Safety:**
    *   [x] **Prevent Initial Snapshot Deletion:** In `templateList.js`, disable the delete button for templates marked as `is_initial_snapshot`.
    *   [x] **Add Delete Confirmation Modal:** 
        *   [x] Create a Bootstrap modal (`delete_confirmation_modal.html`).
        *   [x] Create associated JS (`modal/deleteModal.js`) with `initializeDeleteModal` and `openDeleteModal(id, name)` functions.
        *   [x] Modify `templateList.js` and `sharedTemplateList.js` delete handlers to use events triggering `openDeleteModal`.
        *   [x] The modal's confirm button triggers the actual DELETE API call.
    *   [x] **Refresh List after Delete:** Ensure the template list widgets correctly refresh after a successful deletion triggered via the modal.


## UI/UX Enhancements (Lower Priority)

*   [ ] **Improve Visual Accuracy:**
    *   **Files:** `app/web/static/js/views/guild/designer/widget/structureTree.js`, `app/web/static/js/views/guild/designer/widget/channelsList.js`.
    *   **Task:** Adjust sorting/data generation to place uncategorized channels visually at the top.
*   [ ] **Properties Panel:**
    *   **Files:** `app/web/static/js/views/guild/designer/panel/properties.js`, `app/web/static/js/views/guild/designer/widget/structureTree.js`.
    *   **Task:** Implement UI for viewing/editing selected node properties (name, topic etc.). Integrate saving changes with the "Save Structure" API call (Phase 1).
*   [ ] **Toolbox Panel:**
    *   **Files:** `app/web/static/js/views/guild/designer/panel/toolboxList.js`, `app/web/static/js/views/guild/designer/widget/structureTree.js`.
    *   **Task:** Implement UI for dragging new elements. Integrate adding new elements with the "Save Structure" API call (Phase 1).
*   [ ] **Refine Share Modal:**
    *   **Files:** `app/web/templates/views/guild/designer/index.html`, `