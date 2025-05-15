from functools import wraps
import logging
import re
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, make_response, jsonify, current_app, abort
from bson import ObjectId
from app.database import (get_reset_tokens_collection, get_users_collection,
                      get_audit_logs_collection, get_catalogs_collection)
from app.audit import audit_log
from app.auth_utils import admin_required
import app.monitoring as monitoring
import app.notifications as notifications
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import io
import csv
import json
import os
import shutil
from flask import send_file
from app.extensions import is_mongo_available

# Importar nuestro módulo de monitoreo
from app import monitoring

logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
# # @admin_required
def dashboard_admin():
    try:
        users_collection = get_users_collection()
        spreadsheets_collection = getattr(current_app, 'spreadsheets_collection', None)
        logger.info(f"[DEBUG] spreadsheets_collection: {spreadsheets_collection}")
        if spreadsheets_collection is not None:
            logger.info(f"[DEBUG] spreadsheets_collection.count_documents: {spreadsheets_collection.count_documents({})}")
        else:
            logger.warning("[DEBUG] spreadsheets_collection es None")
        total_usuarios = users_collection.count_documents({})
        total_catalogos = spreadsheets_collection.count_documents({}) if spreadsheets_collection is not None else 0
        tablas = []
        if spreadsheets_collection is not None:
            # Mostrar todas las tablas/catálogos, no solo los del admin
            tablas = list(spreadsheets_collection.find().sort('created_at', -1))
            logger.info(f"[ADMIN] Se encontraron {len(tablas)} catálogos totales para mostrar en el dashboard.")
        else:
            logger.warning("[ADMIN] La colección de hojas de cálculo es None")
        # Cálculo seguro del porcentaje
        if total_usuarios > 0:
            porcentaje = float(total_catalogos) / float(total_usuarios) * 100.0
        else:
            porcentaje = 0.0
        logger.info(f"[ADMIN] total_usuarios={total_usuarios}, total_catalogos={total_catalogos}, porcentaje calculado: {porcentaje} (tipo: {type(porcentaje)})")
        response = make_response(render_template("admin/dashboard_admin.html",
                                                total_usuarios=total_usuarios,
                                                total_catalogos=total_catalogos,
                                                tablas=tablas,
                                                porcentaje=porcentaje))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        logger.error(f"Error en dashboard_admin: {str(e)}")
        return render_template("error.html", error=f"Error en el panel de administración: {str(e)}"), 500

