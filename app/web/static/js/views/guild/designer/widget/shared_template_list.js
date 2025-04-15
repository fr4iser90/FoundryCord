import { apiRequest, showToast, ApiError } from '/static/js/components/common/notifications.js';

/**
 * Fetches and displays the list of SHARED guild structure templates.
 * @param {HTMLElement} contentElement - The container element for the widget content.
 * @param {string} currentGuildId - The current guild ID (might be needed for context).
 */
export async function initializeSharedTemplateList(contentElement, currentGuildId) {
    if (!contentElement) {
        console.warn("[SharedTemplateListWidget] Content element not provided.");
        return;
    }

    console.log("[SharedTemplateListWidget] Initializing...");
    contentElement.innerHTML = '<p class="panel-placeholder">Loading shared templates...</p>';

    // --- API ENDPOINT for SHARED templates --- 
    const listApiUrl = `/api/v1/templates/guilds/shared/`; 

    try {
        // Fetch the list of shared templates
        const response = await apiRequest(listApiUrl); 
        
        // Expect response format: { templates: [ { template_id: ..., template_name: ... }, ... ] }
        const templates = response?.templates; // Get the array from the 'templates' key

        if (!Array.isArray(templates)) {
            if (response === null || response === undefined) {
                 console.warn("[SharedTemplateListWidget] No response received from shared template list API.");
                 contentElement.innerHTML = '<p class="panel-placeholder">Could not load shared templates.</p>';
            } else {
                console.error("[SharedTemplateListWidget] Invalid data received from API (expected array in response.templates):", response);
                contentElement.innerHTML = '<p class="text-danger p-3">Error loading shared templates: Invalid data format.</p>';
            }
            return;
        }

        if (templates.length === 0) {
            contentElement.innerHTML = '<p class="panel-placeholder">No shared guild structure templates found.</p>';
            return;
        }
        
        const fragment = document.createDocumentFragment();

        templates.forEach(template => {
            const templateId = template.template_id; 
            const templateName = template.template_name || 'Unnamed Shared Template';
            
            if (templateId === undefined || templateId === null) {
                console.warn('[SharedTemplateListWidget] Template object missing template_id:', template);
                return;
            }

            const listItem = document.createElement('div');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';

            const link = document.createElement('a');
            link.href = '#';
            link.className = 'text-decoration-none text-body flex-grow-1 me-2 template-use-link'; // Changed class
            link.dataset.templateId = templateId;
            link.addEventListener('click', (event) => {
                event.preventDefault();
                handleTemplateUse(templateId, templateName); // Changed handler
            });

            const iconElement = document.createElement('i');
            iconElement.className = 'template-icon fas fa-globe-americas me-2'; // Different icon for shared
            link.appendChild(iconElement);

            const nameSpan = document.createElement('span');
            nameSpan.className = 'template-name';
            nameSpan.textContent = templateName;
            link.appendChild(nameSpan);

            listItem.appendChild(link);

            // --- Action Buttons (Placeholder for "Use" or "Copy") ---
            const buttonGroup = document.createElement('div');
            buttonGroup.className = 'btn-group btn-group-sm';
            buttonGroup.setAttribute('role', 'group');
            buttonGroup.setAttribute('aria-label', 'Shared Template Actions');

            // Example "Use" Button (functionality not implemented yet)
            const useButton = document.createElement('button');
            useButton.type = 'button';
            useButton.className = 'btn btn-outline-primary btn-use-template';
            useButton.title = `Use shared template '${templateName}'`;
            useButton.dataset.templateId = templateId;
            useButton.dataset.templateName = templateName;
            const useIcon = document.createElement('i');
            useIcon.className = 'fas fa-download'; // Example icon
            useButton.appendChild(useIcon);
            useButton.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                handleTemplateUse(templateId, templateName);
            });
            buttonGroup.appendChild(useButton);
            // --- End Action Buttons ---

            listItem.appendChild(buttonGroup);
            fragment.appendChild(listItem);
        });

        contentElement.innerHTML = ''; 
        const listGroup = document.createElement('div');
        listGroup.className = 'list-group list-group-flush';
        listGroup.appendChild(fragment);
        contentElement.appendChild(listGroup);

    } catch (error) {
        console.error("[SharedTemplateListWidget] Error fetching shared templates:", error);
        contentElement.innerHTML = `<p class="text-danger p-3">Error loading shared templates: ${error.message}</p>`;
    }
}

/**
 * Handles using a selected SHARED template.
 * @param {string} templateId - The ID of the template to use.
 * @param {string} templateName - The name of the template.
 */
function handleTemplateUse(templateId, templateName) {
    console.log(`[SharedTemplateListWidget] Use shared template selected: ${templateId}, Name: ${templateName}`);
    // TODO: Implement logic to apply this shared structure template (e.g., load into designer, maybe confirm overwrite?)
    showToast('info', `Using shared template '${templateName}'... (Not implemented yet)`);
}

// Removed handleTemplateShare and handleTemplateDelete functions previously here
