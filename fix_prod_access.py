#!/usr/bin/env python3
"""
Script para arreglar el acceso en producción.
Este script:
1. Verifica y corrige la configuración de MongoDB
2. Asegura que el usuario administrador existe y tiene la contraseña correcta
3. Crea una ruta de acceso de emergencia para entornos de producción
"""

import os
import sys
import logging
import time
import pymongo
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import traceback

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [FIX_PROD_ACCESS] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("fix_prod_access")

def get_mongo_connection():
    """Obtiene una conexión a MongoDB desde la variable de entorno o usando la URI por defecto"""
    try:
        # Intentar obtener la URI de MongoDB de las variables de entorno
        mongo_uri = os.environ.get("MONGO_URI", 
                                   "mongodb+srv://edfrutos:rYjwUC6pUNrLtbaI@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority")
        
        logger.info(f"Conectando a MongoDB: {mongo_uri[:20]}...")
        
        # Intentar conexión a MongoDB con timeout aumentado
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=20000,
            socketTimeoutMS=30000,
            retryWrites=True,
            retryReads=True
        )
        
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
        # Determinar el nombre de la base de datos desde la URI o usar el por defecto
        mongo_uri = os.environ.get("MONGO_URI", "")
        if "app_catalogojoyero" in mongo_uri:
            db_name = "app_catalogojoyero"
        else:
            # Buscar el nombre de la base de datos en la URI
            parts = mongo_uri.split("/")
            if len(parts) > 3:
                # Extraer el nombre de la base de datos y quitar parámetros adicionales
                db_name = parts[3].split("?")[0]
            else:
                db_name = "app_catalogojoyero"  # Valor por defecto
        
        logger.info(f"Usando base de datos: {db_name}")
        db = client[db_name]
        
        # Verificar colecciones disponibles
        collections = db.list_collection_names()
        logger.info(f"Colecciones disponibles: {collections}")
        
        # Determinar el nombre de la colección para usuarios
        if "users" in collections:
            collection_name = "users"
        elif "usuarios" in collections:
            collection_name = "usuarios"
        elif "users_unified" in collections:
            collection_name = "users_unified"
        else:
            # Si no existe ninguna colección de usuarios, crear 'users'
            collection_name = "users"
            db.create_collection(collection_name)
            logger.info(f"Creada nueva colección: {collection_name}")
        
        users_collection = db[collection_name]
        logger.info(f"Usando colección de usuarios: {collection_name}")
        
        # Datos del administrador
        admin_email = "admin@example.com"
        admin_password = "admin123"  # Contraseña simple para pruebas
        admin_pass_hash = generate_password_hash(admin_password)
        
        # Buscar si existe el administrador por email
        admin_user = users_collection.find_one({"email": admin_email})
        
        if admin_user:
            logger.info(f"Usuario administrador encontrado: {admin_email}")
            
            # Verificar si ya existe otro usuario con username 'admin' que no sea este
            existing_admin_user = users_collection.find_one({"username": "admin", "email": {"$ne": admin_email}})
            admin_username = "administrator" if existing_admin_user else "admin"
            
            if existing_admin_user:
                logger.warning(f"Ya existe otro usuario con username 'admin', usando 'administrator' para {admin_email}")
            
            try:
                # Actualizar datos del administrador
                update_result = users_collection.update_one(
                    {"email": admin_email},
                    {
                        "$set": {
                            "password": admin_pass_hash,
                            "role": "admin",
                            "is_active": True,
                            "active": True,
                            "locked_until": None,
                            "failed_attempts": 0,
                            "username": admin_username,
                            "nombre": "Administrador"
                        }
                    }
                )
                
                logger.info(f"Actualización del administrador: {update_result.modified_count} documentos modificados")
            except Exception as e:
                logger.error(f"Error al actualizar administrador: {str(e)}")
                
                # Intentar actualizar solo la contraseña como último recurso
                try:
                    minimal_update = users_collection.update_one(
                        {"email": admin_email},
                        {
                            "$set": {
                                "password": admin_pass_hash,
                                "role": "admin",
                                "is_active": True,
                                "active": True,
                                "locked_until": None,
                                "failed_attempts": 0
                            }
                        }
                    )
                    logger.info(f"Actualización mínima del administrador: {minimal_update.modified_count} documentos modificados")
                except Exception as e2:
                    logger.error(f"Error también en actualización mínima: {str(e2)}")
                    return False
        else:
            # Verificar si ya existe un usuario con username 'admin'
            existing_admin_user = users_collection.find_one({"username": "admin"})
            admin_username = "administrator" if existing_admin_user else "admin"
            
            if existing_admin_user:
                logger.warning(f"Ya existe otro usuario con username 'admin', usando 'administrator' para el nuevo usuario")
            
            # Crear usuario administrador
            new_admin = {
                "email": admin_email,
                "password": admin_pass_hash,
                "nombre": "Administrador",
                "username": admin_username,
                "role": "admin",
                "is_active": True,
                "active": True,
                "failed_attempts": 0,
                "locked_until": None
            }
            
            try:
                insert_result = users_collection.insert_one(new_admin)
                logger.info(f"Usuario administrador creado con ID: {insert_result.inserted_id}")
            except Exception as e:
                logger.error(f"Error al crear usuario administrador: {str(e)}")
                
                # Intentar con un nombre de usuario único como último recurso
                try:
                    new_admin["username"] = f"admin_{int(time.time())}"
                    insert_result = users_collection.insert_one(new_admin)
                    logger.info(f"Usuario administrador creado con username único y ID: {insert_result.inserted_id}")
                except Exception as e2:
                    logger.error(f"Error también en la creación con username único: {str(e2)}")
                    return False
        
        # Verificar que el usuario se creó/actualizó correctamente
        admin_check = users_collection.find_one({"email": admin_email})
        if admin_check:
            logger.info("Usuario administrador verificado correctamente")
            logger.info(f"Datos: {admin_check}")
            return True
        else:
            logger.error("No se pudo verificar el usuario administrador después de crearlo/actualizarlo")
            return False
            
    except Exception as e:
        logger.error(f"Error al asegurar usuario administrador: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def create_emergency_access_route():
    """Crea un archivo HTML para acceso de emergencia"""
    try:
        # Crear archivo de acceso de emergencia en la raíz del sitio
        emergency_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin-emergency.html")
        
        html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acceso de Emergencia</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 500px; margin: 50px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-top: 0; }
        .btn { display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; }
        .btn:hover { background-color: #45a049; }
        .warning { color: #856404; background-color: #fff3cd; border: 1px solid #ffeeba; padding: 15px; margin: 20px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Acceso de Emergencia</h1>
        <p>Esta página permite el acceso directo al sistema en caso de problemas con el login normal.</p>
        
        <div class="warning">
            <strong>Importante:</strong> Esta página debe eliminarse después de su uso por razones de seguridad.
        </div>
        
        <h2>Opciones de Acceso</h2>
        <p>
            <a href="/login_directo" class="btn">Acceso como Administrador</a>
        </p>
        
        <h3>Credenciales:</h3>
        <p>Email: admin@example.com<br>
        Contraseña: admin123</p>
    </div>
</body>
</html>
        """
        
        with open(emergency_file, 'w') as f:
            f.write(html_content)
        
        # Asegurar permisos de lectura para el servidor web
        os.chmod(emergency_file, 0o644)
        
        logger.info(f"Archivo de acceso de emergencia creado: {emergency_file}")
        return True
    except Exception as e:
        logger.error(f"Error al crear archivo de acceso de emergencia: {str(e)}")
        return False

def create_admin_direct_html():
    """Crea una página HTML para acceso directo de administrador"""
    try:
        # Crear archivo de acceso directo en la raíz del sitio
        direct_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_direct.html")
        
        html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="0;url=/login_directo">
    <title>Redireccionando...</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; text-align: center; }
        .loader { border: 5px solid #f3f3f3; border-top: 5px solid #3498db; border-radius: 50%; width: 50px; height: 50px; animation: spin 2s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <h1>Redireccionando al panel de administración...</h1>
    <div class="loader"></div>
    <p>Si no eres redireccionado automáticamente, <a href="/login_directo">haz clic aquí</a>.</p>
</body>
</html>
        """
        
        with open(direct_file, 'w') as f:
            f.write(html_content)
        
        # Asegurar permisos de lectura para el servidor web
        os.chmod(direct_file, 0o644)
        
        logger.info(f"Archivo de acceso directo creado: {direct_file}")
        return True
    except Exception as e:
        logger.error(f"Error al crear archivo de acceso directo: {str(e)}")
        return False

def main():
    """Función principal que ejecuta las correcciones"""
    logger.info("Iniciando correcciones de acceso en producción...")
    
    # Paso 1: Conectar a MongoDB
    client = get_mongo_connection()
    if not client:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    # Paso 2: Asegurar que existe el usuario administrador
    if not ensure_admin_user(client):
        logger.error("No se pudo asegurar el usuario administrador. Abortando.")
        return False
    
    # Paso 3: Crear archivo de acceso de emergencia
    if not create_emergency_access_route():
        logger.warning("No se pudo crear el archivo de acceso de emergencia. Continuando con las demás correcciones.")
    
    # Paso 4: Crear archivo de acceso directo
    if not create_admin_direct_html():
        logger.warning("No se pudo crear el archivo de acceso directo. Continuando con las demás correcciones.")
    
    logger.info("¡Correcciones completadas con éxito!")
    logger.info("Ahora puedes acceder al sistema usando:")
    logger.info(" - URL de emergencia: https://edefrutos2025.xyz/admin-emergency.html")
    logger.info(" - URL de acceso directo: https://edefrutos2025.xyz/admin_direct.html")
    logger.info(" - Credenciales: admin@example.com / admin123")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
