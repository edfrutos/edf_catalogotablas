// Script para convertir enlaces usados como botones a elementos button reales
document.addEventListener('DOMContentLoaded', function() {
    // Buscar todos los enlaces que previenen el comportamiento predeterminado (a href="#" con onclick que contiene event.preventDefault)
    const fakeButtons = document.querySelectorAll('a[href="#"][onclick*="event.preventDefault"]');
    
    fakeButtons.forEach(link => {
        // Crear un nuevo botón
        const button = document.createElement('button');
        
        // Copiar atributos
        for (const attr of link.attributes) {
            if (attr.name !== 'href') { // No copiar el atributo href
                button.setAttribute(attr.name, attr.value);
            }
        }
        
        // Asegurarse de que tiene type="button"
        if (!button.getAttribute('type')) {
            button.setAttribute('type', 'button');
        }
        
        // Copiar todas las clases
        button.className = link.className;
        
        // Copiar el contenido interno
        button.innerHTML = link.innerHTML;
        
        // Reemplazar el enlace con el botón
        link.parentNode.replaceChild(button, link);
    });

    // También buscar enlaces que usen showMultimediaModal, showPyWebViewDocument o showDocumentModal
    const otherFakeButtons = document.querySelectorAll('a[onclick*="showMultimediaModal"], a[onclick*="showPyWebViewDocument"], a[onclick*="showDocumentModal"]');
    
    otherFakeButtons.forEach(link => {
        if (link.getAttribute('href') === '#') {
            // Crear un nuevo botón
            const button = document.createElement('button');
            
            // Copiar atributos
            for (const attr of link.attributes) {
                if (attr.name !== 'href') { // No copiar el atributo href
                    button.setAttribute(attr.name, attr.value);
                }
            }
            
            // Asegurarse de que tiene type="button"
            if (!button.getAttribute('type')) {
                button.setAttribute('type', 'button');
            }
            
            // Copiar todas las clases
            button.className = link.className;
            
            // Copiar el contenido interno
            button.innerHTML = link.innerHTML;
            
            // Reemplazar el enlace con el botón
            link.parentNode.replaceChild(button, link);
        }
    });
});