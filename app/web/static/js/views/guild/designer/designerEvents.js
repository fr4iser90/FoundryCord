import { state } from './designerState.js';
import { getGuildIdFromUrl, formatStructureForApi } from './designerUtils.js';
import { apiRequest, showToast, ApiError } from '/static/js/components/common/notifications.js';
import { openSaveAsNewModal } from './modal/saveAsNewModal.js';
import { openDeleteModal } from './modal/deleteModal.js'; // Import delete modal opener
import { openActivateConfirmModal } from './modal/activateConfirmModal.js'; // Import activation modal opener
// Import widget initializers needed for refresh
import { initializeTemplateList } from './widget/templateList.js'; 
import { initializeStructureTree } from './widget/structureTree.js';
import { populateGuildDesignerWidgets } from './designerWidgets.js'; // Needed for loadTemplateData
import { openShareModal } from './modal/shareModal.js'; // Add import for share modal opener

// --- Function to update save button state --- 
// DEPRECATED: Logic moved to updateToolbarButtonStates
/*
function updateSaveButtonState() {
    const saveButton = document.getElementById('save-structure-btn');
    if (saveButton) {
        // Access dirty state via the state module
        saveButton.disabled = !state.isDirty(); 
    } 
}
*/

// --- Function to update toolbar button states ---
function updateToolbarButtonStates() {
    const saveButton = document.getElementById('save-structure-btn');
    const activateButton = document.getElementById('activate-template-btn');
    
    const isDirty = state.isDirty();
    const currentTemplate = state.getCurrentTemplateData();
    const globalActiveId = state.getActiveTemplateId();
    const isActive = currentTemplate && globalActiveId !== null && String(currentTemplate.template_id) === String(globalActiveId);

    // Debugging log
    console.log(`[DesignerEvents] Updating button states: isDirty=${isDirty}, isCurrentLoadedTemplateActive=${isActive} (CurrentID: ${currentTemplate?.template_id}, GlobalActiveID: ${globalActiveId})`);

    if (saveButton) {
        saveButton.disabled = !isDirty;
        // console.log(`[DesignerEvents] Save button disabled: ${saveButton.disabled}`);
    } else {
        console.warn("[DesignerEvents] Save button not found during state update.");
    }

    if (activateButton) {
        // Disable activate button if:
        // 1. There are unsaved changes (isDirty is true)
        // 2. The currently loaded template is already the active one (isActive is true)
        activateButton.disabled = isDirty || isActive; 
        
        // Optional: Change appearance if active (e.g., text or icon)
        if (isActive) {
             // Example: Modify text/icon if already active
             // activateButton.innerHTML = `<i class="bi bi-check-all"></i> <span class="d-none d-md-inline">Active</span>`;
             activateButton.title = "This template is already active for the guild.";
        } else {
             // Restore default appearance if not active
             // activateButton.innerHTML = `<i class="bi bi-check-circle-fill"></i> <span class="d-none d-md-inline">Activate</span>`;
             activateButton.title = "Set this template as the active one for the guild";
        }
        // console.log(`[DesignerEvents] Activate button disabled: ${activateButton.disabled}`);
    } else {
        console.warn("[DesignerEvents] Activate button not found during state update.");
    }
}

// --- Event Handler Functions --- 

// Handles the successful save of a template (either PUT or POST)
function handleStructureSaved(event) {
    console.log("[DesignerEvents] Handling 'structureSaved' event:", event.detail);
    state.setDirty(false); // Use state setter
    // ---> UPDATED: Use new function
    updateToolbarButtonStates();
    
    // Optionally refresh the template list if a new template was created
    if (event.detail?.isNew && event.detail?.newTemplateId) {
        const templateListContentEl = document.getElementById('widget-content-template-list');
        const guildId = getGuildIdFromUrl();
        if (templateListContentEl && guildId) {
             console.log("[DesignerEvents] Refreshing template list after new template creation.");
             // Pass the new ID as the active one for the refresh
             initializeTemplateList(templateListContentEl, guildId, String(event.detail.newTemplateId)); 
             // Update the active state globally as well
             state.setActiveTemplateId(String(event.detail.newTemplateId));
             // Update buttons again after setting active state
             updateToolbarButtonStates(); 
        } else {
             console.warn("[DesignerEvents] Could not find template list or guildId to refresh after save.");
        }
    }
}

