# Guild Structure Designer

## Current Functionality

The Guild Structure Designer provides a web interface to manage and visualize Discord guild channel/category structures.

*   **Visualization:** Displays guild structures (categories, channels) based on saved data ("templates").
*   **Multiple Views:** Offers different views:
    *   Interactive Tree View (`structureTree.js`) using jsTree.
    *   List View for Categories (`categoriesList.js`).
    *   List View for Channels (`channelsList.js`).
    *   Basic Template Information (`templateInfo.js`).
*   **Template Management:**
    *   Lists user-saved templates and the initial guild snapshot (`templateList.js`).
    *   Lists globally shared templates (`sharedTemplateList.js`).
    *   Allows loading a template's structure into the designer view.
    *   Allows setting a template as "active" for the guild (marks it for potential future use by the bot).
    *   Allows saving copies of shared templates.
    *   Allows sharing user-saved templates.
    *   Allows deleting user-saved templates (excluding the initial snapshot) and owned shared templates.
*   **UI:** Uses Gridstack (`gridManager.js`) for a customizable, persistent widget-based layout.

## Bot Interaction & Data Storage

*   **Initial Snapshot:** When a guild is approved, the bot fetches the current structure from Discord, saves it as an "Initial Snapshot" template in the database, and marks it as active for the guild.
*   **Data Storage:**
    *   Templates (structure, categories, channels) are stored in relational database tables.
    *   The active template for a guild is linked (e.g., `active_template_id` on the guild record).
    *   UI layouts (widget positions, lock state) are saved separately per user/page.
*   **Applying Changes (Bot Side - Incomplete):** The backend function `apply_template` is intended to modify the actual Discord server based on a template. Currently, its implementation is very basic and does **not** fully support creating, updating, deleting, or reordering channels/categories based on the template data.

## Current Limitations

*   **Editing:** While the Tree View visually supports drag-and-drop, the **logic to save the modified structure is not implemented**.
*   **Applying Edits:** The bot's `apply_template` function is **incomplete** and cannot yet translate a saved template structure into actual changes on the Discord server.
*   **Visual Accuracy:** The current views (especially the Tree View) do not perfectly replicate the Discord standard where uncategorized channels appear strictly at the top of the list.