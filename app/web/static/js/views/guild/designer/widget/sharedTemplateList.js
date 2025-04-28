import { apiRequest, showToast, ApiError } from '/static/js/components/common/notifications.js';
// Import the initializer for the SAVED templates list to refresh it after saving a copy
import { initializeTemplateList } from './templateList.js';

/**
 * Fetches and displays the list of SHARED guild structure templates.
 * @param {HTMLElement} contentElement - The container element for the widget content.
 * @param {string} currentGuildId - The current guild ID (might be needed for context).
 */
export async function initializeSharedTemplateList(contentElement, currentGuildId) {
    if (!contentElement) {
        console.error("[SharedTemplateListWidget] Content element not provided.");
        return;
    }

    // --- Get Current User ID --- 
    const currentUserIdStr = contentElement.dataset.currentUserId;
    if (!currentUserIdStr) {
        console.error("[SharedTemplateListWidget] Cannot determine current user ID. 'data-current-user-id' attribute missing on content element.");
        contentElement.innerHTML = '<p class="text-danger p-3">Error: Cannot identify user.</p>';
        return;
    }
    // Convert to appropriate type if needed (e.g., integer) depending on API response format
    const currentUserId = parseInt(currentUserIdStr, 10);
    // --- End Get User ID --- 

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
            const creatorUserId = template.creator_user_id; // Get creator ID from API data
            
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
                handleTemplateUse(templateId, templateName, currentGuildId); // Pass guildId if needed later
            });
            buttonGroup.appendChild(useButton);

            // --- Add Save/Copy Button ---
            const saveButton = document.createElement('button');
            saveButton.type = 'button';
            saveButton.className = 'btn btn-outline-secondary btn-save-shared-template'; // New class
            saveButton.title = `Save a copy of '${templateName}' to your templates`;
            saveButton.dataset.templateId = templateId;
            saveButton.dataset.templateName = templateName;
            const saveIcon = document.createElement('i');
            saveIcon.className = 'fas fa-save'; // Save icon
            saveButton.appendChild(saveIcon);
            saveButton.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                handleSharedTemplateSave(templateId, templateName, currentGuildId); // Pass guildId
            });
            buttonGroup.appendChild(saveButton);
            // --- End Save/Copy Button ---

            // --- Debugging Delete Button Logic ---
            console.log(`[Debug Delete] Template: ${templateName} (ID: ${templateId})`);
            console.log(`  Creator ID from API: ${creatorUserId} (Type: ${typeof creatorUserId})`);
            console.log(`  Current User ID from Dataset: ${currentUserId} (Type: ${typeof currentUserId})`);
            const isMatch = creatorUserId === currentUserId;
            console.log(`  Strict Comparison (creator === current): ${isMatch}`);
            // --- End Debugging ---

            // --- Add Delete Button (Conditionally) ---
            const isCurrentUserOwner = contentElement.dataset.isOwner === 'true';
            if ((creatorUserId && creatorUserId === currentUserId) || isCurrentUserOwner) {
                const deleteButton = document.createElement('button');
                deleteButton.type = 'button';
                deleteButton.className = 'btn btn-outline-danger btn-delete-shared-template'; // New class
                deleteButton.title = `Delete your shared template '${templateName}'`;
                deleteButton.dataset.templateId = templateId;
                deleteButton.dataset.templateName = templateName;
                const deleteIcon = document.createElement('i');
                deleteIcon.className = 'fas fa-trash-alt'; // Trash icon
                deleteButton.appendChild(deleteIcon);
                deleteButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    // Dispatch event to request modal opening
                    console.log(`[SharedTemplateList] Dispatching requestDeleteTemplate for ID: ${templateId}`);
                    document.dispatchEvent(new CustomEvent('requestDeleteTemplate', {
                        detail: {
                            templateId: templateId,
                            templateName: templateName,
                            listType: 'shared'
                        }
                    }));
                });
                buttonGroup.appendChild(deleteButton);
            }
            // --- End Delete Button ---

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
async function handleTemplateUse(templateId, templateName) {
    console.log(`[SharedTemplateListWidget] Use shared template selected: ${templateId}, Name: ${templateName}`);
    
    if (!confirm(`Are you sure you want to load the shared template "${templateName}"?\nThis will replace the current structure in the designer.`)) {
        console.log("[SharedTemplateListWidget] 'Use template' action cancelled by user.");
        return;
    }

    console.log(`[SharedTemplateListWidget] Attempting to load structure for shared template ID: ${templateId}`);
    showToast('info', `Loading structure for "${templateName}"...`);

    const apiUrl = `/api/v1/templates/guilds/shared/${templateId}`;
    try {
        const templateData = await apiRequest(apiUrl); // GET request by default
        
        if (!templateData) {
            // apiRequest likely showed a toast, but log and show another just in case
            console.error("[SharedTemplateListWidget] Received null or invalid data for template", templateId);
            showToast('error', `Failed to load data for template "${templateName}".`);
            return;
        }

        // Dispatch event for index.js to handle the update
        document.dispatchEvent(new CustomEvent('loadTemplateData', { 
            detail: { templateData: templateData } // Wrap in object for clarity
        }));

        showToast('success', `Template "${templateName}" loaded successfully!`);

    } catch (error) {
        console.error(`[SharedTemplateListWidget] Error loading template ${templateId}:`, error);
        // apiRequest should have shown a toast, but we can show a generic one if needed
        // showToast('error', `Failed to load template "${templateName}".`); 
    }
}

/**
 * Handles saving a copy of a SHARED template to the user's SAVED templates.
 * @param {string} templateId - The ID of the shared template to copy.
 * @param {string} templateName - The name of the shared template (potentially used as default for copy).
 * @param {string} currentGuildId - The current guild context ID (needed to refresh saved list).
 */
async function handleSharedTemplateSave(templateId, templateName, currentGuildId) {
    console.log(`[SharedTemplateListWidget] Save shared template selected: ${templateId}, Name: ${templateName}`);

    // Optional: Prompt for a new name for the saved copy?
    // const newName = prompt(`Enter a name for your saved copy of "${templateName}":`, templateName);
    // if (!newName) {
    //     console.log("[SharedTemplateListWidget] Save action cancelled by user (no name provided).");
    //     return;
    // }

    const apiUrl = `/api/v1/templates/guilds/copy_shared`;
    const payload = {
        shared_template_id: templateId,
        // new_name: newName // Include if using prompt
    };

    try {
        // Display loading state?
        showToast('info', `Saving a copy of "${templateName}"...`);

        const response = await apiRequest(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        // API returns 201 on success with no body, apiRequest handles this.
        // If it returned the new template info, you could use it: response.new_template_name
        showToast('success', `Copied "${templateName}" to your saved templates!`);

        // Refresh the Saved Templates list
        const savedListEl = document.getElementById('widget-content-template-list');
        if (savedListEl) {
            console.log("[SharedTemplateListWidget] Refreshing saved templates list...");
            initializeTemplateList(savedListEl, currentGuildId); // Call imported function
        } else {
            console.warn("[SharedTemplateListWidget] Could not find saved template list container (#widget-content-template-list) to refresh.");
        }

    } catch (error) {
        console.error(`[SharedTemplateListWidget] Error copying shared template ${templateId}:`, error);
        // apiRequest likely showed an error toast
    }
}

// Removed handleTemplateShare and handleTemplateDelete functions previously here
