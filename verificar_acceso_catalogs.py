#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
import requests
import re
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
ALTERNATIVE_ADMIN = "edefrutos"
ALTERNATIVE_PASSWORD = "Edefrutos2025!"

def obtener_csrf_token(html):
    """Extrae el token CSRF del HTML de la página."""
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None

def iniciar_sesion(session, email, password):
    """Inicia sesión en la aplicación."""
    # Obtener la página de login para extraer el token CSRF
    try:
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

def verificar_acceso_catalogs(session):
    """Verifica el acceso a la sección de catálogos."""
    try:
        # Intentar acceder a la lista de catálogos
        response = session.get(f"{BASE_URL}/catalogs/")
        response.raise_for_status()
        
        # Verificar si la respuesta contiene elementos que indican acceso exitoso
        if "No hay catálogos disponibles" in response.text or "Crear Nuevo Catálogo" in response.text or "catalogs.html" in response.text:
            logger.info("✅ Acceso exitoso a la lista de catálogos")
            return True
        else:
            logger.warning("❌ No se pudo acceder a la lista de catálogos")
            logger.debug(f"Contenido de la respuesta: {response.text[:500]}...")
            return False
    
    except requests.RequestException as e:
        logger.error(f"Error al acceder a los catálogos: {str(e)}")
        return False

def verificar_catalogo_especifico(session, catalog_id):
    """Verifica el acceso a un catálogo específico."""
    try:
        # Intentar acceder a un catálogo específico
        response = session.get(f"{BASE_URL}/catalogs/{catalog_id}")
        response.raise_for_status()
        
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

def obtener_id_primer_catalogo(session):
    """Obtiene el ID del primer catálogo disponible."""
    try:
        # Acceder a la lista de catálogos
        response = session.get(f"{BASE_URL}/catalogs/")
        response.raise_for_status()
        
        # Buscar enlaces a catálogos específicos
        soup = BeautifulSoup(response.text, 'html.parser')
        catalog_links = soup.find_all('a', href=re.compile(r'/catalogs/[a-f0-9]+$'))
        
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

def main():
    """Función principal que ejecuta la verificación de acceso a catálogos."""
    logger.info("Iniciando verificación de acceso a catálogos...")
    
    # Crear sesión para mantener las cookies
    session = requests.Session()
    
    # Intentar iniciar sesión con las credenciales principales
    if not iniciar_sesion(session, ADMIN_EMAIL, ADMIN_PASSWORD):
        # Si falla, intentar con las credenciales alternativas
        logger.info("Intentando con credenciales alternativas...")
        if not iniciar_sesion(session, ALTERNATIVE_ADMIN, ALTERNATIVE_PASSWORD):
            logger.error("No se pudo iniciar sesión con ninguna de las credenciales")
            return False
    
    # Verificar acceso a la lista de catálogos
    if not verificar_acceso_catalogs(session):
        logger.error("No se pudo acceder a la lista de catálogos")
        return False
    
    # Obtener el ID del primer catálogo y verificar acceso
    catalog_id = obtener_id_primer_catalogo(session)
    if catalog_id:
        if not verificar_catalogo_especifico(session, catalog_id):
            logger.error(f"No se pudo acceder al catálogo {catalog_id}")
            return False
    else:
        logger.warning("No se encontraron catálogos para verificar el acceso individual")
    
    # Resumen
    logger.info("\n=== RESUMEN DE LA VERIFICACIÓN ===")
    logger.info("1. Inicio de sesión: ✅ Exitoso")
    logger.info("2. Acceso a lista de catálogos: ✅ Exitoso")
    if catalog_id:
        logger.info(f"3. Acceso a catálogo específico ({catalog_id}): ✅ Exitoso")
    else:
        logger.info("3. Acceso a catálogo específico: ⚠️ No verificado (no hay catálogos)")
    
    logger.info("\n¡La verificación de acceso a catálogos ha sido exitosa!")
    logger.info("Ahora puedes acceder a los catálogos desde la interfaz web en:")
    logger.info(f"  {BASE_URL}/catalogs/")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
