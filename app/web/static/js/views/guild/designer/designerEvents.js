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

// --- Constants for Element IDs ---
const SAVE_BTN_ID = 'save-structure-btn';
const ACTIVATE_BTN_ID = 'activate-template-btn';
const APPLY_BTN_ID = 'apply-template-btn';
const DELETE_UNMANAGED_CHECKBOX_ID = 'delete-unmanaged-checkbox'; // <<< NEW

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
export function updateToolbarButtonStates() {
    const saveButton = document.getElementById('save-structure-btn');
    const activateButton = document.getElementById('activate-template-btn');
    const applyButton = document.getElementById('apply-template-btn'); // Get the new button
    
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

    // --- NEW: Update Apply Button State ---
    if (applyButton) {
        // Disable apply button if:
        // 1. There are unsaved changes (isDirty is true)
        // 2. The currently loaded template is NOT the active one (isActive is false)
        applyButton.disabled = isDirty || !isActive;
        // Set appropriate title based on state
        if (isDirty) {
            applyButton.title = "Save changes before applying the template.";
        } else if (!isActive) {
            applyButton.title = "Activate this template before applying it to Discord.";
        } else {
            applyButton.title = "Apply this template structure to the live Discord server.";
        }
         // console.log(`[DesignerEvents] Apply button disabled: ${applyButton.disabled}`);
    } else {
         console.warn("[DesignerEvents] Apply button not found during state update.");
    }
    // --- END NEW ---
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
        // --- Capture pending changes BEFORE making the API call --- 
        const pendingChangesPayload = state.getPendingPropertyChanges();
        // ---------------------------------------------------------

        const responseData = await apiRequest(apiUrl, { // Now we expect response data
            method: 'PUT', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify(payload) 
        });
        
        showToast('success', `Template structure saved successfully!`);
        
        // --- NEW: Update State and UI --- 
        console.log("[DesignerEvents] Received updated template data after save:", responseData);
        if (responseData) {
            // 1. Update global state
            state.setCurrentTemplateData(responseData);

            // 2. Update jsTree node text if name changed
            if (pendingChangesPayload) {
                const treeInstance = $('#widget-content-structure-tree').jstree(true);
                if (treeInstance) {
                    for (const nodeKey in pendingChangesPayload) {
                        if (pendingChangesPayload[nodeKey].name !== undefined) {
                            const node = treeInstance.get_node(nodeKey); // nodeKey is like "category_123"
                            if (node) {
                                const newName = pendingChangesPayload[nodeKey].name;
                                treeInstance.rename_node(node, newName);
                                console.log(`[DesignerEvents] Renamed node ${nodeKey} in tree to: ${newName}`);
                            }
                        }
                    }
                }
            }
        }
        // 3. Clear pending changes AFTER potentially using them for UI update
        state.clearPendingChanges(); 

        // 4. Reset dirty flag (already done by clearPendingChanges)
        // state.setDirty(false); // Not needed if clearPendingChanges does it
        
        // 5. Dispatch event (if needed by other components, keep it)
        document.dispatchEvent(new CustomEvent('structureSaved', { 
            detail: { isNew: false, updatedData: responseData } // Pass updated data
        }));
        // --- END NEW --- 

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

        // --- NEW: Initialize Delete Unmanaged Checkbox --- 
        const deleteUnmanagedCheckbox = document.getElementById(DELETE_UNMANAGED_CHECKBOX_ID);
        if (deleteUnmanagedCheckbox) {
            const deleteFlag = templateData.template_delete_unmanaged === true; // Ensure boolean
            console.log(`[DesignerEvents] Setting '${DELETE_UNMANAGED_CHECKBOX_ID}' checked state to: ${deleteFlag}`);
            deleteUnmanagedCheckbox.checked = deleteFlag;
            deleteUnmanagedCheckbox.disabled = false; // Enable the checkbox
        } else {
            console.warn(`[DesignerEvents] Checkbox '${DELETE_UNMANAGED_CHECKBOX_ID}' not found during template load.`);
        }
        // --- END NEW ---

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

    // ---> NEU: Guild ID holen <---
    const guildId = getGuildIdFromUrl();
    if (!guildId) {
        console.error("[DesignerEvents] Cannot activate: Could not get Guild ID from URL.");
        showToast('error', 'Activation failed: Could not determine Guild ID.');
        // Optional: Button wiederherstellen?
        return;
    }

    const apiUrl = `/api/v1/guilds/${guildId}/template/templates/${templateId}/activate`;

    
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
        state.setDirty(false); // Ensure dirty flag is false (activation implies saved state)

        updateToolbarButtonStates(); // Update buttons after successful activation

        // Dispatch 'templateActivated' event (as per TODO)
        document.dispatchEvent(new CustomEvent('templateActivated', { 
            detail: { activatedTemplateId: templateId } 
        }));
        console.log("[DesignerEvents] Dispatched 'templateActivated' event.");

    } catch (error) {
        console.error(`[DesignerEvents] Error activating template (ID: ${templateId}) via POST:`, error);
    } finally {
        if (activateButton) {
            activateButton.innerHTML = originalButtonText; 
        }
        updateToolbarButtonStates(); // Always update button states in finally block after activation attempt.
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

// --- NEW: Handler for Apply Template Button Click ---
async function handleApplyTemplateClick() {
    const applyButton = document.getElementById('apply-template-btn');
    if (!applyButton || applyButton.disabled) {
        console.log("[DesignerEvents] Apply button clicked but disabled or missing.");
        return;
    }
    
    const guildId = getGuildIdFromUrl();
    const currentTemplate = state.getCurrentTemplateData();
    const templateId = currentTemplate?.template_id;
    const templateName = currentTemplate?.template_name || 'this template';

    if (!guildId || templateId === undefined || templateId === null) {
        showToast('error', 'Cannot apply: Guild ID or Template ID is missing.');
        return;
    }

    // Confirmation Dialog
    const confirmation = confirm(
        `Are you sure you want to apply the template '${templateName}' (ID: ${templateId}) to the live Discord server for Guild ID ${guildId}? \n\n` +
        `This will attempt to modify the server's categories and channels to match the template. This operation might be irreversible and is currently experimental.`
    );

    if (!confirmation) {
        showToast('info', 'Template application cancelled.');
        return;
    }

    console.log(`[DesignerEvents] Apply template confirmed for template ${templateId} on guild ${guildId}.`);
    showToast('info', `Applying template '${templateName}' to Discord...`);

    applyButton.disabled = true;
    applyButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Applying...`;

    const apiUrl = `/api/v1/guilds/${guildId}/template/apply`;

    try {
        // We might not need a request body if the backend uses the active template for the guild
        const response = await apiRequest(apiUrl, { 
            method: 'POST'
            // Optionally send template ID if backend requires it:
            // headers: { 'Content-Type': 'application/json' }, 
            // body: JSON.stringify({ template_id: templateId })
        });
        
        console.log('[DesignerEvents] Apply template API call successful:', response);
        showToast('success', response.message || `Template '${templateName}' applied successfully!`);
        // No state change needed here unless the apply action deactivates/changes something

    } catch (error) {
        console.error('[DesignerEvents] Error applying template via API:', error);
        // apiRequest handles showing the error toast
    } finally {
        // Re-enable button and restore text regardless of success/failure
        applyButton.disabled = false; // Or re-evaluate state via updateToolbarButtonStates?
        applyButton.innerHTML = `<i class="fas fa-rocket"></i> Apply to Discord`; 
        updateToolbarButtonStates(); // Refresh button state based on current conditions
    }
}
// --- END NEW ---

// --- NEW: Handler for Delete Unmanaged Checkbox Change ---
async function handleDeleteUnmanagedChange(event) {
    const checkbox = event.target;
    const deleteUnmanaged = checkbox.checked;
    const guildId = getGuildIdFromUrl();

    console.log(`[DesignerEvents] '${DELETE_UNMANAGED_CHECKBOX_ID}' changed. New value: ${deleteUnmanaged}`);

    if (!guildId) {
        console.error("[DesignerEvents] Cannot update setting: Guild ID missing.");
        showToast('error', 'Cannot save setting: Guild ID not found.');
        // Revert checkbox state?
        checkbox.checked = !deleteUnmanaged;
        return;
    }

    const apiUrl = `/api/v1/guilds/${guildId}/template/settings`;
    const payload = { delete_unmanaged: deleteUnmanaged };

    checkbox.disabled = true; // Disable during API call

    try {
        await apiRequest(apiUrl, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        showToast('success', `Setting 'Clean Apply' updated to: ${deleteUnmanaged}.`);
        // Optionally update local state if needed, though fetching on load might be sufficient
        // state.setDeleteUnmanaged(deleteUnmanaged); // If state module tracks this
    } catch (error) {
        console.error(`[DesignerEvents] Error updating 'delete_unmanaged' setting:`, error);
        // Revert checkbox state on error
        checkbox.checked = !deleteUnmanaged;
        // apiRequest shows the error toast
    } finally {
        checkbox.disabled = false; // Re-enable checkbox
    }
}
// --- END NEW ---

// --- NEW: Handler for newItemConfirmed --- 
/**
 * Handles the confirmation of adding a new item from the input modal.
 * Adds a temporary node to the tree and marks the state as dirty.
 * @param {CustomEvent} event - The event object containing detail: { itemType, itemName, parentNodeId, position }.
 */
function handleNewItemConfirmed(event) {
    const { itemType, itemName, parentNodeId, position } = event.detail;
    console.log(`[DesignerEvents] Handling 'newItemConfirmed': Adding ${itemType} '${itemName}' under parent ${parentNodeId} at pos ${position}`);

    // 1. Add temporary node to jsTree
    const treeContainer = document.getElementById('widget-content-structure-tree');
    const treeInstance = treeContainer ? $(treeContainer).jstree(true) : null;

    if (!treeInstance) {
        console.error("[DesignerEvents] Cannot add temporary node: jsTree instance not found.");
        showToast('error', 'Failed to add item to the visual structure.');
        return;
    }

    // Generate a temporary ID for the node
    const tempNodeId = `temp_${itemType}_${Date.now()}`;
    let iconClass = 'fas fa-question-circle'; // Default icon
    let nodeTypeForTree = 'channel'; // Default

    if (itemType === 'category') {
        iconClass = 'fas fa-folder text-warning';
        nodeTypeForTree = 'category';
    } else if (itemType === 'text_channel') {
        iconClass = 'fas fa-hashtag text-info';
    } else if (itemType === 'voice_channel') {
        iconClass = 'fas fa-volume-up text-info';
    }

    const newNodeData = {
        id: tempNodeId,
        text: `${itemName} (New)`, // Indicate it's new
        icon: iconClass,
        type: nodeTypeForTree,
        // We don't have a dbId yet
        data: { type: itemType, isTemporary: true } // Store original type and temporary flag
    };

    try {
        const parentId = parentNodeId || '#'; // Use '#' for root if parentNodeId is null/empty
        treeInstance.create_node(parentId, newNodeData, position, (newNode) => {
            console.log(`[DesignerEvents] Temporary node ${newNode.id} created in jsTree.`);
            // Optional: Immediately select the new node?
            // treeInstance.deselect_all();
            // treeInstance.select_node(newNode.id);
        });
    } catch (error) {
        console.error(`[DesignerEvents] Error adding temporary node to jsTree:`, error);
        showToast('error', 'Failed to visually add the new item.');
        return;
    }

    // --- Store pending addition in state --- 
    state.addPendingAddition(tempNodeId, itemType, itemName, parentNodeId, position);
    // ---------------------------------------

    // 3. Set dirty state
    state.setDirty(true);
    updateToolbarButtonStates(); // Update buttons

    showToast('success', `Added '${itemName}'. Save structure to make it permanent.`);
}
// -------------------------------------

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

    const saveButton = document.getElementById(SAVE_BTN_ID);
    saveButton?.addEventListener('click', handleSaveStructureClick);

    const activateButton = document.getElementById(ACTIVATE_BTN_ID);
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

    // --- NEW: Listener for Apply Template ---
    const applyBtn = document.getElementById(APPLY_BTN_ID);
    if (applyBtn) {
        applyBtn.addEventListener('click', handleApplyTemplateClick);
    } else {
        console.warn(`[DesignerEvents] Toolbar button '${APPLY_BTN_ID}' not found.`);
    }
    // --- END NEW ---

    // --- NEW: Delete Unmanaged Checkbox Listener ---
    const deleteUnmanagedCheckbox = document.getElementById(DELETE_UNMANAGED_CHECKBOX_ID);
    deleteUnmanagedCheckbox?.addEventListener('change', handleDeleteUnmanagedChange);

    // --- NEW: Listener for New Item Confirmation ---
    document.addEventListener('newItemConfirmed', handleNewItemConfirmed);
    // ---------------------------------------------

    // Setup panel toggles (if they exist)
    setupPanelToggles(); 

    // Initial button state update
    updateToolbarButtonStates();

    console.log("[DesignerEvents] Designer event listeners initialized.");
}

// Initial log to confirm loading
console.log("[DesignerEvents] Events module loaded.");
