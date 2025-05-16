# app/routes/catalogs_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app, jsonify
from bson.objectid import ObjectId
from functools import wraps
import os
import uuid
import datetime
from werkzeug.utils import secure_filename
from app.extensions import mongo
from app.utils.mongo_utils import is_mongo_available, is_valid_object_id
from app.decorators import is_datetime, is_list, is_string
import logging

logger = logging.getLogger(__name__)

# Función para verificar si el usuario es administrador
def is_admin():
    role = session.get('role')
    current_app.logger.info(f"Rol en sesión: {role}")
    return role == 'admin'

# Decorador para verificar permisos
# Admin puede acceder a cualquier catálogo, usuarios solo a los suyos
# El campo created_by se compara con el username de sesión

def is_valid_object_id(id_str):
    """Verifica si una cadena es un ObjectId válido"""
    try:
        ObjectId(id_str)
        return True
    except Exception:
        return False

def check_catalog_permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        catalog_id = kwargs.get('catalog_id')
        if not catalog_id:
            current_app.logger.error("ID de catálogo no proporcionado")
            flash("Error: ID de catálogo no proporcionado", "danger")
            return redirect(url_for('catalogs.list'))
        
        current_app.logger.info(f"Verificando permisos para catálogo ID: {catalog_id}")
        
        try:
            # Validar el formato del ID del catálogo
            if not is_valid_object_id(catalog_id):
                current_app.logger.error(f"ID de catálogo inválido (formato incorrecto): {catalog_id}")
                flash("El ID del catálogo no tiene el formato correcto", "warning")
                return redirect(url_for('catalogs.list'))
            
            # Convertir a ObjectId para búsquedas
            object_id = ObjectId(catalog_id)
            
            # Inicializar variables
            catalog = None
            collections_to_check = ['spreadsheets', 'catalogs']  # Orden de prioridad para buscar
            
            # Buscar el catálogo en las colecciones principales
            for collection_name in collections_to_check:
                try:
                    collection = mongo.db[collection_name]
                    # Buscar por ObjectId
                    catalog = collection.find_one({"_id": object_id})
                    if catalog:
                        current_app.logger.info(f"Catálogo encontrado en {collection_name} con ObjectId: {catalog_id}")
                        break
                except Exception as e:
                    current_app.logger.error(f"Error al buscar en {collection_name} por ObjectId: {str(e)}")
            
            # Si no se encuentra, buscar en otras colecciones
            if not catalog:
                try:
                    # Obtener todas las colecciones disponibles
                    all_collections = mongo.db.list_collection_names()
                    # Filtrar colecciones que podrían contener catálogos
                    potential_collections = [c for c in all_collections 
                                            if c not in collections_to_check and 
                                            not c.startswith('system.') and 
                                            not c.endswith('_backup')]                    
                    
                    # Buscar en las colecciones potenciales
                    for collection_name in potential_collections:
                        try:
                            collection = mongo.db[collection_name]
                            catalog = collection.find_one({"_id": object_id})
                            if catalog:
                                current_app.logger.info(f"Catálogo encontrado en {collection_name} con ObjectId: {catalog_id}")
                                break
                        except Exception as e:
                            current_app.logger.error(f"Error al buscar en {collection_name}: {str(e)}")
                except Exception as e:
                    current_app.logger.error(f"Error al listar colecciones: {str(e)}")
            
            # Si aún no se encuentra, intentar buscar por nombre o similares
            if not catalog:
                try:
                    # Buscar por nombre en las colecciones principales
                    for collection_name in collections_to_check:
                        collection = mongo.db[collection_name]
                        catalog = collection.find_one({"name": catalog_id})
                        if catalog:
                            current_app.logger.info(f"Catálogo encontrado en {collection_name} por nombre: {catalog_id}")
                            break
                except Exception as e:
                    current_app.logger.error(f"Error al buscar por nombre: {str(e)}")
            
            # Si todavía no se encuentra, mostrar información para depuración
            if not catalog:
                try:
                    # Buscar catálogos similares para ayudar en la depuración
                    similar_catalogs = []
                    for collection_name in collections_to_check:
                        collection = mongo.db[collection_name]
                        sample_catalogs = list(collection.find({}, {"_id": 1, "name": 1, "created_by": 1, "owner": 1}).limit(5))
                        for cat in sample_catalogs:
                            similar_catalogs.append({
                                "collection": collection_name,
                                "id": str(cat["_id"]),
                                "name": cat.get("name", "Sin nombre"),
                                "owner": cat.get("created_by", cat.get("owner", "Sin propietario"))
                            })
                    
                    if similar_catalogs:
                        current_app.logger.info(f"Catálogos disponibles para referencia: {similar_catalogs}")
                except Exception as e:
                    current_app.logger.error(f"Error al buscar catálogos similares: {str(e)}")
            
            # Si no se encuentra el catálogo, redirigir a la lista
            if not catalog:
                current_app.logger.error(f"Catálogo no encontrado: {catalog_id}")
                flash("Catálogo no encontrado", "warning")
                return redirect(url_for('catalogs.list'))
            
            # Verificar permisos de acceso al catálogo
            username = session.get('username')
            email = session.get('email')
            role = session.get('role')
            current_app.logger.info(f"Rol en sesión: {role}")
            
            # Asegurar que el catálogo tenga el campo created_by
            if 'created_by' not in catalog or not catalog.get('created_by'):
                owner = catalog.get('owner_name') or catalog.get('owner') or catalog.get('email') or 'admin@example.com'
                catalog['created_by'] = owner
                # Intentar actualizar el documento en la base de datos
                try:
                    for collection_name in collections_to_check:
                        collection = mongo.db[collection_name]
                        result = collection.update_one({"_id": object_id}, {"$set": {"created_by": owner}})
                        if result.modified_count > 0:
                            current_app.logger.info(f"Añadido campo created_by={owner} al catálogo {catalog_id}")
                            break
                except Exception as e:
                    current_app.logger.error(f"Error al actualizar campo created_by: {str(e)}")
            
            # Obtener el creador del catálogo (puede estar en diferentes campos)
            catalog_owner = catalog.get('created_by') or catalog.get('owner') or catalog.get('email')
            
            current_app.logger.info(f"Usuario: {username}, Email: {email}, Rol: {role}, Propietario del catálogo: {catalog_owner}")
            
            # Comprobar si el usuario tiene permiso para acceder al catálogo
            # Verificar por username, email o rol de administrador
            if (role == 'admin' or 
                catalog_owner == username or 
                catalog_owner == email or
                catalog.get('email') == email):
                # Usuario autorizado, pasar el catálogo a la función decorada
                kwargs['catalog'] = catalog
                return f(*args, **kwargs)
            else:
                # Usuario no autorizado
                current_app.logger.warning(f"Acceso denegado: Usuario {username} ({email}) intentó acceder al catálogo {catalog_id} de {catalog_owner}")
                flash("No tienes permiso para acceder a este catálogo", "danger")
                return redirect(url_for('catalogs.list'))
        
        except Exception as e:
            current_app.logger.error(f"Error en check_catalog_permission: {str(e)}")
            flash(f"Error al verificar permisos: {str(e)}", "danger")
            return redirect(url_for('catalogs.list'))
    
    return decorated_function

