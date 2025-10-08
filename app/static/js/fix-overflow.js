/**
 * FIX OVERFLOW SCRIPT
 * Script independiente para corregir problemas de overflow en la página
 * 
 * Este script puede incluirse en cualquier página que tenga problemas
 * con el desplazamiento después de cerrar modales.
 * 
 * Versión: 1.0 (2025-10-08)
 */

// Auto-ejecutable para aislar variables
(function() {
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
        
        console.log('✅ [FIX-OVERFLOW] Desplazamiento restaurado');
        return true;
    }
    
    // Verificar periódicamente si el overflow está bloqueado sin modal visible
    function checkOverflow() {
        const bodyStyle = window.getComputedStyle(document.body);
        const isOverflowHidden = bodyStyle.overflow === 'hidden';
        const hasModalOpenClass = document.body.classList.contains('modal-open');
        const hasVisibleModal = document.querySelector('.modal.show') !== null;
        
        if ((isOverflowHidden || hasModalOpenClass) && !hasVisibleModal) {
            console.log('🔍 [FIX-OVERFLOW] Detectado bloqueo de desplazamiento sin modal visible');
            return fixOverflow();
        }
        return false;
    }
    
    // Añadir botón de restauración de emergencia en modo desarrollo
    function addEmergencyButton() {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            // Verificar si el botón ya existe
            if (document.querySelector('.restore-scroll-button')) {
                return;
            }
            
            const button = document.createElement('button');
            button.innerText = '🔄 Restaurar Scroll';
            button.className = 'btn btn-sm btn-warning restore-scroll-button';
            button.addEventListener('click', fixOverflow);
            
            document.body.appendChild(button);
            console.log('ℹ️ [FIX-OVERFLOW] Botón de emergencia añadido');
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
            });
        });
        
        // Observar cambios en las clases de todos los elementos modal
        document.querySelectorAll('.modal').forEach(function(modal) {
            observer.observe(modal, { attributes: true });
        });
    }
    
    // Establecer verificación periódica
    setInterval(checkOverflow, 2000);
    
    // Añadir eventos para restaurar el overflow al cerrar modales
    document.addEventListener('DOMContentLoaded', function() {
        // Verificar y corregir al cargar la página
        setTimeout(checkOverflow, 500);
        
        // Añadir manejadores a todos los modales
        document.querySelectorAll('.modal').forEach(function(modalElement) {
            modalElement.addEventListener('hidden.bs.modal', function() {
                setTimeout(fixOverflow, 100);
            });
        });
        
        // Añadir el botón de emergencia
        addEmergencyButton();
        
        // Observar cambios en modales
        observeModalChanges();
        
        console.log('✅ [FIX-OVERFLOW] Script de corrección inicializado');
    });
    
    // Exportar función para uso global
    window.fixPageOverflow = fixOverflow;
    
    // Ejecutar verificación inicial después de un momento
    setTimeout(checkOverflow, 1000);
})();

// Mensaje de consola para verificar que el script se cargó
console.log('✅ [FIX-OVERFLOW] Script cargado');