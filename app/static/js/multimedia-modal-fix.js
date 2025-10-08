/**
 * MULTIMEDIA MODAL FIX - SOLUCIÓN PARA MODALES MULTIMEDIA
 * Script para solucionar problemas con la apertura de modales multimedia
 * Versión: 1.1 (2025-10-08)
 */

// Verificar si ya existe una función showMultimediaModal
if (typeof window.showMultimediaModal !== 'function') {
  // Usar el logger centralizado si está disponible
  if (window.APP_CONFIG) {
    window.APP_CONFIG.error('⚠️ [MULTIMEDIA-FIX] showMultimediaModal no está definido, creando función de emergencia...');
  }
  
  // Función de emergencia para mostrar multimedia en modal
  window.showMultimediaModal = function(multimediaSrc, multimediaTitle, e) {
    // Usar el logger centralizado si está disponible
    if (window.APP_CONFIG && window.APP_CONFIG.DEBUG_MODE) {
      window.APP_CONFIG.log('🔧 [MULTIMEDIA-FIX] showMultimediaModal (EMERGENCY VERSION) llamado con:', { multimediaSrc, multimediaTitle });
    }
    
    // Prevenir comportamiento predeterminado si hay evento
    if (e) {
      e.preventDefault();
    }
    
    // Buscar elementos del modal
    const modalElement = document.getElementById('multimediaModal');
    const modalContent = document.getElementById('multimediaContent');
    const modalTitle = document.getElementById('multimediaModalLabel');
    
    if (!modalElement || !modalContent || !modalTitle) {
      // Siempre mostrar este error (incluso en producción)
      if (window.APP_CONFIG) {
        window.APP_CONFIG.error('✕ [MULTIMEDIA-FIX] Elementos del modal multimedia no encontrados');
      } else {
        console.error('✕ [MULTIMEDIA-FIX] Elementos del modal multimedia no encontrados');
      }
      alert('Error: Modal multimedia no disponible. Contacte al administrador.');
      return;
    }
    
    // Configurar título
    modalTitle.textContent = multimediaTitle || 'Multimedia';
    
    // Detectar tipo de archivo por extensión
    const fileExtension = multimediaSrc.split('.').pop()?.toLowerCase();
    const isVideo = ['mp4', 'webm', 'avi', 'mov'].includes(fileExtension);
    const isAudio = ['mp3', 'wav', 'ogg', 'aac'].includes(fileExtension);
    const isYouTube = multimediaSrc.includes('youtube.com') || multimediaSrc.includes('youtu.be');
    
    // Preparar el contenido según el tipo
    let contentHTML = '';
    
    if (isVideo) {
      // Contenido de video
      contentHTML = `
        <div class="text-center mb-3">
          <h5><i class="fas fa-video text-primary"></i> Video</h5>
        </div>
        <div class="d-flex justify-content-center">
          <video controls class="img-fluid" style="max-width: 100%; max-height: 60vh;">
            <source src="${multimediaSrc}" type="video/${fileExtension}">
            Tu navegador no soporta el elemento de video.
          </video>
        </div>
      `;
    } else if (isAudio) {
      // Contenido de audio
      contentHTML = `
        <div class="text-center mb-3">
          <h5><i class="fas fa-music text-success"></i> Audio</h5>
        </div>
        <div class="d-flex justify-content-center">
          <audio controls class="img-fluid" style="width: 100%; max-width: 500px;">
            <source src="${multimediaSrc}" type="audio/${fileExtension}">
            Tu navegador no soporta el elemento de audio.
          </audio>
        </div>
      `;
    } else if (isYouTube) {
      // Extraer ID de YouTube
      let videoId = '';
      if (multimediaSrc.includes('youtube.com/watch?v=')) {
        videoId = multimediaSrc.split('v=')[1]?.split('&')[0];
      } else if (multimediaSrc.includes('youtu.be/')) {
        videoId = multimediaSrc.split('youtu.be/')[1]?.split('?')[0];
      }
      
      // Contenido de YouTube
      contentHTML = `
        <div class="text-center mb-3">
          <h5><i class="fab fa-youtube text-danger"></i> Video de YouTube</h5>
        </div>
        <div class="d-flex justify-content-center">
          <iframe width="100%" height="315" src="https://www.youtube.com/embed/${videoId}" 
          frameborder="0" allowfullscreen></iframe>
        </div>
      `;
    } else {
      // Contenido genérico o enlace externo
      contentHTML = `
        <div class="text-center p-4">
          <i class="fas fa-external-link-alt fa-4x text-info mb-3"></i>
          <h5>Recurso Externo</h5>
          <p class="text-muted mb-4">
            <strong>Recurso:</strong> ${multimediaTitle || multimediaSrc}<br>
          </p>
          <div class="d-grid gap-2 d-md-flex justify-content-md-center">
            <a href="${multimediaSrc}" target="_blank" class="btn btn-primary btn-lg">
              <i class="fas fa-external-link-alt"></i> Abrir Recurso
            </a>
          </div>
        </div>
      `;
    }
    
    // Configurar contenido
    modalContent.innerHTML = contentHTML;
    
    // Modal footer con botones básicos
    const modalFooter = document.querySelector('#multimediaModal .modal-footer');
    if (modalFooter) {
      modalFooter.innerHTML = `
        <div class="d-flex gap-2 w-100 justify-content-between">
          <div class="d-flex gap-2">
            <a href="${multimediaSrc}" target="_blank" class="btn btn-primary">
              <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
            </a>
          </div>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
        </div>
      `;
    }
    
    // Mostrar modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    if (window.APP_CONFIG && window.APP_CONFIG.DEBUG_MODE) {
      window.APP_CONFIG.log('✅ [MULTIMEDIA-FIX] Modal multimedia mostrado');
    }
  };
} else {
  // Si ya existe la función, verificamos si necesitamos mejorarla
  // pero sin crear un wrapper que cause recursión infinita
  
  if (window.APP_CONFIG && window.APP_CONFIG.DEBUG_MODE) {
    window.APP_CONFIG.log('ℹ️ [MULTIMEDIA-FIX] showMultimediaModal ya está definido');
  }
  
  // Comprobamos si la función original ya maneja eventos
  // En lugar de crear un wrapper, asumimos que la función original ya es correcta
  
  // Esto evita recursión infinita entre el wrapper y la función original
  if (window.APP_CONFIG && window.APP_CONFIG.DEBUG_MODE) {
    window.APP_CONFIG.log('✅ [MULTIMEDIA-FIX] Función multimedia ya existente detectada');
  }
}

