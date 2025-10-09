/**
 * MODAL FUNCTIONS UNIFIED - VERSIÓN FINAL FUNCIONAL
 * Archivo unificado con todas las funcionalidades de modal
 * Fecha: 4 de Enero de 2025
 * Estado: ✅ FUNCIONAL COMPLETAMENTE
 */

// Sistema de logging optimizado para producción
if (typeof window.DEBUG_MODE === 'undefined') {
  window.DEBUG_MODE = false; // Desactivado en producción
}
if (typeof window.modalLog === 'undefined') {
  window.modalLog = () => {}; // No generar logs en producción
}
if (typeof window.modalLogError === 'undefined') {
  window.modalLogError = console.error; // Siempre mostrar errores
}

// Evitar redeclaración usando namespace único
if (!window.modalUnifiedLog) {
  window.modalUnifiedLog = () => {}; // No generar logs en producción
}
if (!window.modalUnifiedLogError) {
  window.modalUnifiedLogError = console.error;
}
const log = window.modalUnifiedLog;
const logError = window.modalUnifiedLogError;

// ============================================================================
// DETECCIÓN DE ENTORNO
// ============================================================================

// Función para detectar entorno (evita declaración de variables globales)
function getEnvironmentType() {
  // isPyWebView es declarada por pywebview_compatibility.js, la usamos directamente
  if (typeof window.isPyWebView !== 'undefined') {
    return !window.isPyWebView;
  } else {
    // Fallback si pywebview_compatibility.js no se ha cargado aún
    return true;
  }
}



// ============================================================================
// FUNCIONES DE MODAL UNIFICADAS
// ============================================================================

// Función para mostrar documentos en modal (PDF, Markdown, Texto)
// Función auxiliar para determinar el título según la extensión del archivo
function getDocumentTitle(fileExtension) {
  if (fileExtension === 'pdf') {
    return 'Ver PDF';
  } else if (fileExtension === 'md') {
    return 'Ver Markdown';
  } else if (['doc', 'docx'].includes(fileExtension)) {
    return 'Ver Documento';
  } else if (['xls', 'xlsx'].includes(fileExtension)) {
    return 'Ver Hoja de Cálculo';
  } else if (['ppt', 'pptx'].includes(fileExtension)) {
    return 'Ver Presentación';
  }
  return 'Documento';
}

// Función auxiliar para limpiar URLs malformadas
function cleanDocumentUrl(documentSrc) {
  let cleanDocumentSrc = documentSrc;
  if (documentSrc.includes('/static/uploads//admin/s3/')) {
    cleanDocumentSrc = documentSrc.replace('/static/uploads//admin/s3/', '/admin/s3/');
    log("[MODAL-UNIFIED] 🔧 URL limpiada:", cleanDocumentSrc);
  } else if (documentSrc.includes('/imagenes_subidas//admin/s3/')) {
    cleanDocumentSrc = documentSrc.replace('/imagenes_subidas//admin/s3/', '/admin/s3/');
    log("[MODAL-UNIFIED] 🔧 URL limpiada:", cleanDocumentSrc);
  }
  return cleanDocumentSrc;
}

// Función auxiliar para detectar si un archivo está en S3
function isS3Document(documentSrc) {
  return documentSrc.includes('s3.amazonaws.com') || 
         documentSrc.includes('edf-catalogo-tablas.s3') || 
         documentSrc.includes('/admin/s3/') || 
         documentSrc.includes('/s3/');
}

// Función para mostrar contenido PDF desde S3
function showPdfS3Content(modalContent, documentSrc, documentTitle, proxyUrl) {
  // Aumentar la altura del iframe para aprovechar mejor el espacio del modal
  modalContent.innerHTML = `
    <div class="text-center p-3">
      <i class="fas fa-file-pdf fa-3x text-danger mb-2"></i>
      <h5>Documento PDF</h5>
      <p class="text-muted mb-3">
        <strong>Archivo:</strong> ${documentTitle}<br>
        <strong>Tipo:</strong> PDF<br>
        <strong>Ubicación:</strong> S3
      </p>
      
      <div class="pdf-viewer-container">
        <iframe 
          src="${proxyUrl}" 
          width="100%" 
          height="650" 
          style="border: 1px solid #dee2e6; border-radius: 8px;"

          onerror="console.error('[MODAL-UNIFIED] ❌ Error cargando PDF en iframe')">
        </iframe>
      </div>
    </div>
  `;
  
  // Insertar botones en el modal-footer
  setupDocumentButtons(documentSrc, documentTitle, 's3');
  
  // Ajustar el tamaño del modal para PDFs
  const modalDialog = document.querySelector('#documentModal .modal-dialog');
  if (modalDialog) {
    modalDialog.style.maxWidth = '900px';
    modalDialog.style.width = '85%';
  }
  
  const modalContentElement = document.querySelector('#documentModal .modal-content');
  if (modalContentElement) {
    modalContentElement.style.height = '850px';
    modalContentElement.style.maxHeight = '90vh';
  }
}

