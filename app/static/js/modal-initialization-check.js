/**
 * MODAL INITIALIZATION CHECK - VERIFICACIÓN DE INICIALIZACIÓN DE MODALES
 * Este script verifica que todos los modales Bootstrap se inicialicen correctamente
 * Versión: 1.0 (2025-10-08)
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 [MODAL-CHECK] Verificando inicialización de modales...');
    
    // Lista de modales a verificar
    const modals = [
        { id: 'imageModal', name: 'Modal de imágenes' },
        { id: 'documentModal', name: 'Modal de documentos' },
        { id: 'multimediaModal', name: 'Modal multimedia' },
        { id: 'confirmDeleteModal', name: 'Modal de confirmación' },
        { id: 'exportModal', name: 'Modal de exportación' }
    ];
    
    let totalModals = 0;
    let initializedModals = 0;
    let missingModals = 0;
    
    // Verificar si Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.error('❌ [MODAL-CHECK] Bootstrap no está disponible. Los modales no funcionarán correctamente.');
        
        // Añadir advertencia visible
        showBootstrapWarning();
        return;
    } else {
        console.log('✅ [MODAL-CHECK] Bootstrap detectado correctamente.');
    }
    
    // Verificar e inicializar modales si es necesario
    modals.forEach(function(modalConfig) {
        totalModals++;
        const modalElement = document.getElementById(modalConfig.id);
        
        if (modalElement) {
            try {
                // Intentar inicializar el modal con Bootstrap
                new bootstrap.Modal(modalElement);
                initializedModals++;
                
                // Corregir eventos para el problema de overflow
                modalElement.addEventListener('hidden.bs.modal', function() {
                    // Restaurar overflow después de que el modal se cierre
                    setTimeout(function() {
                        document.body.style.overflow = '';
                        document.body.classList.remove('modal-open');
                    }, 100);
                });
                
                console.log(`✅ [MODAL-CHECK] ${modalConfig.name} (${modalConfig.id}) inicializado correctamente.`);
            } catch (error) {
                console.error(`❌ [MODAL-CHECK] Error al inicializar ${modalConfig.name}: ${error.message}`);
            }
        } else {
            missingModals++;
            console.log(`ℹ️ [MODAL-CHECK] ${modalConfig.name} (${modalConfig.id}) no encontrado en esta página.`);
        }
    });
    
    console.log(`🔍 [MODAL-CHECK] Resultado de verificación: ${initializedModals}/${totalModals} modales inicializados, ${missingModals} no encontrados.`);
    
    // Verificar la existencia de showMultimediaModal
    if (typeof window.showMultimediaModal === 'function') {
        console.log('✅ [MODAL-CHECK] Función showMultimediaModal disponible.');
    } else {
        console.error('❌ [MODAL-CHECK] Función showMultimediaModal no disponible. Los modales multimedia no funcionarán correctamente.');
    }
    
    // Función para mostrar advertencia si Bootstrap no está disponible
    function showBootstrapWarning() {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            const warningDiv = document.createElement('div');
            warningDiv.className = 'alert alert-danger position-fixed';
            warningDiv.style.top = '10px';
            warningDiv.style.right = '10px';
            warningDiv.style.zIndex = '9999';
            warningDiv.innerHTML = '<strong>Error:</strong> Bootstrap no detectado. Los modales no funcionarán.';
            document.body.appendChild(warningDiv);
        }
    }
});

/**
 * Función global para comprobar y arreglar el estado del modal bajo demanda
 * Puede ser llamada desde la consola del navegador: fixModalState()
 */
window.fixModalState = function() {
    console.log('🔧 [MODAL-CHECK] Ejecutando corrección manual de estado de modales...');
    
    // Eliminar cualquier backdrop residual
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(function(backdrop) {
        backdrop.remove();
    });
    
    // Restaurar estado del body
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    document.body.classList.remove('modal-open');
    
    console.log('✅ [MODAL-CHECK] Estado de modales corregido manualmente.');
    return 'Estado de modales corregido';
};