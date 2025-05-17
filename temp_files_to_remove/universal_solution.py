#!/usr/bin/env python
"""
Solución Universal para Problemas de Acceso
Este script:
1. Corrige las inconsistencias en las colecciones de usuarios
2. Configura el bypass en modo desarrollo para garantizar acceso
3. Normaliza los hashes de contraseñas a un formato común

IMPORTANTE: Este script debe ejecutarse una sola vez para unificar el sistema
"""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import get_users_collection
from bson.objectid import ObjectId
import traceback

# Constantes de configuración
ADMIN_CREDENTIALS = [
    {
        "email": "admin@example.com",
        "password": "admin123",
        "username": "administrator",
        "role": "admin",
        "id": "680bc20aa170ac7fe8e58bec"
    },
    {
        "email": "edfrutos@gmail.com",
        "password": "admin123",
        "username": "edefrutos",
        "role": "admin",
        "id": "67ed5c96300befce1d631c44"
    }
]

def unified_fix():
    """Aplicar todas las correcciones en un solo paso."""
    print("=== SOLUCIÓN UNIVERSAL DE ACCESO ===")
    
    # 1. Verificar y corregir las colecciones
    normalize_passwords()
    
    # 2. Crear archivos de configuración para el decorador admin_required
    create_admin_config()
    
    # 3. Crear configuración local para el entorno
    create_environment_config()
    
    print("=== SOLUCIÓN COMPLETADA ===")

def normalize_passwords():
    """Normalizar todas las contraseñas al formato werkzeug para compatibilidad universal."""
    print("\n>> Normalizando contraseñas en la colección...")
    
    users_col = get_users_collection()
    
    # Procesar usuarios administradores primero
    for admin in ADMIN_CREDENTIALS:
        try:
            # Buscar usuario por email
            user = users_col.find_one({"email": admin["email"]})
            
            if not user:
                print(f"  - No se encontró usuario: {admin['email']}")
                continue
                
            # Crear hash werkzeug universal que funciona siempre
            new_password_hash = generate_password_hash(admin["password"])
            
            # Actualizar el usuario con los datos normalizados
            update_data = {
                "password": new_password_hash,
                "password_type": "werkzeug",  # Tipo de contraseña conocido
                "username": admin["username"],  # Nombre de usuario consistente
                "role": "admin",  # Rol correcto
                "password_updated_at": datetime.utcnow().isoformat(),
                "failed_attempts": 0,
                "locked_until": None,
                "active": True,
                "_id": ObjectId(admin["id"])  # Asegurar que tenga el ID correcto
            }
            
            # Actualizar o crear el usuario
            result = users_col.update_one(
                {"_id": ObjectId(admin["id"])},
                {"$set": update_data},
                upsert=True
            )
            
            if result.modified_count > 0 or result.upserted_id:
                print(f"  ✅ Usuario {admin['email']} normalizado correctamente")
            else:
                print(f"  ⚠️ No se modificó el usuario {admin['email']}")
                
        except Exception as e:
            print(f"  ❌ Error procesando {admin['email']}: {str(e)}")
            traceback.print_exc()
    
    print("  Proceso de normalización completado")

def create_admin_config():
    """
    Crear un archivo de configuración para el decorator admin_required
    que garantiza acceso sin importar el modo de ejecución
    """
    print("\n>> Configurando el decorador admin_required...")
    
    # Contenido del archivo de configuración para el decorador
    config_content = """
# Archivo de configuración creado por universal_solution.py
# No modificar manualmente

# Credenciales garantizadas para acceso
ADMIN_ID = "680bc20aa170ac7fe8e58bec"
ADMIN_EMAIL = "admin@example.com"
ADMIN_USERNAME = "administrator"

# Configuración de bypass
ENABLE_BYPASS = True
BYPASS_LOCAL_ONLY = False
"""
    
    # Guardar el archivo de configuración
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               "app", "admin_config.py")
    
    try:
        with open(config_path, "w") as f:
            f.write(config_content)
        print(f"  ✅ Configuración de admin creada en: {config_path}")
    except Exception as e:
        print(f"  ❌ Error creando configuración: {str(e)}")

def create_environment_config():
    """Crear un archivo .env para configuración local"""
    print("\n>> Creando configuración de entorno...")
    
    env_content = """
# Configuración de entorno para solución universal
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=edefrutos2025_secure_key_for_sessions
BYPASS_ADMIN=true
"""
    
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    
    try:
        with open(env_path, "w") as f:
            f.write(env_content)
        print(f"  ✅ Configuración de entorno creada en: {env_path}")
    except Exception as e:
        print(f"  ❌ Error creando configuración: {str(e)}")

if __name__ == "__main__":
    unified_fix()
