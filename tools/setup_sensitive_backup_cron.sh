#!/bin/bash

# Script para configurar backup automático de archivos sensibles en crontab
# Creado: 2025-08-12

# Configuración
PROJECT_DIR="/var/www/vhosts/edefrutos2025.xyz/httpdocs"
BACKUP_SCRIPT="${PROJECT_DIR}/tools/backup_sensitive_files_enhanced.sh"
LOG_FILE="${PROJECT_DIR}/logs/sensitive_backup.log"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Verificar que el script de backup existe
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "❌ Error: No se encontró el script de backup en $BACKUP_SCRIPT"
    exit 1
fi

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

log "Configurando backup automático de archivos sensibles..."

# Crear archivo de cron temporal
TEMP_CRON=$(mktemp /tmp/sensitive_backup_cron.XXXXXXXXX)

# Obtener el crontab actual y filtrar entradas existentes del script
crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" > "$TEMP_CRON" || echo "# Crontab para backup de archivos sensibles" > "$TEMP_CRON"

# Agregar la nueva tarea programada
cat >> "$TEMP_CRON" << EOF

# Backup automático de archivos sensibles - EDFrutos2025
# Ejecutar diariamente a las 2:00 AM
0 2 * * * $BACKUP_SCRIPT >> $LOG_FILE 2>&1

# Backup semanal completo (domingos a las 3:00 AM)
0 3 * * 0 $BACKUP_SCRIPT --full >> $LOG_FILE 2>&1
EOF

# Instalar el nuevo crontab
crontab "$TEMP_CRON"
rm -f "$TEMP_CRON"

# Verificar que se instaló correctamente
log "✅ Crontab configurado correctamente"
log "📋 Verificando configuración..."

# Mostrar el crontab actual
echo ""
log "Tareas programadas actuales:"
crontab -l | grep -A 5 -B 5 "backup_sensitive_files"

# Crear script de verificación
VERIFICATION_SCRIPT="${PROJECT_DIR}/tools/verify_sensitive_backup.sh"
cat > "$VERIFICATION_SCRIPT" << 'EOF'
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
EOF

chmod +x "$VERIFICATION_SCRIPT"

log "📋 Script de verificación creado: $VERIFICATION_SCRIPT"

# Crear documentación
DOC_FILE="${PROJECT_DIR}/docs/SENSITIVE_BACKUP_README.md"
mkdir -p "$(dirname "$DOC_FILE")"

cat > "$DOC_FILE" << EOF
# Backup Automático de Archivos Sensibles

## Descripción
Este sistema realiza backups automáticos de archivos sensibles identificados en el `.gitignore` del proyecto.

## Configuración

### Ubicación del Backup
- **Directorio**: `/var/www/vhosts/edefrutos2025.xyz/backups/gitignore/`
- **Formato**: `sensitive_files_YYYYMMDD_HHMMSS.tar.gz`
- **Permisos**: 600 (solo root puede leer)

### Programación
- **Backup diario**: 2:00 AM todos los días
- **Backup semanal**: 3:00 AM los domingos
- **Logs**: `/var/www/vhosts/edefrutos2025.xyz/httpdocs/logs/sensitive_backup.log`

## Archivos Respaldados

### Archivos de Entorno
- \`.env\` y variantes (\`.env.local\`, \`.env.production\`, etc.)

### Credenciales y Tokens
- Archivos que contengan: \`credentials\`, \`secret\`, \`api_key\`, \`token\`, \`password\`
- \`tools/production/db_utils/credentials.json\`
- \`tools/production/db_utils/token.pickle\`

### Certificados y Claves
- \`*.pem\`, \`*.key\`, \`*.crt\`, \`*.cer\`, \`*.p12\`, \`*.pfx\`

### Logs Sensibles
- \`logs/gunicorn_access.log\`
- \`logs/flask_debug.log\`
- \`logs/gunicorn_error.log\`

### Archivos de Debug
- \`debug_*.py\`
- \`*_debug.*\`
- \`app/templates/dev_template/tests/legacy/config_debug.py\`

## Comandos Útiles

### Verificar Estado
\`\`\`bash
./tools/verify_sensitive_backup.sh
\`\`\`

### Backup Manual
\`\`\`bash
./tools/backup_sensitive_files_enhanced.sh
\`\`\`

### Restaurar Backup
\`\`\`bash
tar -xzf /var/www/vhosts/edefrutos2025.xyz/backups/gitignore/sensitive_files_YYYYMMDD_HHMMSS.tar.gz -C /ruta/destino
\`\`\`

### Verificar Contenido
\`\`\`bash
tar -tzf /var/www/vhosts/edefrutos2025.xyz/backups/gitignore/sensitive_files_YYYYMMDD_HHMMSS.tar.gz
\`\`\`

## Mantenimiento

### Limpieza Automática
- Se mantienen los últimos 5 backups
- Los backups antiguos se eliminan automáticamente

### Seguridad
- Los backups tienen permisos 600 (solo root)
- Se comprimen con tar.gz
- Incluyen inventario y metadatos

## Troubleshooting

### Si el backup falla
1. Verificar permisos del script: \`chmod +x tools/backup_sensitive_files_enhanced.sh\`
2. Verificar espacio en disco: \`df -h /var/www/vhosts/edefrutos2025.xyz/backups/\`
3. Revisar logs: \`tail -f /var/www/vhosts/edefrutos2025.xyz/httpdocs/logs/sensitive_backup.log\`

### Si el crontab no funciona
1. Verificar que cron esté ejecutándose: \`systemctl status cron\`
2. Verificar crontab: \`crontab -l\`
3. Reinstalar: \`./tools/setup_sensitive_backup_cron.sh\`
EOF

log "📚 Documentación creada: $DOC_FILE"

echo ""
log "🎉 Configuración completada!"
log "📋 Resumen:"
echo "   - Backup diario: 2:00 AM"
echo "   - Backup semanal: 3:00 AM (domingos)"
echo "   - Ubicación: /var/www/vhosts/edefrutos2025.xyz/backups/gitignore/"
echo "   - Logs: /var/www/vhosts/edefrutos2025.xyz/httpdocs/logs/sensitive_backup.log"
echo ""
log "Para verificar el estado:"
echo "   ./tools/verify_sensitive_backup.sh"
