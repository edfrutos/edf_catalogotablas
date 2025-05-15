# app/routes/main_routes.py

from flask import Blueprint, render_template, redirect, url_for, session, flash, current_app, request
from app.decorators import login_required
from bson.objectid import ObjectId
from bson.errors import InvalidId
import logging
from werkzeug.routing import BuildError
import os
import sys
from app.utils.image_utils import get_image_url
from werkzeug.utils import secure_filename
import secrets
from datetime import datetime
import openpyxl
from openpyxl import Workbook
import csv
from app.utils.spreadsheet_utils import get_spreadsheet_collection
from app.utils.user_utils import get_user_by_username, get_user_by_email
import re
import uuid

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    # Redirigir a welcome si no está logueado
    if 'user_id' not in session:
        return redirect(url_for('main.welcome'))
    return redirect(url_for('main.dashboard'))

@main_bp.route('/welcome')
def welcome():
    return render_template('welcome.html')

@main_bp.route('/dashboard')
# # @login_required
def dashboard():
    try:
        role = session.get('role', 'user')
        
        if role == 'admin':
            # Verificar si existe el endpoint admin.dashboard_admin
            try:
                return redirect(url_for('admin.dashboard_admin'))
            except BuildError:
                logger.warning("Endpoint admin.dashboard_admin no encontrado, redirigiendo a dashboard_user")
                return redirect(url_for('main.dashboard_user'))
        elif role == 'user':
            return redirect(url_for('main.dashboard_user'))
        else:
            flash('Rol desconocido. Contacte con el administrador.', 'error')
            return redirect(url_for('main.welcome'))
    except Exception as e:
        logger.error(f"Error en dashboard: {str(e)}", exc_info=True)
        flash("Error al cargar el dashboard. Por favor intente nuevamente.", "error")
        # Asegurarse de que siempre devuelva una respuesta válida
        return render_template('welcome.html')

@main_bp.route('/dashboard_user')
def dashboard_user():
    # Permitir acceso sin verificación de sesión, pero mostrar solo tablas del usuario
    spreadsheets_collection = getattr(current_app, 'spreadsheets_collection', None)
    if spreadsheets_collection is None and hasattr(current_app, 'db'):
        spreadsheets_collection = current_app.db['spreadsheets']
    if spreadsheets_collection is None:
        flash('No se pudo acceder a las tablas del usuario. Contacte con el administrador.', 'error')
        return redirect(url_for('main.dashboard'))
        
    # Obtener el nombre de usuario de la sesión o usar un valor predeterminado
    owner = session.get('username') or session.get('email') or 'usuario_normal'
    role = session.get('role', 'user')
    
    # Los administradores ven todas las tablas, los usuarios normales solo las suyas
    if role == 'admin':
        tablas = list(spreadsheets_collection.find().sort('created_at', -1))
        logger.info(f"[ADMIN] Mostrando todas las tablas para el administrador {owner}")
    else:
        tablas = list(spreadsheets_collection.find({"owner": owner}).sort('created_at', -1))
        logger.info(f"[USER] Mostrando solo las tablas del usuario {owner}")
    
    # Obtener catálogos del usuario
    try:
        from app.extensions import mongo
        if role == 'admin':
            catalogs = list(mongo.db.catalogs.find())
            logger.info(f"[ADMIN] Mostrando todos los catálogos para el administrador {owner}")
        else:
            catalogs = list(mongo.db.catalogs.find({"created_by": owner}))
            logger.info(f"[USER] Mostrando solo los catálogos del usuario {owner}")
        
        # Agregar _id_str a cada catálogo para facilitar su uso en las plantillas
        for catalog in catalogs:
            catalog['_id_str'] = str(catalog['_id'])
    except Exception as e:
        logger.error(f"Error al obtener catálogos: {str(e)}")
        catalogs = []
        flash('No se pudieron cargar los catálogos. Contacte con el administrador.', 'warning')
        
    return render_template('dashboard_unificado.html', tablas=tablas, catalogs=catalogs)

