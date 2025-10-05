/**
 * MODAL FIX SIMPLE - Solución básica para overlay persistente
 * Reemplaza la versión compleja que causaba problemas
 */

// Función simple para limpiar backdrops
function limpiarBackdropsSimple() {
    console.log('[MODAL-FIX-SIMPLE] 🧹 Limpiando backdrops...');
    
    // Solo eliminar los backdrops, no tocar los modales
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach((backdrop, index) => {
        console.log(`[MODAL-FIX-SIMPLE] 🗑️ Eliminando backdrop ${index + 1}`);
        backdrop.remove();
    });
    
    // Limpiar clases del body
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    
    console.log('[MODAL-FIX-SIMPLE] ✅ Limpieza simple completada');
}

// Configurar limpieza básica al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('[MODAL-FIX-SIMPLE] ⚙️ Configurando limpieza simple...');
    
    // Limpieza cada 3 segundos si hay backdrops
    setInterval(() => {
        const backdrops = document.querySelectorAll('.modal-backdrop');
        if (backdrops.length > 0) {
            console.log(`[MODAL-FIX-SIMPLE] 🕐 Encontrados ${backdrops.length} backdrops, limpiando...`);
            limpiarBackdropsSimple();
        }
    }, 3000);
    
    console.log('[MODAL-FIX-SIMPLE] ✅ Sistema simple configurado');
});

// Exportar función global
window.limpiarBackdropsSimple = limpiarBackdropsSimple;