// Bot Dashboard Overview JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // GridStack initialisieren
    const grid = GridStack.init({
        cellHeight: 70,
        margin: 10,
        minRow: 1,
        disableOneColumnMode: false,
        float: true,
        resizable: {
            handles: 'e,se,s,sw,w'
        }
    });
    
    // Standard-Widgets laden oder gespeichertes Layout wiederherstellen
    loadUserLayout(grid);
    
    // Auto-Refresh für System-Ressourcen und Aktivitäten
    setInterval(updateSystemResources, 30000);
    setInterval(updateRecentActivities, 60000);
    
    // Event-Handler für Widget-Collapse-Buttons
    document.addEventListener('click', function(e) {
        if (e.target.matches('.widget-toggle') || e.target.closest('.widget-toggle')) {
            const widgetCard = e.target.closest('.widget-card');
            const widgetContent = widgetCard.querySelector('.widget-content');
            const icon = e.target.querySelector('i') || e.target.closest('.widget-toggle').querySelector('i');
            
            if (widgetContent.style.display === 'none') {
                widgetContent.style.display = 'block';
                icon.classList.remove('bi-chevron-down');
                icon.classList.add('bi-chevron-up');
            } else {
                widgetContent.style.display = 'none';
                icon.classList.remove('bi-chevron-up');
                icon.classList.add('bi-chevron-down');
            }
        }
    });
    
    // Layout speichern wenn Widgets verschoben werden
    grid.on('change', function() {
        saveUserLayout(grid);
    });

    // Reset-Button Event-Handler
    const resetButton = document.getElementById('reset-layout');
    if (resetButton) {
        // resetButton.addEventListener('click', resetLayout); // Temporarily commented out - function definition missing
        console.warn("Reset layout button found, but resetLayout function is missing.");
    }
});

// Speichert das Layout im localStorage
function saveUserLayout(grid) {
    const serializedLayout = grid.save();
    localStorage.setItem('userDashboardLayout', JSON.stringify(serializedLayout));
}

// Lädt das Layout aus dem localStorage oder Standard-Layout
function loadUserLayout(grid) {
    // Versuche das gespeicherte Layout zu laden
    const savedLayout = localStorage.getItem('userDashboardLayout');
    
    if (savedLayout) {
        // Wenn ein gespeichertes Layout existiert, lade es
        try {
            grid.load(JSON.parse(savedLayout));
            // Aktualisiere die Widget-Inhalte
            updateWidgetContents();
        } catch (e) {
            console.error('Error loading saved layout:', e);
            loadDefaultWidgets(grid);
        }
    } else {
        // Sonst lade die Standard-Widgets
        loadDefaultWidgets(grid);
    }
}

// Lädt die Standard-Widgets
function loadDefaultWidgets(grid) {
    // Standard-Widgets definieren und hinzufügen
    const widgets = [
        {
            x: 0, y: 0, w: 6, h: 4,
            id: 'system-resources',
            content: createSystemResourcesWidget()
        },
        {
            x: 6, y: 0, w: 6, h: 4,
            id: 'recent-activity',
            content: createRecentActivityWidget()
        },
        {
            x: 0, y: 4, w: 12, h: 5,
            id: 'servers-list',
            content: createServersListWidget()
        },
        {
            x: 0, y: 9, w: 6, h: 4,
            id: 'popular-commands',
            content: createPopularCommandsWidget()
        },
        {
            x: 6, y: 9, w: 6, h: 4,
            id: 'quick-actions',
            content: createQuickActionsWidget()
        }
    ];
    
    grid.load(widgets);
    updateWidgetContents();
}

// Widget-Creator-Funktionen
function createWidgetCard(title, content, icon) {
    return `
        <div class="widget-card">
            <div class="widget-header">
                <h4><i class="bi ${icon} me-2"></i>${title}</h4>
                <button class="widget-toggle" title="Collapse/Expand">
                    <i class="bi bi-chevron-up"></i>
                </button>
            </div>
            <div class="widget-content">
                ${content}
            </div>
        </div>
    `;
}

function createSystemResourcesWidget() {
    return createWidgetCard('System Resources', `
        <div class="resource-grid">
            <div class="resource-card" id="cpu-usage">
                <div class="resource-header">
                    <h4>CPU Usage</h4>
                    <span class="resource-value">0%</span>
                </div>
                <div class="progress mt-2">
                    <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
            </div>
            <div class="resource-card" id="memory-usage">
                <div class="resource-header">
                    <h4>Memory Usage</h4>
                    <span class="resource-value">0%</span>
                </div>
                <div class="progress mt-2">
                    <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
            </div>
        </div>
    `, 'bi-cpu');
}

function createRecentActivityWidget() {
    return createWidgetCard('Recent Activity', `
        <div class="activity-list" id="recent-activities">
            <div class="text-center py-3">
                <div class="spinner-border text-secondary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        </div>
    `, 'bi-activity');
}

