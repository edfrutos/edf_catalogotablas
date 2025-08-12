#!/usr/bin/env python3
# Descripción: Verifica el acceso y estado de imágenes en S3
"""
Script para verificar qué imágenes están disponibles en S3
"""

import os
import sys
from dotenv import load_dotenv

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_s3_images():
    """Verifica qué imágenes están disponibles en S3"""
    
    print("🔍 VERIFICANDO IMÁGENES EN S3")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    try:
        # Importar la aplicación Flask
        from main_app import create_app
        
        # Crear la aplicación
        app = create_app()
        
        with app.app_context():
            # Importar funciones necesarias
            from app.utils.s3_utils import get_s3_url, list_s3_objects
            
            print(f"\n☁️  VERIFICANDO BUCKET S3:")
            
            # Listar objetos en S3
            try:
                objects = list_s3_objects()
                if objects:
                    print(f"   📄 Objetos encontrados en S3: {len(objects)}")
                    print(f"   📋 Primeros 10 objetos:")
                    for i, obj in enumerate(objects[:10]):
                        print(f"      {i+1}. {obj}")
                else:
                    print(f"   ❌ No se encontraron objetos en S3")
            except Exception as e:
                print(f"   ❌ Error listando objetos S3: {e}")
            
            # Probar algunas imágenes específicas
            test_images = [
                "64a792c06c434f1c845c3c6954ab572a_breathtakinghermosamujerirl_26781173.png",
                "7903341a544d40218c77ad020c21b4bc_Miguel_Angel_y_yo_de_ninos.jpg",
                "3f75f6c5822d4f40aacc1667c7bf0024_cinematicphotohermosamujer_94172462.png"
            ]
            
            print(f"\n🧪 PROBANDO IMÁGENES ESPECÍFICAS:")
            for image in test_images:
                try:
                    s3_url = get_s3_url(image)
                    if s3_url:
                        print(f"   ✅ {image} → {s3_url}")
                    else:
                        print(f"   ❌ {image} → No encontrada en S3")
                except Exception as e:
                    print(f"   ❌ {image} → Error: {e}")
            
            return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_catalog_images():
    """Verifica las imágenes de catálogos en la base de datos"""
    
    print(f"\n📊 VERIFICANDO IMÁGENES DE CATÁLOGOS EN BD")
    print("=" * 50)
    
    try:
        # Importar la aplicación Flask
        from main_app import create_app
        
        # Crear la aplicación
        app = create_app()
        
        with app.app_context():
            # Importar funciones necesarias
            from app.models import get_mongo_db
            
            db = get_mongo_db()
            if db:
                # Buscar catálogos con imágenes
                catalogs = db["67b8c24a7fdc72dd4d8703cf"].find({})
                
                catalog_count = 0
                image_count = 0
                
                for catalog in catalogs:
                    catalog_count += 1
                    if "rows" in catalog:
                        for row in catalog["rows"]:
                            if "imagenes" in row and row["imagenes"]:
                                image_count += len(row["imagenes"])
                                print(f"   📄 Catálogo '{catalog.get('name', 'Sin nombre')}':")
                                for img in row["imagenes"]:
                                    print(f"      - {img}")
                
                print(f"\n📈 RESUMEN:")
                print(f"   📊 Catálogos revisados: {catalog_count}")
                print(f"   🖼️  Imágenes encontradas: {image_count}")
            
            return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    
    print("🚀 VERIFICANDO SISTEMA DE IMÁGENES")
    print("=" * 50)
    
    # Verificar S3
    s3_success = check_s3_images()
    
    # Verificar catálogos
    catalog_success = check_catalog_images()
    
    print(f"\n🎉 VERIFICACIÓN COMPLETADA")
    print("=" * 50)
    
    if s3_success and catalog_success:
        print(f"   ✅ Verificación completada exitosamente")
        return True
    else:
        print(f"   ❌ Error en la verificación")
        return False

if __name__ == "__main__":
    main()
