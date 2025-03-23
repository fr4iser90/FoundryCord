// Server CRUD Control Module
const ServerCrudControl = (function() {
    // Private variables
    let serverTable;
    let serverForm;
    
    // Private functions
    function initServerTable() {
        serverTable = document.getElementById('server-table');
        if (serverTable) {
            loadServers();
        }
    }
    
    function initServerForm() {
        serverForm = document.getElementById('server-form');
        if (serverForm) {
            serverForm.addEventListener('submit', handleServerSubmit);
        }
    }
    
    async function loadServers() {
        try {
            const response = await fetch('/api/v1/bot-admin/servers');
            const servers = await response.json();
            
            renderServerTable(servers);
        } catch (error) {
            console.error('Error loading servers:', error);
            showNotification('Failed to load servers', 'error');
        }
    }
    
    function renderServerTable(servers) {
        const tableBody = serverTable.querySelector('tbody');
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        servers.forEach(server => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${server.name}</td>
                <td>${server.guild_id}</td>
                <td>${server.member_count || 0}</td>
                <td>${server.is_active ? 'Active' : 'Inactive'}</td>
                <td>
                    <button class="btn btn-sm btn-primary edit-server" data-id="${server.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger delete-server" data-id="${server.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Add event listeners to the buttons
        tableBody.querySelectorAll('.edit-server').forEach(button => {
            button.addEventListener('click', function() {
                editServer(this.dataset.id);
            });
        });
        
        tableBody.querySelectorAll('.delete-server').forEach(button => {
            button.addEventListener('click', function() {
                deleteServer(this.dataset.id);
            });
        });
    }
    
    async function handleServerSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(serverForm);
        const serverData = Object.fromEntries(formData.entries());
        
        try {
            const method = serverData.id ? 'PUT' : 'POST';
            const url = serverData.id 
                ? `/api/v1/bot-admin/servers/${serverData.id}` 
                : '/api/v1/bot-admin/servers';
            
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(serverData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showNotification(
                    serverData.id ? 'Server updated successfully' : 'Server added successfully', 
                    'success'
                );
                
                // Reset form and reload servers
                serverForm.reset();
                loadServers();
            } else {
                showNotification(`Error: ${result.detail || 'Operation failed'}`, 'error');
            }
        } catch (error) {
            console.error('Error saving server:', error);
            showNotification('Failed to communicate with server', 'error');
        }
    }
    
    async function editServer(id) {
        try {
            const response = await fetch(`/api/v1/bot-admin/servers/${id}`);
            const server = await response.json();
            
            // Fill the form with server data
            Object.keys(server).forEach(key => {
                const input = serverForm.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = server[key];
                }
            });
            
            // Scroll to the form
            serverForm.scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error(`Error fetching server ${id}:`, error);
            showNotification('Failed to load server details', 'error');
        }
    }
    
    async function deleteServer(id) {
        if (!confirm('Are you sure you want to delete this server?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/v1/bot-admin/servers/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showNotification('Server deleted successfully', 'success');
                loadServers();
            } else {
                const result = await response.json();
                showNotification(`Error: ${result.detail || 'Failed to delete server'}`, 'error');
            }
        } catch (error) {
            console.error(`Error deleting server ${id}:`, error);
            showNotification('Failed to communicate with server', 'error');
        }
    }
    
    function showNotification(message, type) {
        // Use the global notification function
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, type);
        } else {
            console.log(`[${type}] ${message}`);
        }
    }
    
    // Public API
    return {
        init: function() {
            console.log('Initializing Server CRUD Control');
            initServerTable();
            initServerForm();
        }
    };
})();
