class ServerSelector {
    constructor() {
        this.dropdown = document.querySelector('.server-selector');
        this.button = this.dropdown?.querySelector('.server-select-btn');
        this.currentServer = null;
        this.init();
    }

    init() {
        if (!this.dropdown) {
            console.error('Server selector dropdown not found');
            return;
        }

        // Initialize event listeners
        this.dropdown.addEventListener('click', (e) => {
            const item = e.target.closest('.dropdown-item');
            if (item) {
                e.preventDefault();
                const serverId = item.getAttribute('href').split('/').pop();
                this.switchServer(serverId);
            }
        });

        // Load initial server data
        this.loadServerData();
    }

    async loadServerData() {
        try {
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
                <a class="dropdown-item" href="/switch-server/${server.id}">
                    <img src="${server.icon_url || '/static/img/default_server_icon.png'}" 
                         alt="${server.name}" 
                         class="server-icon"
                         width="24" 
                         height="24">
                    <div class="server-info">
                        <span class="server-name">${server.name}</span>
                        <small class="server-id">${server.id}</small>
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
        if (!this.button) return;

        this.button.innerHTML = `
            <img src="${server.icon_url || '/static/img/default_server_icon.png'}" 
                 alt="Server Icon" 
                 class="server-icon"
                 width="32" 
                 height="32">
            <div class="server-info">
                <span class="server-name">${server.name}</span>
                <small class="server-id">${server.id}</small>
            </div>
        `;
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    new ServerSelector();
});
