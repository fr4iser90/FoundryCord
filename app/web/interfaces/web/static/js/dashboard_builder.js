/**
 * Dashboard Builder JavaScript
 * Handles the interactive functionality of the dashboard builder UI
 */

// Global variables
let grid;
let currentDashboardId = null;
let currentSelectedWidget = null;
let widgetTypes = [];

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize GridStack
    grid = GridStack.init({
        float: false,
        margin: 5,
        cellHeight: 50,
        acceptWidgets: true,
        disableOneColumnMode: true,
    });
    
    // Listen for widget added events
    grid.on('added', function(event, items) {
        items.forEach(item => {
            const widgetType = item.el.getAttribute('data-widget-type');
            if (widgetType) {
                initializeNewWidget(item.el, widgetType);
            }
        });
    });
    
    // Listen for widget selected event
    grid.on('click', function(event, element) {
        if (element) {
            selectWidget(element);
        }
    });
    
    // Load available widget types
    loadWidgetTypes();
    
    // Make widget items draggable
    initializeDraggableWidgets();
    
    // Initialize dashboard list
    loadDashboardList();
    
    // Initialize button handlers
    initializeButtons();
    
    // Check if we're editing an existing dashboard
    const urlParams = new URLSearchParams(window.location.search);
    const dashboardId = urlParams.get('id');
    if (dashboardId) {
        loadDashboard(dashboardId);
    }
});

// Initialize draggable widgets
function initializeDraggableWidgets() {
    document.querySelectorAll('.widget-item').forEach(item => {
        item.addEventListener('mousedown', function(event) {
            const widgetType = this.getAttribute('data-type');
            grid.addWidget({
                x: 0, y: 0, w: 3, h: 2,
                content: `
                    <div class="widget-header">
                        <span>New ${widgetType.replace('_', ' ')} Widget</span>
                    </div>
                    <div class="widget-content">Loading...</div>
                `,
                attributes: {
                    'data-widget-type': widgetType
                }
            });
        });
    });
}

// Initialize a newly added widget
function initializeNewWidget(element, widgetType) {
    // Generate a temporary ID for the widget
    const tempId = 'temp-' + Math.random().toString(36).substr(2, 9);
    element.setAttribute('data-widget-id', tempId);
    
    // Find the widget content div
    const contentDiv = element.querySelector('.widget-content');
    if (contentDiv) {
        contentDiv.id = `widget-content-${tempId}`;
        
        // Generate default widget config based on type
        const defaultConfig = getDefaultConfigForWidgetType(widgetType);
        
        // Store the config on the element
        element.setAttribute('data-widget-config', JSON.stringify(defaultConfig));
        
        // Show some default content
        renderWidgetPreview(contentDiv, widgetType, defaultConfig);
    }
    
    // Select the newly added widget
    selectWidget(element);
}

// Render a preview of the widget content
function renderWidgetPreview(contentDiv, widgetType, config) {
    switch(widgetType) {
        case 'discord_channel':
            contentDiv.innerHTML = `
                <div class="text-center p-3">
                    <div class="mb-2">Discord Channel Preview</div>
                    <div class="small">Channel ID: ${config.channel_id || 'Not set'}</div>
                </div>
            `;
            break;
        case 'discord_members':
            contentDiv.innerHTML = `
                <div class="text-center p-3">
                    <div class="mb-2">Discord Members Preview</div>
                    <div class="small">Server ID: ${config.server_id || 'Not set'}</div>
                </div>
            `;
            break;
        case 'system_stats':
            contentDiv.innerHTML = `
                <div class="p-3">
                    <div class="mb-2">System Stats Preview</div>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-primary" style="width: 45%"></div>
                    </div>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-success" style="width: 65%"></div>
                    </div>
                    <div class="progress">
                        <div class="progress-bar bg-warning" style="width: 30%"></div>
                    </div>
                </div>
            `;
            break;
        case 'button_panel':
            let buttonHtml = '<div class="d-flex flex-wrap gap-2 p-3">';
            if (config.buttons && config.buttons.length > 0) {
                config.buttons.forEach(btn => {
                    buttonHtml += `<button class="btn btn-${btn.color || 'primary'} btn-sm">${btn.label || 'Button'}</button>`;
                });
            } else {
                buttonHtml += `
                    <button class="btn btn-primary btn-sm">Button 1</button>
                    <button class="btn btn-secondary btn-sm">Button 2</button>
                `;
            }
            buttonHtml += '</div>';
            contentDiv.innerHTML = buttonHtml;
            break;
        default:
            contentDiv.innerHTML = `<div class="text-center p-3">Preview for ${widgetType.replace('_', ' ')}</div>`;
    }
}

