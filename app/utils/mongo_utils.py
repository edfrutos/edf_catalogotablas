"""
Utilidades para trabajar con MongoDB
"""
from bson.objectid import ObjectId
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def is_mongo_available():
    """
    Verifica si la conexión a MongoDB está disponible
    """
    try:
        # Intentar una operación simple para verificar la conexión
        # Importamos mongo aquí para evitar importaciones circulares
        from app.extensions import mongo
        info = mongo.db.command('serverStatus')
        return True
    except Exception as e:
        logger.error(f"Error al verificar disponibilidad de MongoDB: {str(e)}")
        return False

def is_valid_object_id(id_str):
    """
    Verifica si una cadena es un ObjectId válido de MongoDB
    """
    try:
        ObjectId(id_str)
        return True
    except Exception:
        return False
