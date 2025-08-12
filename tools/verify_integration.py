#!/usr/bin/env python3
# Descripción: Verifica que todas las herramientas estén correctamente integradas en el sistema

import os
import requests
import json

def verify_tools_integration():
    """Verifica la integración de herramientas"""
    
    print("🔍 VERIFICANDO INTEGRACIÓN DE HERRAMIENTAS")
    print("=" * 50)
    
    # URL base
    base_url = "http://localhost:8000"
    
    # Crear sesión
    session = requests.Session()
    
    # Login como admin
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    print("🔐 Iniciando sesión...")
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    
    if login_response.status_code != 200:
        print(f"   ❌ Error en login: {login_response.status_code}")
        return False
    
    print("   ✅ Login exitoso")
    
    # Verificar acceso al dashboard de herramientas
    print(f"\n📊 Verificando dashboard de herramientas...")
    tools_response = session.get(f"{base_url}/admin/tools/")
    
    if tools_response.status_code != 200:
        print(f"   ❌ Error accediendo a /admin/tools/: {tools_response.status_code}")
        return False
    
    print("   ✅ Dashboard accesible")
    
    # Verificar API de metadatos de scripts
    print(f"\n🔗 Verificando API de metadatos...")
    api_response = session.get(f"{base_url}/admin/tools/api/scripts_metadata")
    
    if api_response.status_code != 200:
        print(f"   ❌ Error en API: {api_response.status_code}")
        return False
    
    print("   ✅ API funcionando")
    
    # Parsear respuesta JSON
    try:
        scripts_data = api_response.json()
        print(f"   📊 Datos recibidos: {len(scripts_data)} entornos")
        
        # Verificar categorías
        for entorno in scripts_data:
            print(f"\n   🌍 Entorno: {entorno.get('entorno', 'N/A')}")
            categorias = entorno.get('categorias', [])
            
            for categoria in categorias:
                nombre_cat = categoria.get('nombre', 'N/A')
                scripts = categoria.get('scripts', [])
                print(f"      📁 {nombre_cat}: {len(scripts)} scripts")
                
                # Verificar nuestras herramientas específicas
                for script in scripts:
                    nombre = script.get('nombre', '')
                    if any(keyword in nombre.lower() for keyword in ['test_', 'check_', 'diagnose_', 'migrate_', 'configurar_']):
                        print(f"         ✅ {nombre}: {script.get('descripcion', 'Sin descripción')}")
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Error parseando JSON: {e}")
        return False
    
    # Verificar herramientas específicas
    print(f"\n🎯 Verificando herramientas específicas...")
    
    specific_tools = [
        "test_image_manager.py",
        "check_catalog_data.py", 
        "simple_s3_migration.py",
        "configurar_s3_publico.py"
    ]
    
    found_tools = 0
    for tool in specific_tools:
        # Buscar en la respuesta JSON
        found = False
        for entorno in scripts_data:
            for categoria in entorno.get('categorias', []):
                for script in categoria.get('scripts', []):
                    if script.get('nombre') == tool:
                        found = True
                        found_tools += 1
                        print(f"   ✅ {tool} encontrado en {categoria.get('nombre')}")
                        break
                if found:
                    break
            if found:
                break
        
        if not found:
            print(f"   ❌ {tool} NO encontrado")
    
    print(f"\n🎉 RESUMEN DE VERIFICACIÓN")
    print(f"   📊 Herramientas específicas encontradas: {found_tools}/{len(specific_tools)}")
    
    if found_tools == len(specific_tools):
        print(f"   ✅ Todas las herramientas están integradas correctamente")
        return True
    else:
        print(f"   ⚠️  Algunas herramientas no están integradas")
        return False

if __name__ == "__main__":
    verify_tools_integration()
