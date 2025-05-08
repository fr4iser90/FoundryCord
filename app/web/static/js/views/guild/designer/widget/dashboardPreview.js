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
                switch (definition.component_type) {
                    case 'embed':
                        embedHtml += renderEmbedPreview(definition, settings);
                        break;
                    case 'button':
                        const renderedBtn = renderButtonPreview(definition, settings);
                        const buttonRow = row || 0;
                        if (!buttonRows[buttonRow]) buttonRows[buttonRow] = [];
                        buttonRows[buttonRow].push(renderedBtn);
                        break;
                    case 'selector':
                        embedHtml += renderSelectorPreview(definition, settings);
                        break;
                    case 'modal':
                        embedHtml += renderModalPreview(definition, settings);
                        break;
                    case 'view':
                        embedHtml += renderViewPreview(definition, settings);
                        break;
                    case 'message':
                        embedHtml += renderMessagePreview(definition, settings);
                        break;
                    default:
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

// --- Additional renderers for more component types ---
function renderSelectorPreview(definition, instanceSettings) {
    const placeholder = instanceSettings.placeholder || definition.metadata?.placeholder || 'Select an option';
    const options = instanceSettings.options || definition.metadata?.options || [];
    let optionsHtml = '';
    if (Array.isArray(options) && options.length > 0) {
        for (const opt of options) {
            optionsHtml += `<option>${opt.emoji ? opt.emoji + ' ' : ''}${opt.label || opt.value}</option>`;
        }
    } else {
        optionsHtml = '<option>Option 1</option>';
    }
    return `
        <div class="discord-selector-preview mb-2">
            <select class="form-select form-select-sm">
                <option disabled selected>${placeholder}</option>
                ${optionsHtml}
            </select>
        </div>
    `;
}

function renderModalPreview(definition, instanceSettings) {
    const title = instanceSettings.title || definition.metadata?.title || 'Modal Title';
    const fields = instanceSettings.fields || definition.metadata?.fields || [];
    let fieldsHtml = '';
    if (Array.isArray(fields) && fields.length > 0) {
        for (const field of fields) {
            fieldsHtml += `<div class="modal-field mb-1"><label class="form-label">${field.label || field.name}</label><input class="form-control form-control-sm" placeholder="${field.placeholder || ''}" ${field.required ? 'required' : ''}></div>`;
        }
    }
    return `
        <div class="discord-modal-preview card p-2 mb-2">
            <div class="modal-title fw-bold mb-1">${title}</div>
            ${fieldsHtml}
            <div class="modal-footer mt-2"><button class="btn btn-primary btn-sm" disabled>Submit</button></div>
        </div>
    `;
}

function renderViewPreview(definition, instanceSettings) {
    // Views are containers for buttons/selectors, so just show a placeholder for now
    const timeout = instanceSettings.timeout || definition.metadata?.timeout;
    return `<div class="discord-view-preview card p-2 mb-2"><div class="small text-muted">[View: timeout ${timeout || 'none'}]</div></div>`;
}

function renderMessagePreview(definition, instanceSettings) {
    const content = instanceSettings.content || definition.metadata?.content || 'Message content';
    return `<div class="discord-message-preview alert alert-info p-2 mb-2">${content}</div>`;
}

// Make sure the module indicates it's loaded.
console.log("dashboardPreview.js module loaded"); 