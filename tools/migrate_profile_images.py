#!/usr/bin/env python3
"""
Script para migrar imágenes de perfil de uploads a imagenes_subidas
"""

import os
import shutil
from pathlib import Path

def migrate_profile_images():
    """Migrar imágenes de perfil de uploads a imagenes_subidas"""
    print("🔄 Migrando imágenes de perfil...")

    # Rutas
    uploads_path = "app/static/uploads"
    imagenes_subidas_path = "app/static/imagenes_subidas"
    
    # Verificar que existe la carpeta de uploads
    if not os.path.exists(uploads_path):
        print(f"❌ Carpeta de uploads no existe: {uploads_path}")
        return False
    
    # Verificar que existe la carpeta de imagenes_subidas
    if not os.path.exists(imagenes_subidas_path):
        print(f"❌ Carpeta de imagenes_subidas no existe: {imagenes_subidas_path}")
        return False
    
    print(f"✅ Carpeta de uploads: {uploads_path}")
    print(f"✅ Carpeta de imagenes_subidas: {imagenes_subidas_path}")
    
    # Listar archivos en uploads
    uploads_files = os.listdir(uploads_path)
    print(f"\n📁 Archivos en uploads: {len(uploads_files)}")
    
    # Filtrar solo imágenes
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    image_files = [
        f for f in uploads_files 
        if Path(f).suffix.lower() in image_extensions
    ]
    
    print(f"📸 Imágenes encontradas: {len(image_files)}")
    
    # Migrar imágenes
    migrated_count = 0
    for image_file in image_files:
        source_path = os.path.join(uploads_path, image_file)
        dest_path = os.path.join(imagenes_subidas_path, image_file)
        
        # Verificar si ya existe en destino
        if os.path.exists(dest_path):
            print(f"⚠️ Ya existe en destino: {image_file}")
            continue
        
        try:
            # Copiar archivo
            shutil.copy2(source_path, dest_path)
            print(f"✅ Migrada: {image_file}")
            migrated_count += 1
        except Exception as e:
            print(f"❌ Error migrando {image_file}: {e}")
    
    print(f"\n📊 Total de imágenes migradas: {migrated_count}")
    
    # Verificar archivos duplicados
    print("\n🔍 Verificando duplicados...")
    imagenes_subidas_files = os.listdir(imagenes_subidas_path)
    image_files_subidas = [
        f for f in imagenes_subidas_files 
        if Path(f).suffix.lower() in image_extensions
    ]
    
    print(f"📸 Imágenes en imagenes_subidas: {len(image_files_subidas)}")
    
    return True

def update_database_references():
    """Actualizar referencias en la base de datos"""
    print("\n🗄️ Actualizando referencias en la base de datos...")
    
    try:
        from pymongo import MongoClient
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        mongo_uri = os.getenv('MONGO_URI')
        
        if not mongo_uri:
            print("❌ MONGO_URI no encontrada")
            return False
        
        client = MongoClient(mongo_uri)
        db = client.get_default_database()
        
        # Buscar usuarios con imágenes de perfil
        users = db.users.find({"foto_perfil": {"$exists": True, "$ne": None}})
        

        for user in users:
            foto_perfil = user.get('foto_perfil')
            if foto_perfil:
                # Verificar si la imagen existe en imagenes_subidas
                imagenes_path = f"app/static/imagenes_subidas/{foto_perfil}"
                if os.path.exists(imagenes_path):
                    print(f"✅ Usuario {user.get('username', 'N/A')}: imagen existe en imagenes_subidas")
                else:
                    print(f"⚠️ Usuario {user.get('username', 'N/A')}: imagen no existe en imagenes_subidas")
        
        print("📊 Usuarios verificados")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando base de datos: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando migración de imágenes de perfil...\n")
    
    # Migrar imágenes
    if not migrate_profile_images():
        print("❌ Error en la migración")
        exit(1)
    
    # Actualizar referencias en BD
    if not update_database_references():
        print("❌ Error actualizando base de datos")
        exit(1)
    
    print("\n" + "="*50)
    print("✅ MIGRACIÓN COMPLETADA")
    print("Las imágenes de perfil han sido migradas correctamente.")