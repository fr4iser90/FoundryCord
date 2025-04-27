// Module to manage shared state for the Guild Designer

let currentActiveTemplateId = null;
let isStructureDirty = false;
let currentTemplateData = null;

// Using a reference object for the dirty flag allows passing it to other modules
// where its value can be updated directly.
const dirtyFlagRef = { value: isStructureDirty };

export const state = {
    getActiveTemplateId: () => currentActiveTemplateId,
    setActiveTemplateId: (id) => { currentActiveTemplateId = id; },

    // Use the reference object for getting/setting dirty status
    isDirty: () => dirtyFlagRef.value,
    setDirty: (dirty) => { 
        dirtyFlagRef.value = dirty; 
        // Optionally, dispatch an event here if other modules need to react DIRECTLY to dirty changes
        // document.dispatchEvent(new CustomEvent('designerDirtyStateChanged', { detail: { isDirty: dirtyFlagRef.value } }));
    },
    getDirtyFlagRef: () => dirtyFlagRef, // Provide direct access to the ref object if needed cautiously

    getCurrentTemplateData: () => currentTemplateData,
    setCurrentTemplateData: (data) => { currentTemplateData = data; },
};

// Initial log to confirm loading
console.log("[DesignerState] State module loaded.");
