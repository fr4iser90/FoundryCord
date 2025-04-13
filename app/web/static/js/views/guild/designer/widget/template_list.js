import { apiRequest, showToast } from '/static/js/components/common/notifications.js';

/**
 * Fetches and displays the list of saved templates for the guild.
 * @param {HTMLElement} contentElement - The container element for the widget content.
 * @param {string} guildId - The current guild ID.
 */
export async function initializeTemplateList(contentElement, guildId) {
    if (!contentElement) {
        console.warn("[TemplateListWidget] Content element not provided.");
        return;
    }
    if (!guildId) {
        contentElement.innerHTML = '<p class="text-muted p-3">Guild ID not available.</p>';
        return;
    }

    console.log("[TemplateListWidget] Initializing...");
    contentElement.innerHTML = '<p class="text-muted p-3">Loading templates...</p>';

    // Define the API endpoint - THIS NEEDS TO EXIST ON THE BACKEND
    const apiUrl = `/api/v1/layouts/templates?guild_id=${guildId}`;
    // Alternatively, if the layout identifier IS the template ID:
    // const apiUrl = `/api/v1/layouts`; // And filter client-side? Less ideal.

    try {
        // Assuming the API returns an object with a 'templates' array: { templates: [...] }
        // Adjust if the API returns the array directly.
        const response = await apiRequest(apiUrl);
        const templates = response?.templates || response; // Handle both cases

        if (!Array.isArray(templates)) {
            console.error("[TemplateListWidget] Invalid data received from API:", templates);
            contentElement.innerHTML = '<p class="text-danger p-3">Error loading templates: Invalid data format.</p>';
            return;
        }

        if (templates.length === 0) {
            contentElement.innerHTML = '<p class="text-muted p-3">No saved templates found for this guild.</p>';
            return;
        }

        // Sort templates if needed (e.g., by name or date)
        // templates.sort((a, b) => a.name.localeCompare(b.name));

        const listItems = templates.map(template => {
            let icon = 'fas fa-file-alt'; // Default icon
            let nameSuffix = '';
            if (template.is_initial) {
                icon = 'fas fa-history';
                nameSuffix = ' (Initial Snapshot)';
            }
            if (template.is_shared) {
                icon = 'fas fa-share-alt'; // Or combine icons?
                nameSuffix += ' (Shared)';
            }

            // Ensure template.id exists - adjust property name based on backend model
            const templateId = template.layout_id || template.id;
            if (!templateId) return ''; // Skip templates without an ID

            return `
                <a href="#" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" data-template-id="${templateId}">
                    <span><i class="${icon} me-2"></i> ${template.name || 'Unnamed Template'}${nameSuffix}</span>
                    <!-- Add other info like date? -->
                    <!-- <small class="text-muted">${template.updated_at ? new Date(template.updated_at).toLocaleDateString() : ''}</small> -->
                </a>
            `;
        }).join('');

        contentElement.innerHTML = `<div class="list-group list-group-flush">${listItems}</div>`;

        // Add event listener to handle clicks
        contentElement.querySelectorAll('.list-group-item').forEach(item => {
            item.addEventListener('click', (event) => {
                event.preventDefault();
                const selectedTemplateId = event.currentTarget.dataset.templateId;
                handleTemplateLoad(selectedTemplateId);
            });
        });

    } catch (error) {
        console.error("[TemplateListWidget] Error fetching templates:", error);
        contentElement.innerHTML = `<p class="text-danger p-3">Error loading templates: ${error.message}</p>`;
    }
}

/**
 * Handles the action when a template is selected from the list.
 * @param {string} templateId - The ID of the selected template.
 */
function handleTemplateLoad(templateId) {
    console.log(`[TemplateListWidget] Template selected: ${templateId}`);
    // TODO: Implement loading logic
    // 1. Confirm with the user (optional but recommended)
    // 2. Fetch the full layout data for this templateId from `/api/v1/layouts/{templateId}`
    // 3. Tell GridManager to load the new layout data (might need access to the gridManager instance)
    //    - This might involve emitting a custom event, or passing the GridManager instance around.
    //    - Example: gridManager.loadLayout(fetchedLayoutData); // Assuming a method exists
    showToast('info', `Loading template ${templateId}... (Not implemented yet)`);
}
