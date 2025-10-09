/**
 * YOUTUBE MODAL FIX - SOLUCIÓN ESPECÍFICA PARA ENLACES DE YOUTUBE
 * Versión: 1.0 (2025-10-08)
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 [YOUTUBE-FIX] Iniciando solución para enlaces de YouTube...');
    
    // Función para detectar enlaces de YouTube en la página
    function detectYouTubeLinks() {
        // Buscar enlaces a YouTube (que contienen youtube.com o youtu.be)
        const youtubeLinks = document.querySelectorAll('a[href*="youtube.com"], a[href*="youtu.be"]');
        console.log(`🔍 [YOUTUBE-FIX] Enlaces de YouTube encontrados: ${youtubeLinks.length}`);
        
        // Convertir cada enlace para que use el modal
        youtubeLinks.forEach(function(link, index) {
            // Verificar si ya tiene data-action
            if (!link.hasAttribute('data-action')) {
                const href = link.getAttribute('href');
                
                // Guardar la URL original
                link.setAttribute('data-media-url', href);
                
                // Establecer un título predeterminado o usar el texto del enlace
                const title = link.textContent.trim() || `Video de YouTube ${index + 1}`;
                link.setAttribute('data-media-name', title);
                
                // Configurar para usar el modal
                link.setAttribute('data-action', 'show-multimedia-modal');
                link.setAttribute('href', 'javascript:void(0)');
                
                // Registrar el cambio
                console.log(`✅ [YOUTUBE-FIX] Enlace #${index + 1} configurado: ${href}`);
                
                // Opcionalmente agregar clases para mejor presentación
                if (!link.classList.contains('btn') && !link.parentElement.classList.contains('btn')) {
                    link.classList.add('youtube-modal-link');
                }
            }
        });
    }
    
    // Detectar enlaces de YouTube específicamente en tablas
    function detectYouTubeInTables() {
        // Buscar todas las celdas de tabla que contienen enlaces a YouTube
        const tableCells = document.querySelectorAll('td a[href*="youtube.com"], td a[href*="youtu.be"]');
        console.log(`🔍 [YOUTUBE-FIX] Enlaces de YouTube en tablas: ${tableCells.length}`);
        
        tableCells.forEach(function(link, index) {
            // Verificar si ya tiene data-action
            if (!link.hasAttribute('data-action')) {
                const href = link.getAttribute('href');
                const cell = link.closest('td');
                const valueText = cell.textContent.trim();
                
                // Registrar el contenido
                console.log(`🔍 [YOUTUBE-FIX] Contenido de celda #${index + 1}: "${valueText}" con URL: ${href}`);
                
                // Guardar la URL original
                link.setAttribute('data-media-url', href);
                
                // Establecer un título predeterminado o usar el texto de la celda
                const title = link.textContent.trim() || `Video de YouTube ${index + 1}`;
                link.setAttribute('data-media-name', title);
                
                // Configurar para usar el modal
                link.setAttribute('data-action', 'show-multimedia-modal');
                link.setAttribute('href', 'javascript:void(0)');
                
                // Marcar con una clase especial
                link.classList.add('youtube-link-in-table');
            }
        });
    }

    // Función para extraer URL de YouTube de un texto
    function extractYoutubeUrl(text) {
        let youtubeUrl = '';
        
        if (text.includes('youtube.com/watch?v=')) {
            const start = text.indexOf('youtube.com/watch?v=');
            const end = text.indexOf(' ', start);
            youtubeUrl = text.substring(start - 8, end > 0 ? end : text.length);
        } else if (text.includes('youtu.be/')) {
            const start = text.indexOf('youtu.be/');
            const end = text.indexOf(' ', start);
            youtubeUrl = text.substring(start - 8, end > 0 ? end : text.length);
        }
        
        return youtubeUrl;
    }
    
    // Función para configurar un botón existente con los atributos para el modal de YouTube
    function configureExistingButton(button, youtubeUrl) {
        button.setAttribute('data-action', 'show-multimedia-modal');
        button.setAttribute('data-media-url', youtubeUrl);
        button.setAttribute('data-media-name', 'Video de YouTube');
        button.setAttribute('href', 'javascript:void(0)');
        console.log('✅ [YOUTUBE-FIX] Botón existente configurado para modal');
    }
    
    // Función para crear un nuevo botón para YouTube
    function createYoutubeButton(youtubeUrl) {
        const newButton = document.createElement('a');
        newButton.setAttribute('data-action', 'show-multimedia-modal');
        newButton.setAttribute('data-media-url', youtubeUrl);
        newButton.setAttribute('data-media-name', 'Video de YouTube');
        newButton.setAttribute('href', 'javascript:void(0)');
        newButton.className = 'btn btn-sm btn-outline-primary mt-2';
        newButton.innerHTML = '<i class="fab fa-youtube text-danger"></i> Ver en Modal';
        return newButton;
    }
    
    // Función para procesar una celda de tabla que contiene URL de YouTube
    function processYoutubeCell(cell) {
        const youtubeUrl = extractYoutubeUrl(cell.textContent);
        
        if (youtubeUrl) {
            console.log(`🔍 [YOUTUBE-FIX] URL de YouTube encontrada en texto: ${youtubeUrl}`);
            
            // Si ya hay un botón "Ver Multimedia" en la celda, configúralo
            const existingButtons = cell.querySelectorAll('a.btn, button.btn');
            if (existingButtons.length > 0) {
                existingButtons.forEach(btn => {
                    configureExistingButton(btn, youtubeUrl);
                });
            } else {
                // Crear un nuevo botón
                const newButton = createYoutubeButton(youtubeUrl);
                
                // Añadir al final de la celda
                cell.appendChild(document.createElement('br'));
                cell.appendChild(newButton);
                console.log('✅ [YOUTUBE-FIX] Nuevo botón creado para YouTube');
            }
        }
    }
    
    // Buscar específicamente el enlace de la tabla como el de la captura
    function fixCapturedYoutubeLink() {
        // Buscar elementos específicamente como los mostrados en la captura
        const youtubeElements = document.querySelectorAll('td:contains("Valor multimedia no reconocido")');
        
        if (youtubeElements.length === 0) {
            // Alternativa: buscar por el contenido del texto
            const allCells = document.querySelectorAll('td');
            allCells.forEach(cell => {
                if (cell.textContent.includes('youtube.com/watch?v=') || 
                    cell.textContent.includes('youtu.be/')) {
                    processYoutubeCell(cell);
                }
            });
        }
    }

    // Ejecutar todas las funciones de corrección
    detectYouTubeLinks();
    detectYouTubeInTables();
    fixCapturedYoutubeLink();
    
    console.log('✅ [YOUTUBE-FIX] Configuración completada');
});