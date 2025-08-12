#!/usr/bin/env python3
"""
Script para diagnosticar y corregir problemas de validación JSON en archivos Markdown en VS Code.
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def check_vscode_configuration():
    """Verifica la configuración actual de VS Code."""
    print("=== DIAGNÓSTICO DE CONFIGURACIÓN VS CODE ===")
    
    # Verificar archivos de configuración
    vscode_dir = Path(".vscode")
    if not vscode_dir.exists():
        print("❌ Directorio .vscode no encontrado")
        return False
    
    print("✅ Directorio .vscode encontrado")
    
    # Verificar settings.json
    settings_file = vscode_dir / "settings.json"
    if not settings_file.exists():
        print("❌ settings.json no encontrado")
        return False
    
    print("✅ settings.json encontrado")
    
    # Verificar contenido de settings.json
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # Verificar configuraciones específicas para Markdown
        markdown_configs = [
            "files.associations",
            "json.validate.enable",
            "json.schemas",
            "markdown.preview.breaks"
        ]
        
        for config in markdown_configs:
            if config in settings:
                print(f"✅ {config} configurado: {settings[config]}")
            else:
                print(f"⚠️  {config} no encontrado en settings.json")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear settings.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Error al leer settings.json: {e}")
        return False

def check_markdown_files():
    """Verifica archivos Markdown en el proyecto."""
    print("\n=== VERIFICACIÓN DE ARCHIVOS MARKDOWN ===")
    
    markdown_files = list(Path(".").rglob("*.md"))
    
    if not markdown_files:
        print("⚠️  No se encontraron archivos Markdown")
        return
    
    print(f"✅ Encontrados {len(markdown_files)} archivos Markdown:")
    
    for md_file in markdown_files:
        print(f"  - {md_file}")
        
        # Verificar si el archivo es válido
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar si el contenido parece ser JSON
            if content.strip().startswith('{') or content.strip().startswith('['):
                print(f"    ⚠️  El archivo parece contener JSON en lugar de Markdown")
            else:
                print(f"    ✅ Contenido parece ser Markdown válido")
                
        except Exception as e:
            print(f"    ❌ Error al leer archivo: {e}")

def create_workspace_settings():
    """Crea configuraciones específicas del workspace para resolver el problema."""
    print("\n=== CREANDO CONFIGURACIONES ESPECÍFICAS ===")
    
    # Crear .vscode/settings.json si no existe
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    settings_file = vscode_dir / "settings.json"
    
    # Configuraciones específicas para resolver el problema
    markdown_settings = {
        "files.associations": {
            "*.md": "markdown"
        },
        "json.validate.enable": True,
        "json.schemas": [],
        "markdown.preview.breaks": "on",
        "markdown.preview.linkify": True,
        "markdown.preview.scrollPreviewWithEditor": True,
        "markdown.preview.scrollEditorWithPreview": True,
        "markdown.preview.fontSize": 14,
        "markdown.preview.lineHeight": 1.6,
        "markdown.preview.marker": "•",
        "markdown.preview.typographer": False,
        "markdown.extension.preview.autoShowPreviewToSide": True,
        "markdown.extension.toc.levels": "1..6",
        "markdown.extension.toc.orderedList": False,
        "markdown.extension.toc.plaintext": False,
        "markdown.extension.toc.updateOnSave": True
    }
    
    # Leer configuración existente
    existing_settings = {}
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
        except Exception as e:
            print(f"⚠️  Error al leer settings.json existente: {e}")
    
    # Fusionar configuraciones
    existing_settings.update(markdown_settings)
    
    # Guardar configuración actualizada
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4, ensure_ascii=False)
        
        print("✅ Configuración de Markdown actualizada en settings.json")
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar settings.json: {e}")
        return False

def create_markdown_workspace_config():
    """Crea un archivo de configuración específico para archivos Markdown."""
    print("\n=== CREANDO CONFIGURACIÓN ESPECÍFICA PARA MARKDOWN ===")
    
    # Crear .vscode/markdown.json
    vscode_dir = Path(".vscode")
    markdown_config_file = vscode_dir / "markdown.json"
    
    markdown_config = {
        "markdown.preview.breaks": "on",
        "markdown.preview.linkify": True,
        "markdown.preview.scrollPreviewWithEditor": True,
        "markdown.preview.scrollEditorWithPreview": True,
        "markdown.preview.fontSize": 14,
        "markdown.preview.lineHeight": 1.6,
        "markdown.preview.marker": "•",
        "markdown.preview.typographer": False,
        "markdown.extension.preview.autoShowPreviewToSide": True,
        "markdown.extension.toc.levels": "1..6",
        "markdown.extension.toc.orderedList": False,
        "markdown.extension.toc.plaintext": False,
        "markdown.extension.toc.updateOnSave": True
    }
    
    try:
        with open(markdown_config_file, 'w', encoding='utf-8') as f:
            json.dump(markdown_config, f, indent=4, ensure_ascii=False)
        
        print("✅ Archivo markdown.json creado")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear markdown.json: {e}")
        return False

def check_vscode_extensions():
    """Verifica las extensiones de VS Code instaladas."""
    print("\n=== VERIFICACIÓN DE EXTENSIONES VS CODE ===")
    
    # Extensiones recomendadas para Markdown
    recommended_extensions = [
        "yzhang.markdown-all-in-one",
        "davidanson.vscode-markdownlint",
        "streetsidesoftware.code-spell-checker"
    ]
    
    print("Extensiones recomendadas para Markdown:")
    for ext in recommended_extensions:
        print(f"  - {ext}")
    
    print("\nPara instalar estas extensiones, ejecuta:")
    for ext in recommended_extensions:
        print(f"  code --install-extension {ext}")

def main():
    """Función principal del script."""
    print("🔧 DIAGNÓSTICO Y CORRECCIÓN DE VALIDACIÓN JSON EN MARKDOWN")
    print("=" * 60)
    
    # Verificar configuración actual
    config_ok = check_vscode_configuration()
    
    # Verificar archivos Markdown
    check_markdown_files()
    
    # Crear configuraciones específicas
    if not config_ok:
        print("\n🛠️  Aplicando correcciones...")
        create_workspace_settings()
        create_markdown_workspace_config()
    
    # Verificar extensiones
    check_vscode_extensions()
    
    print("\n" + "=" * 60)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("\nRecomendaciones:")
    print("1. Reinicia VS Code para aplicar los cambios")
    print("2. Instala las extensiones recomendadas para Markdown")
    print("3. Si el problema persiste, verifica que no haya extensiones conflictivas")
    print("4. Considera deshabilitar temporalmente extensiones de validación JSON")

if __name__ == "__main__":
    main()
