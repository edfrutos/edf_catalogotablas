#!/usr/bin/env python3
import sys
import os
import logging
import traceback

# Configurar logging para monitorear la inicialización - usando solo salida estándar
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [WSGI] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Agregar el directorio actual al path para encontrar los módulos
sys.path.insert(0, os.path.dirname(__file__))

# CONFIGURACIÓN DE SESIÓN DIRECTA
# Esta configuración se aplicará a la aplicación Flask
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_CONFIG = {
    'SESSION_TYPE': 'filesystem',
    'SESSION_FILE_DIR': os.path.join(ROOT_DIR, 'flask_session'),
    'SESSION_COOKIE_NAME': 'edefrutos2025_session',
    'SESSION_COOKIE_SECURE': False,  # IMPORTANTE: Deshabilitado para desarrollo
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax',
    'SESSION_PERMANENT': True,
    'PERMANENT_SESSION_LIFETIME': 86400,  # 24 horas en segundos
    'SESSION_REFRESH_EACH_REQUEST': True,
    'SESSION_USE_SIGNER': False,
    'SECRET_KEY': 'desarrollo_clave_secreta_fija_12345'
}

# Asegurarse de que el directorio de sesiones existe
os.makedirs(SESSION_CONFIG['SESSION_FILE_DIR'], exist_ok=True)

# Exponer solo una instancia Flask real
try:
    from app import create_app
    flask_app = create_app()
    
    # Aplicar configuración de sesión directamente a la aplicación
    for key, value in SESSION_CONFIG.items():
        flask_app.config[key] = value
    
    # Establecer también como atributo directo para mayor compatibilidad
    flask_app.secret_key = flask_app.config['SECRET_KEY']
    
    logging.info("✅ Aplicación Flask creada correctamente")
    logging.info(f"✅ Configuración de sesión aplicada directamente en wsgi.py")
    logging.info(f"✅ SESSION_COOKIE_SECURE = {flask_app.config.get('SESSION_COOKIE_SECURE')}")
except Exception as e:
    logging.error(f"❌ Error al crear la aplicación Flask: {e}")
    logging.error(traceback.format_exc())
    raise

# Para Gunicorn y servidores WSGI
app = flask_app

# Para desarrollo local con flask run
if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0")
