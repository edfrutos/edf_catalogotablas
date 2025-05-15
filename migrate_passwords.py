import os
import sys
import bcrypt
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import certifi
from datetime import datetime
import logging
from bson import ObjectId

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/migration.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Establece conexión con MongoDB"""
    try:
        MONGO_URI = os.environ.get("MONGO_URI")
        if not MONGO_URI:
            raise ValueError("MONGO_URI environment variable is not set")

        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            server_api=ServerApi('1')
        )
        
        # Test connection
        client.admin.command('ping')
        logger.info("Conexión a MongoDB establecida exitosamente")
        return client['app_catalogojoyero']
    except Exception as e:
        logger.error(f"Error al conectar con MongoDB: {str(e)}")
        raise

def verify_password(password, stored_password):
    """
    Verifica si la contraseña proporcionada coincide con la almacenada.
    Soporta múltiples formatos: bcrypt, scrypt y werkzeug.
    """
    try:
        password_bytes = password.encode('utf-8')
        
        if isinstance(stored_password, str):
            if stored_password.startswith('scrypt:'):
                from passlib.hash import scrypt
                return scrypt.verify(password, stored_password)
            
            if stored_password.startswith('pbkdf2:sha256:'):
                from werkzeug.security import check_password_hash
                return check_password_hash(stored_password, password)
            
            stored_password_bytes = stored_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, stored_password_bytes)
        
        return bcrypt.checkpw(password_bytes, stored_password)
    except Exception as e:
        logger.error(f"Error al verificar contraseña: {str(e)}")
        return False

def hash_password(password):
    """Genera un hash seguro de la contraseña usando bcrypt"""
    try:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt)
    except Exception as e:
        logger.error(f"Error al generar hash de contraseña: {str(e)}")
        raise

def migrate_user(user, users_collection, users_unified_collection):
    """Migra un usuario de la colección antigua a la nueva"""
    try:
        # Verificar si el usuario ya existe en la colección unificada
        existing_user = users_unified_collection.find_one({"email": user.get("email")})
        if existing_user:
            logger.info(f"Usuario {user.get('email')} ya existe en la colección unificada")
            return False

        # Crear nuevo documento de usuario
        new_user = {
            "email": user.get("email"),
            "nombre": user.get("nombre"),
            "role": user.get("role", "normal"),
            "created_at": user.get("created_at", datetime.utcnow()),
            "updated_at": datetime.utcnow(),
            "is_2fa_enabled": user.get("is_2fa_enabled", False),
            "secret_2fa": user.get("secret_2fa"),
            "qr_code": user.get("qr_code"),
            "last_login": user.get("last_login"),
            "last_ip": user.get("last_ip"),
            "locked_until": user.get("locked_until"),
            "migrated_at": datetime.utcnow(),
            "migrated_from": "users"
        }

        # Insertar en la colección unificada
        result = users_unified_collection.insert_one(new_user)
        if result.inserted_id:
            logger.info(f"Usuario {user.get('email')} migrado exitosamente")
            return True
        return False
    except Exception as e:
        logger.error(f"Error al migrar usuario {user.get('email')}: {str(e)}")
        return False

def main():
    try:
        # Conectar a MongoDB
        db = connect_to_mongodb()
        
        # Obtener colecciones
        users_collection = db['users']
        users_unified_collection = db['users_unified']
        
        # Crear índices en la colección unificada
        users_unified_collection.create_index("email", unique=True)
        users_unified_collection.create_index("role")
        
        # Contadores
        total_users = users_collection.count_documents({})
        migrated_users = 0
        failed_users = 0
        
        logger.info(f"Iniciando migración de {total_users} usuarios")
        
        # Migrar usuarios
        for user in users_collection.find():
            if migrate_user(user, users_collection, users_unified_collection):
                migrated_users += 1
            else:
                failed_users += 1
            
            # Mostrar progreso cada 100 usuarios
            if (migrated_users + failed_users) % 100 == 0:
                logger.info(f"Progreso: {migrated_users + failed_users}/{total_users} usuarios procesados")
        
        # Resumen final
        logger.info("Migración completada")
        logger.info(f"Total de usuarios: {total_users}")
        logger.info(f"Usuarios migrados exitosamente: {migrated_users}")
        logger.info(f"Usuarios fallidos: {failed_users}")
        
    except Exception as e:
        logger.error(f"Error en la migración: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 