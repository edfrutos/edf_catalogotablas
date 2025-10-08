/**
 * MODAL FIXES - SOLUCIÓN DE PROBLEMAS
 * Script para asegurar que las funciones de modal están disponibles
 * en caso de que haya problemas con el archivo principal
 */

// Verificar primero si las funciones ya existen
if (typeof window.showDocumentModal !== 'function') {
  console.warn('⚠️ showDocumentModal no está definido, creando función de emergencia...');

  // Función de emergencia para mostrar documentos en modal
  window.showDocumentModal = function(documentSrc, documentTitle) {
    console.log('🔧 showDocumentModal (EMERGENCY VERSION) llamado con:', { documentSrc, documentTitle });
    
    // Buscar elementos del modal
    const modalElement = document.getElementById('documentModal');
    const modalContent = document.getElementById('documentContent');
    const modalTitle = document.getElementById('documentModalLabel');
    
    if (!modalElement || !modalContent || !modalTitle) {
      console.error('❌ [EMERGENCY] Elementos del modal no encontrados');
      alert('Error: Modal no disponible. Contacte al administrador.');
      return;
    }
    
    // Configurar título
    modalTitle.textContent = documentTitle || 'Documento';
    
    // Mostrar contenido simple
    modalContent.innerHTML = `
      <div class="text-center p-4">
        <i class="fas fa-file-pdf fa-4x text-danger mb-3"></i>
        <h5>Documento</h5>
        <p class="text-muted mb-4">
          <strong>Archivo:</strong> ${documentTitle}<br>
        </p>
        
        <div class="pdf-viewer-container">
          <iframe 
            src="${documentSrc}" 
            width="100%" 
            height="500" 
            style="border: 1px solid #dee2e6; border-radius: 8px;">
          </iframe>
        </div>
      </div>
    `;
    
    // Modal footer con botones básicos
    const modalFooter = document.querySelector('#documentModal .modal-footer');
    if (modalFooter) {
      modalFooter.innerHTML = `
        <div class="d-flex gap-2 w-100 justify-content-between">
          <div class="d-flex gap-2">
            <a href="${documentSrc}" target="_blank" class="btn btn-primary">
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
    
    console.log('✅ [EMERGENCY] Modal de documento mostrado');
  };
}

if (typeof window.showMultimediaModal !== 'function') {
  console.warn('⚠️ showMultimediaModal no está definido, creando función de emergencia...');
  
  // Función de emergencia para mostrar multimedia en modal
  window.showMultimediaModal = function(multimediaSrc, multimediaTitle, e) {
    console.log('🔧 showMultimediaModal (EMERGENCY VERSION) llamado con:', { multimediaSrc, multimediaTitle });
    
    // Prevenir que URLs se abran en navegador directamente
    if (e) {
      e.preventDefault();
    }
    
    // Buscar elementos del modal
    const modalElement = document.getElementById('multimediaModal');
    const modalContent = document.getElementById('multimediaContent');
    const modalTitle = document.getElementById('multimediaModalLabel');
    
    if (!modalElement || !modalContent || !modalTitle) {
      console.error('❌ [EMERGENCY] Elementos del modal multimedia no encontrados');
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
    
    console.log('✅ [EMERGENCY] Modal multimedia mostrado');
  };
}

if (typeof window.showImageModal !== 'function') {
  console.warn('⚠️ showImageModal no está definido, creando función de emergencia...');
  
  // Función de emergencia para mostrar imágenes en modal
  window.showImageModal = function(imageSrc, imageTitle) {
    console.log('🔧 showImageModal (EMERGENCY VERSION) llamado con:', { imageSrc, imageTitle });
    
    // Buscar elementos del modal
    const modalElement = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('imageModalLabel');
    
    if (!modalElement || !modalImage || !modalTitle) {
      console.error('❌ [EMERGENCY] Elementos del modal de imagen no encontrados');
      alert('Error: Modal de imagen no disponible. Contacte al administrador.');
      return;
    }
    
    // Configurar título e imagen
    modalTitle.textContent = imageTitle || 'Imagen';
    modalImage.src = imageSrc;
    modalImage.alt = imageTitle || 'Imagen';
    
    // Manejar errores de carga de imagen
    modalImage.onerror = function() {
      console.error('[EMERGENCY] Error cargando imagen:', imageSrc);
      modalImage.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlbiBubyBlbmNvbnRyYWRhPC90ZXh0Pjwvc3ZnPg==';
      modalTitle.textContent = 'Imagen no encontrada';
    };
    
    // Mostrar modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    console.log('✅ [EMERGENCY] Modal de imagen mostrado');
  };
}

// Informar en la consola que el script de emergencia está listo
console.log('✅ [EMERGENCY MODAL FIXES] Script de emergencia cargado correctamente');
console.log('🔍 Funciones disponibles después de las correcciones:');
console.log('  - showDocumentModal:', typeof window.showDocumentModal);
console.log('  - showMultimediaModal:', typeof window.showMultimediaModal);
console.log('  - showImageModal:', typeof window.showImageModal);