#!/usr/bin/env python3
# Descripción: Verifica el perfil de usuario y sus imágenes
"""
Script para verificar la configuración de foto de perfil del usuario
"""

import os
import sys
from dotenv import load_dotenv

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_user_profile():
    """Verifica la configuración de foto de perfil del usuario"""
    
    print("🔍 VERIFICANDO CONFIGURACIÓN DE FOTO DE PERFIL")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    try:
        # Importar la aplicación Flask
        from main_app import create_app
        
        # Crear la aplicación
        app = create_app()
        
        with app.app_context():
            # Importar funciones necesarias
            from app.models import get_users_collection
            
            # Buscar el usuario edefrutos
            users_collection = get_users_collection()
            user = users_collection.find_one({"email": "edfrutos@gmail.com"})
            
            if user:
                print(f"\n👤 USUARIO ENCONTRADO:")
                print(f"   📧 Email: {user.get('email')}")
                print(f"   👤 Usuario: {user.get('username')}")
                print(f"   📸 Foto de perfil: {user.get('foto_perfil', 'No configurada')}")
                print(f"   🆔 ID: {user.get('_id')}")
                
                # Verificar si la imagen existe
                foto_perfil = user.get('foto_perfil')
                if foto_perfil:
                    # Verificar en imagenes_subidas
                    imagenes_path = "app/static/imagenes_subidas"
                    if os.path.exists(os.path.join(imagenes_path, foto_perfil)):
                        print(f"   ✅ Imagen encontrada en: {imagenes_path}/{foto_perfil}")
                    else:
                        print(f"   ❌ Imagen NO encontrada en: {imagenes_path}/{foto_perfil}")
                        
                        # Buscar la imagen en otras ubicaciones
                        print(f"\n🔍 BUSCANDO IMAGEN EN OTRAS UBICACIONES:")
                        for root, dirs, files in os.walk("app/static"):
                            if foto_perfil in files:
                                print(f"   ✅ Encontrada en: {root}/{foto_perfil}")
                                break
                        else:
                            print(f"   ❌ No se encontró la imagen en ningún lugar")
                else:
                    print(f"   ⚠️  No hay foto de perfil configurada")
                    
                    # Mostrar imágenes disponibles
                    print(f"\n📸 IMÁGENES DISPONIBLES EN imagenes_subidas:")
                    imagenes_path = "app/static/imagenes_subidas"
                    if os.path.exists(imagenes_path):
                        for file in os.listdir(imagenes_path):
                            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                                print(f"   - {file}")
                    else:
                        print(f"   ❌ Directorio {imagenes_path} no existe")
                
                return True
            else:
                print(f"   ❌ Usuario no encontrado")
                return False
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    
    print("🚀 VERIFICANDO CONFIGURACIÓN DE PERFIL")
    print("=" * 60)
    
    # Ejecutar verificación
    success = check_user_profile()
    
    if success:
        print(f"\n🎉 Verificación completada")
        return True
    else:
        print(f"\n❌ Error en la verificación")
        return False

if __name__ == "__main__":
    main()
