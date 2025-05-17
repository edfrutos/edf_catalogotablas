#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
import shutil
import re

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

def corregir_check_catalog_permission():
    """Corrige la función check_catalog_permission en catalogs_routes.py para manejar mejor las sesiones."""
    ruta_archivo = "app/routes/catalogs_routes.py"
    
    try:
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.{os.path.getmtime(ruta_archivo)}"
        with open(backup_path, 'w') as f:
            f.write(contenido)
        logger.info(f"✅ Backup creado: {backup_path}")
        
        # Buscar y reemplazar la función check_catalog_permission
        patron = re.compile(r'def check_catalog_permission\(f\):(.*?)return decorated_function', re.DOTALL)
        match = patron.search(contenido)
        
        if not match:
            logger.error("❌ No se encontró la función check_catalog_permission en el archivo")
            return False
        
        # Reemplazar la función con una versión mejorada
        nueva_funcion = """def check_catalog_permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar disponibilidad de MongoDB
        if not is_mongo_available():
            flash("Error de conexión a la base de datos.", "danger")
            return redirect(url_for('main.dashboard_user'))
        
        # Verificar si el usuario está autenticado
        if 'logged_in' not in session:
            flash("Debe iniciar sesión para acceder a los catálogos", "warning")
            return redirect(url_for('auth.login'))
        
        # Obtener el ID del catálogo
        catalog_id = kwargs.get('catalog_id')
        if not catalog_id:
            return f(*args, **kwargs)
        
        # Validar el ID del catálogo
        try:
            object_id = ObjectId(catalog_id)
        except Exception as e:
            current_app.logger.error(f"ID de catálogo inválido: {catalog_id} - {str(e)}")
            flash("ID de catálogo inválido", "danger")
            return redirect(url_for("catalogs.list"))
        
        # Buscar el catálogo en la base de datos
        catalog = mongo.db.catalogs.find_one({"_id": object_id})
        if not catalog:
            flash("Catálogo no encontrado", "danger")
            return redirect(url_for("catalogs.list"))
        
        # Verificar permisos
        user_email = session.get('email')
        user_username = session.get('username')
        user_id = user_email or user_username
        
        # Verificar si el usuario es administrador
        is_user_admin = session.get('role') == 'admin'
        
        # Administradores pueden acceder a todos los catálogos
        if is_user_admin:
            current_app.logger.info(f"Acceso de administrador al catálogo {catalog_id}")
            kwargs['catalog'] = catalog
            return f(*args, **kwargs)
        
        # Usuarios normales solo pueden acceder a sus propios catálogos
        if user_id:
            catalog_owner = catalog.get('created_by')
            if catalog_owner and catalog_owner == user_id:
                current_app.logger.info(f"Acceso de usuario {user_id} a su catálogo {catalog_id}")
                kwargs['catalog'] = catalog
                return f(*args, **kwargs)
            else:
                current_app.logger.warning(f"Intento de acceso no autorizado: Usuario {user_id} intentó acceder al catálogo {catalog_id} creado por {catalog_owner}")
                flash("No tiene permisos para acceder a este catálogo", "danger")
                return redirect(url_for("catalogs.list"))
        
        # Si no hay usuario identificado, redirigir al login
        flash("Debe iniciar sesión para acceder a los catálogos", "warning")
        return redirect(url_for('auth.login'))
    
    return decorated_function"""
        
        # Reemplazar la función en el contenido
        nuevo_contenido = patron.sub(nueva_funcion, contenido)
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(nuevo_contenido)
        
        logger.info("✅ Función check_catalog_permission corregida")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al corregir la función check_catalog_permission: {str(e)}")
        return False

