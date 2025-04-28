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
import { state } from '../designerState.js'; // Import state if needed

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
    
    // TODO: Add event listeners for input changes in the form fields
    // propNameInput.addEventListener('input', handleInputChange);
    // ... etc ...

    // TODO: Add event listener for the delete button
    // propDeleteBtn.addEventListener('click', handleDeleteClick);

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

    if (!fullNodeData) {
        console.error(`[PropertiesPanel] Could not find full data in state for ${nodeData.type} ID ${nodeData.dbId}`);
        showToast('error', 'Could not load properties for selected item.');
        resetPanel();
        return;
    }
    
    // Pass the full data and original type to populatePanel
    populatePanel(fullNodeData, nodeData.type);
}

// TODO: Implement handleInputChange, handleDeleteClick etc.

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
    propTopicInput.closest('.mb-3').classList.add('d-none'); 
    propNsfwSwitch.closest('.mb-3').classList.add('d-none'); // Hide the whole settings div containing NSFW and Slowmode
    // No need to hide slowmode separately if its parent div is hidden

    // --- Fill Type-Specific Fields & Enable Controls ---
    if (nodeType === 'category') {
        // Enable name editing for categories (LATER - keep disabled for now)
        // propNameInput.disabled = false;
        
        // Enable delete button (LATER - keep disabled for now)
        // propDeleteBtn.disabled = false;
        
    } else if (nodeType === 'channel') {
        // Enable name editing for channels (LATER - keep disabled for now)
        // propNameInput.disabled = false;
        
        // Enable delete button (LATER - keep disabled for now)
        // propDeleteBtn.disabled = false;

        // Show/Populate fields applicable to the specific channel type
        const channelType = data.type ? data.type.toLowerCase() : ''; // Use 'type' from full data
        
        // Topic: Text channels only
        if (channelType === 'text') {
            const topicSection = propTopicInput.closest('.mb-3');
            topicSection.classList.remove('d-none'); // Show topic section
            propTopicInput.value = data.topic || '';
            // propTopicInput.disabled = false; // Keep disabled for now
        }
        
        // Settings Div (NSFW, Slowmode): Text & Voice channels 
        const settingsSection = propNsfwSwitch.closest('.mb-3');
        if (channelType === 'text' || channelType === 'voice') {
            settingsSection.classList.remove('d-none'); // Show settings section
            propNsfwSwitch.checked = data.is_nsfw || false;
            // propNsfwSwitch.disabled = false; // Keep disabled for now
        }

        // Slowmode: Text channels only (within the settings div)
        const slowmodeContainer = propSlowmodeInput.closest('.d-inline-block');
        if (channelType === 'text') {
            slowmodeContainer.classList.remove('d-none'); // Show slowmode input
            propSlowmodeInput.value = data.slowmode_delay || 0;
            // propSlowmodeInput.disabled = false; // Keep disabled for now
        } else {
             slowmodeContainer.classList.add('d-none'); // Hide slowmode if not text
        }
        
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