@admin_bp.route("/maintenance")
# # @admin_required
def maintenance():
    try:
        # Obtener estadísticas de archivos temporales
        monitoring.check_temp_files()
        temp_stats = monitoring._app_metrics["temp_files"]
        
        # Obtener estadísticas de caché
        cache_stats = monitoring._app_metrics["cache_status"]
        
        # Obtener espacio en disco disponible
        monitoring.check_system_health()
        disk_stats = monitoring._app_metrics["system_status"]["disk_usage"]
        
        # Preparar datos para la plantilla
        maintenance_data = {
            "temp_files": temp_stats,
            "cache": cache_stats,
            "disk": disk_stats,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return render_template("admin/maintenance.html", data=maintenance_data)
    except Exception as e:
        logger.error(f"Error en maintenance: {str(e)}")
        flash("Error al cargar la página de mantenimiento", "danger")
        return redirect(url_for('admin.dashboard_admin'))

@admin_bp.route("/system-status")
# # @admin_required
def system_status():
    try:
        # Obtener datos del sistema
        data = get_system_status_data()
        
        # Obtener la lista de archivos de log
        logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs'))
        log_files = get_log_files(logs_dir)
        
        # Obtener la lista de archivos de backup
        backup_dir = os.path.abspath(os.path.join(os.getcwd(), 'backups'))
        logger.info(f"Directorio de backups: {backup_dir}")
        backup_files = get_backup_files(backup_dir)
        
        return render_template('admin/system_status.html', data=data, log_files=log_files, backup_files=backup_files)
    except Exception as e:
        logger.error(f"Error en system_status: {str(e)}", exc_info=True)
        flash("Error al obtener el estado del sistema", "danger")
        return redirect(url_for('admin.dashboard_admin'))

def get_system_status_data():
    try:
        # Obtener informe completo de estado
        health_report = monitoring.get_health_status()
        
        # Actualizar información de la base de datos
        from app.extensions import mongo
        if is_mongo_available():
            monitoring.check_database_health(mongo.cx)
        else:
            monitoring._app_metrics["database_status"] = {
                "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "is_available": False,
                "response_time_ms": 0,
                "error": "Conexión a la base de datos no inicializada"
            }
        
        # Obtener estadísticas de solicitudes
        request_stats = monitoring._app_metrics["request_stats"]
        
        # Calcular uptime
        start_time = datetime.strptime(monitoring._app_metrics["start_time"], "%Y-%m-%d %H:%M:%S")
        uptime = datetime.now() - start_time
        uptime_str = str(uptime).split('.')[0]  # Formato HH:MM:SS
        
        status_data = {
            "health": health_report,
            "uptime": uptime_str,
            "request_stats": request_stats,
            "database": monitoring._app_metrics["database_status"],
            "refresh_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return status_data
    except Exception as e:
        logger.error(f"Error en get_system_status_data: {str(e)}", exc_info=True)
        return {
            "health": {"status": "error", "metrics": {"system_status": {"cpu_usage": 0, "memory_usage": {"used_mb": 0, "total_mb": 0}, "disk_usage": {"used_gb": 0, "total_gb": 0}}}},
            "uptime": "Error",
            "request_stats": {"total_requests": 0},
            "database": {"is_available": False, "response_time_ms": 0},
            "refresh_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    return status_data

def get_log_files(logs_dir):
    """Obtiene la lista de archivos de log disponibles"""
    try:
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
            return []
        
        # Obtener todos los archivos con extensión .log
        log_files = []
        for file in os.listdir(logs_dir):
            if file.endswith('.log'):
                file_path = os.path.join(logs_dir, file)
                # Obtener tamaño y fecha de modificación
                stats = os.stat(file_path)
                size_kb = stats.st_size / 1024
                mod_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                log_files.append({
                    'name': file,
                    'size': f"{size_kb:.2f} KB",
                    'modified': mod_time
                })
        
        # Ordenar por fecha de modificación (más reciente primero)
        log_files.sort(key=lambda x: x['modified'], reverse=True)
        return log_files
    except Exception as e:
        logger.error(f"Error al obtener archivos de log: {str(e)}", exc_info=True)
        return []
        
def get_backup_files(backup_dir):
    """Obtiene la lista de archivos de backup disponibles"""
    try:
        logger.info(f"Buscando archivos de backup en: {backup_dir}")
        if not os.path.exists(backup_dir):
            logger.warning(f"El directorio de backups no existe: {backup_dir}")
            os.makedirs(backup_dir, exist_ok=True)
            logger.info(f"Directorio de backups creado: {backup_dir}")
            return []
        
        # Patrones para identificar archivos de backup
        backup_patterns = [
            r'^.*\.bak.*$',  # Cualquier archivo que contenga .bak en cualquier parte de la extensión
            r'^.*\.backup.*$',
            r'^.*\.old.*$',
            r'^.*\.back.*$',
            r'^.*_backup.*$',
            r'^backup_.*$',
            r'^.*_old.*$',
            r'^.*_copy.*$',
            r'^copy_of_.*$',
            r'^.*\.tmp$',
            r'^.*\.swp$',
            r'^.*~$'  # Archivos temporales de editores como vim
        ]
        
        # Extensiones comunes de backup
        backup_extensions = [
            '.bak', '.backup', '.zip', '.tar', '.gz', '.sql', '.dump',
            '.old', '.back', '.tmp', '.swp', '~'
        ]
        
        # Función para determinar si un archivo es de backup
        def is_backup_file(filename):
            basename = os.path.basename(filename)
            
            # Verificar patrones específicos
            for pattern in backup_patterns:
                if re.match(pattern, basename):
                    return True
            
            # Verificar extensiones compuestas (como .bak.funcionalidad)
            if '.bak.' in basename:
                return True
            
            # Verificar otras extensiones comunes de backup
            for ext in backup_extensions:
                if basename.endswith(ext):
                    return True
                    
            # Verificar si contiene palabras clave de backup
            keywords = ['backup', 'copia', 'old', 'bak', 'respaldo']
            for keyword in keywords:
                if keyword in basename.lower():
                    return True
            
            return False
        
        # Procesar todos los archivos en el directorio de backups
        backup_files = []
        all_files = []
        
        # Recorrer recursivamente el directorio de backups
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                # Ignorar archivos ocultos
                if file.startswith('.'):
                    continue
                    
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, backup_dir)
                
                # Si está en un subdirectorio, añadir el nombre relativo
                display_name = rel_path if os.path.dirname(rel_path) else file
                
                # Verificar si es un archivo de backup
                if is_backup_file(file):
                    all_files.append((full_path, display_name))
        
        logger.info(f"Total de archivos encontrados en {backup_dir}: {len(all_files)}")
        
        # Procesar los archivos encontrados
        for full_path, display_name in all_files:
            try:
                stats = os.stat(full_path)
                size_bytes = stats.st_size
                
                # Formato de tamaño legible
                if size_bytes < 1024:
                    size_str = f"{size_bytes} bytes"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes/1024:.2f} KB"
                else:
                    size_str = f"{size_bytes/(1024*1024):.2f} MB"
                    
                mod_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                backup_files.append({
                    'name': display_name,
                    'size': size_str,
                    'modified': mod_time,
                    'path': full_path
                })
                logger.debug(f"Archivo de backup encontrado: {display_name} ({size_str})")
            except Exception as e:
                logger.error(f"Error al procesar archivo {display_name}: {str(e)}")
        
        logger.info(f"Total de archivos de backup encontrados: {len(backup_files)}")
        
        # Ordenar por fecha de modificación (más reciente primero)
        backup_files.sort(key=lambda x: x['modified'], reverse=True)
        return backup_files
    except Exception as e:
        logger.error(f"Error al obtener archivos de backup: {str(e)}", exc_info=True)
        return []

@admin_bp.route("/usuarios")
# # @admin_required
def lista_usuarios():
    try:
        # Obtener la lista de usuarios
        users = list(get_users_collection().find())
        
        # Obtener catálogos para calcular cuántos tiene cada usuario
        catalogs_collection = getattr(current_app, 'spreadsheets_collection', None)
        if catalogs_collection is None:
            from app.extensions import mongo
            catalogs_collection = mongo.db.spreadsheets
        
        # Crear un diccionario con el conteo de catálogos por usuario
        catalog_counts = {}
        
        # Contar por created_by (email del usuario)
        for user in users:
            user_email = user.get("email")
            if user_email:
                count = catalogs_collection.count_documents({"created_by": user_email})
                user["num_catalogs"] = count
                logger.info(f"[ADMIN] Usuario {user_email} tiene {count} catálogos")
            else:
                user["num_catalogs"] = 0
        
        # Calcular estadísticas
        stats = {
            "total": len(users),
            "roles": {
                "admin": sum(1 for u in users if u.get("role") == "admin"),
                "normal": sum(1 for u in users if u.get("role") == "user"),
                "no_role": sum(1 for u in users if not u.get("role"))
            }
        }
        
        return render_template("admin/users.html", users=users, stats=stats)
    except Exception as e:
        logger.error(f"Error en lista_usuarios: {str(e)}", exc_info=True)
        flash(f"Error al cargar la lista de usuarios: {str(e)}", "error")
        return redirect(url_for('admin.dashboard_admin'))

@admin_bp.route("/usuarios/<user_email>/catalogos")
# # @admin_required
def ver_catalogos_usuario(user_email):
    try:
        # Verificar que el usuario existe
        user = get_users_collection().find_one({"email": user_email})
        if not user:
            flash(f"Usuario con email {user_email} no encontrado", "error")
            return redirect(url_for('admin.lista_usuarios'))
        
        # Obtener los catálogos del usuario
        from app.extensions import mongo
        catalogs = list(mongo.db.catalogs.find({"created_by": user_email}))
        
        # Añadir _id_str a cada catálogo para facilitar su uso en las plantillas
        for catalog in catalogs:
            catalog['_id_str'] = str(catalog['_id'])
            
            # Calcular el número de filas del catálogo
            if 'rows' in catalog:
                catalog['row_count'] = len(catalog['rows'])
            elif 'data' in catalog:
                catalog['row_count'] = len(catalog['data'])
            else:
                catalog['row_count'] = 0
                
            # Formatear la fecha de creación
            if 'created_at' in catalog and catalog['created_at']:
                if isinstance(catalog['created_at'], str):
                    catalog['created_at_formatted'] = catalog['created_at']
                else:
                    catalog['created_at_formatted'] = catalog['created_at'].strftime('%d/%m/%Y %H:%M')
            else:
                catalog['created_at_formatted'] = 'N/A'
        
        return render_template("admin/catalogos_usuario.html", user=user, catalogs=catalogs)
    except Exception as e:
        logger.error(f"Error en ver_catalogos_usuario: {str(e)}", exc_info=True)
        flash(f"Error al cargar los catálogos del usuario: {str(e)}", "error")
        return redirect(url_for('admin.lista_usuarios'))

@admin_bp.route("/usuarios/catalogo/<catalog_id>")
# # @admin_required
def ver_catalogo_admin(catalog_id):
    try:
        # Obtener el catálogo
        from app.extensions import mongo
        from bson.objectid import ObjectId
        
        catalog = mongo.db.catalogs.find_one({"_id": ObjectId(catalog_id)})
        if not catalog:
            flash(f"Catálogo con ID {catalog_id} no encontrado", "error")
            return redirect(url_for('admin.lista_usuarios'))
        
        # Añadir _id_str al catálogo
        catalog['_id_str'] = str(catalog['_id'])
        
        return render_template("admin/ver_catalogo.html", catalog=catalog)
    except Exception as e:
        logger.error(f"Error en ver_catalogo_admin: {str(e)}", exc_info=True)
        flash(f"Error al cargar el catálogo: {str(e)}", "error")
        return redirect(url_for('admin.lista_usuarios'))

@admin_bp.route("/usuarios/delete/<user_id>", methods=["POST"])
# # @admin_required
def eliminar_usuario(user_id):
    get_users_collection().delete_one({"_id": ObjectId(user_id)})
    flash("Usuario eliminado", "success")
    return redirect(url_for("admin.lista_usuarios"))

@admin_bp.route("/usuarios/edit/<user_id>", methods=["GET", "POST"])
# # @admin_required
def editar_usuario(user_id):
    try:
        users_col = get_users_collection()
        user = users_col.find_one({"_id": ObjectId(user_id)})
        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("admin.lista_usuarios"))

        if request.method == "POST":
            # Verificar si es una solicitud de verificación desde la página verify_users
            verified = request.form.get("verified")
            if verified == "true":
                users_col.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"verified": True, "updated_at": datetime.now()}}
                )
                flash(f"Usuario {user.get('nombre', 'desconocido')} ha sido verificado", "success")
                # Registrar en el log de auditoría
                audit_log(f"Usuario {user.get('email')} verificado por {session.get('username')}")
                return redirect(url_for("admin.verify_users"))
                
            # Procesamiento normal de edición de usuario
            nombre = request.form.get("nombre")
            email = request.form.get("email")
            role = request.form.get("role", "user")
            new_password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            verified_status = request.form.get("verified_status") == "on"

            # Validar que el nombre y email no estén vacíos
            if not nombre or not email:
                flash("El nombre y el correo son requeridos", "error")
                return redirect(url_for("admin.editar_usuario", user_id=user_id))
            
            # Verificar si el email ya existe para otro usuario
            email_changed = email.lower() != user.get('email', '').lower()
            email_conflict = False
            
            if email_changed:
                # Buscar si el email ya existe para otro usuario
                existing_user = users_col.find_one({"email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}})
                
                if existing_user and str(existing_user.get('_id')) != user_id:
                    email_conflict = True
                    flash(f"El correo electrónico {email} ya está en uso por otro usuario", "error")
                    logger.warning(f"Intento de actualizar usuario {user_id} con email duplicado: {email}")

            # Si se proporcionó una nueva contraseña
            if new_password:
                if new_password != confirm_password:
                    flash("Las contraseñas no coinciden", "error")
                    return redirect(url_for("admin.editar_usuario", user_id=user_id))

                # Verificar que la contraseña cumpla con los requisitos
                if len(new_password) < 8:
                    flash("La contraseña debe tener al menos 8 caracteres", "error")
                    return redirect(url_for("admin.editar_usuario", user_id=user_id))

                # Actualizar la contraseña
                password_hash = generate_password_hash(new_password)
                users_col.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"password": password_hash}}
                )
                flash("Contraseña actualizada", "success")

            # Si hay conflicto de email, no actualizar nada más
            if email_conflict:
                return redirect(url_for("admin.editar_usuario", user_id=user_id))

            # Actualizar otros campos
            update_data = {
                "nombre": nombre,
                "role": role,
                "verified": verified_status,
                "updated_at": datetime.now()
            }
            
            # Solo actualizar el email si ha cambiado
            if email_changed:
                update_data["email"] = email
            
            # Realizar la actualización
            users_col.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            flash("Usuario actualizado correctamente", "success")
            return redirect(url_for("admin.lista_usuarios"))

        return render_template("admin/editar_usuario.html", usuario=user)
    except Exception as e:
        logger.error(f"Error al editar usuario {user_id}: {str(e)}", exc_info=True)
        flash(f"Error al editar usuario: {str(e)}", "error")
        return redirect(url_for("admin.lista_usuarios"))