catalogs_bp = Blueprint("catalogs", __name__, url_prefix="/catalogs")

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def get_upload_dir():
    # Absolute path to static/uploads irrespective of where the app package is located
    folder = os.path.join(current_app.static_folder, 'uploads')
    os.makedirs(folder, exist_ok=True)
    return folder

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@catalogs_bp.route("/")
def list_catalogs():
    try:
        # Verificar si el usuario está autenticado
        if 'username' not in session:
            flash('Debe iniciar sesión para ver los catálogos', 'warning')
            return redirect(url_for('auth.login'))
            
        # Obtener el nombre de usuario y rol de la sesión
        username = session.get('username')
        role = session.get('role')
        current_app.logger.info(f"Rol en sesión: {role}")
        
        # Obtener parámetros de búsqueda
        search_query = request.args.get('search', '').strip()
        search_type = request.args.get('search_type', 'name')
        
        # Construir el filtro de búsqueda
        filter_query = {}
        
        # Si hay una búsqueda, aplicar el filtro correspondiente
        if search_query:
            if search_type == 'name':
                # Búsqueda por nombre (insensible a mayúsculas/minúsculas)
                filter_query['name'] = {'$regex': search_query, '$options': 'i'}
                current_app.logger.info(f"Búsqueda por nombre: {search_query}")
            elif search_type == 'user':
                # Búsqueda por usuario creador (insensible a mayúsculas/minúsculas)
                filter_query['created_by'] = {'$regex': search_query, '$options': 'i'}
                current_app.logger.info(f"Búsqueda por usuario: {search_query}")
        
        # Obtener las colecciones de catálogos
        from app.extensions import mongo
        collections_to_check = ['catalogs', 'spreadsheets']
        all_catalogs = []
        
        # Buscar en todas las colecciones relevantes
        for collection_name in collections_to_check:
            try:
                collection = mongo.db[collection_name]
                current_app.logger.info(f"Buscando catálogos en la colección {collection_name}")
                
                # Aplicar filtros según el rol del usuario
                if role == 'admin':
                    # Para admins, aplicar solo el filtro de búsqueda
                    catalogs_cursor = collection.find(filter_query)
                else:
                    # Para usuarios normales, combinar el filtro de búsqueda con el filtro de usuario
                    user_filter = {"created_by": username}
                    # Combinar filtros
                    if filter_query:
                        # Usar $and para combinar ambos filtros
                        catalogs_cursor = collection.find({"$and": [filter_query, user_filter]})
                    else:
                        # Si no hay filtro de búsqueda, usar solo el filtro de usuario
                        catalogs_cursor = collection.find(user_filter)
                
                # Convertir el cursor a lista y añadir a los resultados
                for catalog in catalogs_cursor:
                    # Añadir información sobre la colección de origen
                    catalog['collection_source'] = collection_name
                    all_catalogs.append(catalog)
            except Exception as e:
                current_app.logger.error(f"Error al buscar en colección {collection_name}: {str(e)}")
        
        current_app.logger.info(f"Total de catálogos encontrados en todas las colecciones: {len(all_catalogs)}")
        
        # Usar la lista combinada de catálogos
        catalogs = all_catalogs
        
        # Registrar información sobre los catálogos encontrados según el rol
        if role == 'admin':
            current_app.logger.info(f"[ADMIN] Mostrando catálogos filtrados para el administrador {username}")
        else:
            current_app.logger.info(f"[USER] Mostrando catálogos filtrados para el usuario {username}")
            
        # Convertir el cursor a una lista para poder usarlo en la plantilla
        catalogs_list = []
        catalog_ids = []
        
        for catalog in catalogs:
            try:
                # Guardar el ID original para depuración
                original_id = catalog.get('_id')
                catalog_ids.append(str(original_id))
                
                # Asegurarse de que _id_str existe y es correcto
                catalog['_id_str'] = str(original_id)
                
                # Calcular el número de filas del catálogo
                if 'rows' in catalog and catalog['rows'] is not None:
                    catalog['row_count'] = len(catalog['rows'])
                elif 'data' in catalog and catalog['data'] is not None:
                    catalog['row_count'] = len(catalog['data'])
                else:
                    catalog['row_count'] = 0
                
                # Formatear la fecha de creación
                if 'created_at' in catalog and catalog['created_at']:
                    try:
                        # Verificar si es un objeto datetime usando hasattr en lugar de isinstance
                        if hasattr(catalog['created_at'], 'strftime'):
                            catalog['created_at_formatted'] = catalog['created_at'].strftime('%d/%m/%Y %H:%M')
                        else:
                            # Si ya es una cadena, usarla directamente
                            catalog['created_at_formatted'] = str(catalog['created_at'])
                    except Exception as e:
                        current_app.logger.error(f"Error al formatear fecha: {str(e)}")
                        catalog['created_at_formatted'] = str(catalog['created_at'])
                else:
                    catalog['created_at_formatted'] = 'N/A'
                    
                # Asegurarse de que todos los campos necesarios existan
                if 'headers' not in catalog or catalog['headers'] is None:
                    catalog['headers'] = []
                if 'data' not in catalog and 'rows' not in catalog:
                    catalog['data'] = []
                elif 'rows' in catalog and 'data' not in catalog:
                    catalog['data'] = catalog['rows']
                    
                # Asegurarse de que hay un creador/propietario
                if 'created_by' not in catalog or not catalog['created_by']:
                    catalog['created_by'] = catalog.get('owner_name') or catalog.get('owner') or 'Desconocido'
                    
                catalogs_list.append(catalog)
            except Exception as e:
                current_app.logger.error(f"Error al procesar catálogo: {str(e)}")
                continue
        
        # Registrar los IDs de los catálogos para depuración
        current_app.logger.info(f"IDs de catálogos listados: {catalog_ids}")
        current_app.logger.info(f"Total de catálogos encontrados: {len(catalogs_list)}")
            
        return render_template('catalogs.html', catalogs=catalogs_list, is_admin=is_admin(), current_user_email=session.get('username'), search_query=search_query, search_type=search_type)
    except Exception as e:
        current_app.logger.error(f"Error al listar catálogos: {str(e)}", exc_info=True)
        flash(f"Error al listar los catálogos: {str(e)}", "danger")
        return render_template("error.html", error="Error al listar los catálogos")

