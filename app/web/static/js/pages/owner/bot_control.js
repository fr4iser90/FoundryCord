// Bot Control Functions
async function startBot() {
    try {
        const response = await fetch('/api/v1/bot-admin/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        if (response.ok) {
            showToast('success', 'Bot started successfully');
        } else {
            showToast('error', data.detail || 'Failed to start bot');
        }
    } catch (error) {
        console.error('Error starting bot:', error);
        showToast('error', 'Failed to start bot');
    }
}

async function stopBot() {
    try {
        const response = await fetch('/api/v1/bot-admin/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        if (response.ok) {
            showToast('success', 'Bot stopped successfully');
        } else {
            showToast('error', data.detail || 'Failed to stop bot');
        }
    } catch (error) {
        console.error('Error stopping bot:', error);
        showToast('error', 'Failed to stop bot');
    }
}

async function restartBot() {
    try {
        const response = await fetch('/api/v1/bot-admin/restart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        if (response.ok) {
            showToast('success', 'Bot restarted successfully');
        } else {
            showToast('error', data.detail || 'Failed to restart bot');
        }
    } catch (error) {
        console.error('Error restarting bot:', error);
        showToast('error', 'Failed to restart bot');
    }
}

// Server Management Functions
async function addServer() {
    const form = document.getElementById('addServerForm');
    const formData = new FormData(form);
    const serverData = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/v1/owner/servers/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(serverData)
        });
        
        const data = await response.json();
        if (response.ok) {
            showToast('success', 'Server added successfully');
            // Close modal and refresh page
            const modal = bootstrap.Modal.getInstance(document.getElementById('addServerModal'));
            modal.hide();
            window.location.reload();
        } else {
            showToast('error', data.detail || 'Failed to add server');
        }
    } catch (error) {
        console.error('Error adding server:', error);
        showToast('error', 'Failed to add server');
    }
}

async function removeServer(guildId) {
    if (!confirm('Are you sure you want to remove this server?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/v1/owner/servers/${guildId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        if (response.ok) {
            showToast('success', 'Server removed successfully');
            window.location.reload();
        } else {
            showToast('error', data.detail || 'Failed to remove server');
        }
    } catch (error) {
        console.error('Error removing server:', error);
        showToast('error', 'Failed to remove server');
    }
}

// Bot Configuration Functions
document.getElementById('botConfigForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const configData = Object.fromEntries(formData.entries());
    
    // Convert checkbox value to boolean
    configData.auto_reconnect = formData.get('auto_reconnect') === 'on';
    
    try {
        const response = await fetch('/api/v1/owner/bot/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configData)
        });
        
        const data = await response.json();
        if (response.ok) {
            showToast('success', 'Configuration saved successfully');
        } else {
            showToast('error', data.detail || 'Failed to save configuration');
        }
    } catch (error) {
        console.error('Error saving configuration:', error);
        showToast('error', 'Failed to save configuration');
    }
});

// Helper Functions
function showToast(type, message) {
    // Assuming you have a toast notification system
    // You can implement this based on your UI framework
    console.log(`${type}: ${message}`);
    // Example implementation with Bootstrap toast
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        document.body.removeChild(toast);
    });
} 