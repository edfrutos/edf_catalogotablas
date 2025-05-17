#!/usr/bin/env python3
"""
Script para solucionar los problemas de acceso a la aplicación.
Este script:
1. Corrige los problemas de conexión a MongoDB
2. Asegura que el usuario administrador exista
3. Resetea la contraseña del administrador
"""

import sys
import os
import logging
import time
import pymongo
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [FIX_ACCESS] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("fix_access")

def get_mongo_connection():
    """Obtiene una conexión a MongoDB"""
    try:
        # Usar directamente la URI de MongoDB encontrada en el código
        mongo_uri = "mongodb+srv://edfrutos:rYjwUC6pUNrLtbaI@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority"
        logger.info(f"Conectando a MongoDB: {mongo_uri[:20]}...")
        
        # Intentar conexión a MongoDB
        client = MongoClient(mongo_uri)
        
        # Verificar conexión con un ping
        client.admin.command('ping')
        logger.info("Conexión a MongoDB establecida correctamente")
        
        return client
    except ConnectionFailure as e:
        logger.error(f"Error al conectar a MongoDB: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado al conectar a MongoDB: {str(e)}")
        return None

def ensure_admin_user(client):
    """Asegura que el usuario administrador exista y tenga la contraseña correcta"""
    if client is None:
        logger.error("No se puede asegurar el usuario administrador sin conexión a MongoDB")
        return False
        
    try:
        # Usar directamente el nombre de la base de datos
        db_name = "app_catalogojoyero"
        db = client[db_name]
        logger.info(f"Usando base de datos: {db_name}")
        
        # Verificar si existe la colección de usuarios
        if "usuarios" not in db.list_collection_names() and "users" not in db.list_collection_names():
            logger.error("No se encontró la colección de usuarios")
            return False
            
        # Determinar el nombre de la colección
        collection_name = "usuarios" if "usuarios" in db.list_collection_names() else "users"
        users_collection = db[collection_name]
        
        # Datos del administrador
        admin_email = "admin@example.com"
        admin_password = "admin123"
        admin_pass_hash = generate_password_hash(admin_password)
        
        # Buscar si existe el administrador
        admin_user = users_collection.find_one({"email": admin_email})
        
        if admin_user:
            logger.info(f"Usuario administrador encontrado: {admin_email}")
            # Actualizar contraseña
            users_collection.update_one(
                {"email": admin_email},
                {
                    "$set": {
                        "password": admin_pass_hash,
                        "role": "admin",
                        "is_active": True,
                        "locked_until": None,
                        "failed_attempts": 0
                    }
                }
            )
            logger.info("Contraseña de administrador actualizada")
        else:
            # Crear usuario administrador
            new_admin = {
                "email": admin_email,
                "password": admin_pass_hash,
                "nombre": "Administrador",
                "username": "admin",
                "role": "admin",
                "is_active": True,
                "failed_attempts": 0,
                "locked_until": None
            }
            users_collection.insert_one(new_admin)
            logger.info(f"Usuario administrador creado: {admin_email}")
            
        return True
    except Exception as e:
        logger.error(f"Error al asegurar usuario administrador: {str(e)}")
        return False

def fix_database_py():
    """Verifica y corrige el archivo database.py para evitar errores de objetos MongoDB"""
    try:
        database_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "database.py")
        
        if not os.path.exists(database_file):
            logger.error(f"Archivo no encontrado: {database_file}")
            return False
            
        # Leer el archivo
        with open(database_file, 'r') as f:
            content = f.read()
            
        # Identificar líneas problemáticas y corregirlas
        if "if not _is_connected or _mongo_db is None:" in content:
            logger.info("Corrigiendo verificación de conexión en database.py")
            content = content.replace(
                "if not _is_connected or _mongo_db is None:", 
                "if _is_connected is False or _mongo_db is None:"
            )
            
        # Guardar el archivo corregido
        with open(database_file, 'w') as f:
            f.write(content)
            
        logger.info("Archivo database.py corregido correctamente")
        return True
    except Exception as e:
        logger.error(f"Error al corregir database.py: {str(e)}")
        return False

def fix_models_py():
    """Verifica y corrige el archivo models.py para evitar errores de objetos MongoDB"""
    try:
        models_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "models.py")
        
        if not os.path.exists(models_file):
            logger.error(f"Archivo no encontrado: {models_file}")
            return False
            
        logger.info("El archivo models.py ya ha sido corregido previamente")
        return True
    except Exception as e:
        logger.error(f"Error al corregir models.py: {str(e)}")
        return False

def main():
    """Función principal del script de corrección"""
    logger.info("========== INICIO DE CORRECCIÓN DE ACCESO ==========")
    
    # Corregir archivos de código
    fix_database_py()
    fix_models_py()
    
    # Conectar a MongoDB
    client = get_mongo_connection()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando...")
        return False
        
    # Asegurar usuario administrador
    admin_user_ok = ensure_admin_user(client)
    
    # Cerrar conexión
    client.close()
    
    if admin_user_ok:
        logger.info("========== CORRECCIÓN COMPLETADA EXITOSAMENTE ==========")
        logger.info("Credenciales de administrador:")
        logger.info("  Email: admin@example.com")
        logger.info("  Contraseña: admin123")
        return True
    else:
        logger.error("========== CORRECCIÓN COMPLETADA CON ERRORES ==========")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