// Función para mostrar archivos Excel desde S3
function showExcelS3Content(modalContent, documentSrc, documentTitle, proxyUrl) {
  // Obtener la URL pública para archivos de S3
  let publicViewUrl = documentSrc;
  if (documentSrc.includes('/admin/s3/')) {
    // Convertir URL interna a URL pública para visualización externa
    const fileName = documentSrc.split('/').pop();
    publicViewUrl = `https://edf-catalogo-tablas.s3.eu-central-1.amazonaws.com/${fileName}`;
  }
  
  // Preparar el contenido
  modalContent.innerHTML = `
    <div class="text-center p-3">
      <i class="fas fa-file-excel fa-3x text-success mb-2"></i>
      <h5>Documento Excel</h5>
      <p class="text-muted mb-3">
        <strong>Archivo:</strong> ${documentTitle}<br>
        <strong>Tipo:</strong> XLSX<br>
        <strong>Ubicación:</strong> S3
      </p>
      
      <div class="alert alert-info mt-3">
        <i class="fas fa-info-circle"></i>
        <strong>Información:</strong> Para visualizar este tipo de archivo correctamente, use el botón para abrirlo en una nueva pestaña o descargarlo.
      </div>
      
      <div class="excel-viewer-container">
        <div class="text-center mt-4">
          <i class="fas fa-file-excel fa-5x text-success mb-3"></i>
          <h4>Archivo Excel</h4>
          <p>Puede utilizar los botones a continuación para abrir o descargar este archivo.</p>
          <div class="d-grid gap-2 d-md-flex justify-content-md-center mt-4">
            <a href="${proxyUrl}" target="_blank" class="btn btn-success btn-lg">
              <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
            </a>
            <button type="button" class="btn btn-outline-success btn-lg" data-action="download-s3-file" data-document-src="${documentSrc}" data-document-title="${documentTitle}">
              <i class="fas fa-download"></i> Descargar
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Insertar botones en el modal-footer
  setupDocumentButtons(documentSrc, documentTitle, 's3');
  
  // Ajustar el tamaño del modal para archivos Excel
  const modalDialog = document.querySelector('#documentModal .modal-dialog');
  if (modalDialog) {
    modalDialog.style.maxWidth = '900px';
    modalDialog.style.width = '85%';
  }
  
  const modalContentElement = document.querySelector('#documentModal .modal-content');
  if (modalContentElement) {
    modalContentElement.style.height = '850px';
    modalContentElement.style.maxHeight = '90vh';
  }
}

// Función para mostrar archivos Excel locales
function showExcelLocalContent(modalContent, documentSrc, documentTitle) {
  // Convertir ruta local a URL absoluta para Office Online Viewer
  const absoluteUrl = new URL(documentSrc, window.location.origin).href;
  
  modalContent.innerHTML = `
    <div class="text-center p-3">
      <i class="fas fa-file-excel fa-3x text-success mb-2"></i>
      <h5>Documento Excel</h5>
      <p class="text-muted mb-3">
        <strong>Archivo:</strong> ${documentTitle}<br>
        <strong>Tipo:</strong> XLSX<br>
        <strong>Ubicación:</strong> Local
      </p>
      
      <div class="alert alert-info mt-3">
        <i class="fas fa-info-circle"></i>
        <strong>Información:</strong> Para visualizar este tipo de archivo correctamente, use el botón para abrirlo en una nueva pestaña o descargarlo.
      </div>
      
      <div class="excel-viewer-container">
        <div class="text-center mt-4">
          <i class="fas fa-file-excel fa-5x text-success mb-3"></i>
          <h4>Archivo Excel</h4>
          <p>Puede utilizar los botones a continuación para abrir o descargar este archivo.</p>
          <div class="d-grid gap-2 d-md-flex justify-content-md-center mt-4">
            <a href="${documentSrc}" target="_blank" class="btn btn-success btn-lg">
              <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
            </a>
            <button type="button" class="btn btn-outline-success btn-lg" data-action="download-local-file" data-document-src="${documentSrc}" data-document-title="${documentTitle}">
              <i class="fas fa-download"></i> Descargar
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Insertar botones en el modal-footer
  setupDocumentButtons(documentSrc, documentTitle, 'local');
  
  // Ajustar el tamaño del modal para archivos Excel
  const modalDialog = document.querySelector('#documentModal .modal-dialog');
  if (modalDialog) {
    modalDialog.style.maxWidth = '900px';
    modalDialog.style.width = '85%';
  }
  
  const modalContentElement = document.querySelector('#documentModal .modal-content');
  if (modalContentElement) {
    modalContentElement.style.height = '850px';
    modalContentElement.style.maxHeight = '90vh';
  }
}

// Función para mostrar otros tipos de contenido desde S3
function showOtherS3Content(modalContent, documentSrc, documentTitle, fileExtension) {
  modalContent.innerHTML = `
    <div class="text-center p-4">
      <i class="fas fa-file fa-4x text-primary mb-3"></i>
      <h5>Documento S3</h5>
      <p class="text-muted mb-4">
        <strong>Archivo:</strong> ${documentTitle}<br>
        <strong>Tipo:</strong> ${fileExtension?.toUpperCase() || 'Desconocido'}<br>
        <strong>Ubicación:</strong> S3
      </p>
    </div>
  `;
  
  // Insertar botones en el modal-footer
  setupDocumentButtons(documentSrc, documentTitle, 's3');
}

// Función para mostrar contenido PDF local
function showPdfLocalContent(modalContent, documentSrc, documentTitle) {
  // Aumentar la altura del iframe para aprovechar mejor el espacio del modal
  modalContent.innerHTML = `
    <div class="text-center p-3">
      <i class="fas fa-file-pdf fa-3x text-danger mb-2"></i>
      <h5>Documento PDF</h5>
      <p class="text-muted mb-3">
        <strong>Archivo:</strong> ${documentTitle}<br>
        <strong>Tipo:</strong> PDF<br>
        <strong>Ubicación:</strong> Local
      </p>
      
      <div class="pdf-viewer-container">
        <iframe 
          src="${documentSrc}" 
          width="100%" 
          height="650" 
          style="border: 1px solid #dee2e6; border-radius: 8px;"

          onerror="console.error('[MODAL-UNIFIED] ❌ Error cargando PDF local en iframe')">
        </iframe>
      </div>
    </div>
  `;
  
  // Insertar botones en el modal-footer
  setupDocumentButtons(documentSrc, documentTitle, 'local');
  
  // Ajustar el tamaño del modal para PDFs
  const modalDialog = document.querySelector('#documentModal .modal-dialog');
  if (modalDialog) {
    modalDialog.style.maxWidth = '900px';
    modalDialog.style.width = '85%';
  }
  
  const modalContentElement = document.querySelector('#documentModal .modal-content');
  if (modalContentElement) {
    modalContentElement.style.height = '850px';
    modalContentElement.style.maxHeight = '90vh';
  }
}

// Función para mostrar otros tipos de contenido local
function showOtherLocalContent(modalContent, documentSrc, documentTitle, fileExtension) {
  modalContent.innerHTML = `
    <div class="text-center p-4">
      <i class="fas fa-file fa-4x text-primary mb-3"></i>
      <h5>Documento Local</h5>
      <p class="text-muted mb-4">
        <strong>Archivo:</strong> ${documentTitle}<br>
        <strong>Tipo:</strong> ${fileExtension?.toUpperCase() || 'Desconocido'}<br>
        <strong>Ubicación:</strong> Local
      </p>
      <div class="alert alert-info mt-3">
        <i class="fas fa-info-circle"></i>
        <strong>Información:</strong> Para visualizar este tipo de archivo, use el botón para abrirlo en una nueva pestaña.
      </div>
    </div>
  `;
  
  // Insertar botones en el modal-footer
  setupDocumentButtons(documentSrc, documentTitle, 'local');
}

// Función para configurar botones del modal de documento
function setupDocumentButtons(documentSrc, documentTitle, sourceType) {
  const modalFooter = document.querySelector('#documentModal .modal-footer');
  if (!modalFooter) return;
  
  const actionType = sourceType === 's3' ? 'download-s3-file' : 'download-local-file';
  
  modalFooter.innerHTML = `
    <div class="d-flex gap-2 w-100 justify-content-between">
      <div class="d-flex gap-2">
        <a href="${documentSrc}" target="_blank" class="btn btn-primary">
          <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
        </a>
        <button type="button" class="btn btn-outline-primary" data-action="${actionType}" data-document-src="${documentSrc}" data-document-title="${documentTitle}">
          <i class="fas fa-download"></i> Descargar
        </button>
      </div>
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
    </div>
  `;
}