// Handles the confirmation from the Save As New modal
async function handleSaveAsNewConfirmed(event) {
    console.log("[DesignerEvents] Handling 'saveAsNewConfirmed' event:", event.detail);
    const { newName, newDescription } = event.detail;

    if (!newName) {
        console.error("[DesignerEvents] 'saveAsNewConfirmed' event missing new name.");
        showToast('error', 'Failed to save: Name was missing.');
        return;
    }

    const templateData = state.getCurrentTemplateData();
    const templateIdForStructure = templateData?.template_id;
    if (templateIdForStructure === undefined || templateIdForStructure === null) {
        console.error("[DesignerEvents] Cannot get structure: Current template ID is unknown.");
        showToast('error', 'Failed to save: Cannot identify current structure.');
        return;
    }
    
    const structurePayload = formatStructureForApi(templateIdForStructure); // Use util function
    if (!structurePayload) {
        return; // Error already shown by formatStructureForApi
    }

    const apiUrl = '/api/v1/templates/guilds/from_structure';
    const payload = {
        new_template_name: newName,
        new_template_description: newDescription,
        structure: structurePayload
    };

    console.log("[DesignerEvents] Attempting POST to save new template from structure:", payload);
    showToast('info', `Saving new template '${newName}'...`);
    
    try {
        const response = await apiRequest(apiUrl, { 
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify(payload) 
        });

        console.log('[DesignerEvents] New template saved successfully via POST:', response);
        showToast('success', `New template '${newName}' (ID: ${response.template_id}) created successfully!`);

        // Dispatch structureSaved event to reset dirty flag and refresh lists
        document.dispatchEvent(new CustomEvent('structureSaved', { 
            detail: { isNew: true, newTemplateId: response.template_id } 
        }));

    } catch (error) {
        console.error('[DesignerEvents] Error saving new template via POST:', error);
        // apiRequest handles toast
    }
}

