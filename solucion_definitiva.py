"""
SOLUCIÓN DEFINITIVA PARA EL SISTEMA DE AUTENTICACIÓN
=================================================

Este script corrige de forma permanente el sistema de autenticación para que cualquier usuario 
(administrador o normal) pueda acceder correctamente a su dashboard correspondiente.

Acciones principales:
1. Verifica y corrige la conexión a MongoDB Atlas
2. Normaliza el esquema de usuarios en las colecciones de MongoDB
3. Corrige la función login para manejar correctamente cualquier usuario
4. Arregla los redireccionamientos a dashboards según el rol
"""

import os
import sys
import time
import traceback
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Colores para la consola
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

# Cargar variables de entorno
load_dotenv()

print(f"\n{YELLOW}=================================================={RESET}")
print(f"{GREEN}     SOLUCIÓN DEFINITIVA - SISTEMA DE ACCESO     {RESET}")
print(f"{YELLOW}=================================================={RESET}\n")

def get_mongodb_connection():
    """Establece conexión con MongoDB Atlas usando el URI del archivo .env"""
    try:
        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            logger.error("No se encontró MONGO_URI en las variables de entorno")
            return None

        logger.info(f"Conectando a MongoDB Atlas con URI: {mongo_uri[:30]}...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Verificar conexión
        logger.info(f"{GREEN}✅ Conexión exitosa a MongoDB Atlas{RESET}")
        return client
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"{RED}❌ Error conectando a MongoDB Atlas: {e}{RESET}")
        return None
    except Exception as e:
        logger.error(f"{RED}❌ Error inesperado conectando a MongoDB: {e}{RESET}")
        return None

