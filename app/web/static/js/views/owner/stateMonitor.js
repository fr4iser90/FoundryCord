/**
 * State Monitoring Dashboard
 * Displays collected state information from bot and web runtime
 */
import stateBridge from '/static/js/core/state_bridge/bridgeMain.js';

class StateMonitorDashboard {
    constructor() {
        this.collectors = {};
        this.currentScope = 'all';
        this.currentSnapshot = null;
        this.refreshInterval = null;
        this.autoRefreshEnabled = false;
        this.autoRefreshIntervalMs = 10000; // 10 seconds
        
        // Initialize UI elements
        this.initElements();
        
        // Load available collectors
        this.loadAvailableCollectors();
        
        // Set up event listeners
        this.setupEventListeners();
    }
    
    initElements() {
        // Collector selection panel
        this.collectorPanel = document.getElementById('collector-panel');
        
        // Scope selection buttons
        this.scopeAllBtn = document.getElementById('scope-all');
        this.scopeBotBtn = document.getElementById('scope-bot');
        this.scopeWebBtn = document.getElementById('scope-web');
        
        // Action buttons
        this.captureBtn = document.getElementById('capture-snapshot');
        this.refreshBtn = document.getElementById('refresh-collectors');
        this.downloadBtn = document.getElementById('download-snapshot');
        this.copyBtn = document.getElementById('copy-snapshot');
        this.autoRefreshBtn = document.getElementById('toggle-auto-refresh');
        
        // Results display
        this.resultsPanel = document.getElementById('results-panel');
        this.statusDisplay = document.getElementById('status-display');
        this.snapshotTimestamp = document.getElementById('snapshot-timestamp');
        
        // Initialize toggle switches and other UI components
        this.initializeToggles();
    }
    
