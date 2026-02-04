/**
 * DEBUG CONFIGURATION
 * Archivo centralizado para configurar opciones de depuración
 * Actualizado: 2026-02-04
 */

(function() {
    // Detección automática de entorno
    const isLocalhost = window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1';
    
    // Comprobar si el debug persistente está activado
    const isPersistentDebug = localStorage.getItem('debugMode') === 'true';
    
    // Configuración global para todo el proyecto
    window.APP_CONFIG = {
        // Activar debug en localhost o si está configurado como persistente
        DEBUG_MODE: isLocalhost || isPersistentDebug,
        
        // Otras configuraciones de rendimiento
        PERFORMANCE: {
            DISABLE_ANIMATIONS: !isLocalhost,
            OPTIMIZE_RENDERING: true,
            REDUCE_DOM_OPERATIONS: true
        },
        
        // Logger centralizado que no genera salida en producción
        log: function() {
            if (this.DEBUG_MODE) {
                console.log.apply(console, arguments);
            }
        },
        
        // Siempre permitir errores críticos
        error: function() {
            console.error.apply(console, arguments);
        },
        
        // Logger para información de rendimiento (desactivado en producción)
        perfLog: function() {
            if (this.DEBUG_MODE && console.timeLog) {
                console.timeLog.apply(console, arguments);
            }
        }
    };
    
    // Función global para obtener el estado de debug
    window.getDebugMode = function() {
        return window.APP_CONFIG.DEBUG_MODE;
    };
    
    // Reemplazar console.log en producción para evitar logs accidentales
    if (!window.APP_CONFIG.DEBUG_MODE) {
        // Guardar la referencia original por si es necesaria
        window._originalConsoleLog = console.log;
        
        // Reemplazar con función vacía en producción
        console.log = function() {
            // No hacer nada en producción
            return;
        };
    } else {
        console.log('%c[DEBUG-CONFIG] Modo de depuración ACTIVO', 'color: green; font-weight: bold');
    }
})();