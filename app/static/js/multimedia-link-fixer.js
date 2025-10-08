/**
 * SOLUCIÓN PARA ENLACES MULTIMEDIA Y YOUTUBE
 * 
 * Este script analiza la página HTML después de que se carga
 * y modifica los enlaces multimedia que se mostrarían en una
 * nueva pestaña para que en su lugar se muestren en un modal.
 * 
 * Versión: 1.0.0 (2025-10-08)
 */

// Función principal para inicializar el corrector de enlaces multimedia
function initMultimediaLinkFixer() {
    console.group('🛠️ Inicialización del corrector de enlaces multimedia');
    
    // Función para extraer URL de YouTube del texto
    function extractYouTubeUrl(text) {
        if (text.includes('youtube.com/watch?v=')) {
            const startIdx = text.indexOf('youtube.com/watch?v=');
            if (startIdx >= 0) {
                const fullUrl = 'https://www.' + text.substring(startIdx);
                // Extraer solo la URL sin texto adicional
                const urlEnd = fullUrl.search(/[\s"'<>]/);
                return urlEnd > 0 ? fullUrl.substring(0, urlEnd) : fullUrl;
            }
        } else if (text.includes('youtu.be/')) {
            const startIdx = text.indexOf('youtu.be/');
            if (startIdx >= 0) {
                const fullUrl = 'https://' + text.substring(startIdx);
                // Extraer solo la URL sin texto adicional
                const urlEnd = fullUrl.search(/[\s"'<>]/);
                return urlEnd > 0 ? fullUrl.substring(0, urlEnd) : fullUrl;
            }
        }
        return null;
    }
    
    // 1. Corregir botones "Ver Multimedia" con URLs de YouTube
    function fixMultimediaButtons() {
        const buttons = document.querySelectorAll('a.btn');
        let modifiedCount = 0;
        
        buttons.forEach(button => {
            if (button.textContent.includes('Ver Multimedia')) {
                // Buscar si hay un valor multimedia cerca
                const row = button.closest('tr');
                
                if (row) {
                    // Buscar texto que contenga URL de YouTube en la fila
                    const cells = row.querySelectorAll('td');
                    let youtubeUrl = null;
                    
                    cells.forEach(cell => {
                        const extractedUrl = extractYouTubeUrl(cell.textContent);
                        if (extractedUrl) youtubeUrl = extractedUrl;
                    });
                    
                    if (youtubeUrl) {
                        console.log(`🔍 Botón "Ver Multimedia" encontrado cerca de: ${youtubeUrl}`);
                        
                        // Modificar el botón para usar modal
                        button.setAttribute('href', 'javascript:void(0)');
                        button.setAttribute('data-action', 'show-multimedia-modal');
                        button.setAttribute('data-media-url', youtubeUrl);
                        button.setAttribute('data-media-name', 'Video de YouTube');
                        
                        modifiedCount++;
                    }
                }
            }
        });
        
        console.log(`✅ ${modifiedCount} botones "Ver Multimedia" modificados`);
        return modifiedCount;
    }
    
    // 2. Procesar directamente las celdas con "Valor multimedia no reconocido"
    function fixUnrecognizedMultimedia() {
        let modifiedCount = 0;
        
        // Primera estrategia: buscar exactamente por el texto "Valor multimedia no reconocido"
        document.querySelectorAll('td').forEach(cell => {
            if (cell.textContent.includes('Valor multimedia no reconocido')) {
                const row = cell.closest('tr');
                if (!row) return;
                
                // Extraer la URL de YouTube del texto
                const youtubeUrl = extractYouTubeUrl(cell.textContent);
                if (!youtubeUrl) return;
                
                console.log(`🔍 Celda con "Valor multimedia no reconocido" encontrada: ${youtubeUrl}`);
                
                // Buscar botón "Ver Multimedia" en la misma fila
                const buttons = row.querySelectorAll('a.btn, button.btn');
                let buttonFound = false;
                
                buttons.forEach(button => {
                    if (button.textContent.includes('Ver Multimedia')) {
                        // Modificar el botón existente
                        button.setAttribute('href', 'javascript:void(0)');
                        button.setAttribute('data-action', 'show-multimedia-modal');
                        button.setAttribute('data-media-url', youtubeUrl);
                        button.setAttribute('data-media-name', 'Video de YouTube');
                        buttonFound = true;
                        modifiedCount++;
                    }
                });
                
                // Si no hay botón, crear uno nuevo
                if (!buttonFound) {
                    const newButton = document.createElement('a');
                    newButton.setAttribute('href', 'javascript:void(0)');
                    newButton.setAttribute('data-action', 'show-multimedia-modal');
                    newButton.setAttribute('data-media-url', youtubeUrl);
                    newButton.setAttribute('data-media-name', 'Video de YouTube');
                    newButton.className = 'btn btn-sm btn-outline-primary ml-2';
                    newButton.innerHTML = '<i class="fab fa-youtube"></i> Ver en Modal';
                    
                    // Agregarlo junto al texto
                    cell.appendChild(document.createElement('br'));
                    cell.appendChild(newButton);
                    modifiedCount++;
                }
            }
        });
        
        console.log(`✅ ${modifiedCount} elementos "Valor multimedia no reconocido" procesados`);
        return modifiedCount;
    }
    
    // 3. Aplicar corrección específica para la imagen capturada
    function fixCapturedExample() {
        // Buscar especialmente la tabla con el identificador mostrado en la captura
        const rows = document.querySelectorAll('tr');
        let modifiedCount = 0;
        
        rows.forEach((row, index) => {
            // Buscar fila específica que contenga "2025-09-29" y valor multimedia no reconocido
            const cells = row.querySelectorAll('td');
            let hasDate = false;
            let hasYoutubeUrl = null;
            let buttonCell = null;
            
            cells.forEach(cell => {
                if (cell.textContent.includes('2025-09-29')) {
                    hasDate = true;
                }
                
                if (cell.textContent.includes('youtube.com/watch?v=') || 
                    cell.textContent.includes('youtu.be/')) {
                    hasYoutubeUrl = extractYouTubeUrl(cell.textContent);
                }
                
                // Detectar celda con botones
                if (cell.querySelector('a.btn')) {
                    buttonCell = cell;
                }
            });
            
            // Si encontramos la fila específica
            if (hasDate && hasYoutubeUrl && buttonCell) {
                console.log(`🎯 Fila específica de la captura encontrada (#${index + 1}): ${hasYoutubeUrl}`);
                
                // Modificar todos los botones en esta celda
                const buttons = buttonCell.querySelectorAll('a.btn');
                buttons.forEach(button => {
                    button.setAttribute('href', 'javascript:void(0)');
                    button.setAttribute('data-action', 'show-multimedia-modal');
                    button.setAttribute('data-media-url', hasYoutubeUrl);
                    button.setAttribute('data-media-name', 'Video de YouTube');
                    modifiedCount++;
                });
            }
        });
        
        console.log(`✅ ${modifiedCount} elementos específicos de la captura corregidos`);
        return modifiedCount;
    }
    
    // Ejecutar todas las funciones de corrección
    const totalModified = 
        fixMultimediaButtons() + 
        fixUnrecognizedMultimedia() + 
        fixCapturedExample();
    
    console.log(`🏁 Corrección de enlaces multimedia completada: ${totalModified} modificaciones`);
    console.groupEnd();
}

// Iniciar cuando la página esté completamente cargada
document.addEventListener('DOMContentLoaded', function() {
    // Asegurarse de que los scripts necesarios estén cargados
    if (typeof showMultimediaModal === 'function' || typeof window.showMultimediaModal === 'function') {
        console.log('✅ showMultimediaModal está disponible, aplicando correcciones...');
        setTimeout(initMultimediaLinkFixer, 500); // Pequeño retraso para asegurar que todo está cargado
    } else {
        console.warn('⚠️ showMultimediaModal no está disponible, intentando nuevamente en 1 segundo...');
        setTimeout(function() {
            if (typeof showMultimediaModal === 'function' || typeof window.showMultimediaModal === 'function') {
                console.log('✅ showMultimediaModal está ahora disponible, aplicando correcciones...');
                initMultimediaLinkFixer();
            } else {
                console.error('❌ showMultimediaModal sigue sin estar disponible, no se pueden aplicar correcciones');
            }
        }, 1000);
    }
});