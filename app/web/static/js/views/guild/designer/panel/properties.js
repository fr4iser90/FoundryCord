/**
 * properties.js
 * 
 * Handles the logic for the Properties Panel in the Guild Structure Designer.
 * - Listens for node selection events.
 * - Populates the panel with data of the selected node.
 * - Handles user input for property editing.
 * - Manages the display state of different property fields.
 */

import { showToast } from '/static/js/components/common/notifications.js';
import { state } from '../designerState.js';
import { openDeleteModal } from '../modal/deleteModal.js';
import { updateToolbarButtonStates } from '../designerEvents.js';

// --- DOM Element References (Lazy Loaded) ---
let panelContent = null;
let placeholderDiv = null;
let formContainer = null;
let propTypeSpan = null;
let propIdSpan = null;
let propNameInput = null;
let propTopicInput = null;
let propNsfwSwitch = null;
let propSlowmodeInput = null;
let propDeleteBtn = null;
// --- NEW: Placeholders & Inline Save ---
let propWebhookPlaceholder = null;
let propDashboardPlaceholder = null;
let propSaveInlineBtn = null;
// --- NEW: Add refs for property groups --- 
let propertyGroups = [];
// --------------------------------------

// Store current node info
let currentNodeType = null;
let currentNodeDbId = null;
let currentNodeName = null;
// ----------------------------------

// Add refs for parent/position later if needed

// --- Initialization ---

function cacheDomElements() {
    panelContent = document.getElementById('properties-panel-content');
    if (!panelContent) return false;

    placeholderDiv = panelContent.querySelector('#properties-placeholder');
    formContainer = panelContent.querySelector('#properties-form-container');
    propTypeSpan = panelContent.querySelector('#prop-type');
    propIdSpan = panelContent.querySelector('#prop-id');
    propNameInput = panelContent.querySelector('#prop-name-input');
    propTopicInput = panelContent.querySelector('#prop-topic-input');
    propNsfwSwitch = panelContent.querySelector('#prop-nsfw-switch');
    propSlowmodeInput = panelContent.querySelector('#prop-slowmode-input');
    propDeleteBtn = panelContent.querySelector('#prop-delete-btn');
    // --- NEW: Cache new elements ---
    propWebhookPlaceholder = panelContent.querySelector('#prop-webhook-placeholder');
    propDashboardPlaceholder = panelContent.querySelector('#prop-dashboard-placeholder');
    propSaveInlineBtn = panelContent.querySelector('#prop-save-inline-btn');
    // --- NEW: Cache property groups --- 
    propertyGroups = formContainer.querySelectorAll('.property-group');
    // -------------------------------

    // Check if all essential elements were found
    // Basic check, assuming placeholders/save button might not exist yet
    return !!(placeholderDiv && formContainer && propTypeSpan && propIdSpan && 
              propNameInput && propTopicInput && propNsfwSwitch && 
              propSlowmodeInput && propDeleteBtn && propertyGroups.length > 0); 
              // Note: Not checking new elements strictly here allows gradual HTML implementation
}

/**
 * Initializes the properties panel logic and event listeners.
 */
export function initializePropertiesPanel() {
    console.log("[PropertiesPanel] Initializing...");
    if (!cacheDomElements()) {
        console.error("[PropertiesPanel] Failed to find essential DOM elements. Aborting initialization.");
        return;
    }

    // Add event listener for node selection
    document.addEventListener('designerNodeSelected', handleNodeSelection);
    
    // --- Add event listeners for input changes --- 
    propNameInput.addEventListener('input', handleInputChange);
    propTopicInput.addEventListener('input', handleInputChange);
    propSlowmodeInput.addEventListener('input', handleInputChange);
    propNsfwSwitch.addEventListener('change', handleInputChange); // Use 'change' for checkbox/switch
    // -----------------------------------------

    // --- Add event listener for the delete button --- 
    propDeleteBtn.addEventListener('click', handleDeleteClick);
    // ---------------------------------------------

    // --- NEW: Add event listener for the inline save button ---
    if (propSaveInlineBtn) {
        propSaveInlineBtn.addEventListener('click', handleInlineSaveClick);
    }
    // -------------------------------------------------------

    resetPanel(); // Show placeholder initially
    console.log("[PropertiesPanel] Initialization complete.");

    // --- NEW: Listener to reset panel when requested --- 
    document.addEventListener('requestPanelReset', resetPanel);
    // ---------------------------------------------------
}