@admin_bp.route("/usuarios/create", methods=["GET", "POST"])
# # @admin_required
def crear_usuario():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role", "user")
        
        if not all([nombre, email, password]):
            flash("Todos los campos son requeridos", "error")
            return render_template("admin/crear_usuario.html")
            
        users_col = get_users_collection()
        existing_user = users_col.find_one({"email": email})
        
        if existing_user:
            flash("Ya existe un usuario con este email", "error")
            return render_template("admin/crear_usuario.html")
            
        # Aquí deberías implementar la lógica para hashear la contraseña
        # Por ahora, usaremos el password directamente
        user_data = {
            "nombre": nombre,
            "email": email,
            "password": password,  # En producción, hashea esto
            "role": role,
            "num_tables": 0,
            "tables_updated_at": None,
            "last_ip": "",
            "last_login": None,
            "updated_at": None,
            "failed_attempts": 0,
            "locked_until": None
        }
        
        users_col.insert_one(user_data)
        flash("Usuario creado exitosamente", "success")
        return redirect(url_for("admin.lista_usuarios"))
    
    return render_template("admin/crear_usuario.html")

@admin_bp.route("/backup/json")
def backup_json():
    catalog = get_catalogs_collection()
    data = list(catalog.find())
    for d in data:
        d["_id"] = str(d["_id"])
    output = io.StringIO()
    json.dump(data, output, indent=4)
    output.seek(0)
    return send_file(io.BytesIO(output.read().encode()), download_name="backup_catalog.json", as_attachment=True)