@main_bp.route("/editar/<id>", methods=["GET", "POST"])
def editar(id):
    # Eliminar verificaciones de sesión y permisos
    # if "username" not in session:
    #     return redirect(url_for("auth.login"))
    if "selected_table" not in session:
        # Si no hay tabla seleccionada, usar el ID proporcionado para buscar la tabla
        try:
            table_info = current_app.spreadsheets_collection.find_one({"_id": ObjectId(id)})
            if table_info:
                selected_table = table_info.get("filename")
                session["selected_table"] = selected_table
            else:
                flash("Tabla no encontrada.", "error")
                return redirect(url_for("main.tables"))
        except Exception as e:
            logger.error(f"Error al buscar tabla por ID: {str(e)}")
            flash("Error al buscar la tabla.", "error")
            return redirect(url_for("main.tables"))
    else:
        selected_table = session["selected_table"]
        table_info = current_app.spreadsheets_collection.find_one({"filename": selected_table})
        if not table_info:
            flash("Tabla no encontrada.", "error")
            return redirect(url_for("main.tables"))
    # Control de acceso: solo admin o dueño puede editar
    if session.get("role") != "admin" and table_info.get("owner") != session.get("username"):
        flash("No tiene permisos para editar esta tabla", "error")
        return redirect(url_for("main.tables"))

    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre", "").strip()
        nuevos_headers = [h.strip() for h in request.form.get("headers", "").split(",") if h.strip()]
        update = {}
        if nuevo_nombre:
            update["name"] = nuevo_nombre
        if nuevos_headers:
            update["headers"] = nuevos_headers
        if update:
            current_app.spreadsheets_collection.update_one(
                {"filename": selected_table},
                {"$set": update}
            )
            flash("Tabla actualizada correctamente.", "success")
        else:
            flash("No se detectaron cambios.", "info")
        return redirect(url_for("main.ver_tabla", table_id=id))

    # GET: mostrar formulario de edición
    return render_template(
        "editar_tabla.html",
        table=table_info
    )

@main_bp.route('/ver_tabla/<table_id>')
# # @login_required
def ver_tabla(table_id):
    try:
        table = current_app.spreadsheets_collection.find_one({'_id': ObjectId(table_id)})
        current_app.logger.info(f"[DEBUG][VISIONADO] Tabla encontrada: {table}")
        if not table:
            flash('Tabla no encontrada.', 'error')
            return redirect(url_for('main.dashboard_user'))
        
        # Log de sesión y permisos
        current_app.logger.info(f"[DEBUG][VISIONADO] Sesión: {dict(session)}")
        current_app.logger.info(f"[DEBUG][VISIONADO] table.owner: {table.get('owner')}, session.username: {session.get('username')}, session.role: {session.get('role')}")
        
        # Verificar permisos: solo el propietario o admin puede ver la tabla
        if session.get('role') != 'admin' and table.get('owner') != session.get('username'):
            mensaje = (
                f"No tiene permisos para ver esta tabla. "
                f"(owner={table.get('owner')}, username={session.get('username')}, role={session.get('role')})"
            )
            flash(mensaje, "error")
            return redirect(url_for('main.dashboard_user'))
        
        # Si llegamos aquí, el usuario tiene permisos para ver la tabla
        # Obtener las URLs de las imágenes
        from app.utils.image_utils import get_image_url
        
        # Procesar las imágenes en cada fila
        for row in table.get('data', []):
            if 'imagenes' in row and row['imagenes']:
                # Crear un diccionario con las URLs de las imágenes
                row['imagen_urls'] = [get_image_url(img) for img in row['imagenes']]
        
        return render_template('ver_tabla.html', table=table)
    except BuildError as e:
        logger.error(f"BuildError en ver_tabla: {str(e)}", exc_info=True)
        flash("Error interno: ruta no encontrada o mal configurada.", "danger")
        return render_template("error.html", error="Error interno: ruta no encontrada o mal configurada.")
        return redirect(url_for('main.dashboard_user'))
    except Exception as e:
        logger.error(f"Error inesperado en ver_tabla: {str(e)}", exc_info=True)
        flash("Error interno inesperado.", "danger")
        return redirect(url_for('main.dashboard_user'))

@main_bp.route('/select_table/<table_id>')
def select_table(table_id):
    if not (session.get('username') or session.get('email')):
        return redirect(url_for("auth.login"))
    table = current_app.spreadsheets_collection.find_one({"_id": ObjectId(table_id)})
    if not table:
        flash("Tabla no encontrada.", "error")
        return redirect(url_for("tables"))
    session["selected_table"] = table["filename"]
    session["selected_table_id"] = str(table["_id"])
    session["selected_table_name"] = table.get("name", "Sin nombre")
    return redirect(url_for("main.ver_tabla", table_id=table_id))

