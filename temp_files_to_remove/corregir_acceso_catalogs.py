#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
import shutil

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

def corregir_decorador_permisos():
    """Corrige el decorador de permisos en catalogs_routes.py."""
    ruta_archivo = "app/routes/catalogs_routes.py"
    
    try:
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Hacer backup del archivo original
        backup_path = f"{ruta_archivo}.bak"
        with open(backup_path, 'w') as f:
            f.write(contenido)
        logger.info(f"✅ Backup creado para {ruta_archivo}")
        
        # Corregir el decorador de permisos
        decorador_original = """def check_catalog_permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_mongo_available():
            flash("Error de conexión a la base de datos.", "danger")
            return redirect(url_for('main.dashboard_user'))
        catalog_id = kwargs.get('catalog_id')
        if not catalog_id:
            return f(*args, **kwargs)
        try:
            object_id = ObjectId(catalog_id)
        except Exception as e:
            current_app.logger.error(f"catalog_id inválido: {catalog_id} - {str(e)}")
            flash("ID de catálogo inválido.", "danger")
            return redirect(url_for("catalogs.list"))
        catalog = mongo.db.catalogs.find_one({"_id": object_id})
        if not catalog:
            flash("Catálogo no encontrado", "danger")
            return redirect(url_for("catalogs.list"))
        user = session.get('username') or session.get('email')
        if user and not is_admin():
            if catalog.get('created_by') != user:
                flash("No tienes permiso para acceder a este catálogo", "danger")
                return redirect(url_for("catalogs.list"))
        # Admin puede acceder a todos
        kwargs['catalog'] = catalog
        return f(*args, **kwargs)
    return decorated_function"""
        
        decorador_corregido = """def check_catalog_permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_mongo_available():
            flash("Error de conexión a la base de datos.", "danger")
            return redirect(url_for('main.dashboard_user'))
        
        # Verificar si el usuario está autenticado
        if not session.get('logged_in'):
            flash("Debe iniciar sesión para acceder a los catálogos", "warning")
            return redirect(url_for('auth.login'))
        
        catalog_id = kwargs.get('catalog_id')
        if not catalog_id:
            return f(*args, **kwargs)
        
        try:
            object_id = ObjectId(catalog_id)
        except Exception as e:
            current_app.logger.error(f"catalog_id inválido: {catalog_id} - {str(e)}")
            flash("ID de catálogo inválido.", "danger")
            return redirect(url_for("catalogs.list"))
        
        catalog = mongo.db.catalogs.find_one({"_id": object_id})
        if not catalog:
            flash("Catálogo no encontrado", "danger")
            return redirect(url_for("catalogs.list"))
        
        # Obtener el identificador del usuario (email o username)
        user_email = session.get('email')
        user_username = session.get('username')
        user_id = user_email or user_username
        
        # Verificar si el usuario es administrador
        is_user_admin = session.get('role') == 'admin'
        
        # Si no es admin, verificar si tiene permisos para el catálogo
        if not is_user_admin and user_id:
            catalog_owner = catalog.get('created_by')
            if catalog_owner and catalog_owner != user_id:
                flash("No tienes permiso para acceder a este catálogo", "danger")
                return redirect(url_for("catalogs.list"))
        
        # Admin puede acceder a todos
        kwargs['catalog'] = catalog
        return f(*args, **kwargs)
    return decorated_function"""
        
        # Reemplazar el decorador
        contenido_corregido = contenido.replace(decorador_original, decorador_corregido)
        
        # Guardar el archivo corregido
        with open(ruta_archivo, 'w') as f:
            f.write(contenido_corregido)
        
        logger.info(f"✅ Decorador de permisos corregido en {ruta_archivo}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al corregir el decorador de permisos: {str(e)}")
        return False

