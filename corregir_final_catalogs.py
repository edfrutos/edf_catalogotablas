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
import re
from werkzeug.security import generate_password_hash

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

def corregir_obtener_id_catalogo():
    """Corrige la función de obtención de ID de catálogo en el script de verificación."""
    ruta_archivo = "verificar_final_catalogs.py"
    
    try:
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Corregir la función obtener_id_primer_catalogo
        patron = re.compile(r'def obtener_id_primer_catalogo\(session\):(.*?)return None', re.DOTALL)
        match = patron.search(contenido)
        
        if not match:
            logger.error("❌ No se encontró la función obtener_id_primer_catalogo en el script de verificación")
            return False
        
        # Nueva implementación de la función
        nueva_funcion = """def obtener_id_primer_catalogo(session):
    \"\"\"Obtiene el ID del primer catálogo disponible.\"\"\"
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
        return None"""
        
        # Reemplazar la función en el contenido
        nuevo_contenido = patron.sub(nueva_funcion, contenido)
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(nuevo_contenido)
        
        logger.info("✅ Función obtener_id_primer_catalogo corregida en el script de verificación")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al corregir la función obtener_id_primer_catalogo: {str(e)}")
        return False

def crear_usuario_normal(db):
    """Crea o actualiza el usuario normal para pruebas."""
    try:
        # Datos del usuario
        email = "usuario@example.com"
        password = "admin123"
        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        
        # Verificar si el usuario ya existe
        usuario = db.users.find_one({"email": email})
        
        if usuario:
            # Actualizar el usuario existente
            db.users.update_one(
                {"email": email},
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
            logger.info(f"✅ Usuario {email} actualizado")
        else:
            # Crear un nuevo usuario
            nuevo_usuario = {
                "email": email,
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
            logger.info(f"✅ Usuario {email} creado")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear/actualizar usuario normal: {str(e)}")
        return False

def crear_catalogo_usuario(db):
    """Crea un catálogo para el usuario normal."""
    try:
        # Verificar si ya existe un catálogo para el usuario normal
        catalogo_usuario = db.catalogs.find_one({"created_by": "usuario@example.com"})
        
        if not catalogo_usuario:
            # Crear un catálogo para el usuario normal
            catalogo = {
                "name": "Catálogo del Usuario Normal",
                "description": "Este es un catálogo de prueba para el usuario normal",
                "headers": ["ID", "Producto", "Descripción", "Precio"],
                "rows": [
                    {"ID": "001", "Producto": "Producto 1", "Descripción": "Descripción del producto 1", "Precio": "100"},
                    {"ID": "002", "Producto": "Producto 2", "Descripción": "Descripción del producto 2", "Precio": "200"}
                ],
                "created_by": "usuario@example.com",
                "created_at": datetime.datetime.now()
            }
            
            db.catalogs.insert_one(catalogo)
            logger.info("✅ Catálogo creado para el usuario normal")
        else:
            logger.info("✅ Ya existe un catálogo para el usuario normal")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear catálogo para el usuario normal: {str(e)}")
        return False

def corregir_funcion_list():
    """Corrige la función list en catalogs_routes.py para mejorar la depuración."""
    ruta_archivo = "app/routes/catalogs_routes.py"
    
    try:
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Buscar la función list
        patron = re.compile(r'@catalogs_bp\.route\("/"\)\ndef list\(\):(.*?)return render_template\("catalogs\.html", catalogs=catalogs, session=session\)', re.DOTALL)
        match = patron.search(contenido)
        
        if not match:
            logger.error("❌ No se encontró la función list en el formato esperado")
            return False
        
        # Nueva implementación de la función list con más logging
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
    
    # Registrar información de la sesión para depuración
    current_app.logger.info(f"Sesión actual: {dict(session)}")
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
        
        logger.info("✅ Función list corregida con más logging")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al corregir la función list: {str(e)}")
        return False

def main():
    """Función principal que ejecuta las correcciones finales."""
    logger.info("Iniciando correcciones finales para el acceso a catálogos...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # 1. Corregir la función de obtención de ID de catálogo en el script de verificación
        id_catalogo_ok = corregir_obtener_id_catalogo()
        
        # 2. Crear o actualizar el usuario normal
        usuario_ok = crear_usuario_normal(db)
        
        # 3. Crear un catálogo para el usuario normal
        catalogo_ok = crear_catalogo_usuario(db)
        
        # 4. Corregir la función list para mejorar la depuración
        list_ok = corregir_funcion_list()
        
        # Resumen
        logger.info("\n=== RESUMEN DE CORRECCIONES FINALES ===")
        logger.info(f"1. Función obtener_id_primer_catalogo: {'✅ Corregida' if id_catalogo_ok else '❌ No corregida'}")
        logger.info(f"2. Usuario normal: {'✅ Creado/Actualizado' if usuario_ok else '❌ No creado/actualizado'}")
        logger.info(f"3. Catálogo para usuario normal: {'✅ Creado' if catalogo_ok else '❌ No creado'}")
        logger.info(f"4. Función list: {'✅ Corregida' if list_ok else '❌ No corregida'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Ejecuta el script de verificación final:")
        logger.info("   $ python3 verificar_final_catalogs.py")
        logger.info("3. Accede a la aplicación en http://127.0.0.1:8002")
        logger.info("4. Inicia sesión con las siguientes credenciales:")
        logger.info("   - Administrador: admin@example.com / admin123")
        logger.info("   - Usuario normal: usuario@example.com / admin123")
        logger.info("5. Navega a http://127.0.0.1:8002/catalogs para ver los catálogos")
        
        return True
    
    except Exception as e:
        logger.error(f"Error durante las correcciones finales: {str(e)}")
        return False
    
    finally:
        if client:
            client.close()
            logger.info("Conexión a MongoDB cerrada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
