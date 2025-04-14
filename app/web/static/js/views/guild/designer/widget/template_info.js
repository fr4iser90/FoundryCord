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

    // console.log("[TemplateInfoWidget] Populating..."); // AUSKOMMENTIERT

    // Create elements using DOM manipulation
    const nameHeader = document.createElement('h5');
    nameHeader.textContent = templateData.template_name || 'Unnamed Template';

    const createdP = document.createElement('p');
    createdP.className = 'mb-0';
    const createdSmall = document.createElement('small');
    createdSmall.className = 'text-secondary'; // Changed from text-muted for better visibility maybe?
    createdSmall.textContent = `Created: ${templateData.created_at ? new Date(templateData.created_at).toLocaleString() : 'N/A'}`;
    createdP.appendChild(createdSmall);

    // Clear previous content and append new elements
    contentElement.innerHTML = '';
    contentElement.appendChild(nameHeader);
    contentElement.appendChild(createdP);
} 