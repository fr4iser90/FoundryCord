import { apiRequest, showToast, ApiError } from '/static/js/components/common/notifications.js';

// Internal flag to prevent multiple listeners if initialized multiple times (simple safeguard)
let isActivationListenerAdded = false; 

// Store guildId globally within the module scope
let currentGuildIdForActivation = null;

// --- Internal Helper: Renders the template list ---
async function _renderTemplateList(contentElement, currentGuildId, activeTemplateId) {
    if (!contentElement) return;
    
    currentGuildIdForActivation = currentGuildId; // Store guild ID for later use (like loading details)
    
    if (!currentGuildId) {
        contentElement.innerHTML = '<p class="panel-placeholder">Guild context not available.</p>';
        return;
    }

    console.log(`[GuildTemplateListWidget] Rendering template list. Active ID: ${activeTemplateId}`);
    contentElement.innerHTML = '<p class="panel-placeholder">Loading saved guild structure templates...</p>';

    const listApiUrl = `/api/v1/guilds/${currentGuildId}/template/?context_guild_id=${currentGuildId}`;
    console.log(`[GuildTemplateListWidget] Fetching templates from: ${listApiUrl}`); 

    try {
        const response = await apiRequest(listApiUrl); 
        const templates = response?.templates; 

        if (!Array.isArray(templates)) {
            console.error("[GuildTemplateListWidget] Invalid data received from API:", response);
            contentElement.innerHTML = '<p class="text-danger p-3">Error loading templates: Invalid data format.</p>';
            return;
        }

        if (templates.length === 0) {
            contentElement.innerHTML = '<p class="panel-placeholder">No saved guild structure templates found.</p>';
            return;
        }
        
        const fragment = document.createDocumentFragment();
        const currentActiveIdStr = activeTemplateId != null ? String(activeTemplateId) : null; // Ensure string for comparison

        templates.forEach(template => {
            const templateId = template.template_id;
            const templateName = template.template_name || 'Unnamed Template';
            
            if (templateId === undefined || templateId === null) return;
            
            const isInitialSnapshot = template.is_initial_snapshot === true;
            console.log(`[TemplateList Render Check] Template ID: ${templateId}, Global Active ID: ${currentActiveIdStr}`);
            const isActive = currentActiveIdStr != null && String(templateId) === currentActiveIdStr;
             
            // --- Create list item elements ---
            const listItem = document.createElement('div');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';

            // Load Link
            const link = document.createElement('a');
            link.href = '#';
            link.className = 'text-decoration-none text-body flex-grow-1 me-2 template-load-link';
            link.dataset.templateId = templateId;
            link.addEventListener('click', (event) => {
                event.preventDefault();
                handleTemplateLoad(templateId); 
            });
            const iconElement = document.createElement('i');
            iconElement.className = 'template-icon fas fa-server me-2'; 
            link.appendChild(iconElement);
            const nameSpan = document.createElement('span');
            nameSpan.className = 'template-name';
            nameSpan.textContent = templateName;
            link.appendChild(nameSpan);
             if (isActive) {
                 nameSpan.insertAdjacentHTML('beforeend', ' <span class="badge bg-success ms-1">Active</span>');
             }
            listItem.appendChild(link);

            // Action Buttons Group
            const buttonGroup = document.createElement('div');
            buttonGroup.className = 'btn-group btn-group-sm';
            buttonGroup.setAttribute('role', 'group');

            // Share Button
            const shareButton = document.createElement('button');
            shareButton.type = 'button';
            shareButton.className = 'btn btn-outline-secondary btn-share-template';
            shareButton.title = `Share template '${templateName}'`;
            shareButton.dataset.templateId = templateId;
            shareButton.dataset.templateName = templateName;
            const shareIcon = document.createElement('i');
            shareIcon.className = 'fas fa-share-alt';
            shareButton.appendChild(shareIcon);
            // Disable share for initial snapshot
            if (isInitialSnapshot) {
                shareButton.disabled = true;
                shareButton.title = 'Cannot share the initial guild snapshot.';
                shareButton.classList.add('disabled');
            } else {
                shareButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    handleTemplateShare(templateId, templateName);
                });
            }
            buttonGroup.appendChild(shareButton);

            // --- NEW: Rename Button ---
            const renameButton = document.createElement('button');
            renameButton.type = 'button';
            renameButton.className = 'btn btn-outline-secondary btn-rename-template'; // New class
            renameButton.title = `Rename template '${templateName}'`;
            renameButton.dataset.templateId = templateId;
            renameButton.dataset.templateName = templateName; // Store current name
            const renameIcon = document.createElement('i');
            renameIcon.className = 'fas fa-pencil-alt'; // Pencil icon
            renameButton.appendChild(renameIcon);
            // Disable rename for initial snapshot
            if (isInitialSnapshot) {
                renameButton.disabled = true;
                renameButton.title = 'Cannot rename the initial guild snapshot.';
                renameButton.classList.add('disabled');
            } else {
                renameButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    handleTemplateRenameRequest(templateId, templateName); // New handler needed
                });
            }
            buttonGroup.appendChild(renameButton);
            // --- END NEW: Rename Button ---

            // Activate Button (MODIFIED LOGIC)
            const activateButton = document.createElement('button');
            activateButton.type = 'button';
            activateButton.className = 'btn btn-outline-success btn-activate-template'; 
            activateButton.dataset.templateId = templateId;
            activateButton.dataset.templateName = templateName;
            const activateIcon = document.createElement('i');
            
            if (isActive) {
                activateButton.disabled = true;
                activateButton.title = `Template '${templateName}' is already active`;
                activateButton.classList.remove('btn-outline-success');
                activateButton.classList.add('btn-success', 'active'); 
                activateIcon.className = 'fas fa-star'; // Use star when active
            } else {
                 activateButton.title = `Activate template '${templateName}' for this guild`;
                 activateIcon.className = 'fas fa-check-circle'; // Use checkmark when inactive
                 // Call API directly instead of dispatching event
                 activateButton.addEventListener('click', async (event) => {
                     event.preventDefault();
                     event.stopPropagation();
                     // Call the direct activation function
                     await handleTemplateActivateDirect(templateId, templateName, event.currentTarget);
                 });
            }
            activateButton.appendChild(activateIcon);
            buttonGroup.appendChild(activateButton);

            // Delete Button
            const deleteButton = document.createElement('button');
            deleteButton.type = 'button';
            deleteButton.className = 'btn btn-outline-secondary btn-delete-template';
            deleteButton.title = `Delete template '${templateName}'`;
            deleteButton.dataset.templateId = templateId;
            deleteButton.dataset.templateName = templateName;
            const deleteIcon = document.createElement('i');
            deleteIcon.className = 'fas fa-trash-alt text-danger';
            deleteButton.appendChild(deleteIcon);
            if (isInitialSnapshot) {
                deleteButton.disabled = true;
                deleteButton.title = 'Cannot delete the initial guild snapshot.';
                deleteButton.classList.add('disabled');
            } else {
                deleteButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    console.log(`[TemplateList] Dispatching requestDeleteTemplate for ID: ${templateId}`);
                    document.dispatchEvent(new CustomEvent('requestDeleteTemplate', {
                         detail: { templateId: templateId, templateName: templateName, listType: 'saved' }
                    }));
                });
            }
            buttonGroup.appendChild(deleteButton);
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
        console.error("[GuildTemplateListWidget] Error rendering guild structure templates:", error);
        contentElement.innerHTML = `<p class="text-danger p-3">Error rendering templates: ${error.message}</p>`;
    }
}


