/**
 * QUICK FIX VALOR MULTIMEDIA - PARCHE ESPECÍFICO PARA LA CAPTURA
 * Versión: 1.0 (2025-10-08)
 */

// Esta función se ejecutará automáticamente cuando se cargue la página
(function() {
    // Esperar a que el DOM esté completamente cargado
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 [QUICK-FIX] Iniciando parche específico para valor multimedia...');
        
        // Buscar elementos que contienen "Valor multimedia no reconocido"
        const elementos = document.querySelectorAll('*:contains("Valor multimedia no reconocido")');
        console.log(`🔍 [QUICK-FIX] Elementos encontrados: ${elementos.length}`);
        
        elementos.forEach(function(elem) {
            // Verificar si el elemento contiene un enlace a YouTube
            if (elem.textContent.includes('youtube.com/watch?v=') || elem.textContent.includes('youtu.be/')) {
                console.log('🔍 [QUICK-FIX] Elemento con enlace a YouTube encontrado');
                
                // Extraer la URL de YouTube
                let youtubeUrl = '';
                const text = elem.textContent;
                
                if (text.includes('youtube.com/watch?v=')) {
                    const startIdx = text.indexOf('youtube.com/watch?v=');
                    youtubeUrl = 'https://www.' + text.substring(startIdx).split(' ')[0];
                } else if (text.includes('youtu.be/')) {
                    const startIdx = text.indexOf('youtu.be/');
                    youtubeUrl = 'https://' + text.substring(startIdx).split(' ')[0];
                }
                
                console.log(`🔍 [QUICK-FIX] URL extraída: ${youtubeUrl}`);
                
                // Buscar el botón "Ver Multimedia" cercano
                const buttons = elem.parentElement.querySelectorAll('a.btn');
                buttons.forEach(function(btn) {
                    if (btn.textContent.includes('Ver Multimedia')) {
                        console.log('🔍 [QUICK-FIX] Botón "Ver Multimedia" encontrado, modificando...');
                        
                        // Modificar el botón para que use el modal
                        btn.setAttribute('href', 'javascript:void(0)');
                        btn.setAttribute('data-action', 'show-multimedia-modal');
                        btn.setAttribute('data-media-url', youtubeUrl);
                        btn.setAttribute('data-media-name', 'Video de YouTube');
                        
                        console.log('✅ [QUICK-FIX] Botón modificado correctamente');
                    }
                });
            }
        });
        
        // Solución alternativa usando selectores de atributos
        const verMultimediaLinks = document.querySelectorAll('a[href*="youtube.com"], a[href*="youtu.be"]');
        verMultimediaLinks.forEach(function(link) {
            const href = link.getAttribute('href');
            console.log(`🔍 [QUICK-FIX] Enlace directo encontrado: ${href}`);
            
            // Modificar para usar el modal
            link.setAttribute('href', 'javascript:void(0)');
            link.setAttribute('data-action', 'show-multimedia-modal');
            link.setAttribute('data-media-url', href);
            link.setAttribute('data-media-name', 'Video de YouTube');
            
            console.log('✅ [QUICK-FIX] Enlace directo modificado correctamente');
        });
        
        console.log('✅ [QUICK-FIX] Parche completado');
    });
})();