function showDocumentModal(documentSrc, documentTitle) {
  log("[MODAL-UNIFIED] 📄 showDocumentModal llamado con:", { documentSrc, documentTitle });
  
  // Buscar elementos del modal
  const modalElement = document.getElementById('documentModal');
  const modalContent = document.getElementById('documentContent');
  const modalTitle = document.getElementById('documentModalLabel');
  
  if (!modalElement || !modalContent || !modalTitle) {
    logError("[MODAL-UNIFIED] ❌ Elementos del modal no encontrados");
    alert("Error: Modal no disponible");
    return;
  }
  
  // Configurar título genérico basado en el tipo de archivo
  const fileExtension = documentSrc.split('.').pop()?.toLowerCase();
  modalTitle.textContent = getDocumentTitle(fileExtension);
  
  // Log de la extensión detectada
  log("[MODAL-UNIFIED] 🔍 Extensión detectada:", fileExtension);
  
  // Log adicional para ayudar en la depuración de archivos Excel
  if (['xls', 'xlsx'].includes(fileExtension)) {
    log("[MODAL-UNIFIED] 📊 Archivo Excel detectado:", documentSrc);
  }
  
  // Mostrar modal primero
  const modal = new bootstrap.Modal(modalElement);
  modal.show();
  
  // Mostrar loading
  showLoadingInModal(modalContent);
  
  // Limpiar URL si contiene rutas malformadas ANTES de detectar el tipo
  const cleanDocumentSrc = cleanDocumentUrl(documentSrc);
  
  // DETECCIÓN HÍBRIDA S3/LOCAL
  const isS3File = isS3Document(cleanDocumentSrc);
  log("[MODAL-UNIFIED] 🔍 URL del documento:", documentSrc);
  log("[MODAL-UNIFIED] 🔍 URL limpia:", cleanDocumentSrc);
  log("[MODAL-UNIFIED] 🔍 ¿Es archivo S3?:", isS3File);
  
  if (isS3File) {
    log("[MODAL-UNIFIED] 🔧 Archivo S3 detectado, usando proxy...");
    
    if (fileExtension === 'pdf') {
      // PDF S3 - usar iframe directo (más confiable)
      const proxyUrl = cleanDocumentSrc.replace(
        'https://edf-catalogo-tablas.s3.eu-central-1.amazonaws.com/',
        '/admin/s3/'
      );
      
      // Mostrar PDF S3
      showPdfS3Content(modalContent, documentSrc, documentTitle, proxyUrl);
      
    } else if (['xls', 'xlsx'].includes(fileExtension)) {
      // Excel S3 - usar Office Online Viewer
      const proxyUrl = cleanDocumentSrc.replace(
        'https://edf-catalogo-tablas.s3.eu-central-1.amazonaws.com/',
        '/admin/s3/'
      );
      
      // Log mejorado para depuración
      log("[MODAL-UNIFIED] 📊 Mostrando archivo Excel S3:", documentSrc);
      log("[MODAL-UNIFIED] 🔗 URL de proxy:", proxyUrl);
      
      // Mostrar Excel S3
      showExcelS3Content(modalContent, documentSrc, documentTitle, proxyUrl);
      
    } else if (fileExtension === 'md') {
      // Markdown S3
      showMarkdownInModal(documentSrc, documentTitle);
      
    } else if (['txt', 'log'].includes(fileExtension)) {
      // Texto S3
      showTextInModal(documentSrc, documentTitle);
      
    } else {
      // Otros tipos S3
      showOtherS3Content(modalContent, documentSrc, documentTitle, fileExtension);
    }
    
  } else {
    // Archivo local
    log("[MODAL-UNIFIED] 🔧 Archivo local detectado...");
    
    if (fileExtension === 'pdf') {
      // PDF local - iframe directo
      showPdfLocalContent(modalContent, documentSrc, documentTitle);
      
    } else if (['xls', 'xlsx'].includes(fileExtension)) {
      // Excel local - usar Office Online Viewer
      log("[MODAL-UNIFIED] 📊 Mostrando archivo Excel local:", documentSrc);
      showExcelLocalContent(modalContent, documentSrc, documentTitle);
      
    } else if (fileExtension === 'md') {
      // Markdown local
      showMarkdownInModal(documentSrc, documentTitle);
      
    } else if (['txt', 'log'].includes(fileExtension)) {
      // Texto local
      showTextInModal(documentSrc, documentTitle);
      
    } else {
      // Otros tipos locales
      showOtherLocalContent(modalContent, documentSrc, documentTitle, fileExtension);
    }
  }
  
  log("[MODAL-UNIFIED] ✅ Modal de documento configurado");
}

