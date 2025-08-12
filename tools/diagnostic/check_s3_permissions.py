#!/usr/bin/env python3
# Descripción: Verifica los permisos de S3
"""
Script para verificar permisos de S3 y disponibilidad de imágenes
"""

import os
import sys
from dotenv import load_dotenv

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_s3_permissions():
    """Verifica los permisos de S3"""
    
    print("🔍 VERIFICANDO PERMISOS DE S3")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    try:
        # Importar funciones necesarias
        from app.utils.s3_utils import get_s3_client, get_s3_url
        
        print(f"\n📋 CONFIGURACIÓN S3:")
        print(f"   🔑 AWS_ACCESS_KEY_ID: {'✅ Configurado' if os.environ.get('AWS_ACCESS_KEY_ID') else '❌ No configurado'}")
        print(f"   🔑 AWS_SECRET_ACCESS_KEY: {'✅ Configurado' if os.environ.get('AWS_SECRET_ACCESS_KEY') else '❌ No configurado'}")
        print(f"   🌍 AWS_REGION: {os.environ.get('AWS_REGION', 'eu-central-1')}")
        print(f"   🪣 S3_BUCKET_NAME: {os.environ.get('S3_BUCKET_NAME', 'No configurado')}")
        
        # Probar cliente S3
        s3_client = get_s3_client()
        if s3_client:
            print(f"   ✅ Cliente S3 creado exitosamente")
            
            # Probar acceso al bucket
            bucket_name = os.environ.get('S3_BUCKET_NAME')
            if bucket_name:
                try:
                    response = s3_client.head_bucket(Bucket=bucket_name)
                    print(f"   ✅ Acceso al bucket '{bucket_name}' exitoso")
                except Exception as e:
                    print(f"   ❌ Error accediendo al bucket '{bucket_name}': {e}")
            else:
                print(f"   ❌ No se especificó S3_BUCKET_NAME")
        else:
            print(f"   ❌ No se pudo crear el cliente S3")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_s3_images():
    """Prueba imágenes específicas en S3"""
    
    print(f"\n🧪 PROBANDO IMÁGENES EN S3")
    print("=" * 50)
    
    try:
        # Importar funciones necesarias
        from app.utils.s3_utils import get_s3_url
        import requests
        
        # Lista de imágenes para probar
        test_images = [
            "30391fbc32904c97883c713b6c3eee19_9d023a524a254234a90d1f20bbbbf419_caec1d0221bd40b2bb680c03729c9d78_Firefly_Hermosa_joven_nordica_de_exuberante_cuerpo_con_poca_ropa_dejando_entre_ver_sus_bellezas_habl_1.jpg",
            "64a792c06c434f1c845c3c6954ab572a_breathtakinghermosamujerirl_26781173.png",
            "7903341a544d40218c77ad020c21b4bc_Miguel_Angel_y_yo_de_ninos.jpg"
        ]
        
        for image in test_images:
            print(f"\n📄 Probando: {image}")
            
            # Generar URL de S3
            s3_url = get_s3_url(image)
            if s3_url:
                print(f"   🔗 URL S3: {s3_url}")
                
                # Probar acceso HTTP
                try:
                    response = requests.head(s3_url, timeout=10)
                    print(f"   📊 Status: {response.status_code}")
                    if response.status_code == 200:
                        print(f"   ✅ Imagen accesible en S3")
                    elif response.status_code == 403:
                        print(f"   ❌ Error 403: Acceso denegado")
                    elif response.status_code == 404:
                        print(f"   ❌ Error 404: Imagen no encontrada en S3")
                    else:
                        print(f"   ⚠️  Status inesperado: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error HTTP: {e}")
            else:
                print(f"   ❌ No se pudo generar URL de S3")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_local_images():
    """Verifica qué imágenes están en local"""
    
    print(f"\n📁 VERIFICANDO IMÁGENES LOCALES")
    print("=" * 50)
    
    try:
        # Ruta de imágenes locales
        local_path = "app/static/imagenes_subidas"
        
        if os.path.exists(local_path):
            print(f"   📂 Directorio local: {local_path}")
            
            # Listar archivos
            files = os.listdir(local_path)
            print(f"   📄 Archivos encontrados: {len(files)}")
            
            # Mostrar algunos archivos
            for i, file in enumerate(files[:10]):
                print(f"      {i+1}. {file}")
            
            if len(files) > 10:
                print(f"      ... y {len(files) - 10} más")
        else:
            print(f"   ❌ Directorio local no existe: {local_path}")
        
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
    
    # Verificar permisos S3
    s3_success = check_s3_permissions()
    
    # Probar imágenes S3
    test_success = test_s3_images()
    
    # Verificar imágenes locales
    local_success = check_local_images()
    
    print(f"\n🎉 VERIFICACIÓN COMPLETADA")
    print("=" * 50)
    
    if s3_success and test_success and local_success:
        print(f"   ✅ Verificación completada exitosamente")
        return True
    else:
        print(f"   ❌ Error en la verificación")
        return False

if __name__ == "__main__":
    main()
