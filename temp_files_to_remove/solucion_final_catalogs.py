#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import re
from pymongo import MongoClient
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

def crear_acceso_directo_simple():
    """Crea un script de acceso directo simple para los catálogos."""
    ruta_archivo = "acceso_directo_simple.py"
    
    try:
        contenido = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('http://127.0.0.1:8002/catalogs/')

if __name__ == '__main__':
    print("Acceso directo a catálogos iniciado en http://127.0.0.1:5001")
    print("Accede a http://127.0.0.1:5001 para ser redirigido automáticamente a los catálogos")
    app.run(host='127.0.0.1', port=5001, debug=True)
"""
        
        with open(ruta_archivo, 'w') as f:
            f.write(contenido)
        
        logger.info(f"✅ Script de acceso directo simple creado: {ruta_archivo}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al crear script de acceso directo simple: {str(e)}")
        return False

def modificar_catalogs_routes():
    """Modifica el archivo catalogs_routes.py para permitir acceso sin restricciones."""
    ruta_archivo = "app/routes/catalogs_routes.py"
    ruta_backup = "app/routes/catalogs_routes.py.bak.original"
    
    try:
        # Verificar si ya existe un backup original
        if not os.path.exists(ruta_backup):
            # Hacer backup del archivo original
            shutil.copy2(ruta_archivo, ruta_backup)
            logger.info(f"✅ Backup original creado: {ruta_backup}")
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Reemplazar el decorador check_catalog_permission
        contenido_modificado = re.sub(
            r'def check_catalog_permission\(f\):(.*?)return decorated_function',
            """def check_catalog_permission(f):
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
        current_app.logger.info(f"Acceso permitido al catálogo {catalog_id}")
        kwargs['catalog'] = catalog
        return f(*args, **kwargs)
    
    return decorated_function""",
            contenido,
            flags=re.DOTALL
        )
        
        # Reemplazar la función list
        contenido_modificado = re.sub(
            r'@catalogs_bp\.route\("/"\)\ndef list\(\):(.*?)return render_template\("catalogs\.html", catalogs=catalogs, session=session\)',
            """@catalogs_bp.route("/")
def list():
    # Verificar disponibilidad de MongoDB
    if not is_mongo_available():
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for('main.dashboard_user'))
    
    # Mostrar todos los catálogos sin restricciones
    current_app.logger.info("Acceso a lista de catálogos")
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
    return render_template("catalogs.html", catalogs=catalogs, session=session)""",
            contenido_modificado,
            flags=re.DOTALL
        )
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(contenido_modificado)
        
        logger.info("✅ Archivo catalogs_routes.py modificado para permitir acceso sin restricciones")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar catalogs_routes.py: {str(e)}")
        return False

def modificar_plantilla_catalogs():
    """Modifica la plantilla catalogs.html para mostrar todos los botones sin restricciones."""
    ruta_archivo = "app/templates/catalogs.html"
    ruta_backup = "app/templates/catalogs.html.bak.original"
    
    try:
        # Verificar si ya existe un backup original
        if not os.path.exists(ruta_backup) and os.path.exists(ruta_archivo):
            # Hacer backup del archivo original
            shutil.copy2(ruta_archivo, ruta_backup)
            logger.info(f"✅ Backup original creado: {ruta_backup}")
        
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            logger.warning(f"⚠️ El archivo {ruta_archivo} no existe")
            return False
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Reemplazar las condiciones que ocultan botones
        contenido_modificado = contenido.replace(
            '{% if session.get("logged_in") %}',
            '{% if True %}'
        )
        
        contenido_modificado = contenido_modificado.replace(
            '{% if session.get("role") == "admin" %}',
            '{% if True %}'
        )
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(contenido_modificado)
        
        logger.info("✅ Plantilla catalogs.html modificada para mostrar todos los botones")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar plantilla catalogs.html: {str(e)}")
        return False

def modificar_plantilla_ver_catalogo():
    """Modifica la plantilla ver_catalogo.html para mostrar todos los botones sin restricciones."""
    ruta_archivo = "app/templates/ver_catalogo.html"
    ruta_backup = "app/templates/ver_catalogo.html.bak.original"
    
    try:
        # Verificar si ya existe un backup original
        if not os.path.exists(ruta_backup) and os.path.exists(ruta_archivo):
            # Hacer backup del archivo original
            shutil.copy2(ruta_archivo, ruta_backup)
            logger.info(f"✅ Backup original creado: {ruta_backup}")
        
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            logger.warning(f"⚠️ El archivo {ruta_archivo} no existe")
            return False
        
        # Leer el archivo original
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()
        
        # Reemplazar las condiciones que ocultan botones
        contenido_modificado = contenido.replace(
            '{% if session.get("logged_in") %}',
            '{% if True %}'
        )
        
        contenido_modificado = contenido_modificado.replace(
            '{% if session.get("role") == "admin" %}',
            '{% if True %}'
        )
        
        # Guardar el archivo modificado
        with open(ruta_archivo, 'w') as f:
            f.write(contenido_modificado)
        
        logger.info("✅ Plantilla ver_catalogo.html modificada para mostrar todos los botones")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al modificar plantilla ver_catalogo.html: {str(e)}")
        return False

def main():
    """Función principal que ejecuta la solución final para los catálogos."""
    logger.info("Iniciando solución final para los catálogos...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # 1. Crear script de acceso directo simple
        acceso_directo_ok = crear_acceso_directo_simple()
        
        # 2. Modificar catalogs_routes.py
        catalogs_routes_ok = modificar_catalogs_routes()
        
        # 3. Modificar plantilla catalogs.html
        plantilla_catalogs_ok = modificar_plantilla_catalogs()
        
        # 4. Modificar plantilla ver_catalogo.html
        plantilla_ver_catalogo_ok = modificar_plantilla_ver_catalogo()
        
        # Resumen
        logger.info("\n=== RESUMEN DE LA SOLUCIÓN FINAL ===")
        logger.info(f"1. Script de acceso directo simple: {'✅ Creado' if acceso_directo_ok else '❌ No creado'}")
        logger.info(f"2. Modificar catalogs_routes.py: {'✅ Completado' if catalogs_routes_ok else '❌ No completado'}")
        logger.info(f"3. Modificar plantilla catalogs.html: {'✅ Completado' if plantilla_catalogs_ok else '❌ No completado'}")
        logger.info(f"4. Modificar plantilla ver_catalogo.html: {'✅ Completado' if plantilla_ver_catalogo_ok else '❌ No completado'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Inicia el script de acceso directo simple:")
        logger.info("   $ python3 acceso_directo_simple.py")
        logger.info("3. Accede directamente a los catálogos mediante las siguientes URLs:")
        logger.info("   - Acceso directo: http://127.0.0.1:5001")
        logger.info("   - Acceso directo a la lista de catálogos: http://127.0.0.1:8002/catalogs/")
        
        return True
    
    except Exception as e:
        logger.error(f"Error durante la solución final: {str(e)}")
        return False
    
    finally:
        if client:
            client.close()
            logger.info("Conexión a MongoDB cerrada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