// Select a widget to edit
function selectWidget(element) {
    // Deselect any previously selected widget
    if (currentSelectedWidget) {
        currentSelectedWidget.classList.remove('selected-widget');
    }
    
    // Mark the new widget as selected
    element.classList.add('selected-widget');
    currentSelectedWidget = element;
    
    // Show properties panel for this widget
    showWidgetProperties(element);
    
    // Hide dashboard settings panel
    document.getElementById('dashboard-settings-panel').style.display = 'none';
    document.getElementById('properties-panel').style.display = 'block';
}

// Get default config for a widget type
function getDefaultConfigForWidgetType(widgetType) {
    // Look up the widget type in our loaded widget types
    const typeInfo = widgetTypes.find(t => t.type === widgetType);
    if (typeInfo && typeInfo.config_schema) {
        // Generate default values from schema
        const defaultConfig = {};
        Object.keys(typeInfo.config_schema).forEach(key => {
            const schema = typeInfo.config_schema[key];
            if (schema.default !== undefined) {
                defaultConfig[key] = schema.default;
            } else if (schema.type === 'string') {
                defaultConfig[key] = '';
            } else if (schema.type === 'number') {
                defaultConfig[key] = 0;
            } else if (schema.type === 'boolean') {
                defaultConfig[key] = false;
            } else if (schema.type === 'array') {
                defaultConfig[key] = [];
            } else if (schema.type === 'object') {
                defaultConfig[key] = {};
            }
        });
        return defaultConfig;
    }
    
    // Fallback default configs
    switch(widgetType) {
        case 'discord_channel':
            return { channel_id: '', show_members: true };
        case 'discord_members':
            return { server_id: '', max_members: 10 };
        case 'system_stats':
            return { refresh_interval: 5 };
        case 'button_panel':
            return { buttons: [
                { label: 'Button 1', action: 'action1', color: 'primary' },
                { label: 'Button 2', action: 'action2', color: 'secondary' }
            ]};
        case 'network_stats':
            return { refresh_interval: 5, show_graph: true };
        case 'game_server_status':
            return { server_id: '', show_players: true };
        default:
            return {};
    }
}

