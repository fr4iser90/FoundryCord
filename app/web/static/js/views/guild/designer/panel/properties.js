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
// ------------------------------------

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
    // -------------------------------

    // Check if all essential elements were found
    // Basic check, assuming placeholders/save button might not exist yet
    return !!(placeholderDiv && formContainer && propTypeSpan && propIdSpan && 
              propNameInput && propTopicInput && propNsfwSwitch && 
              propSlowmodeInput && propDeleteBtn); 
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
 * Populates the panel fields based on the selected node data.
 * @param {object} data - The full data object for the category or channel (from state).
 * @param {string} nodeType - 'category' or 'channel' (from the event).
 */
function populatePanel(data, nodeType) {
    if (!formContainer || !placeholderDiv) return;

    // Use the correct ID field based on nodeType for check and display
    const correctId = (nodeType === 'category') ? data.category_id : data.channel_id;
    if (correctId === undefined || correctId === null) {
        console.error(`[PropertiesPanel] populatePanel called with data missing correct ID (${nodeType} ID).`, data);
        resetPanel();
        return;
    }
    console.log(`[PropertiesPanel] Populating panel for ${nodeType} ID ${correctId}`);

    // Show form, hide placeholder
    formContainer.classList.remove('d-none');
    placeholderDiv.classList.add('d-none');

    // --- Fill Common Fields ---
    propTypeSpan.textContent = nodeType.charAt(0).toUpperCase() + nodeType.slice(1);
    propTypeSpan.className = `badge ${nodeType === 'category' ? 'bg-warning text-dark' : 'bg-info text-dark'}`; 
    propIdSpan.textContent = correctId; // Display the correct ID
    
    // Use type-specific name field
    let currentName = '';
    if (nodeType === 'category' && data.category_name) {
        currentName = data.category_name;
    } else if (nodeType === 'channel' && data.channel_name) {
        currentName = data.channel_name;
    } else if (data.name) { // Fallback for root node?
        currentName = data.name;
    }
    propNameInput.value = currentName;

    // --- Reset all fields to default visibility/state/value ---
    propTopicInput.value = ''; 
    propNsfwSwitch.checked = false;
    propSlowmodeInput.value = 0;
    propDeleteBtn.disabled = true; // Keep delete disabled by default
    // --- NEW: Reset placeholders and inline save button ---
    if (propWebhookPlaceholder) propWebhookPlaceholder.classList.add('d-none');
    if (propDashboardPlaceholder) propDashboardPlaceholder.classList.add('d-none');
    if (propSaveInlineBtn) {
         propSaveInlineBtn.classList.add('d-none'); // Hide initially
         propSaveInlineBtn.disabled = true; // Disable initially
    }
    // ----------------------------------------------------

    // Hide type-specific fields/sections initially
    const topicSection = propTopicInput.closest('.mb-3'); 
    const settingsSection = propNsfwSwitch.closest('.mb-3');
    const slowmodeContainer = propSlowmodeInput.closest('.d-inline-block');

    topicSection.classList.add('d-none'); 
    settingsSection.classList.add('d-none'); 
    slowmodeContainer.classList.add('d-none');


    // --- Fill Type-Specific Fields & Adjust Visibility ---
    if (nodeType === 'category') {
        propDeleteBtn.disabled = false; 
        propNameInput.disabled = false; 
        // --- NEW: Show inline save for editable nodes ---
        if (propSaveInlineBtn) propSaveInlineBtn.classList.remove('d-none');
        // ---------------------------------------------
        
    } else if (nodeType === 'channel') {
        propNameInput.disabled = false; 
        propDeleteBtn.disabled = false; 
        // --- NEW: Show inline save for editable nodes ---
        if (propSaveInlineBtn) propSaveInlineBtn.classList.remove('d-none');
        // ---------------------------------------------

        // Use 'type' from channel data
        const channelType = data.type ? data.type.toLowerCase() : ''; 
        
        // Topic: Text channels only
        if (channelType === 'text') {
            topicSection.classList.remove('d-none');
            propTopicInput.value = data.topic || '';
            propTopicInput.disabled = false; 
        }
        
        // Settings Div (NSFW): Text & Voice channels 
        if (channelType === 'text' || channelType === 'voice') {
            settingsSection.classList.remove('d-none');
            propNsfwSwitch.checked = data.is_nsfw || false;
            propNsfwSwitch.disabled = false; 
        }

        // Slowmode (within the settings div): Text channels only
        if (channelType === 'text') {
            slowmodeContainer.classList.remove('d-none');
            propSlowmodeInput.value = data.slowmode_delay || 0;
            propSlowmodeInput.disabled = false; 
        }
        
        // --- NEW: Show placeholders for channels ---
        if (propWebhookPlaceholder) propWebhookPlaceholder.classList.remove('d-none');
        if (propDashboardPlaceholder) propDashboardPlaceholder.classList.remove('d-none');
        // -----------------------------------------
        
    } else if (nodeType === 'template') {
         // Special handling for the root template node
         propNameInput.disabled = false; // Allow renaming the template itself?
         propDeleteBtn.disabled = true; // Cannot delete the root node from here
         // --- NEW: Show inline save for root node (for name changes) ---
         if (propSaveInlineBtn) propSaveInlineBtn.classList.remove('d-none');
         // -----------------------------------------------------------
         // Keep other fields hidden/disabled
    } else {
         console.log(`[PropertiesPanel] Selected node type '${nodeType}' not handled explicitly. Resetting panel.`);
         resetPanel(); 
    }
}

