// Module to manage shared state for the Guild Designer

let currentActiveTemplateId = null; // ID of the *guild's* active template
let isStructureDirty = false;
let currentTemplateData = null;
let currentTemplateIsActive = false; // Is the *currently loaded* template the active one?

// Using a reference object for the dirty flag allows passing it to other modules
// where its value can be updated directly.
const dirtyFlagRef = { value: isStructureDirty };

export const state = {
    getActiveTemplateId: () => currentActiveTemplateId,
    setActiveTemplateId: (id) => { currentActiveTemplateId = id; },

    // Use the reference object for getting/setting dirty status
    isDirty: () => dirtyFlagRef.value,
    setDirty: (dirty) => {
        if (dirtyFlagRef.value !== dirty) { // Only update and log if changed
            dirtyFlagRef.value = dirty;
            console.log(`[DesignerState] Dirty state set to: ${dirty}`);
            // Optionally, dispatch an event here if other modules need to react DIRECTLY to dirty changes
            // document.dispatchEvent(new CustomEvent('designerDirtyStateChanged', { detail: { isDirty: dirtyFlagRef.value } }));
        }
    },
    getDirtyFlagRef: () => dirtyFlagRef, // Provide direct access to the ref object if needed cautiously

    getCurrentTemplateData: () => currentTemplateData,
    setCurrentTemplateData: (data) => { 
        currentTemplateData = data; 
        console.log("[DesignerState] Current template data updated.");
    },

    // New state for tracking if the loaded template is the active one
    isCurrentTemplateActive: () => currentTemplateIsActive,
    setCurrentTemplateIsActive: (isActive) => {
        if (currentTemplateIsActive !== isActive) { // Only update and log if changed
            currentTemplateIsActive = isActive;
            console.log(`[DesignerState] Current template active status set to: ${isActive}`);
        }
    },
};

// Initial log to confirm loading
console.log("[DesignerState] State module loaded.");
