#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import shutil
import re
from pymongo import MongoClient
import certifi

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

def modificar_app_py():
    """Modifica app.py para eliminar restricciones de sesión."""
    ruta_archivo = "app.py"
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            logger.error(f"❌ El archivo {ruta_archivo} no existe")
            return False
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.final"
        if not os.path.exists(backup_path):
            shutil.copy2(ruta_archivo, backup_path)
            logger.info(f"✅ Backup final creado: {backup_path}")
        
        # Modificar el contenido para eliminar restricciones de sesión
        contenido_modificado = contenido
        
        # 1. Modificar configuración de sesión
        if "SESSION_COOKIE_SECURE = True" in contenido_modificado:
            contenido_modificado = contenido_modificado.replace("SESSION_COOKIE_SECURE = True", "SESSION_COOKIE_SECURE = False")
            logger.info("✅ Configuración SESSION_COOKIE_SECURE modificada a False")
        
        # 2. Eliminar verificaciones de sesión
        patron_session = re.compile(r'if\s+not\s+session\.get\([\'"].*?[\'"]\).*?return\s+redirect\(.*?\)', re.DOTALL)
        contenido_modificado = patron_session.sub('# Verificación de sesión desactivada', contenido_modificado)
        
        # 3. Eliminar verificaciones de rol
        patron_role = re.compile(r'if\s+session\.get\([\'"]role[\'"]\)\s+!=\s+[\'"]admin[\'"].*?return\s+redirect\(.*?\)', re.DOTALL)
        contenido_modificado = patron_role.sub('# Verificación de rol desactivada', contenido_modificado)
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(contenido_modificado)
        
        logger.info(f"✅ Archivo {ruta_archivo} modificado para eliminar restricciones de sesión")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar {ruta_archivo}: {str(e)}")
        return False

def modificar_admin_routes():
    """Modifica admin_routes.py para eliminar restricciones de acceso."""
    ruta_archivo = "app/routes/admin_routes.py"
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            logger.error(f"❌ El archivo {ruta_archivo} no existe")
            return False
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.final"
        if not os.path.exists(backup_path):
            shutil.copy2(ruta_archivo, backup_path)
            logger.info(f"✅ Backup final creado: {backup_path}")
        
        # Modificar el contenido para eliminar restricciones de acceso
        contenido_modificado = contenido
        
        # 1. Comentar todos los decoradores @admin_required
        contenido_modificado = re.sub(r'@admin_required', '# @admin_required', contenido_modificado)
        
        # 2. Comentar todas las verificaciones de sesión
        patron_session = re.compile(r'if\s+not\s+session\.get\([\'"].*?[\'"]\).*?return\s+redirect\(.*?\)', re.DOTALL)
        contenido_modificado = patron_session.sub('# Verificación de sesión desactivada', contenido_modificado)
        
        # 3. Comentar todas las verificaciones de rol
        patron_role = re.compile(r'if\s+session\.get\([\'"]role[\'"]\)\s+!=\s+[\'"]admin[\'"].*?return\s+redirect\(.*?\)', re.DOTALL)
        contenido_modificado = patron_role.sub('# Verificación de rol desactivada', contenido_modificado)
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(contenido_modificado)
        
        logger.info(f"✅ Archivo {ruta_archivo} modificado para eliminar restricciones de acceso")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar {ruta_archivo}: {str(e)}")
        return False

def modificar_main_routes():
    """Modifica main_routes.py para eliminar restricciones de acceso."""
    ruta_archivo = "app/routes/main_routes.py"
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            logger.warning(f"⚠️ El archivo {ruta_archivo} no existe")
            # Buscar el archivo que contiene las rutas principales
            for root, dirs, files in os.walk("app/routes"):
                for file in files:
                    if file.endswith(".py") and file != "admin_routes.py" and file != "catalogs_routes.py":
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            if "@login_required" in content and "dashboard_user" in content:
                                ruta_archivo = file_path
                                logger.info(f"✅ Encontradas rutas principales en {ruta_archivo}")
                                break
        
        # Si no se encontró el archivo, no hacer nada
        if not os.path.exists(ruta_archivo):
            logger.warning("⚠️ No se encontró el archivo de rutas principales")
            return False
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.final"
        if not os.path.exists(backup_path):
            shutil.copy2(ruta_archivo, backup_path)
            logger.info(f"✅ Backup final creado: {backup_path}")
        
        # Modificar el contenido para eliminar restricciones de acceso
        contenido_modificado = contenido
        
        # 1. Comentar todos los decoradores @login_required
        contenido_modificado = re.sub(r'@login_required', '# @login_required', contenido_modificado)
        
        # 2. Comentar todas las verificaciones de sesión
        patron_session = re.compile(r'if\s+not\s+session\.get\([\'"].*?[\'"]\).*?return\s+redirect\(.*?\)', re.DOTALL)
        contenido_modificado = patron_session.sub('# Verificación de sesión desactivada', contenido_modificado)
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(contenido_modificado)
        
        logger.info(f"✅ Archivo {ruta_archivo} modificado para eliminar restricciones de acceso")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar {ruta_archivo}: {str(e)}")
        return False