// Handles the main Save Structure button click (PUT request)
async function handleSaveStructureClick() {
    const saveButton = document.getElementById('save-structure-btn');
    if (!saveButton || !state.isDirty()) {
        console.log("[DesignerEvents] Save button clicked but not dirty or button missing.");
        return;
    }
    
    console.log("[DesignerEvents] Save Structure button clicked (Attempting PUT)...");
    showToast('info', 'Attempting to save structure...');

    const templateData = state.getCurrentTemplateData();
    const templateId = templateData?.template_id;
    if (templateId === undefined || templateId === null) {
         console.error("[DesignerEvents] Cannot save: Current template ID is unknown.");
         showToast('error', 'Cannot determine which template to save.');
         return;
    }

    const payload = formatStructureForApi(templateId); // Use util function
    if (!payload) { 
        return; // Error already shown
    }
    
    const apiUrl = `/api/v1/templates/guilds/${templateId}/structure`;
    saveButton.disabled = true;
    saveButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Saving...`;

    try {
        await apiRequest(apiUrl, { // response not needed on success for PUT
            method: 'PUT', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify(payload) 
        });
        
        showToast('success', `Template structure saved successfully!`);
        // Dispatch event to reset dirty flag
        document.dispatchEvent(new CustomEvent('structureSaved', { 
            detail: { isNew: false } 
        }));

    } catch (error) {
        const isPermissionError = error instanceof ApiError && error.status === 403; 

        if (isPermissionError) {
            console.warn("[DesignerEvents] Permission denied (403) on PUT. Triggering 'Save As New' modal.");
            showToast('warning', 'Cannot modify the initial snapshot. Please save as a new template.');
            const originalName = templateData?.template_name || 'Template';
            const dateSuffix = new Date().toISOString().slice(0, 10);
            const suggestedName = `Copy of ${originalName} - ${dateSuffix}`;
            openSaveAsNewModal(suggestedName); // Call the modal's open function
            state.setDirty(true); // Ensure state remains dirty
        } else {
            console.error("[DesignerEvents] Error saving template structure via PUT:", error);
            // apiRequest handles toast
        }
    } finally {
         saveButton.innerHTML = `<i class="bi bi-save-fill"></i> <span class="d-none d-md-inline">Save Structure</span>`;
         // ---> UPDATED: Use new function
         updateToolbarButtonStates(); 
    }
}

// NEW: Handles the Toolbar "Activate" button click
function handleToolbarActivateClick() {
    console.log("[DesignerEvents] Activate button clicked.");
    const templateData = state.getCurrentTemplateData();
    const templateId = templateData?.template_id;
    const templateName = templateData?.template_name || 'Unnamed Template'; // Provide a fallback name

    if (templateId === undefined || templateId === null) {
        console.error("[DesignerEvents] Cannot activate: Current template ID is unknown.");
        showToast('error', 'Cannot determine which template to activate.');
        return;
    }
    
    // Check if the template is already active (we might need to fetch/store this info first)
    // For now, let's assume we always show the confirmation. We'll add the check later.
    // TODO: Fetch/store active status and potentially disable button if already active.

    console.log(`[DesignerEvents] Requesting activation confirmation for: ${templateName} (ID: ${templateId})`);
    openActivateConfirmModal(templateId, templateName); 
}

// Handles the event when template data is loaded (e.g., from list click)
function handleTemplateDataLoad(event) {
    console.log("[DesignerEvents] Handling 'loadTemplateData' event:", event.detail);
    if (event.detail && event.detail.templateData) {
        const templateData = event.detail.templateData;
        showToast('info', `Loading structure from template: ${templateData.template_name || 'Unnamed Template'}`);
        
        // Update state with the newly loaded template data
        state.setCurrentTemplateData(templateData);
        
        // Re-populate widgets and tree - Use functions from designerWidgets and structureTree directly
        populateGuildDesignerWidgets(templateData);
        initializeStructureTree(templateData);

        // Reset dirty flag and update buttons
        state.setDirty(false);
        // ---> UPDATED: Use new function
        updateToolbarButtonStates(); 

    } else {
        console.error("[DesignerEvents] 'loadTemplateData' event received without valid data.");
        showToast('error', 'Failed to load template data from event.');
    }
}

// Handles the event when the tree structure is changed (e.g., node moved)
function handleStructureChange(event) {
    console.log("[DesignerEvents] Handling 'structureChanged' event:", event.detail);
    state.setDirty(true); // Set dirty flag via state module
    // ---> UPDATED: Use new function
    updateToolbarButtonStates();
}

// --- NEW: Handler for delete request --- 
function handleRequestDeleteTemplate(event) {
    console.log("[DesignerEvents] Handling 'requestDeleteTemplate' event:", event.detail);
    const { templateId, templateName, listType } = event.detail;
    if (templateId !== undefined && templateName !== undefined && listType !== undefined) {
        openDeleteModal(templateId, templateName, listType);
    } else {
        console.error("[DesignerEvents] 'requestDeleteTemplate' event missing necessary detail data.");
        showToast('error', 'Could not initiate delete process.');
    }
}

// NEW: Handler for activation request (e.g., from list widget)
function handleRequestActivateTemplate(event) {
    console.log("[DesignerEvents] Handling 'requestActivateTemplate' event:", event.detail);
    const { templateId, templateName } = event.detail;

    if (templateId === undefined || templateId === null || !templateName) {
        console.error("[DesignerEvents] 'requestActivateTemplate' event missing necessary detail data.");
        showToast('error', 'Could not initiate activation process: Details missing.');
        return;
    }

    // Open the same confirmation modal used by the toolbar button
    openActivateConfirmModal(templateId, templateName);
}

// --- NEW: Handler for confirmed delete ---
async function handleTemplateDeleteConfirmed(event) {
    console.log("[DesignerEvents] Handling 'deleteConfirmed' event:", event.detail);
    const { templateId, listType } = event.detail;

    if (templateId === undefined || templateId === null || !listType) {
        console.error("[DesignerEvents] 'deleteConfirmed' event missing necessary data.");
        showToast('error', 'Delete confirmation failed: Missing ID or list type.');
        return;
    }

    const apiUrl = `/api/v1/templates/guilds/${templateId}`;
    showToast('info', `Attempting to delete template ID: ${templateId}...`);

    try {
        await apiRequest(apiUrl, { method: 'DELETE' });
        showToast('success', `Template (ID: ${templateId}) deleted successfully!`);

        // Determine which list widget to refresh
        let listContentEl = null;
        let initializer = null;
        const guildId = getGuildIdFromUrl();

        if (listType === 'saved') {
            listContentEl = document.getElementById('widget-content-template-list');
            initializer = initializeTemplateList;
        } else if (listType === 'shared') {
            // listContentEl = document.getElementById('widget-content-shared-template-list');
            // initializer = initializeSharedTemplateList; // Assuming this exists
            console.warn("[DesignerEvents] Shared template list refresh not implemented yet after delete.");
            // TODO: Implement shared template list refresh if needed
        }

        if (listContentEl && initializer && guildId) {
            console.log(`[DesignerEvents] Refreshing ${listType} template list after deletion.`);
            // Re-initialize the specific list widget
            initializer(listContentEl, guildId); 
        } else if (guildId) {
            console.warn(`[DesignerEvents] Could not find elements or initializer to refresh ${listType} list.`);
        } else {
            console.warn("[DesignerEvents] Could not find guildId to refresh list after delete.");
        }

    } catch (error) {
        console.error(`[DesignerEvents] Error deleting template (ID: ${templateId}):`, error);
        // apiRequest handles showing the toast
    }
}

// NEW: Handles the confirmation from the Activate modal
async function handleActivateConfirmed(event) {
    console.log("[DesignerEvents] Handling 'activateConfirmed' event:", event.detail);
    const { templateId } = event.detail;

    if (templateId === undefined || templateId === null) {
        console.error("[DesignerEvents] 'activateConfirmed' event missing templateId.");
        showToast('error', 'Activation failed: Template ID was missing.');
        return;
    }

    const apiUrl = `/api/v1/templates/guilds/${templateId}/activate`;
    const activateButton = document.getElementById('activate-template-btn'); // Need button for loading state
    const originalButtonText = activateButton ? activateButton.innerHTML : ''; // Store original content

    if (activateButton) {
        activateButton.disabled = true;
        activateButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Activating...`;
    }
    showToast('info', `Activating template ID: ${templateId}...`);

    try {
        const response = await apiRequest(apiUrl, { method: 'POST' }); // No body needed
        
        console.log('[DesignerEvents] Template activated successfully via POST:', response);
        showToast('success', `Template (ID: ${templateId}) activated successfully!`);

        // Update state: Mark current template as active and update global active ID
        state.setActiveTemplateId(String(templateId)); // Update the guild-wide active ID (Ensure string)
        // Ensure dirty flag is false (activation implies saved state)
        state.setDirty(false); 

        // ---> UPDATED: Update buttons after successful activation
        updateToolbarButtonStates();

        // Dispatch 'templateActivated' event (as per TODO)
        document.dispatchEvent(new CustomEvent('templateActivated', { 
            detail: { activatedTemplateId: templateId } 
        }));
        console.log("[DesignerEvents] Dispatched 'templateActivated' event.");

    } catch (error) {
        console.error(`[DesignerEvents] Error activating template (ID: ${templateId}) via POST:`, error);
        // apiRequest already shows toast on error
    } finally {
        // Restore button appearance (loading spinner removed)
        if (activateButton) {
            activateButton.innerHTML = originalButtonText; 
        }
        // ---> UPDATED: Always update button states in finally block
        updateToolbarButtonStates();
        console.log("[DesignerEvents] Button states updated in finally block after activation attempt.");
    }
}

