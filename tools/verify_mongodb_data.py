#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_mongodb_data():
    print("🔍 Verificando datos en MongoDB...")
    
    try:
        from app import create_app
        from app.database import get_mongo_db, is_connected
        
        app = create_app()
        
        with app.app_context():
            if not is_connected():
                print("❌ No hay conexión a MongoDB")
                return False
            
            db = get_mongo_db()
            
            # Verificar colecciones
            collections = db.list_collection_names()
            print(f"📚 Colecciones disponibles: {collections}")
            
            # Verificar usuarios
            users_collection = db.users
            user_count = users_collection.count_documents({})
            print(f"👥 Usuarios en la base de datos: {user_count}")
            
            if user_count > 0:
                # Mostrar un usuario de ejemplo
                sample_user = users_collection.find_one({}, {'email': 1, 'username': 1, '_id': 0})
                if sample_user:
                    print(f"📋 Usuario de ejemplo: {sample_user}")
            
            # Verificar catálogos
            catalogs_collection = db.catalogs
            catalog_count = catalogs_collection.count_documents({})
            print(f"📖 Catálogos en la base de datos: {catalog_count}")
            
            # Verificar tokens de reset
            tokens_collection = db.reset_tokens
            token_count = tokens_collection.count_documents({})
            print(f"🔑 Tokens de reset: {token_count}")
            
            print("✅ Verificación completada - MongoDB está funcionando correctamente")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = verify_mongodb_data()
    print("✅ DATOS ACCESIBLES" if success else "❌ ERROR")
    sys.exit(0 if success else 1)