// --- Event Handlers ---

/**
 * Handles the 'designerNodeSelected' event.
 * @param {CustomEvent} event - The event object containing node data in detail.
 */
function handleNodeSelection(event) {
    const nodeData = event.detail;
    console.log("[PropertiesPanel] Received 'designerNodeSelected':", nodeData);
    
    if (!nodeData || !nodeData.type || nodeData.dbId === undefined) { // Check for dbId too
        console.warn("[PropertiesPanel] Invalid or incomplete node data received from event.");
        resetPanel();
        return;
    }

    // Find the full data object using the dbId and type from the event
    const fullNodeData = findNodeDataInState(nodeData.type, nodeData.dbId);

    // --- Debug Log for fullNodeData ---
    console.log("[PropertiesPanel] fullNodeData from state:", fullNodeData);
    // -----------------------------------

    if (!fullNodeData) {
        console.error(`[PropertiesPanel] Could not find full data in state for ${nodeData.type} ID ${nodeData.dbId}`);
        showToast('error', 'Could not load properties for selected item.');
        resetPanel();
        return;
    }
    
    // Pass the full data and original type to populatePanel
    populatePanel(fullNodeData, nodeData.type);

    // --- MODIFIED: Store current node info for input handler --- 
    currentNodeType = nodeData.type;
    // --- CORRECTED: Use the correct ID based on type ---
    currentNodeDbId = (currentNodeType === 'category') 
                        ? fullNodeData.category_id 
                        : (currentNodeType === 'channel') 
                            ? fullNodeData.channel_id 
                            : null; // Fallback to null if type is unknown
    console.log(`[PropertiesPanel] Stored currentNodeType: ${currentNodeType}, currentNodeDbId: ${currentNodeDbId}`);
    // --------------------------------------------------
    
    // Extract name based on type, similar to populatePanel
    let nameToStore = 'Unnamed Item';
    if (currentNodeType === 'category' && fullNodeData.category_name) {
        nameToStore = fullNodeData.category_name;
    } else if (currentNodeType === 'channel' && fullNodeData.channel_name) {
        nameToStore = fullNodeData.channel_name;
    } else if (fullNodeData.name) { // Fallback for template root?
        nameToStore = fullNodeData.name;
    }
    currentNodeName = nameToStore; // Store the correctly extracted name
    console.log(`[PropertiesPanel] Stored currentNodeName: ${currentNodeName}`);
    // --- END MODIFICATION ---
}

// --- NEW: Handle Input Changes --- 
/**
 * Handles input changes in the properties form fields.
 * Sets the designer state to dirty and updates toolbar buttons.
 * Stores the pending change in the designer state.
 * @param {Event} event - The input or change event object.
 */
function handleInputChange(event) {
    const inputElement = event.target;
    const propertyName = inputElement.id; // e.g., 'prop-name-input', 'prop-nsfw-switch'
    const newValue = (inputElement.type === 'checkbox') ? inputElement.checked : inputElement.value;

    console.log(`[PropertiesPanel] Input changed: ${propertyName} = ${newValue}`);

    // 1. Set the state to dirty
    state.setDirty(true);

    // 2. Update the toolbar button states (e.g., enable Save)
    updateToolbarButtonStates(); 

    // --- NEW: Enable inline save button ---
    if (propSaveInlineBtn) {
        propSaveInlineBtn.disabled = false;
    }
    // ------------------------------------

    // --- Call state to add the change --- 
    if (currentNodeType && currentNodeDbId !== null) {
        // Map the input ID back to a simpler property name if needed
        let statePropertyName = propertyName.replace('prop-', '').replace('-input', '').replace('-switch', ''); 
        // e.g., 'prop-name-input' -> 'name', 'prop-nsfw-switch' -> 'nsfw'
        
        // Special handling for nsfw to match potential backend expectation (is_nsfw)
        if (statePropertyName === 'nsfw') {
            statePropertyName = 'is_nsfw';
        }
        // Add more mappings if needed
        
        state.addPendingPropertyChange(currentNodeType, currentNodeDbId, statePropertyName, newValue);
    } else {
        console.warn("[PropertiesPanel] Cannot store pending change: Current node type or ID is not set.");
    }
    // --- END NEW --- 
}

// --- NEW: Handle Delete Click --- 
/**
 * Handles the click event for the delete button in the properties panel.
 * Opens the confirmation modal, passing necessary details.
 */
