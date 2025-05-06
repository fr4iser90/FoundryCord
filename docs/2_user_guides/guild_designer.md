# User Guide: Guild Structure Designer

Welcome to the [FoundryCord](../1_introduction/glossary.md#foundrycord) [Guild Structure Designer](../1_introduction/glossary.md#guild-designer)! This powerful tool allows you to visualize, create, manage, and apply templates to define the structure of your Discord servers ([guilds](../1_introduction/glossary.md#guild)), including categories and channels.

**With the [Guild Designer](../1_introduction/glossary.md#guild-designer), you can:**

*   Visualize your current server setup.
*   Create reusable templates from your existing server or from scratch (future enhancement).
*   Modify templates by reordering categories and channels.
*   Apply these templates to your Discord server, letting the FoundryCord bot automatically create or update the structure.
*   Share your templates with others (future enhancement) or use templates shared by the community.

This guide will walk you through how to use the Guild Designer effectively.

## Accessing the Guild Designer

1.  Log in to the FoundryCord web interface.
2.  Select the Discord server ([guild](../1_introduction/glossary.md#guild)) you wish to manage from the Guild Selector (usually at the top of the page or in the navigation bar).
3.  Navigate to the "Guild Designer" or "Structure Designer" section. This is typically found in the main navigation menu for your selected guild.
    `[SCREENSHOT: Main navigation menu highlighting Guild Designer link after guild selection]`

## Understanding the Interface

The Guild Designer interface is typically composed of several key areas:
`[SCREENSHOT: Guild Designer Main UI with annotations for each panel described below]`

*   **A. Template List Panel:**
    *   **Your Templates:** Shows a list of templates you have saved, including the "Initial Snapshot" which is a representation of your server when it was first added to FoundryCord.
    *   **Shared Templates:** Lists templates shared by other users that you can view and copy (future enhancement for full sharing).
    *   **Actions:** Allows you to load, activate, save copies of, share, or delete templates.
*   **B. Structure View/Editor Panel:**
    *   This is the main area where the category and channel structure of the currently loaded template is displayed.
    *   It often uses an interactive tree view where you can see the hierarchy.
    *   **Current Capability:** You can drag and drop categories and channels to reorder them or move channels between categories.
*   **C. Properties Panel (Contextual):**
    *   When you select a category or channel in the Structure View, this panel would typically show its properties (name, topic, type, permissions). *(Current Limitation: Direct editing of these properties in this panel is mostly not yet implemented; changes are primarily structural via drag-and-drop.)*
*   **D. Action Toolbar/Buttons:**
    *   **Load Template:** (Usually done by clicking a template in the list).
    *   **Save Structure:** Saves changes made to the currently loaded template (if it's not the read-only "Initial Snapshot").
    *   **Save As New Template:** Allows you to save the current structure (whether from an existing template or the initial snapshot) as a brand new template under your account.
    *   **Set Active / Apply to Discord:** Marks the loaded template as the one the bot should use for the guild and triggers the bot to apply this structure to your live Discord server.
    *   **Clean Apply (Toggle/Checkbox):** An option related to "Apply to Discord." When enabled, the bot will delete categories and channels on your Discord server that are not defined in the template being applied. If disabled, it will only create/update and leave unmanaged elements alone.

## Core Use Cases: Step-by-Step

### 1. Viewing Your Current Server Structure

FoundryCord automatically takes an "Initial Snapshot" of your server's structure when it's first added.

1.  Access the Guild Designer for your server (as described above).
2.  In the "Your Templates" list, the template named "Initial Snapshot" (or similar) should be present. It might be loaded by default, or you may need to click on it to load its structure into the Structure View panel.
3.  You can now see a representation of your server's categories and channels as of that initial snapshot.
    `[SCREENSHOT: Guild Designer showing the 'Initial Snapshot' loaded in the structure view]`

### 2. Creating a New Template from Your Current Server

This is useful for taking your existing server setup and saving it as a reusable template that you can later modify or apply to other servers (if that feature becomes available).

1.  Ensure the "Initial Snapshot" of your server is loaded in the Guild Designer (see previous step).
2.  If you've made any drag-and-drop modifications to this view and want to save them as part of your new template, do so now.
3.  Click the **"Save As New Template"** button.
4.  A modal window will appear, prompting you to enter a name and an optional description for your new template.
    `[SCREENSHOT: 'Save As New Template' modal dialog]`
5.  Enter a descriptive name (e.g., "My Gaming Community Base," "Project Team Server Layout").
6.  Click "Save."
7.  Your new template will now appear in the "Your Templates" list.

### 3. Modifying an Existing Template

You can modify templates you have previously saved (you cannot directly save changes to the "Initial Snapshot" or shared templates you don't own – use "Save As New Template" or "Save a Copy" for those).

1.  In the "Your Templates" list, click on the template you wish to modify. Its structure will load into the Structure View panel.
2.  **Reordering Categories and Channels:**
    *   In the Structure View (often a tree view), you can click and drag categories or channels to change their order or move channels into different categories.
        `[GIF: Dragging a channel from one category to another, and reordering channels within a category]`
    *   As you make changes, the designer will enter a "dirty" state, usually indicated by the "Save Structure" button becoming enabled.
3.  **Editing Properties (Current Limitation):**
    *   Currently, direct editing of properties like category/channel names, topics, types, or specific permissions *within the designer UI itself* is generally **not implemented**. The primary modification supported is structural reordering and re-parenting.
4.  **Saving Your Changes:**
    *   Once you are satisfied with the structural changes, click the **"Save Structure"** button.
    *   This will update the currently loaded template with your modifications.
    *   If you try to save the "Initial Snapshot," you will likely receive a permission error, prompting you to use "Save As New Template" instead.

### 4. Applying a Template to Your Discord Server

This is where the bot takes action on your live Discord server based on the selected template.

1.  Load the template you wish to apply into the Guild Designer (from "Your Templates" or a copy of a shared template).
2.  **Set as Active:** There is usually an option or button to "Set as Active" or similar. This tells FoundryCord that this is the template the bot should use for this guild.
    `[SCREENSHOT: Highlighting the 'Set Active' button for a loaded template]`
3.  **Understand "Clean Apply":** Locate the "Clean Apply" option (often a checkbox or toggle near the "Apply" button). 
    *   **If checked/enabled:** When the bot applies the template, it will delete any categories and channels on your Discord server that are *not* defined in the template. **Use with caution!**
    *   **If unchecked/disabled:** The bot will only create new categories/channels defined in the template and update existing ones it manages. It will not delete unmanaged elements.
4.  Click the **"Apply to Discord"** (or similar) button.
5.  Confirm the action if prompted. The bot will then begin processing the template and making changes to your Discord server. This may take a few moments depending on the complexity of the template.
6.  You should see changes reflected in your Discord server. The bot may also provide feedback in a log channel or via a web notification about the status of the application.

### 5. Managing Your Templates

Once you have created templates, you can manage them from the "Your Templates" list in the Guild Designer.

*   **Loading a Template:** Click on any template name in the list to load its structure into the main view.
*   **Deleting a Template:**
    1.  Find the template you wish to delete in the "Your Templates" list.
    2.  There will typically be a delete icon (e.g., a trash can) or a delete option in a context menu associated with the template.
        `[SCREENSHOT: Template list item showing a delete button/icon]`
    3.  Click the delete button/option.
    4.  A confirmation modal will appear to prevent accidental deletion. Read the confirmation carefully.
        `[SCREENSHOT: Delete template confirmation modal]`
    5.  Confirm the deletion. The template will be removed from your list.
    *   *Note: You typically cannot delete the "Initial Snapshot" template.*
*   **Sharing Templates (Future Enhancement):**
    *   The ability to easily share your templates with other FoundryCord users or make them publicly available might be a future enhancement. Currently, any "shared templates" listed are likely pre-defined or globally available.

### 6. Using Shared Templates (If Available)

If there is a "Shared Templates" list visible:

1.  **Browsing:** You can browse this list to see templates created by others or provided by default.
2.  **Loading to View:** Click on a shared template name or a "Load" button associated with it to view its structure in the designer. You typically cannot directly edit or save changes to these shared templates.
3.  **Saving a Copy:** If you like a shared template and want to customize it or use it as a base, look for an option like "Save a Copy" or "Copy to My Templates." This will create a new template under "Your Templates" that you own and can modify.
    `[SCREENSHOT: Shared template list item showing a 'Save a Copy' button/icon]`

## Understanding Template Application by the Bot (Simplified)

When you click "Apply to Discord," you\'re instructing the FoundryCord bot to make changes to your actual Discord server based on the active template. Here\'s a simplified idea of what happens:

*   **Reads Template:** The bot reads the structure (categories, channels, basic settings) defined in your active template.
*   **Compares with Server:** It looks at your current Discord server setup.
*   **Creates/Updates:**
    *   If a category or channel in the template doesn\'t exist on your server, the bot creates it.
    *   If a category or channel managed by the template exists, the bot might update its name or topic to match the template (full property updates depend on implementation).
*   **Handles Unmanaged Elements (with "Clean Apply"):**
    *   If "Clean Apply" is ON, the bot will also delete any categories or channels it finds on your server that are *not* part of the template. This helps keep your server exactly matching the template.
    *   If "Clean Apply" is OFF, the bot leaves these extra, unmanaged elements alone.
*   **Permissions:** Applying detailed permission overwrites from the template is a complex feature and its current level of implementation may vary. The bot will attempt to set permissions as defined in the template where possible.

This process can take a few moments. The bot usually tries to be efficient and only make necessary changes.

## Current Limitations & Important Notes (User Perspective)

While powerful, the Guild Designer has some limitations to be aware of:

*   **No Direct Property Editing in UI:** You can reorder and re-parent categories/channels via drag-and-drop. However, directly editing names, topics, types, or detailed permissions for these items *within the designer UI itself* is generally not yet implemented. These properties are primarily set by how they are defined in the template data when it was first saved (e.g., from an initial snapshot or if template editing tools improve in the future).
*   **Reordering Precision on Apply:** When a template is applied, the bot creates channels in the specified order. However, if you reorder *already existing* channels in the designer and re-apply, the bot's ability to precisely match that new order on Discord for existing channels might be limited. It excels at initial setup.
*   **No "Undo" for Apply:** Applying a template makes direct changes to your Discord server. There is currently no one-click "undo" feature. It\'s good practice to save a copy of your server structure as a new template *before* applying major changes if you want a rollback point.
*   **Permissions in Templates:** While templates can store permission information, the full application of complex permission schemes by the bot is an advanced feature. Basic permission overwrites are more likely to be handled initially.

## Troubleshooting & FAQ

*   **Q: Why can't I save changes to the "Initial Snapshot" template?**
    *   A: The "Initial Snapshot" is a read-only baseline representation of your server. To modify it, first load it, then use the "Save As New Template" button to create your own editable version.
*   **Q: I clicked "Apply to Discord" but nothing happened, or only some things changed.**
    *   A: Check if the template you intended to apply is set as "Active." The bot only applies the template marked active for the guild.
    *   The bot might require specific permissions in your Discord server to create channels, categories, or manage permissions. Ensure the FoundryCord bot role has adequate administrative permissions.
    *   Check any bot log channels in your Discord server or web UI notifications for error messages or status updates from the bot.
*   **Q: What does "Clean Apply" do? Should I use it?**
    *   A: "Clean Apply" tells the bot to delete any categories and channels on your server that are *not* in the template being applied. Use it if you want your server to *exactly* match the template. Be cautious, as this can remove content. If unsure, leave it off; the bot will then only add/update based on the template and won\'t delete extra elements.
*   **Q: Can I add new channels or categories directly in the designer UI?**
    *   A: Currently, the Guild Designer primarily focuses on visualizing and reordering structures loaded from templates (which are often based on initial server snapshots). Direct creation of new channels/categories within the UI is generally not yet a feature. You would typically define these by having them on your server when an "Initial Snapshot" is taken or if future template editing tools allow adding them to the template data directly.

We hope this guide helps you make the most of the Guild Structure Designer! 