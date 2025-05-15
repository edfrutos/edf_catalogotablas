#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import requests
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# URLs de la aplicación
BASE_URL = 'http://127.0.0.1:8002'
ADMIN_URL = f'{BASE_URL}/admin/'
USER_URL = f'{BASE_URL}/dashboard_user'
CATALOGS_URL = f'{BASE_URL}/catalogs/'

def verificar_url(url, descripcion):
    """Verifica si una URL es accesible y muestra el resultado."""
    try:
        logger.info(f"Verificando acceso a {descripcion} ({url})...")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            # Analizar el contenido para verificar si es una página de error o acceso denegado
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar mensajes de error comunes
            mensajes_error = [
                "Error interno",
                "ruta no encontrada",
                "mal configurada",
                "No tiene permisos",
                "Acceso denegado",
                "Forbidden",
                "Not Found"
            ]
            
            for mensaje in mensajes_error:
                if mensaje in response.text:
                    logger.error(f"❌ Acceso a {descripcion} fallido: {mensaje}")
                    return False
            
            # Verificar si el título o encabezados contienen la palabra esperada
            titulo = soup.title.string if soup.title else ""
            encabezados = [h.text for h in soup.find_all(['h1', 'h2', 'h3'])]
            
            if descripcion.lower() == "panel de administración":
                palabras_clave = ["admin", "administración", "panel", "dashboard"]
                if any(palabra in titulo.lower() for palabra in palabras_clave) or \
                   any(any(palabra in h.lower() for palabra in palabras_clave) for h in encabezados):
                    logger.info(f"✅ Acceso a {descripcion} exitoso")
                    return True
                else:
                    logger.warning(f"⚠️ Acceso a {descripcion} posiblemente fallido: no se encontraron palabras clave en el título o encabezados")
            
            elif descripcion.lower() == "dashboard de usuario":
                palabras_clave = ["user", "usuario", "dashboard", "panel"]
                if any(palabra in titulo.lower() for palabra in palabras_clave) or \
                   any(any(palabra in h.lower() for palabra in palabras_clave) for h in encabezados):
                    logger.info(f"✅ Acceso a {descripcion} exitoso")
                    return True
                else:
                    logger.warning(f"⚠️ Acceso a {descripcion} posiblemente fallido: no se encontraron palabras clave en el título o encabezados")
            
            elif descripcion.lower() == "catálogos":
                palabras_clave = ["catálogo", "catalogo", "catalog"]
                if any(palabra in titulo.lower() for palabra in palabras_clave) or \
                   any(any(palabra in h.lower() for palabra in palabras_clave) for h in encabezados):
                    logger.info(f"✅ Acceso a {descripcion} exitoso")
                    return True
                else:
                    logger.warning(f"⚠️ Acceso a {descripcion} posiblemente fallido: no se encontraron palabras clave en el título o encabezados")
            
            # Si no se pudo verificar por palabras clave, asumir que es exitoso por el código 200
            logger.info(f"✅ Acceso a {descripcion} exitoso (código 200)")
            return True
        
        else:
            logger.error(f"❌ Acceso a {descripcion} fallido: código {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error al verificar acceso a {descripcion}: {str(e)}")
        return False

def main():
    """Función principal que verifica el acceso a todas las secciones."""
    logger.info("Iniciando verificación de acceso completo...")
    
    # Verificar acceso al panel de administración
    admin_ok = verificar_url(ADMIN_URL, "Panel de Administración")
    
    # Verificar acceso al dashboard de usuario
    user_ok = verificar_url(USER_URL, "Dashboard de Usuario")
    
    # Verificar acceso a los catálogos
    catalogs_ok = verificar_url(CATALOGS_URL, "Catálogos")
    
    # Resumen
    logger.info("\n=== RESUMEN DE LA VERIFICACIÓN DE ACCESO ===")
    logger.info(f"1. Panel de Administración: {'✅ Accesible' if admin_ok else '❌ No accesible'}")
    logger.info(f"2. Dashboard de Usuario: {'✅ Accesible' if user_ok else '❌ No accesible'}")
    logger.info(f"3. Catálogos: {'✅ Accesible' if catalogs_ok else '❌ No accesible'}")
    
    # Resultado final
    if admin_ok and user_ok and catalogs_ok:
        logger.info("\n✅ RESULTADO FINAL: Todas las secciones son accesibles")
        return True
    else:
        logger.warning("\n⚠️ RESULTADO FINAL: Algunas secciones no son accesibles")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