function handleDeleteClick() {
    if (currentNodeDbId === null || !currentNodeType) {
        console.error("[PropertiesPanel] Delete clicked but current node info is missing.");
        showToast('error', 'Cannot delete: Item details not available.');
        return;
    }

    // Use the internally stored name
    const currentName = currentNodeName || 'Unnamed Item'; 

    console.log(`[PropertiesPanel] Requesting delete confirmation for ${currentNodeType} ID: ${currentNodeDbId}, Name: ${currentName}`);

    // Open the existing delete modal, passing type information
    openDeleteModal(currentNodeDbId, currentName, `designer_${currentNodeType}`);
}

// --- NEW: Handle Inline Save Click ---
/**
 * Handles the click event for the inline save button.
 * Placeholder for future implementation.
 */
function handleInlineSaveClick() {
    if (!state.isDirty()) {
        console.log("[PropertiesPanel] Inline Save clicked, but no changes detected.");
        showToast('info', 'No changes to save.');
        return;
    }

    console.log("[PropertiesPanel] Inline Save button clicked. Dispatching 'requestSaveStructure' event.");
    showToast('info', 'Saving changes...'); // Immediate feedback

    // Dispatch an event that the main save handler in designerEvents.js can listen for
    document.dispatchEvent(new CustomEvent('requestSaveStructure'));

    // Disable the button immediately to prevent double-clicks while saving
    if (propSaveInlineBtn) {
        propSaveInlineBtn.disabled = true;
    }

    // The actual saving logic (API call, state update) is handled by the listener
    // for 'requestSaveStructure' in designerEvents.js, which calls handleSaveStructureClick.
}

// --- UI Logic ---

/**
 * Populates the properties panel with data for the selected node.
 * Handles showing/hiding fields based on node type.
 * @param {object} data - The full data object for the node from the state.
 * @param {string} nodeType - The type of node ('guild', 'category', 'channel').
 */
function populatePanel(data, nodeType) {
    console.log(`[PropertiesPanel] Populating panel for ${nodeType} ID ${data.category_id || data.channel_id || data.template_id}`);

    if (!formContainer || !placeholderDiv) {
        console.error("[PropertiesPanel] Form container or placeholder not cached.");
        return;
    }

    // --- Show form, hide placeholder --- 
    formContainer.classList.remove('d-none');
    placeholderDiv.classList.add('d-none');
    // -----------------------------------

    // --- Hide all specific property groups initially --- 
    propertyGroups.forEach(group => {
        // Keep #properties-general visible if it's a property group
        if (group.id !== 'properties-general') {
            group.classList.add('d-none');
        }
        // Ensure general is visible if it was hidden
        if (group.id === 'properties-general') {
             group.classList.remove('d-none');
        }
    });
    // --- Disable all inputs/buttons initially within the function scope --- 
    const inputs = formContainer.querySelectorAll('input, textarea, button');
    inputs.forEach(input => input.disabled = true);
    // ----------------------------------------------------------------------

    // --- Populate General Info --- 
    let displayType = 'N/A';
    let displayId = 'N/A';
    let isEditable = false; // Flag to enable inputs/buttons at the end

    if (nodeType === 'guild') { // Assuming root node represents the template/guild
        displayType = 'Template';
        displayId = data.template_id || 'N/A';
        propNameInput.value = data.template_name || '';
        // Show only name and general info, keep others hidden
        formContainer.querySelector('#properties-name')?.classList.remove('d-none');
        // Keep all other fields/buttons disabled for the root node for now
        isEditable = false; 
        // Specific elements to re-disable if they were made visible by other groups
        propDeleteBtn.disabled = true;
        propSaveInlineBtn.disabled = true;

    } else if (nodeType === 'category') {
        displayType = 'Category';
        displayId = data.category_id || 'N/A';
        propNameInput.value = data.category_name || '';
        isEditable = true;
        // Show category-specific groups
        formContainer.querySelectorAll('.category-property').forEach(el => el.classList.remove('d-none'));
        
    } else if (nodeType === 'channel') {
        displayType = `Channel (${data.type || 'Unknown'})`; // Use channel_type from DB
        displayId = data.channel_id || 'N/A';
        propNameInput.value = data.channel_name || '';
        propTopicInput.value = data.topic || '';
        propNsfwSwitch.checked = data.is_nsfw || false;
        propSlowmodeInput.value = data.slowmode_delay || 0;
        isEditable = true;
        // Show general channel groups
        formContainer.querySelectorAll('.channel-property').forEach(el => el.classList.remove('d-none'));
        // Show type-specific channel groups
        if (data.type === 'text') {
            formContainer.querySelectorAll('.text-channel-property').forEach(el => el.classList.remove('d-none'));
        } else if (data.type === 'voice') {
            formContainer.querySelectorAll('.voice-channel-property').forEach(el => el.classList.remove('d-none'));
        } else if (data.type === 'forum') {
             formContainer.querySelectorAll('.forum-channel-property').forEach(el => el.classList.remove('d-none'));
        } // Add more types (stage?) if needed
        
    } else {
        // Unknown type, reset the panel
        console.warn(`[PropertiesPanel] Unknown node type received: ${nodeType}`);
        resetPanel();
        return;
    }

    // --- Update General Display --- 
    propTypeSpan.textContent = displayType;
    propTypeSpan.className = `badge bg-primary`; // Use a more prominent color
    propIdSpan.textContent = displayId;

    // --- Enable/Disable Inputs and Buttons based on type --- 
    if (isEditable) {
        // Enable relevant inputs/buttons for editable types (Category, Channel)
        const visibleInputs = formContainer.querySelectorAll('.property-group:not(.d-none) input, .property-group:not(.d-none) textarea');
        visibleInputs.forEach(input => input.disabled = false);
        propDeleteBtn.disabled = false;
        // Keep save button disabled until a change is made
        propSaveInlineBtn.disabled = true; 
        // Ensure save button is visible if properties are editable
        propSaveInlineBtn.classList.remove('d-none'); 

    } else {
        // Explicitly disable for non-editable types (like Guild root)
        inputs.forEach(input => input.disabled = true); 
        propSaveInlineBtn.classList.add('d-none'); // Hide inline save for root
    }
    // -----------------------------------------------------
}

