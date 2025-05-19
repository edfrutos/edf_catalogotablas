#!/usr/bin/env python3
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Intentar conectar a MongoDB
uri = "mongodb+srv://edfrutos:rYjwUC6pUNrLtbaI@cluster0.pmokh.mongodb.net/app_catalogojoyero?retryWrites=true&w=majority"
try:
    client = MongoClient(uri, tls=True)
    db = client['app_catalogojoyero']
    users = db['users']
    
    # Verificar si hay usuarios
    print("Conexión exitosa a MongoDB")
    print("Hay", users.count_documents({}), "usuarios en la base de datos")
    
    # Mostrar información de los usuarios (sin mostrar contraseñas)
    for user in users.find({}, {'password': 0}):
        print(f"Usuario: {user.get('nombre')}, Email: {user.get('email')}, Rol: {user.get('rol')}")

except Exception as e:
    print(f"Error al conectar a MongoDB: {str(e)}")