# Alias para la función list_catalogs para mantener compatibilidad con las plantillas
@catalogs_bp.route("/")
def list():
    return list_catalogs()

@catalogs_bp.route("/<catalog_id>")
@check_catalog_permission
def view(catalog_id, catalog):
    try:
        current_app.logger.info(f"Visualizando catálogo {catalog_id}")
        
        # Registrar información del catálogo para depuración
        current_app.logger.info(f"Datos del catálogo: ID={catalog.get('_id')}, Nombre={catalog.get('name')}, Creado por={catalog.get('created_by') or catalog.get('owner_name') or catalog.get('owner')}")
        
        # Asegurarse de que el catálogo tiene los campos necesarios
        if 'headers' not in catalog or catalog['headers'] is None:
            catalog['headers'] = []
            current_app.logger.info(f"Añadiendo campo 'headers' vacío al catálogo {catalog_id}")
        
        # Manejar diferentes estructuras de datos (rows o data)
        if 'rows' in catalog and catalog['rows'] is not None:
            catalog['data'] = catalog['rows']
            # Asegurar que rows y data son consistentes
            catalog['rows'] = catalog['data']
            current_app.logger.info(f"Usando 'rows' como 'data' para el catálogo {catalog_id}")
        elif 'data' in catalog and catalog['data'] is not None:
            # Asegurar que rows y data son consistentes
            catalog['rows'] = catalog['data']
            current_app.logger.info(f"Usando 'data' como 'rows' para el catálogo {catalog_id}")
        else:
            # Si no hay ni rows ni data, inicializar ambos como listas vacías
            catalog['data'] = []
            catalog['rows'] = []
            current_app.logger.info(f"Añadiendo campos 'data' y 'rows' vacíos al catálogo {catalog_id}")
        
        # Asegurarse de que _id_str existe
        catalog['_id_str'] = str(catalog['_id'])
        
        # Asegurarse de que los campos de fecha se manejen correctamente
        from datetime import datetime
        
        # Manejar created_at
        if 'created_at' in catalog and catalog['created_at']:
            # Usar is_string en lugar de isinstance para evitar errores
            if catalog['created_at'] and not is_string(catalog['created_at']):
                try:
                    # Importar datetime para la comparación
                    from datetime import datetime
                    # Si es un objeto datetime, mantenerlo como está
                    if hasattr(catalog['created_at'], 'strftime'):  # Verificar si es un objeto datetime
                        catalog['created_at'] = catalog['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        # Convertir a string formateado si no es un datetime
                        catalog['created_at'] = str(catalog['created_at'])
                except Exception as e:
                    current_app.logger.error(f"Error al procesar created_at: {str(e)}")
                    catalog['created_at'] = str(catalog['created_at'])
        else:
            catalog['created_at'] = "No disponible"
        
        # Manejar updated_at
        if 'updated_at' in catalog and catalog['updated_at']:
            # Usar is_string en lugar de isinstance para evitar errores
            if catalog['updated_at'] and not is_string(catalog['updated_at']):
                try:
                    # Importar datetime para la comparación
                    from datetime import datetime
                    # Si es un objeto datetime, mantenerlo como está
                    if hasattr(catalog['updated_at'], 'strftime'):  # Verificar si es un objeto datetime
                        catalog['updated_at'] = catalog['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        # Convertir a string formateado si no es un datetime
                        catalog['updated_at'] = str(catalog['updated_at'])
                except Exception as e:
                    current_app.logger.error(f"Error al procesar updated_at: {str(e)}")
                    catalog['updated_at'] = str(catalog['updated_at'])
        else:
            catalog['updated_at'] = "No disponible"
        
        # Registrar información adicional para depuración
        current_app.logger.info(f"Catálogo preparado para visualización: ID={catalog['_id_str']}, Headers={len(catalog['headers'])}, Datos={len(catalog['data'])}")
        current_app.logger.info(f"Fechas: created_at={catalog['created_at']} ({type(catalog['created_at']).__name__}), updated_at={catalog['updated_at']} ({type(catalog['updated_at']).__name__})")
        
        return render_template("ver_catalogo.html", catalog=catalog, session=session)
    except Exception as e:
        current_app.logger.error(f"Error al visualizar catálogo: {str(e)}", exc_info=True)
        flash(f"Error al visualizar el catálogo: {str(e)}", "danger")
        return redirect(url_for('catalogs.list'))

@catalogs_bp.route("/<catalog_id>/edit", methods=["GET", "POST"])
@check_catalog_permission
def edit(catalog_id, catalog):
    if request.method == "POST":
        try:
            # Obtener los datos del formulario
            new_name = request.form.get("name", "").strip()
            headers_str = request.form.get("headers", "").strip()
            
            # Validar los datos
            if not new_name:
                flash("El nombre del catálogo no puede estar vacío.", "error")
                return render_template("editar_catalogo.html", catalog=catalog, session=session)
            
            # Procesar los encabezados
            new_headers = [h.strip() for h in headers_str.split(",") if h.strip()]
            
            if not new_headers:
                flash("Debe proporcionar al menos un encabezado.", "error")
                return render_template("editar_catalogo.html", catalog=catalog, session=session)
            
            # Actualizar el catálogo en la base de datos
            current_app.logger.info(f"Actualizando catálogo {catalog_id} con nombre={new_name}, headers={new_headers}")
            
            # Intentar actualizar en ambas colecciones posibles
            collections_to_check = ['catalogs', 'spreadsheets']
            update_success = False
            
            for collection_name in collections_to_check:
                try:
                    collection = mongo.db[collection_name]
                    result = collection.update_one(
                        {"_id": ObjectId(catalog_id)},
                        {"$set": {
                            "name": new_name,
                            "headers": new_headers,
                            "updated_at": datetime.datetime.utcnow()
                        }}
                    )
                    
                    if result.matched_count > 0:
                        current_app.logger.info(f"Catálogo actualizado en colección {collection_name}: {result.modified_count} documento(s) modificado(s)")
                        update_success = True
                        break
                except Exception as e:
                    current_app.logger.error(f"Error al actualizar catálogo en {collection_name}: {str(e)}")
            
            if not update_success:
                raise Exception("No se pudo actualizar el catálogo en ninguna colección")
            
            flash("Catálogo actualizado correctamente.", "success")
            return redirect(url_for("catalogs.view", catalog_id=catalog_id))
        
        except Exception as e:
            current_app.logger.error(f"Error al actualizar catálogo: {str(e)}", exc_info=True)
            flash(f"Error al actualizar el catálogo: {str(e)}", "error")
            return render_template("editar_catalogo.html", catalog=catalog, session=session)
    
    # Método GET: mostrar formulario
    return render_template("editar_catalogo.html", catalog=catalog, session=session)

@catalogs_bp.route("/edit-row/<catalog_id>/<int:row_index>", methods=["GET", "POST"])
@check_catalog_permission
def edit_row(catalog_id, row_index, catalog):
    if not is_mongo_available():
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for("catalogs.view", catalog_id=catalog_id))
    # Obtener la fila correspondiente
    row_data = catalog["rows"][row_index] if 0 <= row_index < len(catalog["rows"]) else None
    
    # Registrar información sobre la fila para depuración
    current_app.logger.info(f"Datos de la fila a editar: {row_data}")
    
    # Verificar si hay imágenes en la fila y asegurarse de que estén en el formato correcto
    if row_data:
        # Verificar todos los posibles campos de imágenes
        if 'imagenes' in row_data and row_data['imagenes']:
            current_app.logger.info(f"Imágenes encontradas en 'imagenes': {row_data['imagenes']}")
            # Asegurarse de que sea una lista
            if not is_list(row_data['imagenes']):
                row_data['imagenes'] = [row_data['imagenes']]
        elif 'images' in row_data and row_data['images']:
            current_app.logger.info(f"Imágenes encontradas en 'images': {row_data['images']}")
            # Copiar las imágenes de 'images' a 'imagenes' para mantener consistencia
            if not is_list(row_data['images']):
                row_data['imagenes'] = [row_data['images']]
            else:
                row_data['imagenes'] = row_data['images']
        # Verificar si hay un campo 'imagen' singular
        elif 'imagen' in row_data and row_data['imagen']:
            current_app.logger.info(f"Imagen encontrada en 'imagen': {row_data['imagen']}")
            row_data['imagenes'] = [row_data['imagen']]
        # Verificar si hay un campo 'image' singular
        elif 'image' in row_data and row_data['image']:
            current_app.logger.info(f"Imagen encontrada en 'image': {row_data['image']}")
            row_data['imagenes'] = [row_data['image']]
        else:
            current_app.logger.info("No se encontraron imágenes en la fila")
            # Inicializar el campo 'imagenes' como una lista vacía
            row_data['imagenes'] = []
            
        # Asegurarse de que el campo 'imagenes' exista
        if 'imagenes' not in row_data:
            row_data['imagenes'] = []
            
        current_app.logger.info(f"Campo 'imagenes' final: {row_data['imagenes']}")
    if request.method == "POST":
        # Actualizar los datos de la fila
        for header in catalog["headers"]:
            row_data[header] = request.form.get(header, "")
        # Procesar imágenes
        # Asegurarse de que imagenes sea una lista
        if 'imagenes' not in row_data:
            row_data['imagenes'] = []
        elif not is_list(row_data['imagenes']):
            # Si no es una lista, convertirlo a lista
            if row_data['imagenes']:
                row_data['imagenes'] = [row_data['imagenes']]
            else:
                row_data['imagenes'] = []
            
        current_app.logger.info(f"Imágenes actuales: {row_data['imagenes']}")
        
        # Procesar imágenes a eliminar
        imagenes_a_eliminar_json = request.form.get('imagenes_a_eliminar', '')
        if imagenes_a_eliminar_json:
            try:
                import json
                imagenes_a_eliminar = json.loads(imagenes_a_eliminar_json)
                current_app.logger.info(f"Imágenes a eliminar: {imagenes_a_eliminar}")
                
                # Filtrar las imágenes a eliminar
                if imagenes_a_eliminar and is_list(imagenes_a_eliminar):
                    row_data['imagenes'] = [img for img in row_data['imagenes'] if img not in imagenes_a_eliminar]
                    current_app.logger.info(f"Imágenes después de eliminar: {row_data['imagenes']}")
            except Exception as e:
                current_app.logger.error(f"Error al procesar imágenes a eliminar: {str(e)}")
        
        # Procesar nuevas imágenes
        if 'imagenes' in request.files:
            files = request.files.getlist('imagenes')
            upload_dir = get_upload_dir()
            nuevas_imagenes = []
            
            for file in files:
                if file and file.filename and allowed_image(file.filename):
                    filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    nuevas_imagenes.append(filename)
                    current_app.logger.info(f"Nueva imagen guardada: {filename}")
            
            # Añadir nuevas imágenes a las existentes
            if nuevas_imagenes:
                row_data['imagenes'].extend(nuevas_imagenes)
                current_app.logger.info(f"Imágenes actualizadas: {row_data['imagenes']}")
        # Guardar la fila actualizada en la base de datos
        mongo.db.catalogs.update_one(
            {"_id": catalog["_id"]},
            {"$set": {f"rows.{row_index}": row_data}}
        )
        flash("Fila actualizada correctamente", "success")
        return redirect(url_for("catalogs.view", catalog_id=str(catalog["_id"])) )
    return render_template("editar_fila.html", catalog=catalog, fila=row_data, row_index=row_index, session=session, headers=catalog["headers"])

@catalogs_bp.route("/add-row/<catalog_id>", methods=["GET", "POST"])
@check_catalog_permission
def add_row(catalog_id, catalog):
    if not is_mongo_available():
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for("catalogs.view", catalog_id=catalog_id))
    if request.method == "POST":
        # Procesar datos del formulario
        row = {}
        for header in catalog["headers"]:
            row[header] = request.form.get(header, "")
        # Procesar imágenes
        imagenes = []
        if 'imagenes' in request.files:
            files = request.files.getlist('imagenes')
            upload_dir = get_upload_dir()
            for file in files:
                if file and allowed_image(file.filename):
                    filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                    file.save(os.path.join(upload_dir, filename))
                    imagenes.append(filename)
        row['imagenes'] = imagenes
        # Agregar la fila al catálogo en ambos campos (rows y data) para mantener consistencia
        try:
            # Determinar en qué colección está el catálogo
            collections_to_check = ['catalogs', 'spreadsheets']
            update_success = False
            
            for collection_name in collections_to_check:
                try:
                    collection = mongo.db[collection_name]
                    # Intentar actualizar tanto rows como data para mantener consistencia
                    result = collection.update_one(
                        {"_id": ObjectId(catalog_id)},
                        {
                            "$push": {
                                "rows": row,
                                "data": row
                            },
                            "$set": {
                                "updated_at": datetime.datetime.utcnow()
                            }
                        }
                    )
                    
                    if result.matched_count > 0:
                        current_app.logger.info(f"Fila agregada al catálogo {catalog_id} en colección {collection_name}")
                        update_success = True
                        break
                except Exception as e:
                    current_app.logger.error(f"Error al agregar fila en {collection_name}: {str(e)}")
            
            if not update_success:
                raise Exception("No se pudo agregar la fila al catálogo en ninguna colección")
        except Exception as e:
            current_app.logger.error(f"Error al agregar fila: {str(e)}")
            flash(f"Error al agregar fila: {str(e)}", "danger")
            return redirect(url_for("catalogs.view", catalog_id=catalog_id))
        flash("Fila agregada correctamente", "success")
        return redirect(url_for("catalogs.view", catalog_id=catalog_id))
    return render_template("agregar_fila.html", catalog=catalog, session=session)

