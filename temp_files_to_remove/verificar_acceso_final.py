#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import requests
from bs4 import BeautifulSoup
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuración
FLASK_URL = "http://127.0.0.1:8002"
ACCESO_DIRECTO_URL = "http://127.0.0.1:5000"

def verificar_acceso_directo():
    """Verifica que el servidor de acceso directo esté funcionando."""
    try:
        response = requests.get(ACCESO_DIRECTO_URL)
        response.raise_for_status()
        
        if "Acceso Directo a Catálogos" in response.text:
            logger.info("✅ Servidor de acceso directo funcionando correctamente")
            return True
        else:
            logger.warning("❌ Servidor de acceso directo no muestra la página esperada")
            return False
    
    except requests.RequestException as e:
        logger.error(f"❌ Error al acceder al servidor de acceso directo: {str(e)}")
        return False

def obtener_session_admin():
    """Obtiene una sesión de administrador a través del acceso directo."""
    try:
        session = requests.Session()
        response = session.get(f"{ACCESO_DIRECTO_URL}/login_admin")
        response.raise_for_status()
        
        # Verificar redirección a catálogos
        if "/catalogs/" in response.url:
            logger.info("✅ Sesión de administrador obtenida correctamente")
            return session
        else:
            logger.warning(f"❌ No se pudo obtener sesión de administrador (URL final: {response.url})")
            return None
    
    except requests.RequestException as e:
        logger.error(f"❌ Error al obtener sesión de administrador: {str(e)}")
        return None

def obtener_session_usuario():
    """Obtiene una sesión de usuario normal a través del acceso directo."""
    try:
        session = requests.Session()
        response = session.get(f"{ACCESO_DIRECTO_URL}/login_usuario")
        response.raise_for_status()
        
        # Verificar redirección a catálogos
        if "/catalogs/" in response.url:
            logger.info("✅ Sesión de usuario normal obtenida correctamente")
            return session
        else:
            logger.warning(f"❌ No se pudo obtener sesión de usuario normal (URL final: {response.url})")
            return None
    
    except requests.RequestException as e:
        logger.error(f"❌ Error al obtener sesión de usuario normal: {str(e)}")
        return None

def verificar_acceso_catalogs(session, role="admin"):
    """Verifica el acceso a la lista de catálogos."""
    try:
        response = session.get(f"{FLASK_URL}/catalogs/")
        response.raise_for_status()
        
        # Verificar si hay mensajes de error específicos
        if "Error interno: ruta no encontrada o mal configurada" in response.text:
            logger.error(f"❌ [{role}] Se encontró el mensaje de error 'Error interno: ruta no encontrada o mal configurada'")
            return False
        
        if "No tiene permisos para acceder a esta página" in response.text:
            logger.error(f"❌ [{role}] Se encontró el mensaje de error 'No tiene permisos para acceder a esta página'")
            return False
        
        # Verificar si la respuesta contiene elementos que indican acceso exitoso
        if "Crear Nuevo Catálogo" in response.text or "catalogs.html" in response.text:
            logger.info(f"✅ [{role}] Acceso exitoso a la lista de catálogos")
            
            # Extraer información de los catálogos
            soup = BeautifulSoup(response.text, 'html.parser')
            catalogs_table = soup.find('table')
            
            if catalogs_table:
                catalogs_rows = catalogs_table.find_all('tr')[1:]  # Excluir la fila de encabezado
                logger.info(f"✅ [{role}] Se encontraron {len(catalogs_rows)} catálogos")
            else:
                logger.info(f"✅ [{role}] No se encontraron catálogos o no hay tabla de catálogos")
            
            return True
        else:
            logger.warning(f"❌ [{role}] No se encontraron elementos esperados en la página de catálogos")
            return False
    
    except requests.RequestException as e:
        logger.error(f"❌ [{role}] Error al acceder a los catálogos: {str(e)}")
        return False

def obtener_id_primer_catalogo(session, role="admin"):
    """Obtiene el ID del primer catálogo disponible."""
    try:
        response = session.get(f"{FLASK_URL}/catalogs/")
        response.raise_for_status()
        
        # Buscar enlaces a catálogos específicos (excluyendo /catalogs/create)
        soup = BeautifulSoup(response.text, 'html.parser')
        catalog_links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/catalogs/') and '/create' not in href and '/edit' not in href and '/delete' not in href:
                # Asegurarse de que el href tiene el formato /catalogs/{id}
                parts = href.split('/')
                if len(parts) == 3 and parts[1] == 'catalogs' and len(parts[2]) > 0:
                    catalog_links.append(a)
        
        if catalog_links:
            # Extraer el ID del primer catálogo
            href = catalog_links[0]['href']
            catalog_id = href.split('/')[-1]
            logger.info(f"✅ [{role}] ID del primer catálogo encontrado: {catalog_id}")
            return catalog_id
        else:
            logger.warning(f"⚠️ [{role}] No se encontraron catálogos disponibles")
            return None
    
    except requests.RequestException as e:
        logger.error(f"❌ [{role}] Error al obtener el ID del primer catálogo: {str(e)}")
        return None

