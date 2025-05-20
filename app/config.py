import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    # Configuración general de Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev_key')

    # Configuración de MongoDB
    MONGO_URI = os.getenv('MONGO_URI')
    MONGODB_SETTINGS = {
        'connect': False
    }

    # Configuración de correo electrónico
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = (os.getenv('MAIL_DEFAULT_SENDER_NAME'), os.getenv('MAIL_DEFAULT_SENDER_EMAIL'))
    MAIL_DEBUG = os.getenv('MAIL_DEBUG', 'False') == 'True'

    # Configuración de sesión
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False

    # Configuración de AWS S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    USE_S3 = os.getenv("USE_S3", "false").lower() in ["true", "1"]

    # Rutas de carpetas internas
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '../imagenes_subidas')
    SPREADSHEET_FOLDER = os.path.join(BASE_DIR, '../spreadsheets')

    # Otros
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