// Función para mostrar Markdown en modal
function showMarkdownInModal(markdownUrl, markdownTitle) {
  log("[MODAL-UNIFIED] 📝 showMarkdownInModal llamado con:", { markdownUrl, markdownTitle });
  
  const modalContent = document.getElementById('documentContent');
  if (!modalContent) return;
  
  // Limpiar URL si contiene rutas malformadas
  let cleanMarkdownUrl = markdownUrl;
  if (markdownUrl.includes('/static/uploads//admin/s3/')) {
    cleanMarkdownUrl = markdownUrl.replace('/static/uploads//admin/s3/', '/admin/s3/');
    log("[MODAL-UNIFIED] 🔧 URL de Markdown limpiada:", cleanMarkdownUrl);
  } else if (markdownUrl.includes('/imagenes_subidas//admin/s3/')) {
    cleanMarkdownUrl = markdownUrl.replace('/imagenes_subidas//admin/s3/', '/admin/s3/');
    log("[MODAL-UNIFIED] 🔧 URL de Markdown limpiada:", cleanMarkdownUrl);
  }
  
  // Determinar URL para fetch
  let fetchUrl = cleanMarkdownUrl;
  const isS3File = cleanMarkdownUrl.includes('s3.amazonaws.com') || cleanMarkdownUrl.includes('edf-catalogo-tablas.s3') || cleanMarkdownUrl.includes('/admin/s3/') || cleanMarkdownUrl.includes('/s3/');
  
  if (isS3File) {
    fetchUrl = cleanMarkdownUrl.replace(
      'https://edf-catalogo-tablas.s3.eu-central-1.amazonaws.com/',
      '/admin/s3/'
    );
  } else if (cleanMarkdownUrl.includes('/static/uploads/')) {
    // Convertir ruta de archivo local a ruta de Flask para Markdown
    const filename = cleanMarkdownUrl.split('/').pop();
    fetchUrl = `/catalogs/view_markdown/${filename}`;
  }
  
  // Cargar Markdown
  log("[MODAL-UNIFIED] 🔍 Fetching URL:", fetchUrl);
  fetch(fetchUrl)
    .then(response => {
      log("[MODAL-UNIFIED] 🔍 Response status:", response.status);
      log("[MODAL-UNIFIED] 🔍 Response ok:", response.ok);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.text();
    })
    .then(markdownText => {
      log("[MODAL-UNIFIED] 🔍 Markdown text length:", markdownText.length);
      log("[MODAL-UNIFIED] 🔍 Markdown preview:", markdownText.substring(0, 100));
      // Renderizado simple de Markdown
      const htmlContent = markdownText
        .replace(/^### (.*$)/gim, "<h3>$1</h3>")
        .replace(/^## (.*$)/gim, "<h2>$1</h2>")
        .replace(/^# (.*$)/gim, "<h1>$1</h1>")
        .replace(/\*\*(.*)\*\*/gim, "<strong>$1</strong>")
        .replace(/\*(.*)\*/gim, "<em>$1</em>")
        .replace(/\n/gim, "<br>");
      
      modalContent.innerHTML = `
        <div class="text-center p-4">
          <i class="fas fa-file-code fa-4x text-info mb-3"></i>
          <h5>Documento Markdown</h5>
          <p class="text-muted mb-4">
            <strong>Archivo:</strong> ${markdownTitle}<br>
            <strong>Tipo:</strong> Markdown<br>
            <strong>Ubicación:</strong> ${isS3File ? 'S3' : 'Local'}
          </p>
          
          <div class="markdown-content-wrapper" style="max-height: 35vh; overflow-y: auto; padding: 15px; background: #f8f9fa; border-radius: 8px; text-align: left; margin-bottom: 15px;"
            <div class="markdown-rendered">
              ${htmlContent}
            </div>
          </div>
        </div>
      `;
      
      // Insertar botones en el modal-footer
      const modalFooter = document.querySelector('#documentModal .modal-footer');
      if (modalFooter) {
        modalFooter.innerHTML = `
          <div class="d-flex gap-2 w-100 justify-content-between">
            <div class="d-flex gap-2">
              <a href="${markdownUrl}" target="_blank" class="btn btn-primary">
                <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
              </a>
              <button type="button" class="btn btn-outline-primary" onclick="downloadMarkdownFile('${markdownUrl}', '${markdownTitle}')">
                <i class="fas fa-download"></i> Descargar
              </button>
            </div>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
          </div>
        `;
      }
      
    })
    .catch(error => {
      log("[MODAL-UNIFIED] ❌ Error cargando Markdown:", error);
      modalContent.innerHTML = `
        <div class="text-center p-4">
          <i class="fas fa-exclamation-triangle fa-4x text-danger mb-3"></i>
          <h5>Error al cargar Markdown</h5>
          <p class="text-muted">${error.message}</p>
          <p class="text-danger small">URL intentada: ${fetchUrl}</p>
        </div>
      `;
      
      // Insertar botones en el modal-footer
      const modalFooter = document.querySelector('#documentModal .modal-footer');
      if (modalFooter) {
        modalFooter.innerHTML = `
          <div class="d-flex gap-2 w-100 justify-content-between">
            <div class="d-flex gap-2">
              <a href="${markdownUrl}" target="_blank" class="btn btn-primary">
                <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
              </a>
              <button type="button" class="btn btn-outline-primary" onclick="downloadMarkdownFile('${markdownUrl}', '${markdownTitle}')">
                <i class="fas fa-download"></i> Descargar
              </button>
            </div>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
          </div>
        `;
      }
    });
}

// Función para mostrar los botones del modal de texto
function setupTextModalButtons(modalFooter, fileUrl, fileTitle) {
  if (!modalFooter) return;
  
  modalFooter.innerHTML = `
    <div class="d-flex gap-2 w-100 justify-content-between">
      <div class="d-flex gap-2">
        <a href="${fileUrl}" target="_blank" class="btn btn-primary">
          <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
        </a>
        <button type="button" class="btn btn-outline-primary" data-action="download-local-file" data-document-src="${fileUrl}" data-document-title="${fileTitle}">
          <i class="fas fa-download"></i> Descargar
        </button>
      </div>
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
    </div>
  `;
}

// Función para mostrar el contenido del texto
function displayTextContent(modalContent, content, location, finalUrl, textTitle) {
  modalContent.innerHTML = `
    <div class="text-center p-4">
      <i class="fas fa-file-alt fa-4x text-primary mb-3"></i>
      <h5>Documento de Texto</h5>
      <p class="text-muted mb-4">
        <strong>Archivo:</strong> ${textTitle}<br>
        <strong>Tipo:</strong> Texto<br>
        <strong>Ubicación:</strong> ${location}
      </p>
      
      <div class="text-content-wrapper" style="max-height: 35vh; overflow-y: auto; padding: 15px; background: #f8f9fa; border-radius: 8px; text-align: left; margin-bottom: 15px;"
        <pre style="white-space: pre-wrap; font-family: 'Courier New', monospace;">${content}</pre>
      </div>
    </div>
  `;
  
  // Insertar botones en el modal-footer
  const modalFooter = document.querySelector('#documentModal .modal-footer');
  setupTextModalButtons(modalFooter, finalUrl, textTitle);
}

// Función para mostrar error al cargar texto
function showTextLoadError(modalContent, textTitle, isS3Failure = false) {
  const errorMessage = isS3Failure ?
    "No se pudo cargar el archivo desde S3 ni desde almacenamiento local." :
    "No se pudo cargar el archivo.";
    
  modalContent.innerHTML = `
    <div class="text-center p-4">
      <i class="fas fa-exclamation-triangle fa-4x text-danger mb-3"></i>
      <h5>Error al cargar texto</h5>
      <p class="text-muted">${errorMessage}</p>
      <p class="text-muted"><strong>Archivo:</strong> ${textTitle}</p>
    </div>
  `;
}

// Función para intentar cargar desde una URL
function loadTextFromUrl(url, location, modalContent, textTitle) {
  return fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.text();
    })
    .then(textContent => {
      displayTextContent(modalContent, textContent, location, url, textTitle);
      return true; // Éxito - devuelve boolean
    })
    .catch(error => {
      log(`[MODAL-UNIFIED] ❌ Error cargando desde ${location}:`, error);
      return false; // Fallo - devuelve boolean
    });
}

// Función para cargar texto desde S3 y hacer fallback a local si es necesario
function loadTextFromS3(textUrl, textTitle, modalContent) {
  log("[MODAL-UNIFIED] 🔄 Intentando cargar desde S3...");
  return loadTextFromUrl(textUrl, "S3", modalContent, textTitle)
    .then(success => {
      if (!success) {
        // Fallback a local
        const filename = textUrl.split('/').pop();
        const localUrl = `/imagenes_subidas/${filename}`;
        log("[MODAL-UNIFIED] 🔄 Fallback a local:", localUrl);
        return loadTextFromUrl(localUrl, "Local", modalContent, textTitle);
      }
      return Promise.resolve(true);
    });
}

// Función para cargar texto desde fuente local
function loadTextFromLocal(textUrl, textTitle, modalContent) {
  return loadTextFromUrl(textUrl, "Local", modalContent, textTitle);
}

// Función para mostrar texto en modal
function showTextInModal(textUrl, textTitle) {
  log("[MODAL-UNIFIED] 📄 showTextInModal llamado con:", { textUrl, textTitle });
  
  const modalContent = document.getElementById('documentContent');
  if (!modalContent) return;
  
  // Determinar estrategia de carga basada en la URL
  const loadStrategy = textUrl.includes('/admin/s3/') 
    ? loadTextFromS3(textUrl, textTitle, modalContent) 
    : loadTextFromLocal(textUrl, textTitle, modalContent);
  
  // Manejo de errores común
  loadStrategy.then(success => {
    if (!success) {
      // El parámetro isS3Failure será true si estamos en la ruta S3
      showTextLoadError(modalContent, textTitle, textUrl.includes('/admin/s3/'));
    }
  });
}

// Función para verificar si una imagen existe
async function checkImageExists(imageSrc) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = imageSrc;
  });
}

