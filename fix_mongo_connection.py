#!/usr/bin/env python3
"""
Script para verificar y reparar la conexión a MongoDB.
Este script está diseñado para diagnosticar problemas específicos
con la conexión a MongoDB que afectan el inicio de sesión.
"""

import os
import sys
import json
import logging
import traceback
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
import bson
from bson.objectid import ObjectId
import pprint
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [MONGO_FIX] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("mongo_fix")

# Variables de configuración
APP_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_PATH, "app_data")
CONFIG_PATH = os.path.join(APP_PATH, "config.py")
OVERRIDE_CONFIG_PATH = os.path.join(DATA_PATH, "mongodb_override.json")

def ensure_data_directory():
    """Asegura que el directorio de datos exista"""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH, exist_ok=True)
        logger.info(f"Directorio de datos creado: {DATA_PATH}")

def get_mongo_uri():
    """Obtiene la URI de MongoDB desde varias fuentes posibles"""
    # 1. Primero intentamos desde una variable de entorno
    mongo_uri = os.environ.get("MONGO_URI")
    if mongo_uri:
        logger.info("URI de MongoDB obtenida desde variable de entorno")
        return mongo_uri
    
    # 2. Intentamos desde el archivo de configuración principal
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as file:
                config_content = file.read()
                # Buscar la variable MONGO_URI en el archivo
                import re
                match = re.search(r'MONGO_URI\s*=\s*[\'"](.+?)[\'"]', config_content)
                if match:
                    mongo_uri = match.group(1)
                    logger.info("URI de MongoDB obtenida desde config.py")
                    return mongo_uri
    except Exception as e:
        logger.error(f"Error al leer config.py: {str(e)}")
    
    # 3. Intentamos desde el archivo de configuración override
    try:
        if os.path.exists(OVERRIDE_CONFIG_PATH):
            with open(OVERRIDE_CONFIG_PATH, 'r') as file:
                config = json.load(file)
                if "mongo_uri" in config:
                    logger.info("URI de MongoDB obtenida desde archivo override")
                    return config["mongo_uri"]
    except Exception as e:
        logger.error(f"Error al leer archivo override: {str(e)}")
    
    # Si llegamos aquí, no se encontró la URI
    logger.error("No se encontró la URI de MongoDB en ninguna fuente")
    return None

def test_mongo_connection(mongo_uri):
    """Prueba la conexión a MongoDB"""
    if not mongo_uri:
        return False, "No hay URI de MongoDB configurada"
    
    try:
        logger.info(f"Intentando conectar a MongoDB: {mongo_uri[:20]}...")
        
        # Configurar timeout más corto para pruebas
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,  # 5 segundos
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Verificar conexión con ping
        client.admin.command('ping')
        
        # Verificar que podemos acceder a la base de datos
        db_name = pymongo.uri_parser.parse_uri(mongo_uri)['database']
        if not db_name:
            db_name = "app_catalogojoyero"  # Nombre por defecto
        
        db = client[db_name]
        collections = db.list_collection_names()
        
        logger.info(f"Conexión exitosa a MongoDB. Base de datos: {db_name}")
        logger.info(f"Colecciones disponibles: {collections}")
        
        # Verificar si existe la colección de usuarios
        if 'users' in collections:
            users_count = db.users.count_documents({})
            logger.info(f"Encontrados {users_count} usuarios en la base de datos")
            
            # Verificar usuario administrador
            admin = db.users.find_one({"email": "admin@example.com"})
            if admin:
                logger.info(f"Usuario administrador encontrado: {admin.get('email')}")
            else:
                logger.warning("¡Usuario administrador NO encontrado!")
        else:
            logger.warning("¡Colección de usuarios no encontrada!")
        
        return True, f"Conexión exitosa a MongoDB: {db_name}"
    
    except ServerSelectionTimeoutError as e:
        error_msg = f"Error de timeout al seleccionar servidor: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    
    except ConnectionFailure as e:
        error_msg = f"Error de conexión a MongoDB: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    
    except Exception as e:
        error_msg = f"Error inesperado al conectar a MongoDB: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def save_override_config(mongo_uri):
    """Guarda la configuración override para MongoDB"""
    ensure_data_directory()
    
    try:
        config = {"mongo_uri": mongo_uri}
        with open(OVERRIDE_CONFIG_PATH, 'w') as file:
            json.dump(config, file, indent=2)
        logger.info(f"Configuración override guardada en: {OVERRIDE_CONFIG_PATH}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar configuración override: {str(e)}")
        return False