@main_bp.route('/perfil')
def perfil():
    # Verificar si el usuario está autenticado
    if 'user_id' not in session:
        flash('Debe iniciar sesión para ver su perfil', 'warning')
        return redirect(url_for('auth.login'))
    
    try:
        # Obtener la colección de usuarios
        users_collection = getattr(current_app, 'users_collection', None)
        if users_collection is None:
            # Importar mongo desde app.extensions
            from app.extensions import mongo
            users_collection = mongo.db.users
        
        # Obtener datos del usuario actual
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        if not user:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('main.dashboard_user'))
            
        # Asegurar que existe la imagen de perfil predeterminada
        default_profile_path = os.path.join(current_app.root_path, 'static', 'default_profile.png')
        if not os.path.exists(default_profile_path):
            try:
                # Importar la función para crear la imagen predeterminada
                sys.path.append(os.path.dirname(os.path.dirname(current_app.root_path)))
                from crear_imagen_perfil_default import crear_imagen_perfil_default
                crear_imagen_perfil_default()
                logger.info("Imagen de perfil predeterminada creada correctamente")
            except Exception as e:
                logger.error(f"Error al crear imagen predeterminada: {str(e)}", exc_info=True)
        
        return render_template('perfil.html', user=user)
    except Exception as e:
        logger.error(f"Error al cargar perfil: {str(e)}", exc_info=True)
        flash('Error al cargar los datos del perfil', 'error')
        return redirect(url_for('main.dashboard_user'))

@main_bp.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'user_id' not in session:
        flash('Debe iniciar sesión para editar su perfil', 'warning')
        return redirect(url_for('auth.login'))
        
    # Obtener la colección de usuarios
    users_collection = getattr(current_app, 'users_collection', None)
    if users_collection is None:
        # Importar mongo desde app.extensions
        from app.extensions import mongo
        users_collection = mongo.db.users
    
    # Obtener datos del usuario actual
    try:
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        if not user:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('main.dashboard_user'))
    except Exception as e:
        logger.error(f"Error al obtener datos del usuario: {str(e)}", exc_info=True)
        flash('Error al cargar los datos del usuario', 'error')
        return redirect(url_for('main.dashboard_user'))
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        
        # Datos para cambio de contraseña
        password_actual = request.form.get('password_actual')
        password_nuevo = request.form.get('password_nuevo')
        password_confirmacion = request.form.get('password_confirmacion')
        
        # Actualizar en la base de datos
        update_data = {}
        if nombre:
            update_data['nombre'] = nombre
        if email:
            update_data['email'] = email
            
        # Procesar cambio de contraseña si se proporcionaron los campos necesarios
        if password_actual and password_nuevo and password_confirmacion:
            # Verificar que la contraseña actual sea correcta
            from werkzeug.security import check_password_hash, generate_password_hash
            
            if not check_password_hash(user.get('password', ''), password_actual):
                flash('La contraseña actual es incorrecta.', 'error')
                return render_template('editar_perfil.html', user=user)
            
            # Verificar que las nuevas contraseñas coincidan
            if password_nuevo != password_confirmacion:
                flash('Las nuevas contraseñas no coinciden.', 'error')
                return render_template('editar_perfil.html', user=user)
            
            # Verificar que la nueva contraseña tenga al menos 8 caracteres
            if len(password_nuevo) < 8:
                flash('La nueva contraseña debe tener al menos 8 caracteres.', 'error')
                return render_template('editar_perfil.html', user=user)
            
            # Actualizar la contraseña
            update_data['password'] = generate_password_hash(password_nuevo)
        
        # Asegurarse de que existe la carpeta de uploads
        uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        imagenes_subidas_folder = os.path.join(current_app.root_path, 'static', 'imagenes_subidas')
        
        # Crear las carpetas si no existen
        os.makedirs(uploads_folder, exist_ok=True)
        os.makedirs(imagenes_subidas_folder, exist_ok=True)
        
        # Asegurar que existe la imagen de perfil predeterminada
        default_profile_path = os.path.join(current_app.root_path, 'static', 'default_profile.png')
        if not os.path.exists(default_profile_path):
            try:
                # Importar la función para crear la imagen predeterminada
                sys.path.append(os.path.dirname(os.path.dirname(current_app.root_path)))
                from crear_imagen_perfil_default import crear_imagen_perfil_default
                crear_imagen_perfil_default()
                logger.info("Imagen de perfil predeterminada creada correctamente")
            except Exception as e:
                logger.error(f"Error al crear imagen predeterminada: {str(e)}", exc_info=True)
        
        # Procesar la imagen de perfil si se ha subido una nueva
        if 'foto' in request.files:
            profile_image = request.files['foto']
            if profile_image and profile_image.filename != '':
                try:
                    # Guardar la imagen
                    filename = secure_filename(f"{uuid.uuid4().hex}_{profile_image.filename}")
                    filepath = os.path.join(imagenes_subidas_folder, filename)
                    profile_image.save(filepath)
                    
                    # Actualizar el campo foto_perfil en el usuario
                    update_data["foto_perfil"] = filename
                    logger.info(f"Imagen de perfil guardada: {filename}")
                except Exception as e:
                    logger.error(f"Error al guardar imagen de perfil: {str(e)}", exc_info=True)
                    flash(f"Error al guardar la imagen de perfil: {str(e)}", "error")
        
        # Actualizar el usuario en la base de datos
        from app.extensions import mongo
        mongo.db.users.update_one({'_id': ObjectId(session['user_id'])}, {'$set': update_data})
        
        # Mostrar mensaje específico si se cambió la contraseña
        if 'password' in update_data:
            flash('Perfil y contraseña actualizados correctamente.', 'success')
            # Actualizar la sesión para reflejar los cambios
            if 'email' in update_data:
                session['email'] = update_data['email']
            if 'nombre' in update_data and update_data['nombre']:
                session['username'] = update_data['nombre']
            # Redirigir al login para que el usuario inicie sesión con la nueva contraseña
            session.clear()
            flash('Por favor, inicie sesión con su nueva contraseña.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Perfil actualizado correctamente.', 'success')
            # Actualizar la sesión para reflejar los cambios
            if 'email' in update_data:
                session['email'] = update_data['email']
            if 'nombre' in update_data and update_data['nombre']:
                session['username'] = update_data['nombre']
            return redirect(url_for('main.perfil'))
    
    # Para peticiones GET, mostrar el formulario con los datos actuales
    return render_template('editar_perfil.html', user=user)

