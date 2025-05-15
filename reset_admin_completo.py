#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para restablecer el usuario administrador en MongoDB
Este script garantiza que el usuario admin@example.com exista y tenga
la contraseña admin123 correctamente configurada.
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """Función principal para restablecer el usuario administrador"""
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Obtener la URI de MongoDB
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            logger.error("No se encontró MONGO_URI en las variables de entorno")
            return False
        
        logger.info(f"Conectando a MongoDB con URI: {mongo_uri[:20]}...")
        
        # Conectar a MongoDB
        client = MongoClient(
            mongo_uri,
            tls=True,
            tlsCAFile=certifi.where(),
            server_api=ServerApi('1')
        )
        
        # Verificar conexión
        client.admin.command('ping')
        logger.info("✅ Conexión a MongoDB establecida correctamente")
        
        # Seleccionar base de datos y colección
        db = client["app_catalogojoyero"]
        users_collection = db["users"]
        
        # Buscar usuario administrador existente
        admin_user = users_collection.find_one({"email": "admin@example.com"})
        
        # Generar hash de contraseña
        password_hash = generate_password_hash("admin123")
        
        if admin_user:
            # Actualizar usuario existente
            logger.info(f"Usuario administrador encontrado con ID: {admin_user['_id']}")
            
            result = users_collection.update_one(
                {"_id": admin_user["_id"]},
                {"$set": {
                    "password": password_hash,
                    "role": "admin",
                    "failed_attempts": 0,
                    "locked_until": None,
                    "updated_at": datetime.utcnow().isoformat(),
                    "password_updated_at": datetime.utcnow().isoformat()
                }}
            )
            
            if result.modified_count > 0:
                logger.info("✅ Usuario administrador actualizado correctamente")
            else:
                logger.warning("⚠️ No se realizaron cambios en el usuario administrador")
                
        else:
            # Crear nuevo usuario administrador
            logger.info("No se encontró usuario administrador, creando uno nuevo...")
            
            new_admin = {
                "nombre": "Administrador",
                "username": "administrator",
                "email": "admin@example.com",
                "password": password_hash,
                "role": "admin",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow().isoformat(),
                "failed_attempts": 0,
                "last_ip": "",
                "last_login": None,
                "locked_until": None,
                "password_updated_at": datetime.utcnow().isoformat()
            }
            
            result = users_collection.insert_one(new_admin)
            logger.info(f"✅ Usuario administrador creado con ID: {result.inserted_id}")
        
        # Verificar todos los usuarios en la colección
        all_users = list(users_collection.find({}, {"email": 1, "role": 1, "_id": 0}))
        logger.info(f"Total de usuarios en la base de datos: {len(all_users)}")
        for user in all_users[:5]:  # Mostrar solo los primeros 5 para no saturar la salida
            logger.info(f"Usuario: {user}")
        
        logger.info("\n=== INSTRUCCIONES DE ACCESO ===")
        logger.info("1. Accede a la aplicación usando:")
        logger.info("   - Email: admin@example.com")
        logger.info("   - Contraseña: admin123")
        logger.info("2. Si sigues teniendo problemas, verifica la configuración de sesiones en app.py y wsgi.py")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
