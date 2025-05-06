# User Guide: Dashboard Builder

Welcome to the [FoundryCord](../1_introduction/glossary.md#foundrycord) [Dashboard](../1_introduction/glossary.md#dashboard) Builder! This tool empowers you to design and customize interactive dashboards that your bot can display in specific Discord channels. Move beyond static messages and create dynamic, engaging content with buttons, auto-updating embeds, and more, all through a visual interface.

This guide will help you understand how to use the Dashboard Builder to create rich channel experiences.

## Purpose

The Dashboard Builder allows you to create and customize interactive dashboards that can be displayed within specific channels of your Discord [guild](../1_introduction/glossary.md#guild) template. Instead of just sending static messages, dashboards provide dynamic content, buttons, embeds, and other components that can update automatically or react to user interactions.

This builder provides a visual interface to assemble these dashboards without needing to write complex code.

## Key Concepts

*   **Dashboard Instance:** A specific [dashboard](../1_introduction/glossary.md#dashboard) you design and attach to a particular channel (or a channel within a guild template). Each instance typically has a name, a type (which might influence available components or data sources), and its unique configuration.
*   **Components:** These are the visual and interactive building blocks of your dashboard (e.g., Text Blocks, Rich Embeds, Buttons, Select Menus, User Info Displays, Server Statistics). You select, arrange, and configure these to create the dashboard\'s content and layout.
*   **Configuration (`config`):** The saved JSON data that represents how you\'ve arranged and set up the components for a specific Dashboard Instance.
*   **Variables/Placeholders:** Special text snippets (often like `{{user_name}}`, `{{guild_member_count}}`, or `{{server_status.some_metric}}`) that you can insert into component configurations (e.g., in an embed\'s title or a text block). These are dynamically replaced with live data when the bot displays or updates the dashboard in Discord.
*   **Editor Widget / Canvas:** The main interactive area where you visually build your dashboard by adding, arranging, and selecting components to edit their properties.
    `[SCREENSHOT: Dashboard Builder interface highlighting the Editor Widget/Canvas]`
*   **Preview Widget:** A panel that shows an approximation of how your designed dashboard will look in Discord. It usually updates as you make changes or when you load an existing dashboard instance. It often uses placeholder or sample data for variables.
    `[SCREENSHOT: Dashboard Builder interface highlighting the Preview Widget]`
*   **Toolbox Panel:** Lists all available **Components** that you can drag onto the Editor Widget/Canvas.
    `[SCREENSHOT: Dashboard Builder interface highlighting the Toolbox Panel with component examples]`
*   **Properties Panel (Channel Context):** When you select a channel in the main [Guild Designer](../1_introduction/glossary.md#guild-designer) structure tree, this panel (often on the right side of the Guild Designer UI) will show existing Dashboard Instances attached to that channel. It provides buttons to create new instances or edit/delete existing ones for that specific channel.
    `[SCREENSHOT: Guild Designer Properties Panel showing a list of Dashboard Instances for a selected channel]`
*   **Component Properties Editor:** When a component is selected on the Editor Widget/Canvas, its specific configuration options (text fields, color pickers, choices for data sources, etc.) will appear, usually within the Editor Widget itself or in a dedicated properties area.
    `[SCREENSHOT: A selected Embed component on the canvas, with its properties (title, description, color fields) shown in an editor area]`

## General Workflow

The typical process for creating and managing a channel dashboard is as follows:

1.  **Select Target Channel:**
    *   In the main **[Guild Designer](../1_introduction/glossary.md#guild-designer)** interface, click on the channel template (e.g., `#announcements`, `#welcome`) in the server structure tree where you want to add or manage a dashboard.
2.  **Manage Dashboard Instances (via Channel Properties Panel):**
    *   The **Properties Panel** (for the selected channel) will display a list of any Dashboard Instances already configured for this channel.
    *   **To Create a New Dashboard:**
        1.  Click the "New Dashboard" (or similar) button in this panel.
        2.  You might be asked to give the dashboard a name and/or select a `dashboard_type` (e.g., 'Welcome Message', 'Server Stats Panel', 'Generic Info Panel'). The type can influence available components or variables.
        3.  This will open the main **Editor Widget** in a fresh 'create' mode for your new dashboard instance.
    *   **To Edit an Existing Dashboard:**
        1.  Click the "Edit" button next to an existing dashboard instance in the list.
        2.  This opens the **Editor Widget** pre-filled with that instance\'s saved configuration.
    *   **To Delete an Existing Dashboard:**
        1.  Click the "Delete" button next to an instance. A confirmation will be required.
    *   **To Preview an Existing Dashboard:**
        1.  Simply click the name of an instance in the list. Its rendered preview should appear in the **Preview Widget**.
3.  **Build or Edit Your Dashboard (in the Editor Widget):**
    `[GIF: Showing a user dragging a component from Toolbox, dropping it on canvas, selecting it, and editing a property]`
    *   **Add Components:** Drag desired **Components** from the **Toolbox Panel** onto the main canvas area of the Editor Widget.
    *   **Select & Configure Components:**
        1.  Click on a component you\'ve placed on the canvas to select it.
        2.  Its specific configuration options will appear in the **Component Properties Editor** area.
        3.  Fill out these options as needed (e.g., enter text, choose colors, select data sources if applicable).
    *   **Use Variables/Placeholders:** When configuring component text (like titles, descriptions, field values), you can often insert available **Variables**. Look for a list of available variables or a helper button, or type them in directly (e.g., `{{guild_name}}`, `{{user_count}}`).
    *   **Arrange Components:** Drag and drop components on the canvas to arrange their order or position (the layout might be a simple vertical flow or a more complex grid depending on the editor\'s capabilities).
    *   **Save Your Work:** Regularly click the "Save" or "Save Configuration" button within the Editor Widget. This stores the current setup of your dashboard instance in the database.
4.  **Preview Your Dashboard (in the Preview Widget):**
    *   As you make changes and save, or when you load an existing dashboard, the **Preview Widget** should automatically update to show an approximation of how the dashboard will appear in Discord. Use this to check layout, content, and placeholder data.

## Example: Building a Simple Welcome Dashboard

Let\'s walk through creating a basic welcome message for a `#general` channel.

1.  In the [Guild Designer](../1_introduction/glossary.md#guild-designer), select your `#general` channel template.
2.  In its Properties Panel, click "New Dashboard."
3.  Name it "Welcome Message" and choose a relevant type (e.g., 'Generic' or 'Welcome'). The Editor Widget opens.
4.  From the **Toolbox**, drag an **Embed Component** onto the canvas.
5.  Select the Embed Component on the canvas. Its properties appear.
6.  In the Embed Properties:
    *   Set **Title:** `Welcome to {{guild_name}}!`
    *   Set **Description:** `Hi {{user_mention}}, we\'re glad to have you! Please check out our #rules channel.`
    *   Set **Color:** Choose a welcoming color (e.g., a light blue).
    `[SCREENSHOT: Embed component properties being filled for the welcome message]`
7.  From the **Toolbox**, drag a **Button Component** below the embed (if the layout allows).
8.  Select the Button Component. In its Properties:
    *   Set **Label:** `View Rules`
    *   Set **Style:** `Primary` (e.g., a blue button)
    *   Set **Action Type:** `Link` (if supported)
    *   Set **URL/Link:** (Enter the URL to your rules, or a placeholder like `https://discord.com/channels/@me/{guild_id}/{rules_channel_id}` if channel linking is supported directly).
9.  Click "Save" in the Editor Widget.
10. Observe the **Preview Widget**. It should show your embed with the placeholders and the button.
    `[SCREENSHOT: Preview Widget showing the composed Welcome Dashboard]`

This dashboard, once associated with the `#general` channel in an active template and applied by the bot, could then be triggered to display for new users (depending on further bot logic not covered by the builder itself).

## Important Notes

*   **Preview vs. Actual:** The Preview Widget shows an *approximation*. The final appearance in Discord can sometimes vary slightly due to Discord\'s own rendering engine for embeds and components.
*   **Save Regularly:** Always save your changes in the Editor Widget before navigating away or closing it to avoid losing work.
*   **Component & Variable Availability:** The specific components (Text, Embed, Button, Stat Display, etc.) and variables (`{{...}}`) available to you will depend on the overall system configuration and potentially the `dashboard_type` you selected when creating the instance.
*   **Dashboard Activation:** Designing a dashboard here configures *what* it looks like. Separate bot logic (often part of a workflow or command) determines *when and how* this dashboard instance is posted or updated in its assigned Discord channel.

## Troubleshooting / FAQ

*   **Q: My variables like `{{user_name}}` are not showing any data in the preview.**
    *   A: The preview often uses sample or placeholder data. The real data will be populated when the bot displays the dashboard in Discord in a live context (e.g., when a user triggers an event that shows the dashboard).
*   **Q: I can\'t find a specific component I want to use.**
    *   A: The list of available components in the Toolbox is defined by the system administrators or developers. If a component is missing, it might not be implemented or enabled for the dashboard type you are editing.
*   **Q: How do I make my dashboard update automatically with new information?**
    *   A: The Dashboard Builder defines the *structure and content placeholders*. The automatic updating (e.g., for server stats) is handled by the bot\'s backend logic, which will periodically fetch new data and refresh the dashboard message in Discord. You design the template here; the bot handles the live updates based on that template.

We hope this guide helps you create amazing and informative dashboards for your Discord community!
