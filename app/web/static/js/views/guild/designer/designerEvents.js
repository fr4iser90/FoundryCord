import { state } from './designerState.js';
import { getGuildIdFromUrl, formatStructureForApi } from './designerUtils.js';
import { apiRequest, showToast, ApiError } from '/static/js/components/common/notifications.js';
import { openSaveAsNewModal } from './modal/saveAsNewModal.js';
import { openDeleteModal } from './modal/deleteModal.js'; // Import delete modal opener
// Import widget initializers needed for refresh
import { initializeTemplateList } from './widget/templateList.js'; 
import { initializeStructureTree } from './widget/structureTree.js';
import { populateGuildDesignerWidgets } from './designerWidgets.js'; // Needed for loadTemplateData

// --- Function to update save button state --- 
// This function needs access to the state's dirty flag reference
function updateSaveButtonState() {
    const saveButton = document.getElementById('save-structure-btn');
    if (saveButton) {
        // Access dirty state via the state module
        saveButton.disabled = !state.isDirty(); 
    } 
}

// --- Event Handler Functions --- 

// Handles the successful save of a template (either PUT or POST)
function handleStructureSaved(event) {
    console.log("[DesignerEvents] Handling 'structureSaved' event:", event.detail);
    state.setDirty(false); // Use state setter
    updateSaveButtonState();
    
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
         updateSaveButtonState(); // Update based on potentially changed dirty state
    }
}

// Handles the event when template data is loaded (e.g., from list click)
function handleTemplateDataLoad(event) {
    console.log("[DesignerEvents] Handling 'loadTemplateData' event:", event.detail);
    if (event.detail && event.detail.templateData) {
        const templateData = event.detail.templateData;
        showToast('info', `Loading structure from template: ${templateData.template_name || 'Unnamed Template'}`);
        
        state.setCurrentTemplateData(templateData); // Update state
        state.setActiveTemplateId(templateData.template_id); // Update active ID state
        
        // Re-populate widgets and tree - Use functions from designerWidgets and structureTree directly
        populateGuildDesignerWidgets(templateData);
        initializeStructureTree(templateData);

        state.setDirty(false); // Reset dirty flag
        updateSaveButtonState(); 

    } else {
        console.error("[DesignerEvents] 'loadTemplateData' event received without valid data.");
        showToast('error', 'Failed to load template data from event.');
    }
}

// Handles the event when the tree structure is changed (e.g., node moved)
function handleStructureChange(event) {
    console.log("[DesignerEvents] Handling 'structureChanged' event:", event.detail);
    state.setDirty(true); // Set dirty flag via state module
    updateSaveButtonState();
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
    console.log("[DesignerEvents] Initializing all event listeners...");
    
    setupPanelToggles();
    
    // Listen for template loading requests (e.g., from template lists)
    document.addEventListener('loadTemplateData', handleTemplateDataLoad);
    console.log("[DesignerEvents] 'loadTemplateData' listener active.");

    // Listen for structure changes from the tree widget
    document.addEventListener('structureChanged', handleStructureChange);
    console.log("[DesignerEvents] 'structureChanged' listener active.");

    // Listen for successful save events (from PUT or POST)
    document.addEventListener('structureSaved', handleStructureSaved);
    console.log("[DesignerEvents] 'structureSaved' listener active.");

    // Listen for confirmation from the Save As New modal
    document.addEventListener('saveAsNewConfirmed', handleSaveAsNewConfirmed);
    console.log("[DesignerEvents] 'saveAsNewConfirmed' listener active.");

    // --- Add listener for delete requests ---
    document.addEventListener('requestDeleteTemplate', handleRequestDeleteTemplate);
    console.log("[DesignerEvents] 'requestDeleteTemplate' listener active.");
    // ---------------------------------------

    // Add listener for the main Save button
    const saveButton = document.getElementById('save-structure-btn');
    if (saveButton) {
        saveButton.addEventListener('click', handleSaveStructureClick);
        console.log("[DesignerEvents] Save button click listener active.");
    } else {
        console.warn("[DesignerEvents] Main save button (#save-structure-btn) not found.");
    }

    // Initial update for save button state based on initial dirty state
    updateSaveButtonState(); 

    console.log("[DesignerEvents] All event listeners initialized.");
}

// Initial log to confirm loading
console.log("[DesignerEvents] Events module loaded.");
