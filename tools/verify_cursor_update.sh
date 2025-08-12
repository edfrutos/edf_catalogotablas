#!/bin/bash

# Script para verificar la actualización de Cursor IDE
# Ejecutar DESPUÉS de la actualización

echo "🔍 Verificando actualización de Cursor IDE..."
echo "============================================="

# Verificar versión actual
echo "📋 Versión actual de Cursor:"
if command -v cursor >/dev/null 2>&1; then
    CURSOR_VERSION=$(cursor --version 2>/dev/null || echo "No disponible")
    echo "   $CURSOR_VERSION"
else
    echo "   ❌ Cursor no encontrado en PATH"
fi

# Verificar si GitHub Copilot Chat está disponible
echo ""
echo "🤖 Estado de GitHub Copilot Chat:"
if [ -d ~/.cursor-server/extensions/github.copilot-chat-0.23.2.disabled ]; then
    echo "   ⏸️  Deshabilitado (puede ser reactivado)"
    echo "   Para reactivar: mv ~/.cursor-server/extensions/github.copilot-chat-0.23.2.disabled ~/.cursor-server/extensions/github.copilot-chat-0.23.2"
elif [ -d ~/.cursor-server/extensions/github.copilot-chat-* ]; then
    echo "   ✅ Habilitado"
else
    echo "   ❌ No instalado"
fi

# Verificar extensiones principales
echo ""
echo "🔌 Extensiones principales:"
ls -1 ~/.cursor-server/extensions/ | grep -E "(github\.copilot|ms-python|anysphere)" | while read ext; do
    echo "   ✅ $ext"
done

# Verificar configuración
echo ""
echo "⚙️  Configuración:"
if [ -f .vscode/settings.json ]; then
    echo "   ✅ .vscode/settings.json existe"
else
    echo "   ❌ .vscode/settings.json no encontrado"
fi

if [ -f .flake8 ]; then
    echo "   ✅ .flake8 existe"
else
    echo "   ❌ .flake8 no encontrado"
fi

# Verificar entorno Python
echo ""
echo "🐍 Entorno Python:"
if [ -d .venv ]; then
    echo "   ✅ Entorno virtual .venv existe"
    if [ -f .venv/bin/python ]; then
        PYTHON_VERSION=$(.venv/bin/python --version 2>&1)
        echo "   📋 Versión Python: $PYTHON_VERSION"
    fi
else
    echo "   ❌ Entorno virtual .venv no encontrado"
fi

# Verificar scripts de producción
echo ""
echo "🛠️  Scripts de producción:"
if [ -f tools/script_runner.py ]; then
    echo "   ✅ script_runner.py existe"
else
    echo "   ❌ script_runner.py no encontrado"
fi

if [ -f tools/production/db_utils/test_date_format.py ]; then
    echo "   ✅ test_date_format.py existe"
else
    echo "   ❌ test_date_format.py no encontrado"
fi

echo ""
echo "🎉 Verificación completada!"
echo "============================================="
echo "📋 Si todo está correcto, puedes:"
echo "   1. Reactivar GitHub Copilot Chat si lo necesitas"
echo "   2. Continuar trabajando normalmente"
echo "   3. Reportar cualquier problema encontrado"
