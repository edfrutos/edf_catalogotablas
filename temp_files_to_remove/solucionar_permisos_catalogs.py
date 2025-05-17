#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from flask import Flask, session, redirect, url_for
import traceback

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
        client = MongoClient(MONGO_URI)
        db = client.get_database()
        logger.info("✅ Conexión a MongoDB establecida correctamente")
        return client, db
    except Exception as e:
        logger.error(f"❌ Error al conectar a MongoDB: {str(e)}")
        return None, None

def verificar_colecciones(db):
    """Verifica las colecciones disponibles en la base de datos."""
    colecciones = db.list_collection_names()
    logger.info(f"Colecciones disponibles: {colecciones}")
    
    # Identificar colecciones relacionadas con catálogos
    catalogs_collections = [col for col in colecciones if 'catalog' in col.lower() or 'spreadsheet' in col.lower()]
    logger.info(f"Colecciones relacionadas con catálogos: {catalogs_collections}")
    
    return colecciones, catalogs_collections

def verificar_documentos_catalogs(db):
    """Verifica los documentos en la colección catalogs."""
    catalogs_count = db.catalogs.count_documents({})
    logger.info(f"Colección catalogs: {catalogs_count} documentos")
    
    if catalogs_count > 0:
        # Mostrar un ejemplo de documento
        sample_doc = db.catalogs.find_one()
        logger.info(f"Ejemplo de documento en catalogs: {sample_doc}")
        
        # Verificar si los documentos tienen el campo created_by
        docs_sin_created_by = db.catalogs.count_documents({"created_by": {"$exists": False}})
        if docs_sin_created_by > 0:
            logger.warning(f"⚠️ Hay {docs_sin_created_by} documentos sin el campo created_by")
            return False
        return True
    else:
        logger.warning("⚠️ La colección catalogs está vacía")
        return False

def corregir_permisos_catalogs(db):
    """Corrige los problemas de permisos en la colección catalogs."""
    # 1. Asegurarse de que todos los documentos tengan el campo created_by
    docs_sin_created_by = list(db.catalogs.find({"created_by": {"$exists": False}}))
    
    if docs_sin_created_by:
        logger.info(f"Corrigiendo {len(docs_sin_created_by)} documentos sin created_by...")
        
        for doc in docs_sin_created_by:
            # Asignar un usuario predeterminado como propietario
            db.catalogs.update_one(
                {"_id": doc["_id"]},
                {"$set": {"created_by": "admin@example.com"}}
            )
        logger.info("✅ Documentos actualizados con created_by")
    
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
    
    return True

def verificar_plantillas():
    """Verifica si existen las plantillas necesarias para los catálogos."""
    templates_dir = "app/templates"
    plantillas_requeridas = [
        "catalogs.html", 
        "ver_catalogo.html", 
        "agregar_fila.html", 
        "editar_fila.html",
        "editar_catalogo.html"
    ]
    
    plantillas_encontradas = []
    plantillas_faltantes = []
    
    for plantilla in plantillas_requeridas:
        ruta_plantilla = os.path.join(templates_dir, plantilla)
        if os.path.exists(ruta_plantilla):
            plantillas_encontradas.append(plantilla)
        else:
            plantillas_faltantes.append(plantilla)
    
    logger.info(f"Plantillas encontradas: {plantillas_encontradas}")
    
    if plantillas_faltantes:
        logger.warning(f"⚠️ Plantillas faltantes: {plantillas_faltantes}")
    
    return plantillas_encontradas, plantillas_faltantes

def main():
    """Función principal que ejecuta el diagnóstico y corrección."""
    logger.info("Iniciando diagnóstico y corrección de problemas de permisos en catálogos...")
    
    # Conectar a MongoDB
    client, db = conectar_mongodb()
    if client is None:
        logger.error("No se pudo conectar a MongoDB. Abortando.")
        return False
    
    try:
        # Verificar colecciones
        colecciones, catalogs_collections = verificar_colecciones(db)
        
        # Verificar documentos en catalogs
        docs_ok = verificar_documentos_catalogs(db)
        
        # Corregir permisos en catalogs
        corregido = corregir_permisos_catalogs(db)
        
        # Verificar plantillas
        plantillas_encontradas, plantillas_faltantes = verificar_plantillas()
        
        # Resumen
        logger.info("\n=== RESUMEN DEL DIAGNÓSTICO Y CORRECCIÓN ===")
        logger.info(f"1. Colecciones relacionadas con catálogos: {catalogs_collections}")
        logger.info(f"2. Estado de documentos en catalogs: {'✅ OK' if docs_ok else '❌ Con problemas'}")
        logger.info(f"3. Corrección de permisos: {'✅ Completada' if corregido else '❌ Fallida'}")
        logger.info(f"4. Plantillas encontradas: {plantillas_encontradas}")
        logger.info(f"5. Plantillas faltantes: {plantillas_faltantes}")
        
        # Próximos pasos
        logger.info("\n=== PRÓXIMOS PASOS ===")
        logger.info("1. Reinicia la aplicación Flask para aplicar los cambios:")
        logger.info("   $ pkill -f 'python.*ejecutar_flask_directo.py'")
        logger.info("   $ python3 ejecutar_flask_directo.py")
        logger.info("2. Accede a la aplicación en http://127.0.0.1:8002")
        logger.info("3. Inicia sesión con credenciales de administrador")
        logger.info("4. Navega a http://127.0.0.1:8002/catalogs para ver los catálogos")
        
        return True
    
    except Exception as e:
        logger.error(f"Error durante el diagnóstico y corrección: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    
    finally:
        if client:
            client.close()
            logger.info("Conexión a MongoDB cerrada")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
