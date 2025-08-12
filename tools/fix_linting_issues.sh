#!/bin/bash

# Script para corregir problemas de linting en archivos Markdown
echo "🔧 Corrigiendo problemas de linting..."

# Verificar si estamos en el directorio correcto
if [ ! -f ".vscode/settings.json" ]; then
    echo "❌ No se encontró .vscode/settings.json. Ejecuta este script desde el directorio raíz del proyecto."
    exit 1
fi

# Crear backup de configuraciones actuales
echo "📦 Creando backup de configuraciones..."
BACKUP_DIR="/tmp/vscode_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r .vscode "$BACKUP_DIR/"
echo "✅ Backup creado en: $BACKUP_DIR"

# Verificar configuraciones actuales
echo "🔍 Verificando configuraciones actuales..."
echo "   - Python analysis exclude: $(grep -c "*.md" .vscode/settings.json || echo "No encontrado")"
echo "   - JSON validation: $(grep -c "json.validate.enable" .vscode/settings.json || echo "No encontrado")"

# Forzar recarga de configuraciones
echo "🔄 Forzando recarga de configuraciones..."
if command -v code >/dev/null 2>&1; then
    echo "   - Reiniciando VS Code..."
    pkill -f "code" 2>/dev/null || true
    sleep 2
fi

# Verificar archivos problemáticos
echo "📋 Verificando archivos problemáticos..."
if [ -f "RESUMEN_CORRECCION_SCRIPTS_PRODUCCION.md" ]; then
    echo "   ✅ RESUMEN_CORRECCION_SCRIPTS_PRODUCCION.md existe"
else
    echo "   ❌ RESUMEN_CORRECCION_SCRIPTS_PRODUCCION.md no encontrado"
fi

if [ -f ".cursorrules" ]; then
    echo "   ✅ .cursorrules existe"
else
    echo "   ❌ .cursorrules no encontrado"
fi

# Verificar configuraciones de Pyright
echo "🐍 Verificando configuración de Pyright..."
if [ -f "pyrightconfig.json" ]; then
    echo "   ✅ pyrightconfig.json existe"
    echo "   - Exclusiones: $(grep -c "*.md" pyrightconfig.json || echo "0")"
else
    echo "   ❌ pyrightconfig.json no encontrado"
fi

# Verificar configuración de Flake8
echo "🔍 Verificando configuración de Flake8..."
if [ -f ".flake8" ]; then
    echo "   ✅ .flake8 existe"
    echo "   - Exclusiones: $(grep -c "*.md" .flake8 || echo "0")"
else
    echo "   ❌ .flake8 no encontrado"
fi

echo ""
echo "🎉 Proceso completado!"
echo "=========================================="
echo "📋 Próximos pasos:"
echo "   1. Reinicia VS Code/Cursor completamente"
echo "   2. Verifica que los errores hayan desaparecido"
echo "   3. Si persisten, ejecuta: code --reload-window"
echo ""
echo "🔧 Si los problemas persisten:"
echo "   - Elimina la carpeta .vscode/data/logs/"
echo "   - Reinicia el servidor de lenguaje Python"
echo "   - Verifica que las extensiones estén actualizadas"