def fix_app_database_module():
    """Modifica el archivo app/database.py para usar el archivo override"""
    database_path = os.path.join(APP_PATH, "app", "database.py")
    backup_path = database_path + ".bak"
    
    if not os.path.exists(database_path):
        logger.error(f"Archivo no encontrado: {database_path}")
        return False
    
    # Hacer backup
    try:
        with open(database_path, 'r') as file:
            original_content = file.read()
        
        with open(backup_path, 'w') as file:
            file.write(original_content)
        logger.info(f"Backup creado: {backup_path}")
    except Exception as e:
        logger.error(f"Error al crear backup: {str(e)}")
        return False
    
    # Buscar línea donde se obtiene la URI y modificarla
    try:
        lines = original_content.split('\n')
        new_lines = []
        modified = False
        
        for line in lines:
            if "mongo_uri = os.getenv('MONGO_URI')" in line:
                # Reemplazar esta línea con una que también intente desde el archivo override
                new_line = """    # Intentar obtener la URI desde varias fuentes
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        # Intentar desde el archivo override
        override_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_data", "mongodb_override.json")
        if os.path.exists(override_path):
            try:
                with open(override_path, 'r') as f:
                    import json
                    config = json.load(f)
                    mongo_uri = config.get("mongo_uri")
                    if mongo_uri:
                        logging.info("URI de MongoDB cargada desde archivo override")
            except Exception as e:
                logging.error(f"Error al cargar override: {str(e)}")"""
                new_lines.append(new_line)
                modified = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
        
        if modified:
            # Escribir el archivo modificado
            with open(database_path, 'w') as file:
                file.write('\n'.join(new_lines))
            logger.info(f"Archivo modificado: {database_path}")
            return True
        else:
            logger.warning("No se encontró el punto de modificación en database.py")
            return False
    
    except Exception as e:
        logger.error(f"Error al modificar database.py: {str(e)}")
        # Restaurar el backup en caso de error
        try:
            import shutil
            shutil.copy(backup_path, database_path)
            logger.info("Restaurado backup debido a error")
        except:
            pass
        return False

def create_mongodb_env_file():
    """Crea un archivo .env con la URI de MongoDB"""
    env_path = os.path.join(APP_PATH, ".env")
    mongo_uri = get_mongo_uri()
    
    if not mongo_uri:
        logger.error("No se puede crear .env sin URI de MongoDB")
        return False
    
    try:
        with open(env_path, 'w') as file:
            file.write(f"MONGO_URI={mongo_uri}\n")
        logger.info(f"Archivo .env creado en: {env_path}")
        return True
    except Exception as e:
        logger.error(f"Error al crear archivo .env: {str(e)}")
        return False

def main():
    """Función principal del script"""
    logger.info("==== INICIO DE DIAGNÓSTICO DE CONEXIÓN A MONGODB ====")
    
    # Paso 1: Obtener la URI de MongoDB
    mongo_uri = get_mongo_uri()
    if not mongo_uri:
        logger.error("No se pudo obtener la URI de MongoDB. Verifica la configuración")
        return 1
    
    # Paso 2: Probar la conexión
    success, message = test_mongo_connection(mongo_uri)
    if not success:
        logger.error(f"La conexión a MongoDB falló: {message}")
        return 1
    
    # Paso 3: Guardar configuración override
    if not save_override_config(mongo_uri):
        logger.warning("No se pudo guardar la configuración override")
    
    # Paso 4: Modificar app/database.py para usar el archivo override
    if not fix_app_database_module():
        logger.warning("No se pudo modificar app/database.py")
    
    # Paso 5: Crear archivo .env
    if not create_mongodb_env_file():
        logger.warning("No se pudo crear archivo .env")
    
    logger.info("==== DIAGNÓSTICO COMPLETADO ====")
    logger.info("Si la aplicación sigue sin funcionar, reinicia el servidor Gunicorn")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Error no controlado: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)
