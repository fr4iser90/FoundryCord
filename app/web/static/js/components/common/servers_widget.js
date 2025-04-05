/**
 * Servers Widget - Zeigt Informationen über verbundene Discord-Server an
 */

// Widget definieren
WidgetUI.registerWidget('serversWidget', {
    init: function(config) {
        this.config = config;
        this.refreshInterval = config.options?.refreshInterval || 60000; // 1 Minute Standard
        this.maxServers = config.options?.maxServers || 5; // Wie viele Server angezeigt werden sollen
        this.showControls = config.options?.showControls || false;
        this.refreshTimer = null;
        this.servers = [];
    },
    
    render: function() {
        const { container } = this.config;
        
        // Widget-Struktur erstellen
        const widget = WidgetUI.helpers.createWidgetFrame('Discord Servers');
        container.appendChild(widget.frame);
        
        // Content-Bereich für Updates speichern
        this.contentArea = widget.content;
        
        // Lade-Indikator anzeigen
        this.contentArea.innerHTML = `
            <div class="d-flex justify-content-center my-3">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        // Initiale Daten laden
        this.refresh();
        
        // Regelmäßiges Aktualisieren starten
        this.startRefreshTimer();
        
        // Steuerungselemente anzeigen wenn gewünscht
        if (this.showControls) {
            const controlsContainer = document.createElement('div');
            controlsContainer.className = 'mt-3 text-center';
            controlsContainer.innerHTML = `
                <button class="btn btn-sm btn-primary refresh-servers-btn">
                    <i class="bi bi-arrow-clockwise"></i> Aktualisieren
                </button>
            `;
            
            widget.footer.appendChild(controlsContainer);
            
            // Event-Listener für den Aktualisierungsbutton
            const refreshBtn = controlsContainer.querySelector('.refresh-servers-btn');
            refreshBtn.addEventListener('click', () => this.refresh());
        }
    },
    
    refresh: async function() {
        try {
            const response = await fetch('/api/v1/bot-public-info/servers');
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            this.servers = data.servers || [];
            this.renderServers();
        } catch (error) {
            console.error('Error fetching server data:', error);
            this.contentArea.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    Fehler beim Laden der Serverinformationen.
                </div>
            `;
        }
    },
    
    renderServers: function() {
        if (!this.servers || this.servers.length === 0) {
            this.contentArea.innerHTML = `
                <div class="alert alert-info my-3" role="alert">
                    <i class="bi bi-info-circle-fill me-2"></i>
                    Keine Server verbunden
                </div>
            `;
            return;
        }
        
        // Auf maxServers begrenzen
        const serversToShow = this.servers.slice(0, this.maxServers);
        
        // HTML für Serverliste erstellen
        let html = `
            <div class="list-group server-list">
        `;
        
        serversToShow.forEach(server => {
            const memberText = server.member_count === 1 
                ? '1 Mitglied' 
                : `${server.member_count} Mitglieder`;
            
            html += `
                <div class="list-group-item d-flex justify-content-between align-items-center server-item">
                    <div class="server-info">
                        <h6 class="mb-0">${server.name}</h6>
                        <small class="text-muted">${memberText}</small>
                    </div>
                    <span class="badge ${server.is_active ? 'bg-success' : 'bg-secondary'} rounded-pill">
                        ${server.is_active ? 'Online' : 'Offline'}
                    </span>
                </div>
            `;
        });
        
        // "Mehr anzeigen" Link wenn es mehr Server gibt
        if (this.servers.length > this.maxServers) {
            const moreCount = this.servers.length - this.maxServers;
            html += `
                <div class="list-group-item text-center">
                    <a href="/bot/servers" class="text-primary">
                        ${moreCount} weitere Server anzeigen...
                    </a>
                </div>
            `;
        }
        
        html += `</div>`;
        
        // Letzter Update-Zeitstempel
        const now = new Date();
        const timeStr = now.toLocaleTimeString();
        
        html += `
            <div class="text-end mt-2">
                <small class="text-muted">Aktualisiert: ${timeStr}</small>
            </div>
        `;
        
        this.contentArea.innerHTML = html;
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