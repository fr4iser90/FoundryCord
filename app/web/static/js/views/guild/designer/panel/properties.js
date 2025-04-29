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

// --- NEW: Store current node info --- 
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

    // Check if all essential elements were found
    return !!(placeholderDiv && formContainer && propTypeSpan && propIdSpan && 
              propNameInput && propTopicInput && propNsfwSwitch && 
              propSlowmodeInput && propDeleteBtn);
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

    // --- NEW: Store current node info for input handler --- 
    currentNodeType = nodeData.type;
    currentNodeDbId = fullNodeData.id; // Use ID from the full data object
    currentNodeName = fullNodeData.name || 'Unnamed Item'; // Store name here
    // --------------------------------------------------
}

// --- NEW: Handle Input Changes --- 
/**
 * Handles input changes in the properties form fields.
 * Sets the designer state to dirty and updates toolbar buttons.
 * 
 * TODO: Store the specific change temporarily in the state.
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

    // 3. TODO: Store the pending change
    // This requires knowing the ID and type of the currently edited node.
    // We might need to store the current node's ID/type within the properties.js scope
    // when populatePanel is called, or retrieve it from the state again here.
    // Example (Conceptual - requires storing current node info):
    // state.addPendingPropertyChange(currentNodeDbId, currentNodeType, propertyName, newValue);

    // --- NEW: Call state to add the change --- 
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
// --- END NEW --- 

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

    // --- Debug log for name --- 
    console.log(`[PropertiesPanel] Debug: handleDeleteClick - currentNodeName = ${currentNodeName}`);
    // -------------------------

    // Get name from the input field (might be edited)
    const currentName = currentNodeName || 'Unnamed Item';

    console.log(`[PropertiesPanel] Requesting delete confirmation for ${currentNodeType} ID: ${currentNodeDbId}, Name: ${currentName}`);

    // Open the existing delete modal, passing type information
    // The modal currently only handles templates, this needs modification later.
    // Pass a prefixed type to distinguish from template deletion requests later.
    openDeleteModal(currentNodeDbId, currentName, `designer_${currentNodeType}`); 
}
// --- END NEW ---

// --- UI Logic ---

/**
 * Populates the panel fields based on the selected node data.
 * @param {object} data - The full data object for the category or channel (from state).
 * @param {string} nodeType - 'category' or 'channel' (from the event).
 */
function populatePanel(data, nodeType) {
    if (!formContainer || !placeholderDiv) return;

    // Ensure data has an ID (should always be true if findNodeDataInState worked)
    if (data.id === undefined || data.id === null) {
        console.error("[PropertiesPanel] populatePanel called with data missing ID.", data);
        resetPanel();
        return;
    }
    console.log(`[PropertiesPanel] Populating panel for ${nodeType} ID ${data.id}`);

    // Show form, hide placeholder
    formContainer.classList.remove('d-none');
    placeholderDiv.classList.add('d-none');

    // --- Fill Common Fields ---
    propTypeSpan.textContent = nodeType.charAt(0).toUpperCase() + nodeType.slice(1);
    propTypeSpan.className = `badge ${nodeType === 'category' ? 'bg-warning text-dark' : 'bg-info text-dark'}`; // Basic styling
    propIdSpan.textContent = data.id; // Use ID from the full data object
    propNameInput.value = data.name || ''; // Use name from the full data object

    // --- Reset all fields to default visibility/state/value ---
    // Inputs disabled by default, specific logic enables them
    propNameInput.disabled = true;
    propTopicInput.disabled = true;
    propTopicInput.value = '';
    propNsfwSwitch.disabled = true;
    propNsfwSwitch.checked = false;
    propSlowmodeInput.disabled = true;
    propSlowmodeInput.value = 0;
    propDeleteBtn.disabled = true;

    // Hide type-specific fields/sections initially
    const topicSection = propTopicInput.closest('.mb-3'); // Get parent div
    const settingsSection = propNsfwSwitch.closest('.mb-3'); // Get parent div
    const slowmodeContainer = propSlowmodeInput.closest('.d-inline-block'); // Get specific container for slowmode

    topicSection.classList.add('d-none'); 
    settingsSection.classList.add('d-none'); // Hide the whole settings div containing NSFW and Slowmode
    // No need to hide slowmode separately if its parent div is hidden, but good practice to manage its container too
    slowmodeContainer.classList.add('d-none');


    // --- Fill Type-Specific Fields & Adjust Visibility (Controls remain disabled) ---
    if (nodeType === 'category') {
        // Nothing specific to show/hide for categories yet besides common fields
        propDeleteBtn.disabled = false; // Enable delete button for categories
        propNameInput.disabled = false; // Enable name editing for categories
        // Delete button logic will be added later
        
    } else if (nodeType === 'channel') {
        propNameInput.disabled = false; // Enable name editing for channels
        propDeleteBtn.disabled = false; // Enable delete button for channels

        // Show/Populate fields applicable to the specific channel type
        const channelType = data.type ? data.type.toLowerCase() : ''; // Use 'type' from full data
        
        // Topic: Text channels only
        if (channelType === 'text') {
            topicSection.classList.remove('d-none'); // Show topic section
            propTopicInput.value = data.topic || '';
            propTopicInput.disabled = false; // Enable topic editing
        }
        
        // Settings Div (NSFW): Text & Voice channels 
        if (channelType === 'text' || channelType === 'voice') {
            settingsSection.classList.remove('d-none'); // Show settings section
            propNsfwSwitch.checked = data.is_nsfw || false;
            propNsfwSwitch.disabled = false; // Enable NSFW toggle
        }

        // Slowmode (within the settings div): Text channels only
        if (channelType === 'text') {
            // Ensure settings section is visible first if needed (already handled above)
            slowmodeContainer.classList.remove('d-none'); // Show slowmode input within the settings div
            propSlowmodeInput.value = data.slowmode_delay || 0;
            propSlowmodeInput.disabled = false; // Enable slowmode editing
        }
        // Delete button logic will be added later
        
    } else {
         // Handle template root node or other types - reset to placeholder
         console.log("[PropertiesPanel] Selected node is not a category or channel. Resetting panel.");
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
    if (!currentTemplate || !dbId) return null;

    if (nodeType === 'category') {
        return currentTemplate.categories?.find(cat => cat.id === dbId) || null;
    } else if (nodeType === 'channel') {
        return currentTemplate.channels?.find(chan => chan.id === dbId) || null;
    } else {
        // Handle root node or other types if necessary
        if (nodeType === 'template') {
            // Return a mock object or the main template data if useful
            return { id: dbId, name: currentTemplate.template_name, type: 'template' };
        }
        return null;
    }
}
