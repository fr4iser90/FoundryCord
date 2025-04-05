document.addEventListener('DOMContentLoaded', function() {
    const serverSelector = document.querySelector('.server-selector');
    if (!serverSelector) return;

    // Get server list and populate dropdown
    async function loadServers() {
        try {
            const response = await fetch('/api/servers/list');
            if (!response.ok) throw new Error('Failed to load servers');
            
            const servers = await response.json();
            updateServerList(servers);
        } catch (error) {
            console.error('Error loading servers:', error);
        }
    }

    // Update server list in dropdown
    function updateServerList(servers) {
        const serverList = document.querySelector('.server-list');
        if (!serverList) return;

        serverList.innerHTML = servers.map(server => `
            <div class="server-item" data-server-id="${server.id}">
                <img src="${server.icon_url || 'https://cdn.discordapp.com/embed/avatars/0.png'}" alt="${server.name}" class="server-icon">
                <span class="server-name">${server.name}</span>
                <span class="member-count">${server.member_count || 0} members</span>
            </div>
        `).join('');

        // Add click handlers
        document.querySelectorAll('.server-item').forEach(item => {
            item.addEventListener('click', () => switchServer(item.dataset.serverId));
        });
    }

    // Switch active server
    async function switchServer(serverId) {
        try {
            const response = await fetch(`/api/servers/switch/${serverId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('Failed to switch server');
            
            const result = await response.json();
            if (result.success) {
                // Update UI to reflect active_guild change
                const serverButton = document.querySelector('#server-selector-button');
                if (serverButton) {
                    serverButton.innerHTML = `
                        <img src="${result.server.icon_url}" alt="${result.server.name}" class="server-icon">
                        <span>${result.server.name}</span>
                    `;
                }
                // Reload page to update context
                window.location.reload();
            }
        } catch (error) {
            console.error('Error switching server:', error);
        }
    }

    // Initial load
    loadServers();

    // Toggle dropdown
    const currentServer = document.querySelector('.current-server');
    if (currentServer) {
        currentServer.addEventListener('click', function() {
            serverSelector.classList.toggle('active');
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (!serverSelector.contains(event.target)) {
            serverSelector.classList.remove('active');
        }
    });
}); 