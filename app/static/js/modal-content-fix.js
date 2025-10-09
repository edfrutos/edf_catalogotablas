/**
 * SOLUCIÓN PARA MODALES DESBORDADOS
 * Este script corrige el problema donde el contenido de los modales se sale de la ventana
 * Versión: 1.1 (8 de octubre de 2025) - Integración mejorada con debug-config.js
 */

// Auto-ejecutable para aislar el alcance de las variables
(function() {
    // Usar el sistema centralizado de logging si está disponible
    let DEBUG_MODE = false;
    
    // Detectar configuración de depuración
    try {
        if (typeof getDebugMode === 'function') {
            DEBUG_MODE = getDebugMode();
        } else if (typeof window.APP_CONFIG !== 'undefined') {
            DEBUG_MODE = window.APP_CONFIG.DEBUG_MODE;
        }
    } catch (error) {
        console.warn('No se pudo cargar la configuración de depuración para modal-content-fix.js', error);
        DEBUG_MODE = false; // Usar valor por defecto en caso de error
    }
    
    // Función para logging condicional
    function log(message) {
        if (DEBUG_MODE) {
            if (typeof window.APP_CONFIG !== 'undefined' && typeof window.APP_CONFIG.log === 'function') {
                window.APP_CONFIG.log(`[MODAL-OVERFLOW] ${message}`);
            } else {
                console.log(`[MODAL-OVERFLOW] ${message}`);
            }
        }
    }
    
    // Función principal para corregir todos los modales
    function fixModalOverflow() {
        log('Aplicando correcciones a modales');
        
        // Añadir estilos globales para todos los modales
        const style = document.createElement('style');
        style.id = 'modal-overflow-fix-styles';
        style.textContent = `
            /* Estilos para corregir overflow en modales - v1.1 */
            .modal-dialog {
                max-width: 95% !important;
                max-height: 95vh !important;
                margin: 1rem auto !important;
                display: flex !important;
                align-items: center !important;
            }
            
            .modal-content {
                max-height: 90vh !important;
                overflow-y: hidden !important;
                width: 100% !important;
            }
            
            .modal-body {
                overflow-y: auto !important;
                max-height: calc(90vh - 120px) !important;
                padding: 1rem !important;
            }
            
            /* Ajustes para imágenes en modales */
            .modal-img-display,
            .modal img:not(.emoji):not(.image-gallery-thumbnail),
            #modalImage {
                max-width: 100% !important;
                max-height: 70vh !important;
                object-fit: contain !important;
                display: block !important;
                margin: 0 auto !important;
            }
            
            /* Ajustes para iframes en modales */
            .modal iframe {
                max-width: 100% !important;
                max-height: 70vh !important;
                width: 100% !important;
            }
            
            /* Ajustes para tablas en modales */
            .modal table {
                width: 100% !important;
                max-width: 100% !important;
                display: block !important;
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch !important;
            }
            
            /* Evitar que el modal-backdrop bloquee la interacción pero mantener opacidad */
            .modal-backdrop {
                pointer-events: none !important;
            }
            
            /* Asegurar que los botones del footer tengan suficiente espacio */
            .modal-footer {
                flex-wrap: wrap !important;
                gap: 0.5rem !important;
                justify-content: space-between !important;
            }
            
            /* Ajustes específicos para modales de documentos con iframe */
            #documentContent iframe {
                width: 100% !important;
                max-height: 65vh !important;
                border: none !important;
            }
            
            /* Solución específica para spinner de carga */
            .modal-spinner-container {
                position: relative !important;
                min-height: 200px !important;
            }
            
            /* Media queries para diferentes tamaños de pantalla */
            @media (max-width: 768px) {
                .modal-dialog {
                    max-width: 98% !important;
                    margin: 0.5rem auto !important;
                }
                
                .modal-body {
                    max-height: calc(90vh - 100px) !important;
                    padding: 0.75rem !important;
                }
            }
            
            @media (max-width: 576px) {
                .modal-dialog {
                    margin: 0.25rem auto !important;
                }
                
                .modal-body {
                    padding: 0.5rem !important;
                }
                
                .modal-footer {
                    flex-direction: column-reverse !important;
                }
                
                .modal-footer .btn {
                    width: 100% !important;
                    margin: 0.25rem 0 !important;
                }
            }
        `;
        
        // Verificar si ya existe el estilo antes de añadirlo
        if (!document.getElementById('modal-overflow-fix-styles')) {
            document.head.appendChild(style);
            log('Estilos globales para modales añadidos');
        }
    }
    
    // Función para corregir modales específicos después de que se muestren
    function setupModalListeners() {
        // Lista de IDs de modales conocidos
        const modalIds = ['imageModal', 'documentModal', 'multimediaModal', 'confirmDeleteModal', 'exportModal'];
        
        modalIds.forEach(modalId => {
            const modalElement = document.getElementById(modalId);
            if (modalElement) {
                // Corregir al mostrar el modal
                modalElement.addEventListener('shown.bs.modal', function() {
                    fixSpecificModal(modalElement);
                });
                
                log(`Listener para ${modalId} configurado`);
            }
        });
        
        // Evento global para todos los modales
        document.addEventListener('shown.bs.modal', function(event) {
            fixSpecificModal(event.target);
        });
        
        // Funciones auxiliares para reducir el anidamiento
        function processNode(node) {
            if (node.nodeType === 1 && node.classList?.contains('modal')) {
                fixSpecificModal(node);
            }
        }
        
        function processMutation(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(processNode);
            }
        }
        
        // Observer para detectar nuevos modales añadidos dinámicamente
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(processMutation);
        });
        
        // Observar cambios en el body para detectar nuevos modales
        observer.observe(document.body, { childList: true });
        log('Observer para nuevos modales configurado');
        
        // Ajustar modales al cambiar tamaño de ventana
        window.addEventListener('resize', function() {
            const openModals = document.querySelectorAll('.modal.show');
            if (openModals.length > 0) {
                log(`Reajustando ${openModals.length} modal(es) por cambio de tamaño de ventana`);
                openModals.forEach(modal => fixSpecificModal(modal));
            }
        });
    }
    
    // Función para corregir un modal específico
    function fixSpecificModal(modalElement) {
        if (!modalElement) return;
        
        // Verificar si ya se procesó este modal
        if (modalElement.dataset.overflowFixed === 'true') {
            // Si ya se procesó, solo actualizar dimensiones
            adjustModalDimensions(modalElement);
            return;
        }
        
        log(`Corrigiendo modal: ${modalElement.id || 'anónimo'}`);
        
        // Marcar como procesado para evitar múltiples aplicaciones
        modalElement.dataset.overflowFixed = 'true';
        
        // Ajustar dimensiones del contenido del modal
        adjustModalDimensions(modalElement);
        
        // Agregar clase para identificar que está mejorado
        modalElement.classList.add('overflow-fixed-modal');
    }
    
    function adjustModalDimensions(modalElement) {
        // Ajustar dimensiones del contenido del modal
        const modalDialog = modalElement.querySelector('.modal-dialog');
        const modalContent = modalElement.querySelector('.modal-content');
        const modalBody = modalElement.querySelector('.modal-body');
        const modalHeader = modalElement.querySelector('.modal-header');
        const modalFooter = modalElement.querySelector('.modal-footer');
        
        if (modalDialog && modalContent && modalBody) {
            // Ajustar tamaño máximo basado en la ventana
            const windowHeight = window.innerHeight;
            const windowWidth = window.innerWidth;
            const dialogMaxHeight = windowHeight * 0.9;
            
            // Calcular la altura del header y footer
            const headerHeight = modalHeader ? modalHeader.offsetHeight : 0;
            const footerHeight = modalFooter ? modalFooter.offsetHeight : 0;
            
            // Calcular la altura del cuerpo
            const bodyMaxHeight = dialogMaxHeight - headerHeight - footerHeight - 20; // 20px extra para márgenes
            
            // Aplicar dimensiones
            modalDialog.style.maxHeight = dialogMaxHeight + 'px';
            modalContent.style.maxHeight = dialogMaxHeight + 'px';
            modalBody.style.maxHeight = bodyMaxHeight + 'px';
            modalBody.style.overflowY = 'auto';
            modalBody.style.overflowX = 'hidden';
            
            // Ajustar anchura en pantallas pequeñas
            if (windowWidth < 768) {
                modalDialog.style.maxWidth = '95%';
            }
            
            // Tratar diferentes tipos de contenido según el ID del modal
            if (modalElement.id === 'imageModal') {
                handleImageModal(modalElement, bodyMaxHeight);
            } else if (modalElement.id === 'documentModal') {
                handleDocumentModal(modalElement, bodyMaxHeight);
            } else if (modalElement.id === 'multimediaModal') {
                handleMultimediaModal(modalElement, bodyMaxHeight);
            } else {
                // Modal genérico
                handleGenericModal(modalElement, bodyMaxHeight);
            }
            
            log(`Dimensiones de modal ajustadas: altura máxima ${bodyMaxHeight}px`);
        }
    }
    
    function handleImageModal(modalElement, maxHeight) {
        const modalImg = modalElement.querySelector('#modalImage, .modal-img-display');
        if (modalImg) {
            modalImg.style.maxHeight = (maxHeight * 0.95) + 'px';
            modalImg.style.maxWidth = '100%';
            modalImg.style.objectFit = 'contain';
            modalImg.style.display = 'block';
            modalImg.style.margin = '0 auto';
            
            // Asegurar visibilidad
            modalImg.style.visibility = 'visible';
            modalImg.style.opacity = '1';
            
            log('Imagen en modal ajustada');
            
            // Eliminar spinner cuando la imagen esté cargada
            modalImg.onload = function() {
                const spinner = modalElement.querySelector('.spinner-border');
                if (spinner) spinner.style.display = 'none';
            };
        }
    }
    
    function handleDocumentModal(modalElement, maxHeight) {
        const contentDiv = modalElement.querySelector('#documentContent');
        if (!contentDiv) return;
        
        const iframe = contentDiv.querySelector('iframe');
        if (iframe) {
            iframe.style.maxHeight = (maxHeight * 0.95) + 'px';
            iframe.style.width = '100%';
            iframe.style.border = 'none';
            log('Iframe de documento en modal ajustado');
        }
        
        // Tratar tablas en documentos
        const tables = contentDiv.querySelectorAll('table');
        tables.forEach(table => {
            table.style.width = '100%';
            table.style.maxWidth = '100%';
            table.style.overflowX = 'auto';
            table.style.display = 'block';
        });
    }
    
    function handleMultimediaModal(modalElement, maxHeight) {
        const contentDiv = modalElement.querySelector('#multimediaContent');
        if (!contentDiv) return;
        
        const video = contentDiv.querySelector('video');
        if (video) {
            video.style.maxHeight = (maxHeight * 0.95) + 'px';
            video.style.maxWidth = '100%';
            video.controls = true;
            video.style.display = 'block';
            video.style.margin = '0 auto';
            log('Video en modal ajustado');
        }
        
        const audio = contentDiv.querySelector('audio');
        if (audio) {
            audio.style.width = '100%';
            audio.controls = true;
            audio.style.display = 'block';
            audio.style.margin = '20px auto';
            log('Audio en modal ajustado');
        }
    }
    
    function handleGenericModal(modalElement, maxHeight) {
        const modalBody = modalElement.querySelector('.modal-body');
        if (!modalBody) return;
        
        // Ajustar imágenes genéricas
        const images = modalBody.querySelectorAll('img:not(.emoji):not(.image-gallery-thumbnail)');
        images.forEach(img => {
            img.style.maxWidth = '100%';
            img.style.maxHeight = (maxHeight * 0.9) + 'px';
            img.style.objectFit = 'contain';
        });
        
        // Ajustar iframes
        const iframes = modalBody.querySelectorAll('iframe');
        iframes.forEach(iframe => {
            iframe.style.maxWidth = '100%';
            iframe.style.maxHeight = (maxHeight * 0.9) + 'px';
        });
        
        // Ajustar tablas
        const tables = modalBody.querySelectorAll('table');
        tables.forEach(table => {
            // Crear un contenedor para la tabla si no está dentro de uno
            if (table.parentElement.tagName !== 'DIV' || !table.parentElement.classList.contains('table-wrapper')) {
                const wrapper = document.createElement('div');
                wrapper.classList.add('table-wrapper');
                wrapper.style.width = '100%';
                wrapper.style.overflowX = 'auto';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }
            
            table.style.width = '100%';
            table.style.tableLayout = 'auto';
        });
    }
    
    // Inicialización cuando el DOM esté listo
    function init() {
        log('Inicializando solución para modales desbordados');
        fixModalOverflow();
        setupModalListeners();
        log('Solución para modales desbordados instalada');
    }
    
    // Ejecutar al cargar la página
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        // Si el DOM ya está cargado, ejecutar inmediatamente
        init();
    }
})();