// NEW: Handler for share request (from list widget)
function handleRequestShareTemplate(event) {
    console.log("[DesignerEvents] Handling 'requestShareTemplate' event:", event.detail);
    const { templateId, templateName } = event.detail;

    if (templateId === undefined || templateId === null || !templateName) {
        console.error("[DesignerEvents] 'requestShareTemplate' event missing necessary detail data.");
        showToast('error', 'Could not initiate share process: Details missing.');
        return;
    }
    // Open the share modal
    openShareModal(templateId, templateName);
}

// --- Event Listener Setup Functions --- 

function setupPanelToggles() {
    const leftPanelBtn = document.getElementById('toggle-left-panel-btn');
    const rightPanelBtn = document.getElementById('toggle-right-panel-btn');
    const leftPanel = document.querySelector('.editor-panel-left');
    const rightPanel = document.querySelector('.editor-panel-right');

    if (leftPanelBtn && leftPanel) {
        leftPanelBtn.addEventListener('click', () => {
            leftPanel.classList.toggle('collapsed');
            const icon = leftPanelBtn.querySelector('i');
            if (icon) icon.className = leftPanel.classList.contains('collapsed') ? 'bi bi-layout-sidebar' : 'bi bi-layout-sidebar-inset';
        });
    }
    if (rightPanelBtn && rightPanel) {
        rightPanelBtn.addEventListener('click', () => {
            rightPanel.classList.toggle('collapsed');
            const icon = rightPanelBtn.querySelector('i');
            if (icon) icon.className = rightPanel.classList.contains('collapsed') ? 'bi bi-layout-sidebar-reverse' : 'bi bi-layout-sidebar-inset-reverse';
        });
    }
}

