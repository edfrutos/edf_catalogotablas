#!/bin/bash

# Script para actualizar Cursor IDE
# Ejecutar DESPUÉS de desconectarse del entorno remoto

echo "🔄 Iniciando actualización de Cursor IDE..."
echo "=========================================="

# Verificar si Cursor está ejecutándose
if pgrep -f "cursor-server" > /dev/null; then
    echo "❌ Cursor está ejecutándose. Por favor, cierra todas las instancias de Cursor antes de continuar."
    echo "   Puedes usar: pkill -f cursor-server"
    exit 1
fi

# Crear backup de la configuración actual
echo "📦 Creando backup de la configuración actual..."
BACKUP_DIR="/tmp/cursor_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -d ~/.cursor-server ]; then
    cp -r ~/.cursor-server "$BACKUP_DIR/"
    echo "✅ Backup creado en: $BACKUP_DIR"
fi

# Descargar la última versión de Cursor
echo "⬇️  Descargando la última versión de Cursor..."
cd /tmp

# Intentar diferentes métodos de descarga
CURSOR_DOWNLOADED=false

# Método 1: Descarga directa desde GitHub
echo "   Intentando descarga desde GitHub..."
if curl -L -o cursor-latest.AppImage "https://github.com/getcursor/cursor/releases/latest/download/cursor-0.0.0-linux-x64.AppImage" 2>/dev/null; then
    CURSOR_DOWNLOADED=true
    echo "✅ Descarga exitosa desde GitHub"
fi

# Método 2: Si falla GitHub, intentar con wget
if [ "$CURSOR_DOWNLOADED" = false ]; then
    echo "   Intentando con wget..."
    if wget -O cursor-latest.AppImage "https://github.com/getcursor/cursor/releases/latest/download/cursor-0.0.0-linux-x64.AppImage" 2>/dev/null; then
        CURSOR_DOWNLOADED=true
        echo "✅ Descarga exitosa con wget"
    fi
fi

# Método 3: Descarga manual
if [ "$CURSOR_DOWNLOADED" = false ]; then
    echo "❌ No se pudo descargar automáticamente"
    echo "📋 Por favor, descarga manualmente desde:"
    echo "   https://cursor.sh/"
    echo "   O desde: https://github.com/getcursor/cursor/releases"
    echo ""
    echo "🔧 Después de descargar, ejecuta:"
    echo "   chmod +x /ruta/al/archivo/descargado"
    echo "   ./ruta/al/archivo/descargado"
    exit 1
fi

# Dar permisos de ejecución
chmod +x cursor-latest.AppImage

# Instalar la nueva versión
echo "🚀 Instalando nueva versión de Cursor..."
./cursor-latest.AppImage --appimage-extract-and-run --no-sandbox

# Verificar la instalación
echo "🔍 Verificando la instalación..."
sleep 5

if command -v cursor >/dev/null 2>&1; then
    NEW_VERSION=$(cursor --version 2>/dev/null || echo "Nueva versión instalada")
    echo "✅ Cursor actualizado exitosamente"
    echo "📋 Nueva versión: $NEW_VERSION"
else
    echo "⚠️  Cursor no se encuentra en PATH, pero puede estar instalado"
fi

# Limpiar archivos temporales
echo "🧹 Limpiando archivos temporales..."
rm -f /tmp/cursor-latest.AppImage

echo ""
echo "🎉 ¡Actualización completada!"
echo "=========================================="
echo "📋 Próximos pasos:"
echo "   1. Reinicia Cursor IDE"
echo "   2. Verifica que las extensiones funcionen correctamente"
echo "   3. Si hay problemas, puedes restaurar desde: $BACKUP_DIR"
echo ""
echo "🔧 Para reactivar GitHub Copilot Chat:"
echo "   mv ~/.cursor-server/extensions/github.copilot-chat-0.23.2.disabled ~/.cursor-server/extensions/github.copilot-chat-0.23.2"
