/**
 * Populates the content of the Categories List widget.
 * @param {object} templateData - The structured template data.
 * @param {HTMLElement} contentElement - The container element for the widget content.
 * @param {string} guildId - The current guild ID for link generation.
 */
export function initializeCategoriesList(templateData, contentElement, guildId) {
    if (!contentElement) {
        console.warn("[CategoriesListWidget] Content element not provided.");
        return;
    }
     if (!templateData || !Array.isArray(templateData.categories)) {
        contentElement.innerHTML = '<p class="text-muted p-3">Categories data not available.</p>';
        return;
    }

    console.log("[CategoriesListWidget] Populating...");

    if (templateData.categories.length > 0) {
        templateData.categories.sort((a, b) => a.position - b.position);
        const listItems = templateData.categories.map(cat => {
            // Keep the logic to populate categoriesById if needed elsewhere, maybe pass it in/out?
            // For now, just render the list item.
            return `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <span><i class="fas fa-folder me-2 text-warning"></i> ${cat.name || 'Unnamed Category'}</span>
                    <span class="badge bg-secondary rounded-pill">Pos: ${cat.position !== undefined ? cat.position : 'N/A'}</span>
                </li>
            `;
        }).join('');
        contentElement.innerHTML = `<ul class="list-group list-group-flush">${listItems}</ul>`;

        // Ensure Manage link exists - GridManager should handle the header, but link might be missing
        const header = contentElement.closest('.grid-stack-item-content')?.querySelector('.widget-header');
         if (header && guildId && !header.querySelector('a.manage-link')) { // Add class to check specifically
            const manageLink = document.createElement('a');
            manageLink.href = `/guild/${guildId}/designer/categories`;
            manageLink.className = 'btn btn-sm btn-outline-primary ms-auto manage-link'; // Add class
            manageLink.textContent = 'Manage';
             manageLink.style.marginLeft = 'auto';
            header.appendChild(manageLink);
        }

    } else {
        contentElement.innerHTML = '<p class="text-muted p-3">No categories defined.</p>';
    }
} 