# Eliminar fila de un catálogo
@catalogs_bp.route("/delete-row/<catalog_id>/<int:row_index>", methods=["GET", "POST"])
@check_catalog_permission
def delete_row(catalog_id, row_index, catalog):
    if not is_mongo_available():
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for("catalogs.view", catalog_id=catalog_id))
    try:
        # Obtener todas las filas actuales
        current_rows = catalog.get("rows", [])
        
        # Registrar información de depuración
        current_app.logger.info(f"Catálogo ID: {catalog_id}, Tipo: {type(catalog_id)}")
        current_app.logger.info(f"Filas actuales: {len(current_rows)}")
        current_app.logger.info(f"Intentando eliminar fila en índice: {row_index}")
        
        # Verificar que el índice es válido
        if row_index < 0 or row_index >= len(current_rows):
            flash(f"Índice de fila inválido: {row_index}. Total de filas: {len(current_rows)}", "danger")
            return redirect(url_for("catalogs.view", catalog_id=catalog_id))
        
        # Guardar la fila que se va a eliminar para depuración
        row_to_delete = current_rows[row_index]
        current_app.logger.info(f"Fila a eliminar: {row_to_delete}")
        
        # Eliminar la fila específica por índice
        current_app.logger.info(f"Eliminando fila {row_index} del catálogo {catalog_id}")
        current_rows.pop(row_index)
        
        # Actualizar el documento con las filas restantes
        result = mongo.db.catalogs.update_one(
            {"_id": ObjectId(catalog_id)},
            {"$set": {"rows": current_rows}}
        )
        
        current_app.logger.info(f"Resultado de la actualización: {result.modified_count} documento(s) modificado(s)")
        
        if result.modified_count > 0:
            flash("Fila eliminada correctamente", "success")
        else:
            flash("No se pudo eliminar la fila. Inténtelo de nuevo.", "warning")
            
    except Exception as e:
        current_app.logger.error(f"Error al eliminar fila: {str(e)}", exc_info=True)
        flash(f"Error al eliminar fila: {str(e)}", "danger")
        
    return redirect(url_for("catalogs.view", catalog_id=catalog_id))

