# Guild Designer TODO

## Core Functionality

### Phase 1: Saving Edited Structure

*   [ ] **Implement Frontend Save Logic:**
    *   **Capture Moves:** Enhance the `move_node.jstree` event handler in `app/web/static/js/views/guild/designer/widget/structureTree.js` to gather the new parent and position data for the moved node.
    *   **Track Changes:** Implement a mechanism (perhaps in `app/web/static/js/views/guild/designer/index.js`) to track that changes have been made and need saving.
    *   **Format Data:** Create a function (e.g., in `structureTree.js` or a new utility file) to traverse the current jsTree instance (`$(treeContainer).jstree(true).get_json('#', { flat: true })` might be useful) and format the *entire* structure (nodes with IDs, parents, positions) into a JSON payload suitable for the backend API.
    *   **Add Save Button:** Add a "Save Structure" button to `app/web/templates/views/guild/designer/index.html` (e.g., in the toolbar).
    *   **Trigger Save:** Add an event listener in `app/web/static/js/views/guild/designer/index.js` for the save button that calls the formatting function and sends the data to the new backend API endpoint. Handle loading/disabled states for the button.
*   [ ] **Create Backend Save API Endpoint:**
    *   **API Route:** Define a new route like `PUT /api/v1/templates/guilds/{template_id}/structure` in `app/api/v1/endpoints/guild_templates.py`. (Using PUT as we are replacing the structure of an existing template).
    *   **Payload Schema:** Create a Pydantic schema (e.g., `GuildStructureUpdatePayload` in `app/schemas/guild_template.py`) to validate the incoming JSON structure data (expecting a list of nodes with IDs, parent references, positions, potentially names/types if editing those too).
    *   **Service Logic:** Implement a service function (e.g., `update_template_structure` in `app/services/guild_template_service.py`) that:
        *   Takes the template ID and the validated payload.
        *   Carefully updates the `GuildCategoryTemplate` and `GuildChannelTemplate` records in the database based on the received structure. This might involve updating `parent_category_template_id` and `position` for existing items. Consider how to handle new/deleted items if the properties/toolbox panels are implemented. For now, focus on reordering/re-parenting existing items based on the tree data.
    *   **Database Interaction:** Ensure `guild_template_service.py` uses the SQLAlchemy session and models (`app/models/guild_template.py`) correctly to commit the changes.

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