// Función para limpiar imágenes y multimedia rotos en la página
// eslint-disable-next-line no-unused-vars
async function cleanupBrokenImages() {
  log("[MODAL-UNIFIED] 🧹 Iniciando limpieza de imágenes y multimedia rotos...");
  
  const images = document.querySelectorAll('img[src*="/admin/s3/"], img[src*="/s3/"]');
  const videos = document.querySelectorAll('video[src*="/admin/s3/"], video[src*="/s3/"]');
  const audios = document.querySelectorAll('audio[src*="/admin/s3/"], audio[src*="/s3/"]');
  let brokenCount = 0;
  
  // Procesar imágenes
  for (const img of images) {
    const exists = await checkImageExists(img.src);
    if (!exists) {
      log("[MODAL-UNIFIED] 🗑️ Imagen rota encontrada:", img.src);
      brokenCount++;
      
      // Reemplazar con imagen placeholder
      img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzUiIGhlaWdodD0iMzUiIHZpZXdCb3g9IjAgMCAzNSAzNSIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjM1IiBoZWlnaHQ9IjM1IiBmaWxsPSIjRjVGNUY1Ii8+CjxwYXRoIGQ9Ik0xNy41IDEwQzE5LjQzIDEwIDIxIDExLjU3IDIxIDEzLjVDMjEgMTUuNDMgMTkuNDMgMTcgMTcuNSAxN0MxNS41NyAxNyAxNCAxNS40MyAxNCAxMy41QzE0IDExLjU3IDE1LjU3IDEwIDE3LjUgMTBaIiBmaWxsPSIjQ0NDQ0NDIi8+CjxwYXRoIGQ9Ik0xMCAyMkMyMCAyMiAyMCAyMiAyMCAyMkgxMEMxMCAyMiAxMCAyMiAxMCAyMloiIGZpbGw9IiNDQ0NDQ0MiLz4KPC9zdmc+';
      img.style.opacity = '0.5';
      img.alt = 'Imagen no encontrada';
      img.title = 'Imagen no encontrada en S3';
    }
  }
  
  // Procesar videos
  for (const video of videos) {
    const exists = await checkImageExists(video.src);
    if (!exists) {
      log("[MODAL-UNIFIED] 🗑️ Video roto encontrado:", video.src);
      brokenCount++;
      
      // Reemplazar con placeholder
      video.style.display = 'none';
      const placeholder = document.createElement('div');
      placeholder.innerHTML = `
        <div style="width: 100%; height: 200px; background: #f5f5f5; border: 2px dashed #ccc; display: flex; align-items: center; justify-content: center; flex-direction: column;">
          <i class="fas fa-video-slash fa-3x text-muted mb-2"></i>
          <span class="text-muted">Video no encontrado</span>
        </div>
      `;
      video.parentNode.insertBefore(placeholder, video);
    }
  }
  
  // Procesar audios
  for (const audio of audios) {
    const exists = await checkImageExists(audio.src);
    if (!exists) {
      log("[MODAL-UNIFIED] 🗑️ Audio roto encontrado:", audio.src);
      brokenCount++;
      
      // Reemplazar con placeholder
      audio.style.display = 'none';
      const placeholder = document.createElement('div');
      placeholder.innerHTML = `
        <div style="width: 100%; height: 60px; background: #f5f5f5; border: 2px dashed #ccc; display: flex; align-items: center; justify-content: center;">
          <i class="fas fa-music-slash fa-2x text-muted me-2"></i>
          <span class="text-muted">Audio no encontrado</span>
        </div>
      `;
      audio.parentNode.insertBefore(placeholder, audio);
    }
  }
  
  if (brokenCount > 0) {
    log(`[MODAL-UNIFIED] ✅ Limpieza completada: ${brokenCount} archivos rotos reemplazados`);
  } else {
    log("[MODAL-UNIFIED] ✅ No se encontraron archivos rotos");
  }
}

// Función para mostrar imágenes en modal
function showImageModal(imageSrc, imageTitle) {
  log("[MODAL-UNIFIED] 🖼️ showImageModal llamado con:", { imageSrc, imageTitle });
  
  const modalElement = document.getElementById('imageModal');
  const modalImage = document.getElementById('modalImage');
  const modalTitle = document.getElementById('imageModalLabel');
  
  if (!modalElement || !modalImage || !modalTitle) {
    console.error("[MODAL-UNIFIED] ❌ Elementos del modal de imagen no encontrados");
    return;
  }
  
  // Configurar título e imagen
  modalTitle.textContent = imageTitle || 'Imagen';
  modalImage.src = imageSrc;
  modalImage.alt = imageTitle || 'Imagen';
  
  // Manejar errores de carga de imagen
  modalImage.onerror = function() {
    log("[MODAL-UNIFIED] ❌ Error cargando imagen:", imageSrc);
    modalImage.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlbiBubyBlbmNvbnRyYWRhPC90ZXh0Pjwvc3ZnPg==';
    modalImage.alt = 'Imagen no encontrada';
    modalTitle.textContent = 'Imagen no encontrada';
  };
  
  modalImage.onload = function() {
    log("[MODAL-UNIFIED] ✅ Imagen cargada correctamente:", imageSrc);
    
    // Ajustar el tamaño del modal basado en el tamaño de la imagen
    setTimeout(() => {
      const imgWidth = modalImage.naturalWidth;
      const imgHeight = modalImage.naturalHeight;
      
      // Ajustar el tamaño del modal para imágenes más grandes
      const modalDialog = document.querySelector('#imageModal .modal-dialog');
      if (modalDialog) {
        if (imgWidth > 800 || imgHeight > 600) {
          modalDialog.style.maxWidth = '850px';
          modalDialog.style.width = '80%';
        } else {
          modalDialog.style.maxWidth = '700px';
          modalDialog.style.width = '70%';
        }
      }
      
      const modalContentElement = document.querySelector('#imageModal .modal-content');
      if (modalContentElement) {
        if (imgHeight > 600) {
          modalContentElement.style.height = '700px';
          modalContentElement.style.maxHeight = '85vh';
        } else {
          modalContentElement.style.height = '550px';
          modalContentElement.style.maxHeight = '70vh';
        }
      }
    }, 100);
  };
  
  // Mostrar modal
  const modal = new bootstrap.Modal(modalElement);
  modal.show();
  
  log("[MODAL-UNIFIED] ✅ Modal de imagen mostrado");
}

// Función auxiliar para mostrar el spinner de carga en el modal
function showLoadingInModal(modalContent) {
  modalContent.innerHTML = `
    <div class="text-center p-4">
      <div class="spinner-border text-primary mb-3" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
      <h5>Cargando Documento</h5>
      <p class="text-muted">Preparando visualización...</p>
    </div>
  `;
}

// Función para limpiar URLs de multimedia
function cleanMultimediaUrl(multimediaSrc) {
  let cleanSrc = multimediaSrc;
  
  if (multimediaSrc.includes('/static/uploads//admin/s3/')) {
    cleanSrc = multimediaSrc.replace('/static/uploads//admin/s3/', '/admin/s3/');
    log("[MODAL-UNIFIED] 🔧 URL de multimedia limpiada:", cleanSrc);
  } else if (multimediaSrc.includes('/imagenes_subidas//admin/s3/')) {
    cleanSrc = multimediaSrc.replace('/imagenes_subidas//admin/s3/', '/admin/s3/');
    log("[MODAL-UNIFIED] 🔧 URL de multimedia limpiada:", cleanSrc);
  }
  
  return cleanSrc;
}

