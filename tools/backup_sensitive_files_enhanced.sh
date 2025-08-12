#!/bin/bash

# Script mejorado para respaldar archivos sensibles basado en .gitignore
# Backup en /var/www/vhosts/edefrutos2025.xyz/backups/gitignore/
# Creado: 2025-08-12

# set -e  # Comentado para permitir continuar con errores

# Configuración
PROJECT_DIR="/var/www/vhosts/edefrutos2025.xyz/httpdocs"
BACKUP_BASE="/var/www/vhosts/edefrutos2025.xyz/backups"
BACKUP_DIR="${BACKUP_BASE}/gitignore"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="sensitive_files_${DATE}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "${PROJECT_DIR}/.gitignore" ]; then
    error "No se encontró .gitignore en ${PROJECT_DIR}"
    exit 1
fi

log "Iniciando backup de archivos sensibles..."
log "Proyecto: ${PROJECT_DIR}"
log "Backup: ${BACKUP_PATH}"

# Crear directorios de backup
mkdir -p "${BACKUP_PATH}"
mkdir -p "${BACKUP_DIR}"

# Lista de patrones sensibles basados en .gitignore
SENSITIVE_PATTERNS=(
    # Archivos de entorno
    ".env"
    ".env.*"
    "*.env"
    ".env.local"
    ".env.development"
    ".env.test"
    ".env.production"
    
    # Credenciales y tokens
    "*credentials*"
    "*secret*"
    "*api_key*"
    "*apikey*"
    "*password*"
    "*token*"
    
    # Archivos de configuración sensibles
    "mi_config.json"
    "token.pickle"
    "*.pickle"
    "*.pem"
    "*.key"
    "*.p12"
    "*.pfx"
    "*.jks"
    "*.keystore"
    "*.crt"
    "*.cer"
    "*.der"
    
    # Archivos de configuración local
    "config.local.*"
    "settings.local.*"
    
    # Logs sensibles
    "logs/gunicorn_access.log"
    "logs/flask_debug.log"
    "logs/gunicorn_error.log"
    "logs/*.log"
    
    # Archivos de backup específicos
    "**/scripts_routes.py.bak.*"
    "app.py.bak.*"
    ".env.bak.*"
    "wsgi.py.bak.*"
    
    # Archivos de debug y configuración
    "app/templates/dev_template/tests/legacy/config_debug.py"
    "debug_*.py"
    "*_debug.*"
    
    # Archivos de VS Code/Cursor
    ".vscode/settings.json.bak"
    ".vscode/launch.json.bak"
    ".vscode/tasks.json.bak"
    ".vscode/extensions.json.bak"
    
    # Archivos de configuración de Python
    ".pylintrc.bak"
    ".pylintrc.backup"
    "pyrightconfig.json.bak"
    "pyrightconfig.json.backup"
    "mypy.ini"
    "pyproject.toml.bak"
    "setup.cfg.bak"
)

# Archivos específicos que sabemos que existen
SPECIFIC_FILES=(
    "tools/db_utils/credentials.json"
    "tools/db_utils/token.pickle"
    "tools/maintenance/mi_config.json"
    "tools/db_utils/mongodb_backup.log"
    "cookies.txt"
    "clean_project.py"
    "app/static/___prueba_cascade.txt"
)

# Contador de archivos respaldados
BACKED_UP_COUNT=0
MISSING_COUNT=0

log "Buscando archivos sensibles..."

# Función para respaldar un archivo
backup_file() {
    local file="$1"
    local relative_path="${file#${PROJECT_DIR}/}"
    
    if [ -f "$file" ]; then
        local dest_dir="${BACKUP_PATH}/$(dirname "$relative_path")"
        mkdir -p "$dest_dir"
        cp "$file" "${BACKUP_PATH}/${relative_path}"
        log "✅ Respaldo: $relative_path"
        ((BACKED_UP_COUNT++))
    else
        warn "No encontrado: $relative_path"
        ((MISSING_COUNT++))
    fi
}

# Buscar archivos por patrones
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    log "Buscando patrón: $pattern"
    
    # Usar find para buscar archivos que coincidan con el patrón
    find "$PROJECT_DIR" -type f -name "$pattern" 2>/dev/null | while read -r file; do
        # Excluir el directorio de backup actual
        if [[ "$file" != *"${BACKUP_NAME}"* ]]; then
            backup_file "$file"
        fi
    done || true
done

