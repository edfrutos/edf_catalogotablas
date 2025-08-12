#!/usr/bin/env python3
# Descripción: Verificación rápida de herramientas disponibles

import os

def quick_verify():
    """Verificación rápida de herramientas"""
    
    print("🔍 VERIFICACIÓN RÁPIDA DE HERRAMIENTAS")
    print("=" * 50)
    
    # Directorios a verificar
    directories = {
        "Testing": "tools/testing",
        "Diagnostic": "tools/diagnostic",
        "Migration": "tools/migration", 
        "Configuration": "tools/configuration"
    }
    
    total_tools = 0
    
    for category, directory in directories.items():
        if os.path.exists(directory):
            files = [f for f in os.listdir(directory) if f.endswith('.py')]
            total_tools += len(files)
            print(f"📁 {category}: {len(files)} herramientas")
            
            for file in files[:5]:  # Mostrar solo los primeros 5
                print(f"   • {file}")
            if len(files) > 5:
                print(f"   ... y {len(files) - 5} más")
        else:
            print(f"❌ {category}: Directorio no existe")
    
    print(f"\n🎉 TOTAL: {total_tools} herramientas disponibles")
    
    # Verificar que las rutas estén en scripts_routes.py
    print(f"\n🔗 Verificando integración en rutas...")
    
    routes_file = "app/routes/scripts_routes.py"
    if os.path.exists(routes_file):
        with open(routes_file, 'r') as f:
            content = f.read()
            
        if "tools/testing" in content:
            print("   ✅ Testing tools integradas")
        else:
            print("   ❌ Testing tools NO integradas")
            
        if "tools/diagnostic" in content:
            print("   ✅ Diagnostic tools integradas")
        else:
            print("   ❌ Diagnostic tools NO integradas")
            
        if "tools/migration" in content:
            print("   ✅ Migration tools integradas")
        else:
            print("   ❌ Migration tools NO integradas")
            
        if "tools/configuration" in content:
            print("   ✅ Configuration tools integradas")
        else:
            print("   ❌ Configuration tools NO integradas")
    else:
        print("   ❌ Archivo de rutas no encontrado")

if __name__ == "__main__":
    quick_verify()
