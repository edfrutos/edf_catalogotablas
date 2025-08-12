#!/bin/bash

# Script para verificar el estado de los backups de archivos sensibles
# Uso: ./tools/verify_sensitive_backup.sh

BACKUP_DIR="/var/www/vhosts/edefrutos2025.xyz/backups/gitignore"
LOG_FILE="/var/www/vhosts/edefrutos2025.xyz/httpdocs/logs/sensitive_backup.log"

echo "🔍 Verificando backups de archivos sensibles..."
echo "=============================================="

# Verificar directorio de backup
if [ -d "$BACKUP_DIR" ]; then
    echo "✅ Directorio de backup existe: $BACKUP_DIR"
    
    # Contar backups disponibles
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/sensitive_files_*.tar.gz 2>/dev/null | wc -l)
    echo "📦 Backups disponibles: $BACKUP_COUNT"
    
    if [ $BACKUP_COUNT -gt 0 ]; then
        echo ""
        echo "📋 Últimos backups:"
        ls -lh "$BACKUP_DIR"/sensitive_files_*.tar.gz | tail -5
        
        # Mostrar el más reciente
        LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/sensitive_files_*.tar.gz 2>/dev/null | head -1)
        if [ -n "$LATEST_BACKUP" ]; then
            echo ""
            echo "🆕 Backup más reciente: $(basename "$LATEST_BACKUP")"
            echo "📏 Tamaño: $(du -sh "$LATEST_BACKUP" | cut -f1)"
            echo "📅 Fecha: $(stat -c %y "$LATEST_BACKUP")"
        fi
    else
        echo "⚠️  No se encontraron backups"
    fi
else
    echo "❌ Directorio de backup no existe: $BACKUP_DIR"
fi

# Verificar logs
echo ""
echo "📝 Verificando logs..."
if [ -f "$LOG_FILE" ]; then
    echo "✅ Archivo de log existe: $LOG_FILE"
    echo "📏 Tamaño: $(du -sh "$LOG_FILE" | cut -f1)"
    echo "📅 Última modificación: $(stat -c %y "$LOG_FILE")"
    
    echo ""
    echo "🔄 Últimas 10 líneas del log:"
    tail -10 "$LOG_FILE" 2>/dev/null || echo "No se pudo leer el log"
else
    echo "⚠️  Archivo de log no existe: $LOG_FILE"
fi

# Verificar crontab
echo ""
echo "⏰ Verificando crontab..."
if crontab -l 2>/dev/null | grep -q "backup_sensitive_files"; then
    echo "✅ Tarea de backup configurada en crontab"
    crontab -l | grep "backup_sensitive_files"
else
    echo "❌ Tarea de backup no encontrada en crontab"
fi

echo ""
echo "🎉 Verificación completada!"