# Eliminar catálogo
@catalogs_bp.route("/delete/<catalog_id>", methods=["GET", "POST"])
@check_catalog_permission
def delete_catalog(catalog_id, catalog):
    if not is_mongo_available():
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for("catalogs.list"))
    
    # Agregar logs para depuración
    current_app.logger.info(f"Intento de eliminación de catálogo: {catalog_id}")
    current_app.logger.info(f"Método HTTP: {request.method}")
    current_app.logger.info(f"Datos del catálogo: {catalog}")
    
    # Verificar que la solicitud sea POST para evitar eliminaciones accidentales por enlaces directos
    if request.method != "POST":
        flash("Método no permitido para eliminar catálogos. Use el formulario de confirmación.", "warning")
        return redirect(url_for("catalogs.view", catalog_id=catalog_id))
    
    try:
        # Guardar información del catálogo antes de eliminarlo para mostrar mensaje personalizado
        catalog_name = catalog.get('name', 'Sin nombre')
        owner = catalog.get('owner', session.get('username', 'usuario'))
        collection_source = catalog.get('collection_source', 'catalogs')
        
        current_app.logger.info(f"Eliminando catálogo de la colección: {collection_source}")
        
        # Intentar eliminar de la colección correcta
        if collection_source == 'spreadsheets':
            # Si el catálogo está en la colección spreadsheets
            result = mongo.db.spreadsheets.delete_one({"_id": ObjectId(catalog_id)})
        else:
            # Por defecto, intentar eliminar de la colección catalogs
            result = mongo.db.catalogs.delete_one({"_id": ObjectId(catalog_id)})
        
        current_app.logger.info(f"Resultado de eliminación de {collection_source}: {result.deleted_count} documento(s) eliminado(s)")
        
        if result.deleted_count > 0:
            current_app.logger.info(f"Catálogo '{catalog_name}' (ID: {catalog_id}) eliminado por {session.get('username')}")
            flash(f"Catálogo '{catalog_name}' eliminado correctamente", "success")
            
            # Registrar la acción en el log de auditoría si existe
            try:
                from app.audit import audit_log
                audit_log(f"Eliminación de catálogo", f"Catálogo '{catalog_name}' (ID: {catalog_id}) eliminado", session.get('username'))
            except ImportError:
                pass  # Si no existe el módulo de auditoría, continuar sin error
        else:
            # Si no se eliminó nada, intentar en la otra colección
            if collection_source == 'catalogs':
                result = mongo.db.spreadsheets.delete_one({"_id": ObjectId(catalog_id)})
            else:
                result = mongo.db.catalogs.delete_one({"_id": ObjectId(catalog_id)})
                
            current_app.logger.info(f"Segundo intento de eliminación: {result.deleted_count} documento(s) eliminado(s)")
            
            if result.deleted_count > 0:
                flash(f"Catálogo '{catalog_name}' eliminado correctamente", "success")
            else:
                flash("No se pudo eliminar el catálogo. Es posible que ya haya sido eliminado.", "warning")
    except Exception as e:
        current_app.logger.error(f"Error al eliminar catálogo {catalog_id}: {str(e)}", exc_info=True)
        flash(f"Error al eliminar catálogo: {str(e)}", "danger")
    
    # Forzar una redirección a la lista de catálogos para asegurar que se actualice la vista
    return redirect(url_for("catalogs.list"))

