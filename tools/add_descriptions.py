#!/usr/bin/env python3
"""
Script para agregar descripciones a las herramientas creadas
"""

import os
import re

def add_description_to_file(file_path, description):
    """Agrega una descripción al inicio de un archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si ya tiene descripción
        if "# Descripción:" in content:
            print(f"   ⚠️  Ya tiene descripción: {file_path}")
            return False
        
        # Agregar descripción después del shebang
        if content.startswith('#!/usr/bin/env python3'):
            new_content = content.replace(
                '#!/usr/bin/env python3',
                '#!/usr/bin/env python3\n# Descripción: ' + description
            )
        else:
            new_content = '# Descripción: ' + description + '\n\n' + content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"   ✅ Descripción agregada: {file_path}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Agrega descripciones a las herramientas"""
    
    print("📝 AGREGANDO DESCRIPCIONES A HERRAMIENTAS")
    print("=" * 50)
    
    # Definir descripciones para las herramientas
    descriptions = {
        # Testing tools
        "test_image_manager.py": "Prueba el gestor de imágenes y su funcionalidad S3/local",
        "test_catalog_images_with_session.py": "Prueba la carga de imágenes del catálogo con sesión simulada",
        "test_catalog_simple.py": "Prueba simple de imágenes del catálogo",
        "test_edit_row_images.py": "Prueba las imágenes en la página de editar fila",
        "test_catalog_view.py": "Prueba la vista del catálogo y sus imágenes",
        "test_unexpected_slash_error.py": "Diagnostica errores de sintaxis Jinja2 inesperados",
        "test_password_notification_system.py": "Prueba el sistema de notificación de contraseñas",
        "test_blueprint_registration.py": "Prueba el registro de blueprints",
        "test_image_config.py": "Prueba la configuración de imágenes",
        "test_login_credentials.py": "Prueba las credenciales de login",
        
        # Diagnostic tools
        "check_catalog_data.py": "Verifica los datos del catálogo y sus imágenes",
        "check_compatibility.py": "Verifica la compatibilidad del sistema",
        "check_s3_images.py": "Verifica el acceso y estado de imágenes en S3",
        "check_s3_permissions.py": "Verifica los permisos de S3",
        "check_user_profile.py": "Verifica el perfil de usuario y sus imágenes",
        "check_user.py": "Verifica el estado de usuarios en el sistema",
        "diagnose_login_issue.py": "Diagnostica problemas de login y autenticación",
        
        # Migration tools
        "migrate_md_files.py": "Migra archivos markdown al sistema",
        "migrate_existing_images_to_s3.py": "Migra imágenes existentes a S3",
        "simple_s3_migration.py": "Migración simple de imágenes a S3",
        
        # Configuration tools
        "configurar_s3_publico.py": "Configura S3 para acceso público",
        "configurar_s3_completo.py": "Configuración completa de S3 incluyendo permisos",
    }
    
    # Directorios a procesar
    directories = [
        "tools/testing",
        "tools/diagnostic", 
        "tools/migration",
        "tools/configuration"
    ]
    
    total_files = 0
    updated_files = 0
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"   ⚠️  Directorio no existe: {directory}")
            continue
            
        print(f"\n📁 Procesando: {directory}")
        
        for filename in os.listdir(directory):
            if filename.endswith('.py'):
                file_path = os.path.join(directory, filename)
                total_files += 1
                
                if filename in descriptions:
                    if add_description_to_file(file_path, descriptions[filename]):
                        updated_files += 1
                else:
                    print(f"   ⚠️  Sin descripción definida: {filename}")
    
    print(f"\n🎉 RESUMEN")
    print(f"   📊 Total de archivos: {total_files}")
    print(f"   ✅ Archivos actualizados: {updated_files}")
    print(f"   ⚠️  Sin descripción: {total_files - updated_files}")

if __name__ == "__main__":
    main()