// Función para determinar el tipo de contenido multimedia y devolver el HTML apropiado
function determineMultimediaContent(cleanMultimediaSrc, fileExtension, isYouTube, isExternalVideo) {
  if (isYouTube) {
    return getYouTubeEmbedHTML(cleanMultimediaSrc);
  } else if (['mp4', 'webm', 'avi', 'mov'].includes(fileExtension) || isExternalVideo) {
    return getVideoPlayerHTML(cleanMultimediaSrc, fileExtension);
  } else if (['mp3', 'wav', 'ogg', 'aac'].includes(fileExtension)) {
    return getAudioPlayerHTML(cleanMultimediaSrc, fileExtension);
  } else {
    return getExternalResourceHTML(cleanMultimediaSrc, fileExtension);
  }
}

// Función para determinar si una URL es de S3
function isS3Url(url) {
  return url.includes('s3.amazonaws.com') || 
         url.includes('edf-catalogo-tablas.s3') || 
         url.includes('/admin/s3/') || 
         url.includes('/s3/');
}

// Función para generar HTML de YouTube embed
function getYouTubeEmbedHTML(url) {
  let videoId = '';
  if (url.includes('youtube.com/watch?v=')) {
    videoId = url.split('v=')[1]?.split('&')[0];
  } else if (url.includes('youtu.be/')) {
    videoId = url.split('youtu.be/')[1]?.split('?')[0];
  }
  
  if (!videoId) return '';
  
  return `
    <div class="text-center mb-3">
      <h5><i class="fab fa-youtube text-danger"></i> Video de YouTube</h5>
    </div>
    <div class="d-flex justify-content-center">
      <iframe width="100%" height="380" src="https://www.youtube.com/embed/${videoId}" 
      frameborder="0" allowfullscreen 
      style="max-width: 100%; max-height: 380px; aspect-ratio: 16/9;"></iframe>
    </div>
  `;
}

// Función para generar HTML de reproductor de video
function getVideoPlayerHTML(url, fileExtension) {
  // Ajustar el tamaño del modal para videos
  setTimeout(() => {
    const modalDialog = document.querySelector('#multimediaModal .modal-dialog');
    if (modalDialog) {
      modalDialog.style.maxWidth = '850px';
      modalDialog.style.width = '85%';
    }
    
    const modalContentElement = document.querySelector('#multimediaModal .modal-content');
    if (modalContentElement) {
      modalContentElement.style.height = '650px';
      modalContentElement.style.maxHeight = '85vh';
    }
  }, 100);
  
  return `
    <div class="text-center mb-3">
      <h5><i class="fas fa-video text-primary"></i> Reproduciendo Video</h5>
    </div>
    <div class="d-flex justify-content-center" style="width: 100%; max-height: 75vh;">
      <video controls preload="metadata" class="img-fluid" style="max-width: 100%; height: auto; max-height: 65vh; width: auto;">
        <source src="${url}" type="video/${fileExtension || 'mp4'}">
        Tu navegador no soporta el elemento de video.
      </video>
    </div>
  `;
}

// Función para generar HTML de reproductor de audio
function getAudioPlayerHTML(url, fileExtension) {
  return `
    <div class="text-center mb-3">
      <h5><i class="fas fa-music text-success"></i> Reproduciendo Audio</h5>
    </div>
    <div class="d-flex justify-content-center">
      <audio controls class="img-fluid" style="width: 100%; max-width: 500px;">
        <source src="${url}" type="audio/${fileExtension}">
        Tu navegador no soporta el elemento de audio.
      </audio>
    </div>
  `;
}

// Función para generar HTML de recurso externo
function getExternalResourceHTML(url, fileExtension) {
  const isExternalUrl = url.startsWith('http');
  const urlDomain = isExternalUrl ? new URL(url).hostname : '';
  
  return `
    <div class="text-center p-4">
      <i class="fas fa-external-link-alt fa-4x text-info mb-3"></i>
      <h5>Recurso Multimedia Externo</h5>
      ${isExternalUrl ? `<p class="text-muted"><strong>Sitio:</strong> ${urlDomain}</p>` : ''}
      <p class="text-muted"><strong>Tipo:</strong> ${fileExtension?.toUpperCase() || 'Enlace externo'}</p>
      <div class="alert alert-info mt-3">
        <i class="fas fa-info-circle"></i>
        <strong>Información:</strong> Este contenido se abrirá en una nueva pestaña del navegador.
      </div>
      <div class="d-grid gap-2 d-md-flex justify-content-md-center">
        <a href="${url}" target="_blank" class="btn btn-primary btn-lg">
          <i class="fas fa-external-link-alt"></i> Abrir Recurso
        </a>
        <button type="button" class="btn btn-outline-secondary" onclick="navigator.clipboard.writeText('${url}').then(() => alert('URL copiada al portapapeles'))">
          <i class="fas fa-copy"></i> Copiar URL
        </button>
      </div>
    </div>
  `;
}

// Función para configurar el manejo de errores de elementos multimedia
function setupMultimediaErrorHandling(modalContent, cleanMultimediaSrc) {
  const videoElements = modalContent.querySelectorAll('video');
  const audioElements = modalContent.querySelectorAll('audio');
  
  [...videoElements, ...audioElements].forEach(element => {
    element.onerror = function() {
      log("[MODAL-UNIFIED] ❌ Error cargando multimedia:", cleanMultimediaSrc);
      modalContent.innerHTML = `
        <div class="text-center p-4">
          <i class="fas fa-exclamation-triangle fa-4x text-warning mb-3"></i>
          <h5>Error al cargar multimedia</h5>
          <p class="text-muted">No se pudo cargar el archivo multimedia.</p>
          <p class="text-danger small">URL: ${cleanMultimediaSrc}</p>
        </div>
      `;
    };
    
    element.onload = function() {
      log("[MODAL-UNIFIED] ✅ Multimedia cargado correctamente:", cleanMultimediaSrc);
    };
  });
}

// Función para configurar botones del modal multimedia
function setupMultimediaModalButtons(modalFooter, cleanMultimediaSrc, multimediaTitle, isS3File) {
  if (!modalFooter) return;
  
  modalFooter.innerHTML = `
    <div class="d-flex gap-2 w-100 justify-content-between">
      <div class="d-flex gap-2">
        <a href="${cleanMultimediaSrc}" target="_blank" class="btn btn-primary">
          <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
        </a>
        ${isS3File ? 
          `<button type="button" class="btn btn-outline-primary" data-action="download-s3-file" data-document-src="${cleanMultimediaSrc}" data-document-title="${multimediaTitle}">
            <i class="fas fa-download"></i> Descargar
          </button>` : 
          `<button type="button" class="btn btn-outline-primary" data-action="download-local-file" data-document-src="${cleanMultimediaSrc}" data-document-title="${multimediaTitle}">
            <i class="fas fa-download"></i> Descargar
          </button>`
        }
      </div>
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
    </div>
  `;
}