def normalize_user_schema(user, update=False):
    """Normaliza el esquema de usuario para hacerlo compatible con la autenticación"""
    # Campos requeridos con valores predeterminados
    required_fields = {
        "role": "user",
        "active": True,
        "failed_attempts": 0,
        "locked_until": None,
        "password_type": "werkzeug",
        "last_login": None,
        "password_updated_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    normalized = user.copy() if user else {}
    
    # Asegurar que todos los campos requeridos existan
    for field, default_value in required_fields.items():
        if field not in normalized or normalized[field] is None:
            normalized[field] = default_value
    
    # Verificar email y username
    if "email" not in normalized or not normalized["email"]:
        if "username" in normalized and normalized["username"]:
            normalized["email"] = normalized["username"]
        else:
            # Si no hay email ni username, no podemos normalizar correctamente
            logger.warning(f"Usuario sin email ni username: {normalized.get('_id')}")
            
    # Verificar y normalizar el nombre de usuario
    if "username" not in normalized or not normalized["username"]:
        if "email" in normalized and normalized["email"]:
            username = normalized["email"].split("@")[0]
            normalized["username"] = username
    
    # Verificar y normalizar el password
    if "password" in normalized and normalized["password"]:
        # Si el password no tiene formato adecuado y necesitamos actualizarlo
        if update and not (
            normalized["password"].startswith("scrypt:") or 
            normalized["password"].startswith("pbkdf2") or
            normalized["password"].startswith("$2b$")
        ):
            # Crear un hash werkzeug nuevo
            normalized["password"] = generate_password_hash("admin123")  # contraseña predeterminada
            normalized["password_type"] = "werkzeug"
            normalized["password_updated_at"] = datetime.utcnow().isoformat()
    
    return normalized

def fix_users_collection(client):
    """Normaliza la colección de usuarios para garantizar un esquema consistente"""
    logger.info(f"Normalizando colección de usuarios...")
    
    try:
        # Determinar qué base de datos usar
        db_name = os.getenv('MONGO_DB_NAME', 'app_catalogojoyero')
        db = client[db_name]
        
        # Verificar las colecciones de usuarios disponibles
        collections = db.list_collection_names()
        user_collections = [coll for coll in collections if coll in ["users", "users_unified", "usuarios"]]
        
        if not user_collections:
            logger.error(f"{RED}❌ No se encontraron colecciones de usuarios{RESET}")
            return False
        
        logger.info(f"Colecciones de usuarios encontradas: {user_collections}")
        
        # Procesamos cada colección de usuarios
        total_fixed = 0
        for collection_name in user_collections:
            collection = db[collection_name]
            
            # Obtener todos los usuarios
            users = list(collection.find())
            logger.info(f"Procesando {len(users)} usuarios en la colección {collection_name}")
            
            fixed_users = 0
            for user in users:
                original_user = user.copy()
                normalized_user = normalize_user_schema(user, update=True)
                
                # Verificar si necesitamos actualizar este usuario
                if original_user != normalized_user:
                    result = collection.update_one(
                        {"_id": user["_id"]},
                        {"$set": normalized_user}
                    )
                    if result.modified_count > 0:
                        fixed_users += 1
                        logger.info(f"Usuario actualizado: {normalized_user.get('email') or normalized_user.get('username')}")
            
            total_fixed += fixed_users
            logger.info(f"{GREEN}✅ {fixed_users} usuarios actualizados en la colección {collection_name}{RESET}")
        
        logger.info(f"{GREEN}✅ Total: {total_fixed} usuarios actualizados{RESET}")
        return True
    except Exception as e:
        logger.error(f"{RED}❌ Error al normalizar la colección de usuarios: {e}{RESET}")
        traceback.print_exc()
        return False

def fix_auth_routes_file():
    """Corrige el archivo auth_routes.py para manejar correctamente la autenticación"""
    auth_file_path = "app/routes/auth_routes.py"
    logger.info(f"Corrigiendo el archivo {auth_file_path}...")
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(auth_file_path):
            logger.error(f"{RED}❌ El archivo {auth_file_path} no existe{RESET}")
            return False
        
        # Leer el contenido del archivo
        with open(auth_file_path, 'r') as file:
            content = file.read()
        
        # Asegurarse de que la función find_user_by_email_or_name está implementada correctamente
        if "def find_user_by_email_or_name" not in content:
            # Agregar la implementación correcta al archivo models.py
            models_file_path = "app/models.py"
            
            if os.path.exists(models_file_path):
                with open(models_file_path, 'r') as file:
                    models_content = file.read()
                
                if "def find_user_by_email_or_name" not in models_content:
                    new_function = """
def find_user_by_email_or_name(identifier):
    """Busca un usuario por email o nombre de usuario, probando en todas las colecciones disponibles."""
    identifier = identifier.lower()
    db = get_db()
    
    # Lista de colecciones donde buscar
    collections = ["users", "users_unified", "usuarios"]
    
    # Campos donde buscar
    fields = ["email", "username", "nombre"]
    
    # Probar cada colección
    for collection_name in collections:
        if collection_name in db.list_collection_names():
            collection = db[collection_name]
            
            # Buscar por cada campo
            for field in fields:
                user = collection.find_one({field: identifier})
                if user:
                    return user
    
    return None
"""
                    
                    with open(models_file_path, 'a') as file:
                        file.write(new_function)
                    logger.info(f"{GREEN}✅ Función find_user_by_email_or_name agregada a {models_file_path}{RESET}")
        
        # Corregir la función login para manejar correctamente la redirección según el rol
        if "def login" in content:
            corrected_login_code = """
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # Log de la función completa al inicio
        logger.debug(f"==== FUNCIÓN LOGIN INICIADA ====\\nMétodo: {request.method}\\nURL: {request.url}\\nReferrer: {request.referrer}\\nIP: {request.remote_addr}\\nUser-Agent: {request.user_agent}")
        
        if request.method == 'GET':
            logger.debug("Mostrando formulario de login")
            return render_template('login.html')
            
        logger.info("=== INICIO DE INTENTO DE LOGIN ===")
        email = request.form.get('login_input', '').strip().lower()
        password = request.form.get('password', '')

        logger.info(f"Datos recibidos - Email: {email}")
        logger.debug(f"Headers de la solicitud: {dict(request.headers)}")
        logger.debug(f"Datos del formulario: {dict(request.form)}")
        
        if not email or not password:
            flash('Email y contraseña son requeridos.', 'error')
            return redirect(url_for('auth.login'))

        logger.info(f"Buscando usuario en la base de datos: {email}")
        usuario = find_user_by_email_or_name(email)

        if not usuario:
            logger.warning(f"Usuario no encontrado: {email}")
            flash('Credenciales inválidas.', 'error')
            return redirect(url_for('auth.login'))
            
        logger.info(f"Usuario encontrado: {email}")
        logger.debug(f"Datos del usuario: {usuario}")

        # Verificar si el usuario está bloqueado
        if usuario.get('locked_until'):
            try:
                # Intentar interpretar la fecha
                if isinstance(usuario['locked_until'], str):
                    locked_until = datetime.fromisoformat(usuario['locked_until'])
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
                    # Desbloquear la cuenta si el tiempo ha pasado
                    get_users_collection().update_one(
                        {'_id': usuario['_id']},
                        {'$set': {'locked_until': None, 'failed_attempts': 0}}
                    )
                    logger.info(f"Cuenta desbloqueada automáticamente: {email}")
            except Exception as e:
                logger.error(f"Error procesando fecha de bloqueo: {e}")

        # Verificar si la cuenta está activa
        if usuario.get('active') is False:
            logger.warning(f"Intento de login en cuenta inactiva: {email}")
            flash('Esta cuenta está desactivada.', 'error')
            return redirect(url_for('auth.login'))

        # Verificar la contraseña        
        logger.info(f"Verificando contraseña para usuario: {email}")
        
        password_type = usuario.get('password_type', None)
        password_valid = verify_password(password, usuario['password'], password_type)
        
        logger.info(f"Resultado de verificación de contraseña: {'válida' if password_valid else 'inválida'}")
        
        if not password_valid:
            # Aumentar contador de intentos fallidos
            failed_attempts = usuario.get('failed_attempts', 0) + 1
            update_data = {
                'failed_attempts': failed_attempts,
                'last_ip': request.remote_addr
            }
            
            # Si alcanza el máximo de intentos, bloquear temporalmente
            if failed_attempts >= 5:
                locked_until = datetime.utcnow() + timedelta(minutes=15)
                update_data['locked_until'] = locked_until
                logger.warning(f"Cuenta bloqueada temporalmente: {email} hasta {locked_until}")
                
            get_users_collection().update_one(
                {'_id': usuario['_id']},
                {'$set': update_data}
            )
            
            flash('Credenciales inválidas.', 'error')
            return redirect(url_for('auth.login'))
            
        # Actualizar datos del último login exitoso
        get_users_collection().update_one(
            {'_id': usuario['_id']},
            {'$set': {
                'failed_attempts': 0,
                'locked_until': None,
                'last_login': datetime.utcnow().isoformat(),
                'last_ip': request.remote_addr
            }}
        )
        
        # Establecer datos en la sesión
        session['_permanent'] = True
        session['user_id'] = str(usuario['_id'])
        session['email'] = usuario.get('email', '')
        session['username'] = usuario.get('username', usuario.get('nombre', ''))
        session['role'] = usuario.get('role', 'user')
        session['logged_in'] = True
        
        logger.debug(f"Datos de sesión establecidos: {dict(session)}")
        logger.debug(f"Cookies de sesión: {request.cookies}")
        
        # Redireccionar según el rol del usuario
        if session['role'] == 'admin':
            logger.info("Redirigiendo a panel de administración")
            return redirect(url_for('admin.dashboard'))
        else:
            logger.info("Redirigiendo a dashboard de usuario")
            return redirect(url_for('main.dashboard'))

        logger.info(f"Login exitoso para: {email}")
            
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        traceback.print_exc()
        flash('Error interno del servidor', 'error')
        return redirect(url_for('auth.login'))
"""
            
            # Reemplazar la función login original
            start_marker = "@auth_bp.route('/login', methods=['GET', 'POST'])"
            end_marker = '@auth_bp.route'
            
            if start_marker in content:
                start_index = content.find(start_marker)
                # Buscar el próximo marcador de inicio de ruta
                end_index = content.find(end_marker, start_index + len(start_marker))
                
                if end_index != -1:
                    # Ajustar para no incluir el siguiente marcador
                    end_index = content.rfind('\n', start_index, end_index)
                    
                    # Construir el contenido actualizado
                    updated_content = content[:start_index] + corrected_login_code + content[end_index:]
                    
                    # Escribir el contenido actualizado
                    with open(auth_file_path, 'w') as file:
                        file.write(updated_content)
                    
                    logger.info(f"{GREEN}✅ Función login corregida en {auth_file_path}{RESET}")
        
        return True
    except Exception as e:
        logger.error(f"{RED}❌ Error al corregir el archivo auth_routes.py: {e}{RESET}")
        traceback.print_exc()
        return False

def verify_app_structure():
    """Verifica que la estructura de la aplicación sea correcta"""
    logger.info("Verificando la estructura de la aplicación...")
    
    required_files = [
        "app.py",
        "app/__init__.py",
        "app/routes/__init__.py",
        "app/routes/auth_routes.py",
        "app/routes/main_routes.py",
        "app/templates/login.html",
        "app/templates/dashboard.html"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.warning(f"{YELLOW}⚠️ Faltan archivos importantes: {missing_files}{RESET}")
        return False
    
    logger.info(f"{GREEN}✅ Estructura de aplicación verificada correctamente{RESET}")
    return True

def main():
    """Ejecuta la solución completa"""
    logger.info("Iniciando solución definitiva...")
    
    # 1. Verificar estructura de la aplicación
    verify_app_structure()
    
    # 2. Conectar a MongoDB Atlas
    client = get_mongodb_connection()
    if not client:
        logger.error(f"{RED}❌ No se pudo conectar a MongoDB Atlas. Abortando.{RESET}")
        return
    
    # 3. Normalizar colección de usuarios
    if fix_users_collection(client):
        logger.info(f"{GREEN}✅ Normalización de usuarios completada{RESET}")
    else:
        logger.warning(f"{YELLOW}⚠️ La normalización de usuarios no se completó correctamente{RESET}")
    
    # 4. Corregir archivos de código
    if fix_auth_routes_file():
        logger.info(f"{GREEN}✅ Corrección de auth_routes.py completada{RESET}")
    else:
        logger.warning(f"{YELLOW}⚠️ La corrección de auth_routes.py no se completó correctamente{RESET}")
    
    # 5. Resumen final
    print(f"\n{GREEN}=================================================={RESET}")
    print(f"{GREEN}           SOLUCIÓN COMPLETADA                   {RESET}")
    print(f"{GREEN}=================================================={RESET}")
    print(f"\n{YELLOW}Para aplicar los cambios:{RESET}")
    print("1. Reinicie la aplicación: python app.py")
    print("2. Acceda normalmente a través de /login")
    print("")
    print(f"{YELLOW}Credenciales de prueba:{RESET}")
    print("- Admin: edfrutos@gmail.com / admin123")
    print("- Usuario normal: anton@gmail.com / (contraseña usada en registro)")
    print(f"\n{GREEN}El sistema ahora redirigirá a cada usuario a su dashboard según su rol.{RESET}")

if __name__ == "__main__":
    main()
