/**
 * Populates the content of the Template Info widget.
 * @param {object} templateData - The structured template data.
 * @param {HTMLElement} contentElement - The container element for the widget content.
 */
export function initializeTemplateInfo(templateData, contentElement) {
    if (!contentElement) {
        console.warn("[TemplateInfoWidget] Content element not provided.");
        return; // Or find by ID as fallback?
    }
    if (!templateData) {
        contentElement.innerHTML = '<p class="panel-placeholder">Template data not available.</p>';
        return;
    }

    console.log("[TemplateInfoWidget] Populating...");
    contentElement.innerHTML = `
        <h5>${templateData.template_name || 'Unnamed Template'}</h5>
        <p class="mb-0"><small class="text-secondary">Created: ${templateData.created_at ? new Date(templateData.created_at).toLocaleString() : 'N/A'}</small></p>
    `;
} 