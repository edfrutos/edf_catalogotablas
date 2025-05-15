# app/extensions.py

from flask_pymongo import PyMongo
from flask_mail import Mail
import boto3

mail = Mail()
mongo = PyMongo()
s3_client = None
catalog_collection = None

def init_extensions(app):
    global s3_client
    global catalog_collection

    mongo.init_app(app)
    mail.init_app(app)

    if app.config.get("USE_S3"):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=app.config['AWS_REGION']
        )

    catalog_collection = mongo.db.catalogo_tablas

def is_mongo_available():
    try:
        # Verifica si mongo está inicializado y la conexión es válida
        if mongo is None or not hasattr(mongo, 'db') or mongo.db is None:
            return False
        # Intentar un ping simple
        mongo.cx.admin.command('ping')
        return True
    except Exception:
        return False

