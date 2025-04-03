document.addEventListener('DOMContentLoaded', function() {
    // Initialize server selector and role displays
    const serverSelector = document.getElementById('server-selector');
    const roleColumnHeader = document.getElementById('role-column-header');
    const userRows = document.querySelectorAll('.user-row');
    
    // Track current view state
    let currentView = {
        server: 'all',
        searchTerm: ''
    };
    
    // Initialize search functionality
    const searchInput = document.getElementById('user-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // Server selection handler
    if (serverSelector) {
        serverSelector.addEventListener('change', function() {
            currentView.server = this.value;
            updateRoleDisplay();
            filterUsers(this.value);
        });
    }
    
    // Role change handlers
    document.querySelectorAll('.role-select').forEach(select => {
        select.addEventListener('change', handleRoleChange);
        // Store original value for rollback if update fails
        select.dataset.originalValue = select.value;
    });
    
    // App Role Change Handler
    document.querySelectorAll('.app-role-select').forEach(select => {
        select.addEventListener('change', handleAppRoleChange);
        select.dataset.originalValue = select.value;
    });
    
    function updateRoleDisplay() {
        const isSystemView = currentView.server === 'all';
        
        // Update column header
        if (roleColumnHeader) {
            roleColumnHeader.textContent = isSystemView ? 'System Role' : 'Server Role';
        }
        
        // Toggle role display sections
        document.querySelectorAll('.system-role-display').forEach(el => {
            el.style.display = isSystemView ? 'block' : 'none';
        });
        
        document.querySelectorAll('.server-role-display').forEach(el => {
            el.style.display = isSystemView ? 'none' : 'block';
        });
        
        // Update actual role displays
        if (!isSystemView) {
            updateServerRoles(currentView.server);
        }
    }
    
    async function updateServerRoles(serverId) {
        try {
            const response = await fetch(`/api/v1/servers/${serverId}/roles`);
            if (!response.ok) throw new Error('Failed to fetch server roles');
            
            const roles = await response.json();
            
            // Update role displays with actual server roles
            userRows.forEach(row => {
                const userId = row.dataset.userId;
                const userRole = roles.find(r => r.user_id === userId);
                
                const roleDisplay = row.querySelector('.server-role-display select');
                if (roleDisplay && userRole) {
                    roleDisplay.value = userRole.role;
                    roleDisplay.dataset.originalValue = userRole.role;
                }
            });
        } catch (error) {
            console.error('Error fetching server roles:', error);
            showNotification('Failed to load server roles', 'error');
        }
    }
    
    async function handleRoleChange(event) {
        const select = event.target;
        const userId = select.dataset.userId;
        const newRole = select.value;
        const roleType = select.dataset.type;
        const serverId = currentView.server;
        
        try {
            const endpoint = roleType === 'system' 
                ? `/api/v1/admin/users/${userId}/role`
                : `/api/v1/servers/${serverId}/users/${userId}/role`;
                
            const response = await fetch(endpoint, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    role: newRole,
                    server_id: roleType === 'server' ? serverId : undefined
                })
            });
            
            if (!response.ok) throw new Error('Failed to update role');
            
            showNotification('Role updated successfully', 'success');
            select.dataset.originalValue = newRole;
        } catch (error) {
            console.error('Error updating role:', error);
            showNotification('Failed to update role', 'error');
            // Rollback to original value
            select.value = select.dataset.originalValue;
        }
    }
    
    async function handleAppRoleChange(event) {
        const select = event.target;
        const userId = select.dataset.userId;
        const newRole = select.value;

        try {
            const response = await fetch(`/api/v1/admin/users/${userId}/role`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    role: newRole
                })
            });

            if (!response.ok) throw new Error('Failed to update role');

            showNotification('App role updated successfully', 'success');
            select.dataset.originalValue = newRole;

        } catch (error) {
            console.error('Error updating app role:', error);
            showNotification('Failed to update app role', 'error');
            select.value = select.dataset.originalValue;
        }
    }
    
    async function updateUserGuildRoles(userId) {
        try {
            const response = await fetch(`/api/v1/admin/users/${userId}/guild-roles`);
            if (!response.ok) throw new Error('Failed to fetch guild roles');

            const guildRoles = await response.json();
            const userRow = document.querySelector(`tr[data-user-id="${userId}"]`);
            if (!userRow) return;

            const guildRolesCell = userRow.querySelector('.guild-roles');
            if (!guildRolesCell) return;

            // Aktualisiere die Guild-Roles-Anzeige
            guildRolesCell.innerHTML = guildRoles.guilds.map(guild => `
                <div class="guild-role-item">
                    <span class="guild-name">${guild.name}:</span>
                    <span class="guild-role-badges">
                        ${guild.roles.map(role => `
                            <span class="badge bg-discord-role" style="background-color: ${role.color || '#99AAB5'}">
                                ${role.name}
                            </span>
                        `).join('')}
                    </span>
                </div>
            `).join('');

        } catch (error) {
            console.error('Error updating guild roles:', error);
        }
    }
    
    function filterUsers(serverId) {
        const rows = document.querySelectorAll('.user-row');
        
        rows.forEach(row => {
            const serverIds = row.dataset.serverIds ? row.dataset.serverIds.split(',') : [];
            if (serverId === 'all' || serverIds.includes(serverId)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    function handleSearch(event) {
        const searchTerm = event.target.value.toLowerCase();
        
        document.querySelectorAll('.user-row').forEach(row => {
            const username = row.querySelector('.username').textContent.toLowerCase();
            const discordId = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            
            if (username.includes(searchTerm) || discordId.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    function updateUserTable(users) {
        const tbody = document.querySelector('#users-table-body');
        if (!tbody || !users.length) return;
        
        // Update existing rows or add new ones
        users.forEach(user => {
            let row = tbody.querySelector(`tr[data-user-id="${user.id}"]`);
            if (!row) {
                row = createUserRow(user);
                tbody.appendChild(row);
            } else {
                updateUserRow(row, user);
            }
        });
    }
    
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
    
    function showNotification(message, type) {
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, type);
        } else {
            alert(message);
        }
    }
    
    // Initial setup
    updateRoleDisplay();
    filterUsers(currentView.server);
});