/**
 * Initializes the SAVED GUILD STRUCTURE templates list widget.
 * Fetches initial data and sets up listener for activation events.
 * @param {HTMLElement} contentElement - The container element for the widget content.
 * @param {string} currentGuildId - The current guild ID.
 * @param {string|null} initialActiveTemplateId - The ID of the template active on initial load.
 */
export async function initializeTemplateList(contentElement, currentGuildId, initialActiveTemplateId) {
    console.log("[GuildTemplateListWidget] Initializing...");
    
    // Initial render
    await _renderTemplateList(contentElement, currentGuildId, initialActiveTemplateId);

    // Add listener for activation events *only once*
    if (!isActivationListenerAdded) {
        document.addEventListener('templateActivated', (event) => {
            console.log("[GuildTemplateListWidget] Detected 'templateActivated' event. Refreshing list.");
            const activatedTemplateId = event.detail?.activatedTemplateId;
            // Re-render the list with the new active ID
             _renderTemplateList(contentElement, currentGuildId, activatedTemplateId); 
        });
        isActivationListenerAdded = true;
        console.log("[GuildTemplateListWidget] 'templateActivated' listener added.");
    }
}

// --- Event Handlers for actions WITHIN the list ---

// Handles clicking on a template name to load it into the designer
async function handleTemplateLoad(templateId) {
    if (templateId === undefined || templateId === null) {
        console.error("[TemplateList] Load clicked but template ID is missing.");
        showToast('error', 'Cannot load template: ID missing.');
        return;
    }
    // <<< GET GUILD ID needed for the URL >>>
    const currentGuildId = currentGuildIdForActivation; 
    if (!currentGuildId) {
        console.error("[TemplateList] Cannot load template details: Guild ID is missing.");
        showToast('error', 'Cannot load template: Guild context missing.');
        return;
    }
    console.log(`[TemplateList] Requesting load for template ID: ${templateId} in Guild: ${currentGuildId}`);
    
    // API endpoint to fetch FULL structure data for a specific template
    const detailApiUrl = `/api/v1/guilds/${currentGuildId}/template/${templateId}`; // <<< CORRECTED URL
    console.log(`[TemplateList] Fetching template details from: ${detailApiUrl}`); // Log the new URL

    try {
        showToast('info', `Loading template (ID: ${templateId})...`);
        const templateData = await apiRequest(detailApiUrl); // Expects full template object
        
        if (!templateData || typeof templateData !== 'object') {
             throw new Error("Invalid data received for template details.");
        }

        console.log(`[TemplateList] Template data fetched for ID ${templateId}. Dispatching 'loadTemplateData' event.`);
        
        // Dispatch event for the main designer listener
        document.dispatchEvent(new CustomEvent('loadTemplateData', { 
            detail: { templateData: templateData } 
        }));
        
        showToast('success', `Template '${templateData.template_name || 'Unnamed'}' loaded.`);

    } catch (error) {
        console.error(`[TemplateList] Error fetching template details for ID ${templateId}:`, error);
        showToast('error', `Failed to load template: ${error.message}`);
    }
}