def corregir_funcion_list():
    """Corrige la función list en catalogs_routes.py para manejar mejor las sesiones."""
    ruta_archivo = "app/routes/catalogs_routes.py"
    
    try:
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Buscar y reemplazar la función list
        patron = re.compile(r'@catalogs_bp\.route\("/"\)\ndef list\(\):(.*?)return render_template\("catalogs\.html", catalogs=catalogs, session=session\)', re.DOTALL)
        match = patron.search(contenido)
        
        if not match:
            logger.error("❌ No se encontró la función list en el archivo")
            return False
        
        # Reemplazar la función con una versión mejorada
        nueva_funcion = """@catalogs_bp.route("/")
def list():
    # Verificar si el usuario está autenticado
    if 'logged_in' not in session:
        current_app.logger.warning("Intento de acceso a catálogos sin sesión iniciada")
        flash("Debe iniciar sesión para acceder a los catálogos", "warning")
        return redirect(url_for('auth.login'))
    
    # Verificar disponibilidad de MongoDB
    if not is_mongo_available():
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for('main.dashboard_user'))
    
    # Obtener información del usuario
    user_email = session.get('email')
    user_username = session.get('username')
    user_id = user_email or user_username
    is_user_admin = session.get('role') == 'admin'
    
    current_app.logger.info(f"Acceso a catálogos: Usuario={user_id}, Admin={is_user_admin}")
    
    # Filtrar catálogos según el rol
    if user_id and not is_user_admin:
        current_app.logger.info(f"Buscando catálogos para el usuario: {user_id}")
        catalogs_cursor = mongo.db.catalogs.find({"created_by": user_id})
    else:
        current_app.logger.info("Buscando todos los catálogos (admin)")
        catalogs_cursor = mongo.db.catalogs.find()
    
    # Procesar los catálogos encontrados
    catalogs = []
    for c in catalogs_cursor:
        if c.get("_id"):
            # Asegurarse de que el catálogo tenga los campos necesarios
            if "rows" not in c:
                c["rows"] = []
            if "headers" not in c:
                c["headers"] = ["Columna 1", "Columna 2", "Columna 3"]
            
            c["row_count"] = len(c.get("rows", []))
            c["_id_str"] = str(c["_id"])
            catalogs.append(c)
            current_app.logger.info(f"Catálogo encontrado: {c.get('name')} (ID: {c['_id_str']})")
        else:
            current_app.logger.warning(f"Catálogo sin _id detectado: {c}")
    
    if not catalogs:
        flash("No hay catálogos disponibles. Crea uno para comenzar.", "info")
    
    current_app.logger.info(f"Total de catálogos encontrados: {len(catalogs)}")
    return render_template("catalogs.html", catalogs=catalogs, session=session)"""
        
        # Reemplazar la función en el contenido
        nuevo_contenido = patron.sub(nueva_funcion, contenido)
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(nuevo_contenido)
        
        logger.info("✅ Función list corregida")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al corregir la función list: {str(e)}")
        return False

def corregir_funcion_view():
    """Corrige la función view en catalogs_routes.py para manejar mejor las sesiones."""
    ruta_archivo = "app/routes/catalogs_routes.py"
    
    try:
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Buscar y reemplazar la función view
        patron = re.compile(r'@catalogs_bp\.route\("/<catalog_id>"\)\n@check_catalog_permission\ndef view\(catalog_id, catalog\):(.*?)return render_template\("ver_catalogo\.html", catalog=catalog, session=session\)', re.DOTALL)
        match = patron.search(contenido)
        
        if not match:
            logger.warning("⚠️ No se encontró la función view en el formato esperado")
            return False
        
        # Reemplazar la función con una versión mejorada
        nueva_funcion = """@catalogs_bp.route("/<catalog_id>")
@check_catalog_permission
def view(catalog_id, catalog):
    current_app.logger.info(f"Visualizando catálogo {catalog_id}")
    return render_template("ver_catalogo.html", catalog=catalog, session=session)"""
        
        # Reemplazar la función en el contenido
        nuevo_contenido = patron.sub(nueva_funcion, contenido)
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(nuevo_contenido)
        
        logger.info("✅ Función view corregida")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al corregir la función view: {str(e)}")
        return False

def verificar_catalogs_db(db):
    """Verifica y corrige los documentos en la colección catalogs."""
    try:
        # Verificar todos los documentos en la colección catalogs
        catalogs = list(db.catalogs.find())
        logger.info(f"Encontrados {len(catalogs)} catálogos en la base de datos")
        
        # Contador de documentos corregidos
        docs_corregidos = 0
        
        for catalog in catalogs:
            modificaciones = {}
            
            # Verificar campo created_by
            if "created_by" not in catalog:
                modificaciones["created_by"] = "admin@example.com"
                logger.info(f"Añadiendo campo created_by al catálogo {catalog.get('name', 'Sin nombre')}")
            
            # Verificar campo rows
            if "rows" not in catalog:
                modificaciones["rows"] = []
                logger.info(f"Añadiendo campo rows vacío al catálogo {catalog.get('name', 'Sin nombre')}")
            
            # Verificar campo headers
            if "headers" not in catalog:
                modificaciones["headers"] = ["Columna 1", "Columna 2", "Columna 3"]
                logger.info(f"Añadiendo campo headers por defecto al catálogo {catalog.get('name', 'Sin nombre')}")
            
            # Aplicar modificaciones si es necesario
            if modificaciones:
                db.catalogs.update_one({"_id": catalog["_id"]}, {"$set": modificaciones})
                docs_corregidos += 1
        
        logger.info(f"✅ {docs_corregidos} catálogos corregidos en la base de datos")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al verificar catálogos en la base de datos: {str(e)}")
        return False

