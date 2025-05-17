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
BASE_URL = "http://127.0.0.1:8002"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
USER_EMAIL = "usuario@example.com"
USER_PASSWORD = "admin123"

def obtener_csrf_token(html):
    """Extrae el token CSRF del HTML de la página."""
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None

def iniciar_sesion(session, email, password):
    """Inicia sesión en la aplicación."""
    try:
        # Obtener la página de login para extraer el token CSRF
        response = session.get(f"{BASE_URL}/login")
        response.raise_for_status()
        
        csrf_token = obtener_csrf_token(response.text)
        if not csrf_token:
            logger.warning("No se pudo obtener el token CSRF")
        
        # Datos para el inicio de sesión
        login_data = {
            "email": email,
            "password": password,
            "csrf_token": csrf_token
        }
        
        # Enviar solicitud de inicio de sesión
        login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
        login_response.raise_for_status()
        
        # Verificar si el inicio de sesión fue exitoso
        if "dashboard" in login_response.url or "admin" in login_response.url:
            logger.info(f"✅ Inicio de sesión exitoso como {email}")
            return True
        else:
            logger.warning(f"❌ Inicio de sesión fallido como {email}")
            return False
    
    except requests.RequestException as e:
        logger.error(f"Error durante el inicio de sesión: {str(e)}")
        return False

def verificar_acceso_catalogs(session, expected_status=200):
    """Verifica el acceso a la sección de catálogos."""
    try:
        # Intentar acceder a la lista de catálogos
        response = session.get(f"{BASE_URL}/catalogs/")
        
        # Verificar el código de estado
        if response.status_code == expected_status:
            logger.info(f"✅ Acceso a catálogos con código de estado esperado: {response.status_code}")
            
            # Verificar contenido específico
            if "Error interno: ruta no encontrada o mal configurada" in response.text:
                logger.error("❌ Se encontró el mensaje de error 'Error interno: ruta no encontrada o mal configurada'")
                return False
            
            if "No tiene permisos para acceder a esta página" in response.text:
                logger.error("❌ Se encontró el mensaje de error 'No tiene permisos para acceder a esta página'")
                return False
            
            # Verificar si la respuesta contiene elementos que indican acceso exitoso
            if "Crear Nuevo Catálogo" in response.text or "catalogs.html" in response.text:
                logger.info("✅ Contenido de catálogos verificado correctamente")
                return True
            else:
                logger.warning("⚠️ No se encontraron elementos esperados en la página de catálogos")
                return False
        else:
            logger.error(f"❌ Código de estado inesperado: {response.status_code} (esperado: {expected_status})")
            return False
    
    except requests.RequestException as e:
        logger.error(f"Error al acceder a los catálogos: {str(e)}")
        return False

def obtener_id_primer_catalogo(session):
    """Obtiene el ID del primer catálogo disponible."""
    try:
        # Acceder a la lista de catálogos
        response = session.get(f"{BASE_URL}/catalogs/")
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
            logger.info(f"ID del primer catálogo encontrado: {catalog_id}")
            return catalog_id
        else:
            logger.warning("No se encontraron catálogos disponibles")
            return None
    
    except requests.RequestException as e:
        logger.error(f"Error al obtener el ID del primer catálogo: {str(e)}")
        return None
    
    except requests.RequestException as e:
        logger.error(f"Error al obtener el ID del primer catálogo: {str(e)}")
        return None

def verificar_catalogo_especifico(session, catalog_id):
    """Verifica el acceso a un catálogo específico."""
    try:
        # Intentar acceder a un catálogo específico
        response = session.get(f"{BASE_URL}/catalogs/{catalog_id}")
        response.raise_for_status()
        
        # Verificar si hay mensajes de error específicos
        if "Error interno: ruta no encontrada o mal configurada" in response.text:
            logger.error(f"❌ Se encontró el mensaje de error 'Error interno: ruta no encontrada o mal configurada'")
            return False
        
        if "No tiene permisos para acceder a esta página" in response.text:
            logger.error(f"❌ Se encontró el mensaje de error 'No tiene permisos para acceder a esta página'")
            return False
        
        # Verificar si la respuesta contiene elementos que indican acceso exitoso
        if "Ver Catálogo" in response.text or "Editar" in response.text or "Agregar Fila" in response.text:
            logger.info(f"✅ Acceso exitoso al catálogo {catalog_id}")
            return True
        else:
            logger.warning(f"❌ No se pudo acceder al catálogo {catalog_id}")
            return False
    
    except requests.RequestException as e:
        logger.error(f"Error al acceder al catálogo {catalog_id}: {str(e)}")
        return False

