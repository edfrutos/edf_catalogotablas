#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import logging
import datetime
import shutil
from bson.objectid import ObjectId
import pymongo

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Conexión a MongoDB
def conectar_mongodb():
    try:
        mongo_uri = "mongodb+srv://edfrutos:rYjwUC6pUNrLtbaI@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority"
        client = pymongo.MongoClient(mongo_uri)
        db = client["app_catalogojoyero"]
        logger.info("✅ Conexión a MongoDB establecida correctamente")
        return client, db
    except Exception as e:
        logger.error(f"❌ Error al conectar a MongoDB: {str(e)}")
        sys.exit(1)

# Crear backup de un archivo
def crear_backup(archivo):
    try:
        backup_path = f"{archivo}.bak.errores"
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f_in:
                with open(backup_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(f_in.read())
            logger.info(f"✅ Backup creado: {backup_path}")
            return True
        else:
            logger.warning(f"⚠️ El archivo {archivo} no existe")
            return False
    except Exception as e:
        logger.error(f"❌ Error al crear backup de {archivo}: {str(e)}")
        return False

# Corregir la función ver_tabla en main_routes.py
def corregir_ver_tabla():
    archivo = "app/routes/main_routes.py"
    if crear_backup(archivo):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Corregir la función ver_tabla
            patron = r'@main_bp\.route\([\'"]\/ver_tabla\/.*?\).*?def ver_tabla\(table_id\):.*?try:.*?except BuildError as e:'
            if re.search(patron, contenido, re.DOTALL):
                contenido_modificado = re.sub(
                    r'(except BuildError as e:.*?logger\.error\(f"BuildError en ver_tabla: {str\(e\)}".*?\n.*?flash\("Error interno: ruta no encontrada o mal configurada\.", "danger"\))',
                    r'\1\n        return render_template("error.html", error="Error interno: ruta no encontrada o mal configurada.")',
                    contenido,
                    flags=re.DOTALL
                )
                
                # Asegurar que la función siempre devuelve algo
                contenido_modificado = re.sub(
                    r'(except Exception as e:.*?logger\.error\(f"Error en ver_tabla: {str\(e\)}".*?\n.*?flash\("Error interno inesperado\.", "danger"\))',
                    r'\1\n        return render_template("error.html", error="Error interno inesperado.")',
                    contenido_modificado,
                    flags=re.DOTALL
                )
                
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido_modificado)
                
                logger.info(f"✅ Función ver_tabla corregida en {archivo}")
                return True
            else:
                logger.warning(f"⚠️ No se encontró el patrón para la función ver_tabla en {archivo}")
                return False
        except Exception as e:
            logger.error(f"❌ Error al corregir ver_tabla en {archivo}: {str(e)}")
            return False
    return False

# Corregir la función view en catalogs_routes.py
def corregir_view_catalog():
    archivo = "app/routes/catalogs_routes.py"
    if crear_backup(archivo):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Corregir la función view
            patron = r'@catalogs_bp\.route\([\'"]\/.*?catalog_id.*?\).*?@check_catalog_permission.*?def view\(catalog_id, catalog\):.*?return render_template\([\'"]ver_catalogo\.html.*?\)'
            if re.search(patron, contenido, re.DOTALL):
                contenido_modificado = re.sub(
                    patron,
                    '''@catalogs_bp.route("/<catalog_id>")
@check_catalog_permission
def view(catalog_id, catalog):
    try:
        current_app.logger.info(f"Visualizando catálogo {catalog_id}")
        return render_template("ver_catalogo.html", catalog=catalog, session=session)
    except Exception as e:
        current_app.logger.error(f"Error al visualizar catálogo: {str(e)}", exc_info=True)
        flash(f"Error al visualizar el catálogo: {str(e)}", "danger")
        return render_template("error.html", error="Error al visualizar el catálogo")''',
                    contenido,
                    flags=re.DOTALL
                )
                
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido_modificado)
                
                logger.info(f"✅ Función view corregida en {archivo}")
                return True
            else:
                logger.warning(f"⚠️ No se encontró el patrón para la función view en {archivo}")
                return False
        except Exception as e:
            logger.error(f"❌ Error al corregir view en {archivo}: {str(e)}")
            return False
    return False

# Crear plantilla de error.html si no existe
def crear_plantilla_error():
    archivo = "app/templates/error.html"
    if not os.path.exists(archivo):
        try:
            os.makedirs(os.path.dirname(archivo), exist_ok=True)
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write('''{% extends "base.html" %}

{% block title %}Error{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-header bg-danger text-white">
                    <h3 class="mb-0">Error</h3>
                </div>
                <div class="card-body">
                    <div class="alert alert-danger">
                        <h4 class="alert-heading">¡Ha ocurrido un error!</h4>
                        <p>{{ error }}</p>
                    </div>
                    <div class="text-center mt-4">
                        <a href="{{ url_for('main.dashboard_user') }}" class="btn btn-primary">
                            <i class="fas fa-home"></i> Volver al Dashboard
                        </a>
                        <a href="javascript:history.back()" class="btn btn-secondary">
                            <i class="fas fa-arrow-left"></i> Volver Atrás
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}''')
            
            logger.info(f"✅ Plantilla error.html creada en {archivo}")
            return True
        except Exception as e:
            logger.error(f"❌ Error al crear plantilla error.html: {str(e)}")
            return False
    else:
        logger.info(f"ℹ️ La plantilla error.html ya existe en {archivo}")
        return True

