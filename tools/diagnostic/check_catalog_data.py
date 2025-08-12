#!/usr/bin/env python3
# Descripción: Verifica los datos del catálogo y sus imágenes
"""
Script para verificar los datos del catálogo
"""

import requests
import json

def check_catalog_data():
    """Verifica los datos del catálogo"""
    
    print("🔍 VERIFICANDO DATOS DEL CATÁLOGO")
    print("=" * 50)
    
    # URL del catálogo
    catalog_url = "http://localhost:8000/catalogs/687545cf84c646ad216aa3bb"
    
    # Crear sesión
    session = requests.Session()
    
    # Simular login
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    print("🔐 Iniciando sesión...")
    login_response = session.post("http://localhost:8000/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print(f"   ❌ Error en login: {login_response.status_code}")
        return False
    
    print("   ✅ Login exitoso")
    
    # Obtener página del catálogo
    print(f"📄 Obteniendo catálogo: {catalog_url}")
    catalog_response = session.get(catalog_url)
    
    if catalog_response.status_code != 200:
        print(f"   ❌ Error obteniendo catálogo: {catalog_response.status_code}")
        return False
    
    print("   ✅ Catálogo obtenido")
    
    # Buscar datos del catálogo en el HTML
    html_content = catalog_response.text
    
    # Buscar el nombre del catálogo
    import re
    name_match = re.search(r'<h2[^>]*>([^<]+)</h2>', html_content)
    if name_match:
        print(f"   📝 Nombre del catálogo: {name_match.group(1)}")
    
    # Buscar filas en la tabla
    rows = re.findall(r'<tr[^>]*>.*?</tr>', html_content, re.DOTALL)
    print(f"   📊 Filas encontradas: {len(rows)}")
    
    # Buscar imágenes en el HTML
    images = re.findall(r'<img[^>]*src="([^"]*)"[^>]*>', html_content)
    print(f"   🖼️  Imágenes en HTML: {len(images)}")
    
    for i, img_src in enumerate(images, 1):
        print(f"      {i}. {img_src}")
    
    # Buscar contenido de imágenes
    img_content = re.findall(r'images.*?\[(.*?)\]', html_content, re.DOTALL)
    print(f"   📋 Contenido de imágenes encontrado: {len(img_content)}")
    
    for i, content in enumerate(img_content, 1):
        print(f"      {i}. {content}")
    
    # Mostrar más del HTML para debug
    print(f"\n🔍 HTML completo (primeros 1000 chars):")
    print(html_content[:1000])
    
    return True

if __name__ == "__main__":
    check_catalog_data()
