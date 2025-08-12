#!/usr/bin/env python3
# Descripción: Migración simple de imágenes a S3
"""
Script simple para migrar imágenes locales a S3
"""

import os
import boto3
from dotenv import load_dotenv

def migrate_images_to_s3():
    """Migra imágenes locales a S3"""
    
    print("🚀 MIGRANDO IMÁGENES LOCALES A S3")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Configuración S3
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'eu-central-1')
    s3_bucket = os.environ.get('S3_BUCKET_NAME', 'edf-catalogo-tablas')
    
    if not aws_access_key or not aws_secret_key:
        print("   ❌ Credenciales AWS no encontradas")
        return False
    
    # Crear cliente S3
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        print(f"   ✅ Cliente S3 creado")
        print(f"   📦 Bucket: {s3_bucket}")
        print(f"   🌍 Región: {aws_region}")
    except Exception as e:
        print(f"   ❌ Error creando cliente S3: {e}")
        return False
    
    # Directorio local
    local_path = "/var/www/vhosts/edefrutos2025.xyz/httpdocs/app/static/imagenes_subidas"
    
    if not os.path.exists(local_path):
        print(f"   ❌ Directorio local no existe: {local_path}")
        return False
    
    # Listar archivos
    files = [f for f in os.listdir(local_path) 
            if not f.startswith('.') and os.path.isfile(os.path.join(local_path, f))]
    
    print(f"   📄 Total de archivos a migrar: {len(files)}")
    
    if not files:
        print(f"   ✅ No hay archivos para migrar")
        return True
    
    # Migrar archivos
    stats = {'total': len(files), 'uploaded': 0, 'errors': 0}
    
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(local_path, filename)
        print(f"\n   📤 [{i}/{len(files)}] Migrando: {filename}")
        
        try:
            # Subir a S3
            s3_client.upload_file(file_path, s3_bucket, filename)
            
            # Generar URL
            url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{filename}"
            
            stats['uploaded'] += 1
            print(f"      ✅ Subido a S3: {url}")
            
        except Exception as e:
            stats['errors'] += 1
            print(f"      ❌ Error: {e}")
    
    # Resultados
    print(f"\n🎉 MIGRACIÓN COMPLETADA")
    print(f"   📊 Total: {stats['total']}")
    print(f"   ✅ Subidos: {stats['uploaded']}")
    print(f"   ❌ Errores: {stats['errors']}")
    
    if stats['uploaded'] > 0:
        print(f"\n💡 RECOMENDACIONES:")
        print(f"   • Las imágenes ahora se sirven desde S3")
        print(f"   • Puedes eliminar archivos locales para liberar espacio")
        print(f"   • El sistema usa S3 como principal y local como fallback")
    
    return stats['errors'] == 0

if __name__ == "__main__":
    migrate_images_to_s3()