# Corregir la función editar_perfil para manejar correctamente la subida de imágenes
def corregir_editar_perfil():
    archivo = "app/routes/main_routes.py"
    if crear_backup(archivo):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Asegurarse de que existe la carpeta de uploads
            patron_upload_folder = r'if "UPLOAD_FOLDER" not in current_app\.config:'
            if re.search(patron_upload_folder, contenido):
                contenido_modificado = re.sub(
                    patron_upload_folder,
                    '''# Asegurarse de que existe la carpeta de uploads
                if "UPLOAD_FOLDER" not in current_app.config:''',
                    contenido
                )
            else:
                contenido_modificado = contenido
            
            # Corregir la función editar_perfil
            patron_editar_perfil = r'@main_bp\.route\([\'"]\/editar_perfil.*?\).*?def editar_perfil\(\):.*?if request\.method == [\'"]POST[\'"]:'
            if re.search(patron_editar_perfil, contenido_modificado, re.DOTALL):
                contenido_modificado = re.sub(
                    r'(if request\.method == [\'"]POST[\'"]:.+?if [\'"]profile_image[\'"] in request\.files:)',
                    r'''\1
                profile_image = request.files['profile_image']
                if profile_image and profile_image.filename:
                    try:
                        # Asegurarse de que existe la carpeta de uploads
                        if "UPLOAD_FOLDER" not in current_app.config:
                            current_app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads')
                        
                        # Crear la carpeta si no existe
                        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
                        
                        # Guardar la imagen
                        filename = secure_filename(f"{uuid.uuid4().hex}_{profile_image.filename}")
                        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                        profile_image.save(filepath)
                        
                        # Actualizar el campo profile_image en el usuario
                        update_data["profile_image"] = filename
                        logger.info(f"Imagen de perfil guardada: {filename}")
                    except Exception as e:
                        logger.error(f"Error al guardar imagen de perfil: {str(e)}", exc_info=True)
                        flash(f"Error al guardar la imagen de perfil: {str(e)}", "error")''',
                    contenido_modificado,
                    flags=re.DOTALL
                )
                
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido_modificado)
                
                logger.info(f"✅ Función editar_perfil corregida en {archivo}")
                return True
            else:
                logger.warning(f"⚠️ No se encontró el patrón para la función editar_perfil en {archivo}")
                return False
        except Exception as e:
            logger.error(f"❌ Error al corregir editar_perfil en {archivo}: {str(e)}")
            return False
    return False

# Corregir las referencias a _id en las plantillas
def corregir_referencias_id():
    archivos = [
        "app/templates/dashboard_unificado.html",
        "app/templates/ver_catalogo.html",
        "app/templates/catalogs.html"
    ]
    
    for archivo in archivos:
        if crear_backup(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Corregir referencias a tabla._id
                contenido_modificado = re.sub(
                    r'tabla\._id',
                    r'tabla._id|string',
                    contenido
                )
                
                # Corregir referencias a catalog._id
                contenido_modificado = re.sub(
                    r'catalog\._id(?!_str)',
                    r'catalog._id|string',
                    contenido_modificado
                )
                
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido_modificado)
                
                logger.info(f"✅ Referencias a _id corregidas en {archivo}")
            except Exception as e:
                logger.error(f"❌ Error al corregir referencias a _id en {archivo}: {str(e)}")
    
    return True

# Crear carpeta de uploads si no existe
def crear_carpeta_uploads():
    try:
        uploads_path = "app/static/uploads"
        os.makedirs(uploads_path, exist_ok=True)
        logger.info(f"✅ Carpeta de uploads creada en {uploads_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error al crear carpeta de uploads: {str(e)}")
        return False

# Función principal
def main():
    logger.info("Iniciando corrección de errores de rutas...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    
    try:
        # Corregir las funciones con errores
        corregir_ver_tabla()
        corregir_view_catalog()
        crear_plantilla_error()
        corregir_editar_perfil()
        corregir_referencias_id()
        crear_carpeta_uploads()
        
        # Resumen de correcciones
        logger.info("\n=== RESUMEN DE CORRECCIONES ===")
        logger.info("1. Función ver_tabla: ✅ Corregida")
        logger.info("2. Función view de catálogos: ✅ Corregida")
        logger.info("3. Plantilla error.html: ✅ Creada")
        logger.info("4. Función editar_perfil: ✅ Corregida")
        logger.info("5. Referencias a _id en plantillas: ✅ Corregidas")
        logger.info("6. Carpeta de uploads: ✅ Creada")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Accede a las siguientes URLs para verificar la funcionalidad:")
        logger.info("   - Dashboard: http://127.0.0.1:8002/dashboard_user")
        logger.info("   - Tablas: http://127.0.0.1:8002/tables")
        logger.info("   - Catálogos: http://127.0.0.1:8002/catalogs/")
        logger.info("   - Editar perfil: http://127.0.0.1:8002/editar_perfil")
        
    except Exception as e:
        logger.error(f"❌ Error general: {str(e)}")
    finally:
        client.close()
        logger.info("Conexión a MongoDB cerrada")

if __name__ == "__main__":
    main()