// Función para mostrar multimedia en modal
function showMultimediaModal(multimediaSrc, multimediaTitle, e) {
  log("[MODAL-UNIFIED] 🎬 showMultimediaModal llamado con:", { multimediaSrc, multimediaTitle });
  
  const modalElement = document.getElementById('multimediaModal');
  const modalContent = document.getElementById('multimediaContent');
  const modalTitle = document.getElementById('multimediaModalLabel');
  
  if (!modalElement || !modalContent || !modalTitle) {
    console.error("[MODAL-UNIFIED] ❌ Elementos del modal multimedia no encontrados");
    return;
  }
  
  // Prevenir que URLs se abran en navegador directamente
  if (e) {
    e.preventDefault();
  }
  
  // Configurar título según el tipo de contenido
  const fileExtension = multimediaSrc.split('.').pop()?.toLowerCase();
  if (['mp4', 'webm', 'avi', 'mov'].includes(fileExtension)) {
    modalTitle.textContent = 'Reproduciendo Video';
  } else if (['mp3', 'wav', 'ogg', 'aac'].includes(fileExtension)) {
    modalTitle.textContent = 'Reproduciendo Audio';
  } else if (multimediaSrc.includes('youtube.com') || multimediaSrc.includes('youtu.be')) {
    modalTitle.textContent = 'Video de YouTube';
  } else {
    modalTitle.textContent = multimediaTitle || 'Contenido Multimedia';
  }
  
  // Determinar tipo de archivo y URL
  const isYouTube = multimediaSrc.includes('youtube.com') || multimediaSrc.includes('youtu.be');
  const isExternalVideo = multimediaSrc.startsWith('http') && (isYouTube || multimediaSrc.includes('vimeo.com') || multimediaSrc.includes('.mp4') || multimediaSrc.includes('.webm'));
  
  // Limpiar URL si contiene rutas incorrectas
  const cleanMultimediaSrc = cleanMultimediaUrl(multimediaSrc);
  
  // DETECCIÓN HÍBRIDA S3/LOCAL
  const isS3File = isS3Url(cleanMultimediaSrc);
  
  // Generar HTML según el tipo de contenido
  const mediaHTML = determineMultimediaContent(cleanMultimediaSrc, fileExtension, isYouTube, isExternalVideo);
  
  // Configurar contenido y mostrar modal
  modalContent.innerHTML = mediaHTML;
  
  // Agregar manejo de errores para elementos multimedia
  setupMultimediaErrorHandling(modalContent, cleanMultimediaSrc);
  
  // Insertar botones en el modal-footer
  const modalFooter = document.querySelector('#multimediaModal .modal-footer');
  setupMultimediaModalButtons(modalFooter, cleanMultimediaSrc, multimediaTitle, isS3File);
  
  // Mostrar modal
  const modal = new bootstrap.Modal(modalElement);
  modal.show();
  
  log("[MODAL-UNIFIED] ✅ Modal multimedia mostrado");
}

// ============================================================================
// FUNCIONES DE DESCARGA
// ============================================================================

// Función para descargar archivos S3
function downloadS3File(fileUrl, fileName) {
  log("[MODAL-UNIFIED] 🔧 Descargando archivo S3:", fileUrl);
  
  try {
    const proxyUrl = fileUrl.replace(
      'https://edf-catalogo-tablas.s3.eu-central-1.amazonaws.com/',
      '/admin/s3/'
    );
    
    const link = document.createElement('a');
    link.href = proxyUrl;
    link.download = fileName || 'archivo';
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    log("[MODAL-UNIFIED] ✅ Descarga S3 iniciada");
  } catch (error) {
    console.error("[MODAL-UNIFIED] ❌ Error descargando S3:", error);
    alert('Error al descargar: ' + error.message);
  }
}

// Función para descargar archivos locales
function downloadLocalFile(fileUrl, fileName) {
  log("[MODAL-UNIFIED] 🔧 Descargando archivo local:", fileUrl);
  
  try {
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = fileName || 'archivo';
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    log("[MODAL-UNIFIED] ✅ Descarga local iniciada");
  } catch (error) {
    console.error("[MODAL-UNIFIED] ❌ Error descargando local:", error);
    alert('Error al descargar: ' + error.message);
  }
}

// Función para descargar Markdown
function downloadMarkdownFile(fileUrl, fileName) {
  log("[MODAL-UNIFIED] 🔧 Descargando Markdown:", fileUrl);
  
  if (fileUrl.includes('s3.amazonaws.com')) {
    downloadS3File(fileUrl, fileName);
  } else {
    downloadLocalFile(fileUrl, fileName);
  }
}

// Función para descargar documento (genérica)
function downloadDocument() {
  log("[MODAL-UNIFIED] 🔧 downloadDocument llamado");
  
  const modalContent = document.getElementById('documentContent');
  if (!modalContent) return;
  
  // Buscar enlaces de descarga en el contenido del modal
  const downloadLinks = modalContent.querySelectorAll('a[href*="download"], button[onclick*="download"]');
  
  if (downloadLinks.length > 0) {
    // Simular clic en el primer enlace de descarga encontrado
    downloadLinks[0].click();
  } else {
    console.warn("[MODAL-UNIFIED] ⚠️ No se encontraron enlaces de descarga");
  }
}

// Función para descargar multimedia
function downloadMultimedia() {
  log("[MODAL-UNIFIED] 🔧 downloadMultimedia llamado");
  
  const modalContent = document.getElementById('multimediaContent');
  if (!modalContent) return;
  
  // Buscar enlaces de descarga en el contenido del modal
  const downloadLinks = modalContent.querySelectorAll('a[href*="download"], button[onclick*="download"]');
  
  if (downloadLinks.length > 0) {
    // Simular clic en el primer enlace de descarga encontrado
    downloadLinks[0].click();
  } else {
    console.warn("[MODAL-UNIFIED] ⚠️ No se encontraron enlaces de descarga");
  }
}

// Función para abrir PDF en nueva pestaña
function openPDFInNewTab(pdfUrl) {
  log("[MODAL-UNIFIED] 🔧 Abriendo PDF en nueva pestaña:", pdfUrl);
  window.open(pdfUrl, '_blank');
}

// ============================================================================
// FUNCIONES DE UTILIDAD
// ============================================================================

// Función para manejar errores de imagen
function handleImageError(img) {
  log("[MODAL-UNIFIED] ⚠️ Error en imagen:", img);
  if (img?.src && !img.src.includes('image-error-placeholder.png')) {
    // Evitar bucles infinitos estableciendo el placeholder solo una vez
    img.src = '/static/img/image-error-placeholder.png';
    img.alt = 'Error cargando imagen';
    img.onerror = null; // Remover el handler para evitar bucles
  }
}

// Función para ocultar el spinner de carga de imagen
function hideImageLoadingSpinner() {
  log("[MODAL-UNIFIED] 🔧 Ocultando spinner de carga de imagen");
  const spinner = document.querySelector('.image-loading-spinner');
  if (spinner) {
    spinner.style.display = 'none';
  }
}

