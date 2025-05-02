# Dashboard Builder Guide

## Purpose

The Dashboard Builder allows you to create and customize interactive dashboards that can be displayed within specific channels of your Discord guild template. Instead of just sending static messages, dashboards provide dynamic content, buttons, embeds, and other components that can update automatically or react to user interactions.

This builder provides a visual interface to assemble these dashboards without needing to write complex code.

## Key Concepts

*   **Dashboard Instance:** A specific dashboard you design and attach to a particular channel within your guild template. Each instance has a name, a type (which might influence available components), and a configuration.
*   **Components:** These are the building blocks of your dashboard (e.g., Text Blocks, Embeds, Buttons, Selectors, User Info Displays). You select and configure these components to create the dashboard's content and layout.
*   **Configuration (`config`):** This is the technical representation of how you arranged and configured the components in the builder. It's stored as JSON data linked to the dashboard instance.
*   **Variables:** Placeholders (like `{{user_name}}` or `{{server_stats}}`) that you can insert into component configurations. These variables will be replaced with actual live data when the dashboard is displayed in Discord.
*   **Editor Widget:** The main area where you visually build your dashboard by adding, arranging, and configuring components.
*   **Preview Widget:** Shows an approximation of how your designed dashboard will look in Discord, using placeholder data for variables.
*   **Toolbox:** A panel (usually on the left) that lists the available **Components** you can drag into the Editor Widget.
*   **Properties Panel:** When a channel is selected in the main structure tree, this panel (usually on the right) lists the Dashboard Instances already attached to that channel and provides buttons to create new instances or edit/delete existing ones.

## Workflow

1.  **Select Channel:** In the Guild Designer's main structure tree, select the channel template where you want to add or manage a dashboard.
2.  **Manage Instances (Properties Panel):**
    *   The Properties Panel will show a list of existing Dashboard Instances for the selected channel.
    *   **Create New:** Click the "New" button. You might be asked to select a general `dashboard_type` (e.g., 'welcome', 'monitoring'). This opens the **Editor Widget** in 'create' mode.
    *   **Edit Existing:** Click the "Edit" button next to an instance in the list. This opens the **Editor Widget** pre-filled with that instance's configuration.
    *   **Delete Existing:** Click the "Delete" button next to an instance (confirmation will be required).
    *   **Select for Preview:** Clicking the name of an instance in the list loads its preview into the **Preview Widget**.
3.  **Build/Edit Dashboard (Editor Widget):**
    *   **Add Components:** Drag desired **Components** from the **Toolbox** onto the main canvas/area of the Editor Widget.
    *   **Configure Components:** Select a component on the canvas. Its specific configuration options (text fields, color pickers, dropdowns, etc.) will appear within the Editor Widget. Fill these out as needed.
    *   **Use Variables:** Where applicable (usually indicated in the configuration field), insert available **Variables** (e.g., by selecting from a list or typing `{{variable_key}}`). A list of available variables might be shown within the Editor or Properties Panel.
    *   **Arrange Components:** Reorder or arrange components on the editor canvas (details depend on the specific editor implementation).
    *   **Save:** Click the "Save" button within the Editor Widget to store the configuration for the current instance.
4.  **Preview Dashboard (Preview Widget):**
    *   After selecting an instance in the Properties Panel or saving changes in the Editor, the **Preview Widget** automatically updates to show an approximation of the dashboard's appearance in Discord. Check if the layout and content look as expected.

## Important Notes

*   The Preview Widget shows an *approximation*. The final look in Discord might vary slightly.
*   Ensure you save your changes in the Editor Widget before navigating away or closing it.
*   The specific components and variables available depend on the system's configuration and the selected `dashboard_type`.
