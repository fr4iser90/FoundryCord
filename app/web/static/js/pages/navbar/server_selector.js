class ServerSelector {
    constructor() {
        this.dropdown = document.querySelector('.server-selector');
        this.currentServer = null;
        this.init();
    }

    init() {
        // Initialize event listeners
        if (this.dropdown) {
            this.dropdown.addEventListener('click', (e) => {
                const item = e.target.closest('.dropdown-item');
                if (item) {
                    e.preventDefault();
                    const serverId = item.dataset.serverId;
                    this.switchServer(serverId);
                }
            });

            // Load initial server data
            this.loadServerData();
        } else {
            console.error('Server selector dropdown not found');
        }
    }

    async loadServerData() {
        try {
            // Verwende die korrekte API-Route
            const response = await fetch('/api/servers/list');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const servers = await response.json();
            console.log('Loaded servers:', servers);
            this.updateServerList(servers);
        } catch (error) {
            console.error('Error loading server data:', error);
        }
    }

    async switchServer(serverId) {
        try {
            const response = await fetch(`/api/servers/switch/${serverId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            if (result.success) {
                // Reload the page to reflect the new server
                window.location.reload();
            }
        } catch (error) {
            console.error('Error switching server:', error);
        }
    }

    updateServerList(servers) {
        if (!this.dropdown) return;
        
        const serverList = this.dropdown.querySelector('.dropdown-menu');
        if (!serverList) {
            console.error('Server list dropdown menu not found');
            return;
        }
        
        if (servers.length === 0) {
            serverList.innerHTML = '<li><span class="dropdown-item disabled">No servers available</span></li>';
            return;
        }
        
        serverList.innerHTML = servers.map(server => `
            <li>
                <a class="dropdown-item" href="#" data-server-id="${server.id}">
                    <img src="${server.icon_url}" 
                         alt="${server.name}" 
                         class="server-icon rounded-circle"
                         width="24" 
                         height="24">
                    <div class="d-flex flex-column">
                        <span class="server-name">${server.name}</span>
                        <small class="server-id text-muted">${server.id}</small>
                    </div>
                </a>
            </li>
        `).join('');
        
        // Set the first server as current if none is selected
        if (servers.length > 0 && !this.currentServer) {
            this.updateCurrentServer(servers[0]);
        }
    }

    updateCurrentServer(server) {
        this.currentServer = server;
        const button = this.dropdown.querySelector('.btn');
        if (button) {
            button.innerHTML = `
                <img src="${server.icon_url}" 
                     alt="Server Icon" 
                     class="server-icon rounded-circle"
                     width="32" 
                     height="32">
                <div class="d-flex flex-column align-items-start">
                    <span class="server-name">${server.name}</span>
                    <small class="server-id text-muted">${server.id}</small>
                </div>
            `;
        }
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    new ServerSelector();
});
