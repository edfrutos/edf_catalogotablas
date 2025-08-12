#!/usr/bin/env python3
# Descripción: Migra imágenes existentes a S3
"""
Script para migrar imágenes existentes físicamente a S3
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Cargar variables de entorno
load_dotenv()

# Configuración de AWS S3
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME]):
    print("Error: One or more AWS environment variables not set")
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

def migrate_existing_images():
    """Migra todas las imágenes existentes físicamente a S3"""
    
    print(f"Starting migration of existing images to S3 bucket: {S3_BUCKET_NAME}")
    
    # Listar todos los archivos en el directorio uploads
    image_files = list(UPLOAD_FOLDER.glob("*"))
    total_files = len(image_files)
    
    print(f"Found {total_files} files in {UPLOAD_FOLDER}")
    
    # Estadísticas
    uploaded_count = 0
    failed_count = 0
    
    # Procesar cada archivo
    for i, file_path in enumerate(image_files, 1):
        if file_path.is_file():
            filename = file_path.name
            
            # Verificar si ya existe en S3
            try:
                s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=filename)
                print(f"[{i}/{total_files}] ✅ Already exists in S3: {filename}")
                uploaded_count += 1
                continue
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    # No existe en S3, subirlo
                    pass
                else:
                    print(f"[{i}/{total_files}] ❌ Error checking S3: {filename} - {e}")
                    failed_count += 1
                    continue
            
            # Subir a S3
            print(f"[{i}/{total_files}] 📤 Uploading to S3: {filename}")
            if upload_file_to_s3(str(file_path), filename):
                uploaded_count += 1
                print(f"[{i}/{total_files}] ✅ Uploaded successfully: {filename}")
            else:
                failed_count += 1
                print(f"[{i}/{total_files}] ❌ Upload failed: {filename}")
    
    # Imprimir estadísticas
    print(f"\n" + "="*50)
    print("MIGRATION STATISTICS")
    print("="*50)
    print(f"Total files found: {total_files}")
    print(f"Files uploaded to S3: {uploaded_count}")
    print(f"Files failed to upload: {failed_count}")
    print("="*50)
    
    if uploaded_count > 0:
        print("✅ Migration completed successfully")
        return True
    else:
        print("⚠️  No files were uploaded")
        return False

def main():
    """Función principal"""
    
    print("🚀 INICIANDO MIGRACIÓN DE IMÁGENES EXISTENTES A S3")
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
    success = migrate_existing_images()
    
    if success:
        print(f"\n🎉 Migración completada exitosamente")
        print(f"💡 Todas las imágenes están ahora disponibles en S3")
        print(f"🌐 URLs de ejemplo:")
        print(f"   https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/[filename]")
        return True
    else:
        print(f"\n❌ La migración no se completó correctamente")
        return False

if __name__ == "__main__":
    main()