def verificar_catalogo_especifico(session, catalog_id, role="admin"):
    """Verifica el acceso a un catálogo específico."""
    try:
        response = session.get(f"{FLASK_URL}/catalogs/{catalog_id}")
        response.raise_for_status()
        
        # Verificar si hay mensajes de error específicos
        if "Error interno: ruta no encontrada o mal configurada" in response.text:
            logger.error(f"❌ [{role}] Se encontró el mensaje de error 'Error interno: ruta no encontrada o mal configurada'")
            return False
        
        if "No tiene permisos para acceder a esta página" in response.text:
            logger.error(f"❌ [{role}] Se encontró el mensaje de error 'No tiene permisos para acceder a esta página'")
            return False
        
        # Verificar si la respuesta contiene elementos que indican acceso exitoso
        if "Ver Catálogo" in response.text or "Editar" in response.text or "Agregar Fila" in response.text:
            logger.info(f"✅ [{role}] Acceso exitoso al catálogo {catalog_id}")
            return True
        else:
            logger.warning(f"❌ [{role}] No se pudo acceder al catálogo {catalog_id}")
            return False
    
    except requests.RequestException as e:
        logger.error(f"❌ [{role}] Error al acceder al catálogo {catalog_id}: {str(e)}")
        return False

def main():
    """Función principal que ejecuta la verificación final de acceso a catálogos."""
    logger.info("Iniciando verificación final de acceso a catálogos...")
    
    # Verificar que el servidor de acceso directo esté funcionando
    if not verificar_acceso_directo():
        logger.error("El servidor de acceso directo no está funcionando. Abortando.")
        return False
    
    # Verificar acceso como administrador
    admin_session = obtener_session_admin()
    if admin_session:
        admin_catalogs_ok = verificar_acceso_catalogs(admin_session, "admin")
        admin_catalog_id = obtener_id_primer_catalogo(admin_session, "admin")
        
        if admin_catalog_id:
            admin_catalog_specific_ok = verificar_catalogo_especifico(admin_session, admin_catalog_id, "admin")
        else:
            admin_catalog_specific_ok = None
    else:
        admin_catalogs_ok = False
        admin_catalog_specific_ok = False
        admin_catalog_id = None
    
    # Verificar acceso como usuario normal
    user_session = obtener_session_usuario()
    if user_session:
        user_catalogs_ok = verificar_acceso_catalogs(user_session, "usuario")
        user_catalog_id = obtener_id_primer_catalogo(user_session, "usuario")
        
        if user_catalog_id:
            user_catalog_specific_ok = verificar_catalogo_especifico(user_session, user_catalog_id, "usuario")
        else:
            user_catalog_specific_ok = None
    else:
        user_catalogs_ok = False
        user_catalog_specific_ok = False
        user_catalog_id = None
    
    # Mostrar resumen
    logger.info("\n=== RESUMEN DE VERIFICACIÓN FINAL ===")
    
    # Resultados del administrador
    logger.info("\n1. ACCESO COMO ADMINISTRADOR")
    logger.info(f"  - Sesión obtenida: {'✅ Exitoso' if admin_session else '❌ Fallido'}")
    logger.info(f"  - Acceso a lista de catálogos: {'✅ Exitoso' if admin_catalogs_ok else '❌ Fallido'}")
    
    if admin_catalog_id:
        catalog_specific_status = '✅ Exitoso' if admin_catalog_specific_ok else '❌ Fallido'
        logger.info(f"  - Acceso a catálogo específico ({admin_catalog_id}): {catalog_specific_status}")
    else:
        logger.info("  - Acceso a catálogo específico: ⚠️ No verificado (no se encontraron catálogos)")
    
    # Resultados del usuario normal
    logger.info("\n2. ACCESO COMO USUARIO NORMAL")
    logger.info(f"  - Sesión obtenida: {'✅ Exitoso' if user_session else '❌ Fallido'}")
    logger.info(f"  - Acceso a lista de catálogos: {'✅ Exitoso' if user_catalogs_ok else '❌ Fallido'}")
    
    if user_catalog_id:
        catalog_specific_status = '✅ Exitoso' if user_catalog_specific_ok else '❌ Fallido'
        logger.info(f"  - Acceso a catálogo específico ({user_catalog_id}): {catalog_specific_status}")
    else:
        logger.info("  - Acceso a catálogo específico: ⚠️ No verificado (no se encontraron catálogos)")
    
    # Verificar si la solución fue exitosa
    admin_success = admin_session and admin_catalogs_ok
    user_success = user_session and user_catalogs_ok
    
    if admin_success and user_success:
        logger.info("\n✅ ¡LA SOLUCIÓN HA SIDO EXITOSA!")
        logger.info("Tanto el administrador como el usuario normal pueden acceder correctamente a los catálogos.")
        logger.info("\nURLs de acceso:")
        logger.info(f"- Acceso directo: {ACCESO_DIRECTO_URL}")
        logger.info(f"- Lista de catálogos: {FLASK_URL}/catalogs/")
        
        if admin_catalog_id:
            logger.info(f"- Ver catálogo como administrador: {FLASK_URL}/catalogs/{admin_catalog_id}")
        
        if user_catalog_id:
            logger.info(f"- Ver catálogo como usuario normal: {FLASK_URL}/catalogs/{user_catalog_id}")
        
        return True
    else:
        logger.error("\n❌ LA SOLUCIÓN NO HA SIDO COMPLETAMENTE EXITOSA")
        
        if not admin_success:
            logger.error("El administrador no puede acceder correctamente a los catálogos.")
        
        if not user_success:
            logger.error("El usuario normal no puede acceder correctamente a los catálogos.")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
