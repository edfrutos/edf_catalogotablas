# app/routes/auth_routes.py

import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from app.extensions import mail
from app.models import (
    get_users_collection,
    get_resets_collection,
    find_user_by_email_or_name,
    find_reset_token,
    update_user_password,
    mark_token_as_used
)
import secrets
from datetime import datetime, timedelta
import scrypt
import base64
import traceback
import bcrypt
import os
import sys

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

def verify_password(password, stored_password, password_type=None):
    """Verifica una contraseña contra su hash almacenado."""
    try:
        # Convertir a string si es bytes
        if isinstance(stored_password, bytes):
            stored_password = stored_password.decode('utf-8')
            
        # Detectar tipo de hash directamente del prefijo del hash almacenado
        if stored_password.startswith('scrypt:'):
            detected_type = 'scrypt'
        elif stored_password.startswith(('$2a$', '$2b$', '$2y$')):
            detected_type = 'bcrypt'
        else:
            detected_type = 'werkzeug'

        # Si no se pasa password_type o no concuerda con lo detectado, usamos el detectado
        if not password_type or password_type.lower() != detected_type:
            if password_type and password_type.lower() != detected_type:
                logger.warning(
                    "Incongruencia entre password_type='%s' y hash detectado='%s'. Se usará '%s'", 
                    password_type, detected_type, detected_type
                )
            password_type = detected_type

        if password_type == 'scrypt':
            # Primero probar con check_password_hash (compatible con formato scrypt de Werkzeug)
            try:
                if check_password_hash(stored_password, password):
                    logger.debug("Verificación scrypt vía Werkzeug exitosa")
                    return True
            except Exception as e:
                # Si el formato no es el esperado por Werkzeug, continuamos con validación manual
                logger.debug("check_password_hash no aplicable para este hash scrypt: %s", str(e))

            # Extraer parámetros del hash scrypt
            try:
                parts = stored_password.split('$')
                if len(parts) != 3:
                    logger.error("Formato scrypt inválido: %s", stored_password)
                    return False
                    
                # El formato es: scrypt:N:r:p$salt$hash
                params = parts[0].split(':')  # [scrypt, N, r, p]
                if len(params) != 4:
                    logger.error("Parámetros scrypt inválidos: %s", parts[0])
                    return False
                    
                n = int(params[1])  # 32768
                r = int(params[2])  # 8
                p = int(params[3])  # 1
                
                # Decodificar salt de base64
                try:
                    salt = base64.b64decode(parts[1] + '==')
                except Exception as e:
                    logger.error("Error decodificando salt: %s", str(e))
                    return False
                    
                stored_hash = parts[2]
                
                try:
                    # Verificar contraseña usando scrypt
                    hashed_bytes = scrypt.hash(password.encode('utf-8'), salt, N=n, r=r, p=p)
                    # Determinar si el hash almacenado está en hex o base64
                    if all(ch in '0123456789abcdef' for ch in stored_hash.lower()):
                        password_hash = hashed_bytes.hex()
                    else:
                        password_hash = base64.b64encode(hashed_bytes).decode('utf-8')
                        # Eliminar padding '=' si existe
                        password_hash = password_hash.rstrip('=')
                    logger.debug(f"Hash scrypt calculado: {password_hash} (hex? {'hex' if all(ch in '0123456789abcdef' for ch in stored_hash.lower()) else 'b64'})")
                    return password_hash == stored_hash
                except Exception as e:
                    logger.error("Error verificando contraseña scrypt: %s", str(e))
                    return False
            except Exception as e:
                logger.error("Error procesando hash scrypt: %s", str(e))
                return False
        
        elif password_type == 'bcrypt':
            try:
                return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
            except Exception as e:
                logger.error("Error verificando contraseña bcrypt: %s", str(e))
                return False

        elif password_type == 'werkzeug':
            # No es necesario convertir a bytes, check_password_hash maneja pbkdf2 y scrypt
            return check_password_hash(stored_password, password)
        
        else:
            logger.warning("Tipo de contraseña desconocido: %s", password_type)
            return False
            
    except Exception as e:
        logger.error("Error general en verificación de contraseña: %s", str(e))
        return False

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Redirección automática si ya está autenticado
    if session.get('logged_in'):
        if session.get('role') == 'admin':
            return redirect('/admin/')
        else:
            return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        logger.info(f"Intentando registrar usuario: {email}")

        if not nombre or not email or not password:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('auth.register'))

        # Verificar si el email ya existe
        users_collection = getattr(current_app, 'users_collection', None)
        if users_collection is None and hasattr(current_app, 'mongo'):
            users_collection = current_app.mongo.db.users
        if users_collection.find_one({"email": email}):
            logger.warning(f"Email ya registrado: {email}")
            flash('Ese email ya está registrado.', 'error')
            return redirect(url_for('auth.register'))

        # Generar hash de contraseña usando Werkzeug
        hashed_password = generate_password_hash(password)
        
        # Crear documento de usuario
        nuevo_usuario = {
            "nombre": nombre,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "role": "user",
            "updated_at": datetime.utcnow().isoformat(),
            "failed_attempts": 0,
            "last_ip": "",
            "last_login": None,
            "locked_until": None,
            "num_tables": 0,
            "password_updated_at": datetime.utcnow().isoformat(),
            "tables_updated_at": None
        }
        
        # Insertar en la colección users
        try:
            result = users_collection.insert_one(nuevo_usuario)
            logger.info(f"Usuario registrado correctamente: {email}")
            
            # Iniciar sesión automáticamente
            session['user_id'] = str(result.inserted_id)
            session['username'] = nombre
            session['email'] = email
            session['role'] = "user"
            session['logged_in'] = True
            
            flash('¡Registro exitoso!', 'success')
            
            # Redireccionar según el rol del usuario
            if session.get('role') == 'admin':
                logger.info("Redirigiendo a panel de administración")
                return redirect(url_for('admin.dashboard_admin'))
            else:
                logger.info("Redirigiendo a dashboard de usuario")
                return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            logger.error(f"Error registrando usuario: {str(e)}")
            flash('Error interno del servidor. Por favor intenta nuevamente.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirección automática si ya está autenticado
    if session.get('logged_in'):
        if session.get('role') == 'admin':
            return redirect('/admin/')
        else:
            return redirect(url_for('main.dashboard'))
    try:
        # Log de la función completa al inicio
        logger.debug(f"==== FUNCIÓN LOGIN INICIADA ====\nMétodo: {request.method}\nURL: {request.url}\nReferrer: {request.referrer}\nIP: {request.remote_addr}\nUser-Agent: {request.user_agent}")
        
        if request.method == 'GET':
            logger.debug("Mostrando formulario de login")
            return render_template('login.html')
            
        logger.info("=== INICIO DE INTENTO DE LOGIN ===")
        # Permitir formularios que envíen el nombre del campo como 'login_input' o simplemente 'email'
        email = (request.form.get('login_input') or request.form.get('email') or '').strip().lower()
        password = request.form.get('password', '').strip()
        
        logger.info(f"Datos recibidos - Email: {email}")
        logger.debug(f"Headers de la solicitud: {dict(request.headers)}")
        logger.debug(f"Datos del formulario: {dict(request.form)}")
        
        if not email or not password:
            flash('Email y contraseña son requeridos.', 'error')
            return redirect(url_for('auth.login'))

        logger.info(f"Buscando usuario en la base de datos: {email}")
        users_collection = getattr(current_app, 'users_collection', None)
        if users_collection is None and hasattr(current_app, 'mongo'):
            users_collection = current_app.mongo.db.users
        usuario = find_user_by_email_or_name(email)
        logger.info(f"[LOGIN] Usuario recuperado de la base de datos: {usuario}")

        if not usuario:
            logger.warning(f"Usuario no encontrado: {email}")
            flash('Credenciales inválidas.', 'error')
            return redirect(url_for('auth.login'))
        
        # NUEVO: Redirigir a cambio de contraseña si es necesario
        if usuario.get('password') == 'RESET_REQUIRED' or usuario.get('must_change_password'):
            session['force_password_user_id'] = str(usuario['_id'])
            flash('Debes crear una nueva contraseña antes de continuar.', 'warning')
            return redirect(url_for('usuarios.force_password_change'))
        
        logger.info(f"Usuario encontrado: {email}")
        logger.debug(f"Datos del usuario: {usuario}")

        # Verificar si el usuario está bloqueado
        if usuario.get('locked_until'):
            try:
                # Registrar el tipo de dato locked_until para depuración
                logger.debug(f"Tipo de dato locked_until: {type(usuario['locked_until'])}, Valor: {usuario['locked_until']}")
                
                # Intentar interpretar la fecha
                if isinstance(usuario['locked_until'], str):
                    try:
                        locked_until = datetime.fromisoformat(usuario['locked_until'])
                    except ValueError:
                        # Esto maneja formatos antiguos o incorrectos
                        locked_until = datetime.strptime(usuario['locked_until'], "%Y-%m-%dT%H:%M:%S.%f")
                else:
                    # Si es un objeto datetime de MongoDB
                    locked_until = usuario['locked_until']
                    
                # Usar utcnow para garantizar comparación correcta de tiempos
                now = datetime.utcnow()
                logger.info(f"Verificando bloqueo - Hora actual UTC: {now}, Fecha de bloqueo: {locked_until}")
                
                if locked_until > now:
                    remaining_time = (locked_until - now).total_seconds() / 60
                    flash(f'Cuenta bloqueada. Intente nuevamente en {int(remaining_time)} minutos.', 'error')
                    return redirect(url_for('auth.login'))
                else:
                    # Desbloquear la cuenta automáticamente
                    logger.info(f"Bloqueo expirado para usuario {usuario['email']} - Desbloqueando")
                    users_collection.update_one(
                        {'_id': usuario['_id']},
                        {'$set': {
                            'failed_attempts': 0,
                            'locked_until': None
                        }}
                    )
            except Exception as e:
                # Si hay error en el formato de fecha, ignoramos el bloqueo por seguridad
                logger.error(f"Error al procesar la fecha de bloqueo: {str(e)}")
                users_collection.update_one(
                    {'_id': usuario['_id']},
                    {'$set': {
                        'locked_until': None
                    }}
                )

        # Asegurar que password existe en el usuario
        if 'password' not in usuario:
            logger.error(f"Usuario {email} no tiene campo password definido")
            flash('Error en la configuración de la cuenta. Contacte al administrador.', 'error')
            return redirect(url_for('auth.login'))
            
        # Debugging del tipo y valor de password
        logger.debug(f"Tipo de dato password: {type(usuario['password'])}, Longitud: {len(str(usuario['password']))}")
        
        logger.info(f"Verificando contraseña para usuario: {email}")
        password_result = verify_password(password, usuario['password'], usuario.get('password_type'))
        print(f"Resultado de verificación de contraseña: {password_result}")
        
        # Para admin@example.com, permitir acceso directo con admin123 (bypass de seguridad temporal)
        if email == 'admin@example.com' and password == 'admin123':
            logger.warning("Acceso directo permitido para el administrador")
            password_result = True
            
        if password_result:
            # Limpiar intentos fallidos
            users_collection.update_one(
                {'_id': usuario['_id']},
                {'$set': {
                    'failed_attempts': 0,
                    'locked_until': None,
                    'last_login': datetime.utcnow().isoformat(),
                    'last_ip': request.remote_addr
                }}
            )

            # Limpiar la sesión anterior si existe
            session.clear()

            # Restaurar todos los datos necesarios en la sesión
            session.permanent = True
            session['user_id'] = str(usuario.get('_id', ''))
            session['email'] = usuario.get('email', '')
            session['username'] = usuario.get('username') or usuario.get('nombre') or 'usuario'
            session['role'] = usuario.get('role', 'user')
            session['logged_in'] = True
            
            # Establecer hora de inicio de sesión para rastreo
            session['login_time'] = datetime.utcnow().isoformat()
            session['client_ip'] = request.remote_addr

            # Forzar guardado de sesión y envío de cookie
            session.modified = True
            
            # Registrar información detallada para depuración
            logger.info(f"[LOGIN] Sesión establecida para usuario: {session.get('username')} (ID: {session.get('user_id')})")
            logger.info(f"[LOGIN] Datos completos de sesión: {dict(session)}")
            logger.debug(f"[LOGIN] Cookies de sesión: {request.cookies}")
            logger.debug(f"[LOGIN] Configuración de sesión: COOKIE_NAME={current_app.config.get('SESSION_COOKIE_NAME')}, SECURE={current_app.config.get('SESSION_COOKIE_SECURE')}")
            
            # Registrar en la base de datos el inicio de sesión exitoso
            try:
                users_collection.update_one(
                    {'_id': usuario['_id']},
                    {'$push': {
                        'login_history': {
                            'timestamp': datetime.utcnow().isoformat(),
                            'ip': request.remote_addr,
                            'user_agent': str(request.user_agent)
                        }
                    }}
                )
            except Exception as e:
                logger.error(f"Error al registrar historial de login: {str(e)}")
                # No interrumpir el flujo por este error

            # Redirección según rol
            next_url = request.args.get('next')
            safe_redirect = False
            if next_url:
                # Si el admin intenta ir a una ruta que no es admin, forzar /admin/
                if usuario.get('role') == 'admin' and not next_url.startswith('/admin'):
                    logger.info(f"Forzando redirección a panel de administración para admin, ignorando next: {next_url}")
                    response = redirect('/admin/')
                elif 'login' not in next_url.lower():
                    safe_redirect = True
                    logger.info(f"Redirigiendo a URL next (segura): {next_url}")
                    response = redirect(next_url)
                else:
                    logger.warning(f"Evitando redirección circular a: {next_url}")
            if not safe_redirect:
                if usuario.get('role') == 'admin':
                    logger.info(f"Redirigiendo a panel de administración (por defecto)")
                    response = redirect('/admin/')
                else:
                    logger.info(f"Redirigiendo a dashboard para usuario normal: {usuario.get('email')}")
                    response = redirect(url_for('main.dashboard'))
            response.headers.update({
                'Cache-Control': 'no-cache, no-store, must-revalidate, private',
                'Pragma': 'no-cache',
                'Expires': '0'
            })
            logger.info(f"Login exitoso para: {email}")
            return response

        else:
            logger.warning(f"Contraseña inválida para usuario: {email}")

            # Incrementar contador de intentos fallidos
            failed_attempts = usuario.get('failed_attempts', 0) + 1
            update_data = {'failed_attempts': failed_attempts}

            # Si excede el máximo de intentos, bloquear la cuenta
            if failed_attempts >= 5:
                locked_until = datetime.utcnow() + timedelta(minutes=15)
                update_data['locked_until'] = locked_until.isoformat()
                flash('Demasiados intentos fallidos. Cuenta bloqueada por 15 minutos.', 'error')
            else:
                flash('Credenciales inválidas.', 'error')

            users_collection.update_one(
                {'_id': usuario['_id']},
                {'$set': update_data}
            )

            return redirect(url_for('auth.login'))

    except Exception as e:
        logger.error(f"Error en login: {str(e)}\n{traceback.format_exc()}")
        flash('Ha ocurrido un error al procesar la solicitud.', 'error')
        return render_template('login.html')

# Ruta para login directo de pruebas - ¡SOLO PARA DEPURACIÓN!
@auth_bp.route('/login_directo')
def login_directo():
    try:
        logger.info("===== ACCESO DIRECTO PARA DEPURACIÓN =====")
        
        # Buscar usuario admin
        users_collection = getattr(current_app, 'users_collection', None)
        if users_collection is None and hasattr(current_app, 'mongo'):
            users_collection = current_app.mongo.db.users
        usuario = find_user_by_email_or_name('admin@example.com')
        if not usuario:
            logger.warning("No se encontró el usuario admin para login directo")
            flash('No se encontró el usuario administrador', 'error')
            return redirect(url_for('auth.login'))
            
        # Establecer sesión directamente
        session.clear()
        session.permanent = True
        session['user_id'] = str(usuario['_id'])
        session['email'] = usuario['email']
        session['username'] = usuario.get('username', 'administrator')
        session['role'] = usuario.get('role', 'admin')
        session['logged_in'] = True
        session.modified = True
        
        # Registro detallado
        logger.info(f"Datos de sesión establecidos por acceso directo: {dict(session)}")
        
        # Redirigir al panel de administración
        response = redirect(url_for('admin.dashboard_admin'))
        response.headers.update({
            'Cache-Control': 'no-cache, no-store, must-revalidate, private',
            'Pragma': 'no-cache',
            'Expires': '0'
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Error en login_directo: {str(e)}\n{traceback.format_exc()}")
        flash('Error al procesar el acceso directo', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        usuario_input = request.form.get('usuario', '').strip()
        logger.info("Solicitud de recuperación para: %s", usuario_input)

        if not usuario_input:
            flash('Debes ingresar tu nombre o correo.', 'error')
            return redirect(url_for('auth.forgot_password'))

        users_collection = getattr(current_app, 'users_collection', None)
        if users_collection is None and hasattr(current_app, 'mongo'):
            users_collection = current_app.mongo.db.users
        user = find_user_by_email_or_name(usuario_input)

        if not user:
            logger.warning("Usuario no encontrado en recuperación: %s", usuario_input)
            flash('No se encontró ningún usuario con ese nombre o email.', 'error')
            return redirect(url_for('auth.forgot_password'))

        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=30)

        get_resets_collection().insert_one({
            "user_id": user["_id"],
            "token": token,
            "expires_at": expires_at,
            "used": False
        })

        reset_link = url_for('auth.reset_password', token=token, _external=True)
        msg = Message("Recuperación de contraseña", recipients=[user["email"]])
        msg.sender = "no-reply@edefrutos.xyz"
        msg.body = (
            f"Hola {user.get('nombre', 'usuario')},\n\n"
            f"Para restablecer tu contraseña, haz clic en el siguiente enlace:\n"
            f"{reset_link}\n\nEste enlace caduca en 30 minutos."
        )
        try:
            mail.send(msg)
            logger.info("Email de recuperación enviado a: %s", user["email"])
        except Exception as e:
            logger.exception("Error al enviar el email de recuperación")
            flash("No se pudo enviar el email. Contacte con el administrador.", "danger")

        flash('Se ha enviado un enlace de recuperación a tu email.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')

@auth_bp.route('/request-reset-password', methods=['POST'])
def request_reset_password():
    email = request.form.get('email', '').strip().lower()
    
    if not email:
        flash('Email requerido.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Buscar usuario por email
        users_collection = getattr(current_app, 'users_collection', None)
        if users_collection is None and hasattr(current_app, 'mongo'):
            users_collection = current_app.mongo.db.users
        usuario = users_collection.find_one({"email": email})
        if not usuario:
            logger.warning(f"Solicitud de reset para email no encontrado: {email}")
            # No mostramos el error real para no revelar si el email existe
            flash('Si el email existe, se enviará un correo de recuperación.', 'info')
            return redirect(url_for('auth.login'))
            
        # Generar token de reset
        reset_token = secrets.token_hex(32)
        reset_info = {
            "user_id": usuario["_id"],
            "token": reset_token,
            "created_at": datetime.utcnow(),
            "used": False
        }
        
        # Insertar token en la colección de resets
        get_resets_collection().insert_one(reset_info)
        
        # Enviar email de reset
        msg = Message(
            'Recuperación de contraseña',
            sender='noreply@edefrutos2025.xyz',
            recipients=[email]
        )
        reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
        msg.body = f"Para restablecer tu contraseña, haz clic en el siguiente enlace:\n\n{reset_url}"
        mail.send(msg)
        
        logger.info(f"Email de recuperación enviado a: {email}")
        flash('Se ha enviado un correo con instrucciones para recuperar tu contraseña.', 'info')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        logger.error(f"Error en solicitud de reset: {str(e)}")
        flash('Error interno del servidor. Por favor intenta nuevamente.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        # Verificar token
        users_collection = getattr(current_app, 'users_collection', None)
        if users_collection is None and hasattr(current_app, 'mongo'):
            users_collection = current_app.mongo.db.users
        reset_info = get_resets_collection().find_one({"token": token, "used": False})
        if not reset_info:
            flash('Token inválido o expirado.', 'error')
            return redirect(url_for('auth.login'))
            
        if request.method == 'POST':
            new_pass = request.form.get('password', '').strip()
            if not new_pass:
                flash('Contraseña obligatoria.', 'error')
                return render_template('reset_password_form.html', token=token)
            
            # Generar nuevo hash de contraseña usando Werkzeug
            hashed_password = generate_password_hash(new_pass)
            
            # Actualizar contraseña del usuario
            users_collection.update_one(
                {'_id': reset_info["user_id"]},
                {'$set': {
                    'password': hashed_password,
                    'password_updated_at': datetime.utcnow().isoformat()
                }}
            )
            
            # Marcar token como usado
            get_resets_collection().update_one(
                {'_id': reset_info["_id"]},
                {'$set': {'used': True}}
            )
            
            logger.info(f"Contraseña restablecida para usuario ID: '{reset_info['user_id']}'")
            flash('Contraseña restablecida exitosamente. Puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
            
        return render_template('reset_password_form.html', token=token)
        
    except Exception as e:
        logger.error(f"Error en reset de contraseña: {str(e)}")
        flash('Error interno del servidor. Por favor intenta nuevamente.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    usuario = session.get('usuario')
    logger.info("Usuario cerró sesión: %s", usuario)
    
    # Limpiar la sesión
    session.clear()
    
    # Configurar la respuesta para eliminar las cookies
    response = redirect(url_for('auth.login'))  # Redirigir al login ya que no existe welcome.html
    
    # Eliminar explícitamente la cookie de sesión
    response.delete_cookie(current_app.config.get('SESSION_COOKIE_NAME', 'session'))
    
    # Eliminar otras cookies que puedan estar relacionadas con la autenticación
    response.delete_cookie('remember_token')
    
    # Establecer Cache-Control para evitar que el navegador almacene en caché la página
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    flash('Has cerrado sesión correctamente', 'info')
    return response

@auth_bp.route('/debug_secret_key')
def debug_secret_key():
    if 'user_id' not in session:
        return 'No autorizado', 401
    return jsonify({
        'SECRET_KEY': str(current_app.secret_key),
        'SESSION_COOKIE_NAME': current_app.config.get('SESSION_COOKIE_NAME'),
        'pid': os.getpid(),
        'session': dict(session)
    })
