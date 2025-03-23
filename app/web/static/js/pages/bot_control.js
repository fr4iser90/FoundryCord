// Hauptmodul für die Bot-Kontrolle
document.addEventListener('DOMContentLoaded', function() {
    // Stelle sicher, dass sowohl die Widget-UI als auch die CRUD-Module initialisiert werden
    console.log('Bot Control page loaded');
    
    // Lade Widget-UI wenn verfügbar
    if (typeof WidgetUI !== 'undefined') {
        // Status-Widget
        const statusContainer = document.getElementById('bot-status-widget');
        if (statusContainer) {
            WidgetUI.loadWidget('statusWidget', statusContainer, {
                refreshInterval: 10000
            });
        }
        
        // Server-Widget
        const serversContainer = document.getElementById('servers-widget');
        if (serversContainer) {
            WidgetUI.loadWidget('serversWidget', serversContainer, {
                refreshInterval: 30000,
                maxServers: 5,
                showControls: true
            });
        }
    } else {
        console.error('WidgetUI nicht gefunden!');
    }
    
    // Lade alle CRUD-Module
    loadCrudModules();
    
    // Event-Listener für die Bot-Steuerungsknöpfe
    bindBotControlButtons();
    
    // Initialisiere die Workflow-Tabelle
    initWorkflowTable();
    
    // Starte regelmäßige Status-Updates
    startStatusUpdates();
});

// Lädt alle CRUD-Module (Tabs, Inhalte)
function loadCrudModules() {
    // Auf CRUD-Module zugreifen
    if (typeof BotCrudControl !== 'undefined') BotCrudControl.init();
    if (typeof CategoryCrudControl !== 'undefined') CategoryCrudControl.init();
    if (typeof ChannelCrudControl !== 'undefined') ChannelCrudControl.init();
    if (typeof ServerCrudControl !== 'undefined') ServerCrudControl.init();
}

// Event-Listener für die Steuerungsknöpfe
function bindBotControlButtons() {
    // Start-Button
    document.getElementById('btn-start-bot').addEventListener('click', function() {
        startBot();
    });
    
    // Stop-Button
    document.getElementById('btn-stop-bot').addEventListener('click', function() {
        stopBot();
    });
    
    // Restart-Button
    document.getElementById('btn-restart-bot').addEventListener('click', function() {
        restartBot();
    });
}

// Initialisiert die Workflow-Tabelle
function initWorkflowTable() {
    fetchWorkflows().then(data => {
        renderWorkflowTable(data);
    });
}

// Bot-Steuerungsfunktionen
async function startBot() {
    try {
        const response = await fetch('/api/v1/bot-admin/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        showNotification(data.message, 'success');
        
        // Status aktualisieren
        updateBotStatus();
    } catch (error) {
        console.error('Error starting bot:', error);
        showNotification('Failed to start bot', 'error');
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
        showNotification(data.message, 'success');
        
        // Status aktualisieren
        updateBotStatus();
    } catch (error) {
        console.error('Error stopping bot:', error);
        showNotification('Failed to stop bot', 'error');
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
        showNotification(data.message, 'success');
        
        // Status aktualisieren
        updateBotStatus();
    } catch (error) {
        console.error('Error restarting bot:', error);
        showNotification('Failed to restart bot', 'error');
    }
}

// Workflow-Steuerungsfunktionen
async function fetchWorkflows() {
    try {
        const response = await fetch('/api/v1/bot-admin/status');
        const data = await response.json();
        return data.available_workflows || [];
    } catch (error) {
        console.error('Error fetching workflows:', error);
        return [];
    }
}

function renderWorkflowTable(workflows) {
    const tableBody = document.getElementById('workflow-list');
    tableBody.innerHTML = '';
    
    workflows.forEach(workflow => {
        const row = document.createElement('tr');
        
        // Name
        const nameCell = document.createElement('td');
        nameCell.textContent = workflow;
        
        // Status (placeholder)
        const statusCell = document.createElement('td');
        statusCell.innerHTML = '<span class="badge badge-secondary">Inactive</span>';
        
        // Actions
        const actionsCell = document.createElement('td');
        actionsCell.innerHTML = `
            <button class="btn btn-sm btn-success workflow-enable" data-workflow="${workflow}">
                <i class="fas fa-check"></i> Enable
            </button>
            <button class="btn btn-sm btn-danger workflow-disable" data-workflow="${workflow}">
                <i class="fas fa-times"></i> Disable
            </button>
        `;
        
        row.appendChild(nameCell);
        row.appendChild(statusCell);
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    });
    
    // Event-Listener für Workflow-Buttons
    document.querySelectorAll('.workflow-enable').forEach(button => {
        button.addEventListener('click', function() {
            enableWorkflow(this.dataset.workflow);
        });
    });
    
    document.querySelectorAll('.workflow-disable').forEach(button => {
        button.addEventListener('click', function() {
            disableWorkflow(this.dataset.workflow);
        });
    });
}

async function enableWorkflow(workflow) {
    try {
        const response = await fetch(`/api/v1/bot-admin/workflow/${workflow}/enable`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        showNotification(data.message, 'success');
    } catch (error) {
        console.error(`Error enabling workflow ${workflow}:`, error);
        showNotification(`Failed to enable workflow ${workflow}`, 'error');
    }
}

async function disableWorkflow(workflow) {
    try {
        const response = await fetch(`/api/v1/bot-admin/workflow/${workflow}/disable`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        showNotification(data.message, 'success');
    } catch (error) {
        console.error(`Error disabling workflow ${workflow}:`, error);
        showNotification(`Failed to disable workflow ${workflow}`, 'error');
    }
}

// Status-Updates
function startStatusUpdates() {
    updateBotStatus();
    
    // Aktualisiere den Status alle 10 Sekunden
    setInterval(updateBotStatus, 10000);
}

async function updateBotStatus() {
    try {
        const response = await fetch('/api/v1/bot-admin/status');
        const data = await response.json();
        
        // Status-Anzeige aktualisieren
        const statusElement = document.getElementById('bot-status');
        if (data.connected) {
            statusElement.textContent = 'Online';
            statusElement.classList.add('text-success');
            statusElement.classList.remove('text-danger');
        } else {
            statusElement.textContent = 'Offline';
            statusElement.classList.add('text-danger');
            statusElement.classList.remove('text-success');
        }
        
        // Uptime aktualisieren
        document.getElementById('bot-uptime').textContent = data.uptime || 'Not available';
        
    } catch (error) {
        console.error('Error updating bot status:', error);
    }
}

// Hilfsfunktion für Benachrichtigungen
function showNotification(message, type) {
    // Implementiere deine Benachrichtigungslogik hier
    console.log(`[${type}] ${message}`);
    
    // Beispiel mit Bootstrap Toasts
    if (typeof bootstrap !== 'undefined') {
        const toastContainer = document.getElementById('toast-container');
        if (toastContainer) {
            const toastEl = document.createElement('div');
            toastEl.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
            toastEl.setAttribute('role', 'alert');
            toastEl.setAttribute('aria-live', 'assertive');
            toastEl.setAttribute('aria-atomic', 'true');
            
            toastEl.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            `;
            
            toastContainer.appendChild(toastEl);
            const toast = new bootstrap.Toast(toastEl);
            toast.show();
        }
    }
}