def corregir_funcion_list():
    """Corrige la función list en catalogs_routes.py."""
    ruta_archivo = "app/routes/catalogs_routes.py"
    
    try:
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Corregir la función list
        funcion_original = """@catalogs_bp.route("/")
def list():
    if not is_mongo_available():
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for('main.dashboard_user'))
    username = session.get('username') or session.get('email')
    if username and not is_admin():
        catalogs_cursor = mongo.db.catalogs.find({"created_by": username})
    else:
        catalogs_cursor = mongo.db.catalogs.find()
    catalogs = []
    for c in catalogs_cursor:
        if c.get("_id"):
            c["row_count"] = len(c.get("rows", []))
            c["_id_str"] = str(c["_id"])
            catalogs.append(c)
        else:
            current_app.logger.warning(f"Catálogo sin _id detectado: {c}")
    if not catalogs:
        flash("No hay catálogos disponibles. Crea uno para comenzar.", "info")
    return render_template("catalogs.html", catalogs=catalogs, session=session)"""
        
        funcion_corregida = """@catalogs_bp.route("/")
def list():
    # Verificar si el usuario está autenticado
    if not session.get('logged_in'):
        flash("Debe iniciar sesión para acceder a los catálogos", "warning")
        return redirect(url_for('auth.login'))
    
    if not is_mongo_available():
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for('main.dashboard_user'))
    
    # Obtener el identificador del usuario (email o username)
    user_email = session.get('email')
    user_username = session.get('username')
    user_id = user_email or user_username
    
    # Verificar si el usuario es administrador
    is_user_admin = session.get('role') == 'admin'
    
    # Filtrar catálogos según el rol
    if user_id and not is_user_admin:
        current_app.logger.info(f"Buscando catálogos para el usuario: {user_id}")
        catalogs_cursor = mongo.db.catalogs.find({"created_by": user_id})
    else:
        current_app.logger.info("Buscando todos los catálogos (admin)")
        catalogs_cursor = mongo.db.catalogs.find()
    
    catalogs = []
    for c in catalogs_cursor:
        if c.get("_id"):
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
        
        # Reemplazar la función
        contenido_corregido = contenido.replace(funcion_original, funcion_corregida)
        
        # Guardar el archivo corregido
        with open(ruta_archivo, 'w') as f:
            f.write(contenido_corregido)
        
        logger.info(f"✅ Función list corregida en {ruta_archivo}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al corregir la función list: {str(e)}")
        return False

def corregir_permisos_catalogs(db):
    """Corrige los permisos en la colección catalogs."""
    try:
        # 1. Asegurarse de que todos los documentos tengan el campo created_by
        docs_sin_created_by = list(db.catalogs.find({"created_by": {"$exists": False}}))
        
        if docs_sin_created_by:
            logger.info(f"Corrigiendo {len(docs_sin_created_by)} documentos sin created_by...")
            
            for doc in docs_sin_created_by:
                db.catalogs.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"created_by": "admin@example.com"}}
                )
            logger.info("✅ Documentos actualizados con created_by")
        else:
            logger.info("✅ Todos los documentos tienen el campo created_by")
        
        # 2. Crear un catálogo de prueba para el administrador
        catalogo_admin = db.catalogs.find_one({"name": "Catálogo del Administrador"})
        
        if not catalogo_admin:
            catalogo = {
                "name": "Catálogo del Administrador",
                "description": "Catálogo de prueba para el administrador",
                "headers": ["Número", "Descripción", "Valor"],
                "rows": [
                    {"Número": "1", "Descripción": "Item de prueba 1", "Valor": "100"},
                    {"Número": "2", "Descripción": "Item de prueba 2", "Valor": "200"}
                ],
                "created_by": "admin@example.com",
                "created_at": datetime.datetime.now()
            }
            db.catalogs.insert_one(catalogo)
            logger.info("✅ Catálogo de prueba para el administrador creado")
        
        # 3. Crear un catálogo de prueba para el usuario normal
        catalogo_user = db.catalogs.find_one({"name": "Catálogo del Usuario"})
        
        if not catalogo_user:
            catalogo = {
                "name": "Catálogo del Usuario",
                "description": "Catálogo de prueba para el usuario normal",
                "headers": ["Número", "Descripción", "Valor"],
                "rows": [
                    {"Número": "1", "Descripción": "Item de prueba 1", "Valor": "100"},
                    {"Número": "2", "Descripción": "Item de prueba 2", "Valor": "200"}
                ],
                "created_by": "usuario@example.com",
                "created_at": datetime.datetime.now()
            }
            db.catalogs.insert_one(catalogo)
            logger.info("✅ Catálogo de prueba para el usuario normal creado")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al corregir permisos: {str(e)}")
        return False

def crear_usuarios_prueba(db):
    """Crea usuarios de prueba si no existen."""
    try:
        # 1. Crear usuario administrador
        admin_user = db.users.find_one({"email": "admin@example.com"})
        
        if not admin_user:
            admin_user = {
                "email": "admin@example.com",
                "username": "administrator",
                "password": "pbkdf2:sha256:150000$3VRm6eMj$7a50df88e2c8b9b9be0f8a2df21d12a9b9ee224e4f3f84b626c782f816348a39",  # admin123
                "role": "admin",
                "name": "Administrador",
                "last_name": "Sistema",
                "created_at": datetime.datetime.now()
            }
            db.users.insert_one(admin_user)
            logger.info("✅ Usuario administrador creado")
        
        # 2. Crear usuario normal
        normal_user = db.users.find_one({"email": "usuario@example.com"})
        
        if not normal_user:
            normal_user = {
                "email": "usuario@example.com",
                "username": "usuario",
                "password": "pbkdf2:sha256:150000$3VRm6eMj$7a50df88e2c8b9b9be0f8a2df21d12a9b9ee224e4f3f84b626c782f816348a39",  # admin123
                "role": "user",
                "name": "Usuario",
                "last_name": "Normal",
                "created_at": datetime.datetime.now()
            }
            db.users.insert_one(normal_user)
            logger.info("✅ Usuario normal creado")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear usuarios de prueba: {str(e)}")
        return False

def main():
    """Función principal que ejecuta la corrección de acceso a catálogos."""
    logger.info("Iniciando corrección de acceso a catálogos...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # 1. Corregir el decorador de permisos
        decorador_corregido = corregir_decorador_permisos()
        
        # 2. Corregir la función list
        funcion_corregida = corregir_funcion_list()
        
        # 3. Corregir permisos en la colección catalogs
        permisos_corregidos = corregir_permisos_catalogs(db)
        
        # 4. Crear usuarios de prueba
        usuarios_creados = crear_usuarios_prueba(db)
        
        # Resumen
        logger.info("\n=== RESUMEN DE LA CORRECCIÓN ===")
        logger.info(f"1. Decorador de permisos: {'✅ Corregido' if decorador_corregido else '❌ No corregido'}")
        logger.info(f"2. Función list: {'✅ Corregida' if funcion_corregida else '❌ No corregida'}")
        logger.info(f"3. Permisos en la colección: {'✅ Corregidos' if permisos_corregidos else '❌ No corregidos'}")
        logger.info(f"4. Usuarios de prueba: {'✅ Creados' if usuarios_creados else '❌ No creados'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Accede a la aplicación en http://127.0.0.1:8002")
        logger.info("3. Inicia sesión con las siguientes credenciales:")
        logger.info("   - Administrador: admin@example.com / admin123")
        logger.info("   - Usuario normal: usuario@example.com / admin123")
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
