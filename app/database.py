"""
Módulo para gestionar la conexión a la base de datos MongoDB de forma resiliente.
Permite modo fallback y reconexión automática.
"""

import os
import time
import logging
import threading
from pymongo import MongoClient
from pymongo.errors import (ConnectionFailure, ServerSelectionTimeoutError, 
                           OperationFailure, NetworkTimeout)
from config import MONGO_CONFIG, COLLECTION_USERS, COLLECTION_CATALOGOS, COLLECTION_RESET_TOKENS, COLLECTION_AUDIT_LOGS

# Importar sistemas de caché y fallback
from app.cache_system import cached, set_cache, get_cache
from app.data_fallback import (get_fallback_user_by_email, get_fallback_user_by_id, 
                               get_fallback_catalogs_by_user, sync_users_to_fallback,
                               sync_catalogs_to_fallback)

# Configuración de logging (solo consola para evitar problemas de permisos)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [DB] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Variables globales para acceso a la BD
_mongo_client = None
_mongo_db = None
_is_connected = False
_reconnect_thread = None
_last_error = None

def get_mongo_client():
    """Retorna el cliente MongoDB actual (puede ser None)"""
    global _mongo_client
    return _mongo_client

def get_mongo_db():
    """Retorna la BD MongoDB actual (puede ser None)"""
    global _mongo_db
    return _mongo_db

def is_connected():
    """Indica si hay una conexión activa a MongoDB"""
    global _is_connected
    return _is_connected

def get_last_error():
    """Retorna el último error de conexión"""
    global _last_error
    return _last_error

def initialize_db(app=None):
    """Inicializa la conexión a MongoDB"""
    global _mongo_client, _mongo_db, _is_connected, _last_error
    
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        if app:
            app.logger.warning("No se ha configurado MONGO_URI")
        logging.warning("No se ha configurado MONGO_URI")
        _last_error = "No se ha configurado MONGO_URI"
        return False
    
    try:
        logging.info(f"Iniciando conexión a MongoDB: {mongo_uri[:20]}...")
        
        # Configurar un timeout más corto para la conexión inicial
        config = MONGO_CONFIG.copy()
        config['serverSelectionTimeoutMS'] = 10000  # 10 segundos
        
        # Intentar establecer la conexión
        _mongo_client = MongoClient(mongo_uri, **config)
        
        # Verificar que la conexión está activa con un ping
        _mongo_client.admin.command('ping')
        
        # Si llegamos aquí, la conexión fue exitosa
        _mongo_db = _mongo_client.get_database()
        _is_connected = True
        _last_error = None
        
        logging.info(f"Conexión a MongoDB establecida correctamente. BD: {_mongo_db.name}")
        if app:
            app.logger.info(f"Conexión a MongoDB establecida correctamente. BD: {_mongo_db.name}")
        
        # Sincronizar datos para el fallback
        try:
            logging.info("Sincronizando datos para el modo fallback...")
            sync_users_to_fallback(_mongo_db[COLLECTION_USERS])
            sync_catalogs_to_fallback(_mongo_db[COLLECTION_CATALOGOS])
            logging.info("Sincronización de datos completada correctamente")
        except Exception as e:
            logging.error(f"Error al sincronizar datos para fallback: {str(e)}")
        
        return True
        
    except (ConnectionFailure, ServerSelectionTimeoutError, OperationFailure) as e:
        _last_error = str(e)
        logging.error(f"Error al conectar con MongoDB: {str(e)}")
        if app:
            app.logger.error(f"Error al conectar con MongoDB: {str(e)}")
        
        _is_connected = False
        return False

def schedule_reconnect(delay=60, app=None):
    """Programa un intento de reconexión después de un tiempo"""
    global _reconnect_thread
    
    if _reconnect_thread and _reconnect_thread.is_alive():
        return  # Ya hay un intento de reconexión programado
    
    def reconnect_task():
        logging.info(f"Intentando reconexión a MongoDB después de {delay} segundos...")
        time.sleep(delay)
        initialize_db(app)
    
    _reconnect_thread = threading.Thread(target=reconnect_task)
    _reconnect_thread.daemon = True
    _reconnect_thread.start()

def get_collection(collection_name, fallback_data=None):
    """
    Obtiene una colección de MongoDB de forma segura.
    Si no hay conexión, retorna None o los datos de fallback.
    """
    global _mongo_db, _is_connected
    
    # Corregido: los objetos de base de datos en PyMongo no implementan comprobación booleana
    # Por eso debemos comparar explícitamente con None
    if _is_connected is False or _mongo_db is None:
        return fallback_data
    
    try:
        return _mongo_db[collection_name]
    except Exception as e:
        logging.error(f"Error al acceder a la colección {collection_name}: {str(e)}")
        return fallback_data

# Funciones de utilidad para operaciones comunes

@cached(ttl=600, key_prefix='user')
def get_user_by_email(email):
    """Obtiene un usuario por su email con caché y fallback"""
    # Primero intentamos obtener de MongoDB
    users = get_collection(COLLECTION_USERS)
    if users:
        try:
            user = users.find_one({"email": email})
            if user:
                return user
        except Exception as e:
            logging.error(f"Error al buscar usuario por email: {str(e)}")
    
    # Si no se encuentra o hay error, usamos el fallback
    logging.info(f"Usando fallback para buscar usuario por email: {email}")
    return get_fallback_user_by_email(email)

@cached(ttl=600, key_prefix='user')
def get_user_by_id(user_id):
    """Obtiene un usuario por su ID con caché y fallback"""
    # Primero intentamos obtener de MongoDB
    users = get_collection(COLLECTION_USERS)
    if users:
        try:
            from bson.objectid import ObjectId
            user = users.find_one({"_id": ObjectId(user_id)})
            if user:
                return user
        except Exception as e:
            logging.error(f"Error al buscar usuario por ID: {str(e)}")
    
    # Si no se encuentra o hay error, usamos el fallback
    logging.info(f"Usando fallback para buscar usuario por ID: {user_id}")
    return get_fallback_user_by_id(user_id)

@cached(ttl=300, key_prefix='catalogs')
def get_catalogs_by_user(user_id):
    """Obtiene los catálogos de un usuario con caché y fallback"""
    # Primero intentamos obtener de MongoDB
    catalogs = get_collection(COLLECTION_CATALOGOS)
    if catalogs:
        try:
            from bson.objectid import ObjectId
            user_catalogs = list(catalogs.find({"user_id": ObjectId(user_id)}))
            if user_catalogs:
                return user_catalogs
        except Exception as e:
            logging.error(f"Error al buscar catálogos del usuario: {str(e)}")
    
    # Si no se encuentra o hay error, usamos el fallback
    logging.info(f"Usando fallback para buscar catálogos del usuario: {user_id}")
    return get_fallback_catalogs_by_user(user_id)

# Funciones adicionales para acceder a las colecciones

def get_users_collection():
    """Obtiene la colección de usuarios"""
    return get_collection(COLLECTION_USERS)

def get_catalogs_collection():
    """Obtiene la colección de catálogos"""
    return get_collection(COLLECTION_CATALOGOS)

def get_reset_tokens_collection():
    """Obtiene la colección de tokens de restablecimiento de contraseña"""
    return get_collection(COLLECTION_RESET_TOKENS)

def get_audit_logs_collection():
    """Obtiene la colección de logs de auditoría"""
    return get_collection(COLLECTION_AUDIT_LOGS)