/**
 * Resets the properties panel to its initial state (placeholder visible).
 */
function resetPanel() {
    console.log("[PropertiesPanel] Resetting panel.");
    if (!formContainer || !placeholderDiv || !propertyGroups) {
        console.warn("[PropertiesPanel] Cannot reset panel, DOM elements not ready.");
        return;
    }
    // Hide form, show placeholder
    formContainer.classList.add('d-none');
    placeholderDiv.classList.remove('d-none');

    // Hide all specific groups
    propertyGroups.forEach(group => {
         group.classList.add('d-none');
    });

    // Clear and disable all inputs/buttons within the form
    const inputs = formContainer.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        if (input.type === 'checkbox' || input.type === 'radio') {
            input.checked = false;
        } else {
            input.value = '';
        }
        input.disabled = true;
    });
    const buttons = formContainer.querySelectorAll('button');
    buttons.forEach(button => button.disabled = true);

    // Reset internal state
    currentNodeType = null;
    currentNodeDbId = null;
    currentNodeName = null;
}

// --- Helper Functions ---

/**
 * Finds the full node data object within the current template state.
 * @param {string} nodeType - The type of node ('category' or 'channel').
 * @param {number} dbId - The database ID of the node.
 * @returns {object|null} The full data object or null if not found.
 */
function findNodeDataInState(nodeType, dbId) {
    const currentTemplate = state.getCurrentTemplateData();
    if (!currentTemplate) {
        console.error("[PropertiesPanel] Cannot find node data: Current template state is empty.");
        return null;
    }

    if (nodeType === 'guild') { // Handle root node (template itself)
        // Return a subset of the template data relevant for display
        return {
            template_id: currentTemplate.template_id,
            template_name: currentTemplate.template_name,
            // Add other relevant root properties if needed
        };
    } else if (nodeType === 'category') {
        if (!currentTemplate.categories || !Array.isArray(currentTemplate.categories)) {
             console.warn("[PropertiesPanel] Template data has no categories array.");
             return null;
        }
        // Use category_id for matching
        return currentTemplate.categories.find(cat => cat.category_id === dbId) || null;
    } else if (nodeType === 'channel') {
        if (!currentTemplate.channels || !Array.isArray(currentTemplate.channels)) {
            console.warn("[PropertiesPanel] Template data has no channels array.");
            return null;
        }
        // Use channel_id for matching
        return currentTemplate.channels.find(chan => chan.channel_id === dbId) || null;
    } else {
        console.warn(`[PropertiesPanel] Unknown node type for finding data: ${nodeType}`);
        return null;
    }
}