@admin_bp.route("/backup/csv")
def backup_csv():
    catalog = get_catalogs_collection()
    data = list(catalog.find())
    if not data:
        flash("No hay datos para exportar", "warning")
        return redirect(url_for("admin.maintenance"))
    headers = list(data[0].keys())
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in data:
        row["_id"] = str(row["_id"])
        writer.writerow(row)
    output.seek(0)
    
    # Registrar backup en métricas
    backup_info = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "csv",
        "records": len(data)
    }
    if "backups" not in monitoring._app_metrics:
        monitoring._app_metrics["backups"] = []
    monitoring._app_metrics["backups"].append(backup_info)
    monitoring.save_metrics()
    
    return send_file(io.BytesIO(output.read().encode()), download_name="backup_catalog.csv", as_attachment=True)

@admin_bp.route("/cleanup_resets")
# # @admin_required
def cleanup_resets():
    result = get_resets_collection().delete_many({"used": True})
    flash(f"Tokens eliminados: {result.deleted_count}", "info")
    
    # Registrar la limpieza en las métricas
    if "cleanup_history" not in monitoring._app_metrics:
        monitoring._app_metrics["cleanup_history"] = []
    
    monitoring._app_metrics["cleanup_history"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "tokens_reset",
        "count": result.deleted_count
    })
    monitoring.save_metrics()
    
    return redirect(url_for("admin.maintenance"))

# API para limpieza de archivos temporales antiguos
@admin_bp.route("/api/cleanup-temp", methods=["POST"])
# # @admin_required
def api_cleanup_temp():
    days = request.form.get("days", 7, type=int)
    result = monitoring.cleanup_old_temp_files(days)
    
    # Registrar la limpieza en las métricas
    if "cleanup_history" not in monitoring._app_metrics:
        monitoring._app_metrics["cleanup_history"] = []
    
    monitoring._app_metrics["cleanup_history"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "temp_files",
        "days": days,
        "files_removed": result.get("files_removed", 0),
        "bytes_removed": result.get("bytes_removed", 0)
    })
    monitoring.save_metrics()
    
    return jsonify({
        "success": True,
        "message": f"Se eliminaron {result.get('files_removed', 0)} archivos temporales",
        "details": result
    })

# API para obtener el estado del sistema
@admin_bp.route("/api/system-status")
# # @admin_required
def api_system_status():
    try:
        # Obtener métricas del sistema
        monitoring.check_system_health()
        
        # Preparar respuesta
        response = {
            "status": "success",
            "data": monitoring._app_metrics
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error en api_system_status: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)})

