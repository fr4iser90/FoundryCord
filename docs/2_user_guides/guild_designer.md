# Guild Structure Designer

## Current Functionality

The Guild Structure Designer provides a web interface to manage and visualize Discord guild channel/category structures.

*   **Visualization:** Displays guild structures (categories, channels) based on saved data ("templates").
*   **Multiple Views:** Offers different views:
    *   Interactive Tree View (`structureTree.js`) using jsTree.
    *   List View for Categories (`categoriesList.js`).
    *   List View for Channels (`channelsList.js`).
    *   Basic Template Information (`templateInfo.js`).
*   **Editing (Structure):**
    *   Supports drag-and-drop reordering and re-parenting of existing categories and channels in the Tree View.
    *   Changes trigger a "dirty" state, enabling the "Save Structure" button.
*   **Saving Structures:**
    *   **Save Structure:** Saves the modified structure (node order and parentage) back to the *currently loaded template* using a `PUT` request. This fails with a permission error (403) if attempting to modify the initial guild snapshot.
    *   **Save As New Template:** If saving the initial snapshot fails due to permissions, a modal prompts the user to save the modified structure (preserving the currently displayed names, types, positions, and parent relationships) as a *new, separate template* under their account using a `POST` request.
*   **Template Management:**
    *   Lists user-saved templates and the initial guild snapshot (`templateList.js`).
    *   Lists globally shared templates (`sharedTemplateList.js`).
    *   Allows loading a template's structure into the designer view (by clicking the template name in the 'Saved Templates' list or the load button in the 'Shared Templates' list).
    *   Allows setting a template as "active" for the guild (marks it for potential future use by the bot).
    *   Allows saving copies of shared templates.
    *   Allows sharing user-saved templates.
    *   Allows deleting user-saved templates (excluding the initial snapshot) and owned shared templates.
    *   **Deletion Confirmation:** Uses a confirmation modal (`deleteModal.js`, `delete_modal.html`) for all delete operations to prevent accidental deletions.
*   **UI:** Uses Gridstack (`gridManager.js`) for a customizable, persistent widget-based layout.

## Bot Interaction & Data Storage

*   **Initial Snapshot:** When a guild is approved, the bot fetches the current structure from Discord, saves it as an "Initial Snapshot" template in the database, and marks it as active for the guild.
*   **Data Storage:**
    *   Templates (structure, categories, channels) are stored in relational database tables.
    *   UI layouts (widget positions, lock state) are saved separately per user/page.
    *   Guild configuration (e.g., active template, `template_delete_unmanaged` flag) is stored in `guild_configs` table.
*   **Applying Changes (Bot Side):** The backend function `apply_template` modifies the actual Discord server based on the *active* template for the guild. It currently supports:
    *   Creating missing categories and channels.
    *   Updating names and topics of existing categories/channels.
    *   Optionally deleting categories and channels that exist on Discord but are not in the template (controlled by the "Clean Apply" setting in the UI / `template_delete_unmanaged` flag in the database).
    *   Storing the corresponding Discord ID (`discord_channel_id`) in the template channel definition after creation/matching.
    *   **Detailed implementation notes for applying structures, managing related features like channel following, and interacting with the Discord API can be found in `structure_workflow.md` and `channel_follow_implementation.md`.**

## Current Limitations

*   **Property/Element Editing:** The designer currently only supports **reordering and re-parenting** existing elements via drag-and-drop. Editing properties (like names, topics) or adding/deleting categories/channels directly within the designer UI is **not implemented**.
*   **Applying Edits (Reordering):** The bot's `apply_template` function currently only sets the basic position during creation/update. Complex **reordering** of existing categories and channels to precisely match the template order is **not yet implemented**.
*   **Visual Accuracy:** The current views (especially the Tree View) do not perfectly replicate the Discord standard where uncategorized channels appear strictly at the top of the list.
*   **No "Undo" Functionality:** Changes made via "Apply to Discord" are direct and currently lack an undo mechanism. 