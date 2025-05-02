/**
 * dashboardConfiguration.js
 * 
 * Logic for the Dashboard Configuration widget. 
 * Displays and allows editing of the settings for the currently loaded dashboard 
 * in the Dashboard Editor.
 */

import { showToast, apiRequest } from '/static/js/components/common/notifications.js';
// Import state or other modules if needed later

// --- Module-level variables --- 
let isConfigLoadedListenerAdded = false;
let currentConfigId = null; // Store the ID of the loaded config
// ----------------------------

/**
 * Initializes the Dashboard Configuration widget.
 * @param {HTMLElement} contentElement - The container element for the widget's content 
 *                                      (e.g., #widget-content-dashboard-config-list).
 * @param {object} [configData=null] - The configuration data of the dashboard 
 *                                     currently loaded in the editor. Initially null.
 */
export function initializeDashboardConfiguration(contentElement, configData = null) {
    console.log("[DashboardConfigurationWidget] Initializing...");
    
    if (!contentElement) {
        console.error("[DashboardConfigurationWidget] Content element not provided!");
        return;
    }

    // Clear existing content
    contentElement.innerHTML = ''; 

    if (configData) {
        console.log("[DashboardConfigurationWidget] Received config data:", configData);
        currentConfigId = configData.id; // <-- Store the ID
        console.log(`[DashboardConfigurationWidget] Stored currentConfigId: ${currentConfigId}`);

        // TODO: Render the actual configuration form/display based on configData
        // -- Create Form Elements --
        const form = document.createElement('form');
        form.id = 'dashboard-config-form';
        form.classList.add('p-3'); // Add some padding
        form.addEventListener('submit', (e) => e.preventDefault()); // Prevent default submit

        // Name Field
        const nameGroup = document.createElement('div');
        nameGroup.classList.add('mb-3');
        const nameLabel = document.createElement('label');
        nameLabel.htmlFor = 'dashboard-config-name';
        nameLabel.classList.add('form-label', 'small');
        nameLabel.textContent = 'Configuration Name:';
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.id = 'dashboard-config-name';
        nameInput.classList.add('form-control', 'form-control-sm');
        nameInput.value = configData.name || '';
        nameInput.required = true;
        nameGroup.appendChild(nameLabel);
        nameGroup.appendChild(nameInput);
        form.appendChild(nameGroup);

        // Description Field
        const descGroup = document.createElement('div');
        descGroup.classList.add('mb-3');
        const descLabel = document.createElement('label');
        descLabel.htmlFor = 'dashboard-config-description';
        descLabel.classList.add('form-label', 'small');
        descLabel.textContent = 'Description:';
        const descTextarea = document.createElement('textarea');
        descTextarea.id = 'dashboard-config-description';
        descTextarea.classList.add('form-control', 'form-control-sm');
        descTextarea.rows = 2;
        descTextarea.value = configData.description || '';
        descGroup.appendChild(descLabel);
        descGroup.appendChild(descTextarea);
        form.appendChild(descGroup);
        
        // TODO: Add fields for other relevant config properties (e.g., type display)
        const typeDisplay = document.createElement('p');
        typeDisplay.innerHTML = `<small class="text-muted">Type: ${configData.dashboard_type || 'N/A'}</small>`;
        form.appendChild(typeDisplay);

        // Save Button
        const saveButton = document.createElement('button');
        saveButton.type = 'button'; // Use type=button to prevent implicit submit
        saveButton.id = 'dashboard-config-save-btn';
        saveButton.classList.add('btn', 'btn-primary', 'btn-sm');
        saveButton.textContent = 'Save Configuration';
        saveButton.disabled = true; // Disabled initially
        saveButton.addEventListener('click', async () => { // <-- Make handler async
            console.log("[DashboardConfigurationWidget] Save clicked.");
            if (!currentConfigId) {
                console.error("[DashboardConfigurationWidget] Cannot save: No config ID available.");
                showToast('error', 'Cannot save: Configuration ID is missing.');
                return;
            }

            const newName = nameInput.value.trim();
            const newDescription = descTextarea.value.trim();

            if (!newName) {
                showToast('error', 'Configuration name cannot be empty.');
                nameInput.focus();
                return;
            }

            const apiUrl = `/api/v1/dashboards/configurations/${currentConfigId}`;
            const payload = {
                name: newName,
                description: newDescription
                // Only include fields managed by this widget
            };

            console.log(`[DashboardConfigurationWidget] Saving to ${apiUrl} with payload:`, payload);
            saveButton.disabled = true;
            saveButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
            showToast('info', 'Saving configuration...');

            try {
                const updatedConfig = await apiRequest(apiUrl, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                console.log("[DashboardConfigurationWidget] Save successful:", updatedConfig);
                showToast('success', 'Configuration saved successfully!');
                // Keep button disabled as changes are now saved
            } catch (error) {
                console.error("[DashboardConfigurationWidget] Error saving configuration:", error);
                // Re-enable button on error to allow retry
                saveButton.disabled = false; 
            } finally {
                 // Restore button text
                 saveButton.innerHTML = 'Save Configuration';
            }
        });
        form.appendChild(saveButton);
        
        // Add input listeners to enable save button
        const enableSave = () => { saveButton.disabled = false; };
        nameInput.addEventListener('input', enableSave);
        descTextarea.addEventListener('input', enableSave);

        // Append form to content element
        contentElement.appendChild(form);
        // -- End Form Elements --
        
        /* // Remove old JSON display
        contentElement.innerHTML = `
            <div class="p-3">
                <h5>Configuration</h5>
                <p>Name: ${configData.name || 'N/A'}</p> 
                <pre class="small bg-light p-2 rounded">${JSON.stringify(configData, null, 2)}</pre>
                <p class="text-muted small">(Display and editing form TBD)</p>
            </div>
        `;
        */
    } else {
        // Display placeholder if no dashboard is loaded in the editor yet
        contentElement.innerHTML = '<p class="panel-placeholder p-3">No dashboard loaded in editor.</p>';
        console.log("[DashboardConfigurationWidget] No initial config data provided.");
    }

    // --- Add event listener ONCE --- 
    if (!isConfigLoadedListenerAdded) {
        document.addEventListener('dashboardConfigLoaded', (event) => {
            console.log("[DashboardConfigurationWidget] Received 'dashboardConfigLoaded' event:", event.detail);
            const receivedConfigData = event.detail?.configData;
            // Re-initialize the widget content with the received data
            initializeDashboardConfiguration(contentElement, receivedConfigData);
        });
        isConfigLoadedListenerAdded = true;
        console.log("[DashboardConfigurationWidget] 'dashboardConfigLoaded' listener added.");
    }
    // -----------------------------
}

// --- Helper functions for rendering form elements, handling input, API calls etc. will go here ---

// Make sure the module indicates it's loaded.
console.log("dashboardConfiguration.js module loaded");
