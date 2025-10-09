/**
 * MODAL FUNCTIONS ALL - VERSIÓN UNIFICADA COMPLETA
 * Script que integra todas las funcionalidades de modales con mejoras
 * Fecha: 8 de octubre de 2025
 * 
 * Características:
 * - Unifica comportamiento de todos los tipos de modales (documento, imagen, multimedia)
 * - Aplica correcciones específicas para PDFs, Markdown y texto plano
 * - Gestión responsiva para diferentes tamaños de pantalla
 * - Manejo de errores mejorado
 * - Botones funcionales en todos los modales
 * - Compatible con contenido local y almacenado en S3
 */

// Auto-ejecutable para aislar el alcance de las variables
(function() {
    // Configuración de depuración
    let DEBUG_MODE = false;
    
    try {
        if (typeof getDebugMode === 'function') {
            DEBUG_MODE = getDebugMode();
        } else if (typeof window.APP_CONFIG !== 'undefined') {
            DEBUG_MODE = window.APP_CONFIG.DEBUG_MODE;
        }
    } catch (error) {
        console.warn('No se pudo cargar la configuración de depuración para modal-functions-ALL.js', error);
    }
    
    // Función para logging condicional
    function log(message, data) {
        if (DEBUG_MODE) {
            if (typeof window.APP_CONFIG !== 'undefined' && typeof window.APP_CONFIG.log === 'function') {
                window.APP_CONFIG.log(`[MODAL-ALL] ${message}`);
                if (data !== undefined) window.APP_CONFIG.log(data);
            } else {
                console.log(`[MODAL-ALL] ${message}`);
                if (data !== undefined) console.log(data);
            }
        }
    }
    
    function logError(message, error) {
        console.error(`[MODAL-ALL] ${message}`, error);
    }
    
    // ============================================================================
    // ESTILOS GLOBALES PARA MODALES
    // ============================================================================
    
    function injectGlobalStyles() {
        log('Inyectando estilos globales para modales');
        
        const style = document.createElement('style');
        style.id = 'modal-functions-all-styles';
        style.textContent = `
            /* Estilos unificados para modales - v1.0 (8 octubre 2025) */
            
            /* Corrección general para modales */
            .modal-dialog {
                max-width: 95% !important;
                width: 90% !important;
                margin: 1rem auto !important;
                height: 90vh !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            
            .modal-content {
                height: 85vh !important;
                max-height: 90vh !important;
                display: flex !important;
                flex-direction: column !important;
                overflow: hidden !important;
            }
            
            .modal-header {
                flex-shrink: 0 !important;
            }
            
            .modal-footer {
                flex-shrink: 0 !important;
                padding: 0.5rem 1rem !important;
            }
            
            .modal-body {
                flex: 1 1 auto !important;
                overflow-y: hidden !important;
                padding: 0 !important;
                position: relative !important;
            }
            
            /* Estilos específicos para modal de documentos */
            #documentContent {
                height: 100% !important;
                overflow: hidden !important;
                position: relative !important;
            }
            
            /* Ajustes específicos para iframes de PDF */
            #documentContent iframe {
                width: 100% !important;
                height: 100% !important;
                border: none !important;
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
            }
            
            /* Contenedor para viewer de PDF */
            .pdf-viewer-container {
                width: 100% !important;
                height: 100% !important;
                position: relative !important;
                overflow: hidden !important;
            }
            
            /* Estilo para modal de imágenes */
            #imageModal .modal-body {
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 0.5rem !important;
                height: 100% !important;
                overflow: hidden !important;
            }
            
            #modalImage {
                max-height: 75vh !important;
                object-fit: contain !important;
                margin: 0 auto !important;
                border-radius: 5px !important;
            }
            
            /* Estilo para modal de multimedia */
            #multimediaContent {
                width: 100% !important;
                height: 100% !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
                align-items: center !important;
                overflow: hidden !important;
            }
            
            #multimediaContent video,
            #multimediaContent audio {
                max-width: 100% !important;
                max-height: 65vh !important;
            }
            
            /* Estilos para contenedores de Markdown y texto */
            .markdown-content-wrapper,
            .text-content-wrapper {
                max-height: 60vh !important;
                overflow-y: auto !important;
                padding: 15px !important;
                background: #f8f9fa !important;
                border-radius: 8px !important;
                text-align: left !important;
                margin: 15px !important;
                width: calc(100% - 30px) !important;
            }
            
            /* Corrección para botones en todos los modales */
            .modal-footer .d-flex {
                width: 100% !important;
                justify-content: space-between !important;
                gap: 0.5rem !important;
            }
            
            /* Corrección para botones en móviles */
            @media (max-width: 768px) {
                .modal-footer .d-flex {
                    flex-wrap: wrap !important;
                }
                
                .modal-footer .btn {
                    margin-bottom: 0.25rem !important;
                    font-size: 0.875rem !important;
                }
                
                .modal-dialog {
                    width: 95% !important;
                    margin: 0.5rem auto !important;
                    height: 85vh !important;
                }
                
                .modal-content {
                    height: 80vh !important;
                }
                
                #modalImage {
                    max-height: 65vh !important;
                }
            }
        `;
        
        // Verificar si ya existe antes de añadir
        if (!document.getElementById('modal-functions-all-styles')) {
            document.head.appendChild(style);
            log('Estilos globales para modales añadidos');
        }
    }
    
    // ============================================================================
    // FUNCIONES COMPARTIDAS PARA TODOS LOS MODALES
    // ============================================================================
    
    // Función para mostrar indicador de carga en cualquier modal
    function showLoadingInModal(modalContentElement) {
        if (!modalContentElement) return;
        
        modalContentElement.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <h5>Cargando contenido</h5>
                <p class="text-muted">Preparando visualización...</p>
            </div>
        `;
    }
    
    // Función para mostrar errores en cualquier modal
    function showErrorInModal(modalContentElement, errorTitle, errorMessage) {
        if (!modalContentElement) return;
        
        modalContentElement.innerHTML = `
            <div class="text-center p-4">
                <i class="fas fa-exclamation-triangle fa-4x text-danger mb-3"></i>
                <h5>${errorTitle || 'Error'}</h5>
                <p class="text-muted">${errorMessage || 'No se pudo cargar el contenido.'}</p>
            </div>
        `;
    }
    
    // Función para limpiar URLs
    function cleanUrl(url) {
        let cleanedUrl = url;
        
        if (url.includes('/static/uploads//admin/s3/')) {
            cleanedUrl = url.replace('/static/uploads//admin/s3/', '/admin/s3/');
        } else if (url.includes('/imagenes_subidas//admin/s3/')) {
            cleanedUrl = url.replace('/imagenes_subidas//admin/s3/', '/admin/s3/');
        }
        
        return cleanedUrl;
    }
    
    // Función para determinar si una URL es de S3
    function isS3Url(url) {
        return url.includes('s3.amazonaws.com') || 
               url.includes('edf-catalogo-tablas.s3') || 
               url.includes('/admin/s3/') || 
               url.includes('/s3/');
    }
    
    // ============================================================================
    // MODAL DE DOCUMENTOS (PDF, Markdown, Texto)
    // ============================================================================
    
    // Función para determinar título del documento según extensión
    function getDocumentTitle(fileExtension, customTitle) {
        if (customTitle && customTitle.trim() !== '') {
            return customTitle;
        }
        
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
        } else if (['txt', 'log'].includes(fileExtension)) {
            return 'Ver Texto';
        }
        return 'Documento';
    }
    
    // Función principal para mostrar documentos
    function showDocumentModal(documentSrc, documentTitle) {
        log('showDocumentModal llamado con:', { documentSrc, documentTitle });
        
        // Buscar elementos del modal
        const modalElement = document.getElementById('documentModal');
        const modalContent = document.getElementById('documentContent');
        const modalTitle = document.getElementById('documentModalLabel');
        
        if (!modalElement || !modalContent || !modalTitle) {
            logError('Elementos del modal no encontrados');
            alert("Error: Modal de documento no disponible");
            return;
        }
        
        // Limpiar URL
        const cleanDocumentSrc = cleanUrl(documentSrc);
        
        // Detectar extensión del archivo
        const fileExtension = cleanDocumentSrc.split('.').pop()?.toLowerCase();
        
        // Configurar título
        modalTitle.textContent = getDocumentTitle(fileExtension, documentTitle);
        
        // Mostrar modal primero para mejor experiencia de usuario
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        
        // Mostrar loading mientras se procesa
        showLoadingInModal(modalContent);
        
        // Detectar si es archivo S3
        const isS3File = isS3Url(cleanDocumentSrc);
        log('Información del documento:', {
            url: cleanDocumentSrc,
            extension: fileExtension,
            isS3: isS3File,
            title: documentTitle
        });
        
        // Procesar según el tipo de documento
        if (fileExtension === 'pdf') {
            // PDF
            handlePdfDocument(modalContent, cleanDocumentSrc, documentTitle, isS3File);
        } else if (fileExtension === 'md') {
            // Markdown
            handleMarkdownDocument(modalContent, cleanDocumentSrc, documentTitle, isS3File);
        } else if (['txt', 'log'].includes(fileExtension)) {
            // Texto plano
            handleTextDocument(modalContent, cleanDocumentSrc, documentTitle, isS3File);
        } else {
            // Otros tipos de documentos
            handleOtherDocument(modalContent, cleanDocumentSrc, documentTitle, fileExtension, isS3File);
        }
        
        // Optimizar dimensiones del modal para cualquier tipo de documento
        optimizeDocumentModalSize(fileExtension);
        
        // Configurar botones del footer del modal
        setupDocumentModalButtons(cleanDocumentSrc, documentTitle, fileExtension, isS3File);
        
        log('Modal de documento configurado');
    }
    
    // Función para manejar documentos PDF
    function handlePdfDocument(modalContent, documentSrc, documentTitle, isS3File) {
        log('Manejando documento PDF:', documentSrc);
        
        // Generar HTML para PDF
        const pdfHtml = `
            <div class="text-center p-2">
                <i class="fas fa-file-pdf fa-3x text-danger mb-2"></i>
                <h5>${documentTitle || 'Documento PDF'}</h5>
                <p class="text-muted mb-2">
                    <strong>Tipo:</strong> PDF
                    <strong>Ubicación:</strong> ${isS3File ? 'S3' : 'Local'}
                </p>
            </div>
            
            <div class="pdf-viewer-container">
                <iframe 
                    src="${documentSrc}" 
                    width="100%" 
                    height="100%" 
                    style="border: none; position: absolute; top: 0; left: 0; right: 0; bottom: 0;"
                    allowfullscreen
                    onerror="console.error('[MODAL-ALL] Error cargando PDF en iframe')">
                </iframe>
            </div>
        `;
        
        modalContent.innerHTML = pdfHtml;
    }
    
    // Función para manejar documentos Markdown
    function handleMarkdownDocument(modalContent, documentSrc, documentTitle, isS3File) {
        log('Manejando documento Markdown:', documentSrc);
        
        // Determinar URL para fetch
        let fetchUrl = documentSrc;
        
        if (isS3File) {
            fetchUrl = documentSrc.replace(
                'https://edf-catalogo-tablas.s3.eu-central-1.amazonaws.com/',
                '/admin/s3/'
            );
        }
        
        // Cargar y renderizar Markdown
        fetch(fetchUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.text();
            })
            .then(markdownText => {
                // Renderizado simple de Markdown
                const htmlContent = markdownText
                    .replace(/^### (.*$)/gim, "<h3>$1</h3>")
                    .replace(/^## (.*$)/gim, "<h2>$1</h2>")
                    .replace(/^# (.*$)/gim, "<h1>$1</h1>")
                    .replace(/\*\*(.*)\*\*/gim, "<strong>$1</strong>")
                    .replace(/\*(.*)\*/gim, "<em>$1</em>")
                    .replace(/\n/gim, "<br>");
                
                modalContent.innerHTML = `
                    <div class="text-center p-2">
                        <i class="fas fa-file-code fa-3x text-info mb-2"></i>
                        <h5>${documentTitle || 'Documento Markdown'}</h5>
                        <p class="text-muted mb-2">
                            <strong>Tipo:</strong> Markdown
                            <strong>Ubicación:</strong> ${isS3File ? 'S3' : 'Local'}
                        </p>
                    </div>
                    
                    <div class="markdown-content-wrapper">
                        <div class="markdown-rendered">
                            ${htmlContent}
                        </div>
                    </div>
                `;
            })
            .catch(error => {
                showErrorInModal(
                    modalContent,
                    'Error al cargar Markdown',
                    error.message
                );
            });
    }
    
    // Función para manejar documentos de texto
    function handleTextDocument(modalContent, documentSrc, documentTitle, isS3File) {
        log('Manejando documento de texto:', documentSrc);
        
        // Determinar URL para fetch
        let fetchUrl = documentSrc;
        
        if (isS3File) {
            fetchUrl = documentSrc.replace(
                'https://edf-catalogo-tablas.s3.eu-central-1.amazonaws.com/',
                '/admin/s3/'
            );
        }
        
        // Cargar y mostrar texto
        fetch(fetchUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.text();
            })
            .then(textContent => {
                modalContent.innerHTML = `
                    <div class="text-center p-2">
                        <i class="fas fa-file-alt fa-3x text-primary mb-2"></i>
                        <h5>${documentTitle || 'Documento de Texto'}</h5>
                        <p class="text-muted mb-2">
                            <strong>Tipo:</strong> Texto
                            <strong>Ubicación:</strong> ${isS3File ? 'S3' : 'Local'}
                        </p>
                    </div>
                    
                    <div class="text-content-wrapper">
                        <pre style="white-space: pre-wrap; font-family: 'Courier New', monospace;">${textContent}</pre>
                    </div>
                `;
            })
            .catch(error => {
                // Intento de fallback a local si es S3
                if (isS3File) {
                    const filename = documentSrc.split('/').pop();
                    const localUrl = `/imagenes_subidas/${filename}`;
                    
                    log('Fallback a URL local:', localUrl);
                    
                    fetch(localUrl)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                            }
                            return response.text();
                        })
                        .then(textContent => {
                            modalContent.innerHTML = `
                                <div class="text-center p-2">
                                    <i class="fas fa-file-alt fa-3x text-primary mb-2"></i>
                                    <h5>${documentTitle || 'Documento de Texto'}</h5>
                                    <p class="text-muted mb-2">
                                        <strong>Tipo:</strong> Texto
                                        <strong>Ubicación:</strong> Local (fallback)
                                    </p>
                                </div>
                                
                                <div class="text-content-wrapper">
                                    <pre style="white-space: pre-wrap; font-family: 'Courier New', monospace;">${textContent}</pre>
                                </div>
                            `;
                        })
                        .catch(fallbackError => {
                            showErrorInModal(
                                modalContent,
                                'Error al cargar texto',
                                'No se pudo cargar el archivo desde S3 ni desde almacenamiento local.'
                            );
                        });
                } else {
                    showErrorInModal(
                        modalContent,
                        'Error al cargar texto',
                        error.message
                    );
                }
            });
    }
    
    // Función para manejar otros tipos de documentos
    function handleOtherDocument(modalContent, documentSrc, documentTitle, fileExtension, isS3File) {
        log('Manejando otro tipo de documento:', { documentSrc, fileExtension });
        
        modalContent.innerHTML = `
            <div class="text-center p-4">
                <i class="fas fa-file fa-4x text-secondary mb-3"></i>
                <h5>${documentTitle || 'Documento'}</h5>
                <p class="text-muted mb-4">
                    <strong>Archivo:</strong> ${documentTitle || documentSrc.split('/').pop()}<br>
                    <strong>Tipo:</strong> ${fileExtension?.toUpperCase() || 'Desconocido'}<br>
                    <strong>Ubicación:</strong> ${isS3File ? 'S3' : 'Local'}
                </p>
                <div class="alert alert-info mt-3">
                    <i class="fas fa-info-circle"></i>
                    <strong>Información:</strong> Para visualizar este tipo de archivo, use el botón para abrirlo en una nueva pestaña.
                </div>
            </div>
        `;
    }
    
    // Función para optimizar tamaño del modal según tipo de documento
    function optimizeDocumentModalSize(fileExtension) {
        setTimeout(() => {
            const modalDialog = document.querySelector('#documentModal .modal-dialog');
            const modalContent = document.querySelector('#documentModal .modal-content');
            
            if (!modalDialog || !modalContent) return;
            
            // Configuración óptima para diferentes tipos de documentos
            if (fileExtension === 'pdf') {
                // PDF necesita más altura
                modalDialog.style.maxWidth = '95%';
                modalDialog.style.width = '90%';
                modalDialog.style.height = '90vh';
                
                modalContent.style.height = '90vh';
                modalContent.style.maxHeight = '90vh';
                
            } else if (['md', 'txt', 'log'].includes(fileExtension)) {
                // Markdown y texto pueden ser un poco más pequeños
                modalDialog.style.maxWidth = '85%';
                modalDialog.style.width = '80%';
                modalDialog.style.height = '85vh';
                
                modalContent.style.height = '85vh';
                modalContent.style.maxHeight = '85vh';
                
            } else {
                // Documentos genéricos
                modalDialog.style.maxWidth = '80%';
                modalDialog.style.width = '75%';
                modalDialog.style.height = '80vh';
                
                modalContent.style.height = '80vh';
                modalContent.style.maxHeight = '80vh';
            }
        }, 100);
    }
    
    // Función para configurar botones en el modal de documento
    function setupDocumentModalButtons(documentSrc, documentTitle, fileExtension, isS3File) {
        const modalFooter = document.querySelector('#documentModal .modal-footer');
        if (!modalFooter) return;
        
        const actionType = isS3File ? 'download-s3-file' : 'download-local-file';
        const hasPDFButtons = fileExtension === 'pdf';
        
        modalFooter.innerHTML = `
            <div class="d-flex gap-2 w-100 justify-content-between">
                <div class="d-flex gap-2">
                    <a href="${documentSrc}" target="_blank" class="btn btn-primary">
                        <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
                    </a>
                    <button type="button" class="btn btn-outline-primary" data-action="${actionType}" data-document-src="${documentSrc}" data-document-title="${documentTitle}">
                        <i class="fas fa-download"></i> Descargar
                    </button>
                    ${hasPDFButtons ? `
                        <button type="button" class="btn btn-outline-secondary" onclick="printDocument()">
                            <i class="fas fa-print"></i> Imprimir
                        </button>
                        <button type="button" class="btn btn-outline-info" onclick="rotateDocument()">
                            <i class="fas fa-sync"></i> Rotar
                        </button>
                        <button type="button" class="btn btn-outline-warning" onclick="zoomInDocument()">
                            <i class="fas fa-search-plus"></i> Zoom +
                        </button>
                        <button type="button" class="btn btn-outline-warning" onclick="zoomOutDocument()">
                            <i class="fas fa-search-minus"></i> Zoom -
                        </button>
                    ` : ''}
                </div>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
        `;
    }
    
    // ============================================================================
    // MODAL DE IMÁGENES
    // ============================================================================
    
    // Función principal para mostrar imágenes
    function showImageModal(imageSrc, imageTitle) {
        log('showImageModal llamado con:', { imageSrc, imageTitle });
        
        // Buscar elementos del modal
        const modalElement = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        const modalTitle = document.getElementById('imageModalLabel');
        
        if (!modalElement || !modalImage || !modalTitle) {
            logError('Elementos del modal de imagen no encontrados');
            alert("Error: Modal de imagen no disponible");
            return;
        }
        
        // Limpiar URL
        const cleanImageSrc = cleanUrl(imageSrc);
        
        // Configurar título e imagen
        modalTitle.textContent = imageTitle || 'Imagen';
        modalImage.src = cleanImageSrc;
        modalImage.alt = imageTitle || 'Imagen';
        
        // Mostrar modal
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        
        // Manejar errores de carga de imagen
        modalImage.onerror = function() {
            log('Error cargando imagen:', cleanImageSrc);
            modalImage.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlbiBubyBlbmNvbnRyYWRhPC90ZXh0Pjwvc3ZnPg==';
            modalImage.alt = 'Imagen no encontrada';
            modalTitle.textContent = 'Imagen no encontrada';
        };
        
        // Optimizar tamaño del modal según dimensiones de la imagen
        modalImage.onload = function() {
            log('Imagen cargada correctamente:', cleanImageSrc);
            
            // Ajustar el tamaño del modal basado en el tamaño de la imagen
            setTimeout(() => {
                const imgWidth = modalImage.naturalWidth;
                const imgHeight = modalImage.naturalHeight;
                
                // Ajustar tamaño del modal para imágenes
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
        
        // Configurar botones para imagen
        setupImageModalButtons(cleanImageSrc, imageTitle);
        
        log('Modal de imagen mostrado');
    }
    
    // Función para configurar botones en modal de imagen
    function setupImageModalButtons(imageSrc, imageTitle) {
        const modalFooter = document.querySelector('#imageModal .modal-footer');
        if (!modalFooter) return;
        
        modalFooter.innerHTML = `
            <div class="d-flex gap-2 w-100 justify-content-between">
                <div class="d-flex gap-2">
                    <a href="${imageSrc}" target="_blank" class="btn btn-primary">
                        <i class="fas fa-external-link-alt"></i> Ver Original
                    </a>
                    <button type="button" class="btn btn-outline-primary" onclick="downloadImage('${imageSrc}', '${imageTitle || 'imagen'}')">
                        <i class="fas fa-download"></i> Descargar
                    </button>
                    <button type="button" class="btn btn-outline-secondary" onclick="rotateImage()">
                        <i class="fas fa-sync"></i> Rotar
                    </button>
                    <button type="button" class="btn btn-outline-info" onclick="zoomImage(1)">
                        <i class="fas fa-search-plus"></i> Zoom +
                    </button>
                    <button type="button" class="btn btn-outline-info" onclick="zoomImage(-1)">
                        <i class="fas fa-search-minus"></i> Zoom -
                    </button>
                </div>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
        `;
    }
    
    // ============================================================================
    // MODAL DE MULTIMEDIA
    // ============================================================================
    
    // Función para limpiar URLs de multimedia
    function cleanMultimediaUrl(multimediaSrc) {
        return cleanUrl(multimediaSrc);
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
    
    // Función para determinar el título del modal según el tipo de archivo
    function getMultimediaTitle(fileExtension, isYouTube, multimediaTitle) {
        if (['mp4', 'webm', 'avi', 'mov'].includes(fileExtension)) {
            return 'Reproduciendo Video';
        } else if (['mp3', 'wav', 'ogg', 'aac'].includes(fileExtension)) {
            return 'Reproduciendo Audio';
        } else if (isYouTube) {
            return 'Video de YouTube';
        } 
        return multimediaTitle || 'Contenido Multimedia';
    }
    
    // Función para configurar los elementos multimedia y manejar errores
    function setupMultimediaElements(modalContent, cleanMultimediaSrc) {
        const videoElements = modalContent.querySelectorAll('video');
        const audioElements = modalContent.querySelectorAll('audio');
        
        [...videoElements, ...audioElements].forEach(element => {
            element.onerror = function() {
                log('Error cargando multimedia:', cleanMultimediaSrc);
                showErrorInModal(
                    modalContent,
                    'Error al cargar multimedia',
                    'No se pudo cargar el archivo multimedia.'
                );
            };
        });
    }
    
    // Función para mostrar multimedia en modal
    function showMultimediaModal(multimediaSrc, multimediaTitle, e) {
        log('showMultimediaModal llamado con:', { multimediaSrc, multimediaTitle });
        
        // Buscar elementos del modal
        const modalElement = document.getElementById('multimediaModal');
        const modalContent = document.getElementById('multimediaContent');
        const modalTitle = document.getElementById('multimediaModalLabel');
        
        if (!modalElement || !modalContent || !modalTitle) {
            logError('Elementos del modal multimedia no encontrados');
            alert("Error: Modal multimedia no disponible");
            return;
        }
        
        // Prevenir que URLs se abran directamente (si se llamó desde un evento)
        if (e) {
            e.preventDefault();
        }
        
        // Limpiar URL
        const cleanMultimediaSrc = cleanMultimediaUrl(multimediaSrc);
        
        // Detectar tipo de archivo y URL
        const fileExtension = cleanMultimediaSrc.split('.').pop()?.toLowerCase();
        const isYouTube = cleanMultimediaSrc.includes('youtube.com') || cleanMultimediaSrc.includes('youtu.be');
        const isExternalVideo = cleanMultimediaSrc.startsWith('http') && (isYouTube || cleanMultimediaSrc.includes('vimeo.com') || cleanMultimediaSrc.includes('.mp4') || cleanMultimediaSrc.includes('.webm'));
        const isS3File = isS3Url(cleanMultimediaSrc);
        
        // Configurar título según tipo
        modalTitle.textContent = getMultimediaTitle(fileExtension, isYouTube, multimediaTitle);
        
        // Mostrar modal
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        
        // Mostrar loading mientras se procesa
        showLoadingInModal(modalContent);
        
        // Generar HTML según el tipo de contenido
        const mediaHTML = determineMultimediaContent(cleanMultimediaSrc, fileExtension, isYouTube, isExternalVideo);
        
        // Configurar contenido
        modalContent.innerHTML = mediaHTML;
        
        // Configurar elementos multimedia y manejar errores
        setupMultimediaElements(modalContent, cleanMultimediaSrc);
        
        // Optimizar tamaño del modal para multimedia
        optimizeMultimediaModalSize(fileExtension, isYouTube);
        
        // Configurar botones
        setupMultimediaModalButtons(cleanMultimediaSrc, multimediaTitle, fileExtension, isS3File);
        
        log('Modal multimedia mostrado');
    }
    
    // Función para optimizar tamaño del modal multimedia
    function optimizeMultimediaModalSize(fileExtension, isYouTube) {
        setTimeout(() => {
            const modalDialog = document.querySelector('#multimediaModal .modal-dialog');
            const modalContent = document.querySelector('#multimediaModal .modal-content');
            
            if (!modalDialog || !modalContent) return;
            
            if (['mp4', 'webm', 'avi', 'mov'].includes(fileExtension) || isYouTube) {
                // Video necesita más espacio
                modalDialog.style.maxWidth = '850px';
                modalDialog.style.width = '85%';
                modalContent.style.height = '650px';
                modalContent.style.maxHeight = '85vh';
            } else if (['mp3', 'wav', 'ogg', 'aac'].includes(fileExtension)) {
                // Audio puede ser más compacto
                modalDialog.style.maxWidth = '650px';
                modalDialog.style.width = '75%';
                modalContent.style.height = '400px';
                modalContent.style.maxHeight = '70vh';
            } else {
                // Enlaces externos y otros
                modalDialog.style.maxWidth = '700px';
                modalDialog.style.width = '80%';
                modalContent.style.height = '500px';
                modalContent.style.maxHeight = '75vh';
            }
        }, 100);
    }
    
    // Función para configurar botones del modal multimedia
    function setupMultimediaModalButtons(multimediaSrc, multimediaTitle, fileExtension, isS3File) {
        const modalFooter = document.querySelector('#multimediaModal .modal-footer');
        if (!modalFooter) return;
        
        const actionType = isS3File ? 'download-s3-file' : 'download-local-file';
        const hasVideoButtons = ['mp4', 'webm', 'avi', 'mov'].includes(fileExtension);
        const hasAudioButtons = ['mp3', 'wav', 'ogg', 'aac'].includes(fileExtension);
        
        modalFooter.innerHTML = `
            <div class="d-flex gap-2 w-100 justify-content-between">
                <div class="d-flex gap-2">
                    <a href="${multimediaSrc}" target="_blank" class="btn btn-primary">
                        <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
                    </a>
                    <button type="button" class="btn btn-outline-primary" data-action="${actionType}" data-document-src="${multimediaSrc}" data-document-title="${multimediaTitle || 'archivo'}">
                        <i class="fas fa-download"></i> Descargar
                    </button>
                    ${hasVideoButtons ? `
                        <button type="button" class="btn btn-outline-info" onclick="toggleFullscreen()">
                            <i class="fas fa-expand"></i> Pantalla Completa
                        </button>
                    ` : ''}
                    ${hasAudioButtons ? `
                        <button type="button" class="btn btn-outline-secondary" onclick="setPlaybackRate(0.75)">
                            <i class="fas fa-backward"></i> 0.75x
                        </button>
                        <button type="button" class="btn btn-outline-secondary" onclick="setPlaybackRate(1)">
                            <i class="fas fa-play"></i> Normal
                        </button>
                        <button type="button" class="btn btn-outline-secondary" onclick="setPlaybackRate(1.5)">
                            <i class="fas fa-forward"></i> 1.5x
                        </button>
                    ` : ''}
                </div>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
        `;
    }
    
    // ============================================================================
    // FUNCIONES DE UTILIDAD PARA MULTIMEDIA
    // ============================================================================
    
    // Función para alternar pantalla completa
    function toggleFullscreen() {
        const videoElement = document.querySelector('#multimediaContent video');
        if (!videoElement) return;
        
        if (!document.fullscreenElement) {
            if (videoElement.requestFullscreen) {
                videoElement.requestFullscreen();
            } else if (videoElement.webkitRequestFullscreen) {
                videoElement.webkitRequestFullscreen();
            } else if (videoElement.msRequestFullscreen) {
                videoElement.msRequestFullscreen();
            }
        } else if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
    
    // Función para cambiar velocidad de reproducción
    function setPlaybackRate(rate) {
        const mediaElement = document.querySelector('#multimediaContent video') || 
                            document.querySelector('#multimediaContent audio');
        if (!mediaElement) return;
        
        mediaElement.playbackRate = rate;
    }
    
    // ============================================================================
    // FUNCIONES DE DESCARGA
    // ============================================================================
    
    // Función para descargar archivos S3
    function downloadS3File(fileUrl, fileName) {
        log('Descargando archivo S3:', fileUrl);
        
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
            
            log('Descarga S3 iniciada');
        } catch (error) {
            logError('Error descargando S3:', error);
            alert('Error al descargar: ' + error.message);
        }
    }
    
    // Función para descargar archivos locales
    function downloadLocalFile(fileUrl, fileName) {
        log('Descargando archivo local:', fileUrl);
        
        try {
            const link = document.createElement('a');
            link.href = fileUrl;
            link.download = fileName || 'archivo';
            link.style.display = 'none';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            log('Descarga local iniciada');
        } catch (error) {
            logError('Error descargando local:', error);
            alert('Error al descargar: ' + error.message);
        }
    }
    
    // Función para descargar imagen
    function downloadImage(imageSrc, imageTitle) {
        log('Descargando imagen:', { imageSrc, imageTitle });
        
        // Si no se proveen parámetros, intentar obtener del modal actual
        if (!imageSrc) {
            const modalImage = document.getElementById('modalImage');
            if (!modalImage?.src) {
                logError('No se encontró imagen para descargar');
                return;
            }
            
            imageSrc = modalImage.src;
            imageTitle = modalImage.alt || 'imagen';
        }
        
        try {
            const link = document.createElement('a');
            link.href = imageSrc;
            link.download = imageTitle || 'imagen';
            link.style.display = 'none';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            log('Descarga de imagen iniciada');
        } catch (error) {
            logError('Error descargando imagen:', error);
            alert('Error al descargar imagen: ' + error.message);
        }
    }
    
    // ============================================================================
    // FUNCIONES DE DOCUMENTOS PDF
    // ============================================================================
    
    // Funcionalidad de impresión para PDFs
    function printDocument() {
        log('Imprimiendo documento PDF');
        
        const iframe = document.querySelector('#documentContent iframe');
        if (!iframe) {
            alert('No se encontró documento PDF para imprimir');
            return;
        }
        
        try {
            iframe.contentWindow.focus();
            iframe.contentWindow.print();
        } catch (error) {
            logError('Error al imprimir:', error);
            
            // Fallback usando URL directa
            const printWindow = window.open(iframe.src, '_blank');
            if (printWindow) {
                printWindow.onload = function() {
                    printWindow.print();
                };
            } else {
                alert('Error al abrir ventana de impresión. Verifique que no esté bloqueando ventanas emergentes.');
            }
        }
    }
    
    // Función para rotar documento PDF
    function rotateDocument() {
        log('Rotando documento PDF');
        
        const iframe = document.querySelector('#documentContent iframe');
        if (!iframe) return;
        
        try {
            // Solo funciona si el PDF viewer lo soporta (como PDFjs)
            if (iframe.contentWindow.PDFViewerApplication) {
                const pdfViewer = iframe.contentWindow.PDFViewerApplication.pdfViewer;
                const currentRotation = pdfViewer.pagesRotation;
                pdfViewer.pagesRotation = (currentRotation + 90) % 360;
            } else {
                // Fallback simple usando CSS
                const currentRotation = iframe.style.transform ? 
                    parseInt(iframe.style.transform.replace(/\D/g, '')) || 0 : 0;
                const newRotation = (currentRotation + 90) % 360;
                
                iframe.style.transform = `rotate(${newRotation}deg)`;
                
                if (newRotation === 90 || newRotation === 270) {
                    iframe.style.transformOrigin = 'center center';
                    iframe.style.height = '100%';
                    iframe.style.width = '100%';
                } else {
                    iframe.style.transformOrigin = '';
                    iframe.style.height = '100%';
                    iframe.style.width = '100%';
                }
            }
        } catch (error) {
            logError('Error al rotar documento:', error);
            alert('No se pudo rotar el documento. Esta función puede no estar disponible en todos los visualizadores de PDF.');
        }
    }
    
    // Funciones de zoom para PDF
    function zoomInDocument() {
        log('Zoom + en documento PDF');
        changeZoomPDF(1);
    }
    
    function zoomOutDocument() {
        log('Zoom - en documento PDF');
        changeZoomPDF(-1);
    }
    
    function changeZoomPDF(direction) {
        const iframe = document.querySelector('#documentContent iframe');
        if (!iframe) return;
        
        try {
            // Si el viewer tiene API de zoom (como PDFjs)
            if (iframe.contentWindow.PDFViewerApplication) {
                const pdfViewer = iframe.contentWindow.PDFViewerApplication;
                if (direction > 0) {
                    pdfViewer.zoomIn();
                } else {
                    pdfViewer.zoomOut();
                }
            } else {
                // Fallback simple usando escala CSS
                const currentScale = iframe.style.transform ? 
                    parseFloat(iframe.style.transform.replace(/[^\d.]/g, '')) || 1 : 1;
                
                let newScale;
                if (direction > 0) {
                    newScale = currentScale * 1.25;
                    if (newScale > 3) newScale = 3; // Límite máximo
                } else {
                    newScale = currentScale * 0.8;
                    newScale = Math.max(0.5, newScale); // Límite mínimo
                }
                
                iframe.style.transform = `scale(${newScale})`;
                iframe.style.transformOrigin = 'center top';
            }
        } catch (error) {
            logError('Error al cambiar zoom:', error);
        }
    }
    
    // ============================================================================
    // FUNCIONES DE IMÁGENES
    // ============================================================================
    
    // Variables para control de zoom y rotación de imágenes
    let currentImageScale = 1;
    let currentImageRotation = 0;
    
    // Función para rotar imagen
    function rotateImage() {
        log('Rotando imagen');
        
        const modalImage = document.getElementById('modalImage');
        if (!modalImage) return;
        
        // Incrementar rotación en 90 grados
        currentImageRotation = (currentImageRotation + 90) % 360;
        
        // Aplicar transformación
        updateImageTransform(modalImage);
    }
    
    // Función para cambiar zoom de imagen
    function zoomImage(direction) {
        log('Cambiando zoom de imagen:', direction);
        
        const modalImage = document.getElementById('modalImage');
        if (!modalImage) return;
        
        // Ajustar escala según dirección
        if (direction > 0) {
            currentImageScale *= 1.25;
            if (currentImageScale > 3) currentImageScale = 3; // Límite máximo
        } else {
            currentImageScale *= 0.8;
            if (currentImageScale < 0.5) currentImageScale = 0.5; // Límite mínimo
        }
        
        // Aplicar transformación
        updateImageTransform(modalImage);
    }
    
    // Función para actualizar transformación de imagen
    function updateImageTransform(imageElement) {
        if (!imageElement) return;
        
        imageElement.style.transform = `rotate(${currentImageRotation}deg) scale(${currentImageScale})`;
        imageElement.style.transformOrigin = 'center center';
        
        // Ajustar contenedor si es necesario para rotaciones de 90/270 grados
        if (currentImageRotation === 90 || currentImageRotation === 270) {
            imageElement.style.maxHeight = 'none';
            imageElement.style.maxWidth = '75vh';
        } else {
            imageElement.style.maxHeight = '75vh';
            imageElement.style.maxWidth = '100%';
        }
    }
    
    // Restablecer transformaciones al cerrar modal
    function resetImageTransforms() {
        currentImageScale = 1;
        currentImageRotation = 0;
    }
    
    // ============================================================================
    // INICIALIZACIÓN Y EVENT LISTENERS
    // ============================================================================
    
    // Función para inicializar event listeners para modales
    function setupModalEventListeners() {
        // Listener para restablecer transformaciones al cerrar modal de imagen
        const imageModal = document.getElementById('imageModal');
        if (imageModal) {
            imageModal.addEventListener('hidden.bs.modal', resetImageTransforms);
        }
        
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
    }
    
    // Función para arreglar problema de overflow después de cerrar modales
    function fixModalOverflowIssue() {
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
        }
        
        // Función para añadir listener a un modal
        function addOverflowListenerToModal(modalId) {
            const modalElement = document.getElementById(modalId);
            if (modalElement) {
                modalElement.addEventListener('hidden.bs.modal', function() {
                    // Pequeño retraso para asegurar que otras operaciones de cierre terminen primero
                    setTimeout(restoreOverflow, 100);
                });
            }
        }
        
        // Modales conocidos en la aplicación
        const modalIds = ['imageModal', 'documentModal', 'multimediaModal', 'confirmDeleteModal', 'exportModal'];
        
        // Añadir manejador para restaurar overflow después de cerrar modal
        for (const modalId of modalIds) {
            addOverflowListenerToModal(modalId);
        }
    }
    
    // Función de inicialización principal
    function init() {
        log('Inicializando modal-functions-ALL.js');
        
        // Inyectar estilos globales
        injectGlobalStyles();
        
        // Configurar event listeners
        setupModalEventListeners();
        
        // Arreglar problema de overflow
        fixModalOverflowIssue();
        
        log('Inicialización completada');
    }
    
    // ============================================================================
    // EXPORTAR FUNCIONES A SCOPE GLOBAL
    // ============================================================================
    
    // Exportar funciones de modal
    window.showDocumentModal = showDocumentModal;
    window.showImageModal = showImageModal;
    window.showMultimediaModal = showMultimediaModal;
    
    // Exportar funciones de documentos
    window.printDocument = printDocument;
    window.rotateDocument = rotateDocument;
    window.zoomInDocument = zoomInDocument;
    window.zoomOutDocument = zoomOutDocument;
    
    // Exportar funciones de imagen
    window.downloadImage = downloadImage;
    window.rotateImage = rotateImage;
    window.zoomImage = zoomImage;
    
    // Exportar funciones multimedia
    window.toggleFullscreen = toggleFullscreen;
    window.setPlaybackRate = setPlaybackRate;
    
    // Exportar funciones de descarga
    window.downloadS3File = downloadS3File;
    window.downloadLocalFile = downloadLocalFile;
    
    // Ejecutar inicialización cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // Si el DOM ya está cargado, ejecutar inmediatamente
        init();
    }
    
    // Log final
    log('Versión 1.0 - 8 de octubre de 2025');
    log('Sistema de modales unificado listo');
})();