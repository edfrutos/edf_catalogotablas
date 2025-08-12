#!/usr/bin/env python3
"""
Script para migrar imágenes locales a S3
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_images_to_s3():
    """Migra todas las imágenes locales a S3"""
    
    print("🚀 MIGRANDO IMÁGENES LOCALES A S3")
    print("=" * 50)
    
    load_dotenv()
    
    try:
        from main_app import create_app
        from app.utils.image_manager import image_manager
        
        app = create_app()
        
        with app.app_context():
            # Verificar configuración S3
            s3_client = image_manager.s3_client
            if not s3_client:
                print(f"   ❌ Cliente S3 no disponible")
                return False
            
            print(f"   ✅ Cliente S3 disponible")
            print(f"   📦 Bucket: {image_manager.s3_bucket}")
            
            # Verificar directorio local
            local_path = image_manager.local_path
            if not os.path.exists(local_path):
                print(f"   ❌ Directorio local no existe: {local_path}")
                return False
            
            files = [f for f in os.listdir(local_path) 
                    if not f.startswith('.') and os.path.isfile(os.path.join(local_path, f))]
            
            print(f"   📄 Total de archivos a migrar: {len(files)}")
            
            if not files:
                print(f"   ✅ No hay archivos para migrar")
                return True
            
            stats = {'total': len(files), 'uploaded': 0, 'errors': 0}
            
            for i, filename in enumerate(files, 1):
                file_path = os.path.join(local_path, filename)
                print(f"\n   📤 [{i}/{len(files)}] Migrando: {filename}")
                
                try:
                    # Usar directamente S3 para migración
                    from app.utils.s3_utils import upload_file_to_s3
                    s3_result = upload_file_to_s3(file_path, filename, image_manager.s3_bucket)
                    
                    if s3_result.get('success'):
                        stats['uploaded'] += 1
                        print(f"      ✅ Subido a S3: {s3_result.get('url')}")
                    else:
                        stats['errors'] += 1
                        print(f"      ❌ Error S3: {s3_result.get('error')}")
                        
                except Exception as e:
                    stats['errors'] += 1
                    print(f"      ❌ Exception: {e}")
            
            print(f"\n🎉 MIGRACIÓN COMPLETADA")
            print(f"   📊 Total: {stats['total']}")
            print(f"   ✅ Subidos: {stats['uploaded']}")
            print(f"   ❌ Errores: {stats['errors']}")
            
            return stats['errors'] == 0
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    migrate_images_to_s3()
