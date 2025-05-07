/**
 * dashboardPreview.js
 * 
 * Logic for the Dashboard Preview widget.
 * Displays a simulated preview of the currently loaded dashboard configuration.
 */

import { showToast } from '/static/js/components/common/notifications.js';
import { fetchComponentDefinitions, getDefinition } from './componentDefinitionStore.js';

// --- Module-level flag to prevent multiple listeners ---
let isConfigLoadedListenerAdded_Preview = false; 
// -----------------------------------------------------

/**
 * Initializes the Dashboard Preview widget.
 * @param {HTMLElement} contentElement - The container element for the widget's content 
 *                                      (e.g., #widget-content-dashboard-preview).
 * @param {object} [initialData=null] - Potentially initial data (though likely unused here).
 */
export function initializeDashboardPreview(contentElement, initialData = null) {
    console.log("[DashboardPreviewWidget] Initializing...");
    
    if (!contentElement) {
        console.error("[DashboardPreviewWidget] Content element not provided!");
        return;
    }

    // Set initial placeholder
    contentElement.innerHTML = '<p class="panel-placeholder p-3">No dashboard loaded to preview.</p>';

    // --- Add event listener ONCE --- 
    if (!isConfigLoadedListenerAdded_Preview) {
        document.addEventListener('dashboardConfigLoaded', async (event) => {
            console.log("[DashboardPreviewWidget] Received 'dashboardConfigLoaded' event:", event.detail);
            const receivedConfigData = event.detail?.configData;
            if (!receivedConfigData) {
                console.warn("[DashboardPreviewWidget] 'dashboardConfigLoaded' event received without valid configData.");
                contentElement.innerHTML = '<p class="panel-placeholder p-3">No dashboard loaded to preview.</p>';
                return;
            }

            // Extract dashboard info
            const { name, id, dashboard_type, config } = receivedConfigData;
            const componentsToRender = config?.components || [];

            // Fetch component definitions (if not already loaded)
            try {
                await fetchComponentDefinitions();
            } catch (err) {
                contentElement.innerHTML = '<p class="text-danger p-3">Error loading component definitions.</p>';
                return;
            }

            // Prepare HTML containers
            let embedHtml = '';
            let buttonRows = {};

            // Iterate over components and render
            for (const compInstance of componentsToRender) {
                const { component_key: componentKey, settings = {}, row } = compInstance;
                const definition = getDefinition(dashboard_type, componentKey);
                if (!definition) {
                    embedHtml += `<div class="alert alert-warning small">Unknown component: ${componentKey}</div>`;
                    continue;
                }
                if (definition.component_type === 'embed') {
                    embedHtml += renderEmbedPreview(definition, settings);
                } else if (definition.component_type === 'button') {
                    const rendered = renderButtonPreview(definition, settings);
                    const buttonRow = row || 0;
                    if (!buttonRows[buttonRow]) buttonRows[buttonRow] = [];
                    buttonRows[buttonRow].push(rendered);
                } else {
                    embedHtml += `<div class="alert alert-info small">Unsupported component type: ${definition.component_type}</div>`;
                }
            }

            // Group buttons by row
            let buttonsHtml = '';
            const sortedRows = Object.keys(buttonRows).sort((a, b) => a - b);
            for (const rowIdx of sortedRows) {
                buttonsHtml += `<div class="preview-button-row mb-2">${buttonRows[rowIdx].join('')}</div>`;
            }

            // Final HTML output
            contentElement.innerHTML = `
                <div class="discord-preview-wrapper p-3">
                    <h6 class="mb-2">Previewing: ${name || 'Unnamed'} (ID: ${id || 'N/A'})</h6>
                    <hr>
                    <div class="discord-embed-preview mb-3">${embedHtml || '<span class="text-muted small">No embeds to preview.</span>'}</div>
                    <div class="discord-buttons-preview">${buttonsHtml || ''}</div>
                </div>
            `;
        });
        isConfigLoadedListenerAdded_Preview = true;
        console.log("[DashboardPreviewWidget] 'dashboardConfigLoaded' listener added.");
    }
    // -----------------------------
}

// --- Render functions for Discord-style preview ---
function renderEmbedPreview(definition, instanceSettings) {
    // Extract embed properties from definition and instanceSettings
    const title = instanceSettings.title || definition.metadata?.title || 'Embed Title';
    const description = instanceSettings.description || definition.metadata?.description || '';
    const color = instanceSettings.color || definition.metadata?.color || '#5865F2'; // Discord blurple default
    const fields = instanceSettings.fields || definition.metadata?.fields || [];

    // Render fields (if any)
    let fieldsHtml = '';
    if (Array.isArray(fields) && fields.length > 0) {
        fieldsHtml = '<div class="embed-fields">';
        for (const field of fields) {
            const name = field.name || 'Field';
            const value = field.value || '{{value}}';
            const inline = field.inline ? 'inline' : '';
            fieldsHtml += `<div class="embed-field ${inline}"><div class="embed-field-name">${name}</div><div class="embed-field-value">${value}</div></div>`;
        }
        fieldsHtml += '</div>';
    }

    return `
        <div class="discord-embed-preview" style="border-left: 4px solid ${color};">
            <div class="embed-title">${title}</div>
            <div class="embed-description">${description}</div>
            ${fieldsHtml}
        </div>
    `;
}

function renderButtonPreview(definition, instanceSettings) {
    // Extract button properties from definition and instanceSettings
    const label = instanceSettings.label || definition.metadata?.label || 'Button';
    const emoji = instanceSettings.emoji || definition.metadata?.emoji || '';
    const style = instanceSettings.style || definition.metadata?.style || 'primary';
    // Discord button styles: primary, secondary, success, danger, link
    const styleClass = `discord-button-preview discord-button-style-${style}`;
    return `
        <button type="button" class="${styleClass}">
            ${emoji ? `<span class="button-emoji">${emoji}</span>` : ''}
            <span class="button-label">${label}</span>
        </button>
    `;
}

// Make sure the module indicates it's loaded.
console.log("dashboardPreview.js module loaded"); 