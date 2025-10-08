/**
 * MODAL OVERFLOW FIX - SOLUCIÓN PARA PROBLEMA DE OVERFLOW EN MODALES
 * Este script corrige el problema de overflow: hidden que queda en el body después de cerrar modales
 * Versión: 1.0 (2025-10-08)
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 [MODAL-OVERFLOW-FIX] Inicializando solución para problema de overflow...');
    
    // Modales conocidos en la aplicación
    const knownModals = [
        '#imageModal',
        '#documentModal',
        '#multimediaModal',
        '#confirmDeleteModal',
        '#exportModal',
        '.modal' // Selector genérico para cualquier otro modal
    ];
    
    // Función para restaurar el scroll después de cerrar un modal
    function fixOverflowAfterModalClose() {
        // Eliminar clases que Bootstrap añade al body
        document.body.classList.remove('modal-open');
        
        // Eliminar el estilo inline overflow:hidden que Bootstrap añade
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        // Eliminar el backdrop residual si existiera
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => {
            backdrop.remove();
        });
        
        console.log('✅ [MODAL-OVERFLOW-FIX] Overflow restaurado correctamente');
    }
    
    // Función para verificar el estado actual del overflow y corregirlo si es necesario
    function checkAndFixOverflow() {
        const computedStyle = window.getComputedStyle(document.body);
        const hasHiddenOverflow = computedStyle.overflow === 'hidden';
        const hasModalOpenClass = document.body.classList.contains('modal-open');
        const hasVisibleModals = document.querySelector('.modal.show') !== null;
        
        if ((hasHiddenOverflow || hasModalOpenClass) && !hasVisibleModals) {
            console.log('🔍 [MODAL-OVERFLOW-FIX] Detectado overflow:hidden sin modales visibles, corrigiendo...');
            fixOverflowAfterModalClose();
            return true; // Se hizo corrección
        }
        return false; // No fue necesario corregir
    }
    
    // Aplicar evento hidden.bs.modal a todos los modales conocidos
    knownModals.forEach(modalSelector => {
        const modalElements = document.querySelectorAll(modalSelector);
        
        modalElements.forEach(modalElement => {
            if (modalElement) {
                // Usar evento nativo de Bootstrap cuando el modal se oculta completamente
                modalElement.addEventListener('hidden.bs.modal', function() {
                    console.log(`🔍 [MODAL-OVERFLOW-FIX] Modal cerrado: ${modalSelector}`);
                    
                    // Esperar un momento para que Bootstrap termine sus operaciones
                    setTimeout(function() {
                        fixOverflowAfterModalClose();
                    }, 100);
                });
                
                console.log(`✅ [MODAL-OVERFLOW-FIX] Listener añadido a: ${modalSelector}`);
            }
        });
    });
    
    // Verificación periódica del estado de overflow (como respaldo)
    setInterval(checkAndFixOverflow, 2000);
    
    // Comprobar inmediatamente por si ya hay un problema al cargar la página
    if (checkAndFixOverflow()) {
        console.log('⚠️ [MODAL-OVERFLOW-FIX] Problema de overflow corregido al iniciar');
    }
    
    // Añadir un botón de recuperación de emergencia (visible solo en modo desarrollo)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        const emergencyButton = document.createElement('button');
        emergencyButton.textContent = 'Restaurar Scroll';
        emergencyButton.className = 'btn btn-sm btn-warning position-fixed';
        emergencyButton.style.bottom = '10px';
        emergencyButton.style.right = '10px';
        emergencyButton.style.zIndex = '9999';
        emergencyButton.style.opacity = '0.7';
        emergencyButton.onclick = fixOverflowAfterModalClose;
        
        // Agregar el botón al final del body
        document.body.appendChild(emergencyButton);
    }
    
    console.log('✅ [MODAL-OVERFLOW-FIX] Solución instalada correctamente');
});