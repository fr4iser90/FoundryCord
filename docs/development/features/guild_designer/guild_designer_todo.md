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
*   [x] **Implement Frontend Logic for Toolbar "Activate" Button:**
    *   [x] **Target File:** `designerEvents.js` (listener setup), `index.js`/`designerState.js` (state/button updates).
    *   [x] **UI:** Add/uncomment "Activate" button in `index.html` toolbar.
    *   [x] **Listener:** Add listener in `initializeDesignerEventListeners` (`designerEvents.js`) calling `handleToolbarActivateClick`.
    *   [x] **Handler:** Implement `handleToolbarActivateClick` to call `POST /api/v1/templates/guilds/{template_id}/activate`, update state, update toolbar buttons via `updateButtonStates`, dispatch `templateActivated` event.
    *   [x] **Consideration:** Add confirmation modal (`activateConfirmModal.js`, `activate_confirm_modal.html`).
*   [x] **Update Core State/Loading Logic for Activation:**
    *   [x] **Target File:** `index.js`, `designerState.js`, `designerEvents.js`.
    *   [x] **Loading:** Update `fetchGuildTemplate` (`index.js`) and `handleTemplateDataLoad` (`designerEvents.js`) to fetch/use `is_active` status and store in `state`.
    *   [x] **State:** Ensure `designerState.js` tracks `currentTemplateIsActive`.
    *   [x] **Button States:** Implement `updateToolbarButtonStates` in `designerEvents.js` to manage toolbar buttons based on `isDirty` and `currentTemplateIsActive`.
*   [x] **Ensure `templateList.js` Updates on Activation:**
    *   [x] **Target File:** `templateList.js`.
    *   [x] **Listener:** Add listener for `templateActivated` event to re-initialize the list with the correct active indicator (via `_renderTemplateList`).
    *   [x] **Refactor:** Activate button in list now dispatches `requestActivateTemplate`, handled by `designerEvents.js`.
*   [x] **Create Backend Save API Endpoints:**
    *   [x] **API Route (PUT):** Defined `PUT /api/v1/templates/guilds/{template_id}/structure`.
    *   [x] **API Route (POST):** Defined `POST /api/v1/templates/guilds/from_structure`.
    *   [x] **Payload Schemas:** Created `GuildStructureUpdatePayload` & `GuildStructureTemplateCreateFromStructure`.
    *   [x] **Service Logic (PUT):** Implemented `update_template_structure`.
    *   [x] **Service Logic (POST):** Implemented `create_template_from_structure`.
    *   [x] **Database Interaction:** Ensured services use session correctly.
*   [x] **Create Backend Activate API Endpoint:**
    *   [x] **API Route (POST):** Define `POST /api/v1/templates/guilds/{template_id}/activate` in `guild_template_controller.py`.
    *   [x] **Service Logic:** Implement `activate_template` in `template_service.py` to set `is_active` flag (ensure only one per guild).
    *   [x] **Permissions:** Ensure only owner or GUILD ADMIN can activate (Basic check implemented, comments added for future enhancement).

### Phase 2: Applying Template to Discord

*   [ ] **Complete Bot `apply_template` Logic:**
    *   **Target File:** `app/bot/core/workflows/guild_workflow.py` (function `apply_template`).
    *   **Enhancements:**
        *   [x] Fetch the full template structure (categories, channels, positions, parents, permissions etc.) from the database using the shared Template Repositories. (Implemented repository calls)
        *   [x] Fetch the *current* guild structure directly from Discord using the Discord service (`app/bot/application/services/discord/discord_query_service.py` created and used).
        *   [x] Implement comparison logic (diffing) between the template and the live Discord state. (Implemented via loops/checks in apply_template)
        *   [x] Call Discord API functions (via the service) to:
            *   [x] Create missing categories/channels based on the template.
            *   [ ] Delete extra categories/channels not in the template (consider making this optional/configurable). (Logic added, flag hardcoded to False)
            *   [x] Update names, topics, types if they differ.
            *   [ ] **Reorder** categories and channels using Discord's bulk update endpoints if possible, or individual position updates otherwise, to match the template's `position` and parent structure. (Basic position set on create/update, complex reorder pending)
        *   [x] Update `discord_channel_id` in DB. (Implemented via session commit)
*   [x] **Add "Apply Template" Trigger:**
    *   [x] **UI Button:** Add an "Apply to Discord" button in `app/web/templates/views/guild/designer/index.html`.
    *   [x] **Frontend Logic:** Add event listener in `app/web/static/js/views/guild/designer/designerEvents.js` for the apply button. Added confirmation dialog.
    *   [x] **Backend API:** Create a new endpoint `POST /api/v1/guilds/{guild_id}/template/apply` in `app/web/interfaces/api/rest/v1/guild/designer/guild_template_controller.py`.
    *   [x] **Trigger Workflow:** This API endpoint calls the `guild_workflow.apply_template` function.
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