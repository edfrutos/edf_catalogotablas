/**
 * debug-enable.js
 * Script para activar el modo de depuración en toda la aplicación.
 * Este archivo debe ser incluido antes de cualquier otro script para activar la depuración global.
 */
(function() {
    'use strict';
    
    // Activar el modo depuración global
    window.DEBUG_MODE = true;
    
    // Registrar en consola que se ha activado la depuración
    console.info('%c[DEBUG-MODE]', 'background:#ff0; color:#000; font-weight:bold', 'Modo de depuración activado');
    
    // Función para añadir información de depuración al DOM
    function addDebugInfo() {
        // Solo ejecutar una vez que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', addDebugInfoToDom);
        } else {
            addDebugInfoToDom();
        }
    }
    
    function addDebugInfoToDom() {
        // Crear botón de depuración flotante
        const debugButton = document.createElement('div');
        debugButton.innerHTML = `
            <div style="position:fixed; bottom:10px; right:10px; z-index:9999; background:rgba(255,255,0,0.8); 
                        padding:5px 10px; border-radius:5px; font-size:12px; cursor:pointer; user-select:none;">
                <i class="fas fa-bug"></i> DEBUG
            </div>
        `;
        document.body.appendChild(debugButton);
        
        // Evento click para mostrar panel de depuración
        debugButton.addEventListener('click', showDebugPanel);
    }
    
    function showDebugPanel() {
        // Verificar si ya existe el panel
        if (document.getElementById('debug-panel')) {
            document.getElementById('debug-panel').remove();
            return;
        }
        
        // Crear panel de depuración
        const debugPanel = document.createElement('div');
        debugPanel.id = 'debug-panel';
        debugPanel.style.cssText = `
            position: fixed;
            bottom: 40px;
            right: 10px;
            width: 300px;
            max-height: 400px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.8);
            color: #fff;
            z-index: 9998;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
        `;
        
        // Añadir contenido al panel de depuración
        debugPanel.innerHTML = `
            <div style="border-bottom: 1px solid #666; padding-bottom: 5px; margin-bottom: 5px;">
                <strong>Información de depuración</strong>
                <span style="float:right; cursor:pointer;" onclick="document.getElementById('debug-panel').remove();">
                    &times;
                </span>
            </div>
            <p><strong>URL actual:</strong> ${window.location.href}</p>
            <p><strong>User Agent:</strong> ${navigator.userAgent}</p>
            <p><strong>Scripts detectados:</strong> ${document.scripts.length}</p>
            <p><strong>Hora:</strong> ${new Date().toLocaleTimeString()}</p>
            <div id="debug-urls" style="margin-top:10px;"></div>
            <div id="debug-log" style="margin-top:10px; border-top:1px solid #666; padding-top:5px;"></div>
            <div style="margin-top:10px; border-top:1px solid #666; padding-top:5px;">
                <button style="background:#333; border:1px solid #666; color:#fff; padding:3px 8px; cursor:pointer;" 
                        onclick="localStorage.setItem('debugMode', 'true'); alert('Modo debug persistente activado');">
                    Activar Debug Persistente
                </button>
                <button style="background:#333; border:1px solid #666; color:#fff; padding:3px 8px; cursor:pointer; margin-left:5px;" 
                        onclick="localStorage.removeItem('debugMode'); alert('Modo debug persistente desactivado');">
                    Desactivar
                </button>
            </div>
        `;
        
        document.body.appendChild(debugPanel);
        
        // Buscar y mostrar URLs relevantes
        const debugUrls = document.getElementById('debug-urls');
        if (debugUrls) {
            let links = Array.from(document.querySelectorAll('a[href*="spreadsheets"], a[href*="excel"], a[href*=".xls"]'));
            if (links.length > 0) {
                debugUrls.innerHTML = '<strong>URLs de Excel/Spreadsheets:</strong><ul style="padding-left:20px;">';
                links.forEach(link => {
                    debugUrls.innerHTML += `<li>${link.getAttribute('href')}</li>`;
                });
                debugUrls.innerHTML += '</ul>';
            } else {
                debugUrls.innerHTML = '<em>No se encontraron URLs de Excel en la página</em>';
            }
        }
    }
    
    // Sobrescribir console.log para capturar en el panel de depuración
    const originalConsoleLog = console.log;
    console.log = function() {
        originalConsoleLog.apply(console, arguments);
        
        // Añadir al panel de depuración si existe
        const debugLog = document.getElementById('debug-log');
        if (debugLog && arguments.length > 0) {
            const timestamp = new Date().toLocaleTimeString();
            const message = Array.from(arguments).map(arg => {
                if (typeof arg === 'object') {
                    try {
                        return JSON.stringify(arg);
                    } catch (e) {
                        return String(arg);
                    }
                } else {
                    return String(arg);
                }
            }).join(' ');
            
            const logEntry = document.createElement('div');
            logEntry.style.cssText = 'margin:2px 0; font-size:11px; word-break:break-all;';
            logEntry.innerHTML = `<span style="color:#999;">[${timestamp}]</span> ${message}`;
            debugLog.appendChild(logEntry);
            debugLog.scrollTop = debugLog.scrollHeight;
        }
    };
    
    // Comprobar si el modo debug persistente está activado
    if (localStorage.getItem('debugMode') === 'true') {
        console.info('Debug persistente activado desde localStorage');
    }
    
    // Inicializar cuando el DOM esté listo
    addDebugInfo();
    
    // Exponer globalmente
    window.showDebugPanel = showDebugPanel;
})();
