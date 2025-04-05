/**
 * Status Widget - Zeigt Statusinformationen an
 */

// Widget definieren
WidgetUI.registerWidget('statusWidget', {
    init: function(config) {
        this.config = config;
        this.refreshInterval = config.options.refreshInterval || 30000;
        this.refreshTimer = null;
    },
    
    render: function() {
        const { container } = this.config;
        
        // Widget-Struktur erstellen
        const widget = WidgetUI.helpers.createWidgetFrame('System Status');
        container.appendChild(widget.frame);
        
        // Content-Bereich speichern für Updates
        this.contentArea = widget.content;
        
        // Initialen Inhalt laden
        this.refresh();
        
        // Regelmäßige Aktualisierung starten
        this.startRefreshTimer();
    },
    
    refresh: async function() {
        WidgetUI.helpers.showLoading(this.contentArea);
        
        try {
            const response = await fetch('/api/v1/bot-admin/status');
            if (!response.ok) {
                throw new Error('Server-Fehler beim Abrufen des Status');
            }
            
            const data = await response.json();
            this.renderStatusContent(data);
        } catch (error) {
            console.error('Fehler beim Aktualisieren des Status:', error);
            WidgetUI.helpers.showError(this.contentArea, 'Konnte Status nicht laden.');
        }
    },
    
    renderStatusContent: function(data) {
        this.contentArea.innerHTML = `
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-label">Status</div>
                    <div class="status-value ${data.connected ? 'text-success' : 'text-danger'}">
                        ${data.connected ? 'Online' : 'Offline'}
                    </div>
                </div>
                <div class="status-item">
                    <div class="status-label">Laufzeit</div>
                    <div class="status-value">${data.uptime || 'Nicht verfügbar'}</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Server</div>
                    <div class="status-value">${data.server_count || 0}</div>
                </div>
            </div>
        `;
    },
    
    startRefreshTimer: function() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        this.refreshTimer = setInterval(() => {
            this.refresh();
        }, this.refreshInterval);
    },
    
    destroy: function() {
        // Timer stoppen beim Entfernen des Widgets
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
    }
}); 