def verificar_admin_y_usuario():
    """Verifica el acceso tanto para el administrador como para un usuario normal."""
    # Verificar acceso como administrador
    admin_session = requests.Session()
    admin_login_ok = iniciar_sesion(admin_session, ADMIN_EMAIL, ADMIN_PASSWORD)
    
    if admin_login_ok:
        admin_catalogs_ok = verificar_acceso_catalogs(admin_session)
        admin_catalog_id = obtener_id_primer_catalogo(admin_session)
        
        if admin_catalog_id:
            admin_catalog_specific_ok = verificar_catalogo_especifico(admin_session, admin_catalog_id)
        else:
            admin_catalog_specific_ok = None
            logger.warning("No se pudo verificar el acceso a un catálogo específico como administrador (no se encontraron catálogos)")
    else:
        admin_catalogs_ok = False
        admin_catalog_specific_ok = False
        admin_catalog_id = None
    
    # Verificar acceso como usuario normal
    user_session = requests.Session()
    user_login_ok = iniciar_sesion(user_session, USER_EMAIL, USER_PASSWORD)
    
    if user_login_ok:
        user_catalogs_ok = verificar_acceso_catalogs(user_session)
        user_catalog_id = obtener_id_primer_catalogo(user_session)
        
        if user_catalog_id:
            user_catalog_specific_ok = verificar_catalogo_especifico(user_session, user_catalog_id)
        else:
            user_catalog_specific_ok = None
            logger.warning("No se pudo verificar el acceso a un catálogo específico como usuario normal (no se encontraron catálogos)")
    else:
        user_catalogs_ok = False
        user_catalog_specific_ok = False
        user_catalog_id = None
    
    # Resultados
    resultados = {
        "admin": {
            "login": admin_login_ok,
            "catalogs_access": admin_catalogs_ok,
            "catalog_specific_access": admin_catalog_specific_ok,
            "catalog_id": admin_catalog_id
        },
        "user": {
            "login": user_login_ok,
            "catalogs_access": user_catalogs_ok,
            "catalog_specific_access": user_catalog_specific_ok,
            "catalog_id": user_catalog_id
        }
    }
    
    return resultados

def main():
    """Función principal que ejecuta la verificación final de acceso a catálogos."""
    logger.info("Iniciando verificación final de acceso a catálogos...")
    
    # Verificar acceso como administrador y usuario normal
    resultados = verificar_admin_y_usuario()
    
    # Mostrar resumen
    logger.info("\n=== RESUMEN DE VERIFICACIÓN FINAL ===")
    
    # Resultados del administrador
    logger.info("\n1. ACCESO COMO ADMINISTRADOR")
    logger.info(f"  - Inicio de sesión: {'✅ Exitoso' if resultados['admin']['login'] else '❌ Fallido'}")
    logger.info(f"  - Acceso a lista de catálogos: {'✅ Exitoso' if resultados['admin']['catalogs_access'] else '❌ Fallido'}")
    
    if resultados['admin']['catalog_id']:
        catalog_specific_status = '✅ Exitoso' if resultados['admin']['catalog_specific_access'] else '❌ Fallido'
        logger.info(f"  - Acceso a catálogo específico ({resultados['admin']['catalog_id']}): {catalog_specific_status}")
    else:
        logger.info("  - Acceso a catálogo específico: ⚠️ No verificado (no se encontraron catálogos)")
    
    # Resultados del usuario normal
    logger.info("\n2. ACCESO COMO USUARIO NORMAL")
    logger.info(f"  - Inicio de sesión: {'✅ Exitoso' if resultados['user']['login'] else '❌ Fallido'}")
    logger.info(f"  - Acceso a lista de catálogos: {'✅ Exitoso' if resultados['user']['catalogs_access'] else '❌ Fallido'}")
    
    if resultados['user']['catalog_id']:
        catalog_specific_status = '✅ Exitoso' if resultados['user']['catalog_specific_access'] else '❌ Fallido'
        logger.info(f"  - Acceso a catálogo específico ({resultados['user']['catalog_id']}): {catalog_specific_status}")
    else:
        logger.info("  - Acceso a catálogo específico: ⚠️ No verificado (no se encontraron catálogos)")
    
    # Verificar si la solución fue exitosa
    admin_success = resultados['admin']['login'] and resultados['admin']['catalogs_access']
    user_success = resultados['user']['login'] and resultados['user']['catalogs_access']
    
    if admin_success and user_success:
        logger.info("\n✅ ¡LA SOLUCIÓN HA SIDO EXITOSA!")
        logger.info("Tanto el administrador como el usuario normal pueden acceder correctamente a los catálogos.")
        logger.info("\nURLs de acceso:")
        logger.info(f"- Lista de catálogos: {BASE_URL}/catalogs/")
        
        if resultados['admin']['catalog_id']:
            logger.info(f"- Ver catálogo como administrador: {BASE_URL}/catalogs/{resultados['admin']['catalog_id']}")
        
        if resultados['user']['catalog_id']:
            logger.info(f"- Ver catálogo como usuario normal: {BASE_URL}/catalogs/{resultados['user']['catalog_id']}")
        
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
