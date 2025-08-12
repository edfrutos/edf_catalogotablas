#!/usr/bin/env python3
"""
Script para eliminar la imagen de perfil problemática
"""

from pymongo import MongoClient
import os

def get_mongo_connection():
    """Obtener conexión a MongoDB"""
    try:
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

def remove_broken_profile_image():
    """Eliminar la imagen de perfil problemática"""
    print("🔧 Eliminando imagen de perfil problemática...")
    
    db = get_mongo_connection()
    if db is None:
        return False
    
    try:
        # Buscar usuario por email
        user_email = "raul@gmail.com"
        user = db.users.find_one({"email": user_email})
        
        if not user:
            print(f"❌ Usuario no encontrado: {user_email}")
            return False
        
        print(f"👤 Usuario encontrado: {user.get('username')}")
        print(f"   Imagen actual: {user.get('foto_perfil')}")
        
        # Eliminar la imagen de perfil
        result = db.users.update_one(
            {"email": user_email},
            {"$unset": {"foto_perfil": ""}}
        )
        
        if result.modified_count > 0:
            print("✅ Imagen de perfil eliminada correctamente")
            
            # Verificar que se eliminó
            updated_user = db.users.find_one({"email": user_email})
            print(f"   Nueva imagen: {updated_user.get('foto_perfil')}")
        else:
            print("⚠️ No se pudo eliminar la imagen de perfil")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al eliminar imagen: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando eliminación de imagen problemática...\n")
    
    remove_broken_profile_image()
    
    print("\n" + "="*50)
    print("📊 ELIMINACIÓN COMPLETADA")
    print("La imagen de perfil problemática ha sido eliminada.")
