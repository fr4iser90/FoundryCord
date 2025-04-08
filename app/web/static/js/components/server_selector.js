// Server Selector Component
class ServerSelector {
    constructor() {
        console.log('Initializing ServerSelector');
        // Bind methods to this instance
        this.loadServers = this.loadServers.bind(this);
        this.updateServerList = this.updateServerList.bind(this);
        this.switchServer = this.switchServer.bind(this);
        this.setupEventListeners = this.setupEventListeners.bind(this);
        
        this.button = document.getElementById('server-selector-button');
        this.dropdown = document.getElementById('server-dropdown');
        this.serverList = this.dropdown?.querySelector('.server-list');
        
        if (this.button && this.dropdown && this.serverList) {
            console.log('Found all required elements');
            this.setupEventListeners();
            this.loadServers();
        } else {
            console.error('Missing required elements:', {
                button: !!this.button,
                dropdown: !!this.dropdown,
                serverList: !!this.serverList
            });
        }
    }

    setupEventListeners() {
        // Toggle dropdown on button click
        this.button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Toggle dropdown');
            this.dropdown.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (event) => {
            if (!this.button.contains(event.target) && !this.dropdown.contains(event.target)) {
                this.dropdown.classList.remove('show');
            }
        });
    }

    async loadServers() {
        try {
            console.log('Loading servers...');
            this.serverList.classList.add('loading');
            
            const response = await fetch('/api/v1/servers', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const servers = await response.json();
            console.log('Servers loaded:', servers);
            
            // Filter for approved servers only
            const approvedServers = servers.filter(server => {
                console.log('Checking server:', server);
                return server && server.access_status && 
                       server.access_status.toLowerCase() === 'approved';
            });
            
            this.serverList.classList.remove('loading');
            if (approvedServers.length === 0) {
                this.serverList.classList.add('empty');
                this.serverList.innerHTML = '<div class="server-list-item">No approved servers available</div>';
                return;
            }
            
            this.updateServerList(approvedServers);
        } catch (error) {
            console.error('Error loading servers:', error);
            this.serverList.classList.remove('loading');
            this.serverList.innerHTML = '<div class="server-list-item">Error loading servers</div>';
        }
    }

    updateServerList(servers) {
        console.log('Updating server list with:', servers);
        this.serverList.innerHTML = '';
        
        if (!Array.isArray(servers) || servers.length === 0) {
            this.serverList.classList.add('empty');
            this.serverList.innerHTML = '<div class="server-list-item">No servers available</div>';
            return;
        }

        this.serverList.classList.remove('empty');
        servers.forEach(server => {
            const serverItem = document.createElement('div');
            serverItem.className = 'server-list-item';
            serverItem.innerHTML = `
                <img src="${server.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" 
                     alt="${server.name}" 
                     class="server-icon">
                <div class="server-info">
                    <div class="server-name">${server.name}</div>
                    <div class="server-id">${server.guild_id}</div>
                </div>
            `;
            
            // Use bound method for click handler
            serverItem.addEventListener('click', this.switchServer.bind(this, server));
            this.serverList.appendChild(serverItem);
        });
    }

    async switchServer(server, event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        try {
            console.log('Switching to server:', server);
            const response = await fetch(`/api/v1/servers/select/${server.guild_id}`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Switch server response:', result);

            // Update UI
            if (this.button.querySelector('img')) {
                this.button.querySelector('img').src = server.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png';
            }
            if (this.button.querySelector('span')) {
                this.button.querySelector('span').textContent = server.name;
            }
            this.dropdown.classList.remove('show');

            // Reload page to update content
            window.location.reload();
        } catch (error) {
            console.error('Error switching server:', error);
            alert('Failed to switch server. Please try again.');
        }
    }
}

// Initialize when DOM is loaded
if (!window.serverSelector) {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM loaded, initializing ServerSelector');
        window.serverSelector = new ServerSelector();
    });
} 