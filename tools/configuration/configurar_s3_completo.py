#!/usr/bin/env python3
# Descripción: Configuración completa de S3 incluyendo permisos
"""
Script completo para configurar S3 con acceso público
"""

import boto3
import json
from dotenv import load_dotenv
import os

def configurar_s3_completo():
    """Configura el bucket S3 para acceso público completo"""
    
    print("🔧 CONFIGURACIÓN COMPLETA DE S3 PARA ACCESO PÚBLICO")
    print("=" * 60)
    
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
    
    try:
        # Crear cliente S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        print(f"   ✅ Cliente S3 creado")
        print(f"   📦 Bucket: {s3_bucket}")
        
        # 1. Deshabilitar Block Public Access
        print(f"\n   🔓 Deshabilitando Block Public Access...")
        try:
            s3_client.put_public_access_block(
                Bucket=s3_bucket,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
            print(f"      ✅ Block Public Access deshabilitado")
        except Exception as e:
            print(f"      ⚠️  Error deshabilitando Block Public Access: {e}")
            print(f"      💡 Puede que necesites hacerlo manualmente desde AWS Console")
        
        # 2. Configurar política de bucket para acceso público
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{s3_bucket}/*"
                }
            ]
        }
        
        print(f"\n   📝 Configurando política de bucket...")
        try:
            s3_client.put_bucket_policy(
                Bucket=s3_bucket,
                Policy=json.dumps(bucket_policy)
            )
            print(f"      ✅ Política de bucket configurada")
        except Exception as e:
            print(f"      ❌ Error configurando política: {e}")
            print(f"      💡 Verifica que Block Public Access esté deshabilitado")
            return False
        
        # 3. Configurar CORS para acceso web
        cors_configuration = {
            'CORSRules': [{
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'HEAD'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': []
            }]
        }
        
        print(f"\n   🌐 Configurando CORS...")
        try:
            s3_client.put_bucket_cors(
                Bucket=s3_bucket,
                CORSConfiguration=cors_configuration
            )
            print(f"      ✅ CORS configurado")
        except Exception as e:
            print(f"      ⚠️  Error configurando CORS: {e}")
        
        # 4. Verificar configuración
        print(f"\n   🔍 Verificando configuración...")
        try:
            # Probar acceso público
            import requests
            url = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/3f75f6c5822d4f40aacc1667c7bf0024_cinematicphotohermosamujer_94172462.png"
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                print(f"      ✅ Acceso público funcionando")
                print(f"      🔗 URL de prueba: {url}")
            else:
                print(f"      ⚠️  Acceso público no funciona (Status: {response.status_code})")
        except Exception as e:
            print(f"      ⚠️  Error verificando acceso público: {e}")
        
        print(f"\n🎉 CONFIGURACIÓN COMPLETADA")
        print(f"   📦 Bucket configurado para acceso público")
        print(f"   🌐 CORS habilitado para acceso web")
        print(f"   🔗 URLs públicas disponibles")
        
        print(f"\n💡 INSTRUCCIONES MANUALES (si es necesario):")
        print(f"   1. Ve a AWS S3 Console")
        print(f"   2. Selecciona el bucket: {s3_bucket}")
        print(f"   3. Ve a 'Permissions' → 'Block public access'")
        print(f"   4. Desmarca todas las opciones")
        print(f"   5. Guarda los cambios")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    configurar_s3_completo()
