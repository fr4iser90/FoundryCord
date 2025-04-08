import { showToast, apiRequest } from '/static/js/components/common/notifications.js';

// Configuration Management Functions
const handleConfigSubmit = async (event) => {
    event.preventDefault();
    
    const form = event.target;
    if (!form.checkValidity()) {
        event.stopPropagation();
        form.classList.add('was-validated');
        return;
    }
    
    const formData = new FormData(form);
    const config = {
        command_prefix: formData.get('command_prefix'),
        log_level: formData.get('log_level'),
        status_update_interval: parseInt(formData.get('status_update_interval')),
        max_reconnect_attempts: parseInt(formData.get('max_reconnect_attempts')),
        auto_reconnect: formData.get('auto_reconnect') === 'on',
        enable_logging: formData.get('enable_logging') === 'on',
        enable_metrics: formData.get('enable_metrics') === 'on',
        enable_debug: formData.get('enable_debug') === 'on',
        enable_notifications: formData.get('enable_notifications') === 'on'
    };
    
    try {
        await apiRequest('/api/v1/owner/bot/config', {
            method: 'PUT',
            body: JSON.stringify(config),
        });
        
        showToast('success', 'Configuration updated successfully');
    } catch (error) {
        showToast('error', 'Failed to update configuration');
    }
};

const resetConfig = async () => {
    if (!confirm('Are you sure you want to reset all settings to default values?')) {
        return;
    }
    
    try {
        const data = await apiRequest('/api/v1/owner/bot/config/reset', {
            method: 'POST'
        });
        
        showToast('success', 'Configuration reset to defaults');
        
        // Update form with default values
        Object.entries(data).forEach(([key, value]) => {
            const element = document.querySelector(`[name="${key}"]`);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = value;
                } else {
                    element.value = value;
                }
            }
        });
    } catch (error) {
        showToast('error', 'Failed to reset configuration');
    }
};

// Validation Functions
const validateNumberInput = (input) => {
    const value = parseInt(input.value);
    const min = parseInt(input.min);
    const max = parseInt(input.max);
    
    if (isNaN(value) || value < min || value > max) {
        input.setCustomValidity(`Please enter a number between ${min} and ${max}`);
    } else {
        input.setCustomValidity('');
    }
};

// Initialize config management
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('botConfigForm');
    if (form) {
        form.addEventListener('submit', handleConfigSubmit);
    }

    const resetButton = document.querySelector('button[onclick="resetConfig()"]');
    if (resetButton) {
        resetButton.onclick = (e) => {
            e.preventDefault();
            resetConfig();
        };
    }

    // Set up input validation listeners
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', () => validateNumberInput(input));
    });
}); 