function createServersListWidget() {
    return createWidgetCard('Servers', `
        <div class="server-list" id="server-list-container">
            <div class="text-center py-3">
                <div class="spinner-border text-secondary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        </div>
    `, 'bi-hdd-rack');
}

function createPopularCommandsWidget() {
    return createWidgetCard('Popular Commands', `
        <div class="list-group" id="popular-commands-list">
            <div class="text-center py-3">
                <div class="spinner-border text-secondary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        </div>
    `, 'bi-terminal');
}

function createQuickActionsWidget() {
    return createWidgetCard('Quick Actions', `
        <div class="quick-actions">
            <a href="/channel-builder" class="action-card">
                <div class="action-icon">
                    <i class="bi bi-grid"></i>
                </div>
                <div>Channel Builder</div>
            </a>
            <a href="/dashboard-builder" class="action-card">
                <div class="action-icon">
                    <i class="bi bi-layout-text-sidebar"></i>
                </div>
                <div>Dashboard Builder</div>
            </a>
            <a href="/admin/bot-settings" class="action-card">
                <div class="action-icon">
                    <i class="bi bi-gear"></i>
                </div>
                <div>Bot Settings</div>
            </a>
            <a href="/admin/user-management" class="action-card">
                <div class="action-icon">
                    <i class="bi bi-people"></i>
                </div>
                <div>User Management</div>
            </a>
        </div>
    `, 'bi-lightning-charge');
}

// Update-Funktionen für die Widget-Inhalte
function updateWidgetContents() {
    updateSystemResources();
    updateRecentActivities();
    updateServersList();
    // updatePopularCommands(); // Temporarily commented out - function is not defined
}

// Update-Funktion für die Systemressourcen
async function updateSystemResources() {
    try {
        const response = await fetch('/api/v1/system/status');
        if (!response.ok) throw new Error('Failed to fetch system resources');
        
        const data = await response.json();
        
        // CPU-Nutzung aktualisieren
        const cpuEl = document.getElementById('cpu-usage');
        if (cpuEl) {
            cpuEl.querySelector('.resource-value').textContent = `${data.cpu_usage}%`;
            cpuEl.querySelector('.progress-bar').style.width = `${data.cpu_usage}%`;
        }
        
        // Speichernutzung aktualisieren
        const memEl = document.getElementById('memory-usage');
        if (memEl) {
            memEl.querySelector('.resource-value').textContent = `${data.memory_usage}%`;
            memEl.querySelector('.progress-bar').style.width = `${data.memory_usage}%`;
        }
    } catch (error) {
        console.error('Error updating system resources:', error);
    }
}

// Update-Funktion für die letzten Aktivitäten
async function updateRecentActivities() {
    try {
        const response = await fetch('/api/v1/activity/recent');
        if (!response.ok) throw new Error('Failed to fetch recent activities');
        
        const activities = await response.json();
        const container = document.getElementById('recent-activities');
        
        if (!container) return;
        
        if (activities.length === 0) {
            container.innerHTML = '<div class="text-center text-muted py-3">No recent activity</div>';
            return;
        }
        
        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="bi ${getActivityIcon(activity.type)}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-text">${activity.description}</div>
                    <div class="activity-meta text-muted">
                        <small>${formatTimeAgo(activity.timestamp)}</small>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error updating recent activities:', error);
    }
}

// Update-Funktion für die Serverliste
async function updateServersList() {
    try {
        const response = await fetch('/api/v1/servers');
        if (!response.ok) throw new Error('Failed to fetch servers');
        
        const servers = await response.json();
        const container = document.getElementById('server-list-container');
        
        if (!container) return;
        
        if (servers.length === 0) {
            container.innerHTML = '<div class="text-center text-muted py-3">No servers available</div>';
            return;
        }
        
        container.innerHTML = servers.map(server => `
            <div class="server-card">
                ${server.icon_url ? 
                    `<img src="${server.icon_url}" alt="${server.name}" class="server-icon">` : 
                    `<div class="server-icon"><i class="bi bi-discord"></i></div>`
                }
                <div class="server-info">
                    <h5 class="server-name">${server.name}</h5>
                    <div class="server-meta">
                        <small class="text-muted">${server.member_count} members</small>
                        <div class="mt-1">
                            <!-- ${getUserPermissionBadges(server.user_permissions)} --> <!-- Temporarily commented out - function definition missing -->
                            <span class="text-muted small">(Permission badges disabled)</span>
                        </div>
                    </div>
                </div>
                <a href="/bot/servers/${server.id}" class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-box-arrow-in-right"></i>
                </a>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading servers:', error);
        const container = document.getElementById('server-list-container');
        if (container) {
            container.innerHTML = '<div class="alert alert-danger">Failed to load servers</div>';
        }
    }
}

