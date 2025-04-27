# Guild Designer TODO

## Core Functionality

*   [ ] **Implement Save Structure Logic:** Add frontend logic (likely triggered by `move_node.jstree` event in `structureTree.js` or a dedicated "Save" button) to capture the modified tree structure and send it to a new API endpoint.
*   [ ] **Create Save Structure API Endpoint:** Develop a backend API endpoint (e.g., `POST /api/v1/templates/guilds/{template_id}/structure`) to receive the modified structure data and update the corresponding `GuildCategoryTemplate` and `GuildChannelTemplate` records in the database (updating positions, parent categories, etc.).
*   [ ] **Complete Bot `apply_template` Logic:** Flesh out the `guild_workflow.apply_template` function to:
    *   Compare the target template structure with the current Discord server state.
    *   Create missing categories/channels.
    *   Delete extra categories/channels (optional, maybe configurable).
    *   Update names, topics, types where changed.
    *   **Crucially:** Reorder categories and channels within Discord to match the template positions.
    *   Handle permissions (basic implementation, perhaps copy from existing or default).
*   [ ] **Add "Apply Template" Trigger:** Implement a UI element (e.g., button in the designer or guild management page) and corresponding API endpoint/workflow call to trigger the `apply_template` function for the guild's active template.

## UI/UX Enhancements

*   [ ] **Improve Visual Accuracy:** Adjust `structureTree.js` and potentially `channelsList.js` sorting/display logic to more accurately reflect Discord's channel list order (uncategorized channels strictly at the top).
*   [ ] **Properties Panel:** Implement the right-hand "Properties" panel (`properties.js`) to allow editing details (name, topic, type?) of the selected category/channel in the Tree View. Saving these properties needs to integrate with the "Save Structure" logic.
*   [ ] **Toolbox Panel:** Implement the left-hand "Toolbox" panel (`toolboxList.js`) potentially allowing users to drag *new* category/channel elements onto the Tree View.
*   [ ] **Refine Share Modal:** Add better validation and feedback to the "Share Template" modal.
*   [ ] **Visual Feedback:** Provide clearer visual cues during drag-and-drop, saving, and applying operations.
*   [ ] **Error Handling:** Improve user-facing error messages for API failures during save/apply operations.
