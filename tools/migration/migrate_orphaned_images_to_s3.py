#!/usr/bin/env python3
"""
Script para migrar imágenes huérfanas a S3 y crear referencias en la base de datos
"""

import os
import sys
from dotenv import load_dotenv

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_orphaned_images_to_s3():
    """Migra imágenes huérfanas a S3 y crea referencias en la base de datos"""
    
    print("🔄 MIGRANDO IMÁGENES HUÉRFANAS A S3")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    try:
        # Importar la aplicación Flask
        from main_app import create_app
        
        # Crear la aplicación
        app = create_app()
        
        with app.app_context():
            # Importar funciones de base de datos y S3
            from app.database import get_mongo_db
            from app.utils.s3_utils import upload_file_to_s3
            
            # Obtener la base de datos
            db = get_mongo_db()
            if db is None:
                print("   ❌ No se pudo conectar a la base de datos")
                return False
            
            # Obtener archivos físicos
            upload_dir = os.path.join(app.static_folder, 'uploads')
            physical_files = []
            
            if os.path.exists(upload_dir):
                for filename in os.listdir(upload_dir):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                        physical_files.append(filename)
            
            print(f"   📁 Archivos físicos encontrados: {len(physical_files)}")
            
            # Obtener referencias existentes en la base de datos
            collection = db["spreadsheets"]
            catalogs = list(collection.find({}))
            
            db_references = []
            for catalog in catalogs:
                rows = catalog.get("rows", [])
                for row in rows:
                    images = row.get("images", [])
                    db_references.extend(images)
            
            # Identificar archivos huérfanos
            orphaned_files = [f for f in physical_files if f not in db_references]
            print(f"   📁 Archivos huérfanos identificados: {len(orphaned_files)}")
            
            if not orphaned_files:
                print("   ✅ No hay archivos huérfanos para migrar")
                return True
            
            # Crear un catálogo temporal para las imágenes huérfanas
            temp_catalog_name = "Imágenes Huérfanas - " + datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Migrar archivos a S3
            migrated_images = []
            failed_migrations = []
            
            print(f"   🔄 Migrando archivos a S3...")
            
            for i, filename in enumerate(orphaned_files):
                file_path = os.path.join(upload_dir, filename)
                
                if not os.path.exists(file_path):
                    print(f"      ⚠️  Archivo no encontrado: {filename}")
                    failed_migrations.append(filename)
                    continue
                
                try:
                    # Subir a S3
                    s3_result = upload_file_to_s3(file_path, filename)
                    
                    if s3_result.get('success'):
                        migrated_images.append(filename)
                        print(f"      ✅ [{i+1}/{len(orphaned_files)}] Migrado: {filename}")
                        
                        # Eliminar archivo local después de subir a S3
                        os.remove(file_path)
                    else:
                        print(f"      ❌ [{i+1}/{len(orphaned_files)}] Error S3: {filename} - {s3_result.get('error')}")
                        failed_migrations.append(filename)
                        
                except Exception as e:
                    print(f"      ❌ [{i+1}/{len(orphaned_files)}] Error: {filename} - {e}")
                    failed_migrations.append(filename)
            
            # Crear catálogo con las imágenes migradas
            if migrated_images:
                print(f"   📋 Creando catálogo con {len(migrated_images)} imágenes...")
                
                # Crear filas para el catálogo (máximo 10 imágenes por fila)
                rows = []
                for i in range(0, len(migrated_images), 10):
                    batch = migrated_images[i:i+10]
                    row = {
                        "images": batch,
                        "nota": f"Lote {i//10 + 1} de imágenes migradas automáticamente"
                    }
                    rows.append(row)
                
                # Crear el catálogo
                catalog_data = {
                    "name": temp_catalog_name,
                    "description": f"Catálogo automático con {len(migrated_images)} imágenes huérfanas migradas a S3",
                    "headers": ["images", "nota"],
                    "rows": rows,
                    "data": rows,  # Mantener compatibilidad
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "is_auto_generated": True
                }
                
                try:
                    result = collection.insert_one(catalog_data)
                    if result.inserted_id:
                        print(f"   ✅ Catálogo creado con ID: {result.inserted_id}")
                        print(f"   📊 {len(rows)} filas creadas con {len(migrated_images)} imágenes")
                    else:
                        print(f"   ❌ Error al crear catálogo")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ Error al crear catálogo: {e}")
                    return False
            
            # Imprimir estadísticas finales
            print(f"\n" + "="*50)
            print("ESTADÍSTICAS DE MIGRACIÓN")
            print("="*50)
            print(f"Total archivos procesados: {len(orphaned_files)}")
            print(f"Migraciones exitosas: {len(migrated_images)}")
            print(f"Migraciones fallidas: {len(failed_migrations)}")
            print(f"Archivos locales eliminados: {len(migrated_images)}")
            
            if failed_migrations:
                print(f"\n⚠️  ARCHIVOS CON ERRORES:")
                for filename in failed_migrations[:10]:
                    print(f"   - {filename}")
                if len(failed_migrations) > 10:
                    print(f"   ... y {len(failed_migrations) - 10} más")
            
            if migrated_images:
                print(f"\n✅ MIGRACIÓN COMPLETADA")
                print(f"   📋 Catálogo creado: '{temp_catalog_name}'")
                print(f"   🗄️  {len(migrated_images)} imágenes ahora referenciadas en la base de datos")
                print(f"   💾 Espacio liberado en servidor local")
                return True
            else:
                print(f"\n❌ No se pudo migrar ninguna imagen")
                return False
            
    except Exception as e:
        print(f"   ❌ Error en migración: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    
    print("🚀 INICIANDO MIGRACIÓN DE IMÁGENES HUÉRFANAS")
    print("=" * 60)
    
    # Importar datetime aquí para evitar problemas de importación
    global datetime
    from datetime import datetime
    
    # Ejecutar migración
    success = migrate_orphaned_images_to_s3()
    
    if success:
        print(f"\n🎉 Migración completada exitosamente")
        print(f"💡 Las imágenes huérfanas ahora están en S3 y referenciadas en la base de datos")
        return True
    else:
        print(f"\n❌ La migración no se completó correctamente")
        return False

if __name__ == "__main__":
    main()
