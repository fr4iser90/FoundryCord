/**
 * Simple JSON Viewer Component
 * Renders JSON data as an expandable/collapsible tree structure.
 */
class JSONViewer {
    constructor() {
        this._container = document.createElement('div');
        this._container.className = 'json-viewer';
    }

    // Public method to get the container element
    getContainer() {
        return this._container;
    }

    // Public method to display JSON data
    showJSON(jsonData, maxLevel = 4, startLevel = 0) {
        // Clear previous content
        this._container.innerHTML = '';
        // Start rendering the JSON tree
        const treeRoot = this._renderValue(jsonData, maxLevel, startLevel);
        if (treeRoot) {
            this._container.appendChild(treeRoot);
        } else {
            this._container.textContent = 'Invalid JSON data or empty.';
        }
    }

    // Recursive function to render a value (object, array, or primitive)
    _renderValue(value, maxLevel, level) {
        const type = typeof value;

        if (value === null) {
            return this._createItem('null', 'null');
        } else if (Array.isArray(value)) {
            return this._renderCollection(value, 'array', '[', ']', maxLevel, level);
        } else if (type === 'object') {
            return this._renderCollection(value, 'object', '{', '}', maxLevel, level);
        } else if (type === 'string') {
            return this._createItem('string', `"${value}"`);
        } else if (type === 'number') {
            return this._createItem('number', value);
        } else if (type === 'boolean') {
            return this._createItem('boolean', value);
        } else {
            // Handle undefined or other types
            return this._createItem('undefined', 'undefined');
        }
    }

    // Renders an array or object
    _renderCollection(collection, type, openBracket, closeBracket, maxLevel, level) {
        const element = document.createElement('div');
        element.className = `json-${type}`;

        const isArray = type === 'array';
        const keys = isArray ? null : Object.keys(collection);
        const count = isArray ? collection.length : keys.length;

        // Create the header span (e.g., "{ ... } 3 items")
        const header = this._createCollapsibleHeader(type, openBracket, closeBracket, count, level, maxLevel);
        element.appendChild(header);

        // Stop rendering children if max level is reached or collection is empty
        if (level >= maxLevel || count === 0) {
            return element;
        }

        // Create the container for child elements (initially hidden)
        const childrenContainer = document.createElement('div');
        childrenContainer.className = 'json-children';
        childrenContainer.style.display = 'none'; // Initially collapsed
        childrenContainer.style.marginLeft = '20px';
        element.appendChild(childrenContainer);

        // Populate children container
        if (isArray) {
            collection.forEach((item, index) => {
                const childElement = this._renderValue(item, maxLevel, level + 1);
                if (childElement) {
                    const indexSpan = this._createItem('index', `[${index}]: `);
                    const itemContainer = document.createElement('div');
                    itemContainer.className = 'json-item';
                    itemContainer.appendChild(indexSpan);
                    itemContainer.appendChild(childElement);
                    childrenContainer.appendChild(itemContainer);
                }
            });
        } else {
            keys.forEach(key => {
                const childElement = this._renderValue(collection[key], maxLevel, level + 1);
                 if (childElement) {
                    const keySpan = this._createItem('key', `"${key}": `);
                    const itemContainer = document.createElement('div');
                    itemContainer.className = 'json-item';
                    itemContainer.appendChild(keySpan);
                    itemContainer.appendChild(childElement);
                    childrenContainer.appendChild(itemContainer);
                 }
            });
        }

        return element;
    }

    // Creates the clickable header for objects/arrays
    _createCollapsibleHeader(type, openBracket, closeBracket, count, level, maxLevel) {
        const headerSpan = document.createElement('span');
        headerSpan.className = `json-toggle ${type}`;
        headerSpan.textContent = openBracket;

        // Add ellipsis and item count if content is hidden/collapsible
        if (count > 0 && level < maxLevel) {
             const ellipsis = document.createElement('span');
             ellipsis.className = 'json-ellipsis';
             ellipsis.textContent = ' ... ';
             headerSpan.appendChild(ellipsis);
             headerSpan.appendChild(document.createTextNode(closeBracket)); // Closing bracket

             const countSpan = document.createElement('span');
             countSpan.className = 'json-count';
             countSpan.textContent = ` // ${count} item${count !== 1 ? 's' : ''}`;
             headerSpan.appendChild(countSpan);

             headerSpan.style.cursor = 'pointer';
             headerSpan.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent event bubbling
                const children = headerSpan.nextElementSibling; // Assumes childrenContainer is the next sibling
                if (children && children.classList.contains('json-children')) {
                    const isHidden = children.style.display === 'none';
                    children.style.display = isHidden ? 'block' : 'none';
                    ellipsis.style.display = isHidden ? 'none' : 'inline'; // Toggle ellipsis visibility
                    headerSpan.classList.toggle('expanded', isHidden);
                }
             });
        } else {
             // No items or max level reached, just show brackets
             headerSpan.appendChild(document.createTextNode(closeBracket));
             if (count === 0) {
                 const countSpan = document.createElement('span');
                 countSpan.className = 'json-count';
                 countSpan.textContent = ` // 0 items`;
                 headerSpan.appendChild(countSpan);
             }
        }


        return headerSpan;
    }

    // Helper to create a styled span for different JSON value types
    _createItem(type, value) {
        const span = document.createElement('span');
        span.className = `json-${type}`;
        span.textContent = value;
        return span;
    }
}

// Make it available globally if needed, e.g., for direct use in HTML or simple scripts
window.JSONViewer = window.JSONViewer || JSONViewer; 