# API para truncar archivos de log
@admin_bp.route("/api/truncate-logs", methods=["POST"])
# # @admin_required
def api_truncate_logs():
    try:
        # Obtener datos de la solicitud
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No se proporcionaron datos"})
        
        log_files = data.get("logFiles", [])
        method = data.get("method", "complete")
        
        if not log_files:
            return jsonify({"status": "error", "message": "No se especificaron archivos de log"})
        
        # Verificar que los archivos existen y son válidos
        logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs'))
        processed_files = []
        error_files = []
        
        for log_file in log_files:
            # Validar el nombre del archivo para evitar ataques de traversal de directorio
            if '..' in log_file or '/' in log_file or '\\' in log_file:
                error_files.append(f"{log_file} (nombre de archivo no válido)")
                continue
            
            log_path = os.path.join(logs_dir, log_file)
            if not os.path.exists(log_path):
                error_files.append(f"{log_file} (no existe)")
                continue
            
            try:
                if method == "complete":
                    # Truncado completo
                    with open(log_path, 'w') as f:
                        f.truncate(0)
                    processed_files.append(log_file)
                    logger.info(f"Archivo de log {log_file} truncado completamente")
                    
                elif method == "lines":
                    # Mantener últimas N líneas
                    try:
                        line_count = int(data.get("lineCount", 100))
                        if line_count < 10:
                            line_count = 10  # Mínimo 10 líneas
                    except (ValueError, TypeError):
                        line_count = 100  # Valor predeterminado si hay un error
                        logger.warning(f"Valor de lineCount inválido, usando 100 como predeterminado")
                    
                    try:
                        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        # Mantener solo las últimas N líneas
                        if len(lines) > line_count:
                            with open(log_path, 'w', encoding='utf-8') as f:
                                f.writelines(lines[-line_count:])
                            logger.info(f"Archivo de log {log_file} truncado a las últimas {line_count} líneas")
                        else:
                            logger.info(f"El archivo {log_file} tiene menos de {line_count} líneas, no se truncó")
                        
                        processed_files.append(log_file)
                    except UnicodeDecodeError:
                        # Si hay problemas con la codificación, usar un enfoque binario
                        with open(log_path, 'rb') as f:
                            f.seek(0, os.SEEK_END)
                            size = f.tell()
                            
                            # Estimar el tamaño promedio de línea (100 bytes)
                            avg_line_size = 100
                            estimated_size = line_count * avg_line_size
                            
                            # Si el archivo es más grande que el tamaño estimado, truncarlo
                            if size > estimated_size:
                                # Retroceder aproximadamente el número de líneas deseado
                                f.seek(-min(size, estimated_size * 2), os.SEEK_END)
                                # Leer el resto del archivo
                                data = f.read()
                                
                                # Contar nuevas líneas y ajustar si es necesario
                                newlines = data.count(b'\n')
                                if newlines > line_count:
                                    # Encontrar la posición de la línea de inicio
                                    pos = 0
                                    for i in range(newlines - line_count):
                                        next_pos = data.find(b'\n', pos) + 1
                                        if next_pos == 0:  # No se encontró
                                            break
                                        pos = next_pos
                                    
                                    # Escribir solo las últimas líneas
                                    with open(log_path, 'wb') as f:
                                        f.write(data[pos:])
                                    
                                    logger.info(f"Archivo de log {log_file} truncado a aproximadamente las últimas {line_count} líneas (modo binario)")
                                    processed_files.append(log_file)
                                else:
                                    logger.info(f"El archivo {log_file} tiene menos de {line_count} líneas, no se truncó")
                                    processed_files.append(log_file)
                    
                elif method == "date":
                    # Eliminar entradas anteriores a una fecha
                    cutoff_date = data.get("cutoffDate")
                    if not cutoff_date:
                        error_files.append(f"{log_file} (no se especificó fecha de corte)")
                        continue
                    
                    # Convertir la fecha a un objeto datetime
                    try:
                        cutoff_date = datetime.strptime(cutoff_date, "%Y-%m-%d").date()
                    except ValueError:
                        error_files.append(f"{log_file} (formato de fecha inválido, use YYYY-MM-DD)")
                        continue
                    
                    try:
                        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        # Filtrar líneas por fecha
                        kept_lines = []
                        for line in lines:
                            # Intentar extraer la fecha de la línea de log (formato típico: [YYYY-MM-DD HH:MM:SS,mmm])
                            date_match = re.search(r'\[(\d{4}-\d{2}-\d{2})', line)
                            if date_match:
                                try:
                                    line_date_str = date_match.group(1)
                                    line_date = datetime.strptime(line_date_str, "%Y-%m-%d").date()
                                    if line_date >= cutoff_date:
                                        kept_lines.append(line)
                                except ValueError:
                                    # Si hay un error al parsear la fecha, mantener la línea
                                    kept_lines.append(line)
                            else:
                                # Si no se puede extraer la fecha, mantener la línea
                                kept_lines.append(line)
                        
                        # Escribir las líneas filtradas de vuelta al archivo
                        with open(log_path, 'w', encoding='utf-8') as f:
                            f.writelines(kept_lines)
                        
                        logger.info(f"Archivo de log {log_file} truncado a entradas posteriores a {cutoff_date}")
                        processed_files.append(log_file)
                    except UnicodeDecodeError:
                        error_files.append(f"{log_file} (error de codificación, no se puede procesar por fecha)")
                        continue
                    
                else:
                    error_files.append(f"{log_file} (método de truncado no válido)")
                    continue
                    
            except Exception as e:
                logger.error(f"Error al truncar el archivo {log_file}: {str(e)}", exc_info=True)
                error_files.append(f"{log_file} (error: {str(e)})")
        
        # Registrar en el log de auditoría
        audit_log(f"Truncado de logs: {', '.join(processed_files)} usando método {method}")
        
        # Preparar respuesta
        if error_files:
            return jsonify({
                "status": "partial",
                "message": f"Se procesaron {len(processed_files)} archivos con éxito. Errores en {len(error_files)} archivos.",
                "processed": processed_files,
                "errors": error_files
            })
        else:
            return jsonify({
                "status": "success",
                "message": f"Se truncaron {len(processed_files)} archivos de log correctamente.",
                "processed": processed_files
            })
            
    except Exception as e:
        logger.error(f"Error en api_truncate_logs: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"Error al truncar logs: {str(e)}"})

# API para eliminar archivos de backup
@admin_bp.route("/api/delete-backups", methods=["POST"])
# # @admin_required
def api_delete_backups():
    try:
        # Obtener datos de la solicitud
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No se proporcionaron datos"})
        
        backup_files = data.get("backupFiles", [])
        delete_criteria = data.get("deleteCriteria", "selected")
        
        if delete_criteria == "selected" and not backup_files:
            return jsonify({"status": "error", "message": "No se especificaron archivos de backup para eliminar"})
        
        # Verificar que los archivos existen y son válidos
        backup_dir = os.path.abspath(os.path.join(os.getcwd(), 'backups'))
        logger.info(f"API Delete - Directorio de backups: {backup_dir}")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        
        processed_files = []
        error_files = []
        
        # Obtener todos los archivos de backup si el criterio es por fecha o todos
        all_backup_files = []
        if delete_criteria in ["date", "all"]:
            all_backup_files = get_backup_files(backup_dir)
        
        if delete_criteria == "selected":
            # Eliminar archivos seleccionados
            for backup_file in backup_files:
                # Validar el nombre del archivo para evitar ataques de traversal de directorio
                if '..' in backup_file:
                    error_files.append(f"{backup_file} (nombre de archivo no válido)")
                    continue
                
                # Manejar archivos en subdirectorios
                backup_path = os.path.join(backup_dir, backup_file)
                if not os.path.exists(backup_path):
                    error_files.append(f"{backup_file} (no existe)")
                    continue
                
                try:
                    os.remove(backup_path)
                    processed_files.append(backup_file)
                    logger.info(f"Archivo de backup {backup_file} eliminado correctamente")
                except Exception as e:
                    logger.error(f"Error al eliminar el archivo {backup_file}: {str(e)}", exc_info=True)
                    error_files.append(f"{backup_file} (error: {str(e)})")
        
        elif delete_criteria == "date":
            # Eliminar archivos anteriores a una fecha
            cutoff_date = data.get("cutoffDate")
            if not cutoff_date:
                return jsonify({"status": "error", "message": "No se especificó fecha de corte"})
            
            try:
                cutoff_date = datetime.strptime(cutoff_date, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"status": "error", "message": "Formato de fecha inválido, use YYYY-MM-DD"})
            
            for backup_file in all_backup_files:
                try:
                    file_date = datetime.strptime(backup_file['modified'], "%Y-%m-%d %H:%M:%S").date()
                    if file_date < cutoff_date:
                        os.remove(backup_file['path'])
                        processed_files.append(backup_file['name'])
                        logger.info(f"Archivo de backup {backup_file['name']} eliminado (anterior a {cutoff_date})")
                except Exception as e:
                    logger.error(f"Error al procesar el archivo {backup_file['name']}: {str(e)}", exc_info=True)
                    error_files.append(f"{backup_file['name']} (error: {str(e)})")
        
        elif delete_criteria == "all":
            # Eliminar todos los archivos de backup
            for backup_file in all_backup_files:
                try:
                    os.remove(backup_file['path'])
                    processed_files.append(backup_file['name'])
                    logger.info(f"Archivo de backup {backup_file['name']} eliminado (eliminación total)")
                except Exception as e:
                    logger.error(f"Error al eliminar el archivo {backup_file['name']}: {str(e)}", exc_info=True)
                    error_files.append(f"{backup_file['name']} (error: {str(e)})")
        
        else:
            return jsonify({"status": "error", "message": f"Criterio de eliminación no válido: {delete_criteria}"})
        
        # Registrar en el log de auditoría
        audit_log(f"Eliminación de backups: {', '.join(processed_files)} usando criterio {delete_criteria}")
        
        # Preparar respuesta
        if error_files:
            return jsonify({
                "status": "partial",
                "message": f"Se eliminaron {len(processed_files)} archivos, pero hubo errores con {len(error_files)} archivos",
                "processed": processed_files,
                "errors": error_files
            })
        else:
            return jsonify({
                "status": "success",
                "message": f"Se eliminaron {len(processed_files)} archivos correctamente",
                "processed": processed_files
            })
    
    except Exception as e:
        logger.error(f"Error en api_delete_backups: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"Error al procesar la solicitud: {str(e)}"})

# Ruta para descargar un archivo de log específico
@admin_bp.route("/logs/download/<filename>")
# # @admin_required
def download_log(filename):
    try:
        # Validar el nombre del archivo
        if '..' in filename or '/' in filename or '\\' in filename:
            flash("Nombre de archivo no válido", "danger")
            return redirect(url_for("admin.system_status"))
        
        logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs'))
        log_path = os.path.join(logs_dir, filename)
        
        if not os.path.exists(log_path):
            flash(f"El archivo {filename} no existe", "danger")
            return redirect(url_for("admin.system_status"))
        
        # Registrar en el log de auditoría
        audit_log(f"Descarga de archivo de log: {filename}")
        
        return send_file(log_path, as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f"Error al descargar log {filename}: {str(e)}", exc_info=True)
        flash(f"Error al descargar el archivo: {str(e)}", "danger")
        return redirect(url_for("admin.system_status"))

# Ruta para descargar múltiples archivos de log en un ZIP
@admin_bp.route("/logs/download-multiple")
# # @admin_required
def download_multiple_logs():
    try:
        files_param = request.args.get("files", "")
        if not files_param:
            flash("No se especificaron archivos para descargar", "danger")
            return redirect(url_for("admin.system_status"))
        
        files = files_param.split(",")
        logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs'))
        
        # Crear un archivo ZIP temporal
        import tempfile
        import zipfile
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        temp_file.close()
        
        with zipfile.ZipFile(temp_file.name, 'w') as zipf:
            for filename in files:
                # Validar el nombre del archivo
                if '..' in filename or '/' in filename or '\\' in filename:
                    continue
                
                log_path = os.path.join(logs_dir, filename)
                if os.path.exists(log_path):
                    zipf.write(log_path, arcname=filename)
        
        # Registrar en el log de auditoría
        audit_log(f"Descarga de múltiples archivos de log: {', '.join(files)}")
        
        return send_file(temp_file.name, as_attachment=True, download_name="logs.zip")
    except Exception as e:
        logger.error(f"Error al descargar múltiples logs: {str(e)}", exc_info=True)
        flash(f"Error al descargar los archivos: {str(e)}", "danger")
        return redirect(url_for("admin.system_status"))

@admin_bp.route("/notification-settings", methods=["GET", "POST"])
# # @admin_required
def notification_settings():
    """Página de configuración de notificaciones"""
    if request.method == "POST":
        # Actualizar configuración
        enabled = request.form.get("enable_notifications") == "on"
        
        # Configuración SMTP
        smtp_settings = {
            "server": request.form.get("smtp_server"),
            "port": int(request.form.get("smtp_port")),
            "username": request.form.get("smtp_username"),
            "use_tls": request.form.get("smtp_tls") == "on"
        }
        
        # Solo actualizar contraseña si se proporciona una nueva
        password = request.form.get("smtp_password")
        if password:
            smtp_settings["password"] = password
        
        # Procesar destinatarios (filtrar entradas vacías)
        recipients = [r for r in request.form.getlist("recipients") if r.strip()]
        
        # Umbrales
        thresholds = {
            "cpu": int(request.form.get("threshold_cpu")),
            "memory": int(request.form.get("threshold_memory")),
            "disk": int(request.form.get("threshold_disk")),
            "error_rate": int(request.form.get("threshold_error_rate"))
        }
        
        # Tiempo entre alertas
        cooldown = int(request.form.get("cooldown"))
        
        # Guardar configuración
        if notifications.update_settings(
            enabled=enabled,
            smtp_settings=smtp_settings,
            recipients=recipients,
            thresholds=thresholds,
            cooldown=cooldown
        ):
            flash("Configuración de notificaciones actualizada correctamente", "success")
            # Registrar acción de auditoría
            audit_log("notification_settings_updated", details={
                "enabled": enabled,
                "smtp_server": smtp_settings["server"],
                "recipients_count": len(recipients)
            })
        else:
            flash("Error al guardar la configuración de notificaciones", "danger")
        
        return redirect(url_for("admin.notification_settings"))
    
    # Obtener configuración actual
    config = notifications.get_settings()
    
    return render_template("admin/notification_settings.html", config=config)

@admin_bp.route("/api/test-email", methods=["POST"])
# # @admin_required
def test_email():
    """Enviar correo de prueba"""
    email = request.form.get("email")
    if not email:
        return jsonify({"success": False, "error": "No se proporcionó dirección de correo"})
    
    try:
        result = notifications.send_test_email(email)
        if result:
            audit_log("test_email_sent", details={"recipient": email})
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Error al enviar el correo. Verifica la configuración SMTP."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@admin_bp.route("/verify-users")
# # @admin_required
def verify_users():
    try:
        users = list(get_users_collection().find())
        
        # Contar usuarios verificados y no verificados
        verified_count = sum(1 for user in users if user.get('verified', False))
        unverified_count = len(users) - verified_count
        
        # Estadísticas de usuarios
        stats = {
            'total': len(users),
            'verified': verified_count,
            'unverified': unverified_count
        }
        
        # Obtener usuarios no verificados para mostrarlos en la interfaz
        unverified_users = [user for user in users if not user.get('verified', False)]
        
        return render_template('admin/verify_users.html', stats=stats, unverified_users=unverified_users)
    except Exception as e:
        logger.error(f"Error en verify_users: {str(e)}", exc_info=True)
        flash(f"Error al verificar usuarios: {str(e)}", "error")
        return redirect(url_for('admin.maintenance'))

@admin_bp.route("/catalogos-usuario/<user_id>")
# # @admin_required
def ver_catalogos_usuario_por_id(user_id):
    try:
        # Verificar que el usuario existe
        usuario = get_users_collection().find_one({"_id": ObjectId(user_id)})
        if not usuario:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("admin.lista_usuarios"))

        # Obtener la colección de catálogos
        catalogs_collection = getattr(current_app, 'spreadsheets_collection', None)
        if catalogs_collection is None:
            from app.extensions import mongo
            catalogs_collection = mongo.db.spreadsheets

        # Obtener todos los catálogos del usuario por su email
        user_email = usuario.get("email")
        logger.info(f"[ADMIN] Buscando catálogos para el usuario con email: {user_email}")

        catalogs = list(catalogs_collection.find({"created_by": user_email}))
        logger.info(f"[ADMIN] Se encontraron {len(catalogs)} catálogos para el usuario {user_email}")

        # Añadir información adicional a cada catálogo
        for c in catalogs:
            # Contar filas
            c["row_count"] = len(c.get("data", []))
            # Formatear la fecha de creación
            if "created_at" in c and c["created_at"]:
                c["created_at_formatted"] = c["created_at"].strftime("%d/%m/%Y %H:%M")
            else:
                c["created_at_formatted"] = "Fecha desconocida"

        return render_template("admin/catalogos_usuario.html", catalogs=catalogs, usuario=usuario)
    except Exception as e:
        logger.error(f"Error en ver_catalogos_usuario: {str(e)}", exc_info=True)
        flash(f"Error al cargar los catálogos del usuario: {str(e)}", "error")
        return redirect(url_for('admin.lista_usuarios'))

