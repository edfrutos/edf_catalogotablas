#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Cargar configuración
try:
    from config import Config
    MONGO_URI = Config.MONGO_URI
except ImportError:
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://admin:admin123@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority')

def conectar_mongodb():
    """Establece conexión con MongoDB y retorna el cliente y la base de datos."""
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client.get_database()
        logger.info("✅ Conexión a MongoDB establecida correctamente")
        return client, db
    except Exception as e:
        logger.error(f"❌ Error al conectar a MongoDB: {str(e)}")
        return None, None

def corregir_permisos_catalogs(db):
    """Corrige los problemas de permisos en la colección catalogs."""
    # 1. Asegurarse de que todos los documentos tengan el campo created_by
    docs_sin_created_by = list(db.catalogs.find({"created_by": {"$exists": False}}))
    
    if docs_sin_created_by:
        logger.info(f"Corrigiendo {len(docs_sin_created_by)} documentos sin created_by...")
        
        for doc in docs_sin_created_by:
            db.catalogs.update_one(
                {"_id": doc["_id"]},
                {"$set": {"created_by": "admin@example.com"}}
            )
        logger.info("✅ Documentos actualizados con created_by")
    else:
        logger.info("✅ Todos los documentos tienen el campo created_by")
    
    # 2. Verificar si hay catálogos sin filas (rows)
    docs_sin_rows = list(db.catalogs.find({"rows": {"$exists": False}}))
    
    if docs_sin_rows:
        logger.info(f"Corrigiendo {len(docs_sin_rows)} documentos sin el campo rows...")
        
        for doc in docs_sin_rows:
            db.catalogs.update_one(
                {"_id": doc["_id"]},
                {"$set": {"rows": []}}
            )
        logger.info("✅ Documentos actualizados con el campo rows")
    else:
        logger.info("✅ Todos los documentos tienen el campo rows")
    
    # 3. Verificar si hay catálogos sin headers
    docs_sin_headers = list(db.catalogs.find({"headers": {"$exists": False}}))
    
    if docs_sin_headers:
        logger.info(f"Corrigiendo {len(docs_sin_headers)} documentos sin el campo headers...")
        
        for doc in docs_sin_headers:
            # Asignar headers predeterminados
            db.catalogs.update_one(
                {"_id": doc["_id"]},
                {"$set": {"headers": ["Número", "Descripción", "Valor"]}}
            )
        logger.info("✅ Documentos actualizados con el campo headers")
    else:
        logger.info("✅ Todos los documentos tienen el campo headers")
    
    return True

def crear_catalogo_prueba(db):
    """Crea un catálogo de prueba si no existe."""
    catalogo_prueba = db.catalogs.find_one({"name": "Catálogo de Prueba"})
    
    if not catalogo_prueba:
        # Crear catálogo de prueba
        catalogo = {
            "name": "Catálogo de Prueba",
            "description": "Catálogo creado para pruebas de acceso",
            "headers": ["Número", "Descripción", "Valor"],
            "rows": [
                {"Número": "1", "Descripción": "Item de prueba 1", "Valor": "100"},
                {"Número": "2", "Descripción": "Item de prueba 2", "Valor": "200"}
            ],
            "created_by": "admin@example.com",
            "created_at": datetime.datetime.now()
        }
        db.catalogs.insert_one(catalogo)
        logger.info("✅ Catálogo de prueba creado")
        return True
    else:
        logger.info("ℹ️ El catálogo de prueba ya existe")
        return False

def main():
    """Función principal que ejecuta la corrección de permisos."""
    logger.info("Iniciando corrección de permisos en catálogos...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # Corregir permisos en catalogs
        corregido = corregir_permisos_catalogs(db)
        
        # Crear catálogo de prueba
        creado = crear_catalogo_prueba(db)
        
        # Resumen
        logger.info("\n=== RESUMEN DE LA CORRECCIÓN ===")
        logger.info(f"1. Corrección de permisos: {'✅ Completada' if corregido else '❌ Fallida'}")
        logger.info(f"2. Catálogo de prueba: {'✅ Creado' if creado else 'ℹ️ Ya existía'}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Accede a la aplicación en http://127.0.0.1:8002")
        logger.info("3. Inicia sesión con credenciales de administrador:")
        logger.info("   - Email: admin@example.com")
        logger.info("   - Contraseña: admin123")
        logger.info("4. Navega a http://127.0.0.1:8002/catalogs para ver los catálogos")
        
        return True
    
    except Exception as e:
        logger.error(f"Error durante la corrección: {str(e)}")
        return False
    
    finally:
        if client:
            client.close()
            logger.info("Conexión a MongoDB cerrada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