// Export one main function to set up all listeners
export function initializeDesignerEventListeners() {
    console.log("[DesignerEvents] Initializing designer event listeners...");

    const saveButton = document.getElementById('save-structure-btn');
    saveButton?.addEventListener('click', handleSaveStructureClick);

    const activateButton = document.getElementById('activate-template-btn');
    activateButton?.addEventListener('click', handleToolbarActivateClick);

    // Listener for the 'Save As New' confirmation event (fired by the modal)
    document.addEventListener('saveAsNewConfirmed', handleSaveAsNewConfirmed);

    // Listener for when template data is loaded (e.g., from template list click)
    document.addEventListener('loadTemplateData', handleTemplateDataLoad);

    // Listener for when the structure tree reports changes
    document.addEventListener('structureChanged', handleStructureChange);

    // Listener for delete requests (fired by list widgets)
    document.addEventListener('requestDeleteTemplate', handleRequestDeleteTemplate);

    // Listener for confirmed deletion (fired by delete modal)
    document.addEventListener('deleteConfirmed', handleTemplateDeleteConfirmed);

    // Listener for structure saved (fired by PUT/POST handlers)
    document.addEventListener('structureSaved', handleStructureSaved);

    // Listener for activation confirmation (fired by activate confirm modal)
    document.addEventListener('activateConfirmed', handleActivateConfirmed);

    // ---> ADDED: Listener for activation requests (fired by list widget)
    document.addEventListener('requestActivateTemplate', handleRequestActivateTemplate);

    // ---> ADDED: Listener for share requests (fired by list widget)
    document.addEventListener('requestShareTemplate', handleRequestShareTemplate);

    // Setup panel toggles (if they exist)
    setupPanelToggles(); 

    // Initial button state update
    updateToolbarButtonStates();

    console.log("[DesignerEvents] Designer event listeners initialized.");
}

// Initial log to confirm loading
console.log("[DesignerEvents] Events module loaded.");
