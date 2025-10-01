#!/usr/bin/env python3
"""
Script para corregir automáticamente las rutas de imágenes en los templates
"""

import glob
import os
import re


def fix_image_paths():
    """Corrige las rutas de imágenes en todos los templates"""

    print("🔧 CORRIGIENDO RUTAS DE IMÁGENES EN TEMPLATES")
    print("=" * 60)

    # Patrones a buscar y reemplazar
    patterns = [
        (
            r"url_for\(\'static\', filename=\'uploads/\' \+ ([^)]+)\)",
            r"/imagenes_subidas/\1",
        ),
        (
            r"url_for\(\'static\', filename=\'uploads/\' ~ ([^)]+)\)",
            r"/imagenes_subidas/\1",
        ),
        (
            r"url_for\(\'static\', filename=\'uploads/\' \+ ([^)]+)\)",
            r"/imagenes_subidas/\1",
        ),
        (
            r"url_for\(\'static\', filename=\'uploads/\' ~ ([^)]+)\)",
            r"/imagenes_subidas/\1",
        ),
    ]

    # Buscar todos los archivos HTML
    html_files = glob.glob("app/templates/**/*.html", recursive=True)

    total_fixed = 0

    for file_path in html_files:
        print(f"\n📄 Procesando: {file_path}")

        try:
            # Leer el archivo
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            file_fixed = False

            # Aplicar cada patrón
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    file_fixed = True

            # Si se hicieron cambios, escribir el archivo
            if file_fixed:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print("   ✅ Corregido")
                total_fixed += 1
            else:
                print("   ⏭️  Sin cambios necesarios")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n🎉 CORRECCIÓN COMPLETADA")
    print(f"   📄 Archivos procesados: {len(html_files)}")
    print(f"   ✅ Archivos corregidos: {total_fixed}")

    return total_fixed


def fix_python_files():
    """Corrige las rutas de imágenes en archivos Python"""

    print("\n🔧 CORRIGIENDO RUTAS DE IMÁGENES EN ARCHIVOS PYTHON")
    print("=" * 60)

    # Patrones específicos para Python
    patterns = [
        (
            r"url_for\(\'static\', filename=f\'uploads/\{([^}]+)\}\)",
            r"/imagenes_subidas/\1",
        ),
        (
            r"url_for\(\'static\', filename=\'uploads/\' \+ ([^)]+)\)",
            r"/imagenes_subidas/\1",
        ),
    ]

    # Archivos Python específicos que sabemos que tienen problemas
    python_files = [
        "app/models/user.py",
        "app/routes/main_routes.py",
        "app/routes/admin_routes.py",
        "app/utils/image_utils.py",
    ]

    total_fixed = 0

    for file_path in python_files:
        if not os.path.exists(file_path):
            continue

        print(f"\n🐍 Procesando: {file_path}")

        try:
            # Leer el archivo
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            file_fixed = False

            # Aplicar cada patrón
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    file_fixed = True

            # Si se hicieron cambios, escribir el archivo
            if file_fixed:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print("   ✅ Corregido")
                total_fixed += 1
            else:
                print("   ⏭️  Sin cambios necesarios")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n🎉 CORRECCIÓN DE PYTHON COMPLETADA")
    print(f"   🐍 Archivos procesados: {len(python_files)}")
    print(f"   ✅ Archivos corregidos: {total_fixed}")

    return total_fixed


def main():
    """Función principal"""

    print("🚀 CORRIGIENDO RUTAS DE IMÁGENES")
    print("=" * 60)

    # Corregir templates HTML
    html_fixed = fix_image_paths()

    # Corregir archivos Python
    python_fixed = fix_python_files()

    print("\n🎉 RESUMEN FINAL")
    print("=" * 60)
    print(f"   📄 Templates HTML corregidos: {html_fixed}")
    print(f"   🐍 Archivos Python corregidos: {python_fixed}")
    print(f"   📊 Total de archivos corregidos: {html_fixed + python_fixed}")

    if html_fixed + python_fixed > 0:
        print("\n💡 Ahora las imágenes de catálogos deberían mostrarse correctamente")
        print("   🔄 Reinicia el servicio para aplicar los cambios")
    else:
        print("\nℹ️  No se encontraron archivos que necesiten corrección")


if __name__ == "__main__":
    main()