/**
 * Resets the panel to its initial placeholder state.
 */
function resetPanel() {
    if (!formContainer || !placeholderDiv) return;
    
    formContainer.classList.add('d-none');
    placeholderDiv.classList.remove('d-none');
    
    // Optionally clear/disable form fields as well
    if (propNameInput) propNameInput.value = '';
    if (propTopicInput) propTopicInput.value = '';
    if (propNsfwSwitch) propNsfwSwitch.checked = false;
    if (propSlowmodeInput) propSlowmodeInput.value = 0;
    
    if (propNameInput) propNameInput.disabled = true;
    if (propTopicInput) propTopicInput.disabled = true;
    if (propNsfwSwitch) propNsfwSwitch.disabled = true;
    if (propSlowmodeInput) propSlowmodeInput.disabled = true;
    if (propDeleteBtn) propDeleteBtn.disabled = true;

    // --- NEW: Hide/disable placeholders and inline save button ---
    if (propWebhookPlaceholder) propWebhookPlaceholder.classList.add('d-none');
    if (propDashboardPlaceholder) propDashboardPlaceholder.classList.add('d-none');
    if (propSaveInlineBtn) {
        propSaveInlineBtn.classList.add('d-none');
        propSaveInlineBtn.disabled = true;
    }
    // ---------------------------------------------------------
}

// --- Helper Functions ---

/**
 * Finds the full data object for a node from the designer state.
 * @param {string} nodeType - 'category' or 'channel'.
 * @param {number} dbId - The database ID.
 * @returns {object|null} The full data object or null if not found.
 */
function findNodeDataInState(nodeType, dbId) {
    const currentTemplate = state.getCurrentTemplateData();
    // Check if currentTemplate and its lists exist
    if (!currentTemplate || !dbId) {
        console.warn("[PropertiesPanel] State or dbId missing in findNodeDataInState");
        return null;
    }

    if (nodeType === 'category') {
        // Use the correct key 'category_id' to find the category
        if (!Array.isArray(currentTemplate.categories)) {
            console.warn("[PropertiesPanel] currentTemplate.categories is not an array");
            return null;
        }
        return currentTemplate.categories.find(cat => cat && cat.category_id === dbId) || null;
    } else if (nodeType === 'channel') {
        // Use the correct key 'channel_id' to find the channel
        if (!Array.isArray(currentTemplate.channels)) {
             console.warn("[PropertiesPanel] currentTemplate.channels is not an array");
             return null;
        }
        return currentTemplate.channels.find(chan => chan && chan.channel_id === dbId) || null;
    } else {
        // Handle root node or other types if necessary
        if (nodeType === 'template') {
            // Check against the main template ID
            if (currentTemplate.template_id === dbId) {
                // Return data consistent with what populatePanel might expect for the root
                return { id: dbId, name: currentTemplate.template_name, type: 'template' }; 
            }
        }
        console.warn(`[PropertiesPanel] Unknown nodeType '${nodeType}' or ID mismatch in findNodeDataInState`);
        return null;
    }
}
