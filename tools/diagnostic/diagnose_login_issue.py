#!/usr/bin/env python3
# Descripción: Diagnostica problemas de login y autenticación
"""
Script para diagnosticar problemas de login
"""

import os
import sys
from dotenv import load_dotenv

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_login_issue():
    """Diagnostica problemas de login"""
    
    print("🔍 DIAGNOSTICANDO PROBLEMA DE LOGIN")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    try:
        # Importar la aplicación Flask
        from main_app import create_app
        
        # Crear la aplicación
        app = create_app()
        
        with app.app_context():
            # Importar funciones de base de datos
            from app.database import get_mongo_db
            
            # Obtener la base de datos
            db = get_mongo_db()
            if db is None:
                print("   ❌ No se pudo conectar a la base de datos")
                return False
            
            print("   ✅ Conexión a MongoDB exitosa")
            
            # Verificar configuración de MongoDB
            mongo_uri = os.getenv('MONGO_URI')
            if mongo_uri:
                print(f"   📋 MONGO_URI configurado: {mongo_uri[:50]}...")
            else:
                print("   ❌ MONGO_URI no configurado")
            
            # Verificar colección de usuarios
            try:
                users_collection = db["users"]
                user_count = users_collection.count_documents({})
                print(f"   👥 Usuarios en la base de datos: {user_count}")
                
                if user_count > 0:
                    # Mostrar algunos usuarios (sin contraseñas)
                    users = list(users_collection.find({}, {"username": 1, "email": 1, "_id": 0}).limit(5))
                    print("   📋 Usuarios disponibles:")
                    for user in users:
                        username = user.get("username", "Sin username")
                        email = user.get("email", "Sin email")
                        print(f"      - Username: {username}, Email: {email}")
                else:
                    print("   ⚠️  No hay usuarios en la base de datos")
                    
            except Exception as e:
                print(f"   ❌ Error accediendo a colección de usuarios: {e}")
            
            # Verificar configuración de la aplicación
            print(f"\n" + "="*50)
            print("CONFIGURACIÓN DE LA APLICACIÓN")
            print("="*50)
            
            secret_key = app.config.get('SECRET_KEY')
            if secret_key:
                print(f"   ✅ SECRET_KEY configurado: {secret_key[:20]}...")
            else:
                print("   ❌ SECRET_KEY no configurado")
            
            debug_mode = app.config.get('DEBUG', False)
            print(f"   🔧 Modo DEBUG: {debug_mode}")
            
            # Verificar variables de entorno críticas
            print(f"\n" + "="*50)
            print("VARIABLES DE ENTORNO")
            print("="*50)
            
            critical_vars = [
                'MONGO_URI',
                'SECRET_KEY',
                'FLASK_ENV',
                'AWS_ACCESS_KEY_ID',
                'AWS_SECRET_ACCESS_KEY',
                'S3_BUCKET_NAME'
            ]
            
            for var in critical_vars:
                value = os.getenv(var)
                if value:
                    if 'SECRET' in var or 'KEY' in var:
                        print(f"   ✅ {var}: {value[:20]}...")
                    else:
                        print(f"   ✅ {var}: {value}")
                else:
                    print(f"   ❌ {var}: No configurado")
            
            # Verificar estado del servicio
            print(f"\n" + "="*50)
            print("ESTADO DEL SERVICIO")
            print("="*50)
            
            try:
                import requests
                response = requests.get("http://127.0.0.1:8000/", timeout=5)
                print(f"   ✅ Servicio local respondiendo: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Servicio local no responde: {e}")
            
            try:
                response = requests.get("https://edefrutos2025.xyz/", timeout=10)
                print(f"   ✅ Servicio producción respondiendo: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Servicio producción no responde: {e}")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    
    print("🚀 INICIANDO DIAGNÓSTICO DE PROBLEMA DE LOGIN")
    print("=" * 60)
    
    # Ejecutar diagnóstico
    success = diagnose_login_issue()
    
    if success:
        print(f"\n🎉 Diagnóstico completado")
        print(f"💡 Revisa los resultados para identificar el problema")
        return True
    else:
        print(f"\n❌ El diagnóstico no se completó correctamente")
        return False

if __name__ == "__main__":
    main()
