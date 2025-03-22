
document.addEventListener('DOMContentLoaded', function() {
    // Load initial status
    refreshBotStatus();
    
    // Setup refresh interval
    setInterval(refreshBotStatus, 10000); // Refresh every 10 seconds
    
    // Button handlers
    document.getElementById('btn-start-bot').addEventListener('click', startBot);
    document.getElementById('btn-stop-bot').addEventListener('click', stopBot);
    document.getElementById('btn-restart-bot').addEventListener('click', restartBot);
});

function refreshBotStatus() {
    fetch('/api/v1/bot-admin/status')
        .then(response => response.json())
        .then(data => {
            // Update status elements
            document.getElementById('bot-status').innerText = 
                data.connected ? 'Connected' : 'Disconnected';
            
            document.getElementById('bot-uptime').innerText = 
                data.uptime || 'Not running';
                
            // Update workflow table
            const workflowList = document.getElementById('workflow-list');
            workflowList.innerHTML = '';
            
            data.available_workflows.forEach(workflow => {
                const isActive = data.active_workflows.includes(workflow);
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${workflow}</td>
                    <td>
                        <span class="badge badge-${isActive ? 'success' : 'secondary'}">
                            ${isActive ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm ${isActive ? 'btn-danger' : 'btn-success'}" 
                                onclick="${isActive ? 'disableWorkflow' : 'enableWorkflow'}('${workflow}')">
                            ${isActive ? 'Disable' : 'Enable'}
                        </button>
                    </td>
                `;
                workflowList.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching bot status:', error);
        });
}

function startBot() {
    if (confirm('Are you sure you want to start the bot?')) {
        fetch('/api/v1/bot-admin/start', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            setTimeout(refreshBotStatus, 2000);
        })
        .catch(error => {
            console.error('Error starting bot:', error);
            alert('Failed to start bot');
        });
    }
}

function stopBot() {
    if (confirm('Are you sure you want to stop the bot?')) {
        fetch('/api/v1/bot-admin/stop', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            setTimeout(refreshBotStatus, 2000);
        })
        .catch(error => {
            console.error('Error stopping bot:', error);
            alert('Failed to stop bot');
        });
    }
}

function restartBot() {
    if (confirm('Are you sure you want to restart the bot?')) {
        fetch('/api/v1/bot-admin/restart', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            setTimeout(refreshBotStatus, 5000);
        })
        .catch(error => {
            console.error('Error restarting bot:', error);
            alert('Failed to restart bot');
        });
    }
}

function enableWorkflow(workflowName) {
    fetch(`/api/v1/bot-admin/workflow/${workflowName}/enable`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        refreshBotStatus();
    })
    .catch(error => {
        console.error(`Error enabling workflow ${workflowName}:`, error);
        alert(`Failed to enable workflow ${workflowName}`);
    });
}

function disableWorkflow(workflowName) {
    fetch(`/api/v1/bot-admin/workflow/${workflowName}/disable`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        refreshBotStatus();
    })
    .catch(error => {
        console.error(`Error disabling workflow ${workflowName}:`, error);
        alert(`Failed to disable workflow ${workflowName}`);
    });
}