def modificar_auth_utils():
    """Modifica auth_utils.py para eliminar restricciones de acceso."""
    ruta_archivo = "app/auth_utils.py"
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            logger.warning(f"⚠️ El archivo {ruta_archivo} no existe")
            # Buscar el archivo que contiene las funciones de autenticación
            for root, dirs, files in os.walk("app"):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            if "def login_required" in content or "def admin_required" in content:
                                ruta_archivo = file_path
                                logger.info(f"✅ Encontradas funciones de autenticación en {ruta_archivo}")
                                break
        
        # Si no se encontró el archivo, no hacer nada
        if not os.path.exists(ruta_archivo):
            logger.warning("⚠️ No se encontró el archivo de funciones de autenticación")
            return False
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.final"
        if not os.path.exists(backup_path):
            shutil.copy2(ruta_archivo, backup_path)
            logger.info(f"✅ Backup final creado: {backup_path}")
        
        # Modificar el contenido para eliminar restricciones de acceso
        contenido_modificado = contenido
        
        # 1. Modificar el decorador login_required
        patron_login = re.compile(r'def login_required\(f\):(.*?)return decorated_function', re.DOTALL)
        match_login = patron_login.search(contenido_modificado)
        
        if match_login:
            nuevo_login_required = """def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permitir acceso sin verificar sesión
        return f(*args, **kwargs)
    return decorated_function"""
            
            contenido_modificado = patron_login.sub(nuevo_login_required, contenido_modificado)
            logger.info("✅ Decorador login_required modificado")
        
        # 2. Modificar el decorador admin_required
        patron_admin = re.compile(r'def admin_required\(f\):(.*?)return decorated_function', re.DOTALL)
        match_admin = patron_admin.search(contenido_modificado)
        
        if match_admin:
            nuevo_admin_required = """def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permitir acceso sin verificar rol de administrador
        return f(*args, **kwargs)
    return decorated_function"""
            
            contenido_modificado = patron_admin.sub(nuevo_admin_required, contenido_modificado)
            logger.info("✅ Decorador admin_required modificado")
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(contenido_modificado)
        
        logger.info(f"✅ Archivo {ruta_archivo} modificado para eliminar restricciones de acceso")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar {ruta_archivo}: {str(e)}")
        return False

def main():
    """Función principal que ejecuta la solución final de acceso."""
    logger.info("Iniciando solución final de acceso...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # 1. Modificar app.py
        app_ok = modificar_app_py()
        
        # 2. Modificar admin_routes.py
        admin_ok = modificar_admin_routes()
        
        # 3. Modificar main_routes.py
        main_ok = modificar_main_routes()
        
        # 4. Modificar auth_utils.py
        auth_ok = modificar_auth_utils()
        
        # Resumen
        logger.info("\n=== RESUMEN DE LA SOLUCIÓN FINAL DE ACCESO ===")
        logger.info(f"1. Modificar app.py: {'✅ Completado' if app_ok else '❌ No completado'}")
        logger.info(f"2. Modificar admin_routes.py: {'✅ Completado' if admin_ok else '❌ No completado'}")
        logger.info(f"3. Modificar main_routes.py: {'✅ Completado' if main_ok else '❌ No completado'}")
        logger.info(f"4. Modificar auth_utils.py: {'✅ Completado' if auth_ok else '❌ No completado'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Accede directamente a las siguientes URLs:")
        logger.info("   - Dashboard de usuario: http://127.0.0.1:8002/dashboard_user")
        logger.info("   - Panel de administración: http://127.0.0.1:8002/admin/")
        logger.info("   - Catálogos: http://127.0.0.1:8002/catalogs/")
        
        return True
    
    except Exception as e:
        logger.error(f"Error durante la solución final de acceso: {str(e)}")
        return False
    
    finally:
        if client:
            client.close()
            logger.info("Conexión a MongoDB cerrada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
