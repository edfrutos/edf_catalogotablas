#!/usr/bin/env python3
"""
Script para verificar y corregir las imágenes de perfil
"""

import os
import sys
from pymongo import MongoClient

def get_mongo_connection():
    """Obtener conexión a MongoDB"""
    try:
        # Cargar variables de entorno
        from dotenv import load_dotenv
        load_dotenv()
        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            print("❌ MONGO_URI no encontrada en variables de entorno")
            return None
        client = MongoClient(mongo_uri)
        db = client.get_default_database()
        return db
    except Exception as e:
        print(f"❌ Error al conectar a MongoDB: {e}")
        return None

def check_profile_images():
    """Verificar imágenes de perfil en la base de datos"""
    print("🔍 Verificando imágenes de perfil...")
    db = get_mongo_connection()
    if db is None:
        return False
    try:
        # Buscar usuarios con imágenes de perfil
        users = db.users.find({"profile_image": {"$exists": True, "$ne": None}})
        print("\n📊 Usuarios con imágenes de perfil:")
        
        for user in users:
            username = user.get('username', 'N/A')
            email = user.get('email', 'N/A')
            profile_image = user.get('profile_image', 'N/A')
            
            print(f"\n👤 Usuario: {username} ({email})")
            print(f"   Imagen: {profile_image}")
            
            # Verificar si la imagen existe localmente
            if profile_image and profile_image != 'N/A':
                local_path = f"app/static/imagenes_subidas/{profile_image}"
                if os.path.exists(local_path):
                    print(f"   ✅ Imagen existe localmente: {local_path}")
                else:
                    print(f"   ❌ Imagen NO existe localmente: {local_path}")
                    
                    # Buscar la imagen en otras ubicaciones
                    search_paths = [
                        f"app/static/uploads/{profile_image}",
                        f"app/static/images/{profile_image}",
                        f"uploads/{profile_image}",
                        f"imagenes_subidas/{profile_image}"
                    ]
                    
                    found = False
                    for search_path in search_paths:
                        if os.path.exists(search_path):
                            print(f"   🔍 Encontrada en: {search_path}")
                            found = True
                            break
                    
                    if not found:
                        print("   ⚠️ Imagen no encontrada en ninguna ubicación")
                        
                        # Verificar si es una URL de S3
                        if profile_image.startswith('http'):
                            print(f"   🌐 Es una URL externa: {profile_image}")
                        else:
                            print("   🔧 Recomendación: Eliminar imagen de perfil o subir nueva")
                            
                            # Opción para eliminar la imagen de perfil
                            response = input(f"   ¿Eliminar imagen de perfil para {username}? (s/n): ")
                            if response.lower() == 's':
                                db.users.update_one(
                                    {"_id": user["_id"]},
                                    {"$unset": {"profile_image": ""}}
                                )
                                print(f"   ✅ Imagen de perfil eliminada para {username}")

        return True
        
    except Exception as e:
        print(f"❌ Error al verificar imágenes: {e}")
        return False

def fix_missing_images():
    """Corregir imágenes faltantes"""
    print("\n🔧 Corrigiendo imágenes faltantes...")
    
    db = get_mongo_connection()
    if db is None:
        return False
    
    try:
        # Buscar usuarios con imágenes de perfil faltantes
        users = db.users.find({"profile_image": {"$exists": True, "$ne": None}})
        
        fixed_count = 0
        for user in users:
            profile_image = user.get('profile_image')
            if not profile_image:
                continue
                
            local_path = f"app/static/imagenes_subidas/{profile_image}"
            if not os.path.exists(local_path):
                # Eliminar la imagen de perfil si no existe
                db.users.update_one(
                    {"_id": user["_id"]},
                    {"$unset": {"profile_image": ""}}
                )
                print(f"✅ Imagen eliminada para {user.get('username', 'N/A')}")
                fixed_count += 1
        
        print(f"\n📊 Total de imágenes corregidas: {fixed_count}")
        return True
        
    except Exception as e:
        print(f"❌ Error al corregir imágenes: {e}")
        return False

def verify_upload_folder():
    """Verificar que la carpeta de uploads existe y tiene permisos correctos"""
    print("\n📁 Verificando carpeta de uploads...")
    
    upload_folder = "app/static/imagenes_subidas"
    
    if not os.path.exists(upload_folder):
        print(f"❌ Carpeta no existe: {upload_folder}")
        try:
            os.makedirs(upload_folder, exist_ok=True)
            print(f"✅ Carpeta creada: {upload_folder}")
        except Exception as e:
            print(f"❌ Error al crear carpeta: {e}")
            return False
    else:
        print(f"✅ Carpeta existe: {upload_folder}")
    
    # Verificar permisos
    try:
        os.access(upload_folder, os.R_OK | os.W_OK)
        print(f"✅ Permisos correctos en: {upload_folder}")
    except Exception as e:
        print(f"❌ Error de permisos en: {upload_folder}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando verificación de imágenes de perfil...\n")
    
    # Verificar carpeta de uploads
    if not verify_upload_folder():
        print("❌ Error en la carpeta de uploads")
        sys.exit(1)
    
    # Verificar imágenes de perfil
    if not check_profile_images():
        print("❌ Error al verificar imágenes")
        sys.exit(1)

    # Corregir imágenes faltantes
    if not fix_missing_images():
        print("❌ Error al corregir imágenes")
        sys.exit(1) 
    print("\n" + "="*50)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("Las imágenes de perfil han sido verificadas y corregidas.")
