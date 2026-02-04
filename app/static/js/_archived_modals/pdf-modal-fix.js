/**
 * PDF MODAL FIX - SOLUCIÓN PARA MODALES DE PDF
 * Script para solucionar problemas con la visualización de PDF en modales
 * Versión: 1.0 (8 de octubre de 2025)
 */

// Auto-ejecutable para aislar el alcance de las variables
(function() {
    // Intentar usar la configuración de depuración
    let DEBUG_MODE = false;
    
    try {
        if (typeof getDebugMode === 'function') {
            DEBUG_MODE = getDebugMode();
        } else if (typeof window.APP_CONFIG !== 'undefined') {
            DEBUG_MODE = window.APP_CONFIG.DEBUG_MODE;
        }
    } catch (error) {
        console.warn('No se pudo cargar la configuración de depuración para pdf-modal-fix.js');
    }
    
    // Función para logging condicional
    function log(message) {
        if (DEBUG_MODE) {
            if (typeof window.APP_CONFIG !== 'undefined' && typeof window.APP_CONFIG.log === 'function') {
                window.APP_CONFIG.log(`[PDF-MODAL-FIX] ${message}`);
            } else {
                console.log(`[PDF-MODAL-FIX] ${message}`);
            }
        }
    }
    
    // Función principal para corregir los modales de PDF
    function fixPdfModals() {
        log('Aplicando correcciones a modales de PDF');
        
        // Añadir estilos globales para modales de PDF
        const style = document.createElement('style');
        style.id = 'pdf-modal-fix-styles';
        style.textContent = `
            /* Estilos para corregir visualización de PDF en modales - v1.0 */
            #documentModal .modal-dialog {
                max-width: 95% !important;
                width: 90% !important;
                margin: 1rem auto !important;
                height: 90vh !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            
            #documentModal .modal-content {
                height: 90vh !important;
                max-height: 90vh !important;
                display: flex !important;
                flex-direction: column !important;
                overflow: hidden !important;
            }
            
            #documentModal .modal-header {
                flex-shrink: 0 !important;
            }
            
            #documentModal .modal-footer {
                flex-shrink: 0 !important;
                padding: 0.5rem 1rem !important;
            }
            
            #documentModal .modal-body {
                flex: 1 1 auto !important;
                overflow-y: hidden !important;
                padding: 0 !important;
                position: relative !important;
            }
            
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
            
            /* Ajustes para contenedor de información de PDF */
            .pdf-viewer-container {
                width: 100% !important;
                height: 100% !important;
                position: relative !important;
                overflow: hidden !important;
            }
            
            /* Corregir espacios en botones del footer */
            #documentModal .modal-footer .d-flex {
                width: 100% !important;
                justify-content: space-between !important;
                gap: 0.5rem !important;
            }
            
            /* Corrección para botones que quedan fuera en móviles */
            @media (max-width: 768px) {
                #documentModal .modal-footer .d-flex {
                    flex-wrap: wrap !important;
                }
                
                #documentModal .modal-footer .btn {
                    margin-bottom: 0.25rem !important;
                    font-size: 0.875rem !important;
                }
                
                #documentModal .modal-dialog {
                    width: 95% !important;
                    margin: 0.5rem auto !important;
                }
            }
        `;
        
        // Verificar si ya existe el estilo antes de añadirlo
        if (!document.getElementById('pdf-modal-fix-styles')) {
            document.head.appendChild(style);
            log('Estilos globales para modales de PDF añadidos');
        }
    }
    
    // Función para corregir documento modal cuando se muestra
    function setupDocumentModalListener() {
        const documentModal = document.getElementById('documentModal');
        if (documentModal) {
            documentModal.addEventListener('show.bs.modal', function() {
                log('Evento show.bs.modal del modal de documento detectado');
                
                // Aplicar correcciones específicas para el modal de documento
                setTimeout(() => {
                    const modalDialog = documentModal.querySelector('.modal-dialog');
                    const modalContent = documentModal.querySelector('.modal-content');
                    const modalBody = documentModal.querySelector('.modal-body');
                    const documentContent = document.getElementById('documentContent');
                    
                    if (modalDialog && modalContent && modalBody && documentContent) {
                        // Detectar si es un PDF buscando iframe en el contenido
                        const hasPdfIframe = documentContent.querySelector('iframe') !== null;
                        
                        if (hasPdfIframe) {
                            log('PDF iframe detectado, aplicando optimizaciones específicas');
                            
                            // Ajustar dimensiones para visualización óptima
                            modalDialog.style.maxWidth = '95%';
                            modalDialog.style.width = '90%';
                            modalDialog.style.height = '90vh';
                            
                            modalContent.style.height = '90vh';
                            modalContent.style.maxHeight = '90vh';
                            modalContent.style.display = 'flex';
                            modalContent.style.flexDirection = 'column';
                            
                            modalBody.style.flex = '1 1 auto';
                            modalBody.style.overflow = 'hidden';
                            modalBody.style.padding = '0';
                            
                            // Optimizar contenedor de PDF
                            document.querySelectorAll('.pdf-viewer-container').forEach(container => {
                                container.style.width = '100%';
                                container.style.height = '100%';
                                container.style.position = 'relative';
                                
                                // Optimizar iframe de PDF
                                const iframe = container.querySelector('iframe');
                                if (iframe) {
                                    iframe.style.width = '100%';
                                    iframe.style.height = '100%';
                                    iframe.style.border = 'none';
                                    iframe.style.position = 'absolute';
                                    iframe.style.top = '0';
                                    iframe.style.left = '0';
                                    iframe.style.right = '0';
                                    iframe.style.bottom = '0';
                                }
                            });
                            
                            // Optimizar contenedor de información de PDF si existe
                            const pdfInfoDiv = documentContent.querySelector('.text-center.p-3');
                            if (pdfInfoDiv) {
                                pdfInfoDiv.style.padding = '0.5rem';
                                pdfInfoDiv.style.marginBottom = '0';
                                pdfInfoDiv.style.background = '#f8f9fa';
                                pdfInfoDiv.style.borderBottom = '1px solid #dee2e6';
                                
                                // Hacer la información más compacta
                                const icon = pdfInfoDiv.querySelector('.fa-file-pdf');
                                if (icon) icon.classList.remove('fa-3x');
                                
                                // Eliminar márgenes innecesarios
                                const heading = pdfInfoDiv.querySelector('h5');
                                if (heading) heading.style.margin = '0.25rem';
                                
                                const paragraph = pdfInfoDiv.querySelector('p');
                                if (paragraph) {
                                    paragraph.style.margin = '0.25rem';
                                    paragraph.style.fontSize = '0.875rem';
                                }
                            }
                        }
                    }
                }, 50);
            });
            
            // También manejar eventos después de que el modal está completamente mostrado
            documentModal.addEventListener('shown.bs.modal', function() {
                log('Evento shown.bs.modal del modal de documento detectado');
                
                // Verificar si hay un iframe de PDF
                const documentContent = document.getElementById('documentContent');
                if (documentContent) {
                    const iframe = documentContent.querySelector('iframe');
                    if (iframe) {
                        log('Optimizando iframe de PDF después de mostrar el modal');
                        // Asegurar que el iframe tiene el tamaño correcto
                        iframe.style.width = '100%';
                        iframe.style.height = '100%';
                    }
                }
            });
            
            log('Listener para modal de documento configurado');
        } else {
            log('Modal de documento no encontrado en el DOM');
        }
    }
    
    // Comprobar si necesitamos sobreescribir la función showDocumentModal
    function enhanceShowDocumentModal() {
        // Solo sobreescribir si existe la función original
        if (typeof window.showDocumentModal === 'function') {
            log('Mejorando función showDocumentModal existente');
            
            // Guardar referencia a la función original
            const originalShowDocumentModal = window.showDocumentModal;
            
            // Sobreescribir con versión mejorada
            window.showDocumentModal = function(documentSrc, documentTitle) {
                log('showDocumentModal mejorado llamado:', { documentSrc, documentTitle });
                
                // Llamar a la función original
                originalShowDocumentModal(documentSrc, documentTitle);
                
                // Ejecutar mejoras adicionales después de un breve retraso
                setTimeout(() => {
                    // Detectar si es un PDF
                    const isPdf = documentSrc.toLowerCase().endsWith('.pdf');
                    
                    if (isPdf) {
                        log('Documento PDF detectado, aplicando optimizaciones específicas');
                        
                        const documentContent = document.getElementById('documentContent');
                        if (!documentContent) return;
                        
                        // Buscar iframe de PDF
                        const iframe = documentContent.querySelector('iframe');
                        if (iframe) {
                            // Crear un contenedor para el iframe si no existe
                            let container = iframe.closest('.pdf-viewer-container');
                            if (!container) {
                                log('Creando contenedor optimizado para PDF');
                                container = document.createElement('div');
                                container.className = 'pdf-viewer-container';
                                iframe.parentNode.insertBefore(container, iframe);
                                container.appendChild(iframe);
                            }
                            
                            // Optimizar contenedor e iframe
                            container.style.width = '100%';
                            container.style.height = '100%';
                            container.style.position = 'relative';
                            
                            iframe.style.width = '100%';
                            iframe.style.height = '100%';
                            iframe.style.border = 'none';
                            iframe.style.position = 'absolute';
                            iframe.style.top = '0';
                            iframe.style.left = '0';
                        }
                    }
                }, 200);
            };
            
            log('Función showDocumentModal mejorada instalada');
        } else {
            log('Función showDocumentModal no encontrada, no se puede mejorar');
        }
    }
    
    // Inicialización cuando el DOM esté listo
    function init() {
        log('Inicializando solución para modales de PDF');
        fixPdfModals();
        setupDocumentModalListener();
        enhanceShowDocumentModal();
        log('Solución para modales de PDF instalada');
    }
    
    // Ejecutar al cargar la página
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // Si el DOM ya está cargado, ejecutar inmediatamente
        init();
    }
})();