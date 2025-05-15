#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para desbloquear un usuario administrador bloqueado por demasiados intentos fallidos
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def desbloquear_usuario(username_or_email):
    """Desbloquea un usuario por nombre de usuario o email"""
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
        
        # Buscar usuario por nombre de usuario o email
        query = {"$or": [
            {"username": username_or_email},
            {"email": username_or_email}
        ]}
        
        usuario = users_collection.find_one(query)
        
        if not usuario:
            logger.error(f"❌ No se encontró ningún usuario con username o email: {username_or_email}")
            return False
        
        # Mostrar información del usuario
        logger.info(f"Usuario encontrado: {usuario.get('username') or usuario.get('email')}")
        logger.info(f"ID: {usuario.get('_id')}")
        logger.info(f"Rol: {usuario.get('role')}")
        logger.info(f"Intentos fallidos: {usuario.get('failed_attempts', 0)}")
        logger.info(f"Bloqueado hasta: {usuario.get('locked_until')}")
        
        # Verificar si el usuario está bloqueado
        if not usuario.get('locked_until'):
            logger.info("ℹ️ El usuario no está bloqueado actualmente")
        
        # Desbloquear al usuario
        result = users_collection.update_one(
            {"_id": usuario["_id"]},
            {"$set": {
                "failed_attempts": 0,
                "locked_until": None,
                "updated_at": datetime.utcnow().isoformat()
            }}
        )
        
        if result.modified_count > 0:
            logger.info(f"✅ Usuario {username_or_email} desbloqueado correctamente")
            
            # Verificar que el usuario tenga rol de administrador
            if usuario.get('role') != 'admin':
                logger.warning(f"⚠️ El usuario {username_or_email} no tiene rol de administrador")
                
                # Preguntar si se desea asignar rol de administrador
                asignar_admin = input("¿Desea asignar rol de administrador a este usuario? (s/n): ")
                if asignar_admin.lower() == 's':
                    users_collection.update_one(
                        {"_id": usuario["_id"]},
                        {"$set": {"role": "admin"}}
                    )
                    logger.info(f"✅ Rol de administrador asignado a {username_or_email}")
            
            return True
        else:
            logger.warning(f"⚠️ No se realizaron cambios en el usuario {username_or_email}")
            return False
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username_or_email = sys.argv[1]
    else:
        username_or_email = input("Ingrese el nombre de usuario o email a desbloquear: ")
    
    success = desbloquear_usuario(username_or_email)
    sys.exit(0 if success else 1)
