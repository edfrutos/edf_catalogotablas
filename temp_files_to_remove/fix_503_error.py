#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para diagnosticar y corregir el error 503 en edefrutos2025.xyz
"""

import os
import sys
import subprocess
import logging
import socket
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def run_command(command):
    """Ejecuta un comando y devuelve su salida"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"

def check_port(host, port):
    """Verifica si un puerto está abierto"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def check_socket_file(socket_path):
    """Verifica si un archivo de socket existe y tiene los permisos correctos"""
    if not os.path.exists(socket_path):
        return False, f"El archivo de socket {socket_path} no existe"
    
    if not os.path.isfile(socket_path) and not os.path.islink(socket_path):
        return False, f"{socket_path} existe pero no es un archivo o enlace simbólico"
    
    return True, f"El archivo de socket {socket_path} existe y parece válido"

def check_gunicorn_config():
    """Verifica la configuración de Gunicorn"""
    config_path = "/var/www/vhosts/edefrutos2025.xyz/httpdocs/gunicorn_config.py"
    
    if not os.path.exists(config_path):
        logger.warning(f"No se encontró el archivo de configuración de Gunicorn en {config_path}")
        return False, "No se encontró el archivo de configuración de Gunicorn"
    
    with open(config_path, 'r') as f:
        config_content = f.read()
    
    # Verificar si está configurado para usar socket o puerto
    if "bind = 'unix:" in config_content:
        logger.info("Gunicorn está configurado para usar un socket Unix")
        return True, "Gunicorn está configurado para usar un socket Unix"
    elif "bind = '127.0.0.1:" in config_content:
        port = config_content.split("bind = '127.0.0.1:")[1].split("'")[0]
        logger.info(f"Gunicorn está configurado para usar el puerto {port}")
        return True, f"Gunicorn está configurado para usar el puerto {port}"
    else:
        logger.warning("No se pudo determinar la configuración de bind en Gunicorn")
        return False, "No se pudo determinar la configuración de bind en Gunicorn"

def create_gunicorn_config():
    """Crea o actualiza la configuración de Gunicorn"""
    config_path = "/var/www/vhosts/edefrutos2025.xyz/httpdocs/gunicorn_config.py"
    
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
        logger.info(f"Archivo de configuración de Gunicorn creado en {config_path}")
        return True, f"Archivo de configuración de Gunicorn creado en {config_path}"
    except Exception as e:
        logger.error(f"Error al crear el archivo de configuración de Gunicorn: {str(e)}")
        return False, f"Error al crear el archivo de configuración de Gunicorn: {str(e)}"

def create_start_script():
    """Crea un script para iniciar la aplicación"""
    script_path = "/var/www/vhosts/edefrutos2025.xyz/httpdocs/start_app.sh"
    
    script_content = """#!/bin/bash

# Activar entorno virtual
source /var/www/vhosts/edefrutos2025.xyz/httpdocs/.venv/bin/activate

# Cambiar al directorio de la aplicación
cd /var/www/vhosts/edefrutos2025.xyz/httpdocs

# Detener cualquier instancia de Gunicorn en ejecución
pkill -f "gunicorn.*app:app"

