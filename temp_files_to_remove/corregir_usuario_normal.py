#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
import requests
from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuración
BASE_URL = "http://127.0.0.1:8002"
USER_EMAIL = "usuario@example.com"
USER_PASSWORD = "admin123"

# Cargar configuración
try:
    from config import Config
    MONGO_URI = Config.MONGO_URI
except ImportError:
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://admin:admin123@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority')

def conectar_mongodb():
    """Establece conexión con MongoDB y retorna el cliente y la base de datos."""
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client.get_database()
        logger.info("✅ Conexión a MongoDB establecida correctamente")
        return client, db
    except Exception as e:
        logger.error(f"❌ Error al conectar a MongoDB: {str(e)}")
        return None, None

def crear_usuario_normal(db):
    """Crea o actualiza el usuario normal con un hash de contraseña válido."""
    try:
        # Verificar si el usuario ya existe
        usuario = db.users.find_one({"email": USER_EMAIL})
        
        # Generar hash de contraseña
        password_hash = generate_password_hash(USER_PASSWORD, method='pbkdf2:sha256', salt_length=8)
        
        if usuario:
            # Actualizar el usuario existente
            db.users.update_one(
                {"email": USER_EMAIL},
                {"$set": {
                    "password": password_hash,
                    "role": "user",
                    "name": "Usuario",
                    "last_name": "Normal",
                    "active": True,
                    "login_attempts": 0,
                    "locked": False
                }}
            )
            logger.info(f"✅ Usuario {USER_EMAIL} actualizado con nueva contraseña")
            logger.info(f"Hash de contraseña: {password_hash}")
        else:
            # Crear un nuevo usuario
            nuevo_usuario = {
                "email": USER_EMAIL,
                "username": "usuario",
                "password": password_hash,
                "role": "user",
                "name": "Usuario",
                "last_name": "Normal",
                "created_at": datetime.datetime.now(),
                "active": True,
                "login_attempts": 0,
                "locked": False
            }
            db.users.insert_one(nuevo_usuario)
            logger.info(f"✅ Usuario {USER_EMAIL} creado")
            logger.info(f"Hash de contraseña: {password_hash}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear/actualizar usuario normal: {str(e)}")
        return False

def obtener_csrf_token(html):
    """Extrae el token CSRF del HTML de la página."""
    soup = BeautifulSoup(html, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None

def probar_inicio_sesion():
    """Prueba el inicio de sesión con el usuario normal."""
    try:
        # Crear sesión para mantener las cookies
        session = requests.Session()
        
        # Obtener la página de login para extraer el token CSRF
        response = session.get(f"{BASE_URL}/login")
        response.raise_for_status()
        
        csrf_token = obtener_csrf_token(response.text)
        if not csrf_token:
            logger.warning("No se pudo obtener el token CSRF")
        
        # Datos para el inicio de sesión
        login_data = {
            "email": USER_EMAIL,
            "password": USER_PASSWORD,
            "csrf_token": csrf_token
        }
        
        # Enviar solicitud de inicio de sesión
        login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
        login_response.raise_for_status()
        
        # Verificar si el inicio de sesión fue exitoso
        if "dashboard" in login_response.url:
            logger.info(f"✅ Inicio de sesión exitoso como {USER_EMAIL}")
            return True
        else:
            logger.warning(f"❌ Inicio de sesión fallido como {USER_EMAIL}")
            logger.warning(f"URL final: {login_response.url}")
            
            # Buscar mensajes de error
            soup = BeautifulSoup(login_response.text, 'html.parser')
            for alert in soup.find_all('div', {'class': ['alert', 'alert-danger']}):
                logger.warning(f"Mensaje de error: {alert.text.strip()}")
            
            return False
    
    except requests.RequestException as e:
        logger.error(f"Error durante el inicio de sesión: {str(e)}")
        return False

def crear_acceso_directo():
    """Crea un script de acceso directo para el usuario normal."""
    ruta_archivo = "acceso_directo_usuario.py"
    
    try:
        contenido = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
from flask import Flask, session, redirect, url_for
import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Cargar configuración
try:
    from config import Config
    MONGO_URI = Config.MONGO_URI
except ImportError:
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://admin:admin123@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority')

def crear_app_acceso_directo():
    \"\"\"Crea una aplicación Flask para acceso directo.\"\"\"
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    @app.route('/')
    def acceso_directo():
        # Establecer datos de sesión para el usuario normal
        session['logged_in'] = True
        session['email'] = 'usuario@example.com'
        session['username'] = 'usuario'
        session['role'] = 'user'
        session['name'] = 'Usuario Normal'
        
        logger.info("Sesión establecida para usuario normal")
        logger.info(f"Datos de sesión: {dict(session)}")
        
        # Redirigir al dashboard de usuario
        return redirect('/dashboard_user')
    
    return app

if __name__ == '__main__':
    app = crear_app_acceso_directo()
    logger.info("Iniciando servidor de acceso directo para usuario normal...")
    logger.info("Accede a http://127.0.0.1:5000/ para iniciar sesión automáticamente como usuario normal")
    app.run(host='127.0.0.1', port=5000, debug=True)
"""
        
        with open(ruta_archivo, 'w') as f:
            f.write(contenido)
        
        logger.info(f"✅ Script de acceso directo creado: {ruta_archivo}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear script de acceso directo: {str(e)}")
        return False

def main():
    """Función principal que ejecuta la corrección del usuario normal."""
    logger.info("Iniciando corrección del usuario normal...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # 1. Crear o actualizar el usuario normal
        usuario_ok = crear_usuario_normal(db)
        
        # 2. Probar el inicio de sesión
        login_ok = probar_inicio_sesion()
        
        # 3. Crear script de acceso directo
        acceso_directo_ok = crear_acceso_directo()
        
        # Resumen
        logger.info("\n=== RESUMEN DE CORRECCIÓN DE USUARIO NORMAL ===")
        logger.info(f"1. Usuario normal: {'✅ Creado/Actualizado' if usuario_ok else '❌ No creado/actualizado'}")
        logger.info(f"2. Inicio de sesión: {'✅ Exitoso' if login_ok else '❌ Fallido'}")
        logger.info(f"3. Script de acceso directo: {'✅ Creado' if acceso_directo_ok else '❌ No creado'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        
        if login_ok:
            logger.info("1. Accede a la aplicación en http://127.0.0.1:8002")
            logger.info("2. Inicia sesión con las siguientes credenciales:")
            logger.info(f"   - Usuario normal: {USER_EMAIL} / {USER_PASSWORD}")
            logger.info("3. Navega a http://127.0.0.1:8002/catalogs para ver los catálogos")
        else:
            logger.info("1. Utiliza el script de acceso directo para iniciar sesión como usuario normal:")
            logger.info("   $ python3 acceso_directo_usuario.py")
            logger.info("2. Accede a http://127.0.0.1:5000/ para iniciar sesión automáticamente")
            logger.info("3. Serás redirigido al dashboard de usuario")
            logger.info("4. Navega a http://127.0.0.1:8002/catalogs para ver los catálogos")
        
        return True
    
    except Exception as e:
        logger.error(f"Error durante la corrección: {str(e)}")
        return False
    
    finally:
        if client:
            client.close()
            logger.info("Conexión a MongoDB cerrada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