// Show widget properties in the sidebar
function showWidgetProperties(element) {
    const widgetType = element.getAttribute('data-widget-type');
    const widgetId = element.getAttribute('data-widget-id');
    const widgetTitle = element.querySelector('.widget-header span').textContent;
    const configStr = element.getAttribute('data-widget-config');
    const config = configStr ? JSON.parse(configStr) : {};
    
    // Set basic properties
    document.getElementById('widget-title').value = widgetTitle;
    
    // Get grid item metrics
    const gridItem = element.gridstackNode;
    if (gridItem) {
        document.getElementById('widget-width').value = gridItem.w;
        document.getElementById('widget-height').value = gridItem.h;
    }
    
    // Generate widget-specific configuration form
    const configPanel = document.getElementById('widget-specific-config');
    configPanel.innerHTML = '';
    
    // Look up the widget type in our loaded widget types
    const typeInfo = widgetTypes.find(t => t.type === widgetType);
    if (typeInfo && typeInfo.config_schema) {
        Object.keys(typeInfo.config_schema).forEach(key => {
            const schema = typeInfo.config_schema[key];
            const value = config[key] !== undefined ? config[key] : 
                          (schema.default !== undefined ? schema.default : '');
            
            // Create form field based on schema type
            configPanel.appendChild(createFormFieldForSchema(key, schema, value));
        });
    } else {
        // Fallback form generation
        switch(widgetType) {
            case 'discord_channel':
                configPanel.innerHTML = `
                    <div class="mb-3">
                        <label for="widget-channel-id" class="form-label">Channel ID</label>
                        <input type="text" class="form-control" id="widget-channel-id" value="${config.channel_id || ''}">
                    </div>
                    <div class="mb-3 form-check">
                        <input type="checkbox" class="form-check-input" id="widget-show-members" ${config.show_members ? 'checked' : ''}>
                        <label class="form-check-label" for="widget-show-members">Show Members</label>
                    </div>
                `;
                break;
            case 'system_stats':
                configPanel.innerHTML = `
                    <div class="mb-3">
                        <label for="widget-refresh-interval" class="form-label">Refresh Interval (seconds)</label>
                        <input type="number" class="form-control" id="widget-refresh-interval" value="${config.refresh_interval || 5}">
                    </div>
                `;
                break;
            case 'button_panel':
                configPanel.innerHTML = `
                    <div class="mb-3">
                        <label class="form-label">Buttons</label>
                        <div id="button-list">
                            ${(config.buttons || []).map((btn, idx) => `
                                <div class="card mb-2 bg-dark">
                                    <div class="card-body">
                                        <div class="mb-2">
                                            <label for="button-label-${idx}" class="form-label">Label</label>
                                            <input type="text" class="form-control" id="button-label-${idx}" value="${btn.label || ''}">
                                        </div>
                                        <div class="mb-2">
                                            <label for="button-action-${idx}" class="form-label">Action</label>
                                            <input type="text" class="form-control" id="button-action-${idx}" value="${btn.action || ''}">
                                        </div>
                                        <div class="mb-2">
                                            <label for="button-color-${idx}" class="form-label">Color</label>
                                            <select class="form-select" id="button-color-${idx}">
                                                <option value="primary" ${btn.color === 'primary' ? 'selected' : ''}>Primary</option>
                                                <option value="secondary" ${btn.color === 'secondary' ? 'selected' : ''}>Secondary</option>
                                                <option value="success" ${btn.color === 'success' ? 'selected' : ''}>Success</option>
                                                <option value="danger" ${btn.color === 'danger' ? 'selected' : ''}>Danger</option>
                                                <option value="warning" ${btn.color === 'warning' ? 'selected' : ''}>Warning</option>
                                                <option value="info" ${btn.color === 'info' ? 'selected' : ''}>Info</option>
                                            </select>
                                        </div>
                                        <button class="btn btn-sm btn-danger w-100" onclick="removeButton(${idx})">Remove</button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <button class="btn btn-sm btn-outline-secondary w-100" onclick="addButton()">Add Button</button>
                    </div>
                `;
                break;
        }
    }
    
    // Set up button handlers for the properties panel
    document.getElementById('apply-properties').onclick = () => applyWidgetProperties(element);
    document.getElementById('delete-widget').onclick = () => deleteWidget(element);
}

// Create a form field based on schema
function createFormFieldForSchema(key, schema, value) {
    const container = document.createElement('div');
    container.className = 'mb-3';
    
    const label = document.createElement('label');
    label.className = 'form-label';
    label.htmlFor = `widget-${key}`;
    label.textContent = formatLabel(key);
    container.appendChild(label);
    
    if (schema.type === 'string') {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control';
        input.id = `widget-${key}`;
        input.value = value || '';
        container.appendChild(input);
    } else if (schema.type === 'number') {
        const input = document.createElement('input');
        input.type = 'number';
        input.className = 'form-control';
        input.id = `widget-${key}`;
        input.value = value || 0;
        container.appendChild(input);
    } else if (schema.type === 'boolean') {
        const div = document.createElement('div');
        div.className = 'form-check';
        
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.className = 'form-check-input';
        input.id = `widget-${key}`;
        input.checked = !!value;
        div.appendChild(input);
        
        const checkLabel = document.createElement('label');
        checkLabel.className = 'form-check-label';
        checkLabel.htmlFor = `widget-${key}`;
        checkLabel.textContent = formatLabel(key);
        div.appendChild(checkLabel);
        
        container.appendChild(div);
    }
    
    return container;
}

// Format a key as a label
function formatLabel(key) {
    return key
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

// Apply widget properties from the form
function applyWidgetProperties(element) {
    const widgetType = element.getAttribute('data-widget-type');
    const configStr = element.getAttribute('data-widget-config');
    const config = configStr ? JSON.parse(configStr) : {};
    
    // Update title
    const title = document.getElementById('widget-title').value;
    element.querySelector('.widget-header span').textContent = title;
    
    // Update size
    const width = parseInt(document.getElementById('widget-width').value);
    const height = parseInt(document.getElementById('widget-height').value);
    if (!isNaN(width) && !isNaN(height)) {
        grid.update(element, { w: width, h: height });
    }
    
    // Update widget-specific config
    const typeInfo = widgetTypes.find(t => t.type === widgetType);
    if (typeInfo && typeInfo.config_schema) {
        Object.keys(typeInfo.config_schema).forEach(key => {
            const schema = typeInfo.config_schema[key];
            const input = document.getElementById(`widget-${key}`);
            if (input) {
                if (schema.type === 'boolean') {
                    config[key] = input.checked;
                } else if (schema.type === 'number') {
                    config[key] = parseFloat(input.value);
                } else {
                    config[key] = input.value;
                }
            }
        });
    } else {
        // Fallback config update
        switch(widgetType) {
            case 'discord_channel':
                config.channel_id = document.getElementById('widget-channel-id').value;
                config.show_members = document.getElementById('widget-show-members').checked;
                break;
            case 'system_stats':
                config.refresh_interval = parseFloat(document.getElementById('widget-refresh-interval').value);
                break;
            case 'button_panel':
                config.buttons = [];
                const buttonList = document.getElementById('button-list');
                const buttonCards = buttonList.querySelectorAll('.card');
                buttonCards.forEach((card, idx) => {
                    config.buttons.push({
                        label: document.getElementById(`button-label-${idx}`).value,
                        action: document.getElementById(`button-action-${idx}`).value,
                        color: document.getElementById(`button-color-${idx}`).value
                    });
                });
                break;
        }
    }
    
    // Save updated config
    element.setAttribute('data-widget-config', JSON.stringify(config));
    
    // Refresh the widget preview
    const contentDiv = element.querySelector('.widget-content');
    if (contentDiv) {
        renderWidgetPreview(contentDiv, widgetType, config);
    }
}

// Delete a widget
function deleteWidget(element) {
    if (confirm('Are you sure you want to delete this widget?')) {
        grid.removeWidget(element);
        document.getElementById('properties-panel').style.display = 'none';
        currentSelectedWidget = null;
    }
}

// Add a new button to a button panel
function addButton() {
    const buttonList = document.getElementById('button-list');
    const idx = buttonList.querySelectorAll('.card').length;
    
    const buttonCard = document.createElement('div');
    buttonCard.className = 'card mb-2 bg-dark';
    buttonCard.innerHTML = `
        <div class="card-body">
            <div class="mb-2">
                <label for="button-label-${idx}" class="form-label">Label</label>
                <input type="text" class="form-control" id="button-label-${idx}" value="Button ${idx + 1}">
            </div>
            <div class="mb-2">
                <label for="button-action-${idx}" class="form-label">Action</label>
                <input type="text" class="form-control" id="button-action-${idx}" value="action${idx + 1}">
            </div>
            <div class="mb-2">
                <label for="button-color-${idx}" class="form-label">Color</label>
                <select class="form-select" id="button-color-${idx}">
                    <option value="primary" selected>Primary</option>
                    <option value="secondary">Secondary</option>
                    <option value="success">Success</option>
                    <option value="danger">Danger</option>
                    <option value="warning">Warning</option>
                    <option value="info">Info</option>
                </select>
            </div>
            <button class="btn btn-sm btn-danger w-100" onclick="removeButton(${idx})">Remove</button>
        </div>
    `;
    
    buttonList.appendChild(buttonCard);
}

// Remove a button from a button panel
function removeButton(idx) {
    if (confirm('Are you sure you want to remove this button?')) {
        const buttonList = document.getElementById('button-list');
        const buttonCards = buttonList.querySelectorAll('.card');
        buttonCards[idx].remove();
        
        // Re-index the remaining buttons
        buttonList.querySelectorAll('.card').forEach((card, newIdx) => {
            const labels = card.querySelectorAll('label');
            const inputs = card.querySelectorAll('input, select');
            const button = card.querySelector('button');
            
            labels.forEach(label => {
                label.htmlFor = label.htmlFor.replace(/\d+$/, newIdx);
            });
            
            inputs.forEach(input => {
                input.id = input.id.replace(/\d+$/, newIdx);
            });
            
            button.setAttribute('onclick', `removeButton(${newIdx})`);
        });
    }
}

// Initialize button handlers
function initializeButtons() {
    // Preview button
    document.getElementById('preview-btn').addEventListener('click', function() {
        const previewArea = document.getElementById('preview-area');
        if (previewArea.style.display === 'none') {
            previewArea.style.display = 'block';
            this.textContent = 'Hide Preview';
        } else {
            previewArea.style.display = 'none';
            this.textContent = 'Preview';
        }
    });
    
    // New dashboard button
    document.getElementById('new-dashboard-btn').addEventListener('click', function() {
        const modal = new bootstrap.Modal(document.getElementById('newDashboardModal'));
        modal.show();
    });
    
    // Create dashboard button in modal
    document.getElementById('create-dashboard-btn').addEventListener('click', function() {
        const title = document.getElementById('new-dashboard-title').value;
        const description = document.getElementById('new-dashboard-description').value;
        
        if (!title) {
            alert('Please enter a dashboard title');
            return;
        }
        
        // Clear the grid
        grid.removeAll();
        
        // Set title
        document.getElementById('dashboard-title').textContent = title;
        
        // Reset dashboard ID
        currentDashboardId = null;
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('newDashboardModal')).hide();
        
        // Show dashboard settings
        showDashboardSettings(title, description);
    });
    
    // Save dashboard button
    document.getElementById('save-btn').addEventListener('click', saveDashboard);
}

// Show dashboard settings
function showDashboardSettings(title, description) {
    // Hide widget properties
    document.getElementById('properties-panel').style.display = 'none';
    document.getElementById('widgets-panel').style.display = 'none';
    
    // Show dashboard settings
    const settingsPanel = document.getElementById('dashboard-settings-panel');
    settingsPanel.style.display = 'block';
    
    // Set initial values
    document.getElementById('dashboard-title-input').value = title || '';
    document.getElementById('dashboard-description').value = description || '';
    
    // Setup apply button
    document.getElementById('apply-dashboard-settings').onclick = applyDashboardSettings;
}

// Apply dashboard settings
function applyDashboardSettings() {
    const title = document.getElementById('dashboard-title-input').value;
    document.getElementById('dashboard-title').textContent = title;
    
    // Show widget panel again
    document.getElementById('dashboard-settings-panel').style.display = 'none';
    document.getElementById('widgets-panel').style.display = 'block';
}

// Load available widget types
function loadWidgetTypes() {
    // In a real application, this would make an API call
    fetch('/api/v1/dashboards/widget-types')
        .then(response => response.json())
        .then(data => {
            widgetTypes = data;
        })
        .catch(error => {
            console.error('Error loading widget types:', error);
            // Fallback to hardcoded types
            widgetTypes = [
                {
                    type: 'discord_channel',
                    name: 'Discord Channel',
                    description: 'Shows a Discord channel preview',
                    config_schema: {
                        channel_id: { type: 'string', required: true },
                        show_members: { type: 'boolean', default: true }
                    }
                },
                {
                    type: 'system_stats',
                    name: 'System Statistics',
                    description: 'Shows system statistics like CPU, memory, etc.',
                    config_schema: {
                        refresh_interval: { type: 'number', default: 5 }
                    }
                }
            ];
        });
}

// Load dashboard list
function loadDashboardList() {
    // Get dashboards from API
    fetch('/api/v1/dashboards')
        .then(response => response.json())
        .then(dashboards => {
            const dashboardList = document.getElementById('dashboard-list');
            dashboardList.innerHTML = '';
            
            dashboards.forEach(dashboard => {
                const item = document.createElement('div');
                item.className = 'sidebar-item';
                item.textContent = dashboard.title;
                item.addEventListener('click', () => {
                    window.location.href = `/dashboard/builder?id=${dashboard.id}`;
                });
                dashboardList.appendChild(item);
            });
        })
        .catch(error => {
            console.error('Error loading dashboards:', error);
        });
}

// Load an existing dashboard
function loadDashboard(dashboardId) {
    fetch(`/api/v1/dashboards/${dashboardId}`)
        .then(response => response.json())
        .then(dashboard => {
            // Set dashboard ID
            currentDashboardId = dashboard.id;
            
            // Set title
            document.getElementById('dashboard-title').textContent = dashboard.title;
            
            // Clear grid
            grid.removeAll();
            
            // Add widgets
            dashboard.widgets.forEach(widget => {
                const element = grid.addWidget({
                    x: widget.position_x,
                    y: widget.position_y,
                    w: widget.width,
                    h: widget.height,
                    content: `
                        <div class="widget-header">
                            <span>${widget.title}</span>
                        </div>
                        <div class="widget-content" id="widget-content-${widget.id}">Loading...</div>
                    `,
                    attributes: {
                        'data-widget-type': widget.widget_type,
                        'data-widget-id': widget.id,
                        'data-widget-config': JSON.stringify(widget.config)
                    }
                });
                
                // Render widget content
                const contentDiv = element.querySelector('.widget-content');
                if (contentDiv) {
                    renderWidgetPreview(contentDiv, widget.widget_type, widget.config);
                }
            });
        })
        .catch(error => {
            console.error('Error loading dashboard:', error);
            alert('Error loading dashboard. Please try again.');
        });
}

// Save dashboard
function saveDashboard() {
    // Collect dashboard data
    const title = document.getElementById('dashboard-title').textContent;
    const description = document.getElementById('dashboard-description')?.value || '';
    const isPublic = document.getElementById('dashboard-public')?.checked || false;
    
    // Collect widget data
    const widgets = [];
    grid.getGridItems().forEach(element => {
        const widgetType = element.getAttribute('data-widget-type');
        const configStr = element.getAttribute('data-widget-config');
        const config = configStr ? JSON.parse(configStr) : {};
        const titleEl = element.querySelector('.widget-header span');
        const gridItem = element.gridstackNode;
        
        widgets.push({
            widget_type: widgetType,
            title: titleEl ? titleEl.textContent : 'Widget',
            position_x: gridItem.x,
            position_y: gridItem.y,
            width: gridItem.w,
            height: gridItem.h,
            config: config
        });
    });
    
    // Prepare dashboard data
    const dashboardData = {
        title: title,
        description: description,
        is_public: isPublic,
        layout_config: {
            columns: 12
        },
        widgets: widgets
    };
    
    // Send to API
    const url = currentDashboardId 
        ? `/api/v1/dashboards/${currentDashboardId}`
        : '/api/v1/dashboards';
    
    const method = currentDashboardId ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dashboardData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to save dashboard');
        }
        return response.json();
    })
    .then(data => {
        // Update dashboard ID
        currentDashboardId = data.id;
        
        // Show success message
        alert('Dashboard saved successfully!');
        
        // Refresh dashboard list
        loadDashboardList();
    })
    .catch(error => {
        console.error('Error saving dashboard:', error);
        alert('Error saving dashboard. Please try again.');
    });
} 