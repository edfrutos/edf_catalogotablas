#!/usr/bin/env python3
# Descripción: Configura S3 para acceso público
"""
Script para configurar el bucket S3 con acceso público
"""

import boto3
import json
from dotenv import load_dotenv
import os

def configurar_s3_publico():
    """Configura el bucket S3 para acceso público"""
    
    print("🔧 CONFIGURANDO S3 PARA ACCESO PÚBLICO")
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
        
        # 1. Configurar política de bucket para acceso público
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
        s3_client.put_bucket_policy(
            Bucket=s3_bucket,
            Policy=json.dumps(bucket_policy)
        )
        print(f"      ✅ Política de bucket configurada")
        
        # 2. Configurar CORS para acceso web
        cors_configuration = {
            'CORSRules': [{
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'HEAD'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': []
            }]
        }
        
        print(f"   🌐 Configurando CORS...")
        s3_client.put_bucket_cors(
            Bucket=s3_bucket,
            CORSConfiguration=cors_configuration
        )
        print(f"      ✅ CORS configurado")
        
        # 3. Verificar configuración
        print(f"\n   🔍 Verificando configuración...")
        try:
            response = s3_client.head_object(
                Bucket=s3_bucket,
                Key='3f75f6c5822d4f40aacc1667c7bf0024_cinematicphotohermosamujer_94172462.png'
            )
            print(f"      ✅ Objeto accesible desde S3")
        except Exception as e:
            print(f"      ⚠️  Objeto no accesible: {e}")
        
        print(f"\n🎉 CONFIGURACIÓN COMPLETADA")
        print(f"   📦 Bucket configurado para acceso público")
        print(f"   🌐 CORS habilitado para acceso web")
        print(f"   🔗 URLs públicas disponibles")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    configurar_s3_publico()
