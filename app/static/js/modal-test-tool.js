/**
 * Herramienta de prueba para modales
 * Esta herramienta prueba todos los tipos de modales y verifica que funcionan correctamente
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
        console.warn('No se pudo cargar la configuración de depuración para modal-test-tool.js', error);
        DEBUG_MODE = false; // Establecer un valor por defecto en caso de error
    }
    
    // Función para logging condicional
    function log(message) {
        if (DEBUG_MODE) {
            if (typeof window.APP_CONFIG !== 'undefined' && typeof window.APP_CONFIG.log === 'function') {
                window.APP_CONFIG.log(`[MODAL-TEST] ${message}`);
            } else {
                console.log(`[MODAL-TEST] ${message}`);
            }
        }
    }
    
    // URLs de prueba
    const TEST_ASSETS = {
        image: '/static/img/test-image.jpg',
        document: '/static/uploads/test-document.pdf',
        video: '/static/uploads/test-video.mp4',
        audio: '/static/uploads/test-audio.mp3'
    };
    
    // Crear botón de prueba
    function createTestButton() {
        // Verificar si el botón ya existe
        if (document.getElementById('modal-test-button')) {
            return;
        }
        
        const buttonContainer = document.createElement('div');
        buttonContainer.style.position = 'fixed';
        buttonContainer.style.bottom = '70px';
        buttonContainer.style.right = '10px';
        buttonContainer.style.zIndex = '9999';
        buttonContainer.style.display = 'flex';
        buttonContainer.style.flexDirection = 'column';
        buttonContainer.style.gap = '5px';
        
        const mainButton = document.createElement('button');
        mainButton.textContent = '🧪 Probar Modales';
        mainButton.id = 'modal-test-button';
        mainButton.style.padding = '8px 12px';
        mainButton.style.backgroundColor = '#28a745';
        mainButton.style.color = 'white';
        mainButton.style.border = 'none';
        mainButton.style.borderRadius = '4px';
        mainButton.style.cursor = 'pointer';
        mainButton.style.fontSize = '12px';
        mainButton.style.opacity = '0.7';
        
        mainButton.onmouseover = function() {
            this.style.opacity = '1';
        };
        
        mainButton.onmouseout = function() {
            this.style.opacity = '0.7';
        };
        
        mainButton.onclick = function() {
            showTestOptions();
        };
        
        buttonContainer.appendChild(mainButton);
        document.body.appendChild(buttonContainer);
        
        log('Botón de prueba de modales añadido');
    }
    
    // Mostrar opciones de prueba
    function showTestOptions() {
        // Eliminar opciones anteriores si existen
        const oldOptions = document.getElementById('modal-test-options');
        if (oldOptions) {
            oldOptions.remove();
        }
        
        const options = document.createElement('div');
        options.id = 'modal-test-options';
        options.style.position = 'fixed';
        options.style.bottom = '110px';
        options.style.right = '10px';
        options.style.zIndex = '9999';
        options.style.backgroundColor = 'white';
        options.style.padding = '10px';
        options.style.borderRadius = '5px';
        options.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
        options.style.width = '180px';
        
        const title = document.createElement('h6');
        title.textContent = 'Seleccione un tipo de prueba:';
        title.style.margin = '0 0 10px 0';
        title.style.fontSize = '12px';
        title.style.fontWeight = 'bold';
        options.appendChild(title);
        
        const tests = [
            { name: 'Imagen', action: testImageModal, icon: '🖼️' },
            { name: 'Documento', action: testDocumentModal, icon: '📄' },
            { name: 'Video', action: testVideoModal, icon: '🎬' },
            { name: 'Audio', action: testAudioModal, icon: '🔊' },
            { name: 'Todos', action: testAllModals, icon: '🧪' },
            { name: 'Cerrar', action: () => options.remove(), icon: '❌' }
        ];
        
        tests.forEach(test => {
            const button = document.createElement('button');
            button.textContent = `${test.icon} ${test.name}`;
            button.style.display = 'block';
            button.style.width = '100%';
            button.style.padding = '5px';
            button.style.margin = '3px 0';
            button.style.backgroundColor = test.name === 'Cerrar' ? '#f8f9fa' : '#e9ecef';
            button.style.border = '1px solid #dee2e6';
            button.style.borderRadius = '3px';
            button.style.cursor = 'pointer';
            button.style.fontSize = '12px';
            button.style.textAlign = 'left';
            
            button.onmouseover = function() {
                this.style.backgroundColor = test.name === 'Cerrar' ? '#e9ecef' : '#d1ecf1';
            };
            
            button.onmouseout = function() {
                this.style.backgroundColor = test.name === 'Cerrar' ? '#f8f9fa' : '#e9ecef';
            };
            
            button.onclick = function() {
                test.action();
                options.remove();
            };
            
            options.appendChild(button);
        });
        
        document.body.appendChild(options);
    }
    
    // Pruebas individuales de modales
    function testImageModal() {
        log('Probando modal de imagen');
        if (typeof showImageModal === 'function') {
            showImageModal(TEST_ASSETS.image || '/static/img/placeholder.jpg', 'Imagen de Prueba');
            return true;
        } else {
            alert('Error: La función showImageModal no está disponible');
            return false;
        }
    }
    
    function testDocumentModal() {
        log('Probando modal de documento');
        if (typeof showDocumentModal === 'function') {
            showDocumentModal(TEST_ASSETS.document || '/static/uploads/test.pdf', 'Documento de Prueba');
            return true;
        } else {
            alert('Error: La función showDocumentModal no está disponible');
            return false;
        }
    }
    
    function testVideoModal() {
        log('Probando modal de video');
        if (typeof showMultimediaModal === 'function') {
            showMultimediaModal(TEST_ASSETS.video || '/static/uploads/test.mp4', 'Video de Prueba');
            return true;
        } else {
            alert('Error: La función showMultimediaModal no está disponible');
            return false;
        }
    }
    
    function testAudioModal() {
        log('Probando modal de audio');
        if (typeof showMultimediaModal === 'function') {
            showMultimediaModal(TEST_ASSETS.audio || '/static/uploads/test.mp3', 'Audio de Prueba');
            return true;
        } else {
            alert('Error: La función showMultimediaModal no está disponible');
            return false;
        }
    }
    
    // Crear un modal para mostrar resultados de prueba
    function showModalResults(results) {
        let modalContent = `
            <h5>Resultados de la prueba</h5>
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Modal</th>
                        <th>Resultado</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Imagen</td>
                        <td>${results.image ? '✅ OK' : '❌ Error'}</td>
                    </tr>
                    <tr>
                        <td>Documento</td>
                        <td>${results.document ? '✅ OK' : '❌ Error'}</td>
                    </tr>
                    <tr>
                        <td>Video</td>
                        <td>${results.video ? '✅ OK' : '❌ Error'}</td>
                    </tr>
                    <tr>
                        <td>Audio</td>
                        <td>${results.audio ? '✅ OK' : '❌ Error'}</td>
                    </tr>
                </tbody>
            </table>
        `;
        
        const modalElement = document.getElementById('scriptResultModal');
        const modalContentElement = document.getElementById('scriptResultContent');
        
        if (modalElement && modalContentElement) {
            const modalTitleElement = document.getElementById('scriptResultModalLabel');
            if (modalTitleElement) {
                modalTitleElement.textContent = 'Resultados de Prueba de Modales';
            }
            
            modalContentElement.innerHTML = modalContent;
            
            if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
            } else {
                alert('No se pudo mostrar el modal de resultados: Bootstrap no está disponible');
            }
        } else {
            alert('No se pudo mostrar el modal de resultados: Elementos no encontrados');
        }
    }
    
    // Ejecutar prueba de audio y continuar con los resultados
    function runAudioTest(results) {
        try {
            results.audio = testAudioModal();
            
            const multimediaModal = document.getElementById('multimediaModal');
            if (multimediaModal) {
                multimediaModal.addEventListener('hidden.bs.modal', function onHidden() {
                    multimediaModal.removeEventListener('hidden.bs.modal', onHidden);
                    showModalResults(results);
                });
            } else {
                showModalResults(results);
            }
        } catch (error) {
            log('Error en prueba de audio: ' + error.message);
            results.audio = false;
            showModalResults(results);
        }
    }
    
    // Ejecutar prueba de video y continuar con audio
    function runVideoTest(results) {
        try {
            results.video = testVideoModal();
            
            const multimediaModal = document.getElementById('multimediaModal');
            if (multimediaModal) {
                multimediaModal.addEventListener('hidden.bs.modal', function onHidden() {
                    multimediaModal.removeEventListener('hidden.bs.modal', onHidden);
                    runAudioTest(results);
                });
            } else {
                runAudioTest(results);
            }
        } catch (error) {
            log('Error en prueba de video: ' + error.message);
            results.video = false;
            runAudioTest(results);
        }
    }
    
    // Ejecutar prueba de documento y continuar con video
    function runDocumentTest(results) {
        try {
            results.document = testDocumentModal();
            
            const documentModal = document.getElementById('documentModal');
            if (documentModal) {
                documentModal.addEventListener('hidden.bs.modal', function onHidden() {
                    documentModal.removeEventListener('hidden.bs.modal', onHidden);
                    runVideoTest(results);
                });
            } else {
                runVideoTest(results);
            }
        } catch (error) {
            log('Error en prueba de documento: ' + error.message);
            results.document = false;
            runVideoTest(results);
        }
    }
    
    // Probar todos los tipos de modal en secuencia
    function testAllModals() {
        log('Iniciando prueba de todos los modales');
        
        let results = {
            image: false,
            document: false,
            video: false,
            audio: false
        };
        
        // Iniciar la cadena de pruebas con el modal de imagen
        try {
            results.image = testImageModal();
            
            const imageModal = document.getElementById('imageModal');
            if (imageModal) {
                imageModal.addEventListener('hidden.bs.modal', function onHidden() {
                    imageModal.removeEventListener('hidden.bs.modal', onHidden);
                    runDocumentTest(results);
                });
            } else {
                runDocumentTest(results);
            }
        } catch (error) {
            log('Error en prueba de imagen: ' + error.message);
            results.image = false;
            runDocumentTest(results);
        }
    }
    
    // Inicializar herramienta cuando el DOM esté listo
    function init() {
        if (DEBUG_MODE) {
            log('Inicializando herramienta de prueba de modales');
            createTestButton();
        }
    }
    
    // Ejecutar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();