@catalogs_bp.route("/create", methods=["GET", "POST"])
def create():
    if 'username' not in session:
        flash('Debe iniciar sesión para crear catálogos', 'warning')
        return redirect(url_for('auth.login'))
        
    if request.method == "POST":
        try:
            # Obtener datos del formulario
            catalog_name = request.form.get('name', '').strip()  # Cambiado de 'catalog_name' a 'name' para coincidir con el formulario
            headers_str = request.form.get('headers', '').strip()
            
            if not catalog_name:
                flash('El nombre del catálogo es obligatorio', 'danger')
                return redirect(request.url)
                
            # Procesar los encabezados
            headers = [h.strip() for h in headers_str.split(',')] if headers_str else []
            if not headers:
                flash('Debe especificar al menos un encabezado', 'danger')
                return redirect(request.url)
            
            # Obtener información del usuario actual
            username = session.get('username')
            email = session.get('email')
            nombre = session.get('nombre', username)  # Usar nombre si está disponible, sino username
            
            current_app.logger.info(f"Creando catálogo con usuario: {username}, email: {email}, nombre: {nombre}")
                
            # Crear el catálogo en la base de datos
            catalog = {
                'name': catalog_name,
                'headers': headers,
                'rows': [],
                'created_by': username,
                'owner': username,  # Campo adicional para compatibilidad
                'owner_name': nombre,  # Guardar el nombre real del usuario
                'email': email,  # Guardar el email para referencias
                'created_at': datetime.datetime.utcnow(),
                'updated_at': datetime.datetime.utcnow()
            }
            
            result = mongo.db.catalogs.insert_one(catalog)
            catalog_id = str(result.inserted_id)
            
            current_app.logger.info(f"Catálogo creado con ID: {catalog_id}, nombre: {catalog_name}, creado por: {nombre}")
            flash(f'Catálogo "{catalog_name}" creado correctamente', 'success')
            
            # Actualizar el catálogo con el ID como string para facilitar su uso en plantillas
            mongo.db.catalogs.update_one({"_id": result.inserted_id}, {"$set": {"_id_str": catalog_id}})
            
            # Redirigir a una página de confirmación en lugar de directamente a la vista
            return render_template('catalogo_creado.html', 
                                  catalog={
                                      "_id": catalog_id,
                                      "name": catalog_name,
                                      "headers": headers,
                                      "created_by": username,
                                      "owner_name": nombre,
                                      "created_at": datetime.datetime.utcnow().strftime('%d/%m/%Y %H:%M')
                                  })
            
        except Exception as e:
            current_app.logger.error(f"Error al crear catálogo: {str(e)}", exc_info=True)
            flash(f"Error al crear el catálogo: {str(e)}", "danger")
            return redirect(request.url)
    
    # Para peticiones GET, mostrar el formulario de creación
    return render_template('catalogs/create.html')

