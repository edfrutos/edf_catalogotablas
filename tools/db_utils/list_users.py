#!/usr/bin/env python3
from pymongo import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Conectar a MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client['app_catalogojoyero']
users_collection = db['users']
spreadsheets_collection = db['spreadsheets']

# Obtener todos los usuarios registrados
print("\n=== Usuarios Registrados ===")
users = list(users_collection.find())
print(f"Total de usuarios registrados: {len(users)}")
for user in users:
    print(f"\nUsuario: {user.get('username')}")
    print(f"Email: {user.get('email')}")
    print(f"Rol: {user.get('role', 'No especificado')}")
    # Contar tablas del usuario
    tablas = spreadsheets_collection.count_documents({"owner": user.get('username')})
    print(f"Número de tablas: {tablas}")

# Buscar usuarios únicos en la colección de tablas (por si hay algunos no registrados)
print("\n=== Usuarios con Tablas (incluyendo no registrados) ===")
owners = spreadsheets_collection.distinct("owner")
print(f"Total de usuarios con tablas: {len(owners)}")
for owner in owners:
    tablas = spreadsheets_collection.count_documents({"owner": owner})
    print(f"\nUsuario: {owner}")
    print(f"Número de tablas: {tablas}")
    # Listar las tablas
    print("Tablas:")
    for tabla in spreadsheets_collection.find({"owner": owner}):
        print(f"- {tabla.get('name', 'Sin nombre')} (ID: {tabla.get('_id')})")