    setupEventListeners() {
        // Scope selection
        if (this.scopeAllBtn) {
            this.scopeAllBtn.addEventListener('click', () => this.setScope('all'));
        }
        
        if (this.scopeBotBtn) {
            this.scopeBotBtn.addEventListener('click', () => this.setScope('bot'));
        }
        
        if (this.scopeWebBtn) {
            this.scopeWebBtn.addEventListener('click', () => this.setScope('web'));
        }
        
        // Action buttons
        if (this.captureBtn) {
            this.captureBtn.addEventListener('click', () => this.captureSnapshot());
        }
        
        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => this.loadAvailableCollectors());
        }
        
        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => this.downloadSnapshot());
        }
        
        if (this.copyBtn) {
            this.copyBtn.addEventListener('click', () => this.copySnapshot());
        }
        
        if (this.autoRefreshBtn) {
            this.autoRefreshBtn.addEventListener('click', () => this.toggleAutoRefresh());
        }
    }
    
    async loadAvailableCollectors() {
        try {
            this.setStatus('Loading collectors...');
            
            // First, try to load from backend
            const response = await fetch(`/api/v1/owner/state/collectors?scope=${this.currentScope}`);
            if (!response.ok) {
                // Try to get more info from the response if possible
                let errorBody = await response.text();
                console.error("API Response Error Body:", errorBody);
                throw new Error(`Server responded with ${response.status}: ${response.statusText}. Body: ${errorBody.substring(0, 100)}...`);
            }
            
            const collectors = await response.json();
            
            // Then get browser collectors from stateBridge
            const browserCollectors = Object.keys(stateBridge.collectors).map(name => {
                const collector = stateBridge.collectors[name];
                return {
                    name,
                    description: collector.options.description,
                    requires_approval: collector.options.requiresApproval,
                    scope: collector.options.scope,
                    is_approved: stateBridge.approvedCollectors.has(name)
                };
            });
            
            // Combine both sets of collectors
            this.collectors = {
                server: collectors,
                browser: browserCollectors
            };
            
            // Render the collectors
            this.renderCollectorPanel();
            this.setStatus('Ready');
        } catch (error) {
            console.error('Error loading collectors:', error);
            this.setStatus(`Error: ${error.message}`, 'error');
        }
    }
    
    renderCollectorPanel() {
        // Ensure the main panel container exists
        if (!this.collectorPanel) return;
        
        // DO NOT CLEAR the entire panel anymore
        // this.collectorPanel.innerHTML = '';
        
        // Find the server collectors list container (should exist in static HTML)
        const serverList = document.getElementById('server-collectors');
        if (serverList) {
            // Clear only the list content (e.g., "Loading..." text or previous items)
            serverList.innerHTML = ''; 
            // Populate server collectors
            this.collectors.server.forEach(collector => {
                if (this.currentScope !== 'all' && collector.scope !== this.currentScope && collector.scope !== 'global') {
                    return; // Skip collectors that don't match the current scope
                }
                
                const item = document.createElement('div');
                item.className = 'collector-item';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `collector-${collector.name}`;
                checkbox.dataset.name = collector.name;
                checkbox.dataset.source = 'server';
                checkbox.checked = collector.is_approved || !collector.requires_approval;
                
                const label = document.createElement('label');
                label.htmlFor = checkbox.id;
                label.innerHTML = `
                    <span class="collector-name">${collector.name}</span>
                    <span class="collector-description">${collector.description}</span>
                    ${collector.requires_approval ? 
                        '<span class="badge bg-warning text-dark">Requires Approval</span>' : 
                        '<span class="badge bg-success">Auto-approved</span>'}
                    <span class="badge bg-info">${collector.scope}</span>
                `;
                
                item.appendChild(checkbox);
                item.appendChild(label);
                serverList.appendChild(item);
            });
        } else {
            console.error("Server collector list container #server-collectors not found in HTML.");
        }
        
        // Find the browser collectors list container (should exist in static HTML)
        const browserList = document.getElementById('browser-collectors');
        if (browserList) {
            // Clear only the list content (e.g., "Loading..." text or previous items)
            browserList.innerHTML = ''; 
            // Populate browser collectors
            this.collectors.browser.forEach(collector => {
                if (this.currentScope !== 'all' && collector.scope !== this.currentScope && collector.scope !== 'global') {
                    return; // Skip collectors that don't match the current scope
                }
                
                const item = document.createElement('div');
                item.className = 'collector-item';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `collector-browser-${collector.name}`;
                checkbox.dataset.name = collector.name;
                checkbox.dataset.source = 'browser';
                checkbox.checked = collector.is_approved || !collector.requires_approval;
                
                const label = document.createElement('label');
                label.htmlFor = checkbox.id;
                label.innerHTML = `
                    <span class="collector-name">${collector.name}</span>
                    <span class="collector-description">${collector.description}</span>
                    ${collector.requires_approval ? 
                        '<span class="badge bg-warning text-dark">Requires Approval</span>' : 
                        '<span class="badge bg-success">Auto-approved</span>'}
                    <span class="badge bg-info">${collector.scope}</span>
                `;
                
                item.appendChild(checkbox);
                item.appendChild(label);
                browserList.appendChild(item);
            });
        } else {
            console.error("Browser collector list container #browser-collectors not found in HTML.");
        }
    }
    
    async captureSnapshot() {
        try {
            this.setStatus('Capturing state snapshot...');
            
            // Get selected server collectors
            const serverCollectors = Array.from(document.querySelectorAll('[data-source="server"]:checked'))
                .map(checkbox => checkbox.dataset.name);
                
            // Get selected browser collectors
            const browserCollectors = Array.from(document.querySelectorAll('[data-source="browser"]:checked'))
                .map(checkbox => checkbox.dataset.name);
                
            // Capture browser state first
            const browserSnapshot = await stateBridge.collectState(browserCollectors);
            
            // Then capture server state
            const response = await fetch('/api/v1/owner/state/snapshot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-State-Security-Token': stateBridge.securityToken || ''
                },
                body: JSON.stringify({
                    collectors: serverCollectors,
                    context: { 
                        browser_snapshot: browserSnapshot,
                        source: 'state-monitor-dashboard'
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }
            
            const serverSnapshot = await response.json();
            
            // Combine the snapshots
            this.currentSnapshot = {
                timestamp: Date.now(),
                server: serverSnapshot,
                browser: browserSnapshot
            };
            
            // Update the display
            this.renderResults();
            this.setStatus('Snapshot captured successfully');
            
            // Update timestamp
            if (this.snapshotTimestamp) {
                const date = new Date(this.currentSnapshot.timestamp);
                this.snapshotTimestamp.textContent = `Last captured: ${date.toLocaleString()}`;
            }
        } catch (error) {
            console.error('Error capturing snapshot:', error);
            this.setStatus(`Error: ${error.message}`, 'error');
        }
    }
    
    renderResults() {
        if (!this.resultsPanel || !this.currentSnapshot) return;
        
        // Clear the results panel
        this.resultsPanel.innerHTML = '';
        
        // Create tabs for different data sections
        const tabsContainer = document.createElement('div');
        tabsContainer.innerHTML = `
            <ul class="nav nav-tabs" id="resultTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="server-tab" data-bs-toggle="tab" 
                            data-bs-target="#server-data" type="button" role="tab" 
                            aria-controls="server-data" aria-selected="true">
                        Server State
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="browser-tab" data-bs-toggle="tab" 
                            data-bs-target="#browser-data" type="button" role="tab" 
                            aria-controls="browser-data" aria-selected="false">
                        Browser State
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="combined-tab" data-bs-toggle="tab" 
                            data-bs-target="#combined-data" type="button" role="tab" 
                            aria-controls="combined-data" aria-selected="false">
                        Combined View
                    </button>
                </li>
            </ul>
        `;
        
        const tabContent = document.createElement('div');
        tabContent.className = 'tab-content';
        tabContent.innerHTML = `
            <div class="tab-pane fade show active" id="server-data" role="tabpanel" aria-labelledby="server-tab">
                <div class="json-tree-view" id="server-json-view"></div>
            </div>
            <div class="tab-pane fade" id="browser-data" role="tabpanel" aria-labelledby="browser-tab">
                <div class="json-tree-view" id="browser-json-view"></div>
            </div>
            <div class="tab-pane fade" id="combined-data" role="tabpanel" aria-labelledby="combined-tab">
                <div class="json-tree-view" id="combined-json-view"></div>
            </div>
        `;
        
        // Add tabs and content to the panel
        this.resultsPanel.appendChild(tabsContainer);
        this.resultsPanel.appendChild(tabContent);
        
        // Now populate the JSON views
        this.renderJsonView('server-json-view', this.currentSnapshot.server);
        this.renderJsonView('browser-json-view', this.currentSnapshot.browser);
        this.renderJsonView('combined-json-view', this.currentSnapshot);
    }
    
    renderJsonView(elementId, data) {
        const container = document.getElementById(elementId);
        if (!container) return;
        
        // If we have a JSON viewer library available
        if (window.JSONViewer) {
            const viewer = new JSONViewer();
            container.innerHTML = ''; // Clear previous content
            container.appendChild(viewer.getContainer());
            viewer.showJSON(data, 8);
            return;
        }
        
        // Fallback to a simple pre-formatted JSON display
        const pre = document.createElement('pre');
        pre.className = 'json-display';
        pre.textContent = JSON.stringify(data, null, 2);
        container.appendChild(pre);
    }
    
    setScope(scope) {
        this.currentScope = scope;
        
        // Update active button state
        [this.scopeAllBtn, this.scopeBotBtn, this.scopeWebBtn].forEach(btn => {
            if (btn) {
                btn.classList.remove('active');
            }
        });
        
        // Activate the selected button
        switch (scope) {
            case 'all':
                if (this.scopeAllBtn) this.scopeAllBtn.classList.add('active');
                break;
            case 'bot':
                if (this.scopeBotBtn) this.scopeBotBtn.classList.add('active');
                break;
            case 'web':
                if (this.scopeWebBtn) this.scopeWebBtn.classList.add('active');
                break;
        }
        
        // Update displayed collectors
        this.loadAvailableCollectors();
    }
    
    setStatus(message, type = 'info') {
        if (!this.statusDisplay) return;
        
        this.statusDisplay.textContent = message;
        this.statusDisplay.className = `status status-${type}`;
    }
    
    toggleAutoRefresh() {
        this.autoRefreshEnabled = !this.autoRefreshEnabled;
        
        if (this.autoRefreshEnabled) {
            // Start auto-refresh
            this.refreshInterval = setInterval(() => {
                this.captureSnapshot();
            }, this.autoRefreshIntervalMs);
            
            // Update button appearance
            if (this.autoRefreshBtn) {
                this.autoRefreshBtn.classList.add('active');
                this.autoRefreshBtn.textContent = 'Stop Auto-Refresh';
            }
            
            this.setStatus(`Auto-refresh enabled (${this.autoRefreshIntervalMs / 1000}s interval)`);
        } else {
            // Stop auto-refresh
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
                this.refreshInterval = null;
            }
            
            // Update button appearance
            if (this.autoRefreshBtn) {
                this.autoRefreshBtn.classList.remove('active');
                this.autoRefreshBtn.textContent = 'Start Auto-Refresh';
            }
            
            this.setStatus('Auto-refresh disabled');
        }
    }
    
    downloadSnapshot() {
        if (!this.currentSnapshot) {
            this.setStatus('No snapshot data to download', 'warning');
            return;
        }
        
        // Create a blob with the JSON data
        const json = JSON.stringify(this.currentSnapshot, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        
        // Create a timestamp for the filename
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `state-snapshot-${timestamp}.json`;
        
        // Create a download link and trigger it
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.setStatus('Snapshot downloaded');
    }
    
    async copySnapshot() {
        if (!this.currentSnapshot) {
            this.setStatus('No snapshot data to copy', 'warning');
            return;
        }

        try {
            const jsonString = JSON.stringify(this.currentSnapshot, null, 2);
            await navigator.clipboard.writeText(jsonString);
            this.setStatus('Snapshot copied to clipboard', 'success');
        } catch (err) {
            console.error('Failed to copy snapshot:', err);
            this.setStatus('Failed to copy snapshot to clipboard', 'error');
        }
    }
    
    initializeToggles() {
        // For Bootstrap toggle switches, checkboxes, etc.
        // This would be expanded based on the UI framework used
    }
}

// Initialize the dashboard when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.stateMonitor = new StateMonitorDashboard();
});

export default StateMonitorDashboard; 