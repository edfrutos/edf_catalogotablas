#!/usr/bin/env python3
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Conectar a MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client['app_catalogojoyero']
users_collection = db['users']

try:
    # Listar usuarios
    users = list(users_collection.find())
    print(f"\nUsuarios encontrados: {len(users)}")
    
    for user in users:
        print(f"\nUsuario:")
        print(f"Email: {user.get('email')}")
        print(f"Nombre: {user.get('nombre')}")
        print(f"Rol: {user.get('role', 'normal')}")
        print(f"Creado: {user.get('created_at')}")
        print(f"Última actualización: {user.get('updated_at')}")
        print("-" * 50)
        
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    client.close()