def crear_catalogo_prueba(db):
    """Crea un catálogo de prueba si no existe ninguno."""
    try:
        # Verificar si ya existen catálogos
        count = db.catalogs.count_documents({})
        
        if count == 0:
            # Crear un catálogo de prueba
            catalogo = {
                "name": "Catálogo de Prueba",
                "description": "Este es un catálogo de prueba creado automáticamente",
                "headers": ["ID", "Nombre", "Descripción", "Precio"],
                "rows": [
                    {"ID": "001", "Nombre": "Producto 1", "Descripción": "Descripción del producto 1", "Precio": "100"},
                    {"ID": "002", "Nombre": "Producto 2", "Descripción": "Descripción del producto 2", "Precio": "200"}
                ],
                "created_by": "admin@example.com",
                "created_at": datetime.datetime.now()
            }
            
            db.catalogs.insert_one(catalogo)
            logger.info("✅ Catálogo de prueba creado")
        else:
            logger.info(f"Ya existen {count} catálogos, no es necesario crear uno de prueba")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear catálogo de prueba: {str(e)}")
        return False

def verificar_sesion_config():
    """Verifica y corrige la configuración de sesiones en config.py."""
    ruta_archivo = "config.py"
    
    try:
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.{os.path.getmtime(ruta_archivo)}"
        with open(backup_path, 'w') as f:
            f.write(contenido)
        logger.info(f"✅ Backup creado: {backup_path}")
        
        # Verificar configuración de sesiones
        if "SESSION_COOKIE_SECURE = True" in contenido:
            # Cambiar a False para entorno de desarrollo
            contenido = contenido.replace("SESSION_COOKIE_SECURE = True", "SESSION_COOKIE_SECURE = False")
            logger.info("✅ SESSION_COOKIE_SECURE cambiado a False")
        
        if "SESSION_COOKIE_HTTPONLY = True" not in contenido:
            # Añadir configuración si no existe
            if "class Config:" in contenido:
                contenido = contenido.replace("class Config:", "class Config:\n    SESSION_COOKIE_HTTPONLY = True")
                logger.info("✅ SESSION_COOKIE_HTTPONLY añadido")
        
        if "PERMANENT_SESSION_LIFETIME" not in contenido:
            # Añadir configuración si no existe
            if "class Config:" in contenido:
                contenido = contenido.replace("class Config:", "class Config:\n    PERMANENT_SESSION_LIFETIME = 86400  # 24 horas")
                logger.info("✅ PERMANENT_SESSION_LIFETIME añadido")
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(contenido)
        
        logger.info("✅ Configuración de sesiones verificada y corregida")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al verificar configuración de sesiones: {str(e)}")
        return False

def main():
    """Función principal que ejecuta las correcciones de sesión para catálogos."""
    logger.info("Iniciando corrección de sesión para catálogos...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # 1. Corregir la función check_catalog_permission
        check_permission_ok = corregir_check_catalog_permission()
        
        # 2. Corregir la función list
        list_ok = corregir_funcion_list()
        
        # 3. Corregir la función view
        view_ok = corregir_funcion_view()
        
        # 4. Verificar y corregir documentos en la base de datos
        db_ok = verificar_catalogs_db(db)
        
        # 5. Crear catálogo de prueba si es necesario
        catalogo_ok = crear_catalogo_prueba(db)
        
        # 6. Verificar configuración de sesiones
        sesion_ok = verificar_sesion_config()
        
        # Resumen
        logger.info("\n=== RESUMEN DE CORRECCIONES ===")
        logger.info(f"1. Función check_catalog_permission: {'✅ Corregida' if check_permission_ok else '❌ No corregida'}")
        logger.info(f"2. Función list: {'✅ Corregida' if list_ok else '❌ No corregida'}")
        logger.info(f"3. Función view: {'✅ Corregida' if view_ok else '❌ No corregida'}")
        logger.info(f"4. Documentos en base de datos: {'✅ Verificados' if db_ok else '❌ No verificados'}")
        logger.info(f"5. Catálogo de prueba: {'✅ Verificado' if catalogo_ok else '❌ No verificado'}")
        logger.info(f"6. Configuración de sesiones: {'✅ Verificada' if sesion_ok else '❌ No verificada'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Accede a la aplicación en http://127.0.0.1:8002")
        logger.info("3. Inicia sesión con las siguientes credenciales:")
        logger.info("   - Administrador: admin@example.com / admin123")
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
    import datetime
    success = main()
    sys.exit(0 if success else 1)