// Función auxiliar para verificar elementos multimedia en la página
function checkMultimediaElements() {
  const multimediaElements = document.querySelectorAll('[data-action="show-multimedia-modal"]');
  
  if (window.APP_CONFIG && window.APP_CONFIG.DEBUG_MODE) {
    window.APP_CONFIG.log(`🔍 [MULTIMEDIA-FIX] Elementos multimedia encontrados: ${multimediaElements.length}`);
  }
  
  // Verificar solo en modo depuración
  if (window.APP_CONFIG && window.APP_CONFIG.DEBUG_MODE) {
    multimediaElements.forEach((element, index) => {
      const url = element.dataset.mediaUrl;
      const name = element.dataset.mediaName; 
      
      if (!url) {
        window.APP_CONFIG.warn(`⚠️ [MULTIMEDIA-FIX] Elemento #${index + 1} no tiene URL`);
      }
      
      if (!name) {
        window.APP_CONFIG.warn(`⚠️ [MULTIMEDIA-FIX] Elemento #${index + 1} no tiene nombre`);
      }
    });
  }
  
  return multimediaElements.length;
}

// Verificar que todos los elementos multimedia tienen el manejador de eventos adecuado
function setupMultimediaEventHandlers() {
  // Usar delegación de eventos para manejar clics en elementos multimedia
  document.addEventListener('click', function(e) {
    const multimediaElement = e.target.closest('[data-action="show-multimedia-modal"]');
    if (multimediaElement) {
      e.preventDefault();
      const mediaUrl = multimediaElement.dataset.mediaUrl;
      const mediaName = multimediaElement.dataset.mediaName;
      
      if (mediaUrl && mediaName && typeof window.showMultimediaModal === 'function') {
        console.log('🔍 [MULTIMEDIA-FIX] Invocando showMultimediaModal desde el handler global');
        // Verificación adicional para evitar recursión
        try {
          // Pasar el evento explícitamente
          window.showMultimediaModal(mediaUrl, mediaName, e);
        } catch (error) {
          console.error('❌ [MULTIMEDIA-FIX] Error en showMultimediaModal:', error);
          alert('Error al mostrar multimedia: ' + error.message);
        }
      } else {
        console.error('❌ [MULTIMEDIA-FIX] showMultimediaModal no disponible o datos faltantes');
        alert('Error al mostrar multimedia. Por favor, intente abrir el enlace en una nueva pestaña.');
      }
    }
  });
  
  console.log('✅ [MULTIMEDIA-FIX] Manejadores de eventos multimedia configurados');
}

// Ejecutar verificación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  if (window.APP_CONFIG && window.APP_CONFIG.DEBUG_MODE) {
    window.APP_CONFIG.log('🚀 [MULTIMEDIA-FIX] Iniciando solución para modales multimedia...');
  }
  
  const count = checkMultimediaElements();
  if (count > 0) {
    setupMultimediaEventHandlers();
    if (window.APP_CONFIG && window.APP_CONFIG.DEBUG_MODE) {
      window.APP_CONFIG.log(`✅ [MULTIMEDIA-FIX] Configuración completada para ${count} elementos multimedia`);
    }
  } else if (window.APP_CONFIG && window.APP_CONFIG.DEBUG_MODE) {
    window.APP_CONFIG.log('ℹ️ [MULTIMEDIA-FIX] No se encontraron elementos multimedia en la página');
  }
});

// Solo mostrar mensaje de carga en modo depuración
if (window.APP_CONFIG && window.APP_CONFIG.DEBUG_MODE) {
  window.APP_CONFIG.log('✅ [MULTIMEDIA-FIX] Script de solución multimedia cargado correctamente');
}