// Handles clicking the Share button for a template
function handleTemplateShare(templateId, templateName) {
     if (templateId === undefined || templateId === null || !templateName) {
        console.error("[TemplateList] Share clicked but template ID or Name is missing.");
        showToast('error', 'Cannot share template: Details missing.');
        return;
    }
    console.log(`[TemplateList] Requesting share for template: ${templateName} (ID: ${templateId})`);
    
    // Dispatch event to open the share modal (assuming modal logic handles API call)
    document.dispatchEvent(new CustomEvent('requestShareTemplate', { 
        detail: { templateId: templateId, templateName: templateName } 
    }));
}

// --- NEW: Event Handler for Rename Request ---
function handleTemplateRenameRequest(templateId, currentName) {
    console.log(`[TemplateList] Rename requested for template ID: ${templateId}, Current Name: ${currentName}`);
    // Dispatch an event for index.js or a modal manager to handle
    // We'll re-use the newItemInputModal for simplicity, but need to pass context
    document.dispatchEvent(new CustomEvent('requestRenameTemplate', {
        detail: { templateId, currentName }
    }));
}

// --- NEW: Direct activation handler ---
async function handleTemplateActivateDirect(templateId, templateName, buttonElement) {
    console.log(`[TemplateList] Direct activation requested for: ${templateName} (ID: ${templateId})`);

    if (templateId === undefined || templateId === null) {
        showToast('error', 'Activation failed: Template ID missing.');
        return;
    }
    
    const targetGuildId = currentGuildIdForActivation;
    if (!targetGuildId) {
        showToast('error', 'Activation failed: Guild context ID missing.');
        console.error('[TemplateList] Cannot activate: currentGuildIdForActivation is null/undefined.');
        return;
    }

    const apiUrl = `/api/v1/guilds/${targetGuildId}/template/${templateId}/activate`;
    console.log(`[TemplateList] Activation API URL: ${apiUrl}`);
    
    const originalButtonHtml = buttonElement.innerHTML; // Store original content
    const originalTitle = buttonElement.title;

    buttonElement.disabled = true;
    buttonElement.innerHTML = `<span class="spinner-border spinner-border-sm"></span>`;
    buttonElement.title = 'Activating...';
    showToast('info', `Activating template: ${templateName}...`);

    try {
        const response = await apiRequest(apiUrl, { method: 'POST' }); 
        console.log('[TemplateList] Template activated successfully via POST:', response);
        showToast('success', `Template ${templateName} (ID: ${templateId}) activated successfully!`);

        // Dispatch 'templateActivated' event so list and toolbar update state
        document.dispatchEvent(new CustomEvent('templateActivated', { 
            detail: { activatedTemplateId: templateId } 
        }));
        console.log("[TemplateList] Dispatched 'templateActivated' event after direct activation.");

    } catch (error) {
        console.error(`[TemplateList] Error directly activating template (ID: ${templateId}) via POST:`, error);
        // Restore button state on error
        buttonElement.disabled = false;
        buttonElement.innerHTML = originalButtonHtml;
        buttonElement.title = originalTitle;
    } 
}
