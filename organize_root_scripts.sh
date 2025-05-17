#!/bin/bash
# Script para organizar los scripts restantes del directorio raíz
# Creado: 17/05/2025

echo "Iniciando organización de scripts en el directorio raíz..."

# 1. Scripts relacionados con la administración
echo "Moviendo scripts de administración a scripts/admin_utils/..."
mv admin_shell.py admin_utils.py create_admin.py init_admin.py repair_admin.py scripts/admin_utils/ 2>/dev/null

# 2. Scripts para ejecutar la aplicación
echo "Moviendo scripts de ejecución de la aplicación a scripts/app_runners/..."
mv ejecutar_flask_directo.py flask_app.py simple_app.py simple.py app_min.py app_prueba_sesion.py run.py scripts/app_runners/ 2>/dev/null

# 3. Scripts relacionados con la sesión
echo "Moviendo scripts de gestión de sesiones a scripts/session_utils/..."
mv aplicar_configuracion_sesion.py session_config.py session_fix.py scripts/session_utils/ 2>/dev/null

# 4. Scripts de monitoreo
echo "Moviendo scripts de monitoreo a scripts/monitoring/..."
mv advanced_monitor.py error_handling.py scripts/monitoring/ 2>/dev/null

# 5. Scripts relacionados con catálogos
echo "Moviendo scripts relacionados con catálogos a scripts/catalog_utils/..."
mv arreglar_catalogos.py tables_direct.py direct_routes.py convert_to_xlsx.py scripts/catalog_utils/ 2>/dev/null

# 6. Scripts relacionados con imágenes
echo "Moviendo scripts relacionados con imágenes a scripts/image_utils/..."
mv crear_imagen_perfil_default.py scripts/image_utils/ 2>/dev/null

# 7. Scripts de limpieza y organización
echo "Moviendo scripts de limpieza a scripts/maintenance/..."
mv final_cleanup.py organizar_archivos.py scripts/maintenance/ 2>/dev/null

# 8. Archivos que deben permanecer en la raíz (no mover)
# - app.py (punto de entrada principal)
# - config.py (configuración principal)
# - wsgi.py, passenger_wsgi.py, gunicorn.conf.py, gunicorn_config.py (configuración del servidor)

echo "Organización de scripts completada."
echo "Los siguientes archivos se han mantenido en el directorio raíz por ser esenciales:"
echo "- app.py (punto de entrada principal)"
echo "- config.py (configuración principal)"
echo "- wsgi.py, passenger_wsgi.py (puntos de entrada WSGI)"
echo "- gunicorn.conf.py, gunicorn_config.py (configuración de Gunicorn)"
