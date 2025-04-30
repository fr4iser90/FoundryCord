// Module to manage shared state for the Guild Designer

// State Variables
let _isDirty = false;
let _currentTemplateData = null; // Holds the full structure { template_id, name, categories: [], channels: [] }
let _activeTemplateId = null; // DB ID of the template marked active in the guild config
let _initialTemplateDataJson = null; // Store the initial unmodified structure as JSON
let _pendingPropertyChanges = {};
let _pendingAdditions = [];

// Public State Object
export const state = {

    setActiveTemplateId: function(id) {
        console.log(`[DesignerState DEBUG] setActiveTemplateId called with ID: ${id} (Type: ${typeof id})`);
        const previousId = _activeTemplateId;
        _activeTemplateId = id;
        if (previousId !== _activeTemplateId) {
            console.log(`[DesignerState] Active template ID updated from ${previousId} to ${_activeTemplateId}`);
        }
    },

    getActiveTemplateId: function() {
        return _activeTemplateId;
    },

    isDirty: function() {
        return _isDirty;
    },

    setDirty: function(dirty) {
        if (_isDirty !== dirty) {
            _isDirty = dirty;
            console.log(`[DesignerState] Dirty state set to: ${_isDirty}`);
            if (!_isDirty) {
                this.clearPendingPropertyChanges(); // Use 'this'
                this.clearPendingAdditions();     // Use 'this'
            }
        }
    },

    getCurrentTemplateData: function() {
        return _currentTemplateData;
    },

    setCurrentTemplateData: function(data) {
        _currentTemplateData = data;
        console.log("[DesignerState] Current template data updated.");
    },

    // --- Property Changes ---
    addPendingPropertyChange: function(nodeType, nodeId, property, value) {
        if (!nodeType || nodeId === undefined || nodeId === null || !property) {
            console.error("[DesignerState] Invalid arguments for addPendingPropertyChange:", { nodeType, nodeId, property, value });
            return;
        }
        const key = `${nodeType}_${nodeId}`;
        if (!_pendingPropertyChanges[key]) {
            _pendingPropertyChanges[key] = {};
        }
        _pendingPropertyChanges[key][property] = value;
        console.log("[DesignerState] Pending changes updated:", _pendingPropertyChanges);
    },

    getPendingPropertyChanges: function() {
        return _pendingPropertyChanges;
    },

    clearPendingPropertyChanges: function() {
        _pendingPropertyChanges = {};
        console.log("[DesignerState] Pending property changes cleared.");
    },

    // --- Pending Additions ---
    addPendingAddition: function(tempId, itemType, itemName, parentNodeId, position) {
        _pendingAdditions.push({
            tempId: tempId,
            itemType: itemType,
            name: itemName,
            parentId: parentNodeId,
            position: position
        });
        console.log("[DesignerState] Pending additions updated:", _pendingAdditions);
    },

    getPendingAdditions: function() {
        return _pendingAdditions;
    },

    clearPendingAdditions: function() {
        _pendingAdditions = [];
        console.log("[DesignerState] Pending additions cleared.");
    }
}; // End state object definition

// Initial log
console.log("[DesignerState] State module loaded.");