// Función para descargar imagen
function downloadImage() {
  log("[MODAL-UNIFIED] 🔧 downloadImage llamado");
  
  const modalImage = document.getElementById('modalImage');
  if (!modalImage?.src) {
    console.error("[MODAL-UNIFIED] ❌ No se encontró imagen para descargar");
    return;
  }
  
  const imageSrc = modalImage.src;
  const imageTitle = modalImage.alt || 'imagen';
  
  log("[MODAL-UNIFIED] 🔧 Descargando imagen:", { imageSrc, imageTitle });
  
  try {
    const link = document.createElement('a');
    link.href = imageSrc;
    link.download = imageTitle;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    log("[MODAL-UNIFIED] ✅ Descarga de imagen iniciada");
  } catch (error) {
    console.error("[MODAL-UNIFIED] ❌ Error descargando imagen:", error);
    alert('Error al descargar imagen: ' + error.message);
  }
}

// ============================================================================
// EXPORTACIÓN GLOBAL
// ============================================================================

// Exportar todas las funciones principales
window.showDocumentModal = showDocumentModal;
window.showMarkdownInModal = showMarkdownInModal;
window.showTextInModal = showTextInModal;
window.showImageModal = showImageModal;
// Exportar directamente la implementación original de showMultimediaModal
// sin crear un wrapper adicional que podría causar recursión
window.showMultimediaModal = showMultimediaModal;

// Exportar funciones de descarga
window.downloadS3File = downloadS3File;
window.downloadLocalFile = downloadLocalFile;
window.downloadMarkdownFile = downloadMarkdownFile;
window.downloadDocument = downloadDocument;
window.downloadMultimedia = downloadMultimedia;
window.openPDFInNewTab = openPDFInNewTab;

// Exportar funciones de utilidad
window.handleImageError = handleImageError;
window.hideImageLoadingSpinner = hideImageLoadingSpinner;
window.downloadImage = downloadImage;

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

log("[MODAL-UNIFIED] ✅ Todas las funciones exportadas correctamente");
log("[MODAL-UNIFIED] 🎯 Sistema de modales unificado listo");
log("[MODAL-UNIFIED] 📅 VERSIÓN: 2025-10-09-12:45 - UNIFICADA + FUNCIONES COMPLETAS + DOWNLOAD IMAGE + EXCEL VIEWER + XLSX FIX");

// Verificación final de funciones disponibles
log("[MODAL-UNIFIED] 🔍 VERIFICACIÓN FINAL:");
log("  - showImageModal:", typeof window.showImageModal);
log("  - showDocumentModal:", typeof window.showDocumentModal);
log("  - showMultimediaModal:", typeof window.showMultimediaModal);
log("  - downloadImage:", typeof window.downloadImage);
log("  - handleImageError:", typeof window.handleImageError);
log("  - hideImageLoadingSpinner:", typeof window.hideImageLoadingSpinner);

// Ejecutar limpieza de imágenes rotas después de que la página se cargue completamente
// COMENTADO TEMPORALMENTE PARA EVITAR INTERFERENCIA CON IMÁGENES FUNCIONANDO
// if (document.readyState === 'loading') {
//   document.addEventListener('DOMContentLoaded', cleanupBrokenImages);
// } else {
//   // Si el DOM ya está cargado, ejecutar inmediatamente
//   setTimeout(cleanupBrokenImages, 1000); // Esperar 1 segundo para que las imágenes se carguen
// }

// Event listeners para data-action download
document.addEventListener('click', function(e) {
    const action = e.target.dataset.action;
    
    if (action === 'download-s3-file') {
        const documentSrc = e.target.dataset.documentSrc;
        const documentTitle = e.target.dataset.documentTitle;
        if (documentSrc && documentTitle) {
            downloadS3File(documentSrc, documentTitle);
        }
    }
    
    if (action === 'download-local-file') {
        const documentSrc = e.target.dataset.documentSrc;
        const documentTitle = e.target.dataset.documentTitle;
        if (documentSrc && documentTitle) {
            downloadLocalFile(documentSrc, documentTitle);
        }
    }
});

// ============================================================================
// CORRECCIÓN DEL PROBLEMA DE OVERFLOW DESPUÉS DE CERRAR MODALES
// ============================================================================

// Función para restaurar el overflow después de cerrar un modal
function restoreOverflow() {
    document.body.style.overflow = '';
    document.body.classList.remove('modal-open');
    document.body.style.paddingRight = '';
    
    // Eliminar cualquier backdrop residual
    const backdrops = document.querySelectorAll('.modal-backdrop');
    for (const backdrop of backdrops) {
        backdrop.remove();
    }
    
    log("[MODAL-UNIFIED] 🔄 Overflow restaurado después de cerrar modal");
}

// Función para añadir listener a un modal
function addOverflowListenerToModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        modalElement.addEventListener('hidden.bs.modal', function() {
            // Pequeño retraso para asegurar que otras operaciones de cierre terminen primero
            setTimeout(restoreOverflow, 100);
        });
        log(`[MODAL-UNIFIED] ✅ Evento de restauración de overflow añadido a ${modalId}`);
    }
}

// Añadir eventos para todos los modales conocidos para restaurar el overflow
document.addEventListener('DOMContentLoaded', function() {
    // Modales conocidos en la aplicación
    const modalIds = ['imageModal', 'documentModal', 'multimediaModal', 'confirmDeleteModal', 'exportModal'];
    
    // Añadir manejador para restaurar overflow después de cerrar modal
    for (const modalId of modalIds) {
        addOverflowListenerToModal(modalId);
    }
    
    // Evento para manejar la descarga de archivos Excel locales
    document.body.addEventListener('click', function(event) {
        if (event.target.closest('[data-action="download-local-file"]')) {
            const button = event.target.closest('[data-action="download-local-file"]');
            const fileSrc = button.getAttribute('data-document-src');
            const fileName = button.getAttribute('data-document-title');
            
            if (fileSrc) {
                log(`[MODAL-UNIFIED] 📥 Iniciando descarga de archivo Excel local: ${fileName}`);
                
                // Crear un enlace temporal para la descarga
                const downloadLink = document.createElement('a');
                downloadLink.href = fileSrc;
                downloadLink.download = fileName || 'documento_excel.xlsx';
                downloadLink.style.display = 'none';
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                
                log(`[MODAL-UNIFIED] ✅ Descarga de archivo Excel iniciada: ${fileName}`);
            }
        }
    });
    
    // Evento para manejar la descarga de archivos Excel desde S3
    document.body.addEventListener('click', function(event) {
        if (event.target.closest('[data-action="download-s3-file"]')) {
            const button = event.target.closest('[data-action="download-s3-file"]');
            const fileSrc = button.getAttribute('data-document-src');
            const fileName = button.getAttribute('data-document-title');
            
            if (fileSrc) {
                log(`[MODAL-UNIFIED] 📥 Iniciando descarga de archivo Excel desde S3: ${fileName}`);
                
                // Crear un enlace temporal para la descarga
                const downloadLink = document.createElement('a');
                downloadLink.href = fileSrc;
                downloadLink.download = fileName || 'documento_excel.xlsx';
                downloadLink.style.display = 'none';
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                
                log(`[MODAL-UNIFIED] ✅ Descarga de archivo Excel iniciada desde S3: ${fileName}`);
            }
        }
    });
    
    log("[MODAL-UNIFIED] ✅ Corrección de overflow instalada");
    log("[MODAL-UNIFIED] ✅ Soporte para Excel instalado correctamente");
});