@main_bp.route('/editar_fila/<tabla_id>/<int:fila_index>', methods=['GET', 'POST'])
# # @login_required
def editar_fila(tabla_id, fila_index):
    current_app.logger.info(f"[DEBUG] Valores recibidos: tabla_id={tabla_id}, fila_index={fila_index}")
    # Obtener info de la tabla
    table_info = current_app.spreadsheets_collection.find_one({'_id': ObjectId(tabla_id)})
    if not table_info:
        flash('Tabla no encontrada.', 'error')
        return redirect(url_for('main.tables'))
    
    # Verificar permisos: solo el propietario o admin puede editar filas
    if session.get('role') != 'admin' and table_info.get('owner') != session.get('username'):
        flash('No tienes permisos para editar esta fila.', 'error')
        return redirect(url_for('main.ver_tabla', table_id=tabla_id))
    
    # Obtener la fila específica del array de datos
    if not table_info.get('data') or fila_index >= len(table_info.get('data', [])):
        flash('Fila no encontrada.', 'error')
        return redirect(url_for('main.ver_tabla', table_id=tabla_id))
    
    fila = table_info['data'][fila_index]
    headers = table_info.get('headers', [])
    
    if request.method == 'POST':
        update_data = {}
        for header in headers:
            if header != 'Número' and header != 'Imagenes':
                update_data[f"data.{fila_index}.{header}"] = request.form.get(header, '').strip()
        
        # Procesar imágenes a eliminar
        imagenes_a_eliminar = request.form.get('imagenes_a_eliminar', '')
        if imagenes_a_eliminar:
            try:
                import json
                imagenes_a_eliminar = json.loads(imagenes_a_eliminar)
                if isinstance(imagenes_a_eliminar, list) and 'imagenes' in fila:
                    # Eliminar las imágenes del servidor y de S3
                    ruta_uploads = os.path.join(current_app.static_folder, 'uploads')
                    use_s3 = os.environ.get('USE_S3', 'false').lower() == 'true'
                    
                    for img_a_eliminar in imagenes_a_eliminar:
                        try:
                            # Eliminar de S3 si está habilitado
                            if use_s3:
                                from app.utils.s3_utils import delete_file_from_s3
                                delete_file_from_s3(img_a_eliminar)
                                logger.info(f"Imagen eliminada de S3: {img_a_eliminar}")
                            
                            # Eliminar del servidor local
                            ruta_img = os.path.join(ruta_uploads, img_a_eliminar)
                            if os.path.exists(ruta_img):
                                os.remove(ruta_img)
                                logger.info(f"Imagen eliminada del servidor local: {img_a_eliminar}")
                        except Exception as e:
                            logger.error(f"Error al eliminar imagen: {str(e)}", exc_info=True)
                    
                    # Actualizar la lista de imágenes en la fila
                    imagenes_actualizadas = [img for img in fila.get('imagenes', []) if img not in imagenes_a_eliminar]
                    update_data[f"data.{fila_index}.imagenes"] = imagenes_actualizadas
            except Exception as e:
                logger.error(f"Error al procesar imágenes a eliminar: {str(e)}")
        
        # Procesar nuevas imágenes si existen
        nuevas_imagenes = []
        if 'imagenes' in request.files:
            archivos = request.files.getlist('imagenes')
            # Limitar a máximo 3 imágenes
            archivos = archivos[:3] if len(archivos) > 3 else archivos
            
            for archivo in archivos:
                if archivo and archivo.filename.strip():
                    # Generar nombre seguro y único para el archivo
                    nombre_seguro = secure_filename(archivo.filename)
                    extension = os.path.splitext(nombre_seguro)[1].lower()
                    nombre_unico = f"{uuid.uuid4().hex}{extension}"
                    
                    # Verificar que sea una imagen válida
                    if extension.lower() not in ['.jpg', '.jpeg', '.png', '.gif']:
                        continue
                    
                    # Guardar la imagen en la carpeta de uploads
                    ruta_uploads = os.path.join(current_app.static_folder, 'uploads')
                    if not os.path.exists(ruta_uploads):
                        os.makedirs(ruta_uploads)
                    
                    ruta_completa = os.path.join(ruta_uploads, nombre_unico)
                    archivo.save(ruta_completa)
                    
                    # Subir a S3 si está habilitado
                    use_s3 = os.environ.get('USE_S3', 'false').lower() == 'true'
                    if use_s3:
                        try:
                            from app.utils.s3_utils import upload_file_to_s3
                            result = upload_file_to_s3(ruta_completa, nombre_unico)
                            if result['success']:
                                logger.info(f"Imagen subida a S3: {result['url']}")
                                # Eliminar el archivo local después de subirlo a S3
                                os.remove(ruta_completa)
                                logger.info(f"Imagen eliminada del servidor local después de subirla a S3: {nombre_unico}")
                            else:
                                logger.error(f"Error al subir imagen a S3: {result.get('error')}")
                        except Exception as e:
                            logger.error(f"Error al procesar subida a S3: {str(e)}", exc_info=True)
                    
                    nuevas_imagenes.append(nombre_unico)
        
        # Si hay nuevas imágenes, reemplazar las existentes
        if nuevas_imagenes:
            # Si ya se actualizaron las imágenes por eliminación, agregar las nuevas a las restantes
            if f"data.{fila_index}.imagenes" in update_data:
                update_data[f"data.{fila_index}.imagenes"] = update_data[f"data.{fila_index}.imagenes"] + nuevas_imagenes
            else:
                # Reemplazar todas las imágenes con las nuevas
                update_data[f"data.{fila_index}.imagenes"] = nuevas_imagenes
                
                # Eliminar imágenes antiguas del servidor si existen
                if 'imagenes' in fila and fila['imagenes']:
                    ruta_uploads = os.path.join(current_app.static_folder, 'uploads')
                    for img_antigua in fila['imagenes']:
                        try:
                            ruta_img = os.path.join(ruta_uploads, img_antigua)
                            if os.path.exists(ruta_img):
                                os.remove(ruta_img)
                        except Exception as e:
                            logger.error(f"Error al eliminar imagen antigua: {str(e)}")
        
        # Actualizar la fila en la base de datos
        current_app.spreadsheets_collection.update_one(
            {'_id': ObjectId(tabla_id)},
            {'$set': update_data}
        )
        
        flash('Fila actualizada correctamente.', 'success')
        return redirect(url_for('main.ver_tabla', table_id=tabla_id))
    
    return render_template('editar_fila.html', fila=fila, headers=headers, catalog=table_info, tabla_id=tabla_id, fila_index=fila_index)

