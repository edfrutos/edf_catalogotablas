/**
 * spreadsheet-handler.js
 * Manejador especializado para hojas de cálculo (Excel) en la aplicación.
 * Este archivo se encarga de mejorar la detección y visualización de archivos Excel
 * y spreadsheets de catálogo que han sido problemáticos.
 */

(function() {
    'use strict';
    
    // Activar modo depuración cuando sea necesario
    const DEBUG_MODE = window.DEBUG_MODE || false;
    
    /**
     * Determina si una URL corresponde a un archivo Excel
     * @param {string} url - URL a verificar
     * @return {boolean} - true si es un archivo Excel
     */
    function isExcelFile(url) {
        if (!url) return false;
        
        // Detección especial para URLs de spreadsheets de catálogo
        if (url.includes('/catalogo/spreadsheets/')) {
            console.log('[EXCEL-HANDLER] Detectada URL de spreadsheet de catálogo:', url);
            return true;
        }
        
        // Detección por extensiones de archivo
        const urlLower = url.toLowerCase();
        if (urlLower.endsWith('.xlsx') || urlLower.endsWith('.xls')) {
            return true;
        }
        
        // Detección por segmento final de URL
        const lastSegment = url.split('/').pop().split('?')[0];
        if (lastSegment.toLowerCase().endsWith('.xlsx') || 
            lastSegment.toLowerCase().endsWith('.xls')) {
            return true;
        }
        
        // No se detectó como Excel
        return false;
    }
    
    /**
     * Normaliza una URL de S3 para asegurar acceso correcto
     * @param {string} url - URL a normalizar
     * @param {string} urlType - Tipo de URL a generar (admin/public)
     * @return {string} - URL normalizada
     */
    function normalizeS3Url(url, urlType = 'admin') {
        if (!url) return '';
        
        // Extraer nombre del archivo
        let fileName;
        
        if (url.includes('/admin/s3/')) {
            fileName = url.substring(url.indexOf('/admin/s3/') + '/admin/s3/'.length);
        } else if (url.includes('s3.eu-central-1.amazonaws.com')) {
            fileName = url.substring(url.indexOf('.com/') + '.com/'.length);
        } else if (url.includes('/catalogo/spreadsheets/')) {
            // Para URLs de spreadsheets de catálogo, mantener la URL completa
            return url;
        } else if (url.includes('/')) {
            fileName = url.split('/').pop();
        } else {
            fileName = url;
        }
        
        // Eliminar parámetros de consulta
        fileName = fileName.split('?')[0];
        
        // Construir URL según tipo solicitado
        if (urlType === 'admin' || urlType === 'internal') {
            return `/admin/s3/${fileName}`;
        } else if (urlType === 'public' || urlType === 'external') {
            return `https://edf-catalogo-tablas.s3.eu-central-1.amazonaws.com/${fileName}`;
        } else {
            return fileName;
        }
    }
    
    /**
     * Manejador especializado para spreadsheets de catálogo
     * @param {HTMLElement} modalContent - Elemento donde insertar el contenido
     * @param {string} documentSrc - URL del documento
     * @param {string} documentTitle - Título del documento
     */
    function handleCatalogoSpreadsheet(modalContent, documentSrc, documentTitle) {
        console.log('[EXCEL-HANDLER] Manejando spreadsheet de catálogo:', documentSrc);
        
        // Extraer ID del spreadsheet
        let spreadsheetId = '';
        if (documentSrc.includes('/catalogo/spreadsheets/')) {
            spreadsheetId = documentSrc.split('/catalogo/spreadsheets/').pop().split('/')[0];
        } else if (documentSrc.includes('spreadsheets/')) {
            spreadsheetId = documentSrc.split('spreadsheets/').pop().split('/')[0];
        }
        
        // Construir URLs para acceso
        const viewUrl = `/admin/catalogo/spreadsheets/${spreadsheetId}`;
        const downloadUrl = `/admin/catalogo/spreadsheets/${spreadsheetId}/download`;
        
        // Preparar contenido del modal
        modalContent.innerHTML = `
            <div class="text-center p-3">
                <i class="fas fa-table fa-3x text-success mb-2"></i>
                <h5>Hoja de Cálculo de Catálogo</h5>
                <p class="text-muted mb-3">
                    <strong>Título:</strong> ${documentTitle || 'Hoja de Cálculo'}<br>
                    <strong>ID:</strong> ${spreadsheetId}<br>
                </p>
                
                <div class="alert alert-info mt-3">
                    <i class="fas fa-info-circle"></i>
                    <strong>Información:</strong> Este tipo de documento debe abrirse en una nueva pestaña para su correcta visualización.
                </div>
                
                <div class="excel-preview mb-4">
                    <div class="text-center py-3 bg-light border rounded">
                        <i class="fas fa-table fa-4x text-success mb-3"></i>
                        <h5>Vista previa no disponible</h5>
                        <p>Por favor, utilice el botón "Abrir en nueva pestaña" para visualizar este documento.</p>
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <div class="d-grid gap-2 d-md-flex justify-content-md-center">
                        <a href="${viewUrl}" target="_blank" class="btn btn-success btn-lg">
                            <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
                        </a>
                        <a href="${downloadUrl}" class="btn btn-outline-success btn-lg">
                            <i class="fas fa-download"></i> Descargar
                        </a>
                    </div>
                </div>
            </div>
        `;
        
        // Configurar botones en el footer
        const modalFooter = document.querySelector('#documentModal .modal-footer');
        if (modalFooter) {
            modalFooter.innerHTML = `
                <div class="d-flex gap-2 w-100 justify-content-between">
                    <div class="d-flex gap-2">
                        <a href="${viewUrl}" target="_blank" class="btn btn-success">
                            <i class="fas fa-external-link-alt"></i> Abrir en Nueva Pestaña
                        </a>
                        <a href="${downloadUrl}" class="btn btn-outline-success">
                            <i class="fas fa-download"></i> Descargar
                        </a>
                    </div>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                </div>
            `;
        }
        
        // Ajustar el tamaño del modal
        const modalDialog = document.querySelector('#documentModal .modal-dialog');
        if (modalDialog) {
            modalDialog.style.maxWidth = '800px';
            modalDialog.style.width = '85%';
        }
        
        return true;
    }
    
    /**
     * Función para modificar el comportamiento del modal estándar
     * para manejar mejor los archivos Excel y spreadsheets
     */
    function enhanceModalFunctions() {
        // Solo proceder si encontramos las funciones necesarias
        if (!window.showDocumentModal) {
            console.error('[EXCEL-HANDLER] No se encuentra la función showDocumentModal');
            return;
        }
        
        console.log('[EXCEL-HANDLER] Mejorando funciones de modal para Excel');
        
        // Guardar referencia a la función original
        const originalShowDocumentModal = window.showDocumentModal;
        
        // Reemplazar con nuestra versión mejorada
        window.showDocumentModal = function(documentSrc, documentTitle) {
            console.log('[EXCEL-HANDLER] Interceptando llamada a showDocumentModal:', documentSrc);
            
            // Verificar si es una URL de catálogo de spreadsheets
            if (documentSrc && documentSrc.includes('/catalogo/spreadsheets/')) {
                console.log('[EXCEL-HANDLER] Detectado spreadsheet de catálogo');
                
                // Buscar elementos del modal
                const modalElement = document.getElementById('documentModal');
                const modalContent = document.getElementById('documentContent');
                const modalTitle = document.getElementById('documentModalLabel');
                
                if (!modalElement || !modalContent || !modalTitle) {
                    console.error('[EXCEL-HANDLER] No se encontraron elementos del modal');
                    return originalShowDocumentModal(documentSrc, documentTitle);
                }
                
                // Configurar título
                modalTitle.textContent = documentTitle || 'Hoja de Cálculo de Catálogo';
                
                // Mostrar modal
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
                
                // Manejar contenido especializado para spreadsheets
                return handleCatalogoSpreadsheet(modalContent, documentSrc, documentTitle);
            }
            
            // Para otros casos, usar la función original
            return originalShowDocumentModal(documentSrc, documentTitle);
        };
        
        // Exponer nuestras funciones mejoradas
        window.isExcelFile = isExcelFile;
        window.normalizeS3Url = normalizeS3Url;
        window.handleCatalogoSpreadsheet = handleCatalogoSpreadsheet;
        
        console.log('[EXCEL-HANDLER] Funciones de modal mejoradas instaladas');
    }
    
    // Auto-iniciar cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        console.log('[EXCEL-HANDLER] Inicializando manejador de Excel');
        enhanceModalFunctions();
    });
    
    // También permitir inicialización manual
    window.initExcelHandler = enhanceModalFunctions;
    
    // Mostrar mensaje de carga
    console.log('[EXCEL-HANDLER] Manejador de Excel cargado correctamente');
})();