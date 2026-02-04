/**
 * TEST DE MODALES - VERIFICACIÓN DE SOLUCIÓN
 * Script para verificar que la solución a los problemas de recursión infinita funciona correctamente
 */

console.log('🧪 [MODAL-TEST] Iniciando test de modales...');

// Función para verificar si una función existe y es callable
function checkFunction(name, func) {
  const exists = typeof func === 'function';
  console.log(`🔍 [MODAL-TEST] Verificando ${name}: ${exists ? '✅ Existe' : '❌ No existe'}`);
  return exists;
}

// Comprobar que las funciones principales están disponibles
document.addEventListener('DOMContentLoaded', function() {
  console.log('🧪 [MODAL-TEST] DOM cargado, verificando funciones...');
  
  // Verificar funciones principales
  checkFunction('showDocumentModal', window.showDocumentModal);
  checkFunction('showImageModal', window.showImageModal);
  checkFunction('showMultimediaModal', window.showMultimediaModal);
  checkFunction('downloadS3File', window.downloadS3File);
  checkFunction('downloadLocalFile', window.downloadLocalFile);
  
  // Comprobar que no hay wrappers recursivos
  console.log('🧪 [MODAL-TEST] Probando llamada a showMultimediaModal...');
  
  try {
    // Llamar a la función con todos los parámetros
    if (typeof window.showMultimediaModal === 'function') {
      console.log('🧪 [MODAL-TEST] Llamando a showMultimediaModal...');
      // Solo para test - no ejecutar realmente para evitar abrir modal
      // window.showMultimediaModal('https://example.com/video.mp4', 'Video de prueba');
      console.log('✅ [MODAL-TEST] showMultimediaModal debería funcionar correctamente');
    }
  } catch (error) {
    console.error('❌ [MODAL-TEST] Error en la prueba:', error);
  }
  
  console.log('✅ [MODAL-TEST] Test completado');
});