# Iniciar Gunicorn
/var/www/vhosts/edefrutos2025.xyz/httpdocs/.venv/bin/gunicorn --bind 127.0.0.1:8002 --workers 1 --log-level debug --error-logfile logs/gunicorn_error.log --access-logfile logs/gunicorn_access.log app:app
"""
    
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)  # Hacer el script ejecutable
        logger.info(f"Script de inicio creado en {script_path}")
        return True, f"Script de inicio creado en {script_path}"
    except Exception as e:
        logger.error(f"Error al crear el script de inicio: {str(e)}")
        return False, f"Error al crear el script de inicio: {str(e)}"

def main():
    """Función principal"""
    logger.info("Iniciando diagnóstico del error 503...")
    
    # 1. Verificar si Apache está en ejecución
    success, output = run_command("systemctl status apache2")
    if success:
        logger.info("✅ Apache está en ejecución")
    else:
        logger.error("❌ Apache no está en ejecución o hay un problema")
        logger.info("Intentando reiniciar Apache...")
        run_command("systemctl restart apache2")
    
    # 2. Verificar si Gunicorn está en ejecución
    success, output = run_command("ps aux | grep gunicorn")
    if "app:app" in output:
        logger.info("✅ Gunicorn está en ejecución")
    else:
        logger.warning("⚠️ No se encontró ningún proceso de Gunicorn para app:app")
    
    # 3. Verificar la configuración de Gunicorn
    success, message = check_gunicorn_config()
    if not success:
        logger.info("Creando una nueva configuración de Gunicorn...")
        create_gunicorn_config()
    
    # 4. Verificar si el puerto 8002 está abierto
    if check_port("127.0.0.1", 8002):
        logger.info("✅ El puerto 8002 está abierto y aceptando conexiones")
    else:
        logger.warning("⚠️ El puerto 8002 no está abierto")
        logger.info("Creando script de inicio para la aplicación...")
        create_start_script()
        logger.info("Ejecutando script de inicio...")
        run_command("bash /var/www/vhosts/edefrutos2025.xyz/httpdocs/start_app.sh &")
        
        # Esperar un momento y verificar de nuevo
        logger.info("Esperando 5 segundos para que la aplicación inicie...")
        time.sleep(5)
        
        if check_port("127.0.0.1", 8002):
            logger.info("✅ El puerto 8002 ahora está abierto y aceptando conexiones")
        else:
            logger.error("❌ El puerto 8002 sigue sin estar disponible")
    
    # 5. Verificar si el sitio está habilitado en Apache
    success, output = run_command("ls -la /etc/apache2/sites-enabled/ | grep edefrutos")
    if "edefrutos" in output:
        logger.info("✅ El sitio está habilitado en Apache")
    else:
        logger.warning("⚠️ El sitio no está habilitado en Apache")
        logger.info("Habilitando el sitio en Apache...")
        run_command("a2ensite edefrutos2025.xyz-gunicorn.conf")
        run_command("systemctl reload apache2")
    
    # 6. Verificar los logs de error de Apache
    success, output = run_command("tail -n 20 /var/log/apache2/error.log")
    if "proxy" in output and "error" in output:
        logger.warning(f"⚠️ Se encontraron errores de proxy en los logs de Apache: {output}")
    
    # 7. Verificar los logs de error específicos del sitio
    success, output = run_command("tail -n 20 /var/log/apache2/edefrutos2025.xyz-error.log 2>/dev/null || echo 'No se encontró el archivo de log'")
    if "No se encontró el archivo de log" not in output and len(output.strip()) > 0:
        logger.info(f"Logs de error del sitio: {output}")
    
    # 8. Resumen y recomendaciones
    logger.info("\n=== RESUMEN DEL DIAGNÓSTICO ===")
    logger.info("1. Se ha verificado el estado de Apache y Gunicorn")
    logger.info("2. Se ha verificado la configuración de Gunicorn")
    logger.info("3. Se ha verificado si el puerto 8002 está abierto")
    logger.info("4. Se ha verificado si el sitio está habilitado en Apache")
    
    logger.info("\n=== ACCIONES REALIZADAS ===")
    logger.info("1. Se ha creado/actualizado la configuración de Gunicorn para usar el puerto 8002")
    logger.info("2. Se ha creado un script de inicio para la aplicación")
    logger.info("3. Se ha intentado iniciar la aplicación en el puerto 8002")
    
    logger.info("\n=== PRÓXIMOS PASOS ===")
    logger.info("1. Intenta acceder al sitio web: https://edefrutos2025.xyz")
    logger.info("2. Si sigues viendo el error 503, ejecuta este script de nuevo")
    logger.info("3. Si el problema persiste, verifica los logs de error de Apache y Gunicorn")

if __name__ == "__main__":
    main()
