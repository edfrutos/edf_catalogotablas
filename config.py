import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Optimizaciones para reducir consumo de recursos
    
    # Reduce el tiempo de vida de la sesión a 4 horas para liberar recursos más rápido
    PERMANENT_SESSION_LIFETIME = 14400  # 4 horas
    
    # Clave secreta para sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-fija-para-produccion')
    MONGO_URI = os.getenv("MONGO_URI")
    
    # Configuración de proxy
    PREFERRED_URL_SCHEME = 'https'
    
    # Desactivar protección CSRF en rutas que no la necesitan para reducir overhead
    WTF_CSRF_CHECK_DEFAULT = False  # Verificar CSRF solo cuando se solicita explícitamente
    
    # Comprimir respuestas para reducir ancho de banda
    COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
    COMPRESS_LEVEL = 6  # Balance entre CPU y nivel de compresión (1-9)
    COMPRESS_MIN_SIZE = 500  # Solo comprimir respuestas mayores a 500 bytes
    
    # La configuración de sesión se maneja en app.py
    
    # AWS S3
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    
    # Email
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER_NAME = os.getenv("MAIL_DEFAULT_SENDER_NAME")
    MAIL_DEFAULT_SENDER_EMAIL = os.getenv("MAIL_DEFAULT_SENDER_EMAIL")
    MAIL_DEBUG = os.getenv("MAIL_DEBUG", False)
    
    # Flask debug - desactivado en producción para ahorrar recursos
    DEBUG = False  # Forzar a False en producción
    TESTING = False
    EXPLAIN_TEMPLATE_LOADING = False  # Desactivar debugging de plantillas
    
    # Optimizaciones de caché y rendimiento
    SEND_FILE_MAX_AGE_DEFAULT = 43200  # 12 horas de caché en estáticos
    
    # Optimizaciones de Jinja para rendimiento
    TEMPLATES_AUTO_RELOAD = False  # Desactivar recarga automática en producción
    
    # Sesión optimizada
    SESSION_COOKIE_SECURE = True  # Activar en producción
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = None
    
    # Limitar tamaño de subidas para evitar ataques DoS
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB límite máximo
    UPLOAD_FOLDER = 'uploads'

# Configuración adicional que no necesita entrar en app.config
# Optimizada para menor consumo de recursos
MONGO_CONFIG = {
    'serverSelectionTimeoutMS': 10000,  # Reducido a 10 segundos
    'connectTimeoutMS': 5000,           # Reducido a 5 segundos
    'socketTimeoutMS': 30000,           # Reducido a 30 segundos
    'retryWrites': True,
    'retryReads': True,
    'maxPoolSize': 10,                  # Reducido a 10 conexiones máximas
    'minPoolSize': 1,                   # Reducido a 1 conexión mínima
    'maxIdleTimeMS': 60000,             # Reducido a 1 minuto
    'waitQueueTimeoutMS': 10000,        # Reducido a 10 segundos
    'appName': 'edefrutos2025_app'      # Identificador para monitoring
}

COLLECTION_USERS_UNIFIED = 'users_unified'
COLLECTION_USERS = 'users'
COLLECTION_LOGIN_ATTEMPTS = 'login_attempts'
COLLECTION_RESET_TOKENS = 'reset_tokens'
COLLECTION_AUDIT_LOGS = 'audit_logs'
COLLECTION_CATALOGOS = 'catalogos'

# Ajuste de parámetros de reintentos para ser más eficientes
MAX_RETRIES = 2          # Reducido de 3 a 2 reintentos
RETRY_DELAY = 3          # Reducido de 5 a 3 segundos
MAX_UPLOAD_SIZE = 5      # Tamaño máximo de subida en MB
LOG_ROTATION_SIZE = 2    # Tamaño en MB para rotación de logs
LOG_BACKUP_COUNT = 3     # Número de copias de logs a mantener

# SESSION_TYPE = 'filesystem'  # Eliminado para forzar sesiones solo en cookie