@admin_bp.route("/catalogo/<catalog_id>")
# # @admin_required
def ver_catalogo_admin_detalle(catalog_id):
    try:
        logger.info(f"[ADMIN] Entrando en ver_catalogo_admin con catalog_id={catalog_id}")
        
        # Obtener la colección de catálogos
        catalogs_collection = getattr(current_app, 'spreadsheets_collection', None)
        if catalogs_collection is None:
            from app.extensions import mongo
            catalogs_collection = mongo.db.spreadsheets
            
        catalog = catalogs_collection.find_one({"_id": ObjectId(catalog_id)})
        if not catalog:
            logger.warning(f"[ADMIN] Catálogo no encontrado para id={catalog_id}")
            flash("Catálogo no encontrado", "warning")
            return render_template("admin/ver_catalogo.html", catalog=None, error="Catálogo no encontrado")
            
        # Añadir información adicional al catálogo
        if "created_at" in catalog and catalog["created_at"]:
            catalog["created_at_formatted"] = catalog["created_at"].strftime("%d/%m/%Y %H:%M")
        else:
            catalog["created_at_formatted"] = "Fecha desconocida"
            
        # Contar filas
        catalog["row_count"] = len(catalog.get("data", []))
            
        logger.info(f"[ADMIN] Mostrando catálogo: {catalog['name'] if 'name' in catalog else 'Sin nombre'}")
        return render_template("admin/ver_catalogo.html", catalog=catalog, error=None)
    except Exception as e:
        logger.error(f"Error en ver_catalogo_admin: {str(e)}", exc_info=True)
        flash(f"Error al cargar el catálogo: {str(e)}", "error")
        return redirect(url_for('admin.dashboard_admin'))