@main_bp.route("/agregar_fila/<tabla_id>", methods=["GET", "POST"])
def agregar_fila(tabla_id):
    # Verificar sesión
    if "username" not in session:
        flash("Debe iniciar sesión para agregar filas", "warning")
        return redirect(url_for("auth.login"))
    
    try:
        # Obtener la tabla
        tabla = current_app.spreadsheets_collection.find_one({"_id": ObjectId(tabla_id)})
        if not tabla:
            flash("Tabla no encontrada", "error")
            return redirect(url_for("main.dashboard_user"))
        
        # Verificar permisos: solo el propietario o admin puede agregar filas
        if session.get("role") != "admin" and session.get("username") != tabla.get("owner"):
            flash("No tiene permisos para agregar filas a esta tabla", "error")
            return redirect(url_for("main.dashboard_user"))
        
        if request.method == "POST":
            # Obtener datos del formulario
            nueva_fila = {}
            for header in tabla.get("headers", []):
                nueva_fila[header] = request.form.get(header, "")
            
            # Procesar imágenes si existen
            imagenes = []
            if 'imagenes' in request.files:
                archivos = request.files.getlist('imagenes')
                # Limitar a máximo 3 imágenes
                archivos = archivos[:3] if len(archivos) > 3 else archivos
                
                for archivo in archivos:
                    if archivo and archivo.filename.strip():
                        # Generar nombre seguro y único para el archivo
                        nombre_seguro = secure_filename(archivo.filename)
                        extension = os.path.splitext(nombre_seguro)[1].lower()
                        nombre_unico = f"{uuid.uuid4().hex}{extension}"
                        
                        # Verificar que sea una imagen válida
                        if extension.lower() not in ['.jpg', '.jpeg', '.png', '.gif']:
                            continue
                        
                        # Guardar la imagen en la carpeta de uploads
                        ruta_uploads = os.path.join(current_app.static_folder, 'uploads')
                        if not os.path.exists(ruta_uploads):
                            os.makedirs(ruta_uploads)
                        
                        ruta_completa = os.path.join(ruta_uploads, nombre_unico)
                        archivo.save(ruta_completa)
                        
                        # Subir a S3 si está habilitado
                        use_s3 = os.environ.get('USE_S3', 'false').lower() == 'true'
                        if use_s3:
                            try:
                                from app.utils.s3_utils import upload_file_to_s3
                                result = upload_file_to_s3(ruta_completa, nombre_unico)
                                if result['success']:
                                    logger.info(f"Imagen subida a S3: {result['url']}")
                                    # Eliminar el archivo local después de subirlo a S3
                                    os.remove(ruta_completa)
                                    logger.info(f"Imagen eliminada del servidor local después de subirla a S3: {nombre_unico}")
                                else:
                                    logger.error(f"Error al subir imagen a S3: {result.get('error')}")
                            except Exception as e:
                                logger.error(f"Error al procesar subida a S3: {str(e)}", exc_info=True)
                        
                        imagenes.append(nombre_unico)
            
            # Agregar las imágenes a la fila
            if imagenes:
                nueva_fila['imagenes'] = imagenes
            
            # Agregar la fila a la tabla
            current_app.spreadsheets_collection.update_one(
                {"_id": ObjectId(tabla_id)},
                {"$push": {"data": nueva_fila}, "$inc": {"num_rows": 1}}
            )
            
            flash("Fila agregada correctamente", "success")
            return redirect(url_for("main.ver_tabla", table_id=tabla_id))
        
        # Para peticiones GET, mostrar el formulario
        return render_template("agregar_fila_tabla.html", tabla=tabla)
    except Exception as e:
        logger.error(f"Error al agregar fila: {str(e)}", exc_info=True)
        flash(f"Error al agregar fila: {str(e)}", "error")
        return redirect(url_for("main.dashboard_user"))

