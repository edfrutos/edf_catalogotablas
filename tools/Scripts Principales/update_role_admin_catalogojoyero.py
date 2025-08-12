#!/usr/bin/env python3
# Script: update_role_admin_catalogojoyero.py
# Descripción: [Explica brevemente qué hace el script]
# Uso: python3 update_role_admin_catalogojoyero.py [opciones]
# Requiere: [librerías externas, si aplica]
# Variables de entorno: [si aplica]
# Autor: [Tu nombre o equipo] - 2025-05-28

from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI no está definida en el entorno")

client: MongoClient = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["app_catalogojoyero_nueva"]
users = db["users"]

result = users.update_one({"username": "Ricardo"}, {"$set": {"role": "admin"}})
if result.modified_count == 1:
    print("✅ Rol actualizado a admin para 'Ricardo' en 'app_catalogojoyero_nueva'")
else:
    print(
        "⚠️ No se actualizó ningún usuario en 'app_catalogojoyero_nueva'. ¿Ya era admin o no existe?"
    )
