// Bot CRUD Control Module
const BotCrudControl = (function() {
    // Private variables and functions
    let botSettingsForm;
    
    function initForm() {
        botSettingsForm = document.getElementById('bot-settings-form');
        if (botSettingsForm) {
            botSettingsForm.addEventListener('submit', handleSettingsSubmit);
        }
    }
    
    async function handleSettingsSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(botSettingsForm);
        const settings = Object.fromEntries(formData.entries());
        
        try {
            const response = await fetch('/api/v1/bot-admin/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showNotification('Bot settings updated successfully', 'success');
            } else {
                showNotification(`Error: ${result.detail || 'Failed to update settings'}`, 'error');
            }
        } catch (error) {
            console.error('Error updating bot settings:', error);
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
            console.log('Initializing Bot CRUD Control');
            initForm();
        }
    };
})();