@main_bp.route("/tables", methods=["GET", "POST"])
# # @login_required
def tables():
    # Eliminar verificación de sesión para permitir acceso sin restricciones
    # if "username" not in session:
    #     flash("Debe iniciar sesión para acceder a las tablas", "warning")
    #     return redirect(url_for("auth.login"))
        
    owner = "usuario_predeterminado"
    
    # Verificar que la colección de spreadsheets esté disponible
    if not hasattr(current_app, 'spreadsheets_collection'):
        logger.error("Error: No se encontró la colección spreadsheets_collection en current_app")
        flash("Error de conexión a la base de datos. Por favor, contacte al administrador.", "danger")
        return render_template("error.html", error="Error de conexión a la base de datos")
    
    # Método GET: Mostrar tablas existentes
    if request.method == "GET":
        try:
            # Los administradores ven todas las tablas, los usuarios normales solo las suyas
            role = session.get("role", "user")
            if role == "admin":
                todas_las_tablas = list(current_app.spreadsheets_collection.find())
                logger.info(f"[ADMIN] Mostrando todas las tablas para el administrador {owner}")
            else:
                todas_las_tablas = list(current_app.spreadsheets_collection.find({"owner": owner}))
                logger.info(f"[USER] Mostrando solo las tablas del usuario {owner}")
            
            current_app.logger.info(f"[VISIONADO] Tablas encontradas para {owner}: {todas_las_tablas}")
            return render_template("tables.html", tables=todas_las_tablas)
        except Exception as e:
            logger.error(f"Error al listar tablas: {str(e)}", exc_info=True)
            flash("Error al obtener las tablas. Por favor, inténtelo de nuevo.", "danger")
            return render_template("error.html", error="Error al obtener las tablas")
    
    # Método POST: Crear nueva tabla
    try:
        table_name = request.form.get("table_name", "").strip()
        import_file = request.files.get("import_table")
        
        # Validar nombre de tabla
        if not table_name:
            flash("El nombre de la tabla es obligatorio.", "error")
            return redirect(url_for("main.tables"))

        # Comprobar duplicados para el mismo usuario
        if current_app.spreadsheets_collection.find_one({"owner": owner, "name": table_name}):
            flash("Ya existe una tabla con ese nombre.", "error")
            return redirect(url_for("main.tables"))
            
        # Procesar archivo importado o crear tabla nueva
        if import_file and import_file.filename:
            try:
                ext = os.path.splitext(import_file.filename)[1].lower()
                unique_id = uuid.uuid4().hex
                filename = f"table_{unique_id}{ext}"
                
                # Asegurarse de que existe la carpeta de uploads
                if "UPLOAD_FOLDER" not in current_app.config:
                    flash("Error en la configuración del servidor. Contacte al administrador.", "danger")
                    return redirect(url_for("main.tables"))
                    
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                import_file.save(filepath)
                
                # Procesar archivo según su tipo
                headers = None
                rows = []
                
                if ext in [".xlsx", ".xlsm", ".xltx", ".xltm"]:
                    try:
                        wb = openpyxl.load_workbook(filepath)
                        hoja = wb.active
                        headers = list(next(hoja.iter_rows(min_row=1, max_row=1, values_only=True)))
                        for row in hoja.iter_rows(min_row=2, values_only=True):
                            if any(row):
                                rows.append({h: (row[i] if i < len(row) else '') for i, h in enumerate(headers)})
                        wb.close()
                    except Exception as e:
                        flash(f"Error al leer el archivo Excel: {str(e)}", "error")
                        return redirect(url_for("main.tables"))
                elif ext == ".csv":
                    try:
                        with open(filepath, newline='', encoding='utf-8') as csvfile:
                            reader = csv.reader(csvfile)
                            headers = list(next(reader, None))
                            for row in reader:
                                if any(row):
                                    rows.append({h: (row[i] if i < len(row) else '') for i, h in enumerate(headers)})
                    except Exception as e:
                        flash(f"Error al leer el archivo CSV: {str(e)}", "error")
                        return redirect(url_for("main.tables"))
                else:
                    flash("Formato de archivo no soportado. Solo se permiten archivos .xlsx, .xlsm, .xltx, .xltm o .csv", "error")
                    return redirect(url_for("main.tables"))
                
                if not headers or not any(headers):
                    flash("El archivo importado no contiene encabezados válidos.", "error")
                    return redirect(url_for("main.tables"))
                
                # Insertar la tabla en la base de datos
                result = current_app.spreadsheets_collection.insert_one({
                    "owner": owner,
                    "name": table_name,
                    "filename": filename,
                    "headers": headers,
                    "created_at": datetime.utcnow(),
                    "created_by": session["username"],
                    "data": rows,
                    "num_rows": len(rows)
                })
                
                session["selected_headers"] = headers
                return redirect(url_for("main.ver_tabla", table_id=str(result.inserted_id)))
                
            except Exception as e:
                logger.error(f"Error al procesar archivo: {str(e)}", exc_info=True)
                flash(f"Error al procesar el archivo: {str(e)}", "error")
                return redirect(url_for("main.tables"))
        else:
            # Crear tabla nueva desde encabezados ingresados manualmente
            headers_str = request.form.get("table_headers", "").strip()
            headers = [h.strip() for h in headers_str.split(",") if h.strip()] if headers_str else ["Número", "Descripción", "Peso", "Valor"]
            
            if not headers or not any(headers):
                flash("Debes ingresar al menos un encabezado.", "error")
                return redirect(url_for("main.tables"))
            
            try:
                file_id = secrets.token_hex(8)
                filename = f"table_{file_id}.xlsx"
                
                # Asegurarse de que existe la carpeta de uploads
                if "UPLOAD_FOLDER" not in current_app.config:
                    flash("Error en la configuración del servidor. Contacte al administrador.", "danger")
                    return redirect(url_for("main.tables"))
                    
                filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                
                wb = Workbook()
                hoja = wb.active
                hoja.append(headers)
                wb.save(filepath)
                wb.close()
                
                result = current_app.spreadsheets_collection.insert_one({
                    "owner": owner,
                    "name": table_name,
                    "filename": filename,
                    "headers": headers,
                    "created_at": datetime.utcnow(),
                    "created_by": session["username"],
                    "data": [],
                    "num_rows": 0
                })
                
                session["selected_headers"] = headers
                return redirect(url_for("main.ver_tabla", table_id=str(result.inserted_id)))
            except Exception as e:
                logger.error(f"Error al crear tabla manual: {str(e)}", exc_info=True)
                flash(f"Error al crear la tabla: {str(e)}", "error")
                return redirect(url_for("main.tables"))
    except Exception as e:
        logger.error(f"Error general en tables: {str(e)}", exc_info=True)
        flash("Error al procesar la solicitud. Por favor, inténtelo de nuevo.", "danger")
        return redirect(url_for("main.tables"))

