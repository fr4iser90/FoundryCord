/**
 * HomeLab Discord Bot - Widget UI System
 * 
 * Ein modulares Widget-System mit dynamischen Lademöglichkeiten
 */

const WidgetUI = (function() {
    // Speichert registrierte Widgets
    const _registeredWidgets = {};
    
    // Container für aktive Widgets auf der aktuellen Seite
    const _activeWidgets = new Map();
    
    // Konfiguration
    const _defaultConfig = {
        refreshInterval: 30000,      // Standard-Aktualisierungsintervall
        animationSpeed: 300,         // Standard-Animationsgeschwindigkeit
        storagePrefix: 'widget_',     // Präfix für localStorage
        defaultCollapsed: false       // Standard-Zustand (eingeklappt)
    };
    
    let _globalConfig = {..._defaultConfig};
    
    /**
     * Widget registrieren
     * @param {string} widgetId - Eindeutige ID des Widgets
     * @param {object} widgetDefinition - Definition und Verhalten des Widgets
     */
    function registerWidget(widgetId, widgetDefinition) {
        if (_registeredWidgets[widgetId]) {
            console.warn(`Widget '${widgetId}' wurde bereits registriert und wird überschrieben`);
        }
        
        // Sicherstellen, dass Pflichtmethoden vorhanden sind
        const required = ['render', 'init'];
        const missing = required.filter(method => !widgetDefinition[method]);
        
        if (missing.length > 0) {
            throw new Error(`Widget '${widgetId}' fehlen folgende Pflichtmethoden: ${missing.join(', ')}`);
        }
        
        _registeredWidgets[widgetId] = widgetDefinition;
        console.log(`Widget '${widgetId}' erfolgreich registriert`);
        
        return widgetDefinition; // Für Chaining
    }
    
    /**
     * Widget instanziieren und aktivieren
     * @param {string} widgetId - ID des zu ladenden Widgets
     * @param {string} containerId - ID des DOM-Elements, in dem das Widget gerendert wird
     * @param {object} options - Optionen für dieses Widget
     */
    function loadWidget(widgetId, containerId, options = {}) {
        if (!_registeredWidgets[widgetId]) {
            console.error(`Widget '${widgetId}' nicht gefunden. Registriere es zuerst.`);
            return null;
        }
        
        // Widget-Container holen
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container '${containerId}' nicht gefunden`);
            return null;
        }
        
        // Widget-Instance erstellen
        const widgetConfig = {
            id: widgetId,
            container,
            options: {..._globalConfig, ...options}
        };
        
        try {
            // Widget initialisieren
            const widgetInstance = Object.create(_registeredWidgets[widgetId]);
            widgetInstance.init(widgetConfig);
            
            // Widget rendern
            widgetInstance.render();
            
            // Widget in aktive Liste aufnehmen
            _activeWidgets.set(`${widgetId}_${containerId}`, widgetInstance);
            
            return widgetInstance;
        } catch (error) {
            console.error(`Fehler beim Laden des Widgets '${widgetId}':`, error);
            return null;
        }
    }
    
    /**
     * Alle Widgets auf der aktuellen Seite aktualisieren
     */
    function refreshAllWidgets() {
        _activeWidgets.forEach(widget => {
            if (widget.refresh && typeof widget.refresh === 'function') {
                widget.refresh();
            }
        });
    }
    
    /**
     * Widget-Hilfsfunktionen für Standardverhalten
     */
    const helpers = {
        toggleCollapse: function(widgetElement, callback) {
            const content = widgetElement.querySelector('.widget-content');
            const icon = widgetElement.querySelector('.widget-toggle i');
            
            if (!content || !icon) return;
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                icon.classList.remove('bi-chevron-down');
                icon.classList.add('bi-chevron-up');
                if (callback) callback(false); // nicht collapsed
            } else {
                content.style.display = 'none';
                icon.classList.remove('bi-chevron-up');
                icon.classList.add('bi-chevron-down');
                if (callback) callback(true); // collapsed
            }
        },
        
        createWidgetFrame: function(title, withToggle = true) {
            const widgetFrame = document.createElement('div');
            widgetFrame.className = 'widget-card';
            
            const header = document.createElement('div');
            header.className = 'widget-header';
            
            const titleEl = document.createElement('h5');
            titleEl.textContent = title;
            header.appendChild(titleEl);
            
            if (withToggle) {
                const toggle = document.createElement('button');
                toggle.className = 'widget-toggle';
                toggle.innerHTML = '<i class="bi bi-chevron-up"></i>';
                toggle.addEventListener('click', (e) => {
                    const widget = e.target.closest('.widget-card');
                    this.toggleCollapse(widget);
                });
                header.appendChild(toggle);
            }
            
            const content = document.createElement('div');
            content.className = 'widget-content';
            
            widgetFrame.appendChild(header);
            widgetFrame.appendChild(content);
            
            return {
                frame: widgetFrame,
                header,
                content
            };
        },
        
        showLoading: function(element) {
            element.innerHTML = '<div class="text-center p-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        },
        
        showError: function(element, message) {
            element.innerHTML = `<div class="alert alert-danger" role="alert">${message}</div>`;
        }
    };
    
    /**
     * Utility-Funktionen für allgemeine UI-Operationen
     */
    const ui = {
        showToast: function(message, type = 'success') {
            if (typeof bootstrap !== 'undefined') {
                const toastContainer = document.getElementById('toast-container');
                if (!toastContainer) {
                    // Toast-Container erstellen, falls nicht vorhanden
                    const newContainer = document.createElement('div');
                    newContainer.id = 'toast-container';
                    newContainer.className = 'position-fixed bottom-0 end-0 p-3';
                    newContainer.style.zIndex = '11';
                    document.body.appendChild(newContainer);
                }
                
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
            } else {
                console.log(`[${type}] ${message}`);
            }
        }
    };
    
    // Öffentliche API
    return {
        registerWidget,
        loadWidget,
        refreshAllWidgets,
        helpers,
        ui
    };
})();

// Globalen Zugriff erlauben
window.WidgetUI = WidgetUI;

// Benachrichtigungsfunktion global verfügbar machen
window.showNotification = function(message, type) {
    WidgetUI.ui.showToast(message, type);
};
