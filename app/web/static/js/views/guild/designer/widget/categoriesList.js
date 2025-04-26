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
        contentElement.innerHTML = '<p class="panel-placeholder">Categories data not available.</p>';
        return;
    }

    // console.log("[CategoriesListWidget] Populating...");

    if (templateData.categories.length > 0) {
        templateData.categories.sort((a, b) => a.position - b.position);

        // Create elements using DOM manipulation
        const listElement = document.createElement('ul');
        listElement.className = 'list-group list-group-flush';
        const fragment = document.createDocumentFragment();

        templateData.categories.forEach(cat => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';

            const nameSpan = document.createElement('span');
            const icon = document.createElement('i');
            icon.className = 'fas fa-folder me-2 text-warning';
            nameSpan.appendChild(icon);
            nameSpan.appendChild(document.createTextNode(` ${cat.category_name || 'Unnamed Category'}`));

            const badgeSpan = document.createElement('span');
            badgeSpan.className = 'badge bg-secondary rounded-pill';
            badgeSpan.textContent = `Pos: ${cat.position !== undefined ? cat.position : 'N/A'}`;

            listItem.appendChild(nameSpan);
            listItem.appendChild(badgeSpan);
            fragment.appendChild(listItem);
        });

        listElement.appendChild(fragment);
        contentElement.innerHTML = ''; // Clear previous content
        contentElement.appendChild(listElement);

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
        contentElement.innerHTML = '<p class="panel-placeholder">No categories defined.</p>';
    }
} 