@main_bp.route('/editar_tabla/<id>', methods=['GET', 'POST'])
def editar_tabla(id):
    # Verificar sesión
    if "username" not in session:
        flash("Debe iniciar sesión para realizar esta acción", "warning")
        return redirect(url_for("auth.login"))
    
    try:
        # Obtener la tabla
        table = current_app.spreadsheets_collection.find_one({'_id': ObjectId(id)})
        
        if not table:
            flash('Tabla no encontrada.', 'error')
            return redirect(url_for('main.dashboard_user'))
        
        # Verificar permisos: solo el propietario puede editar la tabla
        if session.get('role') != 'admin' and table.get('owner') != session.get('username'):
            flash('No tiene permisos para editar esta tabla.', 'error')
            return redirect(url_for('main.dashboard_user'))
        
        if request.method == 'POST':
            # Obtener los datos del formulario
            new_name = request.form.get('name', '').strip()
            headers_str = request.form.get('headers', '').strip()
            
            # Validar los datos
            if not new_name:
                flash('El nombre de la tabla no puede estar vacío.', 'error')
                return render_template('editar_tabla.html', table=table)
            
            # Procesar los encabezados
            new_headers = [h.strip() for h in headers_str.split(',') if h.strip()]
            
            if not new_headers:
                flash('Debe proporcionar al menos un encabezado.', 'error')
                return render_template('editar_tabla.html', table=table)
            
            # Verificar si los encabezados han cambiado
            old_headers = table.get('headers', [])
            
            # Actualizar la tabla en la base de datos
            update_data = {
                'name': new_name,
                'headers': new_headers
            }
            
            # Si los encabezados cambiaron, actualizar los datos
            if set(old_headers) != set(new_headers):
                # Crear un mapeo de viejos a nuevos encabezados para los que coinciden
                header_map = {}
                for old_h in old_headers:
                    if old_h in new_headers:
                        header_map[old_h] = old_h
                
                # Actualizar los datos con los nuevos encabezados
                data = table.get('data', [])
                new_data = []
                
                for row in data:
                    new_row = {}
                    # Mantener los campos que coinciden
                    for old_h, new_h in header_map.items():
                        if old_h in row:
                            new_row[new_h] = row[old_h]
                    
                    # Añadir campos para los nuevos encabezados
                    for h in new_headers:
                        if h not in new_row:
                            new_row[h] = ''
                    
                    # Mantener campos especiales como 'imagenes'
                    if 'imagenes' in row:
                        new_row['imagenes'] = row['imagenes']
                    
                    new_data.append(new_row)
                
                update_data['data'] = new_data
            
            # Actualizar la tabla
            current_app.spreadsheets_collection.update_one(
                {'_id': ObjectId(id)},
                {'$set': update_data}
            )
            
            flash('Tabla actualizada correctamente.', 'success')
            return redirect(url_for('main.ver_tabla', table_id=id))
        
        # GET: Mostrar formulario de edición
        return render_template('editar_tabla.html', table=table)
    
    except Exception as e:
        logger.error(f"Error en editar_tabla: {str(e)}", exc_info=True)
        flash(f"Error al editar la tabla: {str(e)}", "error")
        return redirect(url_for('main.dashboard_user'))

@main_bp.route("/delete_table/<table_id>", methods=["POST"])
def delete_table(table_id):
    # Verificar sesión
    if "username" not in session:
        flash("Debe iniciar sesión para realizar esta acción", "warning")
        return redirect(url_for("auth.login"))

    # Verificar permisos: solo el propietario o admin puede eliminar la tabla
    if session.get("role") == "admin":
        # Los administradores pueden eliminar cualquier tabla
        table = current_app.spreadsheets_collection.find_one({"_id": ObjectId(table_id)})
    else:
        # Los usuarios normales solo pueden eliminar sus propias tablas
        table = current_app.spreadsheets_collection.find_one({"_id": ObjectId(table_id), "owner": session["username"]})

    if not table:
        flash("Tabla no encontrada o no tiene permisos para eliminarla.", "error")
        return redirect(url_for("main.tables"))

    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], table["filename"])

    if os.path.exists(filepath):
        os.remove(filepath)

    current_app.spreadsheets_collection.delete_one({"_id": ObjectId(table_id)})

    if session.get("selected_table") == table["filename"]:
        session.pop("selected_table", None)

    flash("Tabla eliminada exitosamente.", "success")
    return redirect(url_for("main.tables"))