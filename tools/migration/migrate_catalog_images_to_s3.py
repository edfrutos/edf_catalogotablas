#!/usr/bin/env python3
"""
Script para migrar imágenes de catálogos a S3
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from pymongo import MongoClient
import certifi

# Cargar variables de entorno
load_dotenv()

# Configurar certificado SSL
os.environ['SSL_CERT_FILE'] = certifi.where()

# Configuración de MongoDB
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print("Error: MONGO_URI environment variable not set")
    sys.exit(1)

# Configuración de AWS S3
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME]):
    print("Error: One or more AWS environment variables not set")
    print("Required: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME")
    sys.exit(1)

# Conectar a MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client["app_catalogojoyero_nueva"]
    collection = db["spreadsheets"]  # Colección correcta
    print(f"Connected to MongoDB: {client.server_info()['version']}")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    sys.exit(1)

# Inicializar cliente S3
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    print(f"Connected to AWS S3 in region {AWS_REGION}")
except ClientError as e:
    print(f"Error connecting to AWS S3: {e}")
    sys.exit(1)

# Ruta al directorio de imágenes
UPLOAD_FOLDER = Path("app/static/uploads")
if not UPLOAD_FOLDER.exists():
    print(f"Error: Directory {UPLOAD_FOLDER} does not exist")
    sys.exit(1)

def upload_file_to_s3(file_path, object_name=None):
    """Sube un archivo a S3"""
    if object_name is None:
        object_name = os.path.basename(file_path)
        
    try:
        s3_client.upload_file(file_path, S3_BUCKET_NAME, object_name)
        return True
    except ClientError as e:
        print(f"Error uploading file {file_path} to S3: {e}")
        return False

def migrate_catalog_images():
    """Migra todas las imágenes de catálogos a S3"""
    
    # Estadísticas
    total_catalogs = 0
    catalogs_with_images = 0
    total_images = 0
    images_migrated = 0
    images_failed = 0
    images_not_found = 0
    
    print(f"Starting migration of catalog images to S3 bucket: {S3_BUCKET_NAME}")
    
    # Obtener todos los catálogos
    catalogs = list(collection.find({}))
    total_catalogs = len(catalogs)
    
    print(f"Found {total_catalogs} catalogs")
    
    # Procesar cada catálogo
    for catalog in catalogs:
        catalog_id = catalog.get("_id")
        catalog_name = catalog.get("name", "Sin nombre")
        rows = catalog.get("rows", [])
        
        catalog_has_images = False
        
        print(f"\nProcessing catalog: {catalog_name} (ID: {catalog_id})")
        
        # Procesar cada fila del catálogo
        for row_index, row in enumerate(rows):
            images = row.get("images", [])
            
            if not images:
                continue
                
            catalog_has_images = True
            print(f"  Row {row_index + 1}: {len(images)} images")
            
            # Procesar cada imagen
            updated_images = []
            for img in images:
                total_images += 1
                
                # Verificar si ya está en S3
                if img.startswith("s3://") or "s3.amazonaws.com" in img:
                    print(f"    Image already in S3: {img}")
                    updated_images.append(img)
                    continue
                
                # Buscar archivo físico
                img_path = UPLOAD_FOLDER / img
                
                if not img_path.exists():
                    print(f"    ❌ Image not found: {img}")
                    images_not_found += 1
                    continue
                
                # Subir a S3
                print(f"    📤 Uploading to S3: {img}")
                if upload_file_to_s3(str(img_path), img):
                    # Actualizar ruta a S3
                    s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{img}"
                    updated_images.append(s3_url)
                    images_migrated += 1
                    print(f"    ✅ Uploaded successfully: {s3_url}")
                else:
                    print(f"    ❌ Upload failed: {img}")
                    images_failed += 1
                    updated_images.append(img)  # Mantener ruta original
            
            # Actualizar la fila con las nuevas rutas
            if updated_images != images:
                try:
                    collection.update_one(
                        {"_id": catalog_id},
                        {"$set": {f"rows.{row_index}.images": updated_images}}
                    )
                    print(f"    ✅ Row updated in database")
                except Exception as e:
                    print(f"    ❌ Error updating row: {e}")
        
        if catalog_has_images:
            catalogs_with_images += 1
    
    # Imprimir estadísticas
    print(f"\n" + "="*50)
    print("MIGRATION STATISTICS")
    print("="*50)
    print(f"Total catalogs: {total_catalogs}")
    print(f"Catalogs with images: {catalogs_with_images}")
    print(f"Total images processed: {total_images}")
    print(f"Images successfully migrated: {images_migrated}")
    print(f"Images not found in filesystem: {images_not_found}")
    print(f"Images failed to upload: {images_failed}")
    print("="*50)
    
    if images_migrated > 0:
        print("✅ Migration completed successfully")
        return True
    else:
        print("⚠️  No images were migrated")
        return False

def main():
    """Función principal"""
    
    print("🚀 INICIANDO MIGRACIÓN DE IMÁGENES DE CATÁLOGOS A S3")
    print("=" * 60)
    
    # Verificar que el bucket existe
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        print(f"✅ Bucket {S3_BUCKET_NAME} exists and is accessible")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ Bucket {S3_BUCKET_NAME} does not exist")
            return False
        elif error_code == '403':
            print(f"❌ Access denied to bucket {S3_BUCKET_NAME}")
            return False
        else:
            print(f"❌ Error accessing bucket: {error_code}")
            return False
    
    # Ejecutar migración
    success = migrate_catalog_images()
    
    if success:
        print(f"\n🎉 Migración completada exitosamente")
        print(f"💡 Las imágenes ahora están disponibles en S3")
        return True
    else:
        print(f"\n❌ La migración no se completó correctamente")
        return False

if __name__ == "__main__":
    main()
