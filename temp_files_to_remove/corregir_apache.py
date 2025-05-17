#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para corregir la configuración de Apache para edefrutos2025.xyz
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

def check_port(host, port):
    """Verifica si un puerto está abierto"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def create_apache_config():
    """Crea un archivo de configuración de Apache alternativo"""
    config_path = os.path.join(DOMAIN_ROOT, "edefrutos2025.xyz-local.conf")
    
    config_content = """<VirtualHost *:80>
    ServerName edefrutos2025.xyz
    ServerAlias www.edefrutos2025.xyz

    # Configuración del proxy para Gunicorn
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8002/
    ProxyPassReverse / http://127.0.0.1:8002/

    # Timeout settings
    ProxyTimeout 300
    ProxyBadHeader Ignore
    ProxyPassReverseCookieDomain localhost edefrutos2025.xyz
    ProxyPassReverseCookiePath / /

    # Configuración de headers
    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Forwarded-Port "80"

    # Configuración de logs
    ErrorLog ${APACHE_LOG_DIR}/edefrutos2025.xyz-error.log
    CustomLog ${APACHE_LOG_DIR}/edefrutos2025.xyz-access.log combined
</VirtualHost>

# Configuración para HTTPS
<VirtualHost *:443>
    ServerName edefrutos2025.xyz
    ServerAlias www.edefrutos2025.xyz

    # Configuración del proxy para Gunicorn
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8002/
    ProxyPassReverse / http://127.0.0.1:8002/

    # Timeout settings
    ProxyTimeout 300
    ProxyBadHeader Ignore
    ProxyPassReverseCookieDomain localhost edefrutos2025.xyz
    ProxyPassReverseCookiePath / /

    # Configuración de headers
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-Port "443"

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/edefrutos2025.xyz/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/edefrutos2025.xyz/privkey.pem

    # Configuración de logs
    ErrorLog ${APACHE_LOG_DIR}/edefrutos2025.xyz-ssl-error.log
    CustomLog ${APACHE_LOG_DIR}/edefrutos2025.xyz-ssl-access.log combined
</VirtualHost>
"""
    
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        logger.info(f"✅ Configuración de Apache alternativa creada en {config_path}")
        logger.info("Para aplicar esta configuración, ejecuta los siguientes comandos como root o con sudo:")
        logger.info(f"1. sudo cp {config_path} /etc/apache2/sites-available/edefrutos2025.xyz.conf")
        logger.info("2. sudo a2ensite edefrutos2025.xyz.conf")
        logger.info("3. sudo systemctl reload apache2")
        return True
    except Exception as e:
        logger.error(f"❌ Error al crear la configuración de Apache: {str(e)}")
        return False

def create_direct_start_script():
    """Crea un script para iniciar la aplicación directamente"""
    script_path = os.path.join(DOMAIN_ROOT, "iniciar_app_directo.sh")
    
    script_content = """#!/bin/bash

# Este script inicia la aplicación Flask directamente en el puerto 8002
# para que Apache pueda acceder a ella

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
nohup $APP_DIR/.venv/bin/gunicorn --bind 127.0.0.1:8002 --workers 1 --log-level debug --error-logfile $APP_DIR/logs/gunicorn_error.log --access-logfile $APP_DIR/logs/gunicorn_access.log wsgi:app > $APP_DIR/logs/app.log 2>&1 &

echo "Aplicación iniciada en segundo plano. Logs en $APP_DIR/logs/app.log"
echo "Para verificar si está en ejecución, ejecuta: curl -I http://127.0.0.1:8002"
"""
    
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)  # Hacer el script ejecutable
        logger.info(f"✅ Script de inicio directo creado en {script_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Error al crear el script de inicio directo: {str(e)}")
        return False

def create_plesk_vhost_conf():
    """Crea un archivo de configuración para el vhost en Plesk"""
    config_path = os.path.join(DOMAIN_ROOT, "plesk_vhost.conf")
    
    config_content = """# Configuración para el vhost de Plesk
# Este archivo debe colocarse en el directorio conf/ del vhost

<IfModule mod_proxy.c>
    ProxyRequests Off
    ProxyPreserveHost On
    
    <Proxy *>
        Require all granted
    </Proxy>
    
    ProxyPass / http://127.0.0.1:8002/
    ProxyPassReverse / http://127.0.0.1:8002/
    
    # Headers adicionales
    <IfModule mod_headers.c>
        RequestHeader set X-Forwarded-Proto "https" env=HTTPS
        RequestHeader set X-Forwarded-Port "443" env=HTTPS
        RequestHeader set X-Forwarded-Port "80" env=!HTTPS
    </IfModule>
</IfModule>
"""
    
    try:
        # Crear directorio conf si no existe
        conf_dir = os.path.join(os.path.dirname(DOMAIN_ROOT), "conf")
        os.makedirs(conf_dir, exist_ok=True)
        
        # Escribir archivo de configuración
        with open(os.path.join(conf_dir, "vhost.conf"), 'w') as f:
            f.write(config_content)
        logger.info(f"✅ Configuración de vhost para Plesk creada en {os.path.join(conf_dir, 'vhost.conf')}")
        
        # También guardar una copia en el directorio httpdocs
        with open(config_path, 'w') as f:
            f.write(config_content)
        logger.info(f"✅ Copia de la configuración guardada en {config_path}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error al crear la configuración de vhost para Plesk: {str(e)}")
        return False

def main():
    """Función principal"""
    logger.info("Iniciando corrección de la configuración de Apache para edefrutos2025.xyz...")
    logger.info("Esta operación solo afectará al dominio edefrutos2025.xyz")
    
    # 1. Verificar si el puerto 8002 está abierto
    if check_port("127.0.0.1", 8002):
        logger.info("✅ El puerto 8002 está abierto y aceptando conexiones")
    else:
        logger.warning("⚠️ El puerto 8002 no está abierto")
        logger.info("Ejecuta el script iniciar_produccion.sh para iniciar la aplicación")
        logger.info("$ ./iniciar_produccion.sh")
    
    # 2. Crear configuración de Apache alternativa
    create_apache_config()
    
    # 3. Crear script de inicio directo
    create_direct_start_script()
    
    # 4. Crear configuración de vhost para Plesk
    create_plesk_vhost_conf()
    
    # 5. Resumen y recomendaciones
    logger.info("\n=== RESUMEN DE LA CORRECCIÓN ===")
    logger.info("1. Se ha creado una configuración de Apache alternativa")
    logger.info("2. Se ha creado un script para iniciar la aplicación directamente")
    logger.info("3. Se ha creado una configuración de vhost para Plesk")
    
    logger.info("\n=== PRÓXIMOS PASOS ===")
    logger.info("1. Inicia la aplicación con el script iniciar_app_directo.sh:")
    logger.info("   $ ./iniciar_app_directo.sh")
    logger.info("2. Verifica que la aplicación esté en ejecución:")
    logger.info("   $ curl -I http://127.0.0.1:8002")
    logger.info("3. Si tienes acceso al panel de control de Plesk:")
    logger.info("   - Verifica que el archivo conf/vhost.conf esté presente")
    logger.info("   - Reinicia el servicio web para el dominio desde el panel de Plesk")
    logger.info("4. Si no tienes acceso al panel de Plesk, contacta al administrador del servidor")
    logger.info("   y proporciona los archivos de configuración que hemos creado")

if __name__ == "__main__":
    main()