@admin_bp.route("/catalogo/<catalog_id>/editar", methods=["GET", "POST"])
# # @admin_required
def editar_catalogo_admin(catalog_id):
    catalogs_col = get_catalogs_collection()
    catalog = catalogs_col.find_one({"_id": ObjectId(catalog_id)})
    if not catalog:
        flash("Catálogo no encontrado", "danger")
        return redirect(url_for("admin.dashboard_admin"))
    if request.method == "POST":
        name = request.form.get("name")
        # Puedes añadir más campos editables aquí
        catalogs_col.update_one({"_id": ObjectId(catalog_id)}, {"$set": {"name": name}})
        flash("Catálogo actualizado", "success")
        return redirect(url_for("admin.ver_catalogos_usuario_por_id", user_id=str(catalog.get('created_by_id', ''))))
    return render_template("admin/editar_catalogo.html", catalog=catalog)

@admin_bp.route("/catalogo/<catalog_id>/eliminar", methods=["POST"])
# # @admin_required
def eliminar_catalogo_admin(catalog_id):
    catalogs_col = get_catalogs_collection()
    catalog = catalogs_col.find_one({"_id": ObjectId(catalog_id)})
    if not catalog:
        flash("Catálogo no encontrado", "danger")
        return redirect(url_for("admin.dashboard_admin"))
    catalogs_col.delete_one({"_id": ObjectId(catalog_id)})
    flash("Catálogo eliminado", "success")
    return redirect(request.referrer or url_for("admin.dashboard_admin"))

