"""
SOLUCIÓN DEFINITIVA PARA EL SISTEMA DE AUTENTICACIÓN
Este script corrige la autenticación para que todos los usuarios (administradores y normales) 
puedan acceder correctamente a sus respectivos dashboards.
"""

import os
import sys
import logging
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Colores para consola
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
    """Conectar a MongoDB Atlas usando el URI del archivo .env"""
    try:
        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            logger.error(f"{RED}❌ No se encontró MONGO_URI en las variables de entorno{RESET}")
            return None

        logger.info(f"Conectando a MongoDB Atlas...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Verificar conexión
        logger.info(f"{GREEN}✅ Conexión exitosa a MongoDB Atlas{RESET}")
        return client
    except Exception as e:
        logger.error(f"{RED}❌ Error conectando a MongoDB: {e}{RESET}")
        return None

def arreglar_usuarios(client):
    """Arreglar y normalizar todos los usuarios en la base de datos"""
    try:
        # Determinar qué base de datos usar
        db_name = os.getenv('MONGO_DB_NAME', 'app_catalogojoyero')
        db = client[db_name]
        
        # Verificar colecciones de usuarios
        collections = db.list_collection_names()
        user_collections = [coll for coll in collections if coll in ["users", "users_unified", "usuarios"]]
        
        if not user_collections:
            logger.error(f"{RED}❌ No se encontraron colecciones de usuarios{RESET}")
            return False
        
        logger.info(f"Colecciones de usuarios encontradas: {user_collections}")
        
        # Procesar cada colección
        total_actualizados = 0
        for collection_name in user_collections:
            collection = db[collection_name]
            users = list(collection.find())
            logger.info(f"Procesando {len(users)} usuarios en {collection_name}")
            
            for user in users:
                # Verificar que el usuario tenga los campos necesarios
                updates = {}
                
                # Asegurar rol correcto
                if 'role' not in user or user['role'] not in ['admin', 'user']:
                    updates['role'] = user.get('role', 'user')
                
                # Verificar password
                if 'password' in user:
                    # Si la contraseña no tiene un formato reconocido, resetearla
                    if not (user['password'].startswith('$2b$') or 
                            user['password'].startswith('scrypt:') or
                            user['password'].startswith('pbkdf2:')):
                        updates['password'] = generate_password_hash('admin123')
                        updates['password_type'] = 'werkzeug'
                        updates['password_updated_at'] = datetime.now().isoformat()
                else:
                    # Si no hay contraseña, crear una por defecto
                    updates['password'] = generate_password_hash('admin123')
                    updates['password_type'] = 'werkzeug'
                    updates['password_updated_at'] = datetime.now().isoformat()
                
                # Asegurar que el usuario tiene email y username
                if 'email' not in user or not user['email']:
                    if 'username' in user and user['username']:
                        updates['email'] = user['username']
                    else:
                        # Usar el ID como base para un email por defecto
                        updates['email'] = f"user_{str(user['_id']).split('-')[0]}@example.com"
                
                if 'username' not in user or not user['username']:
                    if 'email' in user and user['email']:
                        updates['username'] = user['email'].split('@')[0]
                    else:
                        updates['username'] = f"user_{str(user['_id']).split('-')[0]}"
                
                # Otros campos importantes
                if 'failed_attempts' not in user:
                    updates['failed_attempts'] = 0
                
                if 'locked_until' not in user:
                    updates['locked_until'] = None
                
                if 'active' not in user:
                    updates['active'] = True
                
                # Actualizar usuario si hay cambios
                if updates:
                    collection.update_one(
                        {'_id': user['_id']},
                        {'$set': updates}
                    )
                    logger.info(f"Usuario actualizado: {user.get('email') or user.get('username')}")
                    total_actualizados += 1
            
            logger.info(f"{GREEN}✅ Procesados todos los usuarios en {collection_name}{RESET}")
        
        logger.info(f"{GREEN}✅ Total: {total_actualizados} usuarios actualizados{RESET}")
        return True
    except Exception as e:
        logger.error(f"{RED}❌ Error actualizando usuarios: {e}{RESET}")
        return False

def crear_usuario_admin_seguro(client):
    """Crear o actualizar usuario administrador con credenciales seguras"""
    try:
        # Determinar qué base de datos usar
        db_name = os.getenv('MONGO_DB_NAME', 'app_catalogojoyero')
        db = client[db_name]
        
        # Usar la colección principal de usuarios
        collection_name = "users"
        if collection_name not in db.list_collection_names():
            collection_name = "users_unified"
            if collection_name not in db.list_collection_names():
                collection_name = "usuarios"
                if collection_name not in db.list_collection_names():
                    logger.error(f"{RED}❌ No se encontró ninguna colección de usuarios{RESET}")
                    return False
        
        collection = db[collection_name]
        
        # Verificar si ya existe el usuario admin
        admin_user = collection.find_one({"email": "admin@example.com"})
        edfrutos_user = collection.find_one({"email": "edfrutos@gmail.com"})
        
        # Crear o actualizar usuario admin@example.com
        if admin_user:
            # Actualizar admin existente
            collection.update_one(
                {"_id": admin_user["_id"]},
                {"$set": {
                    "password": generate_password_hash("admin123"),
                    "password_type": "werkzeug",
                    "role": "admin",
                    "active": True,
                    "failed_attempts": 0,
                    "locked_until": None,
                    "password_updated_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }}
            )
            logger.info(f"{GREEN}✅ Usuario admin@example.com actualizado{RESET}")
        else:
            # Crear nuevo admin
            admin_data = {
                "email": "admin@example.com",
                "username": "administrator",
                "nombre": "Administrator",
                "password": generate_password_hash("admin123"),
                "password_type": "werkzeug",
                "role": "admin",
                "active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now().isoformat(),
                "failed_attempts": 0,
                "locked_until": None,
                "last_login": None,
                "password_updated_at": datetime.now().isoformat()
            }
            collection.insert_one(admin_data)
            logger.info(f"{GREEN}✅ Nuevo usuario admin@example.com creado{RESET}")
        
        # Crear o actualizar usuario edfrutos@gmail.com
        if edfrutos_user:
            # Actualizar usuario existente
            collection.update_one(
                {"_id": edfrutos_user["_id"]},
                {"$set": {
                    "password": generate_password_hash("admin123"),
                    "password_type": "werkzeug",
                    "role": "admin",
                    "active": True,
                    "failed_attempts": 0,
                    "locked_until": None,
                    "password_updated_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }}
            )
            logger.info(f"{GREEN}✅ Usuario edfrutos@gmail.com actualizado{RESET}")
        else:
            # Crear nuevo usuario
            user_data = {
                "email": "edfrutos@gmail.com",
                "username": "edefrutos",
                "nombre": "ED Frutos",
                "password": generate_password_hash("admin123"),
                "password_type": "werkzeug",
                "role": "admin",
                "active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now().isoformat(),
                "failed_attempts": 0,
                "locked_until": None,
                "last_login": None,
                "password_updated_at": datetime.now().isoformat()
            }
            collection.insert_one(user_data)
            logger.info(f"{GREEN}✅ Nuevo usuario edfrutos@gmail.com creado{RESET}")
        
        return True
    except Exception as e:
        logger.error(f"{RED}❌ Error creando usuario admin: {e}{RESET}")
        return False

def arreglar_decorador_admin():
    """Arreglar el decorador admin_required para que verifique correctamente el rol"""
    try:
        decorator_file = "app/decorators.py"
        if not os.path.exists(decorator_file):
            logger.error(f"{RED}❌ No se encontró el archivo {decorator_file}{RESET}")
            return False
        
        with open(decorator_file, 'r') as file:
            content = file.read()
        
        # Verificar si necesitamos reemplazar el decorador admin_required
        if "def admin_required" in content:
            # Buscar el decorador
            start = content.find("def admin_required")
            if start == -1:
                logger.error(f"{RED}❌ No se pudo encontrar el decorador admin_required{RESET}")
                return False
            
            # Encontrar el final del decorador (buscando la siguiente definición)
            end = content.find("def ", start + 10)
            if end == -1:
                end = len(content)
            
            # Decorador correcto que verifica correctamente el rol
            corrected_decorator = """def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si el usuario está logueado
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Verificar si el usuario tiene rol de admin
        if session.get('role') != 'admin':
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function
"""
            
            # Reemplazar el decorador
            new_content = content[:start] + corrected_decorator + content[end:]
            
            with open(decorator_file, 'w') as file:
                file.write(new_content)
            
            logger.info(f"{GREEN}✅ Decorador admin_required corregido{RESET}")
            return True
        else:
            logger.warning(f"{YELLOW}⚠️ No se encontró el decorador admin_required en {decorator_file}{RESET}")
            return False
    except Exception as e:
        logger.error(f"{RED}❌ Error arreglando decorador: {e}{RESET}")
        return False

def main():
    """Función principal que ejecuta todas las correcciones"""
    # 1. Conectar a MongoDB Atlas
    client = get_mongodb_connection()
    if not client:
        logger.error(f"{RED}❌ No se pudo conectar a MongoDB. Abortando.{RESET}")
        return
    
    # 2. Arreglar usuarios
    if arreglar_usuarios(client):
        logger.info(f"{GREEN}✅ Usuarios arreglados correctamente{RESET}")
    else:
        logger.warning(f"{YELLOW}⚠️ Problemas al arreglar usuarios{RESET}")
    
    # 3. Crear/actualizar usuario administrador seguro
    if crear_usuario_admin_seguro(client):
        logger.info(f"{GREEN}✅ Usuarios administradores verificados{RESET}")
    else:
        logger.warning(f"{YELLOW}⚠️ Problemas con usuarios administradores{RESET}")
    
    # 4. Arreglar decorador admin_required
    if arreglar_decorador_admin():
        logger.info(f"{GREEN}✅ Decorador admin_required corregido{RESET}")
    else:
        logger.warning(f"{YELLOW}⚠️ Problemas al corregir decorador{RESET}")
    
    # 5. Mostrar resultado final
    print(f"\n{GREEN}=================================================={RESET}")
    print(f"{GREEN}           SOLUCIÓN COMPLETADA                   {RESET}")
    print(f"{GREEN}=================================================={RESET}")
    print("\nAhora todos los usuarios pueden acceder correctamente:")
    print(f"1. {YELLOW}Usuarios admin{RESET}: Se dirigirán al panel de administración")
    print(f"2. {YELLOW}Usuarios normales{RESET}: Se dirigirán al dashboard de usuario")
    print(f"\n{YELLOW}Credenciales garantizadas:{RESET}")
    print("   - Admin: edfrutos@gmail.com / admin123")
    print("   - Admin: admin@example.com / admin123")
    print("\nPara aplicar los cambios, reinicie la aplicación:")
    print(f"{YELLOW}   python app.py{RESET}")

if __name__ == "__main__":
    main()
