document.addEventListener('DOMContentLoaded', function() {
    // Format date helper function
    function formatDate(isoString) {
        if (!isoString) return 'Never';
        
        try {
            const date = new Date(isoString);
            if (isNaN(date.getTime())) return 'Invalid Date';
            
            return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
        } catch (e) {
            console.error('Error formatting date:', e);
            return 'Invalid Date';
        }
    }

    // Initialize components
    const searchInput = document.querySelector('#user-search');
    const roleFilter = document.querySelector('#role-filter');
    const appRoleSelects = document.querySelectorAll('.app-role-select');
    const statusButtons = document.querySelectorAll('.toggle-status');
    
    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#users-table-body tr');
            
            rows.forEach(row => {
                const username = row.querySelector('.username').textContent.toLowerCase();
                const discordId = row.querySelector('.discord-id').textContent.toLowerCase();
                
                const matches = username.includes(searchTerm) || discordId.includes(searchTerm);
                row.style.display = matches ? '' : 'none';
            });
        }, 300));
    }
    
    // Role filter functionality
    if (roleFilter) {
        roleFilter.addEventListener('change', function(e) {
            const selectedRole = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#users-table-body tr');
            
            rows.forEach(row => {
                if (!selectedRole) {
                    row.style.display = '';
                    return;
                }
                
                const userRole = row.querySelector('.server-role .role-badge').textContent.toLowerCase();
                row.style.display = userRole === selectedRole ? '' : 'none';
            });
        });
    }
    
    // App role update functionality
    appRoleSelects.forEach(select => {
        select.addEventListener('change', async function(e) {
            const userId = this.dataset.userId;
            const newRole = this.value;
            
            try {
                const response = await fetch(`/api/v1/admin/users/${userId}/role`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ role: newRole })
                });
                
                if (!response.ok) throw new Error('Failed to update role');
                
                showToast('Role updated successfully', 'success');
            } catch (error) {
                console.error('Error updating role:', error);
                showToast('Failed to update role', 'error');
                // Reset select to previous value
                this.value = this.dataset.originalRole;
            }
        });
    });
    
    // Status toggle functionality
    statusButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const userId = this.dataset.userId;
            const currentStatus = this.dataset.status === 'true';
            const newStatus = !currentStatus;
            
            try {
                const response = await fetch(`/api/v1/admin/users/${userId}/status`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ verified: newStatus })
                });
                
                if (!response.ok) throw new Error('Failed to update status');
                
                // Update button state
                this.dataset.status = String(newStatus);
                this.classList.toggle('btn-success');
                this.classList.toggle('btn-danger');
                this.querySelector('i').classList.toggle('bi-check-circle');
                this.querySelector('i').classList.toggle('bi-x-circle');
                this.textContent = newStatus ? 'Verified' : 'Unverified';
                
                showToast('Status updated successfully', 'success');
            } catch (error) {
                console.error('Error updating status:', error);
                showToast('Failed to update status', 'error');
            }
        });
    });
    
    // Helper Functions
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Trigger reflow
        toast.offsetHeight;
        
        // Add show class
        toast.classList.add('show');
        
        // Remove after animation
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    // View user details
    window.viewUser = async function(userId) {
        try {
            const response = await fetch(`/api/v1/admin/users/${userId}`);
            if (!response.ok) throw new Error('Failed to fetch user details');
            
            const userData = await response.json();
            const modal = document.getElementById('userViewModal');
            const content = document.getElementById('userViewContent');
            
            content.innerHTML = `
                <div class="user-details">
                    <div class="user-header">
                        <img src="${userData.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png'}" 
                             alt="" class="user-avatar">
                        <h3>${userData.username}</h3>
                        <span class="discord-id">Discord ID: ${userData.discord_id}</span>
                    </div>
                    <div class="user-info-grid">
                        <div class="info-item">
                            <label>App Role:</label>
                            <span>${userData.app_role}</span>
                        </div>
                        <div class="info-item">
                            <label>Guild Role:</label>
                            <span>${userData.guild_role}</span>
                        </div>
                        <div class="info-item">
                            <label>Status:</label>
                            <span class="status-badge ${userData.is_active ? 'active' : 'inactive'}">
                                ${userData.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                        <div class="info-item">
                            <label>Joined Server:</label>
                            <span>${formatDate(userData.joined_at)}</span>
                        </div>
                        <div class="info-item">
                            <label>Last Active:</label>
                            <span>${formatDate(userData.last_active)}</span>
                        </div>
                    </div>
                </div>
            `;
            
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
        } catch (error) {
            console.error('Error fetching user details:', error);
            showToast('Failed to load user details', 'error');
        }
    };
});

