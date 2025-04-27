# Guild Designer TODO

## Core Functionality

### Phase 1: Saving Edited Structure

*   [x] **Implement Frontend Save Logic:**
    *   [x] **Capture Moves:** Enhance the `move_node.jstree` event handler in `app/web/static/js/views/guild/designer/widget/structureTree.js`.
    *   [x] **Track Changes:** Implement dirty state tracking (`designerState.js`) and enable/disable save button (`designerEvents.js`).
    *   [x] **Format Data:** Create `formatStructureForApi` in `designerUtils.js` to format tree data for the API.
    *   [x] **Add Save Button:** Added in `app/web/templates/views/guild/designer/index.html`.
    *   [x] **Trigger Save:** Implemented `handleSaveStructureClick` in `designerEvents.js` for the save button (PUT request).
    *   [x] **Save As New Modal:** Implement modal (`saveAsNewModal.js`) triggered on 403 error, dispatching `saveAsNewConfirmed` event.
    *   [x] **Handle Save As New:** Implement listener for `saveAsNewConfirmed` in `designerEvents.js` to trigger POST request.
*   [x] **Create Backend Save API Endpoints:**
    *   [x] **API Route (PUT):** Defined `PUT /api/v1/templates/guilds/{template_id}/structure` in `guild_template_controller.py`.
    *   [x] **API Route (POST):** Defined `POST /api/v1/templates/guilds/from_structure` in `guild_template_controller.py`.
    *   [x] **Payload Schemas:** Created `GuildStructureUpdatePayload` and `GuildStructureTemplateCreateFromStructure` in `guild_template_schemas.py`.
    *   [x] **Service Logic (PUT):** Implemented `update_template_structure` in `template_service.py` to handle reordering/re-parenting based on payload.
    *   [x] **Service Logic (POST):** Implemented `create_template_from_structure` in `template_service.py` to create a new template from structure payload.
    *   [x] **Database Interaction:** Ensured services use session and models correctly.

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
    *   **Files:** `app/web/templates/views/guild/designer/index.html`, `app/web/static/js/views/guild/designer/index.js`.
    *   **Task:** Add validation and feedback.
*   [ ] **Visual Feedback:** Provide clearer visual cues during drag-and-drop, saving, and applying operations across relevant JS files.
*   [ ] **Error Handling:** Improve user-facing error messages for API failures during save/apply operations in relevant JS files and potentially backend services.

## Specific Component TODOs

*   [ ] **Deletion Safety:**
    *   [ ] **Prevent Initial Snapshot Deletion:** In `templateList.js`, disable the delete button for templates marked as `is_initial_snapshot`.
    *   [ ] **Add Delete Confirmation Modal:** 
        *   Create a Bootstrap modal (`delete_confirmation_modal.html`).
        *   Create associated JS (`modal/deleteModal.js`) with `initializeDeleteModal` and `openDeleteModal(id, name)` functions.
        *   Modify `templateList.js` and `sharedTemplateList.js` delete handlers to call `openDeleteModal`.
        *   The modal's confirm button should trigger the actual DELETE API call.
    *   [ ] **(Optional) Refresh List after Delete:** Ensure the template list widgets correctly refresh after a successful deletion triggered via the modal.