admin_logs_bp = Blueprint('admin_logs', __name__)

# Decorador para restringir acceso solo a admin
def admin_required_logs(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or session.get('role') != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs/flask_debug.log'))

@admin_logs_bp.route('/admin/logs')
# # @admin_required_logs
def logs_manual():
    return render_template('logs_manual.html')

@admin_logs_bp.route('/admin/logs/tail')
# # @admin_required_logs
def logs_tail():
    n = int(request.args.get('n', 20))
    with open(LOG_PATH, 'r') as f:
        lines = f.readlines()
    last_n_lines = lines[-n:] if len(lines) > n else lines
    return jsonify({'logs': last_n_lines})

@admin_logs_bp.route('/admin/logs/search')
# # @admin_required_logs
def logs_search():
    kw = request.args.get('kw', '').strip()
    if not kw:
        return jsonify({'logs': []})
    with open(LOG_PATH, 'r') as f:
        lines = [l for l in f if kw.lower() in l.lower()]
    return jsonify({'logs': lines})

@admin_logs_bp.route('/admin/logs/download')
# # @admin_required_logs
def logs_download():
    return send_file(LOG_PATH, as_attachment=True, download_name='flask_debug.log')

@admin_logs_bp.route('/admin/logs/clear', methods=['POST'])
# # @admin_required_logs
def logs_clear():
    with open(LOG_PATH, 'w') as f:
        f.truncate(0)
    return jsonify({'status': 'Log limpiado correctamente'})

@admin_logs_bp.route('/admin/logs/size')
# # @admin_required_logs
def logs_size():
    size = os.path.getsize(LOG_PATH)
    backups = len([f for f in os.listdir(os.path.dirname(LOG_PATH)) if f.startswith('flask_debug.log.')])
    return jsonify({'size': size, 'backups': backups})