#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
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

def modificar_check_catalog_permission():
    """Modifica el decorador check_catalog_permission para permitir acceso sin sesión."""
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
        
        # Reemplazar la función con una versión simplificada que permite acceso sin sesión
        nueva_funcion = """def check_catalog_permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar disponibilidad de MongoDB
        if not is_mongo_available():
            flash("Error de conexión a la base de datos.", "danger")
            return redirect(url_for('main.dashboard_user'))
        
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
        
        # Permitir acceso a todos los catálogos sin verificar sesión
        kwargs['catalog'] = catalog
        return f(*args, **kwargs)
    
    return decorated_function"""
        
        # Reemplazar la función en el contenido
        nuevo_contenido = patron.sub(nueva_funcion, contenido)
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(nuevo_contenido)
        
        logger.info("✅ Función check_catalog_permission modificada para permitir acceso sin sesión")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar la función check_catalog_permission: {str(e)}")
        return False

def modificar_funcion_list():
    """Modifica la función list para permitir acceso sin sesión."""
    ruta_archivo = "app/routes/catalogs_routes.py"
    
    try:
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Buscar y reemplazar la función list
        patron = re.compile(r'@catalogs_bp\.route\("/"\)\ndef list\(\):(.*?)return render_template\("catalogs\.html", catalogs=catalogs, session=session\)', re.DOTALL)
        match = patron.search(contenido)
        
        if not match:
            logger.error("❌ No se encontró la función list en el formato esperado")
            return False
        
        # Reemplazar la función con una versión simplificada que permite acceso sin sesión
        nueva_funcion = """@catalogs_bp.route("/")
def list():
    # Verificar disponibilidad de MongoDB
    if not is_mongo_available():
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for('main.dashboard_user'))
    
    # Obtener información del usuario (si está disponible)
    user_email = session.get('email')
    user_username = session.get('username')
    user_id = user_email or user_username
    is_user_admin = session.get('role') == 'admin'
    
    # Registrar información de acceso
    current_app.logger.info(f"Acceso a catálogos: Usuario={user_id if user_id else 'Anónimo'}, Admin={is_user_admin}")
    
    # Mostrar todos los catálogos sin filtrar por usuario
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
        
        logger.info("✅ Función list modificada para permitir acceso sin sesión")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar la función list: {str(e)}")
        return False

def crear_ruta_acceso_directo():
    """Crea una ruta de acceso directo en app.py."""
    ruta_archivo = "app.py"
    
    try:
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak.{os.path.getmtime(ruta_archivo)}"
        with open(backup_path, 'w') as f:
            f.write(contenido)
        logger.info(f"✅ Backup creado: {backup_path}")
        
        # Buscar la función create_app
        patron = re.compile(r'def create_app\(\):(.*?)return app', re.DOTALL)
        match = patron.search(contenido)
        
        if not match:
            logger.error("❌ No se encontró la función create_app en el formato esperado")
            return False
        
        # Extraer el contenido de la función create_app
        create_app_content = match.group(1)
        
        # Verificar si ya existe la ruta de acceso directo
        if "def acceso_directo_catalogs():" in create_app_content:
            logger.info("✅ La ruta de acceso directo ya existe")
            return True
        
        # Buscar dónde registrar la ruta (justo antes de "return app")
        nueva_ruta = """
    # Ruta de acceso directo a catálogos
    @app.route('/acceso_directo_catalogs')
    def acceso_directo_catalogs():
        # Establecer datos de sesión para el administrador
        session['logged_in'] = True
        session['email'] = 'admin@example.com'
        session['username'] = 'admin'
        session['role'] = 'admin'
        session['name'] = 'Administrador'
        
        app.logger.info("Sesión establecida para administrador mediante acceso directo")
        app.logger.info(f"Datos de sesión: {dict(session)}")
        
        # Redirigir a los catálogos
        return redirect(url_for('catalogs.list'))
    
    # Ruta de acceso directo para usuario normal
    @app.route('/acceso_directo_usuario')
    def acceso_directo_usuario():
        # Establecer datos de sesión para el usuario normal
        session['logged_in'] = True
        session['email'] = 'usuario@example.com'
        session['username'] = 'usuario'
        session['role'] = 'user'
        session['name'] = 'Usuario Normal'
        
        app.logger.info("Sesión establecida para usuario normal mediante acceso directo")
        app.logger.info(f"Datos de sesión: {dict(session)}")
        
        # Redirigir a los catálogos
        return redirect(url_for('catalogs.list'))
"""
        
        # Insertar la nueva ruta justo antes de "return app"
        nuevo_contenido = contenido.replace("    return app", nueva_ruta + "    return app")
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(nuevo_contenido)
        
        logger.info("✅ Rutas de acceso directo creadas en app.py")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear rutas de acceso directo: {str(e)}")
        return False

def main():
    """Función principal que ejecuta la solución de acceso directo a catálogos."""
    logger.info("Iniciando solución de acceso directo a catálogos...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # 1. Modificar el decorador check_catalog_permission
        check_permission_ok = modificar_check_catalog_permission()
        
        # 2. Modificar la función list
        list_ok = modificar_funcion_list()
        
        # 3. Crear ruta de acceso directo
        acceso_directo_ok = crear_ruta_acceso_directo()
        
        # Resumen
        logger.info("\n=== RESUMEN DE LA SOLUCIÓN ===")
        logger.info(f"1. Modificar check_catalog_permission: {'✅ Completado' if check_permission_ok else '❌ No completado'}")
        logger.info(f"2. Modificar función list: {'✅ Completado' if list_ok else '❌ No completado'}")
        logger.info(f"3. Crear rutas de acceso directo: {'✅ Completado' if acceso_directo_ok else '❌ No completado'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Accede directamente a los catálogos mediante las siguientes URLs:")
        logger.info("   - Como administrador: http://127.0.0.1:8002/acceso_directo_catalogs")
        logger.info("   - Como usuario normal: http://127.0.0.1:8002/acceso_directo_usuario")
        logger.info("   - Acceso directo a la lista de catálogos: http://127.0.0.1:8002/catalogs/")
        
        return True
    
    except Exception as e:
        logger.error(f"Error durante la solución: {str(e)}")
        return False
    
    finally:
        if client:
            client.close()
            logger.info("Conexión a MongoDB cerrada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
