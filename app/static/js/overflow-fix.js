/**
 * SISTEMA DE CORRECCIÓN DE OVERFLOW - MEJORADO
 * Integrado directamente en el proyecto
 * Fecha: 8 de Octubre de 2025
 * 
 * Este sistema mejora la corrección de problemas de overflow
 * tras el cierre de modales en toda la aplicación.
 */

// Auto-ejecutable para aislar variables
(function() {
    // Configuración y logging
    const DEBUG = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const log = DEBUG ? console.log : () => {};
    
    log("🚀 [OVERFLOW-FIX] Inicializando sistema mejorado de corrección de overflow");
    
    // Función principal para restaurar el estado de desplazamiento
    function fixOverflow() {
        // Eliminar estilos y clases que bloquean el scroll
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        document.body.classList.remove('modal-open');
        document.documentElement.classList.remove('scroll-blocked');
        document.body.classList.remove('scroll-blocked');
        
        // Eliminar backdrops de modal residuales
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(function(backdrop) {
            backdrop.remove();
        });
        
        log("✅ [OVERFLOW-FIX] Desplazamiento restaurado");
        return true;
    }
    
    // Verificar periódicamente si el overflow está bloqueado sin modal visible
    function checkOverflow() {
        const bodyStyle = window.getComputedStyle(document.body);
        const isOverflowHidden = bodyStyle.overflow === 'hidden';
        const hasModalOpenClass = document.body.classList.contains('modal-open');
        const hasVisibleModal = document.querySelector('.modal.show') !== null;
        
        if ((isOverflowHidden || hasModalOpenClass) && !hasVisibleModal) {
            log("🔍 [OVERFLOW-FIX] Detectado bloqueo de desplazamiento sin modal visible");
            return fixOverflow();
        }
        return false;
    }
    
    // Añadir botón de restauración de emergencia en modo desarrollo
    function addEmergencyButton() {
        if (DEBUG) {
            // Verificar si el botón ya existe
            if (document.querySelector('.restore-scroll-button')) {
                return;
            }
            
            const button = document.createElement('button');
            button.innerText = '🔄 Restaurar Scroll';
            button.className = 'btn btn-sm btn-warning restore-scroll-button';
            button.style.position = 'fixed';
            button.style.right = '20px';
            button.style.bottom = '80px';
            button.style.zIndex = '9999';
            button.style.opacity = '0.8';
            button.style.borderRadius = '4px';
            button.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';
            button.addEventListener('click', fixOverflow);
            
            document.body.appendChild(button);
            log("ℹ️ [OVERFLOW-FIX] Botón de emergencia añadido");
        }
    }
    
    // Observar cambios en el DOM para detectar modales que se cierran
    function observeModalChanges() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const target = mutation.target;
                    
                    // Si un modal acaba de cerrarse (perdió la clase 'show')
                    if (target.classList.contains('modal') && !target.classList.contains('show')) {
                        setTimeout(fixOverflow, 100);
                    }
                }
                
                // Verificar nodos añadidos
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Si es un modal, añadir evento
                            if (node.classList && node.classList.contains('modal')) {
                                setupModalListener(node);
                            }
                            // Buscar modales dentro del nodo añadido
                            if (node.querySelectorAll) {
                                const modals = node.querySelectorAll('.modal');
                                if (modals.length > 0) {
                                    modals.forEach(setupModalListener);
                                }
                            }
                        }
                    });
                }
            });
        });
        
        // Observar cambios en las clases y nodos añadidos en todo el documento
        observer.observe(document.body, { 
            attributes: true,
            attributeFilter: ['class'],
            childList: true,
            subtree: true
        });
        
        log("✅ [OVERFLOW-FIX] Observador de cambios en modales inicializado");
    }
    
    // Configurar listener para un elemento modal
    function setupModalListener(modalElement) {
        if (!modalElement || modalElement.dataset.overflowFixAdded) {
            return;
        }
        
        modalElement.dataset.overflowFixAdded = "true";
        modalElement.addEventListener('hidden.bs.modal', function() {
            setTimeout(fixOverflow, 100);
        });
        
        log("✅ [OVERFLOW-FIX] Listener añadido a modal: " + (modalElement.id || 'sin ID'));
    }
    
    // Configurar todos los modales existentes
    function setupAllModals() {
        document.querySelectorAll('.modal').forEach(setupModalListener);
    }
    
    // Función principal de inicialización
    function init() {
        // Verificar y corregir inmediatamente al cargar
        setTimeout(checkOverflow, 500);
        
        // Añadir listeners a todos los modales existentes
        setupAllModals();
        
        // Observar cambios en el DOM para nuevos modales
        observeModalChanges();
        
        // Añadir botón de emergencia en desarrollo
        addEmergencyButton();
        
        // Establecer verificación periódica
        setInterval(checkOverflow, 2000);
        
        // Exportar función para uso global
        window.fixPageOverflow = fixOverflow;
        
        log("✅ [OVERFLOW-FIX] Sistema de corrección de overflow inicializado");
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // Si el DOM ya está cargado, ejecutar inmediatamente
        init();
    }
})();

console.log('✅ [OVERFLOW-FIX] Sistema de corrección de overflow cargado correctamente');