# Respaldo de archivos específicos
log "Respaldo de archivos específicos..."
for file in "${SPECIFIC_FILES[@]}"; do
    full_path="${PROJECT_DIR}/${file}"
    backup_file "$full_path"
done

# Buscar archivos de configuración adicionales
log "Buscando archivos de configuración adicionales..."

# Archivos .env y similares
find "$PROJECT_DIR" -type f \( -name ".env*" -o -name "*.env" \) 2>/dev/null | while read -r file; do
    if [[ "$file" != *"${BACKUP_NAME}"* ]]; then
        backup_file "$file"
    fi
done

# Archivos de credenciales
find "$PROJECT_DIR" -type f \( -name "*credentials*" -o -name "*secret*" -o -name "*token*" -o -name "*password*" \) 2>/dev/null | while read -r file; do
    if [[ "$file" != *"${BACKUP_NAME}"* ]]; then
        backup_file "$file"
    fi
done

# Archivos de certificados y claves
find "$PROJECT_DIR" -type f \( -name "*.pem" -o -name "*.key" -o -name "*.crt" -o -name "*.cer" \) 2>/dev/null | while read -r file; do
    if [[ "$file" != *"${BACKUP_NAME}"* ]]; then
        backup_file "$file"
    fi
done

# Crear archivo de inventario
INVENTORY_FILE="${BACKUP_PATH}/backup_inventory.txt"
log "Creando inventario en: $INVENTORY_FILE"

cat > "$INVENTORY_FILE" << EOF
INVENTARIO DE BACKUP DE ARCHIVOS SENSIBLES
==========================================
Fecha: $(date)
Proyecto: ${PROJECT_DIR}
Backup: ${BACKUP_PATH}

ARCHIVOS RESPALDADOS:
$(find "${BACKUP_PATH}" -type f -name "*.txt" -o -name "*.json" -o -name "*.pickle" -o -name "*.pem" -o -name "*.key" -o -name "*.env*" | sort)

ESTADÍSTICAS:
- Archivos respaldados: ${BACKED_UP_COUNT}
- Archivos no encontrados: ${MISSING_COUNT}
- Tamaño total: $(du -sh "${BACKUP_PATH}" | cut -f1)

PATRONES BUSCADOS:
$(printf '%s\n' "${SENSITIVE_PATTERNS[@]}")

ARCHIVOS ESPECÍFICOS:
$(printf '%s\n' "${SPECIFIC_FILES[@]}")

NOTAS:
- Este backup contiene archivos sensibles que NO deben subirse al repositorio
- Los archivos están organizados manteniendo la estructura de directorios original
- Verificar permisos y seguridad antes de restaurar
EOF

# Crear archivo de metadatos
METADATA_FILE="${BACKUP_PATH}/metadata.json"
cat > "$METADATA_FILE" << EOF
{
    "backup_info": {
        "date": "$(date -Iseconds)",
        "project_dir": "${PROJECT_DIR}",
        "backup_path": "${BACKUP_PATH}",
        "files_count": ${BACKED_UP_COUNT},
        "missing_count": ${MISSING_COUNT},
        "size_bytes": $(du -sb "${BACKUP_PATH}" | cut -f1)
    },
    "patterns_searched": $(printf '%s\n' "${SENSITIVE_PATTERNS[@]}" | jq -R . | jq -s .),
    "specific_files": $(printf '%s\n' "${SPECIFIC_FILES[@]}" | jq -R . | jq -s .)
}
EOF

# Comprimir el backup
log "Comprimiendo backup..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"

# Establecer permisos seguros
chmod 600 "${BACKUP_NAME}.tar.gz"
chown root:root "${BACKUP_NAME}.tar.gz" 2>/dev/null || true

# Limpiar backups antiguos (mantener solo los últimos 5)
log "Limpiando backups antiguos..."
ls -t "${BACKUP_DIR}"/sensitive_files_*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm -f

# Resumen final
log "Backup completado exitosamente!"
log "Ubicación: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
log "Tamaño: $(du -sh "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)"
log "Archivos respaldados: ${BACKED_UP_COUNT}"
log "Archivos no encontrados: ${MISSING_COUNT}"

# Mostrar backups disponibles
log "Backups disponibles:"
ls -lh "${BACKUP_DIR}"/sensitive_files_*.tar.gz 2>/dev/null || echo "No hay backups previos"

echo ""
log "Para restaurar el backup:"
echo "  tar -xzf ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz -C /ruta/destino"
echo ""
log "Para verificar el contenido:"
echo "  tar -tzf ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
