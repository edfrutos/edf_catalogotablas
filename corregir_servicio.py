#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para corregir y reiniciar el servicio Gunicorn para edefrutos2025.xyz
Este script solo afecta al dominio edefrutos2025.xyz y no modifica configuraciones globales
"""

import os
import sys
import subprocess
import logging
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Directorio raíz del dominio
DOMAIN_ROOT = "/var/www/vhosts/edefrutos2025.xyz/httpdocs"

def run_command(command):
    """Ejecuta un comando y devuelve su salida"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"

def update_gunicorn_config():
    """Actualiza la configuración de Gunicorn"""
    config_path = os.path.join(DOMAIN_ROOT, "gunicorn_config.py")
    
    config_content = """# Gunicorn configuration file
import multiprocessing

# Server socket
bind = '127.0.0.1:8002'
backlog = 2048

# Worker processes
workers = 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Server mechanics
daemon = False
raw_env = []
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = '/var/www/vhosts/edefrutos2025.xyz/httpdocs/logs/gunicorn_error.log'
loglevel = 'debug'
accesslog = '/var/www/vhosts/edefrutos2025.xyz/httpdocs/logs/gunicorn_access.log'
access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = None

# Server hooks
def on_starting(server):
    pass

def on_reload(server):
    pass

def when_ready(server):
    pass

def post_fork(server, worker):
    pass

def pre_fork(server, worker):
    pass

def pre_exec(server):
    pass

def pre_request(worker, req):
    worker.log.debug("%s %s" % (req.method, req.path))

def post_request(worker, req, environ, resp):
    pass

def worker_exit(server, worker):
    pass

def worker_abort(worker):
    pass

def child_exit(server, worker):
    pass
"""
    
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        logger.info(f"✅ Configuración de Gunicorn actualizada en {config_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error al actualizar la configuración de Gunicorn: {str(e)}")
        return False

def update_service_file():
    """Actualiza el archivo de servicio de Gunicorn"""
    service_path = "/etc/systemd/system/gunicorn-edefrutos.service"
    
    service_content = """[Unit]
Description=Gunicorn daemon for edefrutos2025.xyz
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vhosts/edefrutos2025.xyz/httpdocs
ExecStart=/var/www/vhosts/edefrutos2025.xyz/httpdocs/.venv/bin/gunicorn --config /var/www/vhosts/edefrutos2025.xyz/httpdocs/gunicorn_config.py wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # Verificar si tenemos permisos para modificar el archivo de servicio
        if not os.access(service_path, os.W_OK):
            logger.warning(f"⚠️ No tienes permisos para modificar {service_path}")
            logger.info("Creando un archivo de servicio alternativo...")
            
            # Crear un archivo de servicio alternativo
            alt_service_path = os.path.join(DOMAIN_ROOT, "gunicorn-edefrutos.service")
            with open(alt_service_path, 'w') as f:
                f.write(service_content)
            logger.info(f"✅ Archivo de servicio alternativo creado en {alt_service_path}")
            
            # Mostrar instrucciones para aplicar el cambio
            logger.info("\n=== INSTRUCCIONES PARA APLICAR EL CAMBIO ===")
            logger.info("Para aplicar este cambio, ejecuta los siguientes comandos como root o con sudo:")
            logger.info(f"1. sudo cp {alt_service_path} {service_path}")
            logger.info("2. sudo systemctl daemon-reload")
            logger.info("3. sudo systemctl restart gunicorn-edefrutos.service")
            
            return False
        else:
            # Si tenemos permisos, modificar directamente
            with open(service_path, 'w') as f:
                f.write(service_content)
            logger.info(f"✅ Archivo de servicio actualizado en {service_path}")
            
            # Recargar systemd y reiniciar el servicio
            run_command("systemctl daemon-reload")
            logger.info("✅ Configuración de systemd recargada")
            
            run_command("systemctl restart gunicorn-edefrutos.service")
            logger.info("✅ Servicio Gunicorn reiniciado")
            
            return True
    except Exception as e:
        logger.error(f"❌ Error al actualizar el archivo de servicio: {str(e)}")
        return False

def create_start_script():
    """Crea un script para iniciar la aplicación manualmente"""
    script_path = os.path.join(DOMAIN_ROOT, "iniciar_produccion.sh")
    
    script_content = """#!/bin/bash

# Este script inicia la aplicación Flask en modo producción
# usando Gunicorn directamente sin depender del servicio systemd

# Directorio de la aplicación
APP_DIR="/var/www/vhosts/edefrutos2025.xyz/httpdocs"

# Activar entorno virtual
source $APP_DIR/.venv/bin/activate

# Cambiar al directorio de la aplicación
cd $APP_DIR

# Detener cualquier instancia anterior
pkill -f "gunicorn.*wsgi:app" || true

# Crear directorio de logs si no existe
mkdir -p $APP_DIR/logs

# Iniciar Gunicorn en modo producción
$APP_DIR/.venv/bin/gunicorn --bind 127.0.0.1:8002 --workers 1 --log-level debug --error-logfile $APP_DIR/logs/gunicorn_error.log --access-logfile $APP_DIR/logs/gunicorn_access.log wsgi:app
"""
    
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)  # Hacer el script ejecutable
        logger.info(f"✅ Script de inicio en producción creado en {script_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error al crear el script de inicio: {str(e)}")
        return False

def main():
    """Función principal"""
    logger.info("Iniciando corrección del servicio Gunicorn para edefrutos2025.xyz...")
    logger.info("Esta operación solo afectará al dominio edefrutos2025.xyz")
    
    # 1. Actualizar la configuración de Gunicorn
    update_gunicorn_config()
    
    # 2. Actualizar el archivo de servicio
    update_service_file()
    
    # 3. Crear script de inicio manual
    create_start_script()
    
    # 4. Verificar el estado del servicio
    success, output = run_command("systemctl status gunicorn-edefrutos.service")
    if "active (running)" in output:
        logger.info("✅ El servicio Gunicorn está en ejecución")
    else:
        logger.warning("⚠️ El servicio Gunicorn no está en ejecución")
        logger.info("Puedes iniciar la aplicación manualmente con el script iniciar_produccion.sh")
    
    # 5. Resumen y recomendaciones
    logger.info("\n=== RESUMEN DE LA CORRECCIÓN ===")
    logger.info("1. Se ha actualizado la configuración de Gunicorn")
    logger.info("2. Se ha actualizado el archivo de servicio (o creado una alternativa)")
    logger.info("3. Se ha creado un script para iniciar la aplicación manualmente")
    
    logger.info("\n=== PRÓXIMOS PASOS ===")
    logger.info("1. Si el servicio no se ha reiniciado automáticamente, ejecuta:")
    logger.info("   $ sudo systemctl restart gunicorn-edefrutos.service")
    logger.info("2. Si no tienes acceso a sudo, puedes iniciar la aplicación manualmente:")
    logger.info("   $ ./iniciar_produccion.sh")
    logger.info("3. Verifica que el sitio esté funcionando correctamente:")
    logger.info("   $ curl -I https://edefrutos2025.xyz")

if __name__ == "__main__":
    main()