@catalogs_bp.route("/import", methods=["GET", "POST"])
def import_catalog():
    if 'username' not in session:
        flash('Debe iniciar sesión para importar catálogos', 'warning')
        return redirect(url_for('auth.login'))
        
    if request.method == "POST":
        # Verificar si se ha enviado un archivo
        if 'file' not in request.files:
            flash('No se ha seleccionado ningún archivo', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No se ha seleccionado ningún archivo', 'danger')
            return redirect(request.url)
            
        # Verificar el formato del archivo
        if not file.filename.endswith(('.csv', '.xls', '.xlsx')):
            flash('Formato de archivo no soportado. Use CSV o Excel.', 'danger')
            return redirect(request.url)
            
        try:
            # Obtener datos del formulario
            catalog_name = request.form.get('catalog_name', '').strip()
            
            # Si no se proporciona un nombre, usar el nombre del archivo sin extensión
            if not catalog_name:
                # Extraer el nombre del archivo sin extensión
                catalog_name = os.path.splitext(file.filename)[0]
                current_app.logger.info(f"Usando el nombre del archivo como nombre del catálogo: {catalog_name}")
            
            # Obtener información del usuario actual
            username = session.get('username')
            email = session.get('email')
            nombre = session.get('nombre', username)  # Usar nombre si está disponible, sino username
            
            current_app.logger.info(f"Importando catálogo con usuario: {username}, email: {email}, nombre: {nombre}")
                
            # Procesar el archivo según su formato
            if file.filename.endswith('.csv'):
                # Procesar CSV
                df = pd.read_csv(file, encoding='utf-8')
            else:
                # Procesar Excel
                df = pd.read_excel(file)
                
            # Verificar que el archivo tiene datos
            if df.empty:
                flash('El archivo está vacío', 'danger')
                return redirect(request.url)
                
            # Convertir DataFrame a lista de diccionarios
            headers = df.columns.tolist()
            rows = df.to_dict('records')
            
            # Crear el catálogo en la base de datos
            catalog = {
                'name': catalog_name,
                'headers': headers,
                'rows': rows,
                'created_by': username,
                'owner': username,  # Campo adicional para compatibilidad
                'owner_name': nombre,  # Guardar el nombre real del usuario
                'email': email,  # Guardar el email para referencias
                'created_at': datetime.datetime.utcnow(),
                'updated_at': datetime.datetime.utcnow()
            }
            
            result = mongo.db.catalogs.insert_one(catalog)
            catalog_id = str(result.inserted_id)
            
            current_app.logger.info(f"Catálogo importado con ID: {catalog_id}, nombre: {catalog_name}, creado por: {nombre}")
            flash(f'Catálogo "{catalog_name}" importado correctamente', 'success')
            return redirect(url_for('catalogs.view', catalog_id=catalog_id))
            
        except Exception as e:
            current_app.logger.error(f"Error al importar catálogo: {str(e)}", exc_info=True)
            flash(f"Error al importar el catálogo: {str(e)}", "danger")
            return redirect(request.url)
    
    # Para peticiones GET, mostrar el formulario de importación
    return render_template